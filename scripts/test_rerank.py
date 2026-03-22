import os
import sys
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from rag_engine.retrievers.vector_retriever import VectorRetriever
from rag_engine.retrievers.keyword_retriever import KeywordRetriever
from rag_engine.retrievers.hybrid_retriever import HybridRetriever
from rag_engine.rerank.llm_reranker import LLMReranker
from rag_engine.utils.db_client import DBClient
from rag_engine.utils.llm import OllamaLLM
from rag_engine.embeddings.ollama_embedder import OllamaEmbedder


async def main():
    print("=" * 60)
    print("🚀 PRODUCTION RETRIEVAL PIPELINE TEST")
    print("=" * 60)
    
    # Initialize Core Components
    embedder = OllamaEmbedder(model_name="nomic-embed-text")
    db_client = DBClient(dsn="postgresql://user:pass@localhost:5432/db")
    llm = OllamaLLM(model_name="mistral")

    vector_retriever = VectorRetriever(embedder, db_client)
    keyword_retriever = KeywordRetriever(db_client)
    
    # The hybrid retriever now searches wide (Top-K=15)
    hybrid_retriever = HybridRetriever(vector_retriever, keyword_retriever)
    
    # The reranker will precise narrow (Top-N=5)
    reranker = LLMReranker(llm)

    query = "How does self-attention work?"
    domain = "ai_ml"
    top_k = 15
    top_n = 5
    
    print(f"\n🧐 Query: '{query}'")
    print(f"⏳ Running Hybrid Retrieval (Top_K={top_k})...")
    
    hybrid_results = await hybrid_retriever.retrieve(query, top_k, domain)
    chunks_before = hybrid_results["chunks"]

    # Show noisy, pre-reranked result ranking
    print(f"\n{'-'*60}\n📡 BEFORE RERANKING (Hybrid Top-{top_k} Noise Sample)\n{'-'*60}")
    for i, c in enumerate(chunks_before[:top_n]):  # Just print first 5 to compare 
        source = c.get('metadata', {}).get('source_file', 'unknown')
        print(f"[{i+1}] Source: {source} | {c['content'][:150]}...")

    print(f"\n⏳ Passing all {len(chunks_before)} contexts through LLM Batch Reranker (Top_N={top_n})...")
    
    # Reranking magic
    chunks_after = await reranker.rerank(query=query, chunks=chunks_before, top_n=top_n)

    print(f"\n{'-'*60}\n🔥 AFTER RERANKING (LLM Precision Results)\n{'-'*60}")
    for i, c in enumerate(chunks_after):
        source = c.get('metadata', {}).get('source_file', 'unknown')
        print(f"[{i+1}] Source: {source} | {c['content'][:150]}...")

if __name__ == "__main__":
    asyncio.run(main())
