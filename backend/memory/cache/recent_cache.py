import json

class RecentCache:

    def __init__(self, redis_client):
        self.redis = redis_client

    async def get(self, session_id):
        data = await self.redis.get(f"recent:{session_id}")
        return json.loads(data) if data else None

    async def set(self, session_id, messages, ttl=60):
        await self.redis.set(
            f"recent:{session_id}",
            json.dumps(messages),
            ex=ttl
        )

    async def invalidate(self, session_id):
        await self.redis.delete(f"recent:{session_id}")