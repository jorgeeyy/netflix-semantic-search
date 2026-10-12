import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from ..config import Settings
from .base import Match, VectorStore


class ChromaStore(VectorStore):
    name = "chroma"

    def __init__(self, settings: Settings):
        self._client = chromadb.PersistentClient(path=settings.chroma_path)
        self._collection_name = settings.chroma_collection
        self._embedding_function = OpenAIEmbeddingFunction(
            model_name=settings.embedding_model,
            api_key=settings.openai_api_key,
        )
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            embedding_function=self._embedding_function,
        )

    @property
    def collection(self):
        # Re-fetch in case delete_all() recreated the collection.
        if self._collection is None:
            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                embedding_function=self._embedding_function,
            )
        return self._collection

    @collection.setter
    def collection(self, value):
        self._collection = value

    @staticmethod
    def _score_from_distance(distance: float, space: str | None) -> float:
        # Chroma defaults to l2. OpenAI embeddings are unit-normalized, so
        # cosine distance == l2^2 / 2 and similarity == 1 - l2^2 / 2.
        if space == "cosine":
            similarity = 1.0 - distance
        else:
            similarity = 1.0 - (distance**2) / 2.0
        return max(0.0, min(1.0, similarity))

    def upsert(
        self,
        ids: list[str],
        vectors: list[list[float]],
        metadatas: list[dict],
    ) -> int:
        self.collection.upsert(
            ids=ids,
            embeddings=vectors,
            metadatas=metadatas,
        )
        return len(ids)

    def query(self, vector: list[float], top_k: int) -> list[Match]:
        result = self.collection.query(
            query_embeddings=[vector],
            n_results=top_k,
            include=["metadatas", "documents", "distances"],
        )
        metadata = self.collection.metadata or {}
        space = (metadata.get("hnsw:space") or metadata.get("space") or "l2").lower()

        matches: list[Match] = []
        ids = result.get("ids", [[]])[0]
        distances = result.get("distances", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        documents = result.get("documents", [[]])[0]

        for match_id, distance, meta, document in zip(ids, distances, metadatas, documents):
            record_meta = dict(meta or {})
            if document:
                record_meta.setdefault("text", document)
                # Legacy records from the notebook stored everything in the
                # document text with no metadata; parse it back out so the
                # API can still surface title/director/etc.
                if "title" not in record_meta or not record_meta["title"]:
                    for line in document.strip().splitlines():
                        if ": " in line:
                            key, _, value = line.partition(": ")
                            record_meta.setdefault(key.strip().lower().replace(" ", "_"), value.strip())
            matches.append(
                Match(
                    id=match_id,
                    score=self._score_from_distance(float(distance), space),
                    metadata=record_meta,
                )
            )
        return matches

    def delete_all(self) -> None:
        try:
            self._client.delete_collection(self._collection_name)
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            embedding_function=self._embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        return self.collection.count()
