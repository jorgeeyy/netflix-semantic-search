from fastapi import APIRouter, HTTPException

from . import dependencies
from .config import get_settings
from .services.query_utils import detect_top_k
from .models.schemas import (
    AskRequest,
    AskResponse,
    BackendRequest,
    HealthResponse,
    IngestRequest,
    IngestResponse,
    MetaResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
)

router = APIRouter(prefix="/api")


def require_embedder():
    try:
        return dependencies.get_embedder()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    backend = dependencies.get_active_backend_name()
    try:
        count = dependencies.get_active_store().count()
    except Exception:
        count = None
    return HealthResponse(status="ok", backend=backend, vector_count=count)


@router.get("/meta", response_model=MetaResponse)
def meta() -> MetaResponse:
    settings = get_settings()
    return MetaResponse(
        backends=["pinecone", "chroma"],
        active=dependencies.get_active_backend_name(),
        embedding_model=settings.embedding_model,
        embedding_dim=settings.embedding_dim,
        llm_provider="openai",
        csv_path=settings.csv_path,
    )


@router.post("/backend", response_model=MetaResponse)
def switch_backend(body: BackendRequest) -> MetaResponse:
    dependencies.set_active_backend(body.backend)
    return meta()


@router.post("/search", response_model=SearchResponse)
def search(body: SearchRequest) -> SearchResponse:
    store = dependencies.get_active_store()
    embedder = require_embedder()
    top_k = body.top_k if body.top_k is not None else detect_top_k(body.query)
    vector = embedder.embed_query(body.query)
    matches = store.query(vector, top_k)

    results = [
        SearchResult(
            id=match.id,
            score=match.score,
            title=str(match.metadata.get("title", "")),
            type=str(match.metadata.get("type", "")),
            director=str(match.metadata.get("director", "")),
            cast=str(match.metadata.get("cast", "")),
            country=str(match.metadata.get("country", "")),
            release_year=str(match.metadata.get("release_year", "")),
            rating=str(match.metadata.get("rating", "")),
            duration=str(match.metadata.get("duration", "")),
            genres=str(match.metadata.get("listed_in", match.metadata.get("genres", ""))),
            description=str(match.metadata.get("description", "")),
        )
        for match in matches
    ]
    return SearchResponse(query=body.query, backend=store.name, results=results)


@router.post("/ask", response_model=AskResponse)
def ask(body: AskRequest) -> AskResponse:
    require_embedder()
    rag = dependencies.get_rag_service()
    top_k = body.top_k if body.top_k is not None else detect_top_k(body.question)
    result = rag.ask(body.question, top_k)
    return AskResponse(**result)


@router.post("/ingest", response_model=IngestResponse)
def ingest(body: IngestRequest) -> IngestResponse:
    backend = body.backend or dependencies.get_active_backend_name()
    try:
        store = dependencies.get_store(backend)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    ingest_service = dependencies.get_ingest_service()
    require_embedder()
    result = ingest_service.ingest(store, wipe=body.wipe)
    return IngestResponse(**result)
