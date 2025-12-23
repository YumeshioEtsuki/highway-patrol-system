#!/usr/bin/env python3
"""
直接启动 FastAPI（调试模式）
"""
import os
import sys

print("[STARTUP] Setting env vars...")
os.environ['SKIP_DB_INIT'] = '1'

print("[STARTUP] Importing app...")
try:
    from app import app
    print("[OK] App imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"[OK] App has {len(app.routes)} routes")

print("[STARTUP] Starting uvicorn server...")
try:
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=5000,
        log_level="debug"
    )
except KeyboardInterrupt:
    print("\n[SHUTDOWN] Server interrupted")
except Exception as e:
    print(f"[ERROR] Server error: {e}")
    import traceback
    traceback.print_exc()
