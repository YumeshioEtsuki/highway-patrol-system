#!/usr/bin/env python3
import os
from pathlib import Path

REQUIRED_KEYS = [
    # 支持 DB_PASSWORD 或 DATABASE_PASSWORD 任一
    ("DB_PASSWORD", "DATABASE_PASSWORD"),
    "DEBUG",
]

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

def _load_env_file():
    if not ENV_PATH.exists():
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH)
    except Exception:
        # 简单解析 .env（KEY=VALUE）
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def main():
    _load_env_file()
    missing = []
    for key in REQUIRED_KEYS:
        if isinstance(key, tuple):
            # 任一键存在即可
            if not (os.getenv(key[0]) or os.getenv(key[1])):
                missing.append(f"{key[0]} 或 {key[1]}")
        else:
            if not os.getenv(key):
                missing.append(key)
    if missing:
        print("❌ 缺少以下必需配置项:")
        for k in missing:
            print(f"   - {k}")
        print("\n💡 请运行: python tooling/scripts/switch.py [dev|test|demo|prod]")
        raise SystemExit(1)
    print("✅ 配置校验通过")

if __name__ == "__main__":
    main()
