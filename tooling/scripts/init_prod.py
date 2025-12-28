#!/usr/bin/env python3
import os
import stat
from pathlib import Path

TOOLING_DIR = Path(__file__).resolve().parents[1]
ENV_DIR = TOOLING_DIR / "env"
PROD_ENV = ENV_DIR / "production.env"

REQUIRED_SECRETS = {
    "DATABASE_PASSWORD": os.getenv("PROD_DB_PASSWORD"),
    "REDIS_PASSWORD": os.getenv("PROD_REDIS_PASSWORD", ""),
    "DEBUG": "False",
    "SECURE_MODE": "1",
    "BOOTSTRAP_ADMIN": "0",
    "SKIP_DB_INIT": "1"
}

BASE_CONFIG = {
    "DATABASE_HOST": "localhost",
    "DATABASE_PORT": "3306",
    "DATABASE_USER": "road_patrol",
    "DATABASE_NAME": "road_patrol_db",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "REDIS_DB": "0",
    "UPLOAD_FOLDER": "photos",
    "JWT_ALGORITHM": "HS256",
    "JWT_EXPIRE_HOURS": "24",
}

def main():
    if not REQUIRED_SECRETS["DATABASE_PASSWORD"]:
        print("❌ 生产密钥未提供：PROD_DB_PASSWORD")
        raise SystemExit(1)
    # 合并配置
    lines = []
    for k, v in {**BASE_CONFIG, **REQUIRED_SECRETS}.items():
        lines.append(f"{k}={v}")
    PROD_ENV.write_text("\n".join(lines), encoding="utf-8")
    try:
        os.chmod(PROD_ENV, stat.S_IRUSR | stat.S_IWUSR)  # 600（Windows 可能不完全生效）
    except Exception:
        pass
    print(f"✅ 生产配置已生成: {PROD_ENV}（请确保仅限部署账户可读写）")

if __name__ == "__main__":
    main()
