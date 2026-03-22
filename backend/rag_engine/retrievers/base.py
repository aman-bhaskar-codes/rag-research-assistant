from abc import ABC, abstractmethod
from typing import Dict


class BaseRetriever(ABC):
    """
    Abstract base class for all RAG retrievers.
    Ensures a consistent interface for vector, keyword, or hybrid retrieval.
    """
    
    @abstractmethod
    async def retrieve(self, query: str, top_k: int, domain: str) -> Dict:
        """
        Retrieve chunks relevant to the query.
        
        Args:
            query: The search string.
            top_k: Number of most relevant results to return.
            domain: The domain filter (e.g., 'ai_ml').
            
        Returns:
            Dict containing semantic chunks and strategy metadata:
            {
                "chunks": [
                    {
                        "content": "...",
                        "score": 0.89,
                        "metadata": {"source": "..."}
                    }
                ],
                "meta": {
                    "strategy": "vector",
                    "top_k": 5
                }
            }
        """
        pass
