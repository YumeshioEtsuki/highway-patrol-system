# 限流配置（SlowAPI）
from slowapi import Limiter
from slowapi.util import get_remote_address

# 使用客户端 IP 作为限流键（不传 config，兼容当前 slowapi 版本）
limiter = Limiter(key_func=get_remote_address)
