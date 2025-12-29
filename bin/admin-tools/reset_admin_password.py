#!/usr/bin/env python3
"""
重置管理员(admin)密码（安全交互式）
- 需要数据库可连接
- 使用 Argon2（优先）或 bcrypt 进行哈希
"""
import os
import sys
import getpass

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '1-后端代码'))
from utils.utils import get_db_connection, hash_password


def main():
    print("\n=== 重置管理员密码 ===")
    username = 'admin'
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM User WHERE username=%s", (username,))
        if cur.fetchone()[0] == 0:
            print("未找到 admin 账号，请先运行 bin/create_admin.py 创建。")
            return
        pwd = getpass.getpass("请输入新密码（不会回显）：")
        if not pwd or len(pwd) < 8 or (pwd.isdigit() or pwd.isalpha()):
            print("密码至少8位且需包含字母和数字，重置取消。")
            return
        hashed = hash_password(pwd)
        cur.execute("UPDATE User SET password=%s WHERE username=%s", (hashed, username))
        conn.commit()
        print("✅ 管理员密码已重置")
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    main()
