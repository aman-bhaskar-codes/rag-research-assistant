import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from app.services.memory_client import MemoryClient
from memory.config.db import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_adaptive_memory")


async def main():
    print("\n" + "="*80)
    print("🧠 ADAPTIVE MEMORY & PERSONALIZATION TEST")
    print("="*80)
    
    client = MemoryClient()
    user_id = "00000000-0000-0000-0000-000000000001" # Existing test user
    session_id = "00000000-0000-0000-0000-000000000003"
    
    # Step 1: Establish a Personalization Trait
    print("\n1️⃣ Learning user preference...")
    await client.personalization.learn_preference(user_id, "expertise_level", "Senior Research Scientist")
    await client.personalization.learn_preference(user_id, "primary_focus", "Large Language Models")
    
    context = await client.get_user_context(user_id)
    print(f"📦 Learned Context:\n{context}")
    
    # Step 2: Save High-Importance Interaction
    print("\n2️⃣ Saving high-importance memory (triggering 'remember' keyword)...")
    await client.save_interaction(
        user_id, 
        session_id, 
        "Please remember that I prefer JAX over PyTorch for high-performance computing.", 
        "Understood. I will prioritize JAX in our technical discussions."
    )
    
    # Small delay for async processing
    await asyncio.sleep(2)
    
    # Step 3: Verify Adaptive Ranking
    print("\n3️⃣ Testing Adaptive Recall (Ranking)...")
    # This query should trigger the "JAX" memory with high score because of importance keyword and similarity
    memories = await client.get_relevant_memory(user_id, "What are my HPC preferences?")
    
    print(f"📦 Memories Found: {len(memories)}")
    for i, m in enumerate(memories):
        print(f"✅ Memory {i+1}: {m[:100]}...")
        
    if any("JAX" in m for m in memories):
        print("\n🎉 SUCCESS: Adaptive memory correctly recalled and ranked the interaction!")
    else:
        print("\n❌ FAIL: High-importance memory was not prioritized correctly.")

    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())
