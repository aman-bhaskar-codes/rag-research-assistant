from .base import BaseQueryTransform


class QueryRewriter(BaseQueryTransform):
    """
    Transforms vague user queries into highly descriptive, retrieval-friendly formulations.
    """
    def __init__(self, llm):
        self.llm = llm

    async def transform(self, query: str) -> list[str]:
        prompt = f"""
Rewrite the following query to make it more specific, clear, and optimized for retrieval against academic and technical documentation. Do not add conversational text, just return the improved query.

Query: {query}

Return only one improved query.
"""
        response = await self.llm.generate(prompt)
        # Strip backticks or quotes if the LLM adds them
        clean_resp = response.strip("` \n\"'")
        return [clean_resp]
