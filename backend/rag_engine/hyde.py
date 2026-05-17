# backend/rag_engine/hyde.py
import ollama
from backend.app.config import get_settings

settings = get_settings()

HYDE_PROMPT = """Write a short, factual paragraph answering the question below.
Be specific and technical. Do not mention that you are generating a hypothetical.

Question: {query}

Answer:"""


async def generate_hyde_doc(query: str) -> str:
    """Ask the LLM to generate a hypothetical ideal answer to the query.

    We embed the hypothetical answer, not the query itself.
    This closes the vocabulary gap between questions and document chunks.
    """
    response = await ollama.AsyncClient(host=settings.ollama_base_url).generate(
        model=settings.llm_model,
        prompt=HYDE_PROMPT.format(query=query),
        options={"temperature": 0.2, "num_predict": 200},
    )
    return response["response"]
