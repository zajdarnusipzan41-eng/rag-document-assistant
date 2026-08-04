import os, shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from app.rag_engine import RAGEngine

load_dotenv()
app = FastAPI(title="RAG Document Assistant API")

# Настройка CORS для взаимодействия с React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAGEngine()

class QueryRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Только PDF файлы!")
    
    os.makedirs("./temp", exist_ok=True)
    temp_path = f"./temp/{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        chunks = rag.process_pdf(temp_path, file.filename)
        return {"filename": file.filename, "chunks_processed": chunks, "status": "success"}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/query")
async def ask_question(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Вопрос не может быть пустым")
    return rag.query(request.question)
