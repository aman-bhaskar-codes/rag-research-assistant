import logging
import time
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.api_schemas import ResearchRequest
from app.services.orchestrator import Orchestrator
from app.services.memory_client import MemoryClient
from app.services.retrieval_client import RetrievalClient
from app.services.llm_service import LLMService
from app.utils.production_logger import get_trace_logger
from app.utils.rate_limiter import limiter

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

    # 1. Rate Limiting
    if not limiter.is_allowed(request_data.user_id):
        logger.warning(f"Rate limit exceeded for user {request_data.user_id}")
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a minute.")

    logger.info(f"Researching: {request_data.query[:50]}...")
    start_time = time.time()

    async def event_generator():
        full_response = ""
        try:
            async for chunk in orchestrator.stream(request_data):
                # 🛡️ SSE format
                yield f"data: {chunk}\n\n"
                full_response += chunk

                # Check for client disconnect
                if await request.is_disconnected():
                    logger.info("Client disconnected. Aborting stream.")
                    break
            
            # 🏁 Request cycle complete
            latency = (time.time() - start_time) * 1000
            logger.info("Research complete", extra={"latency_ms": latency, "status": "success"})

        except Exception as e:
            logger.error(f"Streaming error: {e}", extra={"status": "error"})
            yield "data: [ERROR] System timeout. Please try again.\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")