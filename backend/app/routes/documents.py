# backend/app/routes/documents.py
import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_session
from backend.rag_engine.ingestion import ingest_pdf

router = APIRouter()


@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    domain: str = Form("general"),
    session: AsyncSession = Depends(get_session),
):
    """Upload a PDF and ingest it into the RAG knowledge base."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Save to temp file for processing
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        chunk_count = await ingest_pdf(tmp_path, domain, session)
        return {
            "status": "ok",
            "filename": file.filename,
            "domain": domain,
            "chunks_created": chunk_count,
        }
    finally:
        os.unlink(tmp_path)
