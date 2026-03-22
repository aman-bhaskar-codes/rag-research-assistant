import os
import sys
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from rag_engine.retrievers.vector_retriever import VectorRetriever
from rag_engine.embeddings.ollama_embedder import OllamaEmbedder

# ---------------------------------------------------------
# MOCK DB CLIENT (Since Memory team hasn't built it yet)
# ---------------------------------------------------------
class MockMemoryDBClient:
    async def vector_search(self, embedding: list[float], top_k: int, domain: str):
        print(f"   [Mock DB] Executing pgvector <-> search...")
        print(f"   [Mock DB] Received embedding of dimension {len(embedding)}")
        print(f"   [Mock DB] Filtering by domain: {domain}")
        print(f"   [Mock DB] Limiting to top {top_k} results")
        
        # Return mock structured results simulating pgvector L2 distance matches
        return [
            {
                "content": "Transformer architecture is based on self-attention mechanisms allowing models to process sequences in parallel and capture long-range dependencies effectively.",
                "score": 0.12,
                "metadata": {"source": "attention_is_all_you_need.pdf"}
            },
            {
                "content": "Unlike RNNs, the self-attention layers in Transformers do not rely on sequential processing, drastically reducing training times on TPU clusters.",
                "score": 0.18,
                "metadata": {"source": "attention_is_all_you_need.pdf"}
            }
        ]

# ---------------------------------------------------------
# TEST HARNESS
# ---------------------------------------------------------
async def test():
    print("=" * 60)
    print("🚀 CORE INTELLIGENCE LAYER: Vector Retrieval Test")
    print("=" * 60)
    
    # 1. Initialize real embedder & mock DB
    embedder = OllamaEmbedder(model_name="nomic-embed-text")
    db_client = MockMemoryDBClient()

    # 2. Inject into core retriever (Clean Architecture)
    retriever = VectorRetriever(embedder, db_client)

    # 3. Execute retrieval
    print(f"🧐 Querying: 'What is transformer architecture?'\n")
    results = await retriever.retrieve(
        query="What is transformer architecture?",
        top_k=5,
        domain="ai_ml"
    )

    # 4. Display exact outputs
    print("=" * 60)
    print("📊 RESULT RANKING")
    
    for i, r in enumerate(results):
        print(f"\nResult {i+1}")
        print(f"Score: {r['score']}")
        print(f"Text: {r['content'][:200]}")

if __name__ == "__main__":
    asyncio.run(test())
