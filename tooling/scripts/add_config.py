#!/usr/bin/env python3
"""
向指定的环境模板中添加新的配置项（包括.env.example）。

用法:
  1. 直接调用:
     python add_config.py KEY "value" --envs dev,test,demo
  
  2. 通过管理工具（推荐）:
     python manage_env.py
"""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent.parent  # 项目根目录
TOOLING_ENV = ROOT / "tooling" / "env"
ENV_EXAMPLE = ROOT / ".env.example"

MAPPING = {
    "dev": "local.dev.env",
    "test": "local.test.env",
    "demo": "local.demo.env",
    "prod": "production.env"
}

def add_config_to_file(file_path: Path, key: str, value: str, comment: str = None):
    """向指定文件添加配置项"""
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    try:
        content = file_path.read_text(encoding="utf-8")
        # 检查是否已存在
        if f"{key}=" in content:
            print(f"⚠️  {file_path.name} 中已存在 {key}，已跳过")
            return False
        
        # 添加配置
        new_lines = []
        if comment:
            new_lines.append(f"\n# {comment}")
        new_lines.append(f"{key}={value}")
        
        file_path.write_text(content + "\n" + "\n".join(new_lines) + "\n", encoding="utf-8")
        return True
    except Exception as e:
        print(f"❌ 写入失败 {file_path.name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="管理环境变量配置")
    parser.add_argument("key", help="配置键名")
    parser.add_argument("value", help="配置值")
    parser.add_argument("--envs", required=True, help="要更新的环境列表，如: dev,test,demo,prod")
    parser.add_argument("--comment", help="配置注释（可选）")
    parser.add_argument("--skip-example", action="store_true", help="跳过修改.env.example")
    args = parser.parse_args()

    updated_count = 0
    
    # 更新 .env.example（除非指定--skip-example）
    if not args.skip_example and ENV_EXAMPLE.exists():
        if add_config_to_file(ENV_EXAMPLE, args.key, "", args.comment or f"开发环境: {args.key}"):
            print(f"✅ .env.example 已更新")
            updated_count += 1
        else:
            print(f"⚠️  .env.example 未更新或已存在该键")
    
    # 更新对应环境的配置文件
    envs = [e.strip() for e in args.envs.split(",")]
    for env in envs:
        if env not in MAPPING:
            print(f"❌ 未知环境 '{env}'")
            continue
        
        file_path = TOOLING_ENV / MAPPING[env]
        if add_config_to_file(file_path, args.key, args.value, args.comment):
            print(f"✅ {env:6} ({MAPPING[env]:20}) - {args.key} = {args.value}")
            updated_count += 1
        else:
            print(f"⚠️  {env:6} ({MAPPING[env]:20}) - 未更新或已存在")
    
    if updated_count == 0:
        print("\n❌ 没有文件被更新")
        sys.exit(1)
    else:
        print(f"\n✅ 共更新 {updated_count} 个文件")

if __name__ == "__main__":
    main()