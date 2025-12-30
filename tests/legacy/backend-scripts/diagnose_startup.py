#!/usr/bin/env python3
"""
诊断脚本 - 全面检查启动问题
"""
import os
import sys
import socket
import subprocess
import time

print("=" * 70)
print("UVICORN STARTUP DIAGNOSIS")
print("=" * 70)

# 1. 检查端口占用
print("\n[1] CHECKING PORT USAGE...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 5000))
    sock.close()
    if result == 0:
        print("   ✗ Port 5000 is ALREADY IN USE")
        # 尝试找出占用的进程
        proc = subprocess.run(['netstat', '-ano', '|', 'find', '5000'], 
                            shell=True, capture_output=True, text=True)
        if proc.stdout:
            print(f"   Output: {proc.stdout[:200]}")
    else:
        print("   ✓ Port 5000 is FREE")
except Exception as e:
    print(f"   ! Error checking port: {e}")

# 2. 检查 Python 环境
print("\n[2] CHECKING PYTHON ENVIRONMENT...")
print(f"   Python: {sys.executable}")
print(f"   Version: {sys.version}")

# 3. 检查 uvicorn 安装
print("\n[3] CHECKING UVICORN...")
try:
    import uvicorn
    print(f"   ✓ Uvicorn {uvicorn.__version__} installed")
except ImportError:
    print("   ✗ Uvicorn not installed")
    sys.exit(1)

# 4. 检查 app 导入
print("\n[4] CHECKING APP IMPORT...")
os.environ['SKIP_DB_INIT'] = '1'
try:
    from app import app
    print(f"   ✓ App imported: {len(app.routes)} routes")
except Exception as e:
    print(f"   ✗ Failed to import app: {e}")
    sys.exit(1)

# 5. 检查是否有后台 Python 进程
print("\n[5] CHECKING FOR BACKGROUND PYTHON PROCESSES...")
try:
    proc = subprocess.run(['tasklist', '/fi', 'imagename eq python.exe'], 
                         capture_output=True, text=True)
    lines = proc.stdout.strip().split('\n')[3:]  # 跳过标题
    print(f"   Found {len(lines)} Python processes:")
    for line in lines[:5]:  # 只显示前 5 个
        print(f"     {line[:70]}")
except Exception as e:
    print(f"   ! Error listing processes: {e}")

# 6. 检查 Ollama
print("\n[6] CHECKING OLLAMA...")
try:
    import httpx
    r = httpx.get('http://127.0.0.1:11434/api/tags', timeout=2)
    models = [m['name'] for m in r.json()['models']]
    print(f"   ✓ Ollama online: {models}")
except Exception as e:
    print(f"   ! Ollama not accessible: {e}")

print("\n" + "=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)
