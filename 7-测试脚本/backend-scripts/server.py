#!/usr/bin/env python3
"""
启动脚本 - 公路巡查系统 v2
支持环境变量配置
"""
import os
import sys
import asyncio
import uvicorn

# 环境配置
os.environ['SKIP_DB_INIT'] = '1'
PORT = int(os.getenv('PORT', '5000'))
HOST = os.getenv('HOST', '127.0.0.1')

print("\n" + "=" * 70)
print("HIGHWAY PATROL SYSTEM")
print("=" * 70)

# 第 1 步：检查 Ollama
print("\n[STEP 1] Verifying Ollama service...")
try:
    import httpx
    r = httpx.get('http://127.0.0.1:11434/api/tags', timeout=2)
    models = [m['name'] for m in r.json()['models']]
    print(f"  ✓ Ollama running with models: {models}")
except Exception as e:
    print(f"  ⚠ Ollama check failed: {e}")
    print("  ℹ Please ensure Ollama is running: ollama serve")

# 第 2 步：加载应用
print("\n[STEP 2] Loading application...")
try:
    from app import app
    print(f"  ✓ App loaded ({len(app.routes)} routes)")
except Exception as e:
    print(f"  ✗ Failed to load app: {e}")
    sys.exit(1)

# 第 3 步：配置 Uvicorn
print("\n[STEP 3] Configuring Uvicorn...")
config = uvicorn.Config(
    app,
    host=HOST,
    port=PORT,
    log_level="info",
    access_log=True
)
server = uvicorn.Server(config)
print(f"  ✓ Config ready")

# 第 4 步：启动服务器
print("\n[STEP 4] Starting server...")
print(f"\n{'=' * 70}")
print(f"  Website:  http://{HOST}:{PORT}")
print(f"  API docs: http://{HOST}:{PORT}/docs")
print(f"  Chat API: POST http://{HOST}:{PORT}/api/chat")
print(f"  Press Ctrl+C to stop")
print(f"{'=' * 70}\n")

try:
    asyncio.run(server.serve())
except KeyboardInterrupt:
    print(f"\n{'=' * 70}")
    print("SHUTDOWN: Gracefully shutting down...")
    print(f"{'=' * 70}")
except Exception as e:
    print(f"\n{'=' * 70}")
    print(f"ERROR: {e}")
    print(f"{'=' * 70}")
    sys.exit(1)
