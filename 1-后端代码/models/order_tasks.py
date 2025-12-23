# =====================================================
# Phase 2 Stage 1: 工单管理数据库操作
# =====================================================

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from models.order_schemas import (
    OrderAssignRequest, OrderProcessRequest, OrderReviewRequest,
    OrderRejectRequest, OrderReviewApproveRequest, OrderArchiveRequest,
    OrderListResponse, OrderDetailResponse, OrderFlowLogResponse
)

# =====================================================
# 工单状态转换
# =====================================================

def assign_order(order_id: int, assigned_user_id: int, remark: str, operator_id: int, 
                 db_connection, ip_address: str = None) -> bool:
    """
    派单 (new -> assigned)
    
    Args:
        order_id: 工单ID
        assigned_user_id: 派单给用户ID
        remark: 备注
        operator_id: 操作人ID
        db_connection: 数据库连接
        ip_address: 操作IP
    
    Returns:
        bool: 是否成功
    """
    try:
        cursor = db_connection.cursor()
        
        # 检查工单状态
        cursor.execute(
            "SELECT order_status FROM inspectionrecord WHERE id = %s",
            (order_id,)
        )
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"工单 {order_id} 不存在")
        
        old_status = result[0]
        if old_status not in ['new', 'rejected']:  # 新建或驳回状态可以派单
            raise ValueError(f"工单状态 {old_status} 不能派单")
        
        # 更新工单状态
        cursor.execute("""
            UPDATE inspectionrecord SET 
                order_status = 'assigned',
                assigned_user_id = %s,
                assigned_time = NOW()
            WHERE id = %s
        """, (assigned_user_id, order_id))
        
        # 记录流转日志
        cursor.execute("""
            INSERT INTO order_flow_log (
                order_id, old_status, new_status, operator_id, operator_role,
                operation, remark, operation_time, ip_address
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
        """, (
            order_id, old_status, 'assigned', operator_id, 'dispatcher',
            'assign', remark, ip_address
        ))
        
        db_connection.commit()
        cursor.close()
        return True
        
    except Exception as e:
        db_connection.rollback()
        raise ValueError(f"派单失败: {str(e)}")

def process_order(order_id: int, processor_id: int, remark: str, operator_id: int,
                  db_connection, ip_address: str = None) -> bool:
    """
    标记处理中 (assigned -> processing)
    """
    try:
        cursor = db_connection.cursor()
        
        # 检查状态
        cursor.execute(
            "SELECT order_status FROM inspectionrecord WHERE id = %s",
            (order_id,)
        )
        result = cursor.fetchone()
        if not result or result[0] != 'assigned':
            raise ValueError("工单必须处于 'assigned' 状态")
        
        # 更新状态
        cursor.execute("""
            UPDATE inspectionrecord SET 
                order_status = 'processing',
                processor_id = %s,
                process_time = NOW()
            WHERE id = %s
        """, (processor_id, order_id))
        
        # 记录日志
        cursor.execute("""
            INSERT INTO order_flow_log (
                order_id, old_status, new_status, operator_id, operator_role,
                operation, remark, operation_time, ip_address
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
        """, (
            order_id, 'assigned', 'processing', operator_id, 'processor',
            'process', remark, ip_address
        ))
        
        db_connection.commit()
        cursor.close()
        return True
        
    except Exception as e:
        db_connection.rollback()
        raise ValueError(f"标记处理失败: {str(e)}")

def review_order(order_id: int, reviewer_id: int, review_remark: str, operator_id: int,
                 db_connection, ip_address: str = None) -> bool:
    """
    提交审核 (processing -> reviewed)
    """
    try:
        cursor = db_connection.cursor()
        
        cursor.execute(
            "SELECT order_status FROM inspectionrecord WHERE id = %s",
            (order_id,)
        )
        result = cursor.fetchone()
        if not result or result[0] != 'processing':
            raise ValueError("工单必须处于 'processing' 状态")
        
        cursor.execute("""
            UPDATE inspectionrecord SET 
                order_status = 'reviewed',
                reviewer_id = %s,
                review_time = NOW(),
                review_remark = %s
            WHERE id = %s
        """, (reviewer_id, review_remark, order_id))
        
        cursor.execute("""
            INSERT INTO order_flow_log (
                order_id, old_status, new_status, operator_id, operator_role,
                operation, remark, operation_time, ip_address
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
        """, (
            order_id, 'processing', 'reviewed', operator_id, 'auditor',
            'review', review_remark, ip_address
        ))
        
        db_connection.commit()
        cursor.close()
        return True
        
    except Exception as e:
        db_connection.rollback()
        raise ValueError(f"提交审核失败: {str(e)}")

