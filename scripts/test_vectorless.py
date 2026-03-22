import os
import sys
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from rag_engine.retrievers.keyword_retriever import KeywordRetriever
from rag_engine.retrievers.vectorless_retriever import VectorlessRetriever
from rag_engine.utils.db_client import DBClient
from rag_engine.utils.llm import OllamaLLM


async def main():
    print("=" * 60)
    print("🚀 VECTORLESS RAG MODE TEST (Zero-Embedding Intelligence)")
    print("=" * 60)
    
    # Initialize components (No Embedder needed!)
    llm = OllamaLLM(model_name="mistral")
    db_client = DBClient(dsn="postgresql://user:pass@localhost:5432/db")
    keyword_retriever = KeywordRetriever(db_client)

    # Initialize the Vectorless Retriever
    vectorless_retriever = VectorlessRetriever(llm, keyword_retriever)

    query = "attention mechanism in transformer architecture"
    print(f"\n🧐 Query: '{query}'")
    print("⏳ Prompting LLM for high-precision technical keyword extraction...")
    
    result = await vectorless_retriever.retrieve(query, top_k=3, domain="ai_ml")
    
    print(f"\n{'-'*60}\n📡 VECTORLESS RESULTS (Strategy: {result['meta'].get('strategy')})\n{'-'*60}")
    print(f"Extracted Keywords: {result['meta'].get('extracted_keywords')}\n")
    
    for i, c in enumerate(result["chunks"]):
        source = c.get('metadata', {}).get('source_file', 'unknown')
        print(f"[{i+1}] Source: {source} | {c['content'][:150]}...")


if __name__ == "__main__":
    asyncio.run(main())
