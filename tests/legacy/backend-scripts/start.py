#!/usr/bin/env python3
"""
启动脚本 - 公路巡查系统
"""
import os
import sys

os.environ['SKIP_DB_INIT'] = '1'

print("\n" + "=" * 70)
print("HIGHWAY PATROL SYSTEM - STARTING")
print("=" * 70)

# 检查 Ollama
print("\n[CHECK] Verifying Ollama service...")
try:
    import httpx
    r = httpx.get('http://127.0.0.1:11434/api/tags', timeout=2)
    models = [m['name'] for m in r.json()['models']]
    print(f"[OK] Ollama online with models: {models}")
except Exception as e:
    print(f"[WARN] Ollama not reachable: {e}")
    print("[WARN] Please ensure Ollama is running: ollama serve")

# 导入应用
print("\n[LOADING] Importing FastAPI application...")
try:
    from app import app
    print("[OK] Application loaded")
except Exception as e:
    print(f"[ERROR] Failed to load app: {e}")
    sys.exit(1)

# 启动 Uvicorn
print("\n[STARTUP] Starting Uvicorn server...")
print("[INFO] Visit: http://127.0.0.1:5000")
print("[INFO] API docs: http://127.0.0.1:5000/docs")
print("[INFO] Chat API: POST http://127.0.0.1:5000/api/chat")
print("[INFO] Press Ctrl+C to stop")
print("=" * 70 + "\n")

try:
    import asyncio
    import uvicorn
    
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=5000,
        log_level="info",
        access_log=True
    )
    server = uvicorn.Server(config)
    asyncio.run(server.serve())
except KeyboardInterrupt:
    print("\n[SHUTDOWN] Gracefully shutting down...")
except Exception as e:
    print(f"\n[ERROR] Server error: {e}")
    sys.exit(1)

