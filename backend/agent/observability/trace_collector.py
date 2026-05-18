"""
Stores every agent step as a searchable vector in Postgres.
The agent can query its OWN past behavior semantically —
the same infra as RAG retrieval, pointed at agent memory.
"""
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from loguru import logger

from backend.app.agent_models import AgentTrace, TaskOutcome
from backend.agent.context import AgentContext, StepRecord
from backend.rag_engine.embeddings import embed_query


class TraceCollector:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def store_trace(
        self,
        context: AgentContext,
        step: StepRecord,
        step_score: float = 0.5,
        eval_note: str = "",
    ) -> None:
        # Embed the combined trace for self-search
        trace_text = (
            f"Task: {context.task[:200]} | "
            f"Action: {step.thought.action} | "
            f"Reasoning: {step.thought.reasoning[:300]} | "
            f"Result: {step.result_output[:300]}"
        )
        embedding = embed_query(trace_text)

        trace = AgentTrace(
            session_id=context.session_id,
            task_id=context.task_id,
            step_number=step.step_num,
            action=step.thought.action,
            action_args=step.thought.args,
            result=step.result_output[:2000],
            result_summary=step.result_output[:400],
            reasoning=step.thought.reasoning,
            confidence=step.thought.confidence,
            model_used=context.model_override or "default",
            latency_ms=step.latency_ms,
            token_count=step.token_count,
            success=step.success,
            step_score=step_score,
            embedding=embedding,
        )
        self.db.add(trace)
        try:
            await self.db.commit()
        except Exception as e:
            logger.error(f"Trace store error: {e}")
            await self.db.rollback()

    async def store_outcome(
        self,
        context: AgentContext,
        final_answer: str,
        quality_score: float,
        failure_pattern: str | None,
        task_category: str,
    ) -> None:
        embedding = embed_query(context.task)
        outcome = TaskOutcome(
            session_id=context.session_id,
            task_description=context.task,
            task_category=task_category,
            total_steps=len(context.steps),
            final_success=quality_score > 0.5,
            quality_score=quality_score,
            dominant_failure=failure_pattern,
            model_used=context.model_override or "default",
            focus_mode=context.focus_mode,
            embedding=embedding,
            traces_json=[str(s.step_num) for s in context.steps],
        )
        self.db.add(outcome)
        try:
            await self.db.commit()
        except Exception as e:
            logger.error(f"Outcome store error: {e}")
            await self.db.rollback()

    async def query_similar_past_runs(
        self,
        current_task: str,
        top_k: int = 5,
    ) -> list[dict]:
        """Agent queries its own past behavior — 'Have I done something like this before?'"""
        embedding = embed_query(current_task)
        rows = await self.db.execute(text("""
            SELECT task_description, task_category, total_steps,
                   final_success, quality_score, dominant_failure,
                   1 - (embedding <=> :vec::vector) AS similarity
            FROM task_outcomes
            ORDER BY embedding <=> :vec::vector
            LIMIT :k
        """), {"vec": str(embedding), "k": top_k})

        return [dict(r._mapping) for r in rows.fetchall()]

    async def get_session_traces(self, session_id: str) -> list[dict]:
        rows = await self.db.execute(
            select(AgentTrace)
            .where(AgentTrace.session_id == session_id)
            .order_by(AgentTrace.step_number)
        )
        traces = rows.scalars().all()
        return [
            {
                "step": t.step_number,
                "action": t.action,
                "reasoning": t.reasoning,
                "result_summary": t.result_summary,
                "success": t.success,
                "step_score": t.step_score,
                "latency_ms": t.latency_ms,
            }
            for t in traces
        ]
