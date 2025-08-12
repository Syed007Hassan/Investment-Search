"""
Flush all keys from Redis using env-configured host/port.
Prints outcome to console; non-fatal on failure.
"""

import os
import logging
import time

import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def flush():
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", 6379))
    # small retry window in case redis just came up
    for attempt in range(1, 6):
        try:
            r = redis.Redis(host=host, port=port, decode_responses=True)
            pong = r.ping()
            if pong:
                logger.info("[flush_redis] Connected to Redis at %s:%s", host, port)
                r.flushall()
                logger.info("[flush_redis] FLUSHALL complete")
                return
        except Exception as e:
            logger.warning("[flush_redis] Attempt %d failed: %s", attempt, e)
            time.sleep(1)
    logger.error("[flush_redis] Could not connect to Redis after retries; skipping flush")


if __name__ == "__main__":
    flush()

