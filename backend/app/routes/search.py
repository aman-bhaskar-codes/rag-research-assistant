"""
Core Research Assistant search endpoint.
Streams: sources → answer tokens → related questions → done
"""
import json
import uuid
import asyncio
from typing import AsyncGenerator

import ollama
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from backend.app.config import get_settings
from backend.app.database import get_session
from backend.app.models import SearchSession, SearchTurn
from backend.memory.short_term import push_message, get_history
from backend.search.router import run_web_search, enrich_sources
from backend.rag_engine.retriever import retrieve
from backend.rag_engine.reranker import rerank
from backend.rag_engine.hyde import generate_hyde_doc
from backend.utils.llm_router import select_model
from backend.utils.prompts import (
    SYSTEM_PROMPT, RELATED_QUESTIONS_PROMPT, build_context_and_citations
)

router = APIRouter()
settings = get_settings()

FOCUS_MODES = {"general", "academic", "code", "writing", "research", "documents"}


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    focus_mode: str = Field(default="general")
    model: str | None = None
    use_web: bool = True
    use_rag: bool = True
    use_hyde: bool = False  # Disabled by default for speed; enable for academic mode


async def _stream_search(
    query: str,
    session_id: str,
    focus_mode: str,
    model: str,
    use_web: bool,
    use_rag: bool,
    use_hyde: bool,
    db_session: AsyncSession,
) -> AsyncGenerator[str, None]:
    """
    SSE stream protocol:
    - event: sources     → JSON array of source objects
    - event: token       → one LLM token string
    - event: related     → JSON array of 4 follow-up questions
    - event: done        → final metadata JSON
    - event: error       → error message string
    """

    def sse(event: str, data) -> str:
        payload = json.dumps(data)
        return f"event: {event}\ndata: {payload}\n\n"

    sources: list[dict] = []
    rag_chunks = []
    full_answer = ""

    try:
        # ── STEP 1: Gather Sources ──────────────────────────────────────────
        tasks = []
        if use_web:
            tasks.append(run_web_search(query, count=settings.max_search_results))
        if use_rag:
            # HyDE for academic/research modes
            rag_query = query
            if use_hyde or focus_mode in ("academic", "research"):
                rag_query = await generate_hyde_doc(query)
            tasks.append(retrieve(rag_query, db_session, domain=focus_mode if focus_mode == "documents" else None))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        web_results = results[0] if use_web and not isinstance(results[0], Exception) else []
        rag_results = results[1 if use_web else 0] if use_rag and len(results) > (1 if use_web else 0) else []
        if isinstance(rag_results, Exception):
            rag_results = []

        # Enrich web sources with full content
        if web_results:
            sources = await enrich_sources(web_results)

        # Rerank RAG results
        if rag_results:
            rag_chunks = rerank(query, list(rag_results), top_n=settings.rag_top_n)

        # ── STEP 2: Emit Sources Immediately ───────────────────────────────
        yield sse("sources", [
            {
                "index": i + 1,
                "title": s.get("title", ""),
                "url": s.get("url", ""),
                "description": s.get("description", "")[:200],
                "type": "web",
            }
            for i, s in enumerate(sources)
        ] + [
            {
                "index": len(sources) + i + 1,
                "title": c.meta.get("filename", "Document"),
                "url": "",
                "description": c.content[:150],
                "type": "document",
            }
            for i, c in enumerate(rag_chunks)
        ])

        # ── STEP 3: Build Prompt ────────────────────────────────────────────
        context, citation_guide, numbered_sources = build_context_and_citations(sources, rag_chunks)

        chat_history = await get_history(session_id)

        if context.strip():
            messages = [{"role": "system", "content": SYSTEM_PROMPT.format(
                context=context,
                citation_guide=citation_guide,
            )}]
        else:
            # Fallback: no sources, direct LLM conversation
            messages = [{"role": "system", "content": (
                "You are a helpful research assistant. Answer the user's question "
                "clearly and comprehensively. Use markdown formatting."
            )}]

        messages += chat_history[-6:]  # Last 3 exchanges
        messages.append({"role": "user", "content": query})

        # ── STEP 4: Stream LLM Answer ───────────────────────────────────────
        client = ollama.AsyncClient(host=settings.ollama_base_url)

        async for chunk in await client.chat(
            model=model,
            messages=messages,
            stream=True,
            options={"temperature": 0.3, "num_ctx": 4096},
        ):
            token = chunk["message"]["content"]
            full_answer += token
            yield sse("token", token)

        # ── STEP 5: Generate Related Questions ─────────────────────────────
        related_questions = []
        try:
            related_prompt = RELATED_QUESTIONS_PROMPT.format(
                query=query,
                answer_summary=full_answer[:500],
            )
            related_resp = await client.generate(
                model=settings.fast_model,
                prompt=related_prompt,
                options={"temperature": 0.7, "num_predict": 200},
            )
            raw = related_resp["response"].strip()
            # Parse JSON array
            start = raw.find("[")
            end = raw.rfind("]") + 1
            if start != -1 and end > start:
                related_questions = json.loads(raw[start:end])
        except Exception as e:
            logger.debug(f"Related questions generation failed: {e}")

        yield sse("related", related_questions)

        # ── STEP 6: Persist to Database ─────────────────────────────────────
        try:
            # Upsert session
            from sqlalchemy import select as sa_select
            stmt = sa_select(SearchSession).where(
                SearchSession.session_key == session_id
            )
            result = await db_session.execute(stmt)
            sess = result.scalar_one_or_none()

            if not sess:
                sess = SearchSession(
                    session_key=session_id,
                    title=query[:80],
                    focus_mode=focus_mode,
                    model_used=model,
                )
                db_session.add(sess)
                await db_session.flush()

            turn = SearchTurn(
                session_id=sess.id,
                query=query,
                answer=full_answer,
                sources=numbered_sources,
                related_questions=related_questions,
                model_used=model,
                focus_mode=focus_mode,
            )
            db_session.add(turn)
            await db_session.commit()

            # Short-term memory
            await push_message(session_id, "user", query)
            await push_message(session_id, "assistant", full_answer[:500])

            yield sse("done", {
                "turn_id": str(turn.id),
                "session_id": session_id,
                "model": model,
                "sources_count": len(numbered_sources),
            })

        except Exception as e:
            logger.error(f"DB persist failed: {e}")
            yield sse("done", {"session_id": session_id, "error": str(e)})

    except Exception as e:
        logger.error(f"Search pipeline error: {e}", exc_info=True)
        yield sse("error", f"Search failed: {str(e)}")


