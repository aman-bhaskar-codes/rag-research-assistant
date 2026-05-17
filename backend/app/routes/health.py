# backend/app/routes/health.py
from fastapi import APIRouter
from backend.app.database import engine
from backend.memory.short_term import _redis
from sqlalchemy import text

router = APIRouter()


@router.get("/health")
async def health():
    db_ok, redis_ok = False, False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass
    try:
        await _redis.ping()
        redis_ok = True
    except Exception:
        pass
    status = "ok" if (db_ok and redis_ok) else "degraded"
    return {"status": status, "db": db_ok, "redis": redis_ok}
