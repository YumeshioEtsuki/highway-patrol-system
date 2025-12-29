#!/usr/bin/env python3
"""检查admin用户的密码"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '1-后端代码'))

from dotenv import load_dotenv
load_dotenv('.env')

import pymysql
import bcrypt

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='MIMASHI123',
    database='road_patrol_db',
    charset='utf8mb4'
)

cursor = conn.cursor()
cursor.execute("SELECT username, password FROM User WHERE username='admin'")
result = cursor.fetchone()

if result:
    username, stored_hash = result
    print(f"数据库中的admin信息：")
    print(f"  用户名: {username}")
    print(f"  密码哈希: {stored_hash[:60]}...")
    print(f"\n环境变量 DEFAULT_ADMIN_PASSWORD: {os.getenv('DEFAULT_ADMIN_PASSWORD')}")
    
    # 测试密码验证
    test_passwords = ['MIMASHI123', 'admin']
    print(f"\n密码验证测试：")
    for pwd in test_passwords:
        result = bcrypt.checkpw(pwd.encode('utf-8'), stored_hash.encode('utf-8'))
        print(f"  '{pwd}' -> {'✅ 匹配' if result else '❌ 不匹配'}")
else:
    print("❌ 数据库中没有找到admin用户！")

cursor.close()
conn.close()
