import os
import sys
import asyncio
import httpx

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from rag_engine.query.rewrite import QueryRewriter
from rag_engine.query.multi_query import MultiQueryGenerator
from rag_engine.query.hyde import HyDEGenerator
from rag_engine.query.pipeline import QueryPipeline
from rag_engine.utils.llm import OllamaLLM


async def main():
    print("=" * 60)
    print("🧠 CORE INTELLIGENCE LAYER: Query Transform Pipeline")
    print("=" * 60)

    # Initialize the local LLM using Llama3 (must have Ollama running locally)
    llm = OllamaLLM(model_name="mistral")
    
    # Quick health check if the model is alive
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.get(f"{llm.base_url}")
    except Exception:
        print("⚠️  Warning: Ollama server is not reachable at localhost:11434.")
        print("⚠️  Please start Ollama to run the Query Transformers.")
        sys.exit(1)

    rewriter = QueryRewriter(llm)
    multi_query = MultiQueryGenerator(llm, num_queries=3)
    hyde = HyDEGenerator(llm)

    pipeline = QueryPipeline(rewriter, multi_query, hyde)

    query = "what is transformer"
    print(f"\n🧐 Original Input: '{query}'\n")
    print("⏳ Running LLM Transformations (Rewrite, Multi-Query, HyDE)...")
    
    # Run the orchestration pipeline
    queries = await pipeline.run(query)

    print(f"\n{'-'*60}\n✨ Generated Expansion Queries ({len(queries)} total):\n{'-'*60}")
    for i, q in enumerate(queries):
        print(f"🔹 {q}")

if __name__ == "__main__":
    asyncio.run(main())
