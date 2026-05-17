import json
import redis.asyncio as aioredis
from backend.app.config import get_settings

settings = get_settings()
_redis: aioredis.Redis | None = None


async def init_redis():
    global _redis
    _redis = aioredis.from_url(
        settings.redis_url,
        decode_responses=True,
        max_connections=20,
    )
    await _redis.ping()


async def close_redis():
    if _redis:
        await _redis.aclose()


async def get_redis() -> aioredis.Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialised")
    return _redis


def _key(session_id: str) -> str:
    return f"chat:{session_id}:messages"


async def push_message(session_id: str, role: str, content: str) -> None:
    r = await get_redis()
    msg = json.dumps({"role": role, "content": content})
    key = _key(session_id)
    await r.rpush(key, msg)
    await r.ltrim(key, -settings.max_context_messages, -1)
    await r.expire(key, 86400)  # 24h TTL


async def get_history(session_id: str) -> list[dict]:
    r = await get_redis()
    msgs = await r.lrange(_key(session_id), 0, -1)
    return [json.loads(m) for m in msgs]


async def clear_history(session_id: str) -> None:
    r = await get_redis()
    await r.delete(_key(session_id))


async def cache_set(key: str, value: str, ttl: int = 300) -> None:
    r = await get_redis()
    await r.setex(f"cache:{key}", ttl, value)


async def cache_get(key: str) -> str | None:
    r = await get_redis()
    return await r.get(f"cache:{key}")
