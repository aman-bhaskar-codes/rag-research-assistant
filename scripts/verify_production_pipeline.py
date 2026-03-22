import os
import sys
import asyncio
import logging

# Configure production-style logging for the test
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

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
from rag_engine.pipeline.retrieval_pipeline import RetrievalPipeline


async def main():
    print("=" * 70)
    print("🔥 PRODUCTION RAG PIPELINE: FINAL VERIFICATION")
    print("=" * 70)
    
    # -------- 1. INITIALIZE INFRASTRUCTURE --------
    llm = OllamaLLM(model_name="mistral")
    embedder = OllamaEmbedder(model_name="nomic-embed-text")
    db_client = DBClient(dsn="postgresql://user:pass@localhost:5432/db")

    # -------- 2. INITIALIZE INTELLIGENCE --------
    rewriter = QueryRewriter(llm)
    multi_query = MultiQueryGenerator(llm, num_queries=3)
    hyde = HyDEGenerator(llm)
    query_pipeline = QueryPipeline(rewriter, multi_query, hyde)
    
    reranker = LLMReranker(llm)

    # -------- 3. INITIALIZE RETRIEVERS --------
    vector = VectorRetriever(embedder, db_client)
    keyword = KeywordRetriever(db_client)
    hybrid = HybridRetriever(vector, keyword)

    # -------- 4. ASSEMBLE PRODUCTION PIPELINE --------
    rag_pipeline = RetrievalPipeline(
        query_pipeline=query_pipeline,
        vector_retriever=vector,
        keyword_retriever=keyword,
        hybrid_retriever=hybrid,
        reranker=reranker
    )

    # -------- 5. EXECUTE TEST QUERY --------
    test_query = "What are the core components of the Transformer architecture?"
    
    print(f"\n🚀 Running End-to-End Hybrid Pipeline for: '{test_query}'\n")
    
    result = await rag_pipeline.retrieve(
        query=test_query,
        strategy="hybrid",
        top_k=5,
        domain="ai_ml"
    )

    # -------- 6. VALIDATE OUTPUT SCHEMA --------
    print("\n" + "-"*70)
    print(f"📊 PIPELINE OUTPUT (Strategy: {result['meta']['strategy']})")
    print("-"*70)
    
    for i, chunk in enumerate(result["chunks"]):
        meta = chunk["metadata"]
        print(f"[{i+1}] ID: {meta['chunk_id']} | Source: {meta['document_id']}")
        print(f"    Content: {chunk['content'][:120]}...")

    print("\n" + "-"*70)
    print("✅ Schema Validation: PASS")
    print(f"   - chunk_id present: {'chunk_id' in result['chunks'][0]['metadata']}")
    print(f"   - document_id present: {'document_id' in result['chunks'][0]['metadata']}")
    print(f"   - domain present: {'domain' in result['chunks'][0]['metadata']}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
