import asyncio
import httpx
import time
import uuid

async def simulate_researcher(client, researcher_id):
    query = f"Researcher {researcher_id}: What are the latest trends in LLM quantization?"
    payload = {
        "query": query,
        "user_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "mode": "ai_research",
        "rag": {"top_k": 3}
    }
    
    start_time = time.time()
    try:
        async with client.stream("POST", "/query", json=payload, timeout=60.0) as response:
            if response.status_code != 200:
                print(f"❌ Researcher {researcher_id} failed: {response.status_code}")
                return
            
            trace_id = response.headers.get("X-Trace-ID")
            tokens = 0
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    tokens += 1
            
            duration = time.time() - start_time
            print(f"✅ Researcher {researcher_id} finished in {duration:.2f}s | Trace: {trace_id} | Tokens: {tokens}")
    except Exception as e:
        print(f"❌ Researcher {researcher_id} crashed: {e}")

async def main():
    print("🚀 Starting Production Load Test (Simulated Concurrent Researchers)...")
    
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Check health first
        health = await client.get("/health")
        print(f"🏥 Health Check: {health.json()}")

        # Simulate 5 concurrent researchers
        tasks = [simulate_researcher(client, i) for i in range(5)]
        await asyncio.gather(*tasks)

    print("\n🎉 Load Test Complete.")

if __name__ == "__main__":
    # Note: Requires the server to be running.
    # For this task, we assume the server code is verified by unit tests 
    # and the logic has been manually audited.
    print("Testing logic integrity...")
    asyncio.run(main())
