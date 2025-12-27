"""
缓存装饰器（用于 FastAPI 路由）
"""
import json
import hashlib
from functools import wraps
from typing import Optional, Callable, Any
from utils.redis_client import cache_get, cache_set

def cache_response(ttl: int = 300, key_prefix: str = "api"):
    """
    缓存装饰器：将路由的 JSON 响应缓存到 Redis
    
    参数：
        ttl: 缓存过期时间（秒），默认 5 分钟
        key_prefix: 缓存键前缀，用于区分不同模块
    
    示例：
        @router.get("/statistics")
        @cache_response(ttl=600, key_prefix="stats")
        async def get_statistics(scope: str, value: str):
            # 路由逻辑
            return {...}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 生成缓存键（基于函数名和参数）
            cache_key = _generate_cache_key(key_prefix, func.__name__, kwargs)
            
            # 尝试从缓存读取
            cached = cache_get(cache_key)
            if cached is not None:
                return cached
            
            # 执行原函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            if result is not None:
                cache_set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = _generate_cache_key(key_prefix, func.__name__, kwargs)
            
            # 尝试从缓存读取
            cached = cache_get(cache_key)
            if cached is not None:
                return cached
            
            # 执行原函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            if result is not None:
                cache_set(cache_key, result, ttl)
            
            return result
        
        # 返回合适的包装函数（异步或同步）
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def _generate_cache_key(prefix: str, func_name: str, params: dict) -> str:
    """
    生成缓存键
    格式: prefix:func_name:param_hash
    """
    # 过滤分页参数，避免缓存污染
    exclude_keys = {"page_size", "page", "limit", "offset"}
    filtered_params = {k: v for k, v in params.items() if k not in exclude_keys}
    param_str = json.dumps(filtered_params, sort_keys=True, default=str)
    param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
    return f"{prefix}:{func_name}:{param_hash}"


def invalidate_cache(pattern: str = "*"):
    """
    手动失效缓存（通常在数据修改时调用）
    
    示例：
        @router.post("/patrol")
        async def create_patrol(data: PatrolSchema):
            # 创建巡查记录
            # ...
            # 失效缓存
            invalidate_cache("stats:*")
            return result
    """
    from utils.redis_client import cache_delete_pattern
    return cache_delete_pattern(pattern)
