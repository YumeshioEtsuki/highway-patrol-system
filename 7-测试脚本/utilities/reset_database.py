#!/usr/bin/env python3
"""
快速重置数据库脚本（无需打开管理页面）

用法：
  - 仅建表（清空并重建表结构，不插入测试数据）
      python reset_db.py --step 1
  - 完整重置（建表 + 插入测试数据 + 简单校验）
      python reset_db.py --step all

备注：会读取项目根目录 .env 中的数据库连接配置
"""
import sys
import argparse
from pathlib import Path

# 加载 .env
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        print(f"[OK] Loaded .env from {env_path}")
    except Exception as e:
        print(f"[WARN] Failed to load .env: {e}")

# 执行重置
from utils.utils import reinit_database


def main():
    parser = argparse.ArgumentParser(description='Reset database quickly.')
    parser.add_argument('--step', default='all', choices=['1', 'all'], help='1=仅建表, all=建表+测试数据')
    args = parser.parse_args()

    step = 1 if args.step == '1' else 'all'
    print("\n" + "=" * 60)
    print(f"🚧 正在执行数据库重置，步骤: {args.step}")
    print("=" * 60)

    try:
        result = reinit_database(step=step, skip_read_only_queries=True)
        print("\n[RESULT]", result.get('message'))
        print("详情:")
        for s in result.get('steps', []):
            ok = '✅' if s.get('success') else '❌'
            print(f"  {ok} {s.get('name')} ({s.get('duration','-')}ms)")
        print(f"耗时: {result.get('execution_time', 0)} ms\n")
        if result.get('status') != 'success':
            sys.exit(1)
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
