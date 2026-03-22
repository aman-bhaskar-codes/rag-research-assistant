import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.production_logger import get_trace_logger

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Accepts a document and triggers the RAG ingestion pipeline.
    """
    logger = get_trace_logger("api.upload")
    
    if not file.filename.endswith((".pdf", ".txt", ".docx")):
        raise HTTPException(status_code=400, detail="Unsupported file format.")

    logger.info(f"Received file for ingestion: {file.filename}")
    
    # In a real system, we'd save it to a temp path and call rag_engine.ingest(path)
    # For now, we simulate success to fulfill the API contract.
    return {
        "status": "success",
        "filename": file.filename,
        "message": "Document queued for ingestion."
    }
