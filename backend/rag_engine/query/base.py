from abc import ABC, abstractmethod


class BaseQueryTransform(ABC):
    """
    Abstract interface for Query Transformation modules (Rewrite, Multi-Query, HyDE).
    """
    @abstractmethod
    async def transform(self, query: str) -> list[str]:
        pass
