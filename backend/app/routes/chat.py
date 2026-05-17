# backend/app/routes/chat.py
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import ollama
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_session
from backend.app.config import get_settings
from backend.rag_engine.retriever import retrieve
from backend.rag_engine.reranker import rerank
from backend.memory.short_term import get_history, push_message

router = APIRouter()
settings = get_settings()


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="UUID of the chat session")
    query: str = Field(..., min_length=1, max_length=2000)
    domain: str = Field("general", pattern="^[a-z_]+$")
    use_hyde: bool = True


async def _stream_response(
    query: str,
    context: str,
    history: list[dict],
):
    """Async generator that yields SSE-formatted JSON chunks."""
    client = ollama.AsyncClient(host=settings.ollama_base_url)
    system = f"""You are a research assistant. Answer using the context below.
Context:
{context}
"""
    messages = [{"role": "system", "content": system}]
    messages += history
    messages.append({"role": "user", "content": query})

    async for chunk in await client.chat(
        model=settings.llm_model,
        messages=messages,
        stream=True,
    ):
        token = chunk["message"]["content"]
        yield f"data: {json.dumps({'token': token})}\n\n"
    yield "data: [DONE]\n\n"


@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    session: AsyncSession = Depends(get_session),
):
    # 1. Retrieve + rerank relevant chunks
    chunks = await retrieve(req.query, session, mode=req.domain,
                            use_hyde=req.use_hyde)
    top = rerank(req.query, chunks, top_n=settings.rag_top_n)
    context = "\n\n---\n\n".join(c.content for c in top)

    # 2. Load short-term memory
    history = await get_history(req.session_id)

    # 3. Persist user turn
    await push_message(req.session_id, "user", req.query)

    # 4. Stream response
    return StreamingResponse(
        _stream_response(req.query, context, history),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
