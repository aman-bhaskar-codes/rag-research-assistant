import os
import sys
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from rag_engine.retrievers.vector_retriever import VectorRetriever
from rag_engine.retrievers.keyword_retriever import KeywordRetriever
from rag_engine.retrievers.hybrid_retriever import HybridRetriever
from rag_engine.utils.db_client import DBClient
from rag_engine.embeddings.ollama_embedder import OllamaEmbedder


async def main():
    print("=" * 60)
    print("🚀 MULTI-RETRIEVER SYSTEM TEST")
    print("=" * 60)
    
    # Initialize Core Components
    embedder = OllamaEmbedder(model_name="nomic-embed-text")
    db_client = DBClient(dsn="postgresql://user:pass@localhost:5432/db")

    vector_retriever = VectorRetriever(embedder, db_client)
    keyword_retriever = KeywordRetriever(db_client)
    hybrid_retriever = HybridRetriever(vector_retriever, keyword_retriever)

    query = "attention mechanism in transformers"
    domain = "ai_ml"
    top_k = 3
    
    print(f"\n🧐 Query: '{query}'")
    
    # ---------------------------------------------------------
    # TEST 1: VECTOR RETRIEVAL
    # ---------------------------------------------------------
    print(f"\n{'-'*60}\n🧠 1. VECTOR RETRIEVAL (Semantic)\n{'-'*60}")
    v_results = await vector_retriever.retrieve(query, top_k, domain)
    for i, chunk in enumerate(v_results["chunks"]):
        print(f"[{i+1}] Score: {chunk['score']:.4f} | {chunk['content'][:150]}...")

    # ---------------------------------------------------------
    # TEST 2: KEYWORD RETRIEVAL
    # ---------------------------------------------------------
    print(f"\n{'-'*60}\n📝 2. KEYWORD RETRIEVAL (Exact Match)\n{'-'*60}")
    k_results = await keyword_retriever.retrieve(query, top_k, domain)
    for i, chunk in enumerate(k_results["chunks"]):
        print(f"[{i+1}] Score: {chunk['score']:.4f} | {chunk['content'][:150]}...")

    # ---------------------------------------------------------
    # TEST 3: HYBRID RETRIEVAL (RRF)
    # ---------------------------------------------------------
    print(f"\n{'-'*60}\n🔥 3. HYBRID RETRIEVAL (Semantic + Keyword via RRF)\n{'-'*60}")
    h_results = await hybrid_retriever.retrieve(query, top_k, domain)
    print(f"Meta: {h_results['meta']}")
    for i, chunk in enumerate(h_results["chunks"]):
        # With RRF, the score returned here is the finalized chunk.
        # It maintains the original chunk metadata/content securely.
        print(f"[{i+1}] Source: {chunk.get('metadata', {}).get('source_file')} | {chunk['content'][:150]}...")


if __name__ == "__main__":
    asyncio.run(main())
