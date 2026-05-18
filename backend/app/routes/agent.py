"""
Agent API endpoints.
/agent/run     → start a research task (SSE stream)
/agent/traces  → get step-by-step trace for a session
/agent/capability-map → see agent's self-knowledge
/agent/strategies/pending → human approval queue
/agent/strategies/{id}/approve → approve a strategy
/agent/corrections → log a human correction (digital twin data)
"""
import json
import asyncio
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_session
from backend.agent.agent_loop import AgentRunner
from backend.agent.observability.capability_map import CapabilityMap
from backend.agent.observability.strategy_library import StrategyLibrary
from backend.agent.observability.trace_collector import TraceCollector
from backend.app.agent_models import UserCorrection
from backend.rag_engine.embeddings import embed_query

router = APIRouter()


class AgentRunRequest(BaseModel):
    task: str = Field(..., min_length=5, max_length=3000)
    session_id: str = Field(...)
    focus_mode: str = Field(default="research")
    model: str | None = None
    max_steps: int = Field(default=10, ge=3, le=20)


class CorrectionRequest(BaseModel):
    task_id: str
    situation: str
    agent_approach: str
    your_approach: str
    reason: str | None = None
    domain: str = "general"


class StrategyApprovalRequest(BaseModel):
    strategy_id: str


async def _agent_sse_stream(
    runner: AgentRunner,
    req: AgentRunRequest,
) -> AsyncGenerator[str, None]:
    """Wraps AgentRunner.run() as SSE events for the frontend."""
    queue: asyncio.Queue = asyncio.Queue()

    async def callback(event_type: str, data: dict):
        await queue.put((event_type, data))

    async def run_agent():
        try:
            result = await runner.run(
                task=req.task,
                session_id=req.session_id,
                focus_mode=req.focus_mode,
                model_override=req.model,
                max_steps=req.max_steps,
                stream_callback=callback,
            )
            await queue.put(("final_answer", {
                "answer": result.final_answer,
                "quality": result.quality_score,
                "total_steps": result.total_steps,
                "failure_pattern": result.failure_pattern,
            }))
        except Exception as e:
            await queue.put(("error", {"message": str(e)}))
        finally:
            await queue.put(None)  # sentinel

    task = asyncio.create_task(run_agent())

    while True:
        item = await queue.get()
        if item is None:
            break
        event_type, data = item
        yield f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

    await task


@router.post("/run")
async def run_agent(
    req: AgentRunRequest,
    db: AsyncSession = Depends(get_session),
):
    runner = AgentRunner(db)
    return StreamingResponse(
        _agent_sse_stream(runner, req),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/traces/{session_id}")
async def get_traces(
    session_id: str,
    db: AsyncSession = Depends(get_session),
):
    collector = TraceCollector(db)
    traces = await collector.get_session_traces(session_id)
    return {"session_id": session_id, "traces": traces}


@router.get("/similar-past-runs")
async def get_similar_past_runs(
    task: str,
    db: AsyncSession = Depends(get_session),
):
    collector = TraceCollector(db)
    similar = await collector.query_similar_past_runs(task, top_k=5)
    return {"similar_runs": similar}


@router.get("/capability-map")
async def get_capability_map(db: AsyncSession = Depends(get_session)):
    cap_map = CapabilityMap(db)
    full = await cap_map.get_full_map()
    weak = await cap_map.get_weak_areas()
    return {"capability_map": full, "weak_areas": weak}


@router.get("/strategies/pending")
async def get_pending_strategies(db: AsyncSession = Depends(get_session)):
    library = StrategyLibrary(db)
    pending = await library.get_pending_approvals()
    return {"pending": pending, "count": len(pending)}


@router.post("/strategies/{strategy_id}/approve")
async def approve_strategy(
    strategy_id: str,
    db: AsyncSession = Depends(get_session),
):
    library = StrategyLibrary(db)
    ok = await library.approve_strategy(strategy_id)
    if not ok:
        raise HTTPException(404, "Strategy not found")
    return {"approved": True, "strategy_id": strategy_id}


@router.post("/corrections")
async def log_correction(
    req: CorrectionRequest,
    db: AsyncSession = Depends(get_session),
):
    """Log human corrections — training data for digital twin."""
    text = f"{req.situation} | agent: {req.agent_approach} | better: {req.your_approach}"
    embedding = embed_query(text)

    correction = UserCorrection(
        task_id=req.task_id,
        situation=req.situation,
        agent_approach=req.agent_approach,
        your_approach=req.your_approach,
        reason=req.reason,
        domain=req.domain,
        embedding=embedding,
    )
    db.add(correction)
    await db.commit()
    return {"logged": True, "correction_id": str(correction.id)}


@router.get("/daily-report")
async def get_daily_report(db: AsyncSession = Depends(get_session)):
    """Generate the daily evolution report — call this every morning."""
    from backend.agent.digital_twin.evolution_protocol import run_daily_evolution
    report = await run_daily_evolution(db)
    return report

