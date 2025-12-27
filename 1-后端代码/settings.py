# config.py

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Set, Optional


class Settings(BaseSettings):
    """应用配置（支持从环境变量或 .env 文件读取）"""
    
    # 数据库配置
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: Optional[str] = None
    DATABASE_NAME: str = "road_patrol_db"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 验证必填的敏感配置
        if not self.DATABASE_PASSWORD:
            raise ValueError(
                "DATABASE_PASSWORD 未配置！\n"
                "请设置环境变量 DATABASE_PASSWORD 或在 .env 文件中配置 DATABASE_PASSWORD=your_password\n"
                "参考文档: docs/SECURITY_CONFIG.md"
            )
    
    # 向后兼容的别名
    @property
    def DB_HOST(self): return self.DATABASE_HOST
    @property
    def DB_USER(self): return self.DATABASE_USER
    @property
    def DB_PASSWORD(self): return self.DATABASE_PASSWORD
    @property
    def DB_NAME(self): return self.DATABASE_NAME
    
    # 应用配置
    DEBUG: bool = True
    SECRET_KEY: str = "road_patrol_dev_secret_2025_do_not_use_in_production"
    # 分页上限（避免过大分页导致性能问题）
    MAX_PAGE_SIZE: int = 200
    
    # JWT 配置
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    
    # 文件上传/生成路径（默认使用项目后端目录下的 photos）
    UPLOAD_FOLDER: str = "photos"
    PHOTO_OUTPUT_FOLDER: str = "photos/generated"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: Set[str] = {'png', 'jpg', 'jpeg', 'gif'}
    
    # CORS 配置（如需前后端分离）
    # 默认不开放跨域；开发时请在 .env 中设置允许的域名
    ALLOW_ORIGINS: list = []
    
    # Redis 缓存配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Celery 配置（任务队列）
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list = ["json"]
    CELERY_TIMEZONE: str = "Asia/Shanghai"
    
    # 启动控制参数
    SKIP_DB_INIT: bool = False
    
    model_config = SettingsConfigDict(
        # 统一 .env 路径为后端目录下的 .env（无论工作目录在哪都能正确加载）
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# 创建全局配置实例
settings = Settings()

# 规范化上传目录：若为相对路径，统一转换为后端根目录下的绝对路径
_BASE_DIR = Path(__file__).resolve().parent.parent
_upload_path = Path(settings.UPLOAD_FOLDER)
if not _upload_path.is_absolute():
    settings.UPLOAD_FOLDER = str((_BASE_DIR / _upload_path).resolve())

_output_path = Path(settings.PHOTO_OUTPUT_FOLDER)
if not _output_path.is_absolute():
    settings.PHOTO_OUTPUT_FOLDER = str((_BASE_DIR / _output_path).resolve())

# 数据库连接配置（保持向后兼容）
db_config = {
    'host': settings.DATABASE_HOST,
    'port': settings.DATABASE_PORT,
    'user': settings.DATABASE_USER,
    'password': settings.DATABASE_PASSWORD,
    'database': settings.DATABASE_NAME
}


# 已废弃的旧配置类（保留以兼容旧代码）
class Config:
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = settings.SECRET_KEY


class ProductionConfig(Config):
    DEBUG = False