import sys
import os

# Ensure the RAG engine package is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from rag_engine.pipeline.retrieval_pipeline import retrieve


class RetrievalClient:
    """
    Thin adapter for the RAG Engine.
    Exposes a clean, production-safe interface to the Backend Orchestrator.
    Handles safety limits, error fallbacks, and response standardization.
    """

    async def retrieve(
        self,
        query: str,
        strategy: str = "hybrid",
        top_k: int = 20,
        domain: str = "ai_ml"
    ):
        # 🔒 Enforce production safety limits
        top_k = min(top_k, 20)

        try:
            result = await retrieve(
                query=query,
                strategy=strategy,
                top_k=top_k,
                domain=domain
            )

            # Basic validation of the RAG response contract
            if not result or "chunks" not in result:
                return self._empty_response(strategy, top_k)

            return result

        except Exception as e:
            # 🔥 Universal Safety Fallback: The system must NEVER crash during a chat session
            print(f"[RETRIEVAL ERROR] Fallback engaged: {e}")
            return self._empty_response(strategy, top_k)

    def _empty_response(self, strategy, top_k):
        """Standardized empty response to keep orchestrator downstream logic stable."""
        return {
            "chunks": [],
            "meta": {
                "strategy": strategy,
                "top_k": top_k,
                "top_n": 0
            }
        }