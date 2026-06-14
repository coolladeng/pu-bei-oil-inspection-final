"""
数据库连接模块 (SQLAlchemy 2.0 异步)
支持 SQLite (开发) 和 MySQL (生产)
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# 判断是否为SQLite
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# 创建异步引擎 (SQLite需要特殊参数)
_engine_kwargs = {}
if _is_sqlite:
    _engine_kwargs = {"echo": settings.DEBUG}
else:
    _engine_kwargs = {
        "echo": settings.DEBUG,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }

engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

# 创建异步 session 工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy 基类"""
    pass


async def get_db() -> AsyncSession:
    """
    获取数据库 session 的依赖注入
    使用异步生成器，自动管理 session 生命周期
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库表（开发环境使用）"""
    from app import models  # noqa: F401  # 导入所有模型注册到 Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()