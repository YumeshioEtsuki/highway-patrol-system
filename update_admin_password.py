#!/usr/bin/env python3
"""直接更新数据库中 admin 用户的密码为 MIMASHI123"""
import sys
import os
import bcrypt
import pymysql
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '1-后端代码'))

from dotenv import load_dotenv
load_dotenv('.env')

# 要设置的新密码
NEW_PASSWORD = os.getenv('DEFAULT_ADMIN_PASSWORD', 'MIMASHI123')

# 生成 bcrypt 哈希
password_hash = bcrypt.hashpw(NEW_PASSWORD.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

print("=" * 60)
print("更新 admin 密码")
print("=" * 60)
print(f"\n新密码: {NEW_PASSWORD}")
print(f"密码哈希: {password_hash}\n")

# 连接数据库
try:
    conn = pymysql.connect(
        host=os.getenv('DATABASE_HOST', 'localhost'),
        user=os.getenv('DATABASE_USER', 'root'),
        password=os.getenv('DATABASE_PASSWORD'),
        database=os.getenv('DATABASE_NAME', 'road_patrol_db'),
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    
    # 更新密码
    cursor.execute(
        "UPDATE User SET password = %s WHERE username = 'admin'",
        (password_hash,)
    )
    
    if cursor.rowcount > 0:
        conn.commit()
        print(f"✅ 成功更新 admin 用户密码")
        print(f"\n现在可以使用以下凭证登录:")
        print(f"   用户名: admin")
        print(f"   密码: {NEW_PASSWORD}")
    else:
        print("❌ admin 用户不存在")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ 错误: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
