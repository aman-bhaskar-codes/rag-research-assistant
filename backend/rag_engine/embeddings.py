# backend/rag_engine/embeddings.py
from functools import lru_cache
from fastembed import TextEmbedding
import numpy as np

_MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"


@lru_cache(maxsize=1)
def _get_model() -> TextEmbedding:
    """Load once, cache forever in-process."""
    return TextEmbedding(_MODEL_NAME, max_length=512)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Batch-embed a list of strings → list of 768-d vectors."""
    model = _get_model()
    return [v.tolist() for v in model.embed(texts)]


def embed_query(text: str) -> list[float]:
    """Embed a single query string."""
    return embed_texts([text])[0]
