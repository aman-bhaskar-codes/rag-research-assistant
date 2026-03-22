import logging
from typing import Dict, List, Any, Optional
from rag_engine.retrievers.base import BaseRetriever

# Standard production logger
logger = logging.getLogger(__name__)


class RetrievalPipeline:
    """
    The Single Source of Truth for RAG Retrieval.
    Orchestrates the entire lifecycle: [Transform] -> [Retrieve] -> [Fusion] -> [Rerank].
    Designed for Backend Core Team consumption.
    """
    
    def __init__(self, query_pipeline, vector_retriever, keyword_retriever, hybrid_retriever, reranker):
        self.query_pipeline = query_pipeline
        self.vector_retriever = vector_retriever
        self.keyword_retriever = keyword_retriever
        self.hybrid_retriever = hybrid_retriever
        self.reranker = reranker

    async def retrieve(
        self, 
        query: str, 
        strategy: str = "hybrid", 
        top_k: int = 20, 
        domain: str = "ai_ml"
    ) -> Dict[str, Any]:
        """
        Hardened Production Retrieval Pipeline.
        Args:
            query: The user's raw input.
            strategy: ["vector", "keyword", "hybrid"]
            top_k: Number of candidates to retrieve initially.
            domain: Domain filter.
            
        Returns:
            Standardized dict with chunks and metadata.
        """
        logger.info(f"[RETRIEVAL] Incoming Query: '{query}' | Strategy: {strategy}")

        # 1. Query Transformation (Intelligence Phase)
        # Safe fallback: Always includes original query if LLM fails.
        expanded_queries = await self.query_pipeline.run(query, max_queries=5)
        logger.info(f"[TRANSFORM] Generated {len(expanded_queries)} optimized queries.")

        # 2. Select Retrieval Engine based on strategy
        if strategy == "vector":
            retriever = self.vector_retriever
        elif strategy == "keyword":
            retriever = self.keyword_retriever
        else:
            retriever = self.hybrid_retriever

        # 3. Aggregate Results across all expanded queries
        # Deduplication is handled by chunk_id
        all_chunks_map: Dict[str, Dict[str, Any]] = {}
        
        for q in expanded_queries:
            try:
                # We pull top_k candidates for EACH expanded query to ensure high recall
                # This results in a wide pool of candidates for the reranker.
                result = await retriever.retrieve(q, top_k=top_k, domain=domain)
                for chunk in result.get("chunks", []):
                    cid = chunk["metadata"]["chunk_id"]
                    if cid not in all_chunks_map:
                        all_chunks_map[cid] = chunk
            except Exception as e:
                logger.error(f"[ERROR] Retriever failed for query '{q}': {e}")
                # Fallback: Keyword might fail if PG is down, but we continue with other queries.
                continue

        all_unique_chunks = list(all_chunks_map.values())
        logger.info(f"[RETRIEVER] Pool contains {len(all_unique_chunks)} unique candidate chunks.")

        # 4. LLM Reranking (Precision Phase)
        # If reranker fails, we still return the raw retrieval results (High Recall is better than nothing).
        top_n = 5
        try:
            # We rerank the top 20 candidates from the pool
            final_chunks = await self.reranker.rerank(
                query=query, 
                chunks=all_unique_chunks[:20], 
                top_n=top_n
            )
            strategy_tag = f"{strategy}_reranked"
        except Exception as e:
            logger.warning(f"[RERANK FAIL] Defaulting to raw retrieval: {e}")
            final_chunks = all_unique_chunks[:top_n]
            strategy_tag = f"{strategy}_raw"

        logger.info(f"[SUCCESS] Returning {len(final_chunks)} high-precision chunks.")

        return {
            "chunks": final_chunks,
            "meta": {
                "strategy": strategy_tag,
                "input_queries": expanded_queries,
                "retrieved_total": len(all_unique_chunks),
                "top_k": top_k,
                "top_n": top_n
            }
        }


# Singleton-style cached pipeline for functional access
_PIPELINE = None


async def retrieve(query: str, strategy: str = "hybrid", top_k: int = 20, domain: str = "ai_ml") -> Dict[str, Any]:
    """
    Exposed functional interface for Backend Core.
    Initializes the optimized RAG stack on first call.
    """
    global _PIPELINE
    
    if _PIPELINE is None:
        from rag_engine.utils.llm import OllamaLLM
        from rag_engine.embeddings.ollama_embedder import OllamaEmbedder
        from rag_engine.utils.db_client import DBClient
        from rag_engine.retrievers.vector_retriever import VectorRetriever
        from rag_engine.retrievers.keyword_retriever import KeywordRetriever
        from rag_engine.retrievers.hybrid_retriever import HybridRetriever
        from rag_engine.query.rewrite import QueryRewriter
        from rag_engine.query.multi_query import MultiQueryGenerator
        from rag_engine.query.hyde import HyDEGenerator
        from rag_engine.query.pipeline import QueryPipeline
        from rag_engine.rerank.llm_reranker import LLMReranker
        
        # 1. Init Infra
        llm = OllamaLLM()
        embedder = OllamaEmbedder()
        db_client = DBClient(dsn="postgresql://user:pass@localhost:5432/db")

        # 2. Init Intelligence
        rewriter = QueryRewriter(llm)
        multi_query = MultiQueryGenerator(llm)
        hyde = HyDEGenerator(llm)
        query_pipe = QueryPipeline(rewriter, multi_query, hyde)
        reranker = LLMReranker(llm)

        # 3. Init Retrievers
        vector = VectorRetriever(embedder, db_client)
        keyword = KeywordRetriever(db_client)
        hybrid = HybridRetriever(vector, keyword)

        # 4. Final Pipeline
        _PIPELINE = RetrievalPipeline(
            query_pipe,
            vector,
            keyword,
            hybrid,
            reranker
        )

    return await _PIPELINE.retrieve(query, strategy, top_k, domain)
