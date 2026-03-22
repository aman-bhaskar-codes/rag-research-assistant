from typing import Dict, List
from .base import BaseRetriever


class KeywordRetriever(BaseRetriever):
    """
    Core Intelligence Layer: Keyword Retrieval Engine.
    Responsibilities: Exact Match SQL via PostgreSQL full-text search (tsvector).
    """

    def __init__(self, db_client):
        self.db_client = db_client

    async def retrieve(self, query: str, top_k: int = 5, domain: str = "ai_ml") -> Dict:
        results = await self.db_client.keyword_search(
            query=query,
            top_k=top_k,
            domain=domain
        )

        chunks = []
        for r in results:
            metadata = r.get("metadata", {})
            chunk_id = metadata.get("chunk_id") or f"{metadata.get('source_file')}_{metadata.get('chunk_index')}"
            
            chunks.append({
                "content": r["content"],
                "score": float(r["score"]),
                "metadata": {
                    "chunk_id": chunk_id,
                    "document_id": metadata.get("source_file"),
                    "domain": domain,
                    **metadata
                }
            })

        return {
            "chunks": chunks,
            "meta": {
                "strategy": "keyword",
                "top_k": top_k,
                "domain": domain
            }
        }
