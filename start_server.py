#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOLING_DIR = ROOT / "tooling"
ENV_DIR = TOOLING_DIR / "env"
TARGET_ENV = ROOT / ".env"
BACKEND_DIR = ROOT / "1-后端代码"

MAPPING = {
    "dev": "local.dev.env",
    "test": "local.test.env",
    "demo": "local.demo.env",
    "prod": "production.env",
}


def load_env():
    # 优先 dotenv；否则手动解析
    if TARGET_ENV.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(TARGET_ENV)
        except Exception:
            for line in TARGET_ENV.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def switch_environment(env_name: str):
    src = ENV_DIR / MAPPING[env_name]
    if not src.exists():
        print(f"ERROR: Config file not found: {src}")
        raise SystemExit(1)
    if env_name == "prod" and os.getenv("ALLOW_PROD_SWITCH") != "true":
        print("WARNING: Production environment requires auth! Set ALLOW_PROD_SWITCH=true")
        raise SystemExit(1)
    TARGET_ENV.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"[OK] Environment switched: {env_name} -> .env")


def validate_config():
    load_env()
    # 支持 DB_PASSWORD 或 DATABASE_PASSWORD
    if not (os.getenv("DB_PASSWORD") or os.getenv("DATABASE_PASSWORD")):
        print("ERROR: Missing database password (DB_PASSWORD or DATABASE_PASSWORD)")
        raise SystemExit(1)
    if os.getenv("SECURE_MODE") == "1" and os.getenv("BOOTSTRAP_ADMIN") == "1":
        print("WARNING: BOOTSTRAP_ADMIN will be ignored when SECURE_MODE=1, set to 0")
    print("[OK] Config validation passed")


def start_server(env_name: str):
    import subprocess
    os.chdir(BACKEND_DIR)
    backend_entry = BACKEND_DIR / "bin" / "start_server.py"
    if not backend_entry.exists():
        print(f"ERROR: Backend startup script not found: {backend_entry}")
        raise SystemExit(1)
    print("[STEP] Invoking backend startup script: bin/start_server.py")
    try:
        code = subprocess.call([sys.executable, str(backend_entry)])
        if code != 0:
            raise SystemExit(code)
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped (Ctrl+C)")
        raise SystemExit(0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True, choices=MAPPING.keys(), help="环境 (dev/test/demo/prod)")
    args = parser.parse_args()
    switch_environment(args.env)
    validate_config()
    start_server(args.env)

if __name__ == "__main__":
    main()
