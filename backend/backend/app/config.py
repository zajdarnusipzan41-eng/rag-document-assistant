import os

APP_NAME = os.getenv("APP_NAME", "RAG Document Assistant API")
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")


def _split_list(value: str) -> list[str]:
    if not value:
        return ["http://localhost:3000", "http://localhost:5173"]
    return [item.strip() for item in value.split(",") if item.strip()]


CORS_ORIGINS = _split_list(os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./data/chroma_db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "documents")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-004")
GENERATION_MODEL_NAME = os.getenv("GENERATION_MODEL_NAME", "gemini-2.5-flash")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "4"))

settings = {
    "APP_NAME": APP_NAME,
    "APP_ENV": APP_ENV,
    "DEBUG": DEBUG,
    "PORT": PORT,
    "HOST": HOST,
    "CORS_ORIGINS": CORS_ORIGINS,
    "GEMINI_API_KEY": GEMINI_API_KEY,
    "CHROMA_DB_DIR": CHROMA_DB_DIR,
    "CHROMA_COLLECTION_NAME": CHROMA_COLLECTION_NAME,
    "EMBEDDING_MODEL_NAME": EMBEDDING_MODEL_NAME,
    "GENERATION_MODEL_NAME": GENERATION_MODEL_NAME,
    "CHUNK_SIZE": CHUNK_SIZE,
    "CHUNK_OVERLAP": CHUNK_OVERLAP,
    "TOP_K_RESULTS": TOP_K_RESULTS,
}
