#!/usr/bin/env python3
"""修复 .env 文件编码问题"""
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[2] / "src"
env_file = backend_dir / ".env"

if env_file.exists():
    # 尝试以 GBK 读取，然后以 UTF-8 写回
    try:
        with open(env_file, 'r', encoding='gbk', errors='replace') as f:
            content = f.read()
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {env_file} 已转换为 UTF-8 编码")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        sys.exit(1)
else:
    print(f"❌ 文件不存在: {env_file}")
    sys.exit(1)
