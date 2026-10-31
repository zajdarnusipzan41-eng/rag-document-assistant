import json
import os
from typing import Any, Dict, List

import chromadb
from chromadb.config import Settings as ChromaSettings
from google import genai
from pypdf import PdfReader

from app.config import settings


class RAGEngine:
    def __init__(self):
        self.api_key = settings["GEMINI_API_KEY"] or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing. Add it to .env or environment variables.")

        self.genai_client = genai.Client(api_key=self.api_key)

        os.makedirs(settings["CHROMA_DB_DIR"], exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=settings["CHROMA_DB_DIR"])
        self.collection = self.chroma_client.get_or_create_collection(
            name=settings["CHROMA_COLLECTION_NAME"],
            metadata={"hnsw:space": "cosine"},
        )

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        chunks: List[str] = []
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += chunk_size - overlap

        return chunks

    def _extract_text_from_pdf(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        pages = []
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
        lower_name = filename.lower()

        if lower_name.endswith(".pdf"):
            text = self._extract_text_from_pdf(file_path)
        elif lower_name.endswith((".txt", ".md")):
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
                response = self.genai_client.models.embed_content(
                    model=settings["EMBEDDING_MODEL_NAME"],
                    contents=chunk,
                )
                embedding = response.embeddings[0].values
                self.collection.add(
                    ids=[f"{filename}_{index}"],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{"source": filename, "chunk_index": index}],
                )
            except Exception as e:
                print(f"Embedding error for chunk {index}: {e}")
                continue

    def query(self, question: str, top_k: int = 4) -> Dict[str, Any]:
        if not question.strip():
            raise ValueError("Question cannot be empty.")

        response = self.genai_client.models.embed_content(
            model=settings["EMBEDDING_MODEL_NAME"],
            contents=question,
        )
        question_embedding = response.embeddings[0].values

        search_results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=min(top_k, settings["TOP_K_RESULTS"]),
        )

        docs = search_results.get("documents", [[]])[0]
        metadata = search_results.get("metadatas", [[]])[0]

        context_parts = []
        source_list = []
        for doc, meta in zip(docs, metadata):
            context_parts.append(doc)
            source_info = {"content": doc, "metadata": meta}
            source_list.append(source_info)

        context = "\n\n".join(context_parts)

        if not context.strip():
            answer = "Информация не найдена в документах."
            return {"answer": answer, "sources": []}

        prompt = f"""Используй только этот контекст и ответь на вопрос.
Если в контексте нет ответа, напиши: "Информация не найдена в документах".

Контекст:
{context}

Вопрос: {question}

Ответ:"""

        llm_response = self.genai_client.models.generate_content(
            model=settings["GENERATION_MODEL_NAME"],
            contents=prompt,
        )
        answer = getattr(llm_response, "text", None) or "Не удалось сгенерировать ответ."

        return {
            "answer": answer,
            "sources": source_list,
        }