def reject_order(order_id: int, reject_reason: str, reviewer_id: int, operator_id: int,
                 db_connection, ip_address: str = None) -> bool:
    """
    驳回工单 (processing/reviewed -> rejected)
    """
    try:
        cursor = db_connection.cursor()
        
        cursor.execute(
            "SELECT order_status, reject_count FROM inspectionrecord WHERE id = %s",
            (order_id,)
        )
        result = cursor.fetchone()
        if not result or result[0] not in ['processing', 'reviewed']:
            raise ValueError("工单不能在当前状态驳回")
        
        reject_count = (result[1] or 0) + 1
        
        cursor.execute("""
            UPDATE inspectionrecord SET 
                order_status = 'rejected',
                reject_reason = %s,
                reject_count = %s,
                reviewer_id = %s,
                review_time = NOW()
            WHERE id = %s
        """, (reject_reason, reject_count, reviewer_id, order_id))
        
        cursor.execute("""
            INSERT INTO order_flow_log (
                order_id, old_status, new_status, operator_id, operator_role,
                operation, remark, operation_time, ip_address
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
        """, (
            order_id, result[0], 'rejected', operator_id, 'auditor',
            'reject', reject_reason, ip_address
        ))
        
        db_connection.commit()
        cursor.close()
        return True
        
    except Exception as e:
        db_connection.rollback()
        raise ValueError(f"驳回失败: {str(e)}")

def archive_order(order_id: int, operator_id: int, remark: str,
                  db_connection, ip_address: str = None) -> bool:
    """
    归档工单 (reviewed -> archived)
    """
    try:
        cursor = db_connection.cursor()
        
        cursor.execute(
            "SELECT order_status FROM inspectionrecord WHERE id = %s",
            (order_id,)
        )
        result = cursor.fetchone()
        if not result or result[0] != 'reviewed':
            raise ValueError("只能归档已审核的工单")
        
        cursor.execute("""
            UPDATE inspectionrecord SET 
                order_status = 'archived'
            WHERE id = %s
        """, (order_id,))
        
        cursor.execute("""
            INSERT INTO order_flow_log (
                order_id, old_status, new_status, operator_id, operator_role,
                operation, remark, operation_time, ip_address
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
        """, (
            order_id, 'reviewed', 'archived', operator_id, 'admin',
            'archive', remark, ip_address
        ))
        
        db_connection.commit()
        cursor.close()
        return True
        
    except Exception as e:
        db_connection.rollback()
        raise ValueError(f"归档失败: {str(e)}")

# =====================================================
# 工单查询
# =====================================================

