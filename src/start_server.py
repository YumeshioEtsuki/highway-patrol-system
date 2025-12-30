#!/usr/bin/env python3
"""
同名启动包装：转发到 src/bin/start_server.py，保持项目既有行为。
"""
import sys
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ENTRY = HERE / "bin" / "start_server.py"

if __name__ == "__main__":
    if not ENTRY.exists():
        print(f"❌ 未找到后端启动入口: {ENTRY}")
        raise SystemExit(1)
    code = subprocess.call([sys.executable, str(ENTRY)] + sys.argv[1:])
    raise SystemExit(code)
