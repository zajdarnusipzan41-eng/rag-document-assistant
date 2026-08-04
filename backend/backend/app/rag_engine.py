import os
import chromadb
from google import genai
from pypdf import PdfReader

class RAGEngine:
    def __init__(self):
        # Инициализация Gemini API клиента
        self.ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        # Локальная векторная база данных ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(name="pdf_docs")

    def process_pdf(self, file_path: str, filename: str) -> int:
        """Считывание PDF, разбиение на чанки и сохранение в векторную БД"""
        reader = PdfReader(file_path)
        text_chunks, metadatas, ids = [], [], []
        chunk_size, chunk_id = 500, 0

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                if chunk.strip():
                    text_chunks.append(chunk)
                    metadatas.append({"source": filename, "page": page_num + 1})
                    ids.append(f"{filename}_p{page_num+1}_{chunk_id}")
                    chunk_id += 1

        if text_chunks:
            self.collection.add(
                documents=text_chunks,
                metadatas=metadatas,
                ids=ids
            )
        return len(text_chunks)

    def query(self, question: str) -> dict:
        """Поиск релевантных кусков текста и генерация ответа через Gemini"""
        results = self.collection.query(query_texts=[question], n_results=3)
        retrieved_docs = results["documents"][0] if results["documents"] else []
        context = "\n\n".join(retrieved_docs)

        prompt = f"""Используй следующий контекст из загруженных PDF-документов для точного ответа на вопрос.
Если в контексте нет ответа, так и скажи.

Контекст:
{context}

Вопрос: {question}
Ответ:"""

        response = self.ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return {
            "answer": response.text,
            "sources": results["metadatas"][0] if results["metadatas"] else []
        }
