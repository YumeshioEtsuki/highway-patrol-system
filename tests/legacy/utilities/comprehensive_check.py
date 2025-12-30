#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面系统检查脚本
检查数据库、配置、依赖、API等所有关键组件
"""

import sys
import os

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(project_root, '1-后端代码')
sys.path.insert(0, backend_dir)

import requests
import time
from utils.utils import get_db_connection

def check_database():
    """检查数据库连接和表结构"""
    print("\n" + "="*60)
    print("1. DATABASE CHECK")
    print("="*60)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 检查表
        cursor.execute('SHOW TABLES')
        tables = cursor.fetchall()
        table_names = [list(table.values())[0] for table in tables]
        
        print(f"✓ Database connected successfully")
        print(f"✓ Found {len(table_names)} tables: {', '.join(table_names)}")
        
        # 检查每个表的数据量
        table_counts = {}
        for table_name in table_names:
            cursor.execute(f'SELECT COUNT(*) as cnt FROM {table_name}')
            count = cursor.fetchone()['cnt']
            table_counts[table_name] = count
            
        print("\nTable record counts:")
        for table, count in table_counts.items():
            status = "✓" if count > 0 else "⚠"
            print(f"  {status} {table}: {count} records")
        
        # 检查关键字段
        print("\nChecking critical fields...")
        cursor.execute("SHOW COLUMNS FROM user")
        user_columns = [col['Field'] for col in cursor.fetchall()]
        print(f"  ✓ User table columns: {', '.join(user_columns)}")
        
        cursor.execute("SHOW COLUMNS FROM inspectionrecord")
        record_columns = [col['Field'] for col in cursor.fetchall()]
        print(f"  ✓ InspectionRecord columns: {', '.join(record_columns)}")
        
        cursor.close()
        conn.close()
        
        return True, table_counts
        
    except Exception as e:
        print(f"✗ Database check failed: {e}")
        return False, {}

def check_api_server():
    """检查API服务器状态"""
    print("\n" + "="*60)
    print("2. API SERVER CHECK")
    print("="*60)
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        # 健康检查
        resp = requests.get(f"{base_url}/health", timeout=5)
        if resp.status_code == 200:
            print(f"✓ Server is running at {base_url}")
        else:
            print(f"⚠ Server returned status {resp.status_code}")
            
        # 检查文档
        resp = requests.get(f"{base_url}/docs", timeout=5)
        if resp.status_code == 200:
            print(f"✓ API documentation available at {base_url}/docs")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to server at {base_url}")
        print("  Please start the server: python -m uvicorn app:app --port 5000")
        return False
    except Exception as e:
        print(f"✗ API server check failed: {e}")
        return False

def check_authentication():
    """检查认证功能"""
    print("\n" + "="*60)
    print("3. AUTHENTICATION CHECK")
    print("="*60)
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        # 测试登录 - 使用 JSON 格式
        resp = requests.post(
            f"{base_url}/api/login",
            json={"username": "admin", "password": "REDACTED"},  # ← 改为 json 参数
            timeout=5
        )
        
        if resp.status_code == 200:
            data = resp.json()
            if 'access_token' in data:
                print("✓ Login successful (admin/REDACTED)")
                token = data['access_token']
                
                # 测试token验证
                headers = {"Authorization": f"Bearer {token}"}
                resp = requests.get(f"{base_url}/api/me", headers=headers, timeout=5)
                
                if resp.status_code == 200:
                    user_data = resp.json()
                    print(f"✓ Token validation successful")
                    print(f"  User: {user_data.get('username')}, Role: {user_data.get('role')}")
                    return True, token
                else:
                    print(f"⚠ Token validation failed: {resp.status_code}")
            else:
                print(f"⚠ Login response missing access_token")
        elif resp.status_code == 401:
            print(f"✗ Login failed: Invalid credentials")
            print(f"  Please check admin password or run database reset")
        else:
            print(f"✗ Login failed with status {resp.status_code}: {resp.text}")
            
        return False, None
        
    except Exception as e:
        print(f"✗ Authentication check failed: {e}")
        return False, None

def check_admin_apis(token):
    """检查管理员API功能"""
    print("\n" + "="*60)
    print("4. ADMIN API CHECK")
    print("="*60)
    
    base_url = "http://127.0.0.1:5000"
    headers = {"Authorization": f"Bearer {token}"}
    
    results = {}
    
    # 测试查询接口
    try:
        resp = requests.get(
            f"{base_url}/api/admin/patrol/list",
            headers=headers,
            timeout=10
        )
        if resp.status_code == 200:
            records = resp.json()
            print(f"✓ GET /api/admin/patrol/list - {len(records)} records")
            results['patrol_list'] = True
        else:
            print(f"✗ GET /api/admin/patrol/list - Status {resp.status_code}")
            results['patrol_list'] = False
    except Exception as e:
        print(f"✗ patrol/list failed: {e}")
        results['patrol_list'] = False
    
    # 测试导出接口（不实际下载）
    try:
        resp = requests.get(
            f"{base_url}/api/export/excel",
            headers=headers,
            timeout=30,
            stream=True
        )
        if resp.status_code == 200:
            size = len(resp.content)
            print(f"✓ GET /api/export/excel - {size} bytes")
            results['export'] = True
        else:
            print(f"✗ GET /api/export/excel - Status {resp.status_code}")
            results['export'] = False
    except Exception as e:
        print(f"✗ export/excel failed: {e}")
        results['export'] = False
    
    return results

def check_file_structure():
    """检查文件结构"""
    print("\n" + "="*60)
    print("5. FILE STRUCTURE CHECK")
    print("="*60)
    
    # 使用项目根目录
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    required_files = [
        "1-后端代码/app.py",
        "1-后端代码/requirements.txt",
        "1-后端代码/models/tasks.py",
        "1-后端代码/routes/admin.py",
        "1-后端代码/utils/utils.py",
        "3-数据库/create_database.sql",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║     COMPREHENSIVE SYSTEM CHECK                           ║
║     Highway Patrol System Diagnostic Tool                ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    results = {
        'database': False,
        'api_server': False,
        'authentication': False,
        'admin_apis': {},
        'file_structure': False
    }
    
    # 1. 文件结构检查
    results['file_structure'] = check_file_structure()
    
    # 2. 数据库检查
    results['database'], table_counts = check_database()
    
    # 3. API服务器检查
    results['api_server'] = check_api_server()
    
    if results['api_server']:
        # 4. 认证检查
        results['authentication'], token = check_authentication()
        
        if results['authentication'] and token:
            # 5. 管理员API检查
            results['admin_apis'] = check_admin_apis(token)
    
    # 生成总结报告
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    all_passed = True
    
    print(f"\n{'✓' if results['file_structure'] else '✗'} File Structure")
    print(f"{'✓' if results['database'] else '✗'} Database Connection")
    print(f"{'✓' if results['api_server'] else '✗'} API Server")
    print(f"{'✓' if results['authentication'] else '✗'} Authentication")
    
    if results['admin_apis']:
        admin_passed = all(results['admin_apis'].values())
        print(f"{'✓' if admin_passed else '⚠'} Admin APIs ({sum(results['admin_apis'].values())}/{len(results['admin_apis'])} passed)")
        all_passed = all_passed and admin_passed
    
    all_passed = all_passed and all([
        results['file_structure'],
        results['database'],
        results['api_server'],
        results['authentication']
    ])
    
    # 诊断建议
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    if not results['database']:
        print("\n⚠ DATABASE ISSUE:")
        print("  Run: mysql -u root -p < 3-数据库/create_database.sql")
        
    if results['database'] and table_counts:
        empty_tables = [t for t, c in table_counts.items() if c == 0]
        if empty_tables:
            print(f"\n⚠ EMPTY TABLES DETECTED: {', '.join(empty_tables)}")
            print("  Solution: Login as admin and run '完整重置（含测试数据）'")
    
    if not results['api_server']:
        print("\n⚠ SERVER NOT RUNNING:")
        print("  Start with: cd 1-后端代码 && python -m uvicorn app:app --port 5000")
    
    if not results['authentication']:
        print("\n⚠ AUTHENTICATION FAILED:")
        print("  Check admin password or reset database")
    
    print("\n" + "="*60)
    if all_passed:
        print("✓✓✓ ALL CHECKS PASSED ✓✓✓")
    else:
        print("⚠⚠⚠ ISSUES FOUND - SEE RECOMMENDATIONS ABOVE ⚠⚠⚠")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
