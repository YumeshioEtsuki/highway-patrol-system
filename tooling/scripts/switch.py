#!/usr/bin/env python3
import os
import sys
import shutil
from pathlib import Path

TOOLING_DIR = Path(__file__).resolve().parents[1]
ENV_DIR = TOOLING_DIR / "env"
TARGET_ENV = Path(TOOLING_DIR.parent, ".env")
MAPPING = {
    "dev": "local.dev.env",
    "test": "local.test.env",
    "demo": "local.demo.env",
    "prod": "production.env",
}

def main():
    if len(sys.argv) != 2:
        print("❌ 用法: python tooling/scripts/switch.py [dev|test|demo|prod]")
        sys.exit(1)
    env_name = sys.argv[1]
    if env_name not in MAPPING:
        print(f"❌ 无效环境: {env_name}")
        sys.exit(1)
    source_file = ENV_DIR / MAPPING[env_name]
    if not source_file.exists():
        print(f"❌ 配置文件不存在: {source_file}")
        sys.exit(1)
    if env_name == "prod" and os.getenv("ALLOW_PROD_SWITCH") != "true":
        print("⚠️  生产环境需授权! 请设置 ALLOW_PROD_SWITCH=true")
        sys.exit(1)
    shutil.copy(source_file, TARGET_ENV)
    print(f"✅ 已切换到 '{env_name}' 配置 -> {TARGET_ENV}")

if __name__ == "__main__":
    main()
