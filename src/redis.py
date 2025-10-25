import os
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")


class RedisClient:
    """Handles Redis connection."""

    def __init__(self):
        self.redis = None

    async def connect(self):
        """Establish Redis connection"""
        self.redis = await redis.from_url(
            REDIS_URL,
            password=REDIS_PASSWORD,
            decode_responses=True,
            max_connections=100,
        )

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()

    async def hset(self, key: str, mapping: dict = None, **kwargs):
        """Set hash fields"""
        if self.redis is None:
            raise RuntimeError(
                "Redis connection not established. Call connect() first."
            )
        return await self.redis.hset(key, mapping=mapping, **kwargs)

    async def hgetall(self, key: str):
        """Get all hash fields"""
        if self.redis is None:
            raise RuntimeError(
                "Redis connection not established. Call connect() first."
            )
        return await self.redis.hgetall(key)

    async def expire(self, key: str, time: int):
        """Set expiration time for a key"""
        if self.redis is None:
            raise RuntimeError(
                "Redis connection not established. Call connect() first."
            )
        return await self.redis.expire(key, time)

    async def delete(self, key: str):
        """Delete a key"""
        if self.redis is None:
            raise RuntimeError(
                "Redis connection not established. Call connect() first."
            )
        return await self.redis.delete(key)


redis_client = RedisClient()
