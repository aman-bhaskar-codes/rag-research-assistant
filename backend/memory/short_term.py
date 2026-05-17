# backend/memory/short_term.py
import json
import redis.asyncio as aioredis
from backend.app.config import get_settings

settings = get_settings()

_redis: aioredis.Redis | None = None


async def init_redis():
    global _redis
    _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    await _redis.ping()  # validate connection at startup


async def close_redis():
    if _redis:
        await _redis.aclose()


def _key(session_id: str) -> str:
    return f"session:{session_id}:messages"


async def push_message(session_id: str, role: str, content: str) -> None:
    """Append a message and trim to MAX_CONTEXT_MESSAGES."""
    key = _key(session_id)
    msg = json.dumps({"role": role, "content": content})
    await _redis.rpush(key, msg)
    await _redis.ltrim(key, -settings.max_context_messages, -1)
    # TTL: auto-expire after 24 hours of inactivity
    await _redis.expire(key, 86400)


async def get_history(session_id: str) -> list[dict]:
    """Return the last N messages for this session."""
    msgs = await _redis.lrange(_key(session_id), 0, -1)
    return [json.loads(m) for m in msgs]
