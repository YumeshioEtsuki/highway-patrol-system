#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查和创建 AuditLog 表"""

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
        
        # 1. 检查表是否存在
        print("=" * 60)
        print("1️⃣ 检查 AuditLog 表是否存在...")
        cursor.execute("SHOW TABLES LIKE 'AuditLog'")
        result = cursor.fetchall()
        
        if result:
            print("✅ AuditLog 表已存在")
            
            # 查看表结构
            print("\n表结构:")
            cursor.execute("DESCRIBE AuditLog")
            for row in cursor.fetchall():
                print(f"  - {row}")
            
            # 查看记录数
            cursor.execute("SELECT COUNT(*) as cnt FROM AuditLog")
            count = cursor.fetchone()['cnt']
            print(f"\n当前记录数: {count} 条")
            
            if count > 0:
                # 显示最近5条
                print("\n最近5条记录:")
                cursor.execute("""
                    SELECT id, user_id, action, resource, resource_id, 
                           details, timestamp 
                    FROM AuditLog 
                    ORDER BY timestamp DESC 
                    LIMIT 5
                """)
                for row in cursor.fetchall():
                    print(f"  {row}")
        else:
            print("❌ AuditLog 表不存在，准备创建...")
            
            # 创建表
            create_sql = """
            CREATE TABLE AuditLog (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                action VARCHAR(50) NOT NULL COMMENT '操作类型（如：REVIEW, REJECT, EXPORT）',
                resource VARCHAR(100) NOT NULL COMMENT '资源类型（如：InspectionRecord）',
                resource_id INT COMMENT '资源ID',
                details TEXT COMMENT '操作详情',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES User(user_id),
                INDEX idx_user_id (user_id),
                INDEX idx_action (action),
                INDEX idx_timestamp (timestamp DESC),
                INDEX idx_action_time (action, timestamp DESC)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审计日志表'
            """
            
            cursor.execute(create_sql)
            conn.commit()
            print("✅ AuditLog 表创建成功！")
        
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
