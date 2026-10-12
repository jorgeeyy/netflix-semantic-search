from pinecone import Pinecone

from ..config import Settings
from .base import Match, VectorStore

UPSERT_BATCH_SIZE = 100


class PineconeStore(VectorStore):
    name = "pinecone"

    def __init__(self, settings: Settings):
        if not settings.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY is not set")
        self._pc = Pinecone(api_key=settings.pinecone_api_key)
        self._index_name = settings.pinecone_index
        self._namespace = settings.pinecone_namespace
        self._index = None

    @property
    def index(self):
        if self._index is None:
            self._index = self._pc.Index(self._index_name)
        return self._index

    def upsert(
        self,
        ids: list[str],
        vectors: list[list[float]],
        metadatas: list[dict],
    ) -> int:
        total = 0
        for start in range(0, len(ids), UPSERT_BATCH_SIZE):
            batch = list(
                zip(
                    ids[start : start + UPSERT_BATCH_SIZE],
                    vectors[start : start + UPSERT_BATCH_SIZE],
                    metadatas[start : start + UPSERT_BATCH_SIZE],
                )
            )
            self.index.upsert(vectors=batch, namespace=self._namespace)
            total += len(batch)
        return total

    def query(self, vector: list[float], top_k: int) -> list[Match]:
        response = self.index.query(
            vector=vector,
            top_k=top_k,
            namespace=self._namespace,
            include_metadata=True,
        )
        return [
            Match(
                id=match["id"],
                score=float(match["score"]),
                metadata=dict(match.get("metadata") or {}),
            )
            for match in response["matches"]
        ]

    def delete_all(self) -> None:
        self.index.delete(delete_all=True, namespace=self._namespace)

    def count(self) -> int:
        stats = self.index.describe_index_stats()
        namespaces = getattr(stats, "namespaces", None) or {}
        if self._namespace in namespaces:
            return int(namespaces[self._namespace].get("vector_count", 0))
        return int(getattr(stats, "total_vector_count", 0) or 0)
