import logging
from typing import List, Dict, Any, Optional
from rag_engine.retrievers.base import BaseRetriever

logger = logging.getLogger(__name__)


class RAGEngine(BaseRetriever):
    """
    The Ultimate RAG Engine Orchestrator.
    Unifies All Phases: [Query Transform] -> [Hybrid Retrieval] -> [LLM Reranking].
    Provides a single production-ready interface for the backend team.
    """
    
    def __init__(self, query_pipeline, retriever, reranker):
        self.query_pipeline = query_pipeline
        self.retriever = retriever
        self.reranker = reranker

    async def retrieve(self, query: str, top_k: int = 20, domain: str = "ai_ml") -> Dict[str, Any]:
        """
        Complete RAG Pipeline Execution.
        """
        # 1. Query Transformation (Rewrite, Multi-Query, HyDE)
        # Expands 1 query into ~5 distinct search signals.
        logger.info(f"Transforming query: {query}")
        expanded_queries = await self.query_pipeline.run(query)
        
        # 2. Aggregated Hybrid Retrieval
        # We fire the retriever for each expanded query and merge findings.
        all_chunks = []
        seen_ids = set()
        
        for q in expanded_queries:
            result = await self.retriever.retrieve(q, top_k=5, domain=domain)
            for chunk in result.get("chunks", []):
                # Simple deduplication based on content fingerprint
                # In production, use database primary keys (chunk_id).
                chunk_id = f"{chunk.get('metadata', {}).get('source_file')}_{chunk.get('metadata', {}).get('chunk_index')}"
                if chunk_id not in seen_ids:
                    all_chunks.append(chunk)
                    seen_ids.add(chunk_id)

        # 3. LLM Reranking (Precision Refinement)
        # Take the wide pool of high-recall chunks and narrow down to high-precision Top-N.
        logger.info(f"Retrieved {len(all_chunks)} unique candidate chunks. Reranking...")
        
        # We'll rerank the top 20 candidates into the final Top 5.
        top_n = 5
        reranked_chunks = await self.reranker.rerank(
            query=query, 
            chunks=all_chunks[:20], 
            top_n=top_n
        )

        return {
            "chunks": reranked_chunks,
            "meta": {
                "strategy": "intelligence_pipeline",
                "input_query": query,
                "expanded_queries_count": len(expanded_queries),
                "retrieved_total": len(all_chunks),
                "top_n": top_n
            }
        }
