# models/schemas.py
"""
Pydantic 数据模型：用于 FastAPI 请求验证和响应序列化
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


# ========================
# 用户相关模型
# ========================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    real_name: str = Field(..., min_length=2, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")


class RegisterRequest(UserBase):
    password: str = Field(..., min_length=8, description="密码（至少8位，包含字母和数字）")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(c.isalpha() for c in v):
            raise ValueError('密码必须包含字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含数字')
        return v


class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class PasswordChangeRequest(BaseModel):
    username: Optional[str] = Field(None, description="用户名（未登录时必填）")
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=8, description="新密码")
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if not any(c.isalpha() for c in v):
            raise ValueError('密码必须包含字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含数字')
        return v


class UserResponse(BaseModel):
    user_id: int
    username: str
    real_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    role: str
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ========================
# 巡查记录相关模型
# ========================

class PatrolCreate(BaseModel):
    user_id: int = Field(..., description="用户ID")
    patrol_time: datetime = Field(..., description="巡查时间")
    segment_id: int = Field(..., description="路段ID")
    problem_type_id: int = Field(..., description="问题类型ID")
    description: str = Field(..., min_length=1, max_length=500, description="问题描述")
    severity: Optional[int] = Field(1, ge=1, le=5, description="严重等级（1-5）")
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")


class PatrolQuery(BaseModel):
    user_id: int
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")


class PatrolResponse(BaseModel):
    record_id: int
    user_id: int
    upload_time: datetime
    segment_id: int
    problem_type_id: int
    description: str
    status: str
    severity: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    segment_name: Optional[str] = None
    problem_type_name: Optional[str] = None
    inspector_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class PatrolDetailResponse(PatrolResponse):
    department_name: Optional[str] = None
    process_note: Optional[str] = None
    photos: List[dict] = []


class PatrolListResponse(BaseModel):
    records: List[PatrolResponse]
    total: int
    page: int
    page_size: int


# ========================
# 照片相关模型
# ========================

class PhotoResponse(BaseModel):
    photo_id: int
    record_id: int
    file_path: str
    file_name: str
    upload_time: datetime
    
    class Config:
        from_attributes = True


class PhotoUploadResponse(BaseModel):
    photo_id: int
    photo_url: str


# ========================
# 管理员相关模型
# ========================

class AdminProcessRequest(BaseModel):
    record_id: int


class AdminCompleteRequest(BaseModel):
    remark: str = Field(..., min_length=1, max_length=500, description="处理备注")


class PatrolListAdminQuery(BaseModel):
    status: Optional[str] = Field(None, description="状态筛选（pending/processing/completed）")


class ExportExcelQuery(BaseModel):
    start_date: Optional[str] = Field(None, description="开始日期（YYYY-MM-DD）")
    end_date: Optional[str] = Field(None, description="结束日期（YYYY-MM-DD）")
    segment_id: Optional[int] = Field(None, description="路段ID")
    status: Optional[str] = Field(None, description="状态筛选")


# ========================
# 路段和问题类型相关模型
# ========================

class RoadSegmentResponse(BaseModel):
    segment_id: int
    segment_name: str
    start_number: int
    end_number: int
    department_id: Optional[int] = None


class ProblemTypeResponse(BaseModel):
    type_id: int
    type_name: str
    parent_id: Optional[int] = None


class RoadSegmentsListResponse(BaseModel):
    data: List[RoadSegmentResponse]


class ProblemTypesListResponse(BaseModel):
    data: List[ProblemTypeResponse]


# ========================
# 统计相关模型
# ========================

class UserStatsResponse(BaseModel):
    total_records: int
    pending_count: int
    processing_count: int
    completed_count: int


# ========================
# 通用响应模型
# ========================

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
