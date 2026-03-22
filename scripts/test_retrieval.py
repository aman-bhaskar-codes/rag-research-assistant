import os
import sys
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from rag_engine.retrievers.vector_retriever import VectorRetriever
from rag_engine.utils.db_client import DBClient
from rag_engine.embeddings.ollama_embedder import OllamaEmbedder


async def main():
    print("=" * 60)
    print("🚀 CORE INTELLIGENCE LAYER: Vector Retrieval Test")
    print("=" * 60)
    
    # Initialize embedder and generic DB client interface
    embedder = OllamaEmbedder(model_name="nomic-embed-text")
    
    # DBClient uses the provided pgvector query, with a FAISS
    # fallback internally to allow this test script to work over
    # the 2,388 document chunks before the memory team spins up postgres.
    db_client = DBClient(dsn="postgresql://user:pass@localhost:5432/db")

    retriever = VectorRetriever(embedder, db_client)

    print(f"🧐 Querying: 'What is transformer architecture?'\n")
    
    result = await retriever.retrieve(
        query="What is transformer architecture?",
        top_k=5,
        domain="ai_ml"
    )

    print("\n📊 META:", result["meta"])

    for i, chunk in enumerate(result["chunks"]):
        print(f"\n🔹 Result {i+1}")
        print("Score:", chunk["score"])
        print("Text:", chunk["content"][:200])


if __name__ == "__main__":
    asyncio.run(main())