@router.post("/stream")
async def search_stream(
    req: SearchRequest,
    db_session: AsyncSession = Depends(get_session),
):
    if req.focus_mode not in FOCUS_MODES:
        raise HTTPException(400, f"Invalid focus_mode. Must be one of: {FOCUS_MODES}")

    model = select_model(req.focus_mode, req.model)

    return StreamingResponse(
        _stream_search(
            query=req.query,
            session_id=req.session_id,
            focus_mode=req.focus_mode,
            model=model,
            use_web=req.use_web,
            use_rag=req.use_rag,
            use_hyde=req.use_hyde,
            db_session=db_session,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.get("/suggest")
async def suggest_queries(q: str):
    """Auto-complete query suggestions powered by local LLM."""
    from backend.app.config import get_settings
    s = get_settings()
    client = ollama.AsyncClient(host=s.ollama_base_url)
    prompt = f"""Generate 5 search query auto-completions for: "{q}"
Output ONLY a JSON array of 5 strings."""
    try:
        resp = await client.generate(
            model=s.fast_model,
            prompt=prompt,
            options={"temperature": 0.5, "num_predict": 100},
        )
        raw = resp["response"].strip()
        start, end = raw.find("["), raw.rfind("]") + 1
        suggestions = json.loads(raw[start:end]) if start != -1 else []
    except Exception:
        suggestions = []
    return {"suggestions": suggestions[:5]}
