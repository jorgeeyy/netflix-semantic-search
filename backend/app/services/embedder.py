from openai import OpenAI

EMBED_BATCH_SIZE = 100


class Embedder:
    """Thin wrapper around the OpenAI embeddings API."""

    def __init__(self, api_key: str, model: str, dimensions: int):
        self._client = OpenAI(api_key=api_key)
        self.model = model
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), EMBED_BATCH_SIZE):
            batch = texts[start : start + EMBED_BATCH_SIZE]
            response = self._client.embeddings.create(
                input=batch,
                model=self.model,
                dimensions=self.dimensions,
            )
            vectors.extend(item.embedding for item in response.data)
        return vectors

    def embed_query(self, text: str) -> list[float]:
        response = self._client.embeddings.create(
            input=[text],
            model=self.model,
            dimensions=self.dimensions,
        )
        return response.data[0].embedding
