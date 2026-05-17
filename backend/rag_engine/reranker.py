# backend/rag_engine/reranker.py
from functools import lru_cache
from sentence_transformers import CrossEncoder
from backend.rag_engine.retriever import RetrievedChunk


@lru_cache(maxsize=1)
def _get_reranker() -> CrossEncoder:
    # ms-marco is trained specifically for relevance ranking
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank(
    query: str,
    chunks: list[RetrievedChunk],
    top_n: int = 5,
) -> list[RetrievedChunk]:
    """
    Cross-encoder reads (query, chunk) as a PAIR simultaneously.
    Unlike bi-encoders (embed query separately, embed chunk separately),
    the cross-encoder sees both at once — much more accurate relevance score.
    Price: it is slower, so we only run it on the top_k = 20 candidates.
    """
    if not chunks:
        return []
    reranker = _get_reranker()
    pairs = [(query, c.content) for c in chunks]
    scores = reranker.predict(pairs)  # batch inference
    # Attach reranker score and sort
    for chunk, score in zip(chunks, scores):
        chunk.score = float(score)
    return sorted(chunks, key=lambda c: c.score, reverse=True)[:top_n]
