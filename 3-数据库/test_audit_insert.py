#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试审计日志插入"""

import mysql.connector
from datetime import datetime

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
        print("测试插入审计日志...")
        print("=" * 60)
        
        # 插入一条测试记录
        cursor.execute("""
            INSERT INTO AuditLog 
            (user_id, action, resource, resource_id, details) 
            VALUES (%s, %s, %s, %s, %s)
        """, (1, 'TEST', 'System', None, '测试审计日志功能'))
        
        conn.commit()
        print("✅ 插入成功")
        
        # 查询最新记录
        cursor.execute("""
            SELECT id, user_id, action, resource, resource_id, details, timestamp 
            FROM AuditLog 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        
        print("\n最近5条审计记录:")
        for row in cursor.fetchall():
            print(f"  {row}")
        
        print("=" * 60)
        
    except mysql.connector.Error as e:
        print(f"❌ MySQL 错误: {e}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    main()
