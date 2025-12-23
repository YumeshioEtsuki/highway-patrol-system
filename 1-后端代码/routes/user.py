# routes/user.py
from fastapi import APIRouter, HTTPException, Depends, status, Request
from models.schemas import (
    RegisterRequest, LoginRequest, PasswordChangeRequest,
    TokenResponse, UserResponse, ApiResponse
)
from models.tasks import (
    user_login_by_password,
    register_user,
    update_user_password
)
from utils.deps import get_current_user, CurrentUser, create_access_token
from utils.exceptions import BusinessException, AuthException
from utils.logger import setup_logger
from utils.rate_limit import limiter
from fastapi import Depends

logger = setup_logger(__name__)

router = APIRouter(prefix="/api", tags=["user"])


@router.post("/register", response_model=ApiResponse, summary="用户注册")
async def register(req: RegisterRequest):
    """
    用户注册接口
    
    - **username**: 用户名（3-50字符，唯一）
    - **password**: 密码（至少8位，必须包含字母和数字）
    - **real_name**: 真实姓名
    - **phone**: 手机号（可选）
    - **email**: 邮箱（可选）
    """
    try:
        # 简单规则：用户名以 admin_ 开头则注册为管理员，否则巡查员
        role = 'admin' if req.username.startswith('admin_') else 'inspector'

        user_id = register_user(
            username=req.username,
            password=req.password,  # tasks.py 内部会哈希
            real_name=req.real_name,
            phone=req.phone,
            email=req.email,
            role=role
        )
        return ApiResponse(
            success=True,
            message="注册成功",
            data={"user_id": user_id}
        )
    except ValueError as e:
        raise BusinessException(detail=str(e))
    except Exception as e:
        logger.error(f"Register error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )


@router.post("/login", response_model=TokenResponse, summary="用户登录")
@limiter.limit("5/minute")
async def login(req: LoginRequest, request: Request):
    """
    用户登录接口
    
    - **username**: 用户名
    - **password**: 密码
    
    返回 JWT token，后续请求需在 Header 中携带：
    ```
    Authorization: Bearer <token>
    ```
    """
    try:
        user = user_login_by_password(req.username, req.password)
        if not user:
            raise AuthException(detail="用户名或密码错误")
        
        # 生成 JWT token
        token = create_access_token(
            user_id=user['user_id'],
            username=user['username'],
            role=user['role']
        )
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=user
        )
    except AuthException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )


@router.post("/change-password", response_model=ApiResponse, summary="修改密码")
async def change_password(
    req: PasswordChangeRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    修改密码接口（支持登录和未登录两种方式）
    
    - **username**: 用户名（未登录时必填）
    - **old_password**: 原密码
    - **new_password**: 新密码（至少8位，必须包含字母和数字）
    """
    try:
        # 如果提供了username，先验证该用户名和原密码是否匹配
        if req.username:
            user_data = user_login_by_password(req.username, req.old_password)
            if not user_data:
                raise BusinessException(detail="用户名或原密码错误")
            user_id = user_data['user_id']
            # 直接更新为新密码，不需要再次验证旧密码
            from models.tasks import get_db_connection
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE User SET password=%s WHERE user_id=%s",
                (pwd_context.hash(req.new_password), user_id)
            )
            conn.commit()
            cur.close()
            conn.close()
        else:
            # 使用已登录用户的user_id
            success = update_user_password(
                current_user.user_id,
                req.old_password,
                req.new_password
            )
            if not success:
                raise BusinessException(detail="原密码错误")
        
        return ApiResponse(
            success=True,
            message="密码修改成功"
        )
    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )


@router.post("/logout", response_model=ApiResponse, summary="用户登出")
async def logout(current_user: CurrentUser = Depends(get_current_user)):
    """
    用户登出接口（客户端需自行删除 token）
    
    注意：JWT 是无状态的，服务端不保存 token，
    客户端应在登出时删除本地存储的 token。
    """
    return ApiResponse(
        success=True,
        message="登出成功"
    )


@router.get("/me", response_model=CurrentUser, summary="获取当前用户信息")
async def current_user_info(current_user: CurrentUser = Depends(get_current_user)):
    """
    获取当前登录用户信息
    
    需要在 Header 中携带有效的 JWT token。
    """
    return current_user