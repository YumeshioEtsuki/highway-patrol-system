#!/usr/bin/env python3
"""
安全创建管理员账号（一次性运维脚本）
- 仅在缺少 admin 时插入
- 交互式输入强口令（不回显）
- 使用 Argon2（优先）或 bcrypt 进行哈希
"""
import os
import sys
import getpass

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '1-后端代码'))
from utils.utils import get_db_connection, hash_password


def main():
    print("\n=== 创建管理员账号 ===")
    username = 'admin'
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM User WHERE username=%s", (username,))
        if cur.fetchone()[0] > 0:
            print("已存在 admin 账号，无需创建。")
            return
        pwd = getpass.getpass("请输入管理员密码（不会回显）：")
        if not pwd or len(pwd) < 8 or (pwd.isdigit() or pwd.isalpha()):
            print("密码至少8位且需包含字母和数字，创建取消。")
            return
        hashed = hash_password(pwd)
        cur.execute(
            """
            INSERT INTO User (username, password, real_name, phone, email, role, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            (username, hashed, '系统管理员', '11451419198', 'admin@example.com', 'admin')
        )
        conn.commit()
        print("✅ 管理员创建成功")
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    main()
