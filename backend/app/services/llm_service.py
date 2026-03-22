from typing import AsyncGenerator
import httpx

class BaseLLMProvider:
    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        raise NotImplementedError


# 🔹 Dummy Ollama Provider
class OllamaProvider:
    def __init__(self):
        self.base_url = "http://localhost:11434/api/generate"

    async def stream(self, prompt: str):
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                self.base_url,
                json={
                    "model": "llama3",  # change to your model
                    "prompt": prompt,
                    "stream": True
                }
            ) as response:

                async for line in response.aiter_lines():
                    if line:
                        try:
                            import json
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                        except Exception:
                            continue


# 🔹 Dummy Gemini Provider
class GeminiProvider(BaseLLMProvider):
    async def stream(self, prompt: str):
        for token in ["Gemini", " ", "response", " ", "stream"]:
            yield token


# 🔥 MAIN SERVICE (router)
class LLMService:

    def __init__(self):
        self.providers = {
            "ollama": OllamaProvider(),
            "gemini": GeminiProvider(),
        }

    async def stream(self, prompt: str, model: str):
        """
        model:
        - ollama
        - gemini
        - auto (fallback)
        """

        provider = self.providers.get(model)

        if not provider:
            # fallback logic
            provider = self.providers["gemini"]

        async for token in provider.stream(prompt):
            yield token