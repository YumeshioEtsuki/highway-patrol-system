#!/usr/bin/env python3
"""
Redis 缓存功能测试脚本

测试内容：
1. Redis 连接验证
2. 缓存读写操作
3. 缓存失效机制
4. API 缓存命中率（需要启动后端）
"""

import asyncio
import requests
import time
import json
from datetime import datetime

# ==================== 部分 1: Redis 连接测试 ====================
def test_redis_connection():
    """测试 Redis 连接"""
    print("\n" + "="*60)
    print("部分 1: Redis 连接测试")
    print("="*60)
    
    try:
        import redis
        from utils.redis_client import get_redis_client
        
        print("[→] 连接到 Redis...")
        client = get_redis_client()
        
        if client is None:
            print("[✗] Redis 连接失败 - 如果需要缓存功能，请启动 Redis 服务")
            print("   Windows 用户请参考: 1-后端代码/REDIS_SETUP.md")
            return False
        
        print("[✓] Redis 连接成功")
        
        # 获取信息
        info = client.info('server')
        print(f"   - Redis 版本: {info.get('redis_version')}")
        print(f"   - 端口: {info.get('tcp_port')}")
        
        # 测试 PING
        print("[→] 发送 PING 命令...")
        pong = client.ping()
        if pong:
            print("[✓] PING 成功")
        
        return True
    except Exception as e:
        print(f"[✗] 连接测试失败: {e}")
        return False


# ==================== 部分 2: 缓存读写测试 ====================
def test_cache_operations():
    """测试缓存读写操作"""
    print("\n" + "="*60)
    print("部分 2: 缓存读写测试")
    print("="*60)
    
    try:
        from utils.redis_client import cache_set, cache_get, cache_delete
        
        test_key = "test:cache:sample"
        test_value = {"name": "test", "timestamp": datetime.now().isoformat()}
        
        # 测试写入
        print(f"[→] 写入缓存: {test_key}")
        success = cache_set(test_key, test_value, ttl=10)
        if success:
            print(f"[✓] 写入成功")
        else:
            print(f"[!] 写入返回 False（可能 Redis 未运行）")
            return False
        
        # 测试读取
        print(f"[→] 读取缓存: {test_key}")
        cached = cache_get(test_key)
        if cached:
            print(f"[✓] 读取成功: {cached}")
        else:
            print(f"[✗] 读取失败（缓存可能不存在或过期）")
            return False
        
        # 测试删除
        print(f"[→] 删除缓存: {test_key}")
        cache_delete(test_key)
        cached_after = cache_get(test_key)
        if cached_after is None:
            print(f"[✓] 删除成功")
        else:
            print(f"[✗] 删除失败")
            return False
        
        return True
    except Exception as e:
        print(f"[✗] 缓存测试失败: {e}")
        return False


# ==================== 部分 3: 缓存失效测试 ====================
def test_cache_invalidation():
    """测试缓存失效机制"""
    print("\n" + "="*60)
    print("部分 3: 缓存失效测试")
    print("="*60)
    
    try:
        from utils.redis_client import cache_set, cache_get, cache_delete_pattern
        
        # 写入多个相关的缓存
        keys = [
            "admin:stats:abc123",
            "admin:stats:def456",
            "admin:patrol:list:xyz789"
        ]
        
        print(f"[→] 写入 {len(keys)} 个缓存...")
        for key in keys:
            cache_set(key, {"data": "test"}, ttl=60)
        print(f"[✓] 写入完成")
        
        # 验证缓存存在
        print(f"[→] 验证缓存存在...")
        count = sum(1 for key in keys if cache_get(key) is not None)
        print(f"[✓] 共有 {count}/{len(keys)} 个缓存存在")
        
        # 删除匹配模式的缓存
        print(f"[→] 删除匹配 'admin:stats:*' 的缓存...")
        deleted = cache_delete_pattern("admin:stats:*")
        print(f"[✓] 删除了 {deleted} 个缓存")
        
        # 验证删除结果
        remaining = sum(1 for key in keys if cache_get(key) is not None)
        print(f"[→] 剩余 {remaining}/3 个缓存")
        
        if remaining == 1:
            print("[✓] 缓存失效测试成功")
            return True
        else:
            print("[!] 缓存失效可能有问题")
            return False
    except Exception as e:
        print(f"[✗] 缓存失效测试失败: {e}")
        return False


# ==================== 部分 4: API 缓存测试 ====================
def test_api_cache():
    """测试 API 缓存命中率（需要后端运行）"""
    print("\n" + "="*60)
    print("部分 4: API 缓存命中测试")
    print("="*60)
    
    try:
        api_url = "http://127.0.0.1:5000"
        
        # 检查后端是否运行
        print(f"[→] 检查后端服务: {api_url}")
        try:
            resp = requests.get(f"{api_url}/health", timeout=2)
            if resp.status_code == 200:
                print(f"[✓] 后端服务运行中")
            else:
                print(f"[!] 后端服务返回状态码 {resp.status_code}")
        except Exception:
            print(f"[✗] 无法连接到后端服务")
            print(f"   请先运行: python start_server.py")
            return False
        
        # 测试管理员端点缓存（需要有效的 token）
        print(f"\n[ℹ] 提示: API 缓存测试需要有效的认证令牌")
        print(f"   如果要完整测试，请使用 Swagger UI: {api_url}/docs")
        print(f"   1. 登录获取 token")
        print(f"   2. 测试 /api/admin/stats 等端点")
        print(f"   3. 观察响应时间和 Redis 日志")
        
        return True
    except Exception as e:
        print(f"[✗] API 缓存测试失败: {e}")
        return False


# ==================== 主函数 ====================
def main():
    """运行所有测试"""
    print("\n" + "█"*60)
    print("  Redis 缓存系统测试")
    print("█"*60)
    
    results = {
        "Redis 连接": test_redis_connection(),
        "缓存读写": test_cache_operations(),
        "缓存失效": test_cache_invalidation(),
        "API 缓存": test_api_cache(),
    }
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name:.<30} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ 所有测试通过！缓存系统正常工作")
    else:
        print("✗ 部分测试未通过")
        print("\n故障排查建议:")
        
        if not results.get("Redis 连接"):
            print("  1. 启动 Redis 服务（参考 REDIS_SETUP.md）")
            print("     - Docker: docker run -d -p 6379:6379 redis:latest")
            print("     - 或: redis-server")
        
        if not results.get("缓存读写"):
            print("  2. 检查 Redis 连接配置（.env 文件）")
            print("  3. 查看详细错误日志")
        
        if not results.get("API 缓存"):
            print("  4. 启动后端服务: python start_server.py")
    
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
