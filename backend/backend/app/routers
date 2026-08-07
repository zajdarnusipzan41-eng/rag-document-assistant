from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas import DocumentUploadResponse
from app.ingestion import process_file_content
from app.rag_engine import add_chunks_to_vector_db

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        chunks = process_file_content(file.filename, content)
        add_chunks_to_vector_db(chunks, file.filename)
        
        return DocumentUploadResponse(
            filename=file.filename,
            chunks_created=len(chunks),
            message="Файл успешно обработан и векторизован!"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
