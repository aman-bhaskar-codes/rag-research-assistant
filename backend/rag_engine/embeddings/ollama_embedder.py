import requests
import os
from .base import BaseEmbedder


class OllamaEmbedder(BaseEmbedder):
    """
    Local embedding model using Ollama. No rate limits, no API costs.
    Uses nomic-embed-text (768-dim) by default.
    """
    def __init__(self, model_name: str = "nomic-embed-text", base_url: str = None):
        self.model_name = model_name
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def embed_text(self, text: str) -> list[float]:
        try:
            response = requests.post(
                f"{self.base_url}/api/embed",
                json={
                    "model": self.model_name,
                    "input": text,
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return data["embeddings"][0]
        except Exception as e:
            raise RuntimeError(f"Ollama embedding error: {e}")

    def embed_documents(self, docs: list[str]) -> list[list[float]]:
        embeddings = []
        for doc in docs:
            embeddings.append(self.embed_text(doc))
        return embeddings
