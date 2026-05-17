# backend/rag_engine/retriever.py
from dataclasses import dataclass
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.rag_engine.embeddings import embed_query
from backend.rag_engine.hyde import generate_hyde_doc


@dataclass
class RetrievedChunk:
    chunk_id: str
    content: str
    score: float
    meta: dict


K = 60  # RRF constant — recommended by the original paper


async def retrieve(
    query: str,
    session: AsyncSession,
    top_k: int = 20,
    mode: str = "hybrid",
    use_hyde: bool = True,
) -> list[RetrievedChunk]:
    """
    Hybrid retrieval pipeline:
    1. Optionally expand query via HyDE
    2. Run pgvector cosine search
    3. Run PostgreSQL full-text BM25 search
    4. Fuse rankings via Reciprocal Rank Fusion (RRF)
    """
    # ── Step 1: Query expansion ──────────────────────────────────
    if use_hyde:
        hyde_doc = await generate_hyde_doc(query)
        embed_input = hyde_doc
    else:
        embed_input = query

    vector = embed_query(embed_input)

    # ── Step 2: Vector search (pgvector cosine distance) ─────────
    vector_results = await session.execute(text("""
        SELECT id::text, content, meta,
               1 - (embedding <=> :vec::vector) AS score
        FROM chunks
        ORDER BY embedding <=> :vec::vector
        LIMIT :k
    """), {"vec": str(vector), "k": top_k})
    vector_rows = vector_results.fetchall()

    # ── Step 3: BM25 full-text search (tsvector) ─────────────────
    bm25_results = await session.execute(text("""
        SELECT id::text, content, meta,
               ts_rank(to_tsvector('english', content),
                       plainto_tsquery('english', :q)) AS score
        FROM chunks
        WHERE to_tsvector('english', content)
              @@ plainto_tsquery('english', :q)
        ORDER BY score DESC
        LIMIT :k
    """), {"q": query, "k": top_k})
    bm25_rows = bm25_results.fetchall()

    # ── Step 4: RRF Fusion ───────────────────────────────────────
    scores: dict[str, float] = {}
    contents: dict[str, tuple[str, dict]] = {}

    for rank, row in enumerate(vector_rows):
        scores[row.id] = scores.get(row.id, 0) + 1 / (K + rank + 1)
        contents[row.id] = (row.content, row.meta)

    for rank, row in enumerate(bm25_rows):
        scores[row.id] = scores.get(row.id, 0) + 1 / (K + rank + 1)
        contents[row.id] = (row.content, row.meta)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return [
        RetrievedChunk(
            chunk_id=cid,
            content=contents[cid][0],
            score=score,
            meta=contents[cid][1],
        )
        for cid, score in ranked[:top_k]
    ]
