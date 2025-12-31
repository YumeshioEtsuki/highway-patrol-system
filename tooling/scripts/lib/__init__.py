"""
环境变量管理库 - 提供给 CLI 和 Web 使用的核心功能
"""
from .env_manager import EnvManager
from .validators import (
    validate_config, 
    get_recommendations, 
    get_help_text,
    clear_ai_cache,
    clear_ai_cache_item,
    view_ai_cache,
    remove_from_ai_cache,
    submit_ai_feedback,
    get_ai_cache_stats,
    calculate_confidence_score,
    record_ai_recommendation_applied,
    record_ai_recommendation_modified,
    check_and_record_modifications,
    get_cache_with_confidence,
    get_adaptive_weights_info,
)
from .ai_helper import AIHelper, get_ai_helper

__all__ = [
    'EnvManager',
    'validate_config',
    'get_recommendations',
    'get_help_text',
    'clear_ai_cache',
    'clear_ai_cache_item',
    'view_ai_cache',
    'remove_from_ai_cache',
    'submit_ai_feedback',
    'get_ai_cache_stats',
    'calculate_confidence_score',
    'record_ai_recommendation_applied',
    'record_ai_recommendation_modified',
    'check_and_record_modifications',
    'get_cache_with_confidence',
    'get_adaptive_weights_info',
    'AIHelper',
    'get_ai_helper',
]
