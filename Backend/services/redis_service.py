from typing import Optional, Any
import json
from redis import Redis
from config.main import config

class RedisService:
    def __init__(self):
        self.redis_client = Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            decode_responses=True
        )

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in Redis with expiration"""
        try:
            return self.redis_client.setex(
                key,
                expire,
                json.dumps(value)
            )
        except Exception as e:
            print(f"Redis set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False

    async def keys(self, pattern: str) -> list:
        """Get all keys matching the pattern"""
        try:
            return self.redis_client.keys(pattern)
        except Exception as e:
            print(f"Redis keys error: {e}")
            return []

    async def scan_and_delete(self, pattern: str) -> bool:
        """Scan and delete all keys matching the pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return bool(self.redis_client.delete(*keys))
            return True
        except Exception as e:
            print(f"Redis scan and delete error: {e}")
            return False 