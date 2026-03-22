import os
import sys
import asyncio

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from rag_engine.evaluation.evaluator import Evaluator
from rag_engine.retrievers.hybrid_retriever import HybridRetriever
from rag_engine.retrievers.vector_retriever import VectorRetriever
from rag_engine.retrievers.keyword_retriever import KeywordRetriever
from rag_engine.utils.db_client import DBClient
from rag_engine.embeddings.ollama_embedder import OllamaEmbedder


async def main():
    # -------- INIT --------
    # Note: Use model_name to match our implementation
    embedder = OllamaEmbedder(model_name="nomic-embed-text")
    db_client = DBClient(dsn="postgresql://user:pass@localhost:5432/db")

    vector = VectorRetriever(embedder, db_client)
    keyword = KeywordRetriever(db_client)

    retriever = HybridRetriever(vector, keyword)

    evaluator = Evaluator(retriever)

    # -------- RUN --------
    # Use absolute path for reliability
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    eval_file = os.path.join(base_dir, "data/eval/queries.json")
    
    await evaluator.evaluate(
        file_path=eval_file,
        top_k=5,
        domain="ai_ml"
    )


if __name__ == "__main__":
    asyncio.run(main())
