import logging
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.schemas.api_schemas import ResearchRequest
from app.services.orchestrator import Orchestrator
from app.services.memory_client import MemoryClient
from app.services.retrieval_client import RetrievalClient
from app.services.llm_service import LLMService
from app.utils.production_logger import get_trace_logger

router = APIRouter()

# Global Orchestrator Instance
orchestrator = Orchestrator(
    memory_client=MemoryClient(),
    retrieval_client=RetrievalClient(),
    llm_service=LLMService()
)

@router.get("/health")
async def health():
    return {"status": "healthy", "service": "research-assistant"}

@router.post("/query")
async def query(request_data: ResearchRequest, request: Request):
    trace_id = getattr(request.state, "trace_id", "system")
    logger = get_trace_logger("api.query", trace_id)
    
    logger.info(f"Incoming research query: {request_data.query[:50]}...")

    async def generator():
        try:
            async for chunk in orchestrator.stream(request_data):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield "data: [ERROR] An interruption occurred during research.\n\n"

    return StreamingResponse(generator(), media_type="text/event-stream")