# =====================================================
# Phase 2 Stage 1: 工单管理 API 路由
# =====================================================

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import Optional, List
from datetime import datetime

from models.order_schemas import (
    OrderAssignRequest, OrderProcessRequest, OrderReviewRequest,
    OrderRejectRequest, OrderArchiveRequest, OrderListResponse,
    OrderDetailResponse, OrderFlowLogResponse, OrderStatisticsResponse,
    OrderPerformanceMetrics, SLAConfigResponse, SLAAlertResponse
)
from models.order_tasks import (
    assign_order, process_order, review_order, reject_order, archive_order,
    get_order_detail, list_orders, get_sla_violations
)
from utils.permissions import (
    PermissionChecker, get_current_user_info, log_audit_action, invalidate_user_permissions_cache
)
from utils.utils import get_db_connection, close_db_connection

router = APIRouter(prefix="/api/orders", tags=["orders"])

# =====================================================
# 工单派单 API
# =====================================================

@router.post("/{order_id}/assign", response_model=dict, summary="派单")
async def assign_order_api(
    order_id: int,
    request_data: OrderAssignRequest,
    request: Request,
    current_user: dict = Depends(get_current_user_info),
    _: None = Depends(PermissionChecker("order", "assign"))
):
    """
    派单工单给指定用户
    
    - **order_id**: 工单ID
    - **assigned_user_id**: 派单给的用户ID
    - **remark**: 派单备注 (可选)
    
    权限要求: dispatcher 或 admin
    """
    db_connection = get_db_connection()
    try:
        assign_order(
            order_id=order_id,
            assigned_user_id=request_data.assigned_user_id,
            remark=request_data.remark or "",
            operator_id=current_user['user_id'],
            db_connection=db_connection,
            ip_address=request.client.host if request.client else None
        )
        
        log_audit_action(
            user_id=current_user['user_id'],
            resource_type='order',
            action='assign',
            resource_id=order_id,
            change_summary=f"派单给用户 {request_data.assigned_user_id}",
            ip_address=request.client.host if request.client else None,
            db_connection=db_connection
        )
        
        return {
            "status": "success",
            "message": f"工单 {order_id} 已派单",
            "order_id": order_id
        }
    except ValueError as e:
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        close_db_connection(db_connection)

# =====================================================
# 工单处理 API
# =====================================================

@router.post("/{order_id}/process", response_model=dict, summary="标记处理中")
async def process_order_api(
    order_id: int,
    request_data: OrderProcessRequest,
    request: Request,
    current_user: dict = Depends(get_current_user_info),
    _: None = Depends(PermissionChecker("order", "process"))
):
    """
    标记工单为处理中
    
    权限要求: processor 或 admin
    """
    db_connection = get_db_connection()
    try:
        process_order(
            order_id=order_id,
            processor_id=current_user['user_id'],
            remark=request_data.remark or "",
            operator_id=current_user['user_id'],
            db_connection=db_connection,
            ip_address=request.client.host if request.client else None
        )
        
        return {
            "status": "success",
            "message": f"工单 {order_id} 已标记为处理中",
            "order_id": order_id
        }
    except ValueError as e:
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        close_db_connection(db_connection)

# =====================================================
# 工单审核 API
# =====================================================

@router.post("/{order_id}/review", response_model=dict, summary="提交审核")
async def review_order_api(
    order_id: int,
    request_data: OrderReviewRequest,
    request: Request,
    current_user: dict = Depends(get_current_user_info),
    _: None = Depends(PermissionChecker("order", "review"))
):
    """
    提交工单审核
    
    权限要求: auditor 或 admin
    """
    db_connection = get_db_connection()
    try:
        review_order(
            order_id=order_id,
            reviewer_id=current_user['user_id'],
            review_remark=request_data.review_remark,
            operator_id=current_user['user_id'],
            db_connection=db_connection,
            ip_address=request.client.host if request.client else None
        )
        
        return {
            "status": "success",
            "message": f"工单 {order_id} 已审核",
            "order_id": order_id
        }
    except ValueError as e:
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        close_db_connection(db_connection)

@router.post("/{order_id}/reject", response_model=dict, summary="驳回工单")
async def reject_order_api(
    order_id: int,
    request_data: OrderRejectRequest,
    request: Request,
    current_user: dict = Depends(get_current_user_info),
    _: None = Depends(PermissionChecker("order", "reject"))
):
    """
    驳回工单
    
    权限要求: auditor 或 admin
    """
    db_connection = get_db_connection()
    try:
        reject_order(
            order_id=order_id,
            reject_reason=request_data.reject_reason,
            reviewer_id=current_user['user_id'],
            operator_id=current_user['user_id'],
            db_connection=db_connection,
            ip_address=request.client.host if request.client else None
        )
        
        log_audit_action(
            user_id=current_user['user_id'],
            resource_type='order',
            action='reject',
            resource_id=order_id,
            change_summary=f"驳回原因: {request_data.reject_reason}",
            ip_address=request.client.host if request.client else None,
            db_connection=db_connection
        )
        
        return {
            "status": "success",
            "message": f"工单 {order_id} 已驳回",
            "order_id": order_id
        }
    except ValueError as e:
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        close_db_connection(db_connection)

