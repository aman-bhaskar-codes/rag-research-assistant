from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.app.database import get_session
from backend.app.models import SearchSession, SearchTurn

router = APIRouter()


@router.get("")
async def get_history(
    session_key: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(SearchSession)
        .where(SearchSession.session_key == session_key)
        .order_by(desc(SearchSession.updated_at))
        .limit(limit)
        .options(selectinload(SearchSession.turns))
    )
    sessions = result.scalars().all()

    return {
        "sessions": [
            {
                "id": str(s.id),
                "title": s.title,
                "focus_mode": s.focus_mode,
                "model_used": s.model_used,
                "created_at": s.created_at.isoformat(),
                "turn_count": len(s.turns),
                "last_query": s.turns[-1].query if s.turns else None,
            }
            for s in sessions
        ]
    }


@router.get("/{session_id}")
async def get_session_detail(
    session_id: str,
    session: AsyncSession = Depends(get_session),
):
    import uuid as uuid_mod
    result = await session.get(
        SearchSession, uuid_mod.UUID(session_id),
        options=[selectinload(SearchSession.turns)]
    )
    if not result:
        from fastapi import HTTPException
        raise HTTPException(404, "Session not found")

    return {
        "id": str(result.id),
        "title": result.title,
        "focus_mode": result.focus_mode,
        "model_used": result.model_used,
        "turns": [
            {
                "id": str(t.id),
                "query": t.query,
                "answer": t.answer,
                "sources": t.sources,
                "related_questions": t.related_questions,
                "model_used": t.model_used,
                "created_at": t.created_at.isoformat(),
                "feedback": t.feedback,
            }
            for t in result.turns
        ],
    }