def get_order_detail(order_id: int, db_connection) -> Optional[Dict[str, Any]]:
    """
    获取工单详情
    """
    try:
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT 
                ir.id, ir.order_status, ir.description, ir.upload_time,
                ir.assigned_time, ir.process_time, ir.review_time,
                u_creator.real_name, u_assigned.real_name, u_processor.real_name, u_reviewer.real_name,
                pt.name, d.name, rs.name, ir.reject_count, ir.reject_reason, ir.review_remark
            FROM inspectionrecord ir
            LEFT JOIN user u_creator ON ir.user_id = u_creator.user_id
            LEFT JOIN user u_assigned ON ir.assigned_user_id = u_assigned.user_id
            LEFT JOIN user u_processor ON ir.processor_id = u_processor.user_id
            LEFT JOIN user u_reviewer ON ir.reviewer_id = u_reviewer.user_id
            LEFT JOIN problemtype pt ON ir.problem_id = pt.id
            LEFT JOIN roadsegment rs ON ir.road_id = rs.id
            LEFT JOIN department d ON rs.department_id = d.id
            WHERE ir.id = %s
        """, (order_id,))
        
        result = cursor.fetchone()
        if not result:
            return None
        
        # 获取流转日志
        cursor.execute("""
            SELECT id, old_status, new_status, operator_id, operator_role,
                   operation, remark, operation_time, ip_address
            FROM order_flow_log
            WHERE order_id = %s
            ORDER BY operation_time ASC
        """, (order_id,))
        
        flow_logs = [
            {
                'id': row[0],
                'old_status': row[1],
                'new_status': row[2],
                'operator_id': row[3],
                'operator_role': row[4],
                'operation': row[5],
                'remark': row[6],
                'operation_time': row[7],
                'ip_address': row[8]
            }
            for row in cursor.fetchall()
        ]
        
        cursor.close()
        
        return {
            'id': result[0],
            'order_status': result[1],
            'description': result[2],
            'upload_time': result[3],
            'assigned_time': result[4],
            'process_time': result[5],
            'review_time': result[6],
            'creator_name': result[7],
            'assigned_by': result[8],
            'processor_name': result[9],
            'reviewer_name': result[10],
            'problem_type': result[11],
            'department': result[12],
            'road_segment': result[13],
            'reject_count': result[14],
            'reject_reason': result[15],
            'review_remark': result[16],
            'flow_logs': flow_logs
        }
        
    except Exception as e:
        print(f"获取工单详情失败: {str(e)}")
        return None

def list_orders(
    user_id: int,
    role: str,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db_connection = None
) -> Tuple[List[Dict], int]:
    """
    列出工单 (支持基于角色的行权过滤)
    
    Args:
        user_id: 当前用户ID
        role: 用户角色
        status: 工单状态过滤
        limit: 分页大小
        offset: 分页偏移
        db_connection: 数据库连接
    
    Returns:
        (orders, total_count)
    """
    try:
        cursor = db_connection.cursor()
        
        # 根据角色构建查询条件
        role_filter = ""
        if role == "inspector":
            role_filter = f"AND ir.user_id = {user_id}"  # 仅查看自己的记录
        elif role == "dispatcher":
            role_filter = ""  # 查看所有未派单的
        elif role == "processor":
            role_filter = f"AND ir.assigned_user_id = {user_id}"  # 查看派给自己的
        elif role == "auditor":
            role_filter = ""  # 查看所有审核中的
        elif role == "admin":
            role_filter = ""  # 管理员看全部
        
        status_filter = f"AND ir.order_status = '{status}'" if status else ""
        
        # 获取总数
        cursor.execute(f"""
            SELECT COUNT(*) FROM inspectionrecord ir
            WHERE 1=1 {role_filter} {status_filter}
        """)
        total = cursor.fetchone()[0]
        
        # 获取分页数据
        cursor.execute(f"""
            SELECT 
                ir.id, ir.order_status, ir.description, ir.upload_time,
                ir.assigned_time, ir.process_time, ir.review_time,
                u_creator.real_name, u_assigned.real_name, u_processor.real_name, u_reviewer.real_name,
                pt.name, d.name, rs.name, ir.reject_count
            FROM inspectionrecord ir
            LEFT JOIN user u_creator ON ir.user_id = u_creator.user_id
            LEFT JOIN user u_assigned ON ir.assigned_user_id = u_assigned.user_id
            LEFT JOIN user u_processor ON ir.processor_id = u_processor.user_id
            LEFT JOIN user u_reviewer ON ir.reviewer_id = u_reviewer.user_id
            LEFT JOIN problemtype pt ON ir.problem_id = pt.id
            LEFT JOIN roadsegment rs ON ir.road_id = rs.id
            LEFT JOIN department d ON rs.department_id = d.id
            WHERE 1=1 {role_filter} {status_filter}
            ORDER BY ir.upload_time DESC
            LIMIT {limit} OFFSET {offset}
        """)
        
        orders = [
            {
                'id': row[0],
                'order_status': row[1],
                'description': row[2],
                'upload_time': row[3],
                'assigned_time': row[4],
                'process_time': row[5],
                'review_time': row[6],
                'creator_name': row[7],
                'assigned_by': row[8],
                'processor_name': row[9],
                'reviewer_name': row[10],
                'problem_type': row[11],
                'department': row[12],
                'road_segment': row[13],
                'reject_count': row[14]
            }
            for row in cursor.fetchall()
        ]
        
        cursor.close()
        return orders, total
        
    except Exception as e:
        print(f"查询工单列表失败: {str(e)}")
        return [], 0

# =====================================================
# SLA 管理
# =====================================================

def get_sla_violations(db_connection, hours: int = 24) -> List[Dict]:
    """
    获取 SLA 违规工单
    """
    try:
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT ir.id, ir.description, ir.upload_time, sc.dispatch_sla_hours,
                   sc.process_sla_hours, sc.review_sla_hours, sc.total_sla_hours,
                   ir.assigned_time, ir.process_time, ir.review_time
            FROM inspectionrecord ir
            JOIN problemtype pt ON ir.problem_id = pt.id
            JOIN sla_config sc ON pt.id = sc.problem_type_id
            WHERE ir.order_status NOT IN ('archived', 'rejected')
            AND (
                (ir.assigned_time IS NULL AND TIMESTAMPDIFF(HOUR, ir.upload_time, NOW()) > sc.dispatch_sla_hours)
                OR (ir.process_time IS NULL AND ir.assigned_time IS NOT NULL 
                    AND TIMESTAMPDIFF(HOUR, ir.assigned_time, NOW()) > sc.process_sla_hours)
                OR (ir.review_time IS NULL AND ir.process_time IS NOT NULL
                    AND TIMESTAMPDIFF(HOUR, ir.process_time, NOW()) > sc.review_sla_hours)
            )
        """)
        
        violations = [
            {
                'order_id': row[0],
                'description': row[1],
                'upload_time': row[2],
                'sla_hours': {
                    'dispatch': row[3],
                    'process': row[4],
                    'review': row[5],
                    'total': row[6]
                }
            }
            for row in cursor.fetchall()
        ]
        
        cursor.close()
        return violations
        
    except Exception as e:
        print(f"获取 SLA 违规失败: {str(e)}")
        return []

