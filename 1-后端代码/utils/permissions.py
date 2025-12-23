# =====================================================
# Phase 2 Stage 1: 权限检查工具与依赖注入
# =====================================================

import hashlib
import json
from typing import Optional, List, Dict, Set, Tuple
from datetime import datetime, timedelta
from functools import wraps
from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt

from utils.config import settings
from utils.utils import get_db_connection, close_db_connection

# =====================================================
# JWT Token 与刷新令牌管理
# =====================================================

def hash_token(token: str) -> str:
    """哈希 Token (用于存储到数据库)"""
    return hashlib.sha256(token.encode()).hexdigest()

def create_refresh_token(user_id: int, db_connection) -> Tuple[str, str]:
    """
    创建刷新令牌
    返回: (refresh_token, token_hash)
    """
    import uuid
    refresh_token = str(uuid.uuid4())
    token_hash = hash_token(refresh_token)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    try:
        cursor = db_connection.cursor()
        cursor.execute("""
            INSERT INTO refresh_token (user_id, token_hash, expires_at, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (user_id, token_hash, expires_at))
        db_connection.commit()
        cursor.close()
        return refresh_token, token_hash
    except Exception as e:
        db_connection.rollback()
        raise ValueError(f"创建刷新令牌失败: {str(e)}")

def revoke_refresh_token(token: str, db_connection):
    """撤销刷新令牌"""
    try:
        token_hash = hash_token(token)
        cursor = db_connection.cursor()
        cursor.execute("""
            UPDATE refresh_token SET revoked_at = NOW() WHERE token_hash = %s
        """, (token_hash,))
        db_connection.commit()
        cursor.close()
    except Exception as e:
        db_connection.rollback()
        raise ValueError(f"撤销令牌失败: {str(e)}")

def verify_refresh_token(token: str, db_connection) -> Optional[int]:
    """
    验证刷新令牌
    返回: user_id (如果有效) 或 None
    """
    try:
        token_hash = hash_token(token)
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT user_id FROM refresh_token
            WHERE token_hash = %s 
            AND revoked_at IS NULL
            AND expires_at > NOW()
        """, (token_hash,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    except Exception:
        return None

# =====================================================
# 权限缓存 (Redis)
# =====================================================

from utils.redis_client import redis_client

def get_user_permissions_cached(user_id: int, db_connection) -> Dict[str, List[str]]:
    """
    获取用户权限 (带 Redis 缓存)
    返回: {resource: [action1, action2, ...]}
    """
    cache_key = f"user_permissions:{user_id}"
    
    # 尝试从缓存获取
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # 从数据库查询
    permissions = {}
    try:
        cursor = db_connection.cursor()
        
        # 查询角色权限
        cursor.execute("""
            SELECT DISTINCT p.resource, p.action
            FROM user u
            JOIN role r ON u.role_id = r.id
            JOIN role_permission rp ON r.id = rp.role_id
            JOIN permission p ON rp.permission_id = p.id
            WHERE u.user_id = %s
            UNION
            -- 特殊权限覆盖 (允许)
            SELECT p.resource, p.action
            FROM user_permission_override upo
            JOIN permission p ON upo.permission_id = p.id
            WHERE upo.user_id = %s AND upo.allowed = 1
            UNION
            -- 资源级别的特殊权限
            SELECT upo.resource, upo.action
            FROM user_permission_override upo
            WHERE upo.user_id = %s AND upo.resource IS NOT NULL
            AND upo.allowed = 1
        """, (user_id, user_id, user_id))
        
        for resource, action in cursor.fetchall():
            if resource not in permissions:
                permissions[resource] = []
            permissions[resource].append(action)
        
        cursor.close()
        
        # 缓存 24 小时
        redis_client.setex(cache_key, 86400, json.dumps(permissions))
        
    except Exception as e:
        print(f"权限查询失败: {str(e)}")
    
    return permissions

def invalidate_user_permissions_cache(user_id: int):
    """清除用户权限缓存"""
    redis_client.delete(f"user_permissions:{user_id}")

# =====================================================
# 权限检查函数
# =====================================================

def check_permission(
    user_id: int,
    resource: str,
    action: str,
    db_connection,
    data_scope: str = "all"  # own, dept, all
) -> bool:
    """
    检查用户是否有特定权限
    
    Args:
        user_id: 用户ID
        resource: 资源类型 (order, photo, report, user, config)
        action: 操作类型 (create, read, update, delete, etc)
        db_connection: 数据库连接
        data_scope: 数据范围
    
    Returns:
        bool: 是否有权限
    """
    try:
        cursor = db_connection.cursor()
        
        # 检查是否为 Admin (特殊处理)
        cursor.execute("""
            SELECT r.name FROM user u
            JOIN role r ON u.role_id = r.id
            WHERE u.user_id = %s
        """, (user_id,))
        result = cursor.fetchone()
        if result and result[0] == 'admin':
            cursor.close()
            return True
        
        # 检查标准权限
        cursor.execute("""
            SELECT COUNT(*) FROM (
                -- 角色权限
                SELECT 1 FROM user u
                JOIN role r ON u.role_id = r.id
                JOIN role_permission rp ON r.id = rp.role_id
                JOIN permission p ON rp.permission_id = p.id
                WHERE u.user_id = %s AND p.resource = %s AND p.action = %s
                AND (rp.data_scope = %s OR rp.data_scope = 'all')
                
                UNION
                
                -- 特殊权限覆盖
                SELECT 1 FROM user_permission_override upo
                JOIN permission p ON upo.permission_id = p.id
                WHERE upo.user_id = %s AND p.resource = %s 
                AND p.action = %s AND upo.allowed = 1
                
                UNION
                
                -- 资源级别特殊权限
                SELECT 1 FROM user_permission_override upo
                WHERE upo.user_id = %s AND upo.resource = %s
                AND upo.action = %s AND upo.allowed = 1
            ) AS perms
        """, (user_id, resource, action, data_scope,
              user_id, resource, action,
              user_id, resource, action))
        
        count = cursor.fetchone()[0]
        cursor.close()
        
        return count > 0
        
    except Exception as e:
        print(f"权限检查异常: {str(e)}")
        return False

# =====================================================
# FastAPI 依赖注入
# =====================================================

class PermissionChecker:
    """权限检查依赖"""
    
    def __init__(self, resource: str, action: str, data_scope: str = "all"):
        self.resource = resource
        self.action = action
        self.data_scope = data_scope
    
    async def __call__(self, request: Request, current_user: dict = Depends(get_current_user_info)):
        """
        检查权限
        如果无权限，抛出 403 异常
        """
        db_connection = get_db_connection()
        try:
            has_perm = check_permission(
                current_user['user_id'],
                self.resource,
                self.action,
                db_connection,
                self.data_scope
            )
            
            if not has_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"无权限执行: {self.resource}.{self.action}",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # 记录审计日志
            log_audit_action(
                user_id=current_user['user_id'],
                resource_type=self.resource,
                action=self.action,
                status="success",
                ip_address=request.client.host if request.client else None,
                db_connection=db_connection
            )
            
        finally:
            close_db_connection(db_connection)

async def get_current_user_info(request: Request) -> dict:
    """
    获取当前用户信息 (依赖注入)
    """
    # 从 request.state 或 token 解析
    if hasattr(request.state, 'current_user'):
        return request.state.current_user
    
    # 从 Authorization Header 获取 Token
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少有效的认证令牌"
        )
    
    token = auth_header[7:]  # 移除 "Bearer "
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌无效"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌过期或无效"
        )
    
    # 从数据库查询用户详情
    db_connection = get_db_connection()
    try:
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT u.user_id, u.username, u.real_name, r.name
            FROM user u
            LEFT JOIN role r ON u.role_id = r.id
            WHERE u.user_id = %s AND u.is_active = 1
        """, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已禁用"
            )
        
        return {
            'user_id': result[0],
            'username': result[1],
            'real_name': result[2],
            'role_name': result[3] or 'unknown',
            'is_admin': result[3] == 'admin'
        }
    finally:
        close_db_connection(db_connection)

def require_permission(resource: str, action: str, data_scope: str = "all"):
    """
    装饰器: 检查权限
    
    使用示例:
    @router.post("/orders/{id}/assign")
    @require_permission("order", "assign")
    async def assign_order(order_id: int, ...):
        pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request = None, current_user: dict = None, **kwargs):
            if not request or not current_user:
                raise ValueError("require_permission 必须与 FastAPI 依赖一起使用")
            
            db_connection = get_db_connection()
            try:
                has_perm = check_permission(
                    current_user['user_id'],
                    resource,
                    action,
                    db_connection,
                    data_scope
                )
                
                if not has_perm:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"无权限执行: {resource}.{action}"
                    )
                
            finally:
                close_db_connection(db_connection)
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator

# =====================================================
# 审计日志记录
# =====================================================

def log_audit_action(
    user_id: int,
    resource_type: str,
    action: str,
    resource_id: Optional[int] = None,
    old_value: Optional[Dict] = None,
    new_value: Optional[Dict] = None,
    change_summary: Optional[str] = None,
    status: str = "success",
    error_msg: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    db_connection = None
):
    """
    记录操作审计日志
    """
    if not db_connection:
        db_connection = get_db_connection()
    
    try:
        # 获取用户名
        cursor = db_connection.cursor()
        cursor.execute("SELECT real_name FROM user WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        operator_name = result[0] if result else "Unknown"
        
        # 插入审计日志
        cursor.execute("""
            INSERT INTO audit_log (
                operator_id, operator_name, resource_type, resource_id,
                action, old_value, new_value, change_summary,
                operation_time, ip_address, user_agent, status, error_msg
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s)
        """, (
            user_id, operator_name, resource_type, resource_id, action,
            json.dumps(old_value) if old_value else None,
            json.dumps(new_value) if new_value else None,
            change_summary,
            ip_address, user_agent, status, error_msg
        ))
        db_connection.commit()
        cursor.close()
    except Exception as e:
        print(f"审计日志记录失败: {str(e)}")

