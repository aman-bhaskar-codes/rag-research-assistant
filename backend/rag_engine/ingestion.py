# backend/rag_engine/ingestion.py
import re
import pdfplumber
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models import Document, Chunk
from backend.rag_engine.embeddings import embed_texts
from backend.app.config import get_settings

settings = get_settings()


def extract_text_from_pdf(path: str) -> str:
    with pdfplumber.open(path) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    return "\n".join(pages)


def clean_text(text: str) -> str:
    """Remove references, page numbers, and noise."""
    text = re.sub(r"\[\d+\]", "", text)            # [1], [23]
    text = re.sub(r"\s{3,}", "\n", text)            # excess whitespace
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)  # page nums
    return text.strip()


def recursive_chunk(text: str, size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks at sentence boundaries."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, current, current_len = [], [], 0
    for sent in sentences:
        words = len(sent.split())
        if current_len + words > size and current:
            chunks.append(" ".join(current))
            # Keep last N words as overlap
            overlap_words = " ".join(current).split()[-overlap:]
            current = overlap_words + sent.split()
            current_len = len(current)
        else:
            current.extend(sent.split())
            current_len += words
    if current:
        chunks.append(" ".join(current))
    return chunks


async def ingest_pdf(
    path: str,
    domain: str,
    session: AsyncSession,
) -> int:
    """Full pipeline: PDF → clean text → chunks → embeddings → Postgres."""
    raw = extract_text_from_pdf(path)
    clean = clean_text(raw)
    texts = recursive_chunk(clean, settings.chunk_size, settings.chunk_overlap)

    # Persist document record
    doc = Document(filename=path.split("/")[-1], domain=domain)
    session.add(doc)
    await session.flush()  # get doc.id before inserting chunks

    # Batch embed all chunks
    vectors = embed_texts(texts)
    for text, vec in zip(texts, vectors):
        session.add(Chunk(
            document_id=doc.id,
            content=text,
            embedding=vec,
            meta={"domain": domain, "filename": doc.filename},
        ))
    await session.commit()
    return len(texts)
