from abc import ABC, abstractmethod

class BaseEmbedder(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """
        Generates embedding vector for a single text string.
        """
        pass

    @abstractmethod
    def embed_documents(self, docs: list[str]) -> list[list[float]]:
        """
        Generates embedding vectors for a list of document strings.
        """
        pass
