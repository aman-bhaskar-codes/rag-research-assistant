"""
The core Think → Act → Observe → Reflect loop.
This is the BRAIN of the agentic system.
"""
import time
import asyncio
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agent.context import AgentContext, AgentResult, StepRecord
from backend.agent.planner import AgentPlanner
from backend.agent.tool_registry import ToolRegistry
from backend.agent.goal_anchor import GoalAnchor
from backend.agent.observability.trace_collector import TraceCollector
from backend.agent.observability.failure_memory import FailureMemory
from backend.agent.observability.capability_map import CapabilityMap
from backend.agent.observability.task_classifier import classify_task
from backend.rag_engine.embeddings import embed_query
from backend.app.config import get_settings

settings = get_settings()

MAX_STEPS = 12
FINISH_EARLY_THRESHOLD = 0.92  # if step scores are high, allow early finish


class AgentRunner:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.tools = ToolRegistry(db_session)
        self.planner = AgentPlanner(self.tools)
        self.trace_collector = TraceCollector(db_session)
        self.failure_memory = FailureMemory(db_session)
        self.capability_map = CapabilityMap(db_session)

    async def run(
        self,
        task: str,
        session_id: str,
        focus_mode: str = "research",
        model_override: str | None = None,
        max_steps: int = MAX_STEPS,
        stream_callback=None,  # async callable(event_type, data) for SSE
    ) -> AgentResult:
        context = AgentContext(
            task=task,
            session_id=session_id,
            focus_mode=focus_mode,
            model_override=model_override,
        )
        goal_anchor = GoalAnchor(task)

        # ── Pre-task: Load intelligence from memory ─────────────────────
        task_category = await classify_task(task)
        failure_lessons = await self.failure_memory.get_relevant_lessons(task)
        capability_hints = await self.capability_map.get_hints_for_task(task_category)

        logger.info(f"Agent starting | task_category={task_category} | session={session_id}")

        if stream_callback:
            await stream_callback("agent_start", {
                "task": task,
                "task_category": task_category,
                "lessons_loaded": len(failure_lessons) if isinstance(failure_lessons, list) else 0,
            })

        # ── Main Loop ────────────────────────────────────────────────────
        for step_num in range(1, max_steps + 1):
            t0 = time.perf_counter()

            # THINK: Check drift, get next action
            drift = goal_anchor.check(step_num, context.to_prompt_history(max_steps=3))
            if drift.drifted and stream_callback:
                await stream_callback("drift_detected", {"score": drift.drift_score, "step": step_num})

            # Inject drift correction into lessons
            lessons_str = failure_lessons
            if drift.drifted:
                lessons_str = drift.correction_prompt + "\n\n" + (failure_lessons or "")

            thought = await self.planner.decide(
                context,
                failure_lessons=lessons_str,
                capability_hints=capability_hints,
            )

            if stream_callback:
                await stream_callback("agent_thinking", {
                    "step": step_num,
                    "action": thought.action,
                    "reasoning": thought.reasoning,
                    "confidence": thought.confidence,
                })

            # ACT: Execute tool
            result = await self.tools.execute(thought.action, thought.args)
            latency_ms = (time.perf_counter() - t0) * 1000

            # OBSERVE: Cross-model evaluation of this step
            step_eval = await self.planner.cross_evaluate_step(
                task=task,
                action=thought.action,
                reasoning=thought.reasoning,
                result=result.output,
            )
            step_score = step_eval.get("overall", 0.5)

            if stream_callback:
                await stream_callback("agent_step", {
                    "step": step_num,
                    "action": thought.action,
                    "result_preview": result.output[:200],
                    "success": result.success,
                    "step_score": step_score,
                    "latency_ms": round(latency_ms, 1),
                })

            # Record in context
            record = StepRecord(
                step_num=step_num,
                thought=thought,
                result_output=result.output,
                result_data=result.data,
                success=result.success,
                latency_ms=latency_ms,
                token_count=result.token_estimate,
            )
            context.add_step(record)

            # Store trace in DB (async, fire-and-forget to not block loop)
            asyncio.create_task(
                self.trace_collector.store_trace(
                    context=context,
                    step=record,
                    step_score=step_score,
                    eval_note=step_eval.get("note", ""),
                )
            )

            # CHECK: Done?
            if thought.action == "finish":
                final_answer = result.data.get("final_answer", result.output) if result.data else result.output
                break

            # Safety: stop if consecutive failures
            if step_num >= 3:
                last_3 = context.steps[-3:]
                if all(not s.success for s in last_3):
                    logger.error(f"3 consecutive failures — stopping agent")
                    final_answer = "Unable to complete task: repeated tool failures. Please check tool configuration."
                    break
        else:
            # Exhausted max steps — summarize what was found
            notes_result = await self.tools.execute("read_notes", {})
            final_answer = f"Reached step limit ({max_steps}). Research notes:\n\n{notes_result.output}"

        # ── Post-task: Store outcome + extract lessons ────────────────────
        quality = self._estimate_quality(context)
        failure_pattern = self._detect_failure_pattern(context)

        asyncio.create_task(
            self.trace_collector.store_outcome(
                context=context,
                final_answer=final_answer,
                quality_score=quality,
                failure_pattern=failure_pattern,
                task_category=task_category,
            )
        )

        # Extract and store failure lesson if quality was low
        if quality < 0.65 and failure_pattern:
            asyncio.create_task(
                self.failure_memory.extract_and_store_lesson(
                    task=task,
                    context=context,
                    failure_pattern=failure_pattern,
                    quality_score=quality,
                )
            )

        # Update capability map
        asyncio.create_task(
            self.capability_map.update(
                task_category=task_category,
                quality_score=quality,
                steps_taken=len(context.steps),
                failure_pattern=failure_pattern,
            )
        )

        if stream_callback:
            await stream_callback("agent_done", {
                "quality_score": quality,
                "total_steps": len(context.steps),
                "failure_pattern": failure_pattern,
                "task_category": task_category,
            })

        return AgentResult(
            context=context,
            final_answer=final_answer,
            total_steps=len(context.steps),
            success=quality > 0.5,
            quality_score=quality,
            failure_pattern=failure_pattern,
        )

    def _estimate_quality(self, context: AgentContext) -> float:
        """Heuristic quality score from step data. Not perfect — that's fine."""
        if not context.steps:
            return 0.0
        success_rate = sum(1 for s in context.steps if s.success) / len(context.steps)
        has_notes = any(s.thought.action == "write_note" for s in context.steps)
        has_finish = any(s.thought.action == "finish" for s in context.steps)
        used_multiple_tools = len({s.thought.action for s in context.steps}) > 2

        score = success_rate * 0.5
        if has_notes: score += 0.15
        if has_finish: score += 0.25
        if used_multiple_tools: score += 0.10
        return min(score, 1.0)

    def _detect_failure_pattern(self, context: AgentContext) -> str | None:
        if not context.steps:
            return None
        actions = [s.thought.action for s in context.steps]
        failures = [s for s in context.steps if not s.success]

        if len(failures) / max(len(context.steps), 1) > 0.4:
            return "tool_failure"
        if actions.count("web_search") > 4:
            return "tool_overuse"
        if not any(a == "finish" for a in actions):
            return "goal_drift"
        if actions.count(actions[0]) > 3:
            return "stuck_loop"
        return None
