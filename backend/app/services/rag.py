from openai import OpenAI

from ..vectorstores.base import Match
from .embedder import Embedder
from ..vectorstores.base import VectorStore

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions about Netflix titles. "
    "Use ONLY the provided context to answer the question. "
    "If the context does not contain the answer, say you don't have enough information. "
    "Mention the titles you base your answer on."
)


def format_context(matches: list[Match]) -> str:
    blocks = []
    for i, match in enumerate(matches, start=1):
        meta = match.metadata
        blocks.append(
            f"[{i}] Title: {meta.get('title', '')} | Type: {meta.get('type', '')} | "
            f"Director: {meta.get('director', '')} | Genres: {meta.get('listed_in', meta.get('genres', ''))} | "
            f"Description: {meta.get('description', '')}"
        )
    return "\n\n".join(blocks)


class RAGService:
    def __init__(
        self,
        embedder: Embedder,
        store_provider,
        provider: str = "groq",
        groq_api_key: str | None = None,
        groq_model: str = "llama-3.3-70b-versatile",
        openai_api_key: str | None = None,
        openai_model: str = "gpt-4o-mini",
    ):
        self.embedder = embedder
        self.store_provider = store_provider  # callable -> VectorStore
        self.provider = provider
        self.groq_api_key = groq_api_key
        self.groq_model = groq_model
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model

    def _get_client(self):
        if self.provider == "groq" and self.groq_api_key:
            return (
                OpenAI(api_key=self.groq_api_key, base_url="https://api.groq.com/openai/v1"),
                self.groq_model,
            )
        return OpenAI(api_key=self.openai_api_key), self.openai_model

    def ask(self, question: str, top_k: int = 5) -> dict:
        store = self.store_provider()
        query_vector = self.embedder.embed_query(question)
        matches = store.query(query_vector, top_k)

        context = format_context(matches)
        client, model = self._get_client()

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}",
                },
            ],
            temperature=0.2,
        )

        answer = response.choices[0].message.content.strip()

        sources = [
            {
                "id": match.id,
                "score": match.score,
                "title": match.metadata.get("title", ""),
                "director": match.metadata.get("director", ""),
                "genres": match.metadata.get("listed_in", match.metadata.get("genres", "")),
                "description": match.metadata.get("description", ""),
            }
            for match in matches
        ]

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "backend": store.name,
        }
