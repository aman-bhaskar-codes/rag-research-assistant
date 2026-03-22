from .base import BaseQueryTransform


class MultiQueryGenerator(BaseQueryTransform):
    """
    Expands a single query into N unique perspectives to maximize retrieval recall 
    across different document phrasings.
    """
    def __init__(self, llm, num_queries=3):
        self.llm = llm
        self.num_queries = num_queries

    async def transform(self, query: str) -> list[str]:
        prompt = f"""
Generate {self.num_queries} different variations of the following query 
to improve document retrieval. Each query should explore a different semantic angle or use different terminology.
Do not number the variations. Do not add extra text.

Query: {query}

Return each generated query on a new line.
"""
        response = await self.llm.generate(prompt)
        
        # Parse the raw LLM response into a clean list, filtering empty lines
        # and stripping numbering (e.g., "1. Query" -> "Query") if the LLM disobeyed.
        queries = []
        for q in response.split("\n"):
            clean_q = q.strip()
            if clean_q:
                # Remove leading numbers and symbols just in case
                if clean_q[0].isdigit() and len(clean_q) > 2 and clean_q[1] in (".", ")"):
                    clean_q = clean_q[2:].strip()
                queries.append(clean_q)
                
        # Slice to ensure we strictly adhere to the user's limit constraints
        return queries[:self.num_queries]
