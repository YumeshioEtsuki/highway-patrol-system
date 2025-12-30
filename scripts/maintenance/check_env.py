#!/usr/bin/env python3
"""检查环境变量是否被正确加载"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "src"
sys.path.insert(0, str(BACKEND_DIR))

# 加载 .env
from dotenv import load_dotenv
load_dotenv(ROOT / '.env')

print("=" * 60)
print("环境变量加载检查")
print("=" * 60)

print(f"\n📍 当前目录: {os.getcwd()}")
print(f"📄 .env 文件: {Path('.env').resolve()}")
print(f"📄 .env 文件存在: {Path('.env').exists()}")

if Path('.env').exists():
    print(f"\n📋 .env 文件内容:")
    print("-" * 60)
    content = Path('.env').read_text(encoding='utf-8')
    for i, line in enumerate(content.split('\n'), 1):
        if line.strip() and not line.startswith('#'):
            if 'PASSWORD' in line.upper():
                # 隐藏密码
                parts = line.split('=', 1)
                print(f"{i:2d}: {parts[0]}=***")
            else:
                print(f"{i:2d}: {line}")
    print("-" * 60)

print(f"\n🔑 关键环境变量检查:")
print(f"   DEFAULT_ADMIN_PASSWORD: {os.getenv('DEFAULT_ADMIN_PASSWORD', '(未设置)')}")
print(f"   BOOTSTRAP_ADMIN: {os.getenv('BOOTSTRAP_ADMIN', '(未设置)')}")
print(f"   DATABASE_PASSWORD: {os.getenv('DATABASE_PASSWORD', '(未设置)')[:10]}***")
print(f"   DEBUG: {os.getenv('DEBUG', '(未设置)')}")
print(f"   SKIP_DB_INIT: {os.getenv('SKIP_DB_INIT', '(未设置)')}")

print("\n" + "=" * 60)
