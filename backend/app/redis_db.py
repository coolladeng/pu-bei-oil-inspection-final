"""
Redis 连接模块
"""

import redis.asyncio as aioredis

from app.config import settings


# 创建 Redis 连接池
redis_pool = aioredis.ConnectionPool.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=50,
)

redis_client = aioredis.Redis(connection_pool=redis_pool)


async def close_redis():
    """关闭 Redis 连接"""
    await redis_client.close()


async def get_redis():
    """获取 Redis 连接（用于依赖注入）"""
    return redis_client
