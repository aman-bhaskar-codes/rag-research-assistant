import os
import json
import httpx
import logging
import asyncio
from typing import AsyncGenerator
import google.generativeai as genai

logger = logging.getLogger(__name__)

class BaseLLMProvider:
    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        yield "[ERROR] Base provider not implemented"


class OllamaProvider(BaseLLMProvider):
    def __init__(self, model: str = "llama3"):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api/generate")
        self.model = model

    async def stream(self, prompt: str):
        logger.info(f"Ollama streaming start (model: {self.model})")
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    self.base_url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            yield data.get("response", "")
        except Exception as e:
            logger.error(f"Ollama stream error: {e}")
            yield "[ERROR] Ollama connection failed. Is the service running?"


class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found. Gemini will fail.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    async def stream(self, prompt: str):
        logger.info("Gemini streaming start")
        try:
            # Using the native SDK for better performance/streaming
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                stream=True
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini stream error: {e}")
            yield "[ERROR] Gemini intelligence layer unavailable. Check API key."


class LLMService:
    def __init__(self):
        self.providers = {
            "ollama": OllamaProvider(),
            "gemini-1.5-pro": GeminiProvider(),
            "gemini": GeminiProvider(), # Alias
        }

    async def stream(self, prompt: str, model: str = "auto"):
        # Mapping 'auto' or unspecified to gemini for cloud deployment
        target = "gemini" if model in ["auto", "gemini"] else model
        provider = self.providers.get(target)

        if not provider:
            logger.warning(f"Provider {model} unknown. Falling back to Gemini.")
            provider = self.providers["gemini"]

        async for token in provider.stream(prompt):
            yield token