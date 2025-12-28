#!/usr/bin/env python3
"""
向指定的环境模板中添加新的配置项。
用法: python add_config.py NEW_KEY "default_value" --envs dev,test,demo
"""
import argparse
from pathlib import Path

TOOLING_ENV = Path("tooling/env")
MAPPING = {
    "dev": "local.dev.env",
    "test": "local.test.env",
    "demo": "local.demo.env",
    "prod": "production.env"
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("key", help="配置键名")
    parser.add_argument("value", help="配置值")
    parser.add_argument("--envs", required=True, help="要更新的环境列表，如: dev,test,demo")
    args = parser.parse_args()

    envs = args.envs.split(",")
    for env in envs:
        if env not in MAPPING:
            print(f"警告: 未知环境 '{env}'，已跳过。")
            continue
        
        file_path = TOOLING_ENV / MAPPING[env]
        with open(file_path, "a") as f:
            f.write(f"\n{args.key}={args.value}\n")
        print(f"✅ 已向 {env} ({file_path}) 添加 {args.key}")

if __name__ == "__main__":
    main()