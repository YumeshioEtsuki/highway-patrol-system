# config.py

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices
from pathlib import Path
from typing import Set, Optional

# 导入主配置以保持一致性
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from settings import settings as main_settings
    # 使用主配置中的 settings
    settings = main_settings
except ImportError:
    # 回退到本地配置

    
    # 向后兼容的别名
        class Settings(BaseSettings):
            """应用配置（支持从环境变量或 .env 文件读取）"""
        
            # 数据库配置
            DATABASE_HOST: str = "localhost"
            DATABASE_PORT: int = 3306
            DATABASE_USER: str = "root"
            DATABASE_PASSWORD: Optional[str] = Field(
                default=None,
                validation_alias=AliasChoices('DATABASE_PASSWORD', 'DB_PASSWORD')
            )
            DATABASE_NAME: str = "road_patrol_db"
        
            model_config = SettingsConfigDict(
                env_file=str(Path(__file__).resolve().parent.parent / ".env"),
                env_file_encoding="utf-8",
                case_sensitive=True,
                extra="ignore"
            )
    
        settings = Settings()


# 规范化上传目录：若为相对路径，统一转换为后端根目录下的绝对路径
_BASE_DIR = Path(__file__).resolve().parent.parent
_upload_path = Path(settings.UPLOAD_FOLDER)
if not _upload_path.is_absolute():
    settings.UPLOAD_FOLDER = str((_BASE_DIR / _upload_path).resolve())

# 数据库连接配置（保持向后兼容）
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