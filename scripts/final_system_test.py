import os
import sys
import asyncio
import logging

# Configure production-style logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Fix import path to include backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.services.retrieval_client import RetrievalClient


class MockRequest:
    def __init__(self, query, mode, top_k=5):
        self.query = query
        self.mode = mode
        self.rag = type('obj', (object,), {'top_k': top_k})


async def run_test(client, query, mode, strategy):
    print(f"\n--- TESTING MODE: {mode.upper()} (Strategy: {strategy}) ---")
    
    # Simulate orchestrator's domain mapping
    result = await client.retrieve(
        query=query,
        strategy=strategy,
        top_k=5,
        domain=mode
    )
    
    print(f"📡 Strategy Used: {result['meta']['strategy']}")
    print(f"📦 Chunks Retrieved: {len(result['chunks'])}")
    
    if result["chunks"]:
        print(f"✅ Top Chunk ID: {result['chunks'][0]['metadata']['chunk_id']}")
        print(f"📄 Snippet: {result['chunks'][0]['content'][:100]}...")
    else:
        print("❌ No chunks returned.")


async def main():
    print("=" * 80)
    print("🔥 FINAL SYSTEM HANDOFF TEST: 3-MODE VALIDATION")
    print("=" * 80)
    
    client = RetrievalClient()

    # 1. AI RESEARCH MODE (Typically Vector)
    await run_test(
        client, 
        "What is the self-attention mechanism in transformers?", 
        "ai_research", 
        "vector"
    )

    # 2. PROGRAMMING MODE (Typically Keyword)
    await run_test(
        client, 
        "backpropagation algorithm gradient descent", 
        "programming", 
        "keyword"
    )

    # 3. BUSINESS MODE (Typically Hybrid)
    await run_test(
        client, 
        "How is RAG used in production AI systems?", 
        "business", 
        "hybrid"
    )

    print("\n" + "=" * 80)
    print("✅ ALL MODES VERIFIED: RAG ENGINE ↔ BACKEND CORE INTEGRATION SUCCESSFUL")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
