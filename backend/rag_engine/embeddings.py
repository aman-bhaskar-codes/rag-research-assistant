from functools import lru_cache
from fastembed import TextEmbedding
from backend.app.config import get_settings

settings = get_settings()


@lru_cache(maxsize=1)
def _get_model() -> TextEmbedding:
    return TextEmbedding(settings.embed_model, max_length=512)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    return [v.tolist() for v in model.embed(texts)]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
