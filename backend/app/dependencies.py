from functools import lru_cache

from .config import Settings, get_settings
from .services.embedder import Embedder
from .services.ingest import IngestService
from .services.rag import RAGService
from .vectorstores.base import VectorStore
from .vectorstores.chroma_store import ChromaStore
from .vectorstores.pinecone_store import PineconeStore

_active_backend_override: str | None = None


def set_active_backend(backend: str) -> None:
    global _active_backend_override
    _active_backend_override = backend


@lru_cache
def get_embedder() -> Embedder:
    settings = get_settings()
    return Embedder(
        api_key=settings.openai_api_key,
        model=settings.embedding_model,
        dimensions=settings.embedding_dim,
    )


@lru_cache
def get_store(backend: str) -> VectorStore:
    settings = get_settings()
    if backend == "pinecone":
        return PineconeStore(settings)
    if backend == "chroma":
        return ChromaStore(settings)
    raise ValueError(f"Unknown backend: {backend}")


def get_active_backend_name() -> str:
    settings = get_settings()
    return _active_backend_override or settings.vector_db


def get_active_store() -> VectorStore:
    return get_store(get_active_backend_name())


def get_ingest_service() -> IngestService:
    settings = get_settings()
    return IngestService(
        embedder=get_embedder(),
        csv_path=settings.csv_path,
        batch_size=settings.ingest_batch_size,
    )


def get_rag_service() -> RAGService:
    settings = get_settings()
    return RAGService(
        embedder=get_embedder(),
        store_provider=get_active_store,
        provider=settings.llm_provider,
        groq_api_key=settings.groq_api_key,
        groq_model=settings.llm_model,
        openai_api_key=settings.openai_api_key,
        openai_model=settings.openai_chat_model,
    )
