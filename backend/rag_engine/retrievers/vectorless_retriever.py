from typing import List, Dict, Any
from rag_engine.retrievers.base import BaseRetriever


class VectorlessRetriever(BaseRetriever):
    """
    Advanced 'Vectorless RAG' Retriever.
    Uses LLM to extract specific technical keywords from a query, 
    then performs high-precision full-text database lookups.
    Essential for exact-match compliance and fallback scenarios.
    """
    
    def __init__(self, llm, keyword_retriever):
        self.llm = llm
        self.keyword_retriever = keyword_retriever

    async def retrieve(self, query: str, top_k: int = 5, domain: str = "ai_ml") -> Dict[str, Any]:
        """
        Retrieves chunks using keyword reasoning instead of vector similarity.
        """
        # 1. LLM-based Keyword Extraction
        prompt = f"""
Extract 3 to 5 highly specific technical keywords or phrases from the following query that would be found in a database index.
Query: {query}
Return only the keywords separated by spaces.
"""
        keywords_str = await self.llm.generate(prompt)
        
        # 2. Database Keyword Search (tsvector)
        # We pass the extracted keywords to the underlying keyword retriever
        result = await self.keyword_retriever.retrieve(keywords_str, top_k=top_k, domain=domain)
        
        # 3. Append metadata to track strategy
        result["meta"]["strategy"] = "vectorless"
        result["meta"]["extracted_keywords"] = keywords_str
        
        return result
