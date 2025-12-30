# =====================================================
# Phase 2 Stage 1: 工单与权限 Pydantic Schema
# =====================================================

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# =====================================================
# 枚举
# =====================================================

class OrderStatusEnum(str, Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    PROCESSING = "processing"
    REVIEWED = "reviewed"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class UserRoleEnum(str, Enum):
    INSPECTOR = "inspector"
    DISPATCHER = "dispatcher"
    PROCESSOR = "processor"
    AUDITOR = "auditor"
    ADMIN = "admin"

class DataScopeEnum(str, Enum):
    OWN = "own"
    DEPARTMENT = "dept"
    ALL = "all"

class OperationTypeEnum(str, Enum):
    ASSIGN = "assign"
    PROCESS = "process"
    REVIEW = "review"
    REJECT = "reject"
    ARCHIVE = "archive"

# =====================================================
# 角色与权限 Schema
# =====================================================

class PermissionBase(BaseModel):
    """权限基础"""
    resource: str
    action: str
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    """角色基础"""
    name: str
    display_name: str
    description: Optional[str] = None
    priority: int = 0

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None

class RolePermissionResponse(BaseModel):
    """角色包含的权限"""
    permission_id: int
    resource: str
    action: str
    data_scope: DataScopeEnum
    
    class Config:
        from_attributes = True

class RoleResponse(RoleBase):
    """角色详情"""
    id: int
    permissions: List[RolePermissionResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserPermissionOverrideCreate(BaseModel):
    """用户权限覆盖"""
    user_id: int
    permission_id: Optional[int] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    allowed: bool = True
    remark: Optional[str] = None

# =====================================================
# 工单状态机 Schema
# =====================================================

class OrderFlowLogBase(BaseModel):
    """工单流转日志基础"""
    operation: OperationTypeEnum
    remark: Optional[str] = None

class OrderFlowLogResponse(OrderFlowLogBase):
    id: int
    order_id: int
    old_status: str
    new_status: str
    operator_id: int
    operator_role: str
    operation_time: datetime
    ip_address: Optional[str] = None
    
    class Config:
        from_attributes = True

class OrderAssignRequest(BaseModel):
    """派单请求"""
    assigned_user_id: int = Field(..., description="派单人ID")
    remark: Optional[str] = None

    @validator('assigned_user_id')
    def validate_user_id(cls, v):
        if v <= 0:
            raise ValueError('用户ID必须大于0')
        return v

class OrderProcessRequest(BaseModel):
    """标记处理中"""
    remark: Optional[str] = None

class OrderReviewRequest(BaseModel):
    """提交审核"""
    review_remark: str = Field(..., min_length=10, description="审核意见(至少10字)")

class OrderRejectRequest(BaseModel):
    """驳回工单"""
    reject_reason: str = Field(..., min_length=20, description="驳回原因(至少20字)")

class OrderReviewApproveRequest(BaseModel):
    """审核批准"""
    review_remark: Optional[str] = None

class OrderArchiveRequest(BaseModel):
    """归档工单"""
    remark: Optional[str] = None

class OrderBatchOperationRequest(BaseModel):
    """批量操作"""
    order_ids: List[int] = Field(..., min_items=1, max_items=100)
    operation: OperationTypeEnum
    remark: Optional[str] = None

# =====================================================
# 工单查询与统计 Schema
# =====================================================

class OrderStatisticsResponse(BaseModel):
    """工单统计"""
    total: int
    new_count: int
    assigned_count: int
    processing_count: int
    reviewed_count: int
    rejected_count: int
    archived_count: int
    avg_process_time_hours: Optional[float] = None
    
    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    """工单列表项"""
    id: int
    order_status: OrderStatusEnum
    description: str
    upload_time: datetime
    assigned_time: Optional[datetime] = None
    process_time: Optional[datetime] = None
    review_time: Optional[datetime] = None
    creator_name: Optional[str] = None
    assigned_by: Optional[str] = None
    processor_name: Optional[str] = None
    reviewer_name: Optional[str] = None
    problem_type: Optional[str] = None
    department: Optional[str] = None
    road_segment: Optional[str] = None
    reject_count: int = 0
    
    class Config:
        from_attributes = True

class OrderDetailResponse(OrderListResponse):
    """工单详情"""
    reject_reason: Optional[str] = None
    review_remark: Optional[str] = None
    flow_logs: List[OrderFlowLogResponse] = []

# =====================================================
# SLA 配置 Schema
# =====================================================

class SLAConfigCreate(BaseModel):
    """SLA 配置创建"""
    problem_type_id: int
    name: str
    dispatch_sla_hours: int = 24
    process_sla_hours: int = 72
    review_sla_hours: int = 24
    total_sla_hours: int = 120
    priority: int = 5
    remark: Optional[str] = None

class SLAConfigUpdate(BaseModel):
    """SLA 配置更新"""
    dispatch_sla_hours: Optional[int] = None
    process_sla_hours: Optional[int] = None
    review_sla_hours: Optional[int] = None
    total_sla_hours: Optional[int] = None
    priority: Optional[int] = None
    enabled: Optional[bool] = None
    remark: Optional[str] = None

class SLAConfigResponse(SLAConfigCreate):
    """SLA 配置响应"""
    id: int
    enabled: bool
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SLAAlertResponse(BaseModel):
    """SLA 告警响应"""
    id: int
    order_id: int
    sla_type: str  # dispatch, process, review, total
    due_time: datetime
    alert_level: str  # warning, critical
    alerted_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    
    class Config:
        from_attributes = True

class SLAStatisticsResponse(BaseModel):
    """SLA 统计"""
    problem_type: str
    total_orders: int
    completed: int
    dispatch_sla_miss: int
    process_sla_miss: int
    review_sla_miss: int
    sla_compliance_rate: float

# =====================================================
# 审计日志 Schema
# =====================================================

class AuditLogResponse(BaseModel):
    """审计日志"""
    id: int
    operator_id: int
    operator_name: str
    resource_type: str
    resource_id: Optional[int] = None
    action: str
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    change_summary: Optional[str] = None
    operation_time: datetime
    ip_address: Optional[str] = None
    status: str
    error_msg: Optional[str] = None
    
    class Config:
        from_attributes = True

class AuditLogListResponse(BaseModel):
    """审计日志列表"""
    total: int
    items: List[AuditLogResponse]
    
    class Config:
        from_attributes = True

# =====================================================
# 权限检查响应
# =====================================================

class PermissionCheckResponse(BaseModel):
    """权限检查结果"""
    has_permission: bool
    resource: str
    action: str
    data_scope: Optional[DataScopeEnum] = None
    reason: Optional[str] = None

class CurrentUserInfo(BaseModel):
    """当前用户信息"""
    user_id: int
    username: str
    real_name: str
    role_id: Optional[int] = None
    role_name: str
    permissions: List[str] = []
    can_view_segments: List[int] = []
    is_admin: bool
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# =====================================================
# 统计与报表 Schema
# =====================================================

class OrderPerformanceMetrics(BaseModel):
    """工单性能指标"""
    total_orders: int
    completion_rate: float  # 完成率百分比
    avg_dispatch_time_hours: float
    avg_process_time_hours: float
    avg_review_time_hours: float
    avg_total_time_hours: float
    rejection_rate: float  # 驳回率
    overdue_rate: float  # 逾期率
    sla_compliance_rate: float  # SLA 达成率

class DepartmentPerformance(BaseModel):
    """部门绩效统计"""
    department_name: str
    total_assigned: int
    completed: int
    completion_rate: float
    avg_process_time_hours: float
    sla_compliance_rate: float
    top_processor: Optional[str] = None
    processor_completion_count: Optional[int] = None

class UserPerformance(BaseModel):
    """用户个人绩效"""
    user_id: int
    user_name: str
    role: str
    total_handled: int
    completed: int
    completion_rate: float
    avg_process_time_hours: Optional[float] = None
    avg_review_time_hours: Optional[float] = None
    quality_score: Optional[float] = None  # 质量评分

