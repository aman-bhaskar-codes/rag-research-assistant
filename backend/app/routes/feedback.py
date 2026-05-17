from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_session
from backend.app.models import SearchTurn
import uuid

router = APIRouter()


class FeedbackRequest(BaseModel):
    turn_id: str
    feedback: int  # 1 = thumbs up, -1 = thumbs down


@router.post("")
async def submit_feedback(
    req: FeedbackRequest,
    session: AsyncSession = Depends(get_session),
):
    turn = await session.get(SearchTurn, uuid.UUID(req.turn_id))
    if not turn:
        raise HTTPException(404, "Turn not found")
    turn.feedback = req.feedback
    await session.commit()
    return {"ok": True}
