from abc import ABC, abstractmethod

class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, text: str) -> list[str]:
        """
        Splits text into chunks of strings.
        """
        pass
