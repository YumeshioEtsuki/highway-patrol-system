# utils/exceptions.py
"""
自定义异常类：用于业务逻辑错误处理
"""

from fastapi import HTTPException, status


class AuthException(HTTPException):
    """认证异常（401）"""
    def __init__(self, detail: str = "认证失败，请先登录"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class PermissionException(HTTPException):
    """权限异常（403）"""
    def __init__(self, detail: str = "权限不足"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class BusinessException(HTTPException):
    """业务逻辑异常（400）"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(
            status_code=status_code,
            detail=detail
        )


class NotFoundException(HTTPException):
    """资源不存在异常（404）"""
    def __init__(self, detail: str = "请求的资源不存在"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class ValidationException(HTTPException):
    """数据验证异常（422）"""
    def __init__(self, detail: str = "数据验证失败"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class DatabaseException(HTTPException):
    """数据库操作异常（500）"""
    def __init__(self, detail: str = "数据库操作失败"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
