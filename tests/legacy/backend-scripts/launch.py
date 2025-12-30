#!/usr/bin/env python3
"""
生产启动脚本 - 使用 Gunicorn
"""
import os
import subprocess
import sys

os.environ['SKIP_DB_INIT'] = '1'

# 检查 Ollama 连接
print("[CHECK] Verifying Ollama service...")
try:
    import httpx
    r = httpx.get('http://127.0.0.1:11434/api/tags', timeout=2)
    models = [m['name'] for m in r.json()['models']]
    print(f"[OK] Ollama online with models: {models}")
except Exception as e:
    print(f"[WARN] Ollama not reachable: {e}")
    print("[WARN] Please make sure Ollama is running: ollama serve")

# 启动 Gunicorn
print("[STARTUP] Starting application with Gunicorn...")
cmd = [
    sys.executable, '-m', 'gunicorn',
    'app:app',
    '--workers', '1',
    '--worker-class', 'uvicorn.workers.UvicornWorker',
    '--bind', '127.0.0.1:5000',
    '--timeout', '120',
    '--access-logfile', '-',
    '--error-logfile', '-'
]

try:
    subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
except KeyboardInterrupt:
    print("\n[SHUTDOWN] Gracefully shutting down...")
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)
