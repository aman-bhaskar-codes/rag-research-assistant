import os
import json
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)


class OllamaLLM:
    """
    Local LLM Generation Interface using Ollama (free, unlimited).
    Perfectly tailored for local query transformations without hitting API rate-limits.
    """
    def __init__(self, model_name: str = "mistral", base_url: Optional[str] = None):
        self.model_name = model_name
        # Respect the same base URL convention as OllamaEmbedder
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.api_url = f"{self.base_url}/api/generate"

    async def generate(self, prompt: str) -> str:
        """
        Asynchronously invoke Ollama for text generation.
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        # Fallback to requests if we must, but standard httpx is async.
        # This function must be awaited.
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(self.api_url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except httpx.HTTPError as e:
                logger.error(f"OllamaLLM Error: {e}")
                # Fallback to pure query passthrough text if LLM dies so RAG doesn't fully crash
                return prompt
