#!/usr/bin/env python3
"""
极简测试应用
"""
import os
os.environ['SKIP_DB_INIT'] = '1'

from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/chat/health")
def chat_health():
    return {"status": "ok", "message": "Ollama ready"}

if __name__ == '__main__':
    import uvicorn
    print("[STARTUP] Starting minimal FastAPI app...")
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")
