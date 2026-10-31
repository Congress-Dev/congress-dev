"""
Thin OpenAI embeddings client shared by the bill-text importer and the search
handler.

Embeddings are computed explicitly (not through a ChromaDB embedding function)
so the model used at index time and at query time is pinned in one place.
Changing EMBEDDING_MODEL requires rebuilding the ``legislation`` collection.
"""

import os
import time
from typing import List

import requests

EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = 1536
EMBEDDINGS_URL = os.environ.get(
    "OPENAI_EMBEDDINGS_URL", "https://api.openai.com/v1/embeddings"
)
# The API rejects batches over 2048 inputs / ~300k tokens total.
MAX_INPUTS_PER_REQUEST = 256
MAX_RETRIES = 5


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed ``texts`` and return vectors in the same order."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY must be set to compute embeddings")

    vectors: List[List[float]] = []
    for start in range(0, len(texts), MAX_INPUTS_PER_REQUEST):
        batch = texts[start : start + MAX_INPUTS_PER_REQUEST]
        vectors.extend(_embed_batch(batch, api_key))
    return vectors


def _embed_batch(batch: List[str], api_key: str) -> List[List[float]]:
    for attempt in range(MAX_RETRIES):
        resp = requests.post(
            EMBEDDINGS_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": EMBEDDING_MODEL, "input": batch},
            timeout=60,
        )
        if resp.status_code == 429 or resp.status_code >= 500:
            time.sleep(2**attempt)
            continue
        resp.raise_for_status()
        data = sorted(resp.json()["data"], key=lambda d: d["index"])
        return [d["embedding"] for d in data]
    resp.raise_for_status()
    raise RuntimeError("Embedding request failed after retries")
