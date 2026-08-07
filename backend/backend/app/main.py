import os
import shutil
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.rag_engine import RAGEngine

# Инициализируем приложение
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализируем RAG Engine
rag = RAGEngine()

# --- Схемы данных (Pydantic) ---
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str] = []

class UploadResponse(BaseModel):
    filename: str
    chunks_processed: int
    status: str


# --- Эндпоинты ---

@app.get("/", tags=["Health Check"])
async def root():
    return {"status": "online", "app": settings.APP_NAME}


@app.post("/upload", response_model=UploadResponse, tags=["RAG"])
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Поддерживаются только PDF файлы."
        )

    temp_dir = "./temp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Вызов твоего метода из rag_engine.py
        chunks = rag.process_pdf(temp_path, file.filename)

        return UploadResponse(
            filename=file.filename,
            chunks_processed=chunks,
            status="success"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке PDF: {str(e)}"
        )
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/query", tags=["RAG"])
async def ask_question(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Вопрос не может быть пустым."
        )

    try:
        # Вызов твоего метода из rag_engine.py
        result = rag.query(request.question)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при генерации ответа: {str(e)}"
        )
