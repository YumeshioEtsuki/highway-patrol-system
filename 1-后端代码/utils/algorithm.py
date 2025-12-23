# algorithm.py
"""
通用算法与数学工具模块
- 密码哈希处理
- 其他加密/数学操作可后续扩展
"""

import hashlib
import secrets

def hash_password(plain_password: str) -> str:
    """
    将明文密码转换为安全的哈希值（用于存储）
    使用 SHA256 + 随机盐

    Args:
        plain_password (str): 用户输入的明文密码

    Returns:
        str: 安全哈希字符串（格式：salt:hash）

    Example:
        hashed = hash_password("mySecret123")
    """
    if not isinstance(plain_password, str):
        raise ValueError("Password must be a string")
    if len(plain_password) == 0:
        raise ValueError("Password cannot be empty")

    # 生成随机盐
    salt = secrets.token_hex(16)
    # 创建哈希
    password_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
    # 返回 salt:hash 格式
    return f"{salt}:{password_hash}"


def verify_password(hashed_password: str, plain_password: str) -> bool:
    """
    验证明文密码是否与哈希值匹配

    Args:
        hashed_password (str): 数据库存储的哈希密码（格式：salt:hash）
        plain_password (str): 用户输入的明文密码

    Returns:
        bool: True 表示密码正确，False 表示错误

    Example:
        is_valid = verify_password(stored_hash, "inputPassword")
    """
    if not hashed_password or not plain_password:
        return False
    try:
        # 分离 salt 和 hash
        if ':' not in str(hashed_password):
            # 如果格式不对，直接返回 False
            return False
        
        salt, stored_hash = hashed_password.split(':', 1)
        # 用相同的盐重新计算密码哈希
        password_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
        # 比较哈希值
        return password_hash == stored_hash
    except Exception:
        return False