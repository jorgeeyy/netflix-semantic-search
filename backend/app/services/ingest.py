import math
import time

import pandas as pd

from ..vectorstores.base import VectorStore
from .embedder import Embedder

METADATA_COLUMNS = [
    "type",
    "title",
    "director",
    "cast",
    "country",
    "date_added",
    "release_year",
    "rating",
    "duration",
    "listed_in",
    "description",
]

TEXT_COLUMNS = [
    "title",
    "type",
    "director",
    "cast",
    "country",
    "listed_in",
    "description",
]


def _clean_value(value) -> str | int | float | bool:
    if value is None or (isinstance(value, float) and math.isnan(value)) or pd.isna(value):
        return ""
    if hasattr(value, "item"):
        value = value.item()
    if not isinstance(value, (str, int, float, bool)):
        return str(value)
    return value


def build_text(row: pd.Series) -> str:
    return (
        f"Title: {row['title']}. Type: {row['type']}. Director: {row['director']}. "
        f"Cast: {row['cast']}. Country: {row['country']}. Genres: {row['listed_in']}. "
        f"Description: {row['description']}"
    )


def build_metadata(row: pd.Series) -> dict:
    metadata = {"show_id": str(row["show_id"])}
    for col in METADATA_COLUMNS:
        metadata[col] = _clean_value(row[col])
    return metadata


def load_dataset(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    for col in set(TEXT_COLUMNS) | set(METADATA_COLUMNS) | {"show_id"}:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)
    return df


class IngestService:
    def __init__(self, embedder: Embedder, csv_path: str, batch_size: int = 100):
        self.embedder = embedder
        self.csv_path = csv_path
        self.batch_size = batch_size

    def ingest(self, store: VectorStore, wipe: bool = False) -> dict:
        started = time.perf_counter()
        if wipe:
            store.delete_all()

        df = load_dataset(self.csv_path)
        ids: list[str] = []
        texts: list[str] = []
        metadatas: list[dict] = []

        for _, row in df.iterrows():
            ids.append(str(row["show_id"]))
            texts.append(build_text(row))
            metadatas.append(build_metadata(row))

        count = 0
        for start in range(0, len(ids), self.batch_size):
            batch_ids = ids[start : start + self.batch_size]
            batch_texts = texts[start : start + self.batch_size]
            batch_metadatas = metadatas[start : start + self.batch_size]
            vectors = self.embedder.embed_documents(batch_texts)
            count += store.upsert(batch_ids, vectors, batch_metadatas)

        return {
            "status": "ok",
            "count": count,
            "backend": store.name,
            "elapsed_seconds": round(time.perf_counter() - started, 2),
        }
