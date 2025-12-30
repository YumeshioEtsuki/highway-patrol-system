#!/usr/bin/env python3
"""快速测试 Redis 连接"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "src"
sys.path.insert(0, str(BACKEND_DIR))

from settings import settings
from utils.redis_client import RedisClient

print("[INFO] Testing Redis connection...")
print(f"  REDIS_HOST: {settings.REDIS_HOST}")
print(f"  REDIS_PORT: {settings.REDIS_PORT}")
print(f"  REDIS_DB: {settings.REDIS_DB}")
print(f"  REDIS_PASSWORD: {repr(settings.REDIS_PASSWORD)} (empty: {not settings.REDIS_PASSWORD})")
print(f"  CELERY_BROKER_URL: {settings.CELERY_BROKER_URL}")

print("\n[INFO] Attempting to get Redis client...")
client = RedisClient.get_client()

if client:
    print("[OK] Redis client created successfully")
    try:
        result = client.ping()
        print(f"[OK] Redis PING response: {result}")
    except Exception as e:
        print(f"[ERROR] Redis PING failed: {e}")
else:
    print("[WARN] Redis client is None (connection failed, using memory cache)")

print("\n[INFO] Connection test complete")
