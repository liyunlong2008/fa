from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""
    # 应用配置
    APP_NAME: str = "FastAPI管理系统"
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./app.db"

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # 后台入口配置
    ADMIN_PREFIX: str = "/adm"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# 创建全局设置实例
settings = Settings()