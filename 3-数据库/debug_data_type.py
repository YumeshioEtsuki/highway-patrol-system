#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试检查数据类型分布"""

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
        
        print("=" * 60)
        print("1️⃣ 检查 InspectionRecord 数据类型分布...")
        print("=" * 60)
        
        # 查看 data_type 字段定义
        cursor.execute("SHOW COLUMNS FROM InspectionRecord LIKE 'data_type'")
        col_info = cursor.fetchone()
        print(f"\ndata_type 字段定义: {col_info}")
        
        # 统计各类型记录数
        cursor.execute("""
            SELECT data_type, COUNT(*) as cnt 
            FROM InspectionRecord 
            GROUP BY data_type
        """)
        type_counts = cursor.fetchall()
        print("\n数据类型分布:")
        for row in type_counts:
            print(f"  {row['data_type']}: {row['cnt']} 条")
        
        # 查看最近的测试数据
        print("\n最近5条测试数据:")
        cursor.execute("""
            SELECT record_id, description, data_type, upload_time 
            FROM InspectionRecord 
            WHERE data_type = 'test'
            ORDER BY upload_time DESC 
            LIMIT 5
        """)
        test_records = cursor.fetchall()
        for row in test_records:
            print(f"  #{row['record_id']}: {row['description'][:30]}... [{row['data_type']}] {row['upload_time']}")
        
        # 查看最近的真实数据
        print("\n最近5条真实数据:")
        cursor.execute("""
            SELECT record_id, description, data_type, upload_time 
            FROM InspectionRecord 
            WHERE data_type = 'real'
            ORDER BY upload_time DESC 
            LIMIT 5
        """)
        real_records = cursor.fetchall()
        for row in real_records:
            print(f"  #{row['record_id']}: {row['description'][:30]}... [{row['data_type']}] {row['upload_time']}")
        
        # 测试筛选全部数据的SQL
        print("\n" + "=" * 60)
        print("2️⃣ 测试筛选全部数据的SQL...")
        print("=" * 60)
        
        # 不带 data_type 条件（应该返回全部）
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM InspectionRecord
        """)
        all_count = cursor.fetchone()['total']
        print(f"\n不带 data_type 条件: {all_count} 条")
        
        # 带 data_type='real' 条件
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM InspectionRecord 
            WHERE data_type = 'real'
        """)
        real_count = cursor.fetchone()['total']
        print(f"data_type='real': {real_count} 条")
        
        # 带 data_type='test' 条件
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM InspectionRecord 
            WHERE data_type = 'test'
        """)
        test_count = cursor.fetchone()['total']
        print(f"data_type='test': {test_count} 条")
        
        print(f"\n✅ 验证: {real_count} + {test_count} = {real_count + test_count} {'==' if all_count == real_count + test_count else '!='} {all_count}")
        print("=" * 60)
        
    except mysql.connector.Error as e:
        print(f"❌ MySQL 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    main()
