#!/usr/bin/env python3
"""
执行 10_monitor_schema.sql 创建 performance_metrics 表
"""
import sys
from mysql.connector import connect

try:
    conn = connect(
        host="127.0.0.1",
        user="root",
        password="REDACTED",
        database="road_patrol_db"
    )
    cursor = conn.cursor()
    print("[*] 执行 10_monitor_schema.sql 创建监控表...")
    
    # 读取 SQL 文件
    with open("3-数据库\\10_monitor_schema.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()
    
    # 分割成单独的 SQL 语句并执行
    statements = [s.strip() for s in sql_content.split(";") if s.strip()]
    
    for i, statement in enumerate(statements):
        try:
            cursor.execute(statement)
            conn.commit()
            # 提取表名用于显示
            if "CREATE TABLE" in statement:
                table_match = statement.split("CREATE TABLE")[1].split("(")[0].strip()
                table_name = table_match.replace("IF NOT EXISTS", "").strip()
                print(f"  ✓ [{i+1}/{len(statements)}] 表创建成功: {table_name}")
            else:
                print(f"  ✓ [{i+1}/{len(statements)}] SQL 执行成功")
        except Exception as e:
            print(f"  ✗ [{i+1}/{len(statements)}] SQL 执行失败: {e}")
    
    # 验证 performance_metrics 表已创建
    cursor.execute("DESCRIBE performance_metrics")
    columns = cursor.fetchall()
    print(f"\n✓ performance_metrics 表已创建，包含 {len(columns)} 列:")
    for col in columns:
        print(f"  - {col[0]}: {col[1]}")
    
    cursor.close()
    conn.close()
    print("\n✓ 数据库初始化完成")
    
except Exception as e:
    print(f"✗ 初始化失败: {e}")
    sys.exit(1)