@router.post("/{order_id}/approve", response_model=dict, summary="批准工单")
async def approve_order_api(
    order_id: int,
    request_data: OrderArchiveRequest,
    request: Request,
    current_user: dict = Depends(get_current_user_info),
    _: None = Depends(PermissionChecker("order", "review"))
):
    """
    批准工单并归档
    
    权限要求: auditor 或 admin
    """
    db_connection = get_db_connection()
    try:
        archive_order(
            order_id=order_id,
            operator_id=current_user['user_id'],
            remark=request_data.remark or "",
            db_connection=db_connection,
            ip_address=request.client.host if request.client else None
        )
        
        return {
            "status": "success",
            "message": f"工单 {order_id} 已批准并归档",
            "order_id": order_id
        }
    except ValueError as e:
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        close_db_connection(db_connection)

# =====================================================
# 工单查询 API
# =====================================================

@router.get("/{order_id}", response_model=OrderDetailResponse, summary="获取工单详情")
async def get_order_api(
    order_id: int,
    current_user: dict = Depends(get_current_user_info),
    _: None = Depends(PermissionChecker("order", "read"))
):
    """
    获取工单详情
    
    权限要求: order:read
    """
    db_connection = get_db_connection()
    try:
        order = get_order_detail(order_id, db_connection)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"工单 {order_id} 不存在"
            )
        return order
    finally:
        close_db_connection(db_connection)

@router.get("", response_model=dict, summary="工单列表")
async def list_orders_api(
    status: Optional[str] = Query(None, description="工单状态过滤"),
    limit: int = Query(20, ge=1, le=100, description="分页大小"),
    offset: int = Query(0, ge=0, description="分页偏移"),
    current_user: dict = Depends(get_current_user_info),
    _: None = Depends(PermissionChecker("order", "read"))
):
    """
    获取工单列表
    
    支持状态过滤:
    - new: 新建
    - assigned: 已派单
    - processing: 处理中
    - reviewed: 已审核
    - rejected: 已驳回
    - archived: 已归档
    
    权限要求: order:read
    """
    db_connection = get_db_connection()
    try:
        orders, total = list_orders(
            user_id=current_user['user_id'],
            role=current_user.get('role_name', 'unknown'),
            status=status,
            limit=limit,
            offset=offset,
            db_connection=db_connection
        )
        
        return {
            "status": "success",
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": orders
        }
    finally:
        close_db_connection(db_connection)

# =====================================================
# 工单统计与分析 API
# =====================================================

@router.get("/stats/overview", response_model=OrderStatisticsResponse, summary="工单统计")
async def order_statistics_api(
    current_user: dict = Depends(get_current_user_info)
):
    """
    获取工单统计信息
    """
    db_connection = get_db_connection()
    try:
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN order_status = 'new' THEN 1 ELSE 0 END) as new_count,
                SUM(CASE WHEN order_status = 'assigned' THEN 1 ELSE 0 END) as assigned_count,
                SUM(CASE WHEN order_status = 'processing' THEN 1 ELSE 0 END) as processing_count,
                SUM(CASE WHEN order_status = 'reviewed' THEN 1 ELSE 0 END) as reviewed_count,
                SUM(CASE WHEN order_status = 'rejected' THEN 1 ELSE 0 END) as rejected_count,
                SUM(CASE WHEN order_status = 'archived' THEN 1 ELSE 0 END) as archived_count,
                ROUND(AVG(TIMESTAMPDIFF(HOUR, upload_time, 
                    COALESCE(review_time, NOW()))), 2) as avg_process_time_hours
            FROM inspectionrecord
        """)
        
        row = cursor.fetchone()
        cursor.close()
        
        return {
            "total": row[0] or 0,
            "new_count": row[1] or 0,
            "assigned_count": row[2] or 0,
            "processing_count": row[3] or 0,
            "reviewed_count": row[4] or 0,
            "rejected_count": row[5] or 0,
            "archived_count": row[6] or 0,
            "avg_process_time_hours": row[7]
        }
    finally:
        close_db_connection(db_connection)

@router.get("/sla/violations", response_model=dict, summary="SLA 违规告警")
async def sla_violations_api(
    current_user: dict = Depends(get_current_user_info),
    _: None = Depends(PermissionChecker("order", "read"))
):
    """
    获取 SLA 违规的工单
    
    权限要求: order:read (dispatcher/auditor)
    """
    db_connection = get_db_connection()
    try:
        violations = get_sla_violations(db_connection)
        return {
            "status": "success",
            "count": len(violations),
            "items": violations
        }
    finally:
        close_db_connection(db_connection)

# =====================================================
# 批量操作 API
# =====================================================

@router.post("/batch/assign", response_model=dict, summary="批量派单")
async def batch_assign_api(
    order_ids: List[int],
    assigned_user_id: int,
    remark: Optional[str] = None,
    request: Request = None,
    current_user: dict = Depends(get_current_user_info),
    _: None = Depends(PermissionChecker("order", "batch_assign"))
):
    """
    批量派单
    
    权限要求: order:batch_assign (dispatcher)
    """
    db_connection = get_db_connection()
    try:
        success_count = 0
        failed_count = 0
        errors = []
        
        for order_id in order_ids[:100]:  # 限制最多 100 个
            try:
                assign_order(
                    order_id=order_id,
                    assigned_user_id=assigned_user_id,
                    remark=remark or "",
                    operator_id=current_user['user_id'],
                    db_connection=db_connection,
                    ip_address=request.client.host if request and request.client else None
                )
                success_count += 1
            except ValueError as e:
                failed_count += 1
                errors.append(f"工单 {order_id}: {str(e)}")
        
        return {
            "status": "success",
            "message": f"批量派单完成: 成功 {success_count} 个, 失败 {failed_count} 个",
            "success_count": success_count,
            "failed_count": failed_count,
            "errors": errors[:10]  # 仅返回前 10 个错误
        }
    finally:
        close_db_connection(db_connection)

