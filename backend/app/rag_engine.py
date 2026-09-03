import os
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from pypdf import PdfReader
from google.genai import Client
from app.config import settings

class RAGEngine:
    def __init__(self):
        """Инициализация RAG Engine с ChromaDB и Google GenAI"""
        # Инициализируем ChromaDB
        self.chroma_settings = ChromaSettings(
            chroma_db_dir=settings.CHROMA_DB_DIR,
            anonymized_telemetry=False
        )
        self.client = chromadb.Client(self.chroma_settings)
        
        # Получаем или создаем коллекцию
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Инициализируем Google GenAI
        self.genai_client = Client(api_key=settings.GEMINI_API_KEY)
    
    def process_pdf(self, file_path: str, filename: str) -> int:
        """Обработка PDF: извлечение текста, разбиение на чанки, добавление в БД"""
        try:
            # Извлекаем текст из PDF
            pdf_reader = PdfReader(file_path)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            if not text.strip():
                raise ValueError("PDF не содержит извлекаемого текста")
            
            # Разбиваем текст на чанки
            chunks = self._chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
            
            # Добавляем чанки в ChromaDB с метаданными
            self._add_to_vector_db(chunks, filename)
            
            return len(chunks)
        except Exception as e:
            raise Exception(f"Ошибка при обработке PDF: {str(e)}")
    
    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Разбиение текста на перекрывающиеся чанки"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end].strip()
            
            if chunk:
                chunks.append(chunk)
            
            start += chunk_size - overlap
        
        return chunks
    
    def _add_to_vector_db(self, chunks: List[str], filename: str):
        """Добавление чанков в vector database с эмбеддингами"""
        # Генерируем эмбеддинги через Google GenAI
        for i, chunk in enumerate(chunks):
            try:
                # Генерируем эмбеддинг
                embedding_response = self.genai_client.embed_content(
                    model="models/embedding-001",
                    content=chunk,
                )
                embedding = embedding_response.embedding
                
                # Добавляем в ChromaDB
                self.collection.add(
                    ids=[f"{filename}_{i}"],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{"source": filename, "chunk_index": i}]
                )
            except Exception as e:
                print(f"Ошибка при эмбеддинге чанка {i}: {str(e)}")
                continue
    
    def query(self, question: str, top_k: int = 4) -> Dict[str, Any]:
        """Поиск релевантных документов и генерация ответа"""
        try:
            # Генерируем эмбеддинг для вопроса
            question_embedding = self.genai_client.embed_content(
                model="models/embedding-001",
                content=question,
            ).embedding
            
            # Ищем релевантные чанки в ChromaDB
            search_results = self.collection.query(
                query_embeddings=[question_embedding],
                n_results=top_k
            )
            
            # Извлекаем контекст из результатов
            context = ""
            sources = []
            
            if search_results['documents'] and len(search_results['documents']) > 0:
                for doc, metadata in zip(
                    search_results['documents'][0], 
                    search_results['metadatas'][0]
                ):
                    context += f"\n{doc}\n"
                    if metadata['source'] not in sources:
                        sources.append(metadata['source'])
            
            # Генерируем ответ через LLM
            prompt = f"""Используя следующий контекст, ответь на вопрос.
Если ответ не найден в контексте, скажи "Информация не найдена в документах".

Контекст:
{context}

Вопрос: {question}

Ответ:"""
            
            response = self.genai_client.generate_content(prompt)
            answer = response.text if response else "Не удалось сгенерировать ответ"
            
            return {
                "answer": answer,
                "sources": sources
            }
        
        except Exception as e:
            raise Exception(f"Ошибка при выполнении запроса: {str(e)}")
