"""
Domain-aware recursive text chunker.
- Code: splits at function/class boundaries
- Academic: splits at paragraph boundaries
- General: splits at sentence boundaries with overlap
"""
import re
from dataclasses import dataclass
from backend.app.config import get_settings

settings = get_settings()


@dataclass
class TextChunk:
    content: str
    index: int
    meta: dict


def _split_sentences(text: str) -> list[str]:
    return re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)


def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]


def _split_code_blocks(text: str) -> list[str]:
    """Split code at function/class definitions."""
    pattern = r"(?=(?:def |class |async def |function |const |export ))"
    parts = re.split(pattern, text)
    return [p.strip() for p in parts if p.strip()]


def chunk_text(
    text: str,
    domain: str = "general",
    size: int | None = None,
    overlap: int | None = None,
) -> list[TextChunk]:
    size = size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    # Clean common noise
    text = re.sub(r"\[[\d,\s]+\]", "", text)   # Remove [1], [2,3]
    text = re.sub(r"\s{3,}", "\n", text)         # Collapse whitespace
    text = text.strip()

    # Domain-specific splitting
    if domain == "code":
        units = _split_code_blocks(text)
    elif domain == "academic":
        units = _split_paragraphs(text)
    else:
        units = _split_sentences(text)

    # Build chunks with overlap
    chunks: list[TextChunk] = []
    current_words: list[str] = []
    idx = 0

    for unit in units:
        unit_words = unit.split()
        if len(current_words) + len(unit_words) > size and current_words:
            content = " ".join(current_words)
            chunks.append(TextChunk(
                content=content,
                index=idx,
                meta={"domain": domain, "word_count": len(current_words)},
            ))
            # Keep overlap
            current_words = current_words[-overlap:]
            idx += 1

        current_words.extend(unit_words)

    if current_words:
        chunks.append(TextChunk(
            content=" ".join(current_words),
            index=idx,
            meta={"domain": domain, "word_count": len(current_words)},
        ))

    return chunks
