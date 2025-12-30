#!/usr/bin/env python3
"""
快速调试脚本：检查数据库状态和后端接口
"""
import sys
import json

# 连接数据库
try:
    from mysql.connector import connect
    print("[1] 连接数据库...")
    conn = connect(
        host="127.0.0.1",
        user="root",
        password="REDACTED",
        database="road_patrol_db"
    )
    cursor = conn.cursor(dictionary=True)
    print("✓ 数据库连接成功\n")
except Exception as e:
    print(f"✗ 数据库连接失败: {e}")
    sys.exit(1)

# ==================== 第1层：数据库检查 ====================
print("=" * 60)
print("第1层：数据库检查")
print("=" * 60)

# 1.1 检查 Photo 表
print("\n[1.1] Photo 表数据统计")
cursor.execute("SELECT COUNT(*) as count FROM Photo")
photo_count = cursor.fetchone()['count']
print(f"  总照片数: {photo_count}")

if photo_count > 0:
    print("\n  照片详情（前5条）:")
    cursor.execute("SELECT photo_id, file_name, record_id, upload_time FROM Photo LIMIT 5")
    photos = cursor.fetchall()
    for p in photos:
        print(f"    - photo_id={p['photo_id']}, file_name={p['file_name']}, record_id={p['record_id']}")
else:
    print("  ⚠️  Photo 表为空")

# 1.2 检查 InspectionRecord 表
print("\n[1.2] InspectionRecord 表数据统计")
cursor.execute("SELECT COUNT(*) as count FROM InspectionRecord")
record_count = cursor.fetchone()['count']
print(f"  总记录数: {record_count}")

if record_count > 0:
    print("\n  记录详情（前3条）:")
    cursor.execute("SELECT record_id, user_id, upload_time FROM InspectionRecord LIMIT 3")
    records = cursor.fetchall()
    for r in records:
        print(f"    - record_id={r['record_id']}, user_id={r['user_id']}, upload_time={r['upload_time']}")

# 1.3 检查关联关系
print("\n[1.3] Photo 与 InspectionRecord 关联检查")
cursor.execute("""
    SELECT p.photo_id, p.file_name, ir.record_id, ir.user_id 
    FROM Photo p
    LEFT JOIN InspectionRecord ir ON p.record_id = ir.record_id
    LIMIT 5
""")
relations = cursor.fetchall()
if relations:
    print("  关联详情（前5条）:")
    for rel in relations:
        user_id = rel['user_id'] if rel['user_id'] else "NULL"
        print(f"    - photo_id={rel['photo_id']}, file_name={rel['file_name']}, user_id={user_id}")
else:
    print("  ⚠️  无关联数据")

# 1.4 检查 performance_metrics 表
print("\n[1.4] performance_metrics 表检查")
try:
    cursor.execute("SELECT COUNT(*) as count FROM performance_metrics")
    metrics_count = cursor.fetchone()['count']
    print(f"  总监控记录数: {metrics_count}")
    
    if metrics_count > 0:
        cursor.execute("SELECT * FROM performance_metrics ORDER BY timestamp DESC LIMIT 1")
        latest = cursor.fetchone()
        print(f"\n  最新记录:")
        for key, val in latest.items():
            print(f"    - {key}: {val}")
    else:
        print("  ⚠️  performance_metrics 表为空（但可由后端实时采集）")
        
except Exception as e:
    print(f"  ⚠️  表不存在或查询失败: {e}")

# 1.5 检查 User 表（用于认证）
print("\n[1.5] User 表检查（用于照片接口认证）")
cursor.execute("SELECT COUNT(*) as count FROM User")
user_count = cursor.fetchone()['count']
print(f"  总用户数: {user_count}")

if user_count > 0:
    cursor.execute("SELECT user_id, username, role FROM User LIMIT 3")
    users = cursor.fetchall()
    print("\n  用户详情（前3条）:")
    for u in users:
        print(f"    - user_id={u['user_id']}, username={u['username']}, role={u['role']}")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("数据库检查完成")
print("=" * 60)

# ==================== 诊断建议 ====================
print("\n[诊断建议]")
if photo_count == 0:
    print("❌ ISSUE 1: Photo 表无数据")
    print("   → 可能原因：尚未上传照片")
    print("   → 解决：需要通过 patrol.html 或数据导入生成测试数据")
else:
    print(f"✓ Photo 表有 {photo_count} 条记录")

if record_count == 0:
    print("❌ ISSUE 2: InspectionRecord 表无数据")
    print("   → 可能原因：尚未生成巡查记录")
    print("   → 解决：需要生成测试数据")
else:
    print(f"✓ InspectionRecord 表有 {record_count} 条记录")

if user_count == 0:
    print("❌ ISSUE 3: User 表无数据")
    print("   → 这是严重问题，后端无法识别用户")
else:
    print(f"✓ User 表有 {user_count} 条记录")
