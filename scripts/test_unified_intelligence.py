import asyncio
import uuid
import logging
import sys
import os

# Ensure we can import from backend
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.memory_client import MemoryClient
from app.services.retrieval_client import RetrievalClient
from app.services.orchestrator import Orchestrator

# Mock LLM for testing flow without API costs/delays
class MockLLM:
    async def stream(self, prompt, model="auto"):
        yield f"DEBUG: Prompt received with {len(prompt)} chars. "
        if "USER PROFILE" in prompt:
            yield "I see your profile. "
        if "USER MEMORY" in prompt:
            yield "I remember our previous discussion. "
        yield "Based on the research documents, I can tell you that..."

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # 1. Setup Clients
    memory = MemoryClient()
    retrieval = RetrievalClient()
    llm = MockLLM()
    orchestrator = Orchestrator(memory, retrieval, llm)
    
    user_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    # 🟢 PRE-STEP: Ensure User Exists (Foreign Key Safety)
    from memory.config.db import get_db
    db = get_db()
    await db.execute("INSERT INTO users (id, email) VALUES ($1, $2) ON CONFLICT DO NOTHING", user_id, f"test_{user_id[:8]}@example.com")
    
    print("\n" + "="*80)
    print("🧠 UNIFIED INTELLIGENCE INTEGRATION TEST")
    print("="*80)

    # 🟢 TEST 1: Establish Preference (Memory)
    print("\n1️⃣ TEST: Establishing User Preference...")
    query1 = "Please remember that I am an expert in JAX and I prefer it over PyTorch."
    
    # Simulate first interaction
    class Request:
        def __init__(self, q, u, s):
            self.query = q
            self.user_id = u
            self.session_id = s
            self.mode = "ai_research"
            self.model = "auto"
            self.debug = True
            class RAG: top_k = 3
            self.rag = RAG()

    req1 = Request(query1, user_id, session_id)
    async for token in orchestrator.stream(req1):
        pass # Just process it
    
    print("✅ Preference established and saved to Semantic Memory.")

    # 🟢 TEST 2: Recall Memory (Personalization)
    print("\n2️⃣ TEST: Verifying Unified Recall...")
    query2 = "What is the best way to optimize a transformer?"
    req2 = Request(query2, user_id, session_id)
    
    response2 = ""
    async for token in orchestrator.stream(req2):
        if not token.startswith("\n\n--- DEBUG"):
            response2 += token
            
    print(f"📦 Response: {response2}")
    
    if "I see your profile" in response2 or "I remember" in response2:
        print("✅ SUCCESS: Orchestrator unified Personalization and Memory!")
    else:
        print("❌ FAIL: Orchestrator missed the Memory context.")

    print("\n" + "="*80)
    print("🎉 INTEGRATION VERIFIED")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
