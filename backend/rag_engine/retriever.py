from dataclasses import dataclass, field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.rag_engine.embeddings import embed_query
from backend.app.config import get_settings

settings = get_settings()
RRF_K = 60  # Reciprocal Rank Fusion constant (from original paper)


@dataclass
class RetrievedChunk:
    chunk_id: str
    content: str
    score: float
    meta: dict = field(default_factory=dict)
    source: str = "rag"


async def vector_search(
    vector: list[float],
    session: AsyncSession,
    top_k: int = 20,
    domain: str | None = None,
) -> list[tuple[str, str, dict, float]]:
    domain_filter = "AND meta->>'domain' = :domain" if domain else ""
    rows = await session.execute(text(f"""
        SELECT id::text, content, meta,
               1 - (embedding <=> :vec::vector) AS score
        FROM chunks
        WHERE 1=1 {domain_filter}
        ORDER BY embedding <=> :vec::vector
        LIMIT :k
    """), {"vec": str(vector), "k": top_k, **({"domain": domain} if domain else {})})
    return rows.fetchall()


async def bm25_search(
    query: str,
    session: AsyncSession,
    top_k: int = 20,
    domain: str | None = None,
) -> list[tuple[str, str, dict, float]]:
    domain_filter = "AND meta->>'domain' = :domain" if domain else ""
    rows = await session.execute(text(f"""
        SELECT id::text, content, meta,
               ts_rank(to_tsvector('english', content),
                       plainto_tsquery('english', :q)) AS score
        FROM chunks
        WHERE to_tsvector('english', content) @@ plainto_tsquery('english', :q)
        {domain_filter}
        ORDER BY score DESC
        LIMIT :k
    """), {"q": query, "k": top_k, **({"domain": domain} if domain else {})})
    return rows.fetchall()


async def retrieve(
    query: str,
    session: AsyncSession,
    top_k: int | None = None,
    domain: str | None = None,
) -> list[RetrievedChunk]:
    top_k = top_k or settings.rag_top_k

    # Embed query
    vector = embed_query(query)

    # Run both retrievers in parallel
    import asyncio
    vector_rows, bm25_rows = await asyncio.gather(
        vector_search(vector, session, top_k, domain),
        bm25_search(query, session, top_k, domain),
    )

    # RRF Fusion
    scores: dict[str, float] = {}
    data: dict[str, tuple[str, dict]] = {}

    for rank, row in enumerate(vector_rows):
        scores[row[0]] = scores.get(row[0], 0) + 1 / (RRF_K + rank + 1)
        data[row[0]] = (row[1], row[2] or {})

    for rank, row in enumerate(bm25_rows):
        scores[row[0]] = scores.get(row[0], 0) + 1 / (RRF_K + rank + 1)
        data[row[0]] = (row[1], row[2] or {})

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return [
        RetrievedChunk(
            chunk_id=cid,
            content=data[cid][0],
            score=score,
            meta=data[cid][1],
        )
        for cid, score in ranked[:top_k]
    ]
