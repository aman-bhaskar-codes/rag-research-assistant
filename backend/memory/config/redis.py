import redis.asyncio as redis

def get_redis():
    return redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True
    )