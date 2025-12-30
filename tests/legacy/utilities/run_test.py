#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launch server and test admin auth flow
"""
import subprocess
import time
import requests
import sys
import os

# Set Python encoding to UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Start server (skip db init to avoid duplicate seed errors during repeated runs)
print("[START] Launching FastAPI server...")
env = os.environ.copy()
env["SKIP_DB_INIT"] = "1"
use_reload = env.get("USE_RELOAD", "0") == "1"
cmd = [
    "python", "-m", "uvicorn",
    "app:app",
    "--host", "127.0.0.1",
    "--port", "5000"
]
if use_reload:
    cmd.insert(4, "--reload")  # insert after module path for clarity
    print("[INFO] Using --reload (slower, for live code changes)")
else:
    print("[INFO] Fast mode: reload disabled")

server_proc = subprocess.Popen(
    cmd,
    cwd=r"d:\MySQL Project\highway-patrol-system\1-后端代码",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    env=env
)

# Wait for server via /health polling (faster than fixed sleep)
BASE_URL = "http://127.0.0.1:5000"
health_url = f"{BASE_URL}/health"
print("[WAIT] Waiting for server health...")
health_ok = False
for attempt in range(12):  # up to ~6s total (0.5s interval)
    time.sleep(0.5)
    try:
        res = requests.get(health_url, timeout=2)
        if res.status_code == 200:
            elapsed = (attempt + 1) * 0.5
            print(f"[OK] Health ready in {elapsed:.1f}s")
            health_ok = True
            break
    except Exception:
        pass

if not health_ok:
    print("[WARN] Health endpoint not ready after 6s; proceeding with tests")

# Test
try:
    # Keep test target aligned with the uvicorn port above
    BASE_URL = "http://127.0.0.1:5000"
    TIMEOUT = (5, 5)
    
    # Ping
    print("\n[TEST] Testing connection...")
    ping_res = requests.get(f"{BASE_URL}/docs", timeout=TIMEOUT)
    if ping_res.status_code == 200:
        print("[OK] Server started!")
    else:
        print(f"[WARN] Server returned status {ping_res.status_code}")
    
    # Step 1: Login
    print("\n[STEP1] Login with admin account...")
    login_res = requests.post(
        f"{BASE_URL}/api/login",
        json={"username": "admin", "password": "REDACTED"},
        timeout=TIMEOUT
    )
    print(f"  Status: {login_res.status_code}")
    
    if login_res.status_code == 200:
        data = login_res.json()
        token = data.get("access_token")
        if token:
            print(f"  [OK] Got token")
            
            # Step 2: Test SSE
            print("\n[STEP2] Test /api/verify/stream?token=...")
            stream_url = f"{BASE_URL}/api/verify/stream?token={token}"
            
            try:
                stream_res = requests.get(stream_url, stream=True, timeout=(5, 5))
                print(f"  Status: {stream_res.status_code}")
                
                if stream_res.status_code == 200:
                    print(f"  [OK] SSE connection successful!")
                    print(f"  Content-Type: {stream_res.headers.get('content-type')}")
                    
                    # Read first few lines
                    start_time = time.time()
                    for i, line in enumerate(stream_res.iter_lines(decode_unicode=True)):
                        if time.time() - start_time > 5:
                            print("    [WARN] SSE no data within 5s, stopping read")
                            break
                        if i < 3 and line.strip():
                            print(f"    {line[:70]}")
                        if i >= 2:
                            break
                    
                    stream_res.close()
                else:
                    print(f"  [ERROR] Status {stream_res.status_code}")
                    print(f"     {stream_res.text[:200]}")
                    
            except Exception as e:
                print(f"  [WARN] {type(e).__name__}: {str(e)[:100]}")
            
            # Step 3: Test list endpoint
            print("\n[STEP3] Test /api/admin/patrol/list...")
            list_res = requests.get(
                f"{BASE_URL}/api/admin/patrol/list",
                headers={"Authorization": f"Bearer {token}"},
                timeout=TIMEOUT
            )
            print(f"  Status: {list_res.status_code}")
            
            if list_res.status_code == 200:
                try:
                    records = list_res.json()
                    print(f"  [OK] Got {len(records)} records")
                except:
                    print(f"  [WARN] Cannot parse JSON")
            else:
                print(f"  [ERROR] {list_res.text[:200]}")
        else:
            print(f"  [ERROR] No token: {data}")
    else:
        print(f"  [ERROR] Login failed: {login_res.text[:200]}")

except Exception as e:
    print(f"\n[ERROR] Test failed: {type(e).__name__}: {e}")

finally:
    # Kill server
    print("\n[STOP] Shutting down server...")
    server_proc.terminate()
    try:
        server_proc.wait(timeout=5)
    except:
        server_proc.kill()
    print("[OK] Server closed")

