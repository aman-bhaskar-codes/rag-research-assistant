from abc import ABC, abstractmethod
from typing import List


class BaseEmbedder(ABC):
    """
    Abstract Base Class for all Semantic Embedders.
    Ensures consistent API across Document Ingestion and Memory hooks.
    """

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """
        Generates a high-dimensional vector for the provided text.
        """
        pass
