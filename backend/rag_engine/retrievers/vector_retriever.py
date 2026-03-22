from typing import Dict, List
from .base import BaseRetriever


class VectorRetriever(BaseRetriever):
    """
    Core Intelligence Layer: Vector Retrieval Engine.
    Responsibilities: Embed query, call DB search, return structured chunks + meta.
    """
    
    def __init__(self, embedder, db_client):
        self.embedder = embedder
        self.db_client = db_client

    async def retrieve(self, query: str, top_k: int = 5, domain: str = "ai_ml") -> Dict:
        # Step 1: Embed query
        # Support both async and sync embedders seamlessly
        if hasattr(self.embedder, "embed_query"):
            query_embedding = await self.embedder.embed_query(query)
        else:
            # Fallback to standard embed_text if using OllamaEmbedder / GeminiEmbedder
            query_embedding = self.embedder.embed_text(query)

        if not query_embedding:
            raise ValueError("Query embedding failed")

        # Step 2: DB vector search
        results = await self.db_client.vector_search(
            embedding=query_embedding,
            top_k=top_k,
            domain=domain
        )

        # Step 3: Format output
        chunks = []
        for r in results:
            # Ensure mandatory production metadata exists
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
                "strategy": "vector",
                "top_k": top_k,
                "domain": domain
            }
        }
