"""
环境变量管理库 - 提供给 CLI 和 Web 使用的核心功能
"""
from .env_manager import EnvManager
from .validators import (
    validate_config, 
    get_recommendations, 
    get_help_text,
    clear_ai_cache,
    view_ai_cache,
    remove_from_ai_cache,
)
from .ai_helper import AIHelper, get_ai_helper

__all__ = [
    'EnvManager',
    'validate_config',
    'get_recommendations',
    'get_help_text',
    'clear_ai_cache',
    'view_ai_cache',
    'remove_from_ai_cache',
    'AIHelper',
    'get_ai_helper',
]
