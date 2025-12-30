#!/usr/bin/env python3
"""测试 Argon2 密码验证"""
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

ph = PasswordHasher()

# 测试哈希
pwd = "admin"
hashed = ph.hash(pwd)
print(f"哈希后的密码: {hashed}")
print(f"长度: {len(hashed)}")

# 测试验证
try:
    ph.verify(hashed, pwd)
    print("✓ 验证成功")
except VerifyMismatchError:
    print("✗ 密码不匹配")
except InvalidHashError:
    print("✗ 哈希格式无效")

# 现在测试数据库中的密码
db_hash = "c006f9377b165f40af44985ccadfaa4f:a672f7499c680dc6fa9e5ef2b7de0e1c2d65d10b8e17bcd54c30c7f2d9d6e2c1"
print(f"\n数据库密码: {db_hash}")
print(f"长度: {len(db_hash)}")

try:
    ph.verify(db_hash, pwd)
    print("✓ 验证成功")
except VerifyMismatchError:
    print("✗ 密码不匹配")
except InvalidHashError as e:
    print(f"✗ 哈希格式无效: {e}")
