#!/usr/bin/env python3
"""查看 admin 用户的密码"""
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='REDACTED',
    database='road_patrol_db'
)
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT user_id, username, password FROM User LIMIT 5")
for row in cursor.fetchall():
    print(f"ID: {row['user_id']}, Username: {row['username']}")
    pwd = row['password']
    print(f"  Password length: {len(pwd)}")
    print(f"  Password first 50 chars: {pwd[:50]}")
    print()
cursor.close()
conn.close()
