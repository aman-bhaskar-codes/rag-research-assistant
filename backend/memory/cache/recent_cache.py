import json

class RecentCache:

    def __init__(self, redis):
        self.redis = redis

    async def get(self, session_id):
        key = f"recent:{session_id}"
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, session_id, messages, ttl=60):
        key = f"recent:{session_id}"
        await self.redis.set(
            key,
            json.dumps(messages),
            ex=ttl
        )

    async def invalidate(self, session_id):
        key = f"recent:{session_id}"
        await self.redis.delete(key)