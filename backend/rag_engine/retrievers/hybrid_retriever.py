from typing import Dict, List, Any
from .base import BaseRetriever
from .vector_retriever import VectorRetriever
from .keyword_retriever import KeywordRetriever
from rag_engine.fusion.rank_fusion import reciprocal_rank_fusion


class HybridRetriever(BaseRetriever):
    """
    Core Intelligence Layer: Hybrid Search Engine.
    Combines Vector Similarity (Semantic) and Keyword Matching (Exact).
    The Pinnacle of High-Quality RAG search systems.
    """

    def __init__(self, vector_retriever: VectorRetriever, keyword_retriever: KeywordRetriever):
        self.vector_retriever = vector_retriever
        self.keyword_retriever = keyword_retriever

    async def retrieve(self, query: str, top_k: int = 5, domain: str = "ai_ml") -> Dict:
        # Run both retrievals in tandem
        # In a very high performance scenario, these could be run concurrently via asyncio.gather().
        # But running them sequentially here is simple and clean.
        vector_results = await self.vector_retriever.retrieve(query, top_k * 2, domain)
        keyword_results = await self.keyword_retriever.retrieve(query, top_k * 2, domain)

        v_chunks = vector_results["chunks"]
        k_chunks = keyword_results["chunks"]

        # Fuse rankings using Reciprocal Rank Fusion
        fused_ids = reciprocal_rank_fusion([v_chunks, k_chunks])

        # Map IDs back to original chunks
        # Use our safe `source_file::chunk_index` lookup key matching `rank_fusion.py`
        all_chunks: Dict[str, Dict[str, Any]] = {}
        
        for c in v_chunks + k_chunks:
            meta = c.get("metadata", {})
            source = meta.get("source_file", "unknown")
            idx = meta.get("chunk_index", "unknown")
            if source != "unknown" and idx != "unknown":
                cid = f"{source}::{idx}"
            else:
                cid = c["content"]
                
            all_chunks[cid] = c

        # Extract the highest quality finalized chunks up to `top_k`
        final_chunks = []
        for cid in fused_ids[:top_k]:
            final_chunks.append(all_chunks[cid])

        return {
            "chunks": final_chunks,
            "meta": {
                "strategy": "hybrid",
                "top_k": top_k,
                "domain": domain
            }
        }
