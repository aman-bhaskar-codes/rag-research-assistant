from typing import List, Dict, Any
from .base import BaseRetriever


class VectorRetriever(BaseRetriever):
    """
    Core Intelligence Layer: Vector Retrieval Engine.
    Responsibilities: Embed query, call DB search, return structured chunks.
    No raw SQL allowed here.
    """
    
    def __init__(self, embedder, db_client):
        self.embedder = embedder
        self.db_client = db_client

    async def retrieve(self, query: str, top_k: int = 5, domain: str = "ai_ml") -> List[Dict[str, Any]]:
        # Step 1: Embed query
        # Support both async and sync embedders seamlessly
        if hasattr(self.embedder, "embed_query"):
            query_embedding = await self.embedder.embed_query(query)
        else:
            # Fallback to standard embed_text if using OllamaEmbedder / GeminiEmbedder
            query_embedding = self.embedder.embed_text(query)

        # Step 2: Search DB
        results = await self.db_client.vector_search(
            embedding=query_embedding,
            top_k=top_k,
            domain=domain
        )

        # Step 3: Format output
        formatted = []
        for r in results:
            formatted.append({
                "content": r["content"],
                "score": float(r["score"]),
                "metadata": r.get("metadata", {})
            })

        return formatted
