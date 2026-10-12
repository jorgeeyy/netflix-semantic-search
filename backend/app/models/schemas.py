from typing import Any, Literal

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500, examples=["movie about a deadly home invasion"])
    top_k: int = Field(default=5, ge=1, le=25)


class SearchResult(BaseModel):
    id: str
    score: float
    title: str = ""
    type: str = ""
    director: str = ""
    cast: str = ""
    country: str = ""
    release_year: str = ""
    rating: str = ""
    duration: str = ""
    genres: str = ""
    description: str = ""


class SearchResponse(BaseModel):
    query: str
    backend: str
    results: list[SearchResult]


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000, examples=["Which movies are about home invasions?"])
    top_k: int = Field(default=5, ge=1, le=15)


class Source(BaseModel):
    id: str
    score: float
    title: str = ""
    director: str = ""
    genres: str = ""
    description: str = ""


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]
    backend: str


class IngestRequest(BaseModel):
    wipe: bool = Field(default=False, description="Delete existing vectors before ingesting")
    backend: Literal["pinecone", "chroma"] | None = Field(
        default=None, description="Target backend; defaults to the active backend"
    )


class IngestResponse(BaseModel):
    status: str
    count: int
    backend: str
    elapsed_seconds: float


class HealthResponse(BaseModel):
    status: str
    backend: str
    vector_count: int | None


class MetaResponse(BaseModel):
    backends: list[str]
    active: str
    embedding_model: str
    embedding_dim: int
    llm_provider: str
    csv_path: str


class BackendRequest(BaseModel):
    backend: Literal["pinecone", "chroma"]


class ErrorResponse(BaseModel):
    detail: str
    extra: dict[str, Any] | None = None
