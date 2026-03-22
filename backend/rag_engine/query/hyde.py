from .base import BaseQueryTransform


class HyDEGenerator(BaseQueryTransform):
    """
    Hypothetical Document Embeddings (HyDE).
    Generates a hallucinated, semantically-rich 'fake answer' to the user's query.
    Embedding this dense answer yields drastically better similarity matches 
    than embedding a sparse, 3-word question.
    """
    def __init__(self, llm):
        self.llm = llm

    async def transform(self, query: str) -> list[str]:
        prompt = f"""
Write a detailed, academic paragraph answering the following query. 
Assume a professional machine learning context. Do not include introductory conversational text.

Query: {query}
"""
        response = await self.llm.generate(prompt)
        return [response.strip()]
