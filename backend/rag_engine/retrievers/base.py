from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseRetriever(ABC):
    """
    Abstract base class for all RAG retrievers.
    Ensures a consistent interface for vector, keyword, or hybrid retrieval.
    """
    
    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5, domain: str = "ai_ml") -> List[Dict[str, Any]]:
        """
        Retrieve chunks relevant to the query.
        
        Args:
            query: The search string.
            top_k: Number of most relevant results to return.
            domain: The domain filter (e.g., 'ai_ml').
            
        Returns:
            A list of structured dictionary results.
        """
        pass
