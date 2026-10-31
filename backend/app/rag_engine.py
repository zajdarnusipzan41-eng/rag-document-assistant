import os
from typing import Any, Dict, List

import chromadb
from google import genai
from pypdf import PdfReader

from app.config import settings


class RAGEngine:
    def __init__(self):
        self.api_key = settings["GEMINI_API_KEY"] or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is empty. Add it to backend/.env or environment variables.")

        self.client = genai.Client(api_key=self.api_key)

        os.makedirs(settings["CHROMA_DB_DIR"], exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=settings["CHROMA_DB_DIR"])
        self.collection = self.chroma_client.get_or_create_collection(
            name=settings["CHROMA_COLLECTION_NAME"],
            metadata={"hnsw:space": "cosine"},
        )

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        chunks: List[str] = []
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            if overlap >= chunk_size:
                overlap = chunk_size - 1

            start += chunk_size - overlap

        return chunks

    def _extract_text_from_pdf(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        pages: List[str] = []

        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text)

        text = "\n".join(pages)
        if not text.strip():
            raise ValueError("PDF file is empty or text could not be extracted.")
        return text

    def _extract_text_from_txt(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()

        if not text.strip():
            raise ValueError("TXT/MD file is empty.")
        return text

    def process_file(self, file_path: str, filename: str) -> int:
        name = filename.lower()

        if name.endswith(".pdf"):
            text = self._extract_text_from_pdf(file_path)
        elif name.endswith((".txt", ".md")):
            text = self._extract_text_from_txt(file_path)
        else:
            raise ValueError("Unsupported file type. Use PDF, TXT or MD.")

        chunks = self._chunk_text(text, settings["CHUNK_SIZE"], settings["CHUNK_OVERLAP"])
        self._add_to_vector_db(chunks, filename)
        return len(chunks)

    def process_pdf(self, file_path: str, filename: str) -> int:
        return self.process_file(file_path, filename)

    def _add_to_vector_db(self, chunks: List[str], filename: str):
        for index, chunk in enumerate(chunks):
            try:
                embedding_result = self.client.models.embed_content(
                    model=settings["EMBEDDING_MODEL_NAME"],
                    contents=chunk,
                )
                embedding = embedding_result.embeddings[0].values

                self.collection.add(
                    ids=[f"{filename}_{index}"],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{"source": filename, "chunk_index": index}],
                )
            except Exception as exc:
                print(f"Embedding error for chunk {index}: {exc}")
                continue

    def query(self, question: str, top_k: int = 4) -> Dict[str, Any]:
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        embedding_result = self.client.models.embed_content(
            model=settings["EMBEDDING_MODEL_NAME"],
            contents=question,
        )
        query_embedding = embedding_result.embeddings[0].values

        search_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, settings["TOP_K_RESULTS"]),
        )

        docs = search_results.get("documents", [[]])[0]
        metadatas = search_results.get("metadatas", [[]])[0]

        if not docs:
            return {
                "answer": "Информация не найдена в документах.",
                "sources": [],
            }

        context = "\n\n".join(docs)
        sources = [
            {"content": doc, "metadata": meta}
            for doc, meta in zip(docs, metadatas)
        ]

        prompt = f"""Используй только этот контекст для ответа.
Если в контексте нет ответа, напиши ровно: "Информация не найдена в документах".

Контекст:
{context}

Вопрос: {question}

Ответ:"""

        llm_response = self.client.models.generate_content(
            model=settings["GENERATION_MODEL_NAME"],
            contents=prompt,
        )
        answer = getattr(llm_response, "text", None) or "Не удалось сгенерировать ответ."

        return {
            "answer": answer,
            "sources": sources,
        }
