"""
配置管理模块
使用 python-dotenv 加载环境变量
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用基本信息
    APP_NAME: str = "石油巡检与设备管理系统"
    DEBUG: bool = False

    # 数据库配置 (异步 MySQL)
    DATABASE_URL: str = "mysql+aiomysql://root:password@localhost:3306/oil_inspection?charset=utf8mb4"
    SYNC_DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/oil_inspection?charset=utf8mb4"

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 120

    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_PHOTO_SIZE: str = "5MB"
    MAX_VIDEO_SIZE: str = "50MB"


@lru_cache()
def get_settings() -> Settings:
    """获取单例配置对象"""
    return Settings()


# 全局配置实例
settings = get_settings()
