#!/usr/bin/env python3
"""诊断后端数据问题"""
import sys
import os

# 添加后端代码目录到 Python 路径
backend_path = os.path.join(os.path.dirname(__file__), '..', '1-后端代码')
backend_path = os.path.abspath(backend_path)
sys.path.insert(0, backend_path)

from utils.config import settings
from utils.utils import get_db_connection
from models.tasks import get_admin_stats

try:
    # 测试数据库连接
    print("=" * 60)
    print("1. 测试数据库连接...")
    print("=" * 60)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    print(f"✓ 数据库连接成功")
    cursor.close()
    conn.close()
    
    # 测试获取统计数据
    print("\n" + "=" * 60)
    print("2. 测试 get_admin_stats()...")
    print("=" * 60)
    stats = get_admin_stats(
        start_date=None,
        end_date=None,
        data_type='all'
    )
    print(f"✓ 统计数据获取成功")
    print(f"\n返回的数据:")
    print(f"  - total_records: {stats.get('total_records')}")
    print(f"  - status_breakdown: {stats.get('status_breakdown')}")
    print(f"  - type_breakdown 数量: {len(stats.get('type_breakdown', []))}")
    
    type_breakdown = stats.get('type_breakdown', [])
    if type_breakdown:
        print(f"\n type_breakdown 详情 (前5项):")
        for item in type_breakdown[:5]:
            print(f"    - {item}")
    else:
        print(f"\n ❌ type_breakdown 为空!")
    
    print(f"\n  - severity_breakdown 数量: {len(stats.get('severity_breakdown', []))}")
    
    severity_breakdown = stats.get('severity_breakdown', [])
    if severity_breakdown:
        print(f"\n severity_breakdown 详情:")
        for item in severity_breakdown:
            print(f"    - {item}")
    else:
        print(f"\n ⚠️ severity_breakdown 为空")
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
