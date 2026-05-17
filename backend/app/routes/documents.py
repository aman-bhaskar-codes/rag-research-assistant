import tempfile
import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_session
from backend.rag_engine.ingestion import ingest_document, extract_pdf_text

router = APIRouter()

ALLOWED_TYPES = {"application/pdf", "text/plain", "text/markdown"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


@router.post("/ingest")
async def ingest_document_route(
    file: UploadFile = File(...),
    domain: str = Form(default="general"),
    session: AsyncSession = Depends(get_session),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, f"Unsupported file type: {file.content_type}. Use PDF or text.")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large. Max 20MB.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        if file.content_type == "application/pdf":
            text = extract_pdf_text(tmp_path)
        else:
            text = content.decode("utf-8", errors="ignore")

        if len(text.split()) < 20:
            raise HTTPException(422, "Document appears empty or unreadable.")

        result = await ingest_document(
            text=text,
            filename=file.filename,
            domain=domain,
            source_type="upload",
            session=session,
        )
        return result
    finally:
        os.unlink(tmp_path)


@router.post("/ingest-text")
async def ingest_text(
    text: str = Form(...),
    title: str = Form(default="Pasted Text"),
    domain: str = Form(default="general"),
    session: AsyncSession = Depends(get_session),
):
    if len(text.split()) < 10:
        raise HTTPException(422, "Text too short to be useful.")

    return await ingest_document(
        text=text,
        filename=title,
        domain=domain,
        source_type="paste",
        session=session,
    )
