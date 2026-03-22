import json
import os
from typing import List, Dict
from .recall import recall_at_k


class Evaluator:
    """
    Production Evaluator for RAG Retrieval quality.
    Enables iterative debugging by printing both quantitative scores 
    and qualitative chunk previews.
    """
    def __init__(self, retriever):
        self.retriever = retriever

    async def evaluate(self, file_path: str, top_k: int = 5, domain: str = "ai_ml"):
        """
        Runs evaluation over dataset.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Evaluation file path not found: {file_path}")

        with open(file_path, "r") as f:
            dataset = json.load(f)

        scores = []

        for item in dataset:
            query = item["query"]
            expected_keywords = item["expected_keywords"]

            print("\n" + "="*50)
            print(f"🔍 Query: {query}")

            # 🔹 Step 1: Retrieve
            result = await self.retriever.retrieve(query, top_k, domain)

            chunks = result["chunks"]

            # 🔹 Step 2: Compute recall
            score = recall_at_k(chunks, expected_keywords)

            print(f"📊 Recall@{top_k}: {score:.2f}")

            # 🔹 Step 3: Print chunks (VERY IMPORTANT FOR DEBUGGING)
            print("\n📄 Retrieved Chunks Preview:")
            for i, chunk in enumerate(chunks):
                print(f"\n--- Chunk {i+1} ---")
                print(chunk["content"][:200].replace("\n", " ") + "...")

            scores.append(score)

        # 🔹 Final score
        avg_score = sum(scores) / len(scores)

        print("\n" + "="*50)
        print(f"🔥 Average Recall@{top_k}: {avg_score:.2f}")

        # Human-readable tiering
        if avg_score > 0.85:
            print("🚀 STATUS: Strong Retrieval")
        elif avg_score >= 0.7:
            print("✅ STATUS: Good Retrieval")
        elif avg_score >= 0.5:
            print("⚠️ STATUS: Okay / Needs Tuning")
        else:
            print("❌ STATUS: Bad Retrieval")

        return avg_score
