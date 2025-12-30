#!/usr/bin/env python3
"""检查数据库初始化状态"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "src"
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from utils.utils import get_db_connection

print("[INFO] Checking database status...\n")

try:
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 检查 User 表
    try:
        cur.execute("SELECT COUNT(*) FROM User")
        count = cur.fetchone()[0]
        print(f"[OK] User table exists, {count} users found")
        
        # 查看是否存在 admin
        cur.execute("SELECT id, username, role FROM User WHERE username='admin'")
        admin = cur.fetchone()
        if admin:
            print(f"[OK] Admin user exists: id={admin[0]}, username={admin[1]}, role={admin[2]}")
        else:
            print("[WARN] Admin user NOT found - login will fail!")
            print("[TIP] Run 'python bin/create_admin.py' to create admin account")
    except Exception as e:
        print(f"[ERROR] User table missing: {e}")
        print("[TIP] Database not initialized. Run without SKIP_DB_INIT=1 or run 'python bin/create_admin.py' after creating tables")
    
    # 检查其他关键表
    for table in ['Patrol', 'Photo', 'Inspector', 'AuditLog']:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"[OK] {table} table exists, {count} records")
        except:
            print(f"[WARN] {table} table missing")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"[ERROR] Database connection failed: {e}")
    print("[TIP] Check DATABASE_PASSWORD in .env and MySQL service status")
