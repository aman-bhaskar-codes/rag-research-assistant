import google.generativeai as genai
import os
from .base import BaseEmbedder

class GeminiEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = "models/gemini-embedding-001"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        genai.configure(api_key=api_key)
        self.model_name = model_name

    def embed_text(self, text: str) -> list[float]:
        try:
            response = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_document"
            )
            return response["embedding"]
        except Exception as e:
            raise RuntimeError(f"Error generating embedding for text: {e}")

    def embed_documents(self, docs: list[str]) -> list[list[float]]:
        try:
            # Batch embedding if supported by SDK cleanly, else iterate
            embeddings = []
            for doc in docs:
                embeddings.append(self.embed_text(doc))
            return embeddings
        except Exception as e:
            raise RuntimeError(f"Error generating embeddings for documents: {e}")
