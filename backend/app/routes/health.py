from fastapi import APIRouter
from sqlalchemy import text
from backend.app.database import engine
from backend.memory.short_term import get_redis

router = APIRouter()


@router.get("/health", tags=["health"])
async def health():
    db_ok = redis_ok = ollama_ok = False

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    try:
        r = await get_redis()
        await r.ping()
        redis_ok = True
    except Exception:
        pass

    try:
        import httpx
        from backend.app.config import get_settings
        s = get_settings()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{s.ollama_base_url}/api/tags", timeout=3)
            ollama_ok = resp.status_code == 200
    except Exception:
        pass

    status = "ok" if (db_ok and redis_ok) else "degraded"
    return {
        "status": status,
        "db": db_ok,
        "redis": redis_ok,
        "ollama": ollama_ok,
        "version": "2.0.0",
    }
