"""
Daily Evolution Protocol — runs every 24 hours.
Reviews yesterday's traces, proposes strategy updates, queues for human approval.
This is the human-in-loop RSI mechanism.
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from loguru import logger

from backend.app.agent_models import TaskOutcome, FailureLesson, CapabilityRecord
from backend.agent.observability.strategy_library import StrategyLibrary
from backend.app.config import get_settings

settings = get_settings()


class DailyEvolutionReport:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_daily_report(self) -> dict:
        """Summarize yesterday's runs and propose improvements."""
        yesterday = datetime.utcnow() - timedelta(hours=24)

        # Get yesterday's outcomes
        result = await self.db.execute(
            select(TaskOutcome).where(TaskOutcome.created_at >= yesterday)
        )
        outcomes = result.scalars().all()

        if not outcomes:
            return {"message": "No agent runs in the last 24 hours.", "proposals": []}

        total = len(outcomes)
        succeeded = sum(1 for o in outcomes if o.final_success)
        avg_quality = sum(o.quality_score or 0 for o in outcomes) / total
        avg_steps = sum(o.total_steps for o in outcomes) / total

        # Find top failure patterns
        failure_counts: dict[str, int] = {}
        for o in outcomes:
            if o.dominant_failure:
                failure_counts[o.dominant_failure] = failure_counts.get(o.dominant_failure, 0) + 1
        top_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        # Get weak categories
        cap_result = await self.db.execute(
            select(CapabilityRecord).where(CapabilityRecord.total_attempts >= 3)
        )
        cap_records = cap_result.scalars().all()
        weak_categories = [r.task_category for r in cap_records if r.is_weak]

        # Generate strategy proposals for each top failure
        proposals = []
        library = StrategyLibrary(self.db)

        for failure_pattern, count in top_failures[:2]:
            # Find a recent example of this failure
            example_outcome = next(
                (o for o in outcomes if o.dominant_failure == failure_pattern), None
            )
            if example_outcome:
                strategy_id = await library.evolve_strategy(
                    task_category=example_outcome.task_category,
                    failure_pattern=failure_pattern,
                    example_task=example_outcome.task_description[:300],
                    what_failed=f"Failure pattern: {failure_pattern}",
                )
                if strategy_id:
                    proposals.append({
                        "strategy_id": strategy_id,
                        "failure_pattern": failure_pattern,
                        "occurrences": count,
                    })

        report = {
            "period": "last_24_hours",
            "stats": {
                "total_tasks": total,
                "succeeded": succeeded,
                "failed": total - succeeded,
                "success_rate": round(succeeded / total, 3),
                "avg_quality": round(avg_quality, 3),
                "avg_steps": round(avg_steps, 1),
            },
            "top_failures": [{"pattern": f, "count": c} for f, c in top_failures],
            "weak_categories": weak_categories,
            "proposals": proposals,
            "action_required": len(proposals) > 0,
        }

        logger.info(
            f"Daily report: {total} tasks, {succeeded} succeeded, "
            f"{len(proposals)} strategy proposals pending approval"
        )
        return report


async def run_daily_evolution(db: AsyncSession) -> dict:
    """Entry point for scheduled daily evolution."""
    protocol = DailyEvolutionReport(db)
    return await protocol.generate_daily_report()
