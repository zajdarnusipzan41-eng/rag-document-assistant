from fastapi import APIRouter
from app.schemas import QueryRequest, QueryResponse
from app.rag_engine import query_rag

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/query", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    result = query_rag(query=request.query, top_k=request.top_k)
    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"]
    )
