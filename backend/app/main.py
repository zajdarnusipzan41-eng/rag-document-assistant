import os
import shutil
from typing import List

from fastapi import FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.rag_engine import RAGEngine

app = FastAPI(
    title=settings["APP_NAME"],
    debug=settings["DEBUG"],
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings["CORS_ORIGINS"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAGEngine()


class QueryRequest(BaseModel):
    question: str = ""
    query: str = ""
    top_k: int = 4


class UploadResponse(BaseModel):
    filename: str
    chunks_processed: int
    status: str
    message: str = "success"


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict] = []


@app.get("/", tags=["Health Check"])
async def root():
    return {"status": "online", "app": settings["APP_NAME"]}


@app.post("/api/v1/upload", response_model=UploadResponse, tags=["RAG"])
@app.post("/upload", response_model=UploadResponse, tags=["RAG"])
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "Filename is required.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {".pdf", ".txt", ".md"}:
        raise HTTPException(400, "Only PDF, TXT or MD files are supported.")

    temp_dir = "./temp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        chunks_count = rag.process_file(temp_path, file.filename)
        return UploadResponse(
            filename=file.filename,
            chunks_processed=chunks_count,
            status="success",
            message="File processed successfully.",
        )
    except Exception as exc:
        raise HTTPException(500, f"Error processing file: {str(exc)}") from exc
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/api/v1/query", tags=["RAG"])
@app.post("/query", tags=["RAG"])
async def ask_question(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(400, "Request body must be JSON.")

    question = (payload.get("question") or payload.get("query") or "").strip()
    top_k = int(payload.get("top_k", 4))

    if not question:
        raise HTTPException(400, "Question cannot be empty.")

    try:
        result = rag.query(question, top_k=top_k)
        return result
    except Exception as exc:
        raise HTTPException(500, f"Error generating answer: {str(exc)}") from exc
