import os
import json
import logging
from typing import List, Dict, Any

try:
    import asyncpg
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False

logger = logging.getLogger(__name__)


class DBClient:
    """
    Database client for pgvector similarity search.
    Provides a resilient fallback to the local FAISS index if Postgres
    is not yet running/populated by the Memory team.
    """
    def __init__(self, dsn: str):
        self.dsn = dsn

    async def vector_search(self, embedding: list[float], top_k: int, domain: str) -> List[Dict[str, Any]]:
        # Attempt to connect to Postgres if URL is real
        if HAS_ASYNCPG and not self.dsn.endswith("localhost:5432/db"):
            try:
                conn = await asyncpg.connect(self.dsn)
                try:
                    # Using <=> for cosine distance or <-> for L2 distance.
                    # As requested, using the exact SQL abstraction:
                    query = """
                    SELECT content, metadata,
                           embedding <-> $1 AS score
                    FROM document_chunks
                    WHERE metadata->>'domain' = $2
                    ORDER BY embedding <-> $1
                    LIMIT $3;
                    """
                    rows = await conn.fetch(query, embedding, domain, top_k)
                    return [
                        {
                            "content": r["content"],
                            "metadata": r.get("metadata", {}),
                            "score": r["score"]
                        }
                        for r in rows
                    ]
                finally:
                    await conn.close()
            except Exception as e:
                logger.warning(f"Postgres connection failed ({e}). Falling back to FAISS index.")
        
        # -------------------------------------------------------------
        # FALLBACK: Use the massive FAISS index we just generated
        # -------------------------------------------------------------
        return self._faiss_fallback_search(embedding, top_k)

    async def keyword_search(self, query: str, top_k: int, domain: str) -> List[Dict[str, Any]]:
        if HAS_ASYNCPG and not self.dsn.endswith("localhost:5432/db"):
            try:
                conn = await asyncpg.connect(self.dsn)
                try:
                    sql = """
                    SELECT content, metadata,
                           ts_rank(tsv, plainto_tsquery($1)) AS score
                    FROM document_chunks
                    WHERE tsv @@ plainto_tsquery($1)
                      AND metadata->>'domain' = $2
                    ORDER BY score DESC
                    LIMIT $3;
                    """
                    rows = await conn.fetch(sql, query, domain, top_k)
                    return [
                        {
                            "content": r["content"],
                            "metadata": r.get("metadata", {}),
                            "score": r["score"]
                        }
                        for r in rows
                    ]
                finally:
                    await conn.close()
            except Exception as e:
                logger.warning(f"Postgres connection failed ({e}). Falling back to dummy keyword search.")

        # -------------------------------------------------------------
        # FALLBACK: Simulate basic substring keyword search across FAISS chunks
        # Because we don't have Postgres tsvector running locally yet
        # -------------------------------------------------------------
        return self._dummy_keyword_search(query, top_k)

    def _dummy_keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        import numpy as np
        
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/vector_store"))
        chunks_path = os.path.join(base_dir, "chunks.json")
        
        if not os.path.exists(chunks_path):
            raise RuntimeError("No chunks.json found for dummy keyword search.")
            
        with open(chunks_path, "r") as f:
            chunks = json.load(f)
            
        results = []
        # Basic case-insensitive text matching to simulate Exact Match
        query_terms = set(query.lower().split())
        
        for c in chunks:
            text = c["text"]
            text_lower = text.lower()
            
            # Simple keyword overlap scoring
            matches = sum(1 for term in query_terms if term in text_lower)
            if matches > 0:
                # Rank exactly by number of intersecting terms, plus a tiny fraction to break ties
                score = matches + (min(len(text), 1000) / 10000.0) 
                
                results.append({
                    "content": text,
                    "metadata": {
                        "source_file": c.get("source_file", "unknown"),
                        "chunk_index": c.get("chunk_index", "unknown")
                    },
                    "score": float(score)
                })
                
        # Sort descending by naive keyword score and take top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def _faiss_fallback_search(self, embedding: list[float], top_k: int) -> List[Dict[str, Any]]:
        import numpy as np
        import faiss
        
        # Resolve path to the vector store we built in the previous step
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/vector_store"))
        index_path = os.path.join(base_dir, "index.faiss")
        chunks_path = os.path.join(base_dir, "chunks.json")
        
        if not os.path.exists(index_path):
            raise RuntimeError(f"No FAISS index found at {index_path} and Postgres connection failed.")
            
        index = faiss.read_index(index_path)
        with open(chunks_path, "r") as f:
            chunks = json.load(f)
            
        xq = np.array([embedding]).astype('float32')
        distances, indices = index.search(xq, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue
            chunk_data = chunks[idx]
            results.append({
                "content": chunk_data["text"],
                "metadata": {
                    "source_file": chunk_data.get("source_file", "unknown"),
                    "chunk_index": chunk_data.get("chunk_index", "unknown")
                },
                "score": float(distances[0][i])
            })
            
        return results
