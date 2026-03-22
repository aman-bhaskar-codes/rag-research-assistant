import os
import sys
import asyncio
import logging

# Configure production-style logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Fix import path to include backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.services.memory_client import MemoryClient


async def main():
    print("=" * 80)
    print("🧠 SEMANTIC MEMORY END-TO-END TEST")
    print("=" * 80)
    
    client = MemoryClient()
    user_id = "00000000-0000-0000-0000-000000000001"
    session_id = "00000000-0000-0000-0000-000000000002"

    # Step 1: Save an important interaction
    print("\n1️⃣ Saving an interaction to long-term memory...")
    await client.save_interaction(
        user_id=user_id,
        session_id=session_id,
        query="My favorite programming language is Python and I love building RAG systems.",
        response="That's great! Python is perfect for RAG systems because of its library ecosystem."
    )
    
    # Wait for potential async tasks (though we call them directly)
    await asyncio.sleep(2)

    # Step 2: Try to retrieve it via semantic search
    print("\n2️⃣ Retrieving relevant memory for a related query...")
    memories = await client.get_relevant_memory(
        user_id=user_id,
        query="What programming language do I like for AI?"
    )
    
    print(f"📦 Memories Found: {len(memories)}")
    for i, m in enumerate(memories):
        print(f"✅ Memory {i+1}: {m[:100]}...")

    if memories:
        print("\n🎉 SUCCESS: Semantic memory correctly recalled the user's preference!")
    else:
        print("\n❌ FAILURE: No semantic memory found. Check database or embedder.")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
