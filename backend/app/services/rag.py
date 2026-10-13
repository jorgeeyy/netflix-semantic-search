from openai import OpenAI

from .embedder import Embedder
from ..vectorstores.base import Match, VectorStore

SYSTEM_PROMPT = (
    "You answer questions about Netflix titles using ONLY the provided context.\n"
    "Rules:\n"
    "- Lead with the exact answer, as briefly as possible — often just the name, "
    "title, year, or fact that was asked for.\n"
    "- At most one short follow-up sentence for essential clarification.\n"
    "- Never list every field, never restate the context, never add preamble "
    "like 'According to the context'.\n"
    "- Context records that don't match the question are retrieval noise — "
    "ignore them silently.\n"
    "- Prefer a plain comma-separated list over a numbered list.\n"
    "- The sentence \"I don't have enough information to answer that.\" is ONLY "
    "for whole answers when nothing in the context is relevant. NEVER use it to "
    "fill slots in a list.\n"
    "Example: if asked for 5 Denzel Washington titles and the context's only "
    "matching records are Training Day and Safe House, answer exactly: "
    "\"Training Day and Safe House — the dataset only contains 2 titles "
    "featuring Denzel Washington.\""
)


def format_context(matches: list[Match]) -> str:
    blocks = []
    for i, match in enumerate(matches, start=1):
        meta = match.metadata
        blocks.append(
            f"[{i}] Title: {meta.get('title', '')} | Type: {meta.get('type', '')} | "
            f"Director: {meta.get('director', '')} | Cast: {meta.get('cast', '')} | "
            f"Country: {meta.get('country', '')} | Released: {meta.get('release_year', '')} | "
            f"Rating: {meta.get('rating', '')} | Duration: {meta.get('duration', '')} | "
            f"Genres: {meta.get('listed_in', meta.get('genres', ''))} | "
            f"Description: {meta.get('description', '')}"
        )
    return "\n\n".join(blocks)


class RAGService:
    def __init__(
        self,
        embedder: Embedder,
        store_provider,
        openai_api_key: str | None = None,
        openai_model: str = "gpt-4o-mini",
    ):
        self.embedder = embedder
        self.store_provider = store_provider  # callable -> VectorStore
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model

    def ask(self, question: str, top_k: int = 1) -> dict:
        store = self.store_provider()
        query_vector = self.embedder.embed_query(question)
        matches = store.query(query_vector, top_k)

        context = format_context(matches)
        client = OpenAI(api_key=self.openai_api_key)

        response = client.chat.completions.create(
            model=self.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}",
                },
            ],
            temperature=0,
        )

        answer = " ".join(response.choices[0].message.content.split())

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
