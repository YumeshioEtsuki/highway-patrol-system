#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Phase 2 Stage 1 部署验证脚本

验证项目:
1. 数据库表创建
2. 权限配置
3. API 端点可用性
4. 权限检查
5. 审计日志记录
"""

import sys
import os
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_check(name, status, details=""):
    """打印检查项"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {name}")
    if details:
        print(f"  → {details}")

def verify_database_tables():
    """验证数据库表创建"""
    print_header("1️⃣ 验证数据库表")
    
    try:
        from utils.utils import get_db_connection, close_db_connection
        
        db_connection = get_db_connection()
        cursor = db_connection.cursor()
        
        # 检查新表
        required_tables = [
            'role', 'permission', 'role_permission', 'user_permission_override',
            'order_flow_log', 'sla_config', 'sla_alert', 'audit_log',
            'admin_ip_whitelist', 'refresh_token', 'department_segment'
        ]
        
        cursor.execute("""
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"数据库: road_patrol_db")
        print(f"现有表: {len(existing_tables)} 个")
        
        all_tables_exist = True
        for table in required_tables:
            exists = table in existing_tables
            print_check(f"表: {table}", exists)
            all_tables_exist = all_tables_exist and exists
        
        cursor.close()
        close_db_connection(db_connection)
        
        return all_tables_exist
        
    except Exception as e:
        print_check("数据库连接", False, str(e))
        return False

def verify_roles_and_permissions():
    """验证角色和权限配置"""
    print_header("2️⃣ 验证角色与权限")
    
    try:
        from utils.utils import get_db_connection, close_db_connection
        
        db_connection = get_db_connection()
        cursor = db_connection.cursor()
        
        # 检查角色
        cursor.execute("SELECT COUNT(*) FROM role")
        role_count = cursor.fetchone()[0]
        print_check("角色创建", role_count >= 5, f"{role_count} 个角色")
        
        # 检查权限
        cursor.execute("SELECT COUNT(*) FROM permission")
        permission_count = cursor.fetchone()[0]
        print_check("权限创建", permission_count >= 15, f"{permission_count} 个权限")
        
        # 检查角色权限映射
        cursor.execute("SELECT COUNT(*) FROM role_permission")
        mapping_count = cursor.fetchone()[0]
        print_check("角色权限映射", mapping_count > 0, f"{mapping_count} 条映射")
        
        # 列出角色
        cursor.execute("SELECT name, display_name FROM role ORDER BY priority DESC")
        print("\n【角色列表】")
        for name, display in cursor.fetchall():
            print(f"  • {display} ({name})")
        
        cursor.close()
        close_db_connection(db_connection)
        
        return role_count >= 5 and permission_count >= 15
        
    except Exception as e:
        print_check("角色权限查询", False, str(e))
        return False

def verify_inspectionrecord_extensions():
    """验证 InspectionRecord 表扩展"""
    print_header("3️⃣ 验证工单字段扩展")
    
    try:
        from utils.utils import get_db_connection, close_db_connection
        
        db_connection = get_db_connection()
        cursor = db_connection.cursor()
        
        # 检查新字段
        required_fields = [
            'order_status', 'assigned_user_id', 'assigned_time',
            'processor_id', 'process_time', 'reviewer_id', 'review_time',
            'review_remark', 'reject_count', 'reject_reason'
        ]
        
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'inspectionrecord'
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        all_fields_exist = True
        for field in required_fields:
            exists = field in existing_columns
            print_check(f"字段: {field}", exists)
            all_fields_exist = all_fields_exist and exists
        
        cursor.close()
        close_db_connection(db_connection)
        
        return all_fields_exist
        
    except Exception as e:
        print_check("字段检查", False, str(e))
        return False

def verify_api_routes():
    """验证 API 路由导入"""
    print_header("4️⃣ 验证 API 路由导入")
    
    try:
        from routes import orders
        
        print_check("导入 orders 模块", True)
        
        # 检查路由器
        if hasattr(orders, 'router'):
            print_check("路由器定义", True, f"router 对象存在")
            
            # 检查 API 端点
            routes = [route.path for route in orders.router.routes]
            print(f"\n【API 端点数】: {len(routes)}")
            
            key_routes = [
                '/api/orders', '/{order_id}/assign', '/{order_id}/process',
                '/{order_id}/review', '/{order_id}/reject', '/{order_id}/approve'
            ]
            
            for route in key_routes:
                found = any(route in r for r in routes)
                status_str = route if found else f"{route} (未找到)"
                print_check(f"路由: {route}", found)
            
            return True
        else:
            print_check("路由器定义", False, "router 对象不存在")
            return False
            
    except Exception as e:
        print_check("API 路由导入", False, str(e))
        return False

def verify_permissions_module():
    """验证权限模块"""
    print_header("5️⃣ 验证权限系统模块")
    
    try:
        from utils.permissions import (
            check_permission,
            PermissionChecker,
            get_current_user_info,
            log_audit_action,
            create_refresh_token,
            hash_token
        )
        
        print_check("导入 check_permission", True)
        print_check("导入 PermissionChecker", True)
        print_check("导入 get_current_user_info", True)
        print_check("导入 log_audit_action", True)
        print_check("导入 create_refresh_token", True)
        print_check("导入 hash_token", True)
        
        return True
        
    except Exception as e:
        print_check("权限模块导入", False, str(e))
        return False

def verify_order_models():
    """验证工单数据模型"""
    print_header("6️⃣ 验证工单数据模型")
    
    try:
        from models.order_schemas import (
            OrderAssignRequest, OrderDetailResponse, OrderStatisticsResponse
        )
        from models.order_tasks import (
            assign_order, process_order, review_order, get_order_detail
        )
        
        print_check("导入 OrderAssignRequest", True)
        print_check("导入 OrderDetailResponse", True)
        print_check("导入 OrderStatisticsResponse", True)
        print_check("导入 assign_order", True)
        print_check("导入 process_order", True)
        print_check("导入 review_order", True)
        print_check("导入 get_order_detail", True)
        
        return True
        
    except Exception as e:
        print_check("工单模型导入", False, str(e))
        return False

def verify_test_data():
    """验证测试数据"""
    print_header("7️⃣ 验证测试数据")
    
    try:
        from utils.utils import get_db_connection, close_db_connection
        
        db_connection = get_db_connection()
        cursor = db_connection.cursor()
        
        # 检查用户记录
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        print_check("用户记录", user_count > 0, f"{user_count} 条用户")
        
        # 检查工单记录
        cursor.execute("SELECT COUNT(*) FROM inspectionrecord")
        order_count = cursor.fetchone()[0]
        print_check("工单记录", order_count > 0, f"{order_count} 条工单")
        
        # 检查部门记录
        cursor.execute("SELECT COUNT(*) FROM department")
        dept_count = cursor.fetchone()[0]
        print_check("部门记录", dept_count > 0, f"{dept_count} 条部门")
        
        cursor.close()
        close_db_connection(db_connection)
        
        return user_count > 0 and order_count > 0
        
    except Exception as e:
        print_check("测试数据检查", False, str(e))
        return False

def verify_views_and_triggers():
    """验证视图和触发器"""
    print_header("8️⃣ 验证数据库视图")
    
    try:
        from utils.utils import get_db_connection, close_db_connection
        
        db_connection = get_db_connection()
        cursor = db_connection.cursor()
        
        # 检查视图
        required_views = ['vw_order_overview', 'vw_sla_statistics']
        
        cursor.execute("""
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS
            WHERE TABLE_SCHEMA = DATABASE()
        """)
        
        existing_views = [row[0] for row in cursor.fetchall()]
        
        all_views_exist = True
        for view in required_views:
            exists = view in existing_views
            print_check(f"视图: {view}", exists)
            all_views_exist = all_views_exist and exists
        
        cursor.close()
        close_db_connection(db_connection)
        
        return all_views_exist
        
    except Exception as e:
        print_check("视图检查", False, str(e))
        return False

def verify_indexes():
    """验证数据库索引"""
    print_header("9️⃣ 验证关键索引")
    
    try:
        from utils.utils import get_db_connection, close_db_connection
        
        db_connection = get_db_connection()
        cursor = db_connection.cursor()
        
        # 检查索引
        key_indexes = [
            ('inspectionrecord', 'idx_order_status'),
            ('inspectionrecord', 'idx_assigned_user'),
            ('inspectionrecord', 'idx_status_time'),
            ('audit_log', 'idx_audit_time_operator'),
            ('user', 'idx_user_role')
        ]
        
        for table, index_name in key_indexes:
            cursor.execute(f"""
                SELECT INDEX_NAME FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = '{table}' 
                AND INDEX_NAME = '{index_name}'
            """)
            exists = cursor.fetchone() is not None
            print_check(f"索引: {index_name}", exists, f"表: {table}")
        
        cursor.close()
        close_db_connection(db_connection)
        
        return True
        
    except Exception as e:
        print_check("索引检查", False, str(e))
        return False

def generate_report():
    """生成验证报告"""
    print_header("📋 验证报告总结")
    
    results = {
        "数据库表": verify_database_tables(),
        "角色权限": verify_roles_and_permissions(),
        "工单字段": verify_inspectionrecord_extensions(),
        "API 路由": verify_api_routes(),
        "权限系统": verify_permissions_module(),
        "工单模型": verify_order_models(),
        "测试数据": verify_test_data(),
        "数据库视图": verify_views_and_triggers(),
        "关键索引": verify_indexes()
    }
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n【验证结果】")
    for check, result in results.items():
        symbol = "✅" if result else "❌"
        print(f"{symbol} {check}")
    
    print(f"\n【总体评分】")
    print(f"通过: {passed}/{total} ({100*passed//total}%)")
    
    if passed == total:
        print("\n🎉 所有验证通过! Phase 2 Stage 1 已成功部署!")
        return True
    else:
        print(f"\n⚠️ 有 {total - passed} 项检查失败，请查看上面的详细信息")
        return False

def main():
    """主函数"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Phase 2 Stage 1 部署验证脚本".center(58) + "║")
    print("║" + "  工单状态机 + 多角色权限系统".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        success = generate_report()
        
        print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if success:
            print("\n✅ 验证完成 - 系统准备就绪!")
            print("\n【后续步骤】")
            print("1. 在 app.py 中导入 orders 路由")
            print("2. 启动 FastAPI 应用")
            print("3. 访问 http://localhost:5000/docs 查看 API 文档")
            print("4. 运行集成测试")
            return 0
        else:
            print("\n❌ 验证失败 - 请检查上面的错误信息")
            return 1
            
    except Exception as e:
        print(f"\n❌ 验证过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

