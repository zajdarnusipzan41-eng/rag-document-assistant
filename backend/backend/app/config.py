from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "RAG Document Assistant API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    CHROMA_DB_DIR: str = "./data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "documents"

    EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 4

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
