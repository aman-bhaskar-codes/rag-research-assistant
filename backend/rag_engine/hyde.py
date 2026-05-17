import ollama
from backend.app.config import get_settings

settings = get_settings()

HYDE_PROMPT = """Write a short, precise, factual paragraph that directly answers this question.
Be technical. Be specific. Do not hedge.

Question: {query}

Answer:"""


async def generate_hyde_doc(query: str) -> str:
    """Generate a hypothetical answer to embed instead of the raw query.
    This dramatically improves recall for abstract or high-level questions."""
    try:
        client = ollama.AsyncClient(host=settings.ollama_base_url)
        response = await client.generate(
            model=settings.fast_model,
            prompt=HYDE_PROMPT.format(query=query),
            options={"temperature": 0.1, "num_predict": 200},
        )
        return response["response"]
    except Exception:
        return query  # fallback to original query
