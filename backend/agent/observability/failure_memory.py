"""
Stores and retrieves structured failure lessons.
Injected into agent system prompt before each task — persistent cross-session learning.
Lessons validated/decayed based on whether they actually helped.
"""
import re
import json
import ollama
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from loguru import logger

from backend.app.agent_models import FailureLesson
from backend.agent.context import AgentContext
from backend.rag_engine.embeddings import embed_query
from backend.app.config import get_settings

settings = get_settings()

LESSON_EXTRACTION_PROMPT = """You are analyzing a failed AI research agent run to extract a reusable lesson.

Task: {task}
Task Category: {task_category}
Total Steps: {total_steps}
Failure Pattern: {failure_pattern}
Quality Score: {quality_score:.2f}

Step History:
{step_history}

Extract a structured lesson for future runs. Output ONLY valid JSON:
{{
  "situation_type": "brief category name e.g. multi-hop research",
  "trigger_pattern": "the specific pattern that triggered this failure e.g. query asks to compare X and Y",
  "what_failed": "concrete description of what went wrong",
  "why_it_failed": "root cause analysis",
  "better_approach": "step-by-step better strategy for next time",
  "example_task": "the original task as reference"
}}"""


class FailureMemory:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_relevant_lessons(self, task: str, top_k: int = 3) -> str:
        """Retrieve relevant past failure lessons before starting a task."""
        embedding = embed_query(task)

        rows = await self.db.execute(text("""
            SELECT situation_type, trigger_pattern, better_approach,
                   confidence, validated_count, failed_count,
                   1 - (embedding <=> :vec::vector) AS similarity
            FROM failure_lessons
            WHERE confidence > 0.3
            ORDER BY embedding <=> :vec::vector
            LIMIT :k
        """), {"vec": str(embedding), "k": top_k})

        lessons = rows.fetchall()
        if not lessons:
            return ""

        lines = ["LESSONS FROM PAST FAILURES:"]
        for lesson in lessons:
            reliability = lesson.validated_count / max(lesson.validated_count + lesson.failed_count, 1)
            if lesson.similarity < 0.5:
                continue  # too dissimilar — skip
            lines.append(
                f"Pattern: {lesson.trigger_pattern}\n"
                f"Avoid: {lesson.what_failed if hasattr(lesson, 'what_failed') else ''}\n"
                f"Better approach: {lesson.better_approach}\n"
                f"Reliability: {reliability:.0%} ({lesson.validated_count} validations)"
            )
        return "\n\n".join(lines) if len(lines) > 1 else ""

    async def extract_and_store_lesson(
        self,
        task: str,
        context: AgentContext,
        failure_pattern: str,
        quality_score: float,
    ) -> None:
        """Use LLM to extract a structured lesson from this failure."""
        step_history = context.to_prompt_history(max_steps=8)

        from backend.agent.observability.task_classifier import classify_task
        task_category = await classify_task(task)

        prompt = LESSON_EXTRACTION_PROMPT.format(
            task=task,
            task_category=task_category,
            total_steps=len(context.steps),
            failure_pattern=failure_pattern,
            quality_score=quality_score,
            step_history=step_history[:1500],
        )

        client = ollama.AsyncClient(host=settings.ollama_base_url)
        resp = await client.generate(
            model=settings.smart_model,  # phi4-mini — needs reasoning
            prompt=prompt,
            options={"temperature": 0.2, "num_predict": 400},
        )
        raw = resp["response"].strip()
        raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            logger.warning("Failed to extract lesson — no JSON in response")
            return

        try:
            data = json.loads(match.group())
        except json.JSONDecodeError as e:
            logger.error(f"Lesson JSON parse failed: {e}")
            return

        trigger_text = data.get("trigger_pattern", task[:200])
        embedding = embed_query(trigger_text)

        lesson = FailureLesson(
            situation_type=data.get("situation_type", failure_pattern),
            trigger_pattern=data.get("trigger_pattern", ""),
            what_failed=data.get("what_failed", ""),
            why_it_failed=data.get("why_it_failed", ""),
            better_approach=data.get("better_approach", ""),
            example_task=data.get("example_task", task[:400]),
            confidence=0.5,
            embedding=embedding,
        )
        self.db.add(lesson)
        try:
            await self.db.commit()
            logger.info(f"Stored failure lesson: {lesson.situation_type}")
        except Exception as e:
            logger.error(f"Failed to store lesson: {e}")
            await self.db.rollback()

    async def validate_lesson(self, lesson_id: str) -> None:
        """Call when a lesson was retrieved and the task succeeded."""
        from sqlalchemy import select
        import uuid
        lesson = await self.db.get(FailureLesson, uuid.UUID(lesson_id))
        if lesson:
            lesson.validated_count += 1
            lesson.confidence = lesson.reliability_score
            await self.db.commit()

    async def decay_lesson(self, lesson_id: str) -> None:
        """Call when a lesson was retrieved but task still failed."""
        from sqlalchemy import select
        import uuid
        lesson = await self.db.get(FailureLesson, uuid.UUID(lesson_id))
        if lesson:
            lesson.failed_count += 1
            lesson.confidence = lesson.reliability_score
            if lesson.confidence < 0.1:
                await self.db.delete(lesson)  # prune consistently wrong lessons
            await self.db.commit()
