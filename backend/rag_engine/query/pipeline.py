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

    async def run(self, query: str, max_queries: int = 5) -> List[str]:
        """
        Processes a user query into a controlled list of semantic search signals.
        """
        # 1. Start with the original query in case LLMs fail or hallucinate
        final_queries: Set[str] = {query}
        
        # 2. Add expanded signals with safe fallbacks
        try:
            rewritten = await self.rewriter.transform(query)
            for q in rewritten:
                if len(final_queries) < max_queries:
                    final_queries.add(q)
        except Exception as e:
            # Non-blocking: If rewriter fails, we just lose that specific expansion
            pass

        try:
            multi = await self.multi_query.transform(query)
            for q in multi:
                if len(final_queries) < max_queries:
                    final_queries.add(q)
        except Exception as e:
            pass

        try:
            hyde_q = await self.hyde.transform(query)
            for q in hyde_q:
                if len(final_queries) < max_queries:
                    final_queries.add(q)
        except Exception as e:
            pass

        # Use list comprehension for final filtering (len check)
        return [q for q in list(final_queries) if len(q) > 5]
