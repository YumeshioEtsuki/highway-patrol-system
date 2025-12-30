#!/usr/bin/env python3
"""完整启动测试"""
import subprocess
import sys
import time

print("=" * 60)
print("Starting Highway Patrol System (dev environment)")
print("=" * 60)

proc = subprocess.Popen(
    [sys.executable, "start_server.py", "--env", "dev"],
    cwd="D:\\MySQL Project\\highway-patrol-system",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# 读取前 30 秒的输出
start_time = time.time()
line_count = 0
while time.time() - start_time < 30 and line_count < 100:
    try:
        line = proc.stdout.readline()
        if line:
            print(line.rstrip())
            line_count += 1
        else:
            break
    except KeyboardInterrupt:
        break

# 发送 Ctrl+C 停止
proc.terminate()
try:
    proc.wait(timeout=5)
except subprocess.TimeoutExpired:
    proc.kill()

print("\n" + "=" * 60)
print("Server startup test complete")
print("=" * 60)
