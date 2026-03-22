import time


class RetrievalClient:

    async def retrieve(
        self,
        query: str,
        strategy: str,
        top_k: int,
        filters: dict | None = None,
    ) -> dict:
        """
        This will later call rag_engine.pipeline.retrieval_pipeline

        For now: mock response
        """

        start = time.time()

        # 🔥 simulate different strategies
        if strategy == "keyword":
            content = "Keyword-based retrieval result."
        elif strategy == "vector":
            content = "Vector-based semantic retrieval result."
        elif strategy == "hybrid":
            content = "Hybrid retrieval combining vector + keyword."
        else:
            content = "Fallback retrieval."

        latency = int((time.time() - start) * 1000)

        return {
            "chunks": [
                {
                    "content": content,
                    "score": 0.92,
                    "source_id": "doc_123",
                    "metadata": {
                        "strategy_used": strategy
                    }
                }
            ],
            "relationships": [
                # simulate vectorless relations
                {
                    "entity": "AI",
                    "related_to": "Machine Learning"
                }
            ],
            "meta": {
                "strategy": strategy,
                "latency_ms": latency
            }
        }