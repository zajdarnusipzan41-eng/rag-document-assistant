from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3

class SourceDocument(BaseModel):
    content: str
    metadata: dict

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]

class DocumentUploadResponse(BaseModel):
    filename: str
    chunks_created: int
    message: str
