#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试审计日志和数据类型筛选"""

import mysql.connector
import sys

# 数据库连接配置
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'REDACTED',
    'database': 'road_patrol_db',
    'charset': 'utf8mb4'
}

def main():
    conn = None
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        
        print("=" * 70)
        print("1️⃣ 检查 AuditLog 表")
        print("=" * 70)
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'AuditLog'")
        if not cursor.fetchone():
            print("❌ AuditLog 表不存在！")
            return
        
        print("✅ AuditLog 表存在")
        
        # 查看记录数
        cursor.execute("SELECT COUNT(*) as cnt FROM AuditLog")
        audit_count = cursor.fetchone()['cnt']
        print(f"📊 审计日志记录数: {audit_count} 条")
        
        if audit_count > 0:
            # 显示最近5条
            print("\n最近5条审计记录:")
            cursor.execute("""
                SELECT id, user_id, action, resource, 
                       LEFT(details, 50) as details_short, timestamp 
                FROM AuditLog 
                ORDER BY timestamp DESC 
                LIMIT 5
            """)
            for row in cursor.fetchall():
                print(f"  #{row['id']} [{row['timestamp']}] {row['action']}: {row['details_short']}...")
        
        print("\n" + "=" * 70)
        print("2️⃣ 检查 InspectionRecord 数据类型分布")
        print("=" * 70)
        
        # 查看 data_type 字段
        cursor.execute("SHOW COLUMNS FROM InspectionRecord LIKE 'data_type'")
        col = cursor.fetchone()
        print(f"✅ data_type 字段定义: {col['Type']}")
        
        # 统计各类型记录数
        cursor.execute("""
            SELECT data_type, COUNT(*) as cnt 
            FROM InspectionRecord 
            GROUP BY data_type
        """)
        print("\n数据类型分布:")
        type_dist = cursor.fetchall()
        for row in type_dist:
            print(f"  {row['data_type']}: {row['cnt']} 条")
        
        # 测试不带 data_type 筛选的查询
        cursor.execute("SELECT COUNT(*) as total FROM InspectionRecord")
        total = cursor.fetchone()['total']
        print(f"\n不带 data_type 筛选（全部数据）: {total} 条")
        
        # 测试带 data_type='real' 筛选
        cursor.execute("SELECT COUNT(*) as total FROM InspectionRecord WHERE data_type='real'")
        real = cursor.fetchone()['total']
        print(f"data_type='real': {real} 条")
        
        # 测试带 data_type='test' 筛选
        cursor.execute("SELECT COUNT(*) as total FROM InspectionRecord WHERE data_type='test'")
        test = cursor.fetchone()['total']
        print(f"data_type='test': {test} 条")
        
        print(f"\n验证: {real} + {test} = {real + test} {'==' if total == real + test else '!='} {total}")
        
        print("\n" + "=" * 70)
        print("3️⃣ 测试审计日志 API 查询")
        print("=" * 70)
        
        # 模拟 API 查询（不带筛选）
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM AuditLog
            WHERE 1=1
        """)
        api_total = cursor.fetchone()['total']
        print(f"API 模拟查询（无筛选）: {api_total} 条")
        
        # 查询最近10条
        cursor.execute("""
            SELECT id, user_id, action, resource, details, timestamp
            FROM AuditLog
            WHERE 1=1
            ORDER BY timestamp DESC
            LIMIT 10 OFFSET 0
        """)
        api_records = cursor.fetchall()
        print(f"API 分页查询（前10条）: 返回 {len(api_records)} 条记录")
        
        if api_records:
            print("\n前3条记录详情:")
            for row in api_records[:3]:
                print(f"  #{row['id']}: {row['action']} - {row['resource']}")
                print(f"    详情: {row['details'][:80]}...")
                print(f"    时间: {row['timestamp']}")
        
        print("\n" + "=" * 70)
        print("✅ 所有测试完成！")
        print("=" * 70)
        
    except mysql.connector.Error as e:
        print(f"❌ MySQL 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    main()
