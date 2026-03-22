from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.query import QueryRequest
from app.services.orchestrator import Orchestrator
from app.services.memory_client import MemoryClient
from app.services.retrieval_client import RetrievalClient
from app.services.llm_service import LLMService

router = APIRouter()

orchestrator = Orchestrator(
    memory_client=MemoryClient(),
    retrieval_client=RetrievalClient(),
    llm_service=LLMService()
)

@router.post("/query")
async def query(request: QueryRequest):

    async def generator():
        async for chunk in orchestrator.stream(request):
            yield f"data: {chunk}\n\n"   # 🔥 SSE format

    return StreamingResponse(generator(), media_type="text/event-stream")