#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""速度测试脚本"""
import sys
import time
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '1-后端代码'))

from utils.config import db_config
import mysql.connector

print("=" * 60)
print("MySQL 连接速度测试")
print("=" * 60)

# 测试1: 连接速度
print("\n[测试1] 测试数据库连接速度...")
start = time.time()
try:
    conn = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        connect_timeout=3
    )
    elapsed = (time.time() - start) * 1000
    print(f"✅ 连接成功！耗时: {elapsed:.0f} ms")
    
    # 测试2: 简单查询速度
    print("\n[测试2] 测试简单查询速度...")
    cur = conn.cursor()
    start = time.time()
    cur.execute("SELECT 1")
    cur.fetchone()
    elapsed = (time.time() - start) * 1000
    print(f"✅ 查询成功！耗时: {elapsed:.0f} ms")
    
    # 测试3: 表查询速度
    print("\n[测试3] 测试表查询速度...")
    start = time.time()
    cur.execute("SELECT COUNT(*) FROM InspectionRecord")
    count = cur.fetchone()[0]
    elapsed = (time.time() - start) * 1000
    print(f"✅ 表查询成功！记录数: {count}, 耗时: {elapsed:.0f} ms")
    
    # 测试4: 复杂JOIN查询
    print("\n[测试4] 测试复杂查询速度（模拟管理员列表）...")
    start = time.time()
    cur.execute("""
        SELECT ir.record_id, ir.status, u.real_name, rs.segment_name
        FROM InspectionRecord ir
        LEFT JOIN User u ON ir.user_id = u.user_id
        LEFT JOIN RoadSegment rs ON ir.segment_id = rs.segment_id
        LIMIT 10
    """)
    rows = cur.fetchall()
    elapsed = (time.time() - start) * 1000
    print(f"✅ 复杂查询成功！返回 {len(rows)} 行, 耗时: {elapsed:.0f} ms")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("诊断结果:")
    print("=" * 60)
    if elapsed < 100:
        print("✅ 数据库性能正常")
    elif elapsed < 500:
        print("⚠️  数据库响应较慢，但可用")
    else:
        print("❌ 数据库响应非常慢！建议检查:")
        print("   1. MySQL 配置是否合理")
        print("   2. 是否在远程服务器（网络延迟）")
        print("   3. 磁盘 I/O 是否正常")
        
except mysql.connector.Error as e:
    elapsed = (time.time() - start) * 1000
    print(f"❌ 连接失败！耗时: {elapsed:.0f} ms")
    print(f"错误: {e}")
    print("\n可能原因:")
    print("  1. MySQL 服务未启动")
    print("  2. 连接配置错误（用户名/密码/数据库名）")
    print("  3. 防火墙阻止连接")
except Exception as e:
    print(f"❌ 未知错误: {e}")
