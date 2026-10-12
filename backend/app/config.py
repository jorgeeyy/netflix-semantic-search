from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Vector store selection: "pinecone" or "chroma"
    vector_db: Literal["pinecone", "chroma"] = "pinecone"

    # Embeddings
    openai_api_key: str
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536

    # Pinecone
    pinecone_api_key: str | None = None
    pinecone_index: str = "semantic-search-datacamp"
    pinecone_namespace: str = "netflix_dataset"

    # Chroma
    chroma_path: str = str(PROJECT_ROOT / "chroma_db")
    chroma_collection: str = "netflix_titles_1000"

    # LLM (RAG answer generation)
    llm_provider: Literal["groq", "openai"] = "groq"
    groq_api_key: str | None = None
    llm_model: str = "llama-3.3-70b-versatile"
    openai_chat_model: str = "gpt-4o-mini"

    # Dataset
    csv_path: str = str(PROJECT_ROOT / "netflix_titles_1000.csv")
    ingest_batch_size: int = 100

    # API
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
