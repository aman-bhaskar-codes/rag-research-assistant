from functools import lru_cache
from sentence_transformers import CrossEncoder
from backend.rag_engine.retriever import RetrievedChunk
from backend.app.config import get_settings

settings = get_settings()


@lru_cache(maxsize=1)
def _get_reranker() -> CrossEncoder:
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank(
    query: str,
    chunks: list[RetrievedChunk],
    top_n: int | None = None,
) -> list[RetrievedChunk]:
    top_n = top_n or settings.rag_top_n
    if not chunks:
        return []

    reranker = _get_reranker()
    pairs = [(query, c.content) for c in chunks]
    scores = reranker.predict(pairs)

    for chunk, score in zip(chunks, scores):
        chunk.score = float(score)

    return sorted(chunks, key=lambda c: c.score, reverse=True)[:top_n]
