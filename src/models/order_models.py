# =====================================================
# Phase 2 Stage 1: 工单状态机与权限模型
# =====================================================

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum as PyEnum

Base = declarative_base()

# =====================================================
# 枚举定义
# =====================================================

class OrderStatus(PyEnum):
    """工单状态流转"""
    NEW = "new"                    # 新创建
    ASSIGNED = "assigned"          # 已派单
    PROCESSING = "processing"      # 处理中
    REVIEWED = "reviewed"          # 已审核
    REJECTED = "rejected"          # 已驳回
    ARCHIVED = "archived"          # 已归档

class UserRole(PyEnum):
    """用户角色"""
    INSPECTOR = "inspector"        # 巡查员
    DISPATCHER = "dispatcher"      # 派单人
    PROCESSOR = "processor"        # 处理人
    AUDITOR = "auditor"           # 复核人
    ADMIN = "admin"               # 管理员

class DataScope(PyEnum):
    """数据可见范围"""
    OWN = "own"                    # 仅本人
    DEPARTMENT = "dept"            # 部门内
    ALL = "all"                    # 全部

class OperationType(PyEnum):
    """操作类型"""
    ASSIGN = "assign"
    PROCESS = "process"
    REVIEW = "review"
    REJECT = "reject"
    ARCHIVE = "archive"

# =====================================================
# 数据库模型 (SQLAlchemy ORM)
# =====================================================

class Role(Base):
    """角色表"""
    __tablename__ = "role"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Permission(Base):
    """权限表"""
    __tablename__ = "permission"
    
    id = Column(Integer, primary_key=True)
    resource = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class RolePermission(Base):
    """角色权限映射"""
    __tablename__ = "role_permission"
    
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permission.id"), nullable=False)
    data_scope = Column(String(50), default="own")
    created_at = Column(DateTime, default=datetime.utcnow)

class UserPermissionOverride(Base):
    """用户权限覆盖 (特殊权限)"""
    __tablename__ = "user_permission_override"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    permission_id = Column(Integer, ForeignKey("permission.id"))
    resource = Column(String(100))
    action = Column(String(50))
    allowed = Column(Boolean, default=True)
    remark = Column(String(255))
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class OrderFlowLog(Base):
    """工单流转日志"""
    __tablename__ = "order_flow_log"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("inspectionrecord.id"), nullable=False)
    old_status = Column(String(50))
    new_status = Column(String(50))
    operator_id = Column(Integer, nullable=False)
    operator_role = Column(String(50))
    operation = Column(String(50))
    remark = Column(Text)
    operation_time = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))

class SLAConfig(Base):
    """SLA 配置表"""
    __tablename__ = "sla_config"
    
    id = Column(Integer, primary_key=True)
    problem_type_id = Column(Integer, ForeignKey("problemtype.id"), nullable=False)
    name = Column(String(100))
    dispatch_sla_hours = Column(Integer, default=24)
    process_sla_hours = Column(Integer, default=72)
    review_sla_hours = Column(Integer, default=24)
    total_sla_hours = Column(Integer, default=120)
    priority = Column(Integer, default=5)
    enabled = Column(Boolean, default=True)
    remark = Column(Text)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SLAAlert(Base):
    """SLA 违规告警"""
    __tablename__ = "sla_alert"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("inspectionrecord.id"), nullable=False)
    sla_type = Column(String(50))  # dispatch, process, review, total
    due_time = Column(DateTime)
    alert_level = Column(String(50))  # warning, critical
    alerted_at = Column(DateTime)
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer)

class AuditLog(Base):
    """操作审计日志"""
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True)
    operator_id = Column(Integer, nullable=False)
    operator_name = Column(String(50))
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    action = Column(String(50))
    old_value = Column(JSON)
    new_value = Column(JSON)
    change_summary = Column(Text)
    operation_time = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    status = Column(String(50), default="success")
    error_msg = Column(Text)

class AdminIPWhitelist(Base):
    """管理员 IP 白名单"""
    __tablename__ = "admin_ip_whitelist"
    
    id = Column(Integer, primary_key=True)
    ip_address = Column(String(45), unique=True, nullable=False)
    ip_range_start = Column(String(45))
    ip_range_end = Column(String(45))
    description = Column(String(255))
    enabled = Column(Boolean, default=True)
    added_by = Column(Integer)
    added_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RefreshToken(Base):
    """JWT 刷新令牌"""
    __tablename__ = "refresh_token"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_ip = Column(String(45))
    revoked_at = Column(DateTime)

class DepartmentSegment(Base):
    """部门与路段映射"""
    __tablename__ = "department_segment"
    
    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("department.id"), nullable=False)
    segment_id = Column(Integer, ForeignKey("roadsegment.id"), nullable=False)
    primary_dept = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

