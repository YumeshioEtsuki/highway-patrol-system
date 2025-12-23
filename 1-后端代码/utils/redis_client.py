"""
Redis 客户端与连接管理
"""
import redis
import asyncio
from typing import Optional
from utils.config import settings

class RedisClient:
    """Redis 同步客户端单例"""
    _instance: Optional[redis.Redis] = None
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        """获取或创建 Redis 客户端"""
        if cls._instance is None:
            cls._instance = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE
                    2: 3,  # TCP_KEEPINTVL
                    3: 5,  # TCP_KEEPCNT
                },
            )
            # 测试连接
            try:
                cls._instance.ping()
                print("[OK] Redis 连接成功")
            except Exception as e:
                print(f"[WARN] Redis 连接失败: {e}，缓存功能将被禁用")
                cls._instance = None
        return cls._instance
    
    @classmethod
    def close(cls):
        """关闭连接"""
        if cls._instance:
            cls._instance.close()
            cls._instance = None


def get_redis_client() -> Optional[redis.Redis]:
    """依赖注入：获取 Redis 客户端（可能为 None）"""
    return RedisClient.get_client()


def cache_get(key: str, default=None):
    """获取缓存值"""
    client = get_redis_client()
    if not client:
        return default
    try:
        value = client.get(key)
        if value:
            import json
            return json.loads(value)
    except Exception as e:
        print(f"[WARN] 缓存读取失败 {key}: {e}")
    return default


def cache_set(key: str, value, ttl: int = 300):
    """设置缓存值（TTL 秒）"""
    client = get_redis_client()
    if not client:
        return False
    try:
        import json
        client.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception as e:
        print(f"[WARN] 缓存写入失败 {key}: {e}")
        return False


def cache_delete(key: str):
    """删除缓存"""
    client = get_redis_client()
    if not client:
        return False
    try:
        client.delete(key)
        return True
    except Exception as e:
        print(f"[WARN] 缓存删除失败 {key}: {e}")
        return False


def cache_delete_pattern(pattern: str):
    """删除匹配模式的所有缓存"""
    client = get_redis_client()
    if not client:
        return 0
    try:
        keys = client.keys(pattern)
        if keys:
            return client.delete(*keys)
        return 0
    except Exception as e:
        print(f"[WARN] 缓存批量删除失败 {pattern}: {e}")
        return 0
