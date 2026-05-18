"""
Tracks agent success rates by task category.
Provides hints to the planner about known weak areas.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
from backend.app.agent_models import CapabilityRecord
from backend.agent.observability.task_classifier import TASK_CATEGORIES


class CapabilityMap:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def update(
        self,
        task_category: str,
        quality_score: float,
        steps_taken: int,
        failure_pattern: str | None,
    ) -> None:
        result = await self.db.execute(
            select(CapabilityRecord).where(CapabilityRecord.task_category == task_category)
        )
        record = result.scalar_one_or_none()

        if not record:
            record = CapabilityRecord(task_category=task_category)
            self.db.add(record)

        n = record.total_attempts
        record.total_attempts += 1
        if quality_score > 0.5:
            record.success_count += 1
        # Running average
        record.avg_quality = (record.avg_quality * n + quality_score) / (n + 1)
        record.avg_steps = (record.avg_steps * n + steps_taken) / (n + 1)
        if failure_pattern:
            record.most_common_failure = failure_pattern

        try:
            await self.db.commit()
        except Exception as e:
            logger.error(f"CapabilityMap update error: {e}")
            await self.db.rollback()

    async def get_hints_for_task(self, task_category: str) -> str:
        result = await self.db.execute(
            select(CapabilityRecord).where(CapabilityRecord.task_category == task_category)
        )
        record = result.scalar_one_or_none()

        if not record or record.total_attempts < 2:
            return ""

        if record.is_weak:
            hint = (
                f"⚠️ CAPABILITY WARNING: You have historically struggled with "
                f"'{task_category}' tasks (avg quality: {record.avg_quality:.0%}, "
                f"success rate: {record.success_rate:.0%} over {record.total_attempts} attempts).\n"
            )
            if record.most_common_failure:
                hint += f"Most common failure pattern: '{record.most_common_failure}'.\n"
            hint += "Consider: use write_note to accumulate findings before synthesizing. Be more systematic."
            return hint
        return ""

    async def get_full_map(self) -> list[dict]:
        result = await self.db.execute(select(CapabilityRecord))
        records = result.scalars().all()
        return [
            {
                "category": r.task_category,
                "attempts": r.total_attempts,
                "success_rate": round(r.success_rate, 3),
                "avg_quality": round(r.avg_quality, 3),
                "avg_steps": round(r.avg_steps, 1),
                "is_weak": r.is_weak,
                "common_failure": r.most_common_failure,
            }
            for r in sorted(records, key=lambda x: x.avg_quality)
        ]

    async def get_weak_areas(self) -> list[str]:
        full = await self.get_full_map()
        return [r["category"] for r in full if r["is_weak"]]
