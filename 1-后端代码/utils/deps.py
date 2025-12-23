# utils/deps.py
"""
FastAPI 依赖注入：JWT 认证和权限校验
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from utils.config import settings
from typing import Optional


# HTTP Bearer 认证方案
security = HTTPBearer()


class TokenPayload(BaseModel):
    """JWT Token 载荷"""
    user_id: int
    username: str
    role: str
    exp: int


class CurrentUser(BaseModel):
    """当前登录用户信息"""
    user_id: int
    username: str
    role: str


def create_access_token(user_id: int, username: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    生成 JWT access token
    
    Args:
        user_id: 用户ID
        username: 用户名
        role: 角色（inspector/admin）
        expires_delta: 过期时间（默认24小时）
    
    Returns:
        JWT token 字符串
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.JWT_EXPIRE_HOURS)
    
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": expire
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> TokenPayload:
    """
    解析 JWT token
    
    Args:
        token: JWT token 字符串
    
    Returns:
        TokenPayload 对象
    
    Raises:
        HTTPException: token 无效或过期
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return TokenPayload(**payload)
    except (JWTError, Exception) as e:
        # 使用 logger 而不是 print，避免 Windows console 编码问题
        from utils.logger import setup_logger
        logger = setup_logger(__name__)
        logger.error(f"Token decode failed: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    获取当前登录用户（依赖注入）
    
    用法：
        @router.get("/api/me")
        async def get_me(current_user: CurrentUser = Depends(get_current_user)):
            return current_user
    
    Returns:
        CurrentUser 对象
    
    Raises:
        HTTPException 401: 未登录或 token 无效
    """
    token = credentials.credentials
    token_data = decode_access_token(token)
    
    current_user = CurrentUser(
        user_id=token_data.user_id,
        username=token_data.username,
        role=token_data.role
    )
    print(f"[AUTH] 认证成功: user_id={current_user.user_id}, username={current_user.username}, role={current_user.role}")
    return current_user


async def get_current_admin(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    获取当前管理员用户（依赖注入）
    
    用法：
        @router.get("/api/admin/stats")
        async def admin_stats(admin: CurrentUser = Depends(get_current_admin)):
            # 只有管理员能访问
            return {"message": "admin only"}
    
    Returns:
        CurrentUser 对象（已验证为管理员）
    
    Raises:
        HTTPException 403: 权限不足
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足：仅管理员可访问"
        )
    
    return current_user


# 兼容 SSE/查询参数的认证：从 Header 或 token 查询参数获取
async def get_current_user_qs(request: Request) -> CurrentUser:
    token = None

    # 1) Header: Authorization: Bearer <token>
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1].strip()

    # 2) QueryString: ?token=<token>
    if not token:
        token = request.query_params.get("token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌"
        )

    try:
        token_data = decode_access_token(token)
    except HTTPException:
        raise
    except Exception as e:
        from utils.logger import setup_logger
        logger = setup_logger(__name__)
        logger.error(f"Token decode error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证令牌无效"
        )
    
    return CurrentUser(
        user_id=token_data.user_id,
        username=token_data.username,
        role=token_data.role
    )


async def get_current_admin_qs(user: CurrentUser = Depends(get_current_user_qs)) -> CurrentUser:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足：仅管理员可访问"
        )
    return user


# 可选依赖：允许未登录访问
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[CurrentUser]:
    """
    可选的用户认证（允许未登录）
    
    用法：
        @router.get("/api/public")
        async def public_endpoint(user: Optional[CurrentUser] = Depends(get_current_user_optional)):
            if user:
                return {"message": f"Hello {user.username}"}
            return {"message": "Hello guest"}
    
    Returns:
        CurrentUser 对象或 None
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        token_data = decode_access_token(token)
        return CurrentUser(
            user_id=token_data.user_id,
            username=token_data.username,
            role=token_data.role
        )
    except HTTPException:
        return None
