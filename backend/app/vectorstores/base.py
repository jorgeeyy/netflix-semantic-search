from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Match:
    id: str
    score: float
    metadata: dict = field(default_factory=dict)


class VectorStore(ABC):
    """Common interface implemented by the Pinecone and Chroma backends."""

    name: str

    @abstractmethod
    def upsert(
        self,
        ids: list[str],
        vectors: list[list[float]],
        metadatas: list[dict],
    ) -> int:
        """Store vectors with their metadata. Returns the number of records written."""

    @abstractmethod
    def query(self, vector: list[float], top_k: int) -> list[Match]:
        """Return the top_k most similar records for the given vector."""

    @abstractmethod
    def delete_all(self) -> None:
        """Remove every record from the store."""

    @abstractmethod
    def count(self) -> int:
        """Return the total number of records in the store."""
