"""
Learned task-solving playbooks.
Starts empty. Agent generates new strategies after failures.
You approve them (10 seconds). System applies them forever.
"""
import re
import json
import ollama
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from loguru import logger

from backend.app.agent_models import Strategy
from backend.rag_engine.embeddings import embed_query
from backend.app.config import get_settings

settings = get_settings()

STRATEGY_EVOLUTION_PROMPT = """An AI research agent failed at this type of task.
Failure pattern: {failure_pattern}
Task category: {task_category}
Current approach (if any): {current_strategy}
Example failed task: {example_task}
What went wrong: {what_failed}

Write a concise, actionable step-by-step strategy to handle this task type better.
Be specific. Include: when to use it, what to do at each step, what to avoid.

Output ONLY JSON:
{{
  "trigger_description": "when to apply this strategy",
  "strategy_text": "1. First do X\\n2. Then Y\\n3. Finally Z",
  "expected_improvement": "brief explanation of why this is better"
}}"""


class StrategyLibrary:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_relevant_strategy(self, task: str) -> str | None:
        embedding = embed_query(task)
        rows = await self.db.execute(text("""
            SELECT trigger_description, strategy_text, success_rate, sample_size
            FROM strategy_library
            WHERE approved = true AND success_rate > 0.55
            ORDER BY embedding <=> :vec::vector
            LIMIT 1
        """), {"vec": str(embedding)})
        row = rows.fetchone()
        if row and row.success_rate > 0.55 and row.sample_size >= 2:
            return (
                f"LEARNED STRATEGY (success rate: {row.success_rate:.0%}, "
                f"n={row.sample_size}):\n{row.strategy_text}"
            )
        return None

    async def evolve_strategy(
        self,
        task_category: str,
        failure_pattern: str,
        example_task: str,
        what_failed: str,
    ) -> str | None:
        """Generate a new strategy after a failure. Returns strategy ID for approval."""
        # Check if we have an existing strategy for this category
        rows = await self.db.execute(text("""
            SELECT strategy_text FROM strategy_library
            WHERE trigger_description ILIKE :cat
            LIMIT 1
        """), {"cat": f"%{task_category}%"})
        existing_row = rows.fetchone()
        current_strategy = existing_row.strategy_text if existing_row else "No existing strategy"

        prompt = STRATEGY_EVOLUTION_PROMPT.format(
            failure_pattern=failure_pattern,
            task_category=task_category,
            current_strategy=current_strategy[:500],
            example_task=example_task[:300],
            what_failed=what_failed[:300],
        )

        client = ollama.AsyncClient(host=settings.ollama_base_url)
        resp = await client.generate(
            model=settings.smart_model,
            prompt=prompt,
            options={"temperature": 0.3, "num_predict": 400},
        )
        raw = resp["response"].strip()
        raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None

        try:
            data = json.loads(match.group())
        except json.JSONDecodeError:
            return None

        trigger = data.get("trigger_description", task_category)
        embedding = embed_query(trigger)

        strategy = Strategy(
            trigger_description=trigger,
            strategy_text=data.get("strategy_text", ""),
            source="agent",
            success_rate=0.5,
            sample_size=1,
            approved=False,  # REQUIRES HUMAN APPROVAL
            embedding=embedding,
        )
        self.db.add(strategy)
        await self.db.commit()

        logger.info(f"New strategy proposed (pending approval): {trigger[:60]}")
        return str(strategy.id)

    async def get_pending_approvals(self) -> list[dict]:
        """Returns strategies awaiting human approval."""
        result = await self.db.execute(
            select(Strategy).where(Strategy.approved == False)  # noqa: E712
            .order_by(Strategy.created_at.desc())
        )
        strategies = result.scalars().all()
        return [
            {
                "id": str(s.id),
                "trigger": s.trigger_description,
                "strategy": s.strategy_text,
                "source": s.source,
                "created_at": s.created_at.isoformat(),
            }
            for s in strategies
        ]

    async def approve_strategy(self, strategy_id: str) -> bool:
        import uuid
        strategy = await self.db.get(Strategy, uuid.UUID(strategy_id))
        if not strategy:
            return False
        strategy.approved = True
        await self.db.commit()
        logger.info(f"Strategy approved: {strategy.trigger_description[:60]}")
        return True

    async def update_strategy_performance(self, strategy_id: str, succeeded: bool) -> None:
        import uuid
        strategy = await self.db.get(Strategy, uuid.UUID(strategy_id))
        if not strategy:
            return
        n = strategy.sample_size
        strategy.sample_size += 1
        strategy.success_rate = (strategy.success_rate * n + (1.0 if succeeded else 0.0)) / (n + 1)
        # Auto-retire strategies with consistently poor performance
        if strategy.sample_size >= 5 and strategy.success_rate < 0.25:
            strategy.approved = False
            logger.warning(f"Auto-retired poor strategy: {strategy.trigger_description[:60]}")
        await self.db.commit()
