#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '1-后端代码')

print("=== 数据库检查 ===")
from utils.utils import get_db_connection
conn = get_db_connection()
cur = conn.cursor(dictionary=True)

# 1. 检查记录数
cur.execute('SELECT COUNT(*) as cnt FROM InspectionRecord')
count = cur.fetchone()['cnt']
print(f"巡查记录总数: {count}")

if count > 0:
    cur.execute('SELECT record_id, status, description FROM InspectionRecord LIMIT 3')
    for row in cur.fetchall():
        print(f"  - ID={row['record_id']}, 状态={row['status']}, 描述={row['description'][:30]}")

cur.close()
conn.close()

print("\n=== 测试导出功能 ===")
from models.tasks import export_patrol_records_to_excel
try:
    excel_bytes = export_patrol_records_to_excel(filters=None)
    print(f"✅ 导出成功！大小: {len(excel_bytes)} bytes")
except Exception as e:
    print(f"❌ 导出失败: {e}")
    import traceback
    traceback.print_exc()
