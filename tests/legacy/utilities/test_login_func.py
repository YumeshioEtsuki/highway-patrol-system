#!/usr/bin/env python3
"""直接测试 user_login_by_password"""
import sys
sys.path.insert(0, 'd:\\MySQL Project\\highway-patrol-system\\1-后端代码')

try:
    from services.patrol_service import user_login_by_password
    print("✓ 成功导入 user_login_by_password")
    
    user = user_login_by_password('admin', 'admin')
    print(f"结果: {user}")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
