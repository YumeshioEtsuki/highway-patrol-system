#!/usr/bin/env python3
"""一键修改所有env文件中SKIP_DB_INIT的值"""
import re
import os
from pathlib import Path

# 获取脚本位置，向上回溯到项目根目录
script_dir = Path(__file__).resolve().parent
ROOT = script_dir
TOOLING_ENV = ROOT / "tooling" / "env"
ENV_EXAMPLE = ROOT / ".env.example"
ENV_FILE = ROOT / ".env"

MAPPING = {
    "dev": "local.dev.env",
    "test": "local.test.env",
    "demo": "local.demo.env",
    "prod": "production.env"
}

print(f"📍 项目根目录: {ROOT}")
print(f"📍 tooling/env 目录: {TOOLING_ENV}")
print(f"📍 tooling/env 存在: {TOOLING_ENV.exists()}")
print()

def update_skip_db_init(file_path: Path, new_value: str):
    """更新SKIP_DB_INIT值"""
    if not file_path.exists():
        print(f"  ⚠️  文件不存在: {file_path}")
        return False
    
    try:
        content = file_path.read_text(encoding="utf-8")
        if "SKIP_DB_INIT=" not in content:
            print(f"  ⚠️  {file_path.name} 中未找到 SKIP_DB_INIT")
            return False
        
        new_content = re.sub(
            r"^SKIP_DB_INIT=.*$",
            f"SKIP_DB_INIT={new_value}",
            content,
            flags=re.MULTILINE
        )
        
        if new_content != content:
            file_path.write_text(new_content, encoding="utf-8")
            return True
        else:
            print(f"  ℹ️  {file_path.name} 已经是 SKIP_DB_INIT={new_value}")
    except Exception as e:
        print(f"  ❌ 更新失败 {file_path.name}: {e}")
    
    return False

print("=" * 60)
print("一键更新所有env文件的SKIP_DB_INIT=0")
print("=" * 60)
print()

updated_count = 0

# 更新 .env
if update_skip_db_init(ENV_FILE, "0"):
    print(f"✅ .env 已更新")
    updated_count += 1

# 更新 .env.example（留空，供用户填写）
if ENV_EXAMPLE.exists():
    content = ENV_EXAMPLE.read_text(encoding="utf-8")
    if "SKIP_DB_INIT=" in content:
        print(f"ℹ️  .env.example 中的SKIP_DB_INIT保持为空（用户配置）")

# 更新所有环境文件
for env_name, file_name in MAPPING.items():
    file_path = TOOLING_ENV / file_name
    print(f"  检查 {env_name:6} ({file_name:20}): {file_path}")
    if update_skip_db_init(file_path, "0"):
        print(f"✅ {env_name:6} 已更新")
        updated_count += 1

print()
print("=" * 60)
if updated_count > 0:
    print(f"✅ 成功更新 {updated_count} 个文件")
    print()
    print("现在所有env文件中的SKIP_DB_INIT都已设为0")
    print("下次启动时将自动初始化数据库")
else:
    print("❌ 没有文件被更新")
print("=" * 60)
