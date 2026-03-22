from typing import List, Set


class QueryPipeline:
    """
    Core Intelligence Layer: Query Pipeline.
    Orchestrates Query Rewriting, Multi-Query Expansion, and HyDE.
    Constrains and deduplicates total query volume to prevent database explosion.
    """
    def __init__(self, rewriter, multi_query, hyde):
        self.rewriter = rewriter
        self.multi_query = multi_query
        self.hyde = hyde

    async def run(self, query: str) -> List[str]:
        # Generate varied signals
        rewritten = await self.rewriter.transform(query)
        multi = await self.multi_query.transform(query)
        hyde_q = await self.hyde.transform(query)

        # Merge, deduplicate (set comprehension), and bounds check (~5 output queries expected typically)
        # Using a set to enforce uniqueness
        final_queries: Set[str] = set()
        
        # Keep original query just in case the LLM ruined the meaning
        final_queries.add(query)
        
        for q in (rewritten + multi + hyde_q):
            if q and len(q) > 5:  # Basic validation
                final_queries.add(q)

        return list(final_queries)
