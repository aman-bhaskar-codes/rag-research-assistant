import pdfplumber
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models import Document, Chunk
from backend.rag_engine.embeddings import embed_texts
from backend.rag_engine.chunker import chunk_text


def extract_pdf_text(path: str) -> str:
    with pdfplumber.open(path) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    return "\n".join(pages)


async def ingest_document(
    text: str,
    filename: str,
    domain: str,
    source_type: str = "upload",
    source_url: str | None = None,
    session: AsyncSession = None,
) -> dict:
    chunks = chunk_text(text, domain=domain)

    doc = Document(
        filename=filename,
        domain=domain,
        source_type=source_type,
        source_url=source_url,
        word_count=len(text.split()),
    )
    session.add(doc)
    await session.flush()

    texts = [c.content for c in chunks]
    vectors = embed_texts(texts)

    for chunk, vec in zip(chunks, vectors):
        session.add(Chunk(
            document_id=doc.id,
            content=chunk.content,
            embedding=vec,
            chunk_index=chunk.index,
            meta={**chunk.meta, "filename": filename},
        ))

    await session.commit()
    logger.success(f"Ingested '{filename}' → {len(chunks)} chunks in domain '{domain}'")
    return {"document_id": str(doc.id), "chunks": len(chunks), "domain": domain}
