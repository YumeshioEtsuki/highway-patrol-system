# 限流配置（SlowAPI）
from slowapi import Limiter
from slowapi.util import get_remote_address
import os
import builtins

class LazyLimiter:
    """延迟初始化的 Limiter 包装，避免导入时读取 .env 编码问题"""
    def __init__(self):
        self._limiter = None
    
    def _ensure_initialized(self):
        if self._limiter is None:
            # 临时修补 open() 以使用 UTF-8，避免 Starlette Config 的 GBK 编码问题
            original_open = builtins.open
            
            def patched_open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
                # 如果是文本模式且未指定编码，使用 UTF-8
                if isinstance(mode, str) and 'b' not in mode and encoding is None:
                    encoding = 'utf-8'
                return original_open(file, mode, buffering, encoding, errors, newline)
            
            try:
                builtins.open = patched_open
                self._limiter = Limiter(key_func=get_remote_address)
            finally:
                builtins.open = original_open
        return self._limiter
    
    def limit(self, *args, **kwargs):
        """代理 limiter.limit() 方法"""
        return self._ensure_initialized().limit(*args, **kwargs)
    
    def __getattr__(self, name):
        """代理其他属性和方法"""
        return getattr(self._ensure_initialized(), name)

# 全局 limiter 实例
limiter = LazyLimiter()


