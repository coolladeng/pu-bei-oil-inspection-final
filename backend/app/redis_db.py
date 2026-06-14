"""
Redis 连接模块 (可选 - 开发环境无Redis可正常运行)
"""

import redis.asyncio as aioredis

from app.config import settings

redis_client = None


def _get_redis_client():
    global redis_client
    if redis_client is None:
        try:
            redis_pool = aioredis.ConnectionPool.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,
            )
            redis_client = aioredis.Redis(connection_pool=redis_pool)
        except Exception:
            redis_client = False
    return redis_client if redis_client is not False else None


async def close_redis():
    """关闭 Redis 连接"""
    client = _get_redis_client()
    if client:
        await client.close()


async def get_redis():
    """获取 Redis 连接（用于依赖注入）"""
    return _get_redis_client()