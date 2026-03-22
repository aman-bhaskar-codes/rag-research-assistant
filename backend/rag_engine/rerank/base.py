from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseReranker(ABC):
    """
    Abstract interface for post-retrieval Reranking.
    Enforces the contract for taking Top-K high-recall chunks and refining 
    them into a Top-N precision-sorted list.
    """
    
    @abstractmethod
    async def rerank(self, query: str, chunks: List[Dict[str, Any]], top_n: int) -> List[Dict[str, Any]]:
        """
        Rerank the provided candidate chunks.
        
        Args:
            query: The original user search query.
            chunks: The retrieved high-recall chunks (e.g., K=20).
            top_n: The target number of highly precise chunks to return (e.g., N=5).
            
        Returns:
            The precision-sorted list of dictionaries containing content and metadata.
        """
        pass
