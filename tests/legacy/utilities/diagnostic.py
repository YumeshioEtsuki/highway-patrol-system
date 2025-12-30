#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面系统诊断脚本 - 识别所有前后端问题
"""
import subprocess
import time
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8001"
ISSUES = []

def log_issue(severity, category, problem, solution):
    """记录问题"""
    ISSUES.append({
        "severity": severity,  # CRITICAL, ERROR, WARNING
        "category": category,  # Backend, Frontend, Integration, Performance
        "problem": problem,
        "solution": solution
    })
    print(f"[{severity:8}] {category:12} | {problem}")

def test_backend_endpoints():
    """测试后端所有端点"""
    print("\n" + "="*70)
    print("🔍 后端端点诊断")
    print("="*70)
    
    # 1. 登录
    print("\n[1] 测试登录端点")
    try:
        res = requests.post(f"{BASE_URL}/api/login", 
            json={"username": "admin", "password": "REDACTED"},
            timeout=5)
        print(f"  Status: {res.status_code}")
        if res.status_code != 200:
            log_issue("ERROR", "Backend", 
                f"Login failed: {res.status_code}", 
                "检查数据库连接和密码哈希")
            return None
        data = res.json()
        token = data.get("access_token")
        print(f"  ✅ 登录成功")
        return token
    except Exception as e:
        log_issue("CRITICAL", "Backend", 
            f"登录端点异常: {str(e)}", 
            "检查服务器是否运行")
        return None

def test_api_endpoints(token):
    """测试所有 API 端点"""
    endpoints = [
        ("GET", "/api/me", {}, "获取当前用户信息"),
        ("GET", "/api/road-segments", {}, "获取路段列表"),
        ("GET", "/api/issue-types", {}, "获取问题类型"),
        ("GET", "/api/patrol", {}, "获取巡查记录"),
        ("GET", "/api/admin/patrol/list", {}, "获取管理员记录列表"),
    ]
    
    print("\n[2] 测试 API 端点")
    for method, path, params, desc in endpoints:
        try:
            if method == "GET":
                res = requests.get(f"{BASE_URL}{path}",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5)
            print(f"  {method:4} {path:30} | {res.status_code:3} | {desc}")
            
            if res.status_code >= 400:
                error_msg = res.text[:100]
                log_issue("ERROR", "Backend",
                    f"Endpoint {path} returns {res.status_code}",
                    f"检查权限或实现: {error_msg}")
        except Exception as e:
            log_issue("ERROR", "Backend",
                f"Endpoint {path} 异常: {str(e)}",
                "检查网络连接或服务器")

def test_sse_endpoints(token):
    """测试 SSE 流式端点"""
    print("\n[3] 测试 SSE 流式端点")
    sse_endpoints = [
        "/api/verify/stream",
        "/api/status/stream",
        "/api/sse/patrol-photo",
    ]
    
    for endpoint in sse_endpoints:
        try:
            url = f"{BASE_URL}{endpoint}?token={token}"
            res = requests.get(url, stream=True, timeout=3)
            print(f"  {endpoint:30} | {res.status_code:3}", end="")
            
            if res.status_code == 200:
                # 读第一行
                for line in res.iter_lines(decode_unicode=True):
                    if line.strip():
                        print(f" | {line[:40]}")
                        break
                res.close()
            else:
                error = res.text[:80]
                print(f" | ❌ {error}")
                log_issue("ERROR", "Backend",
                    f"SSE {endpoint} returns {res.status_code}",
                    "检查认证处理和错误响应")
                res.close()
        except requests.exceptions.Timeout:
            print(f" | ⚠️  超时（可能是正常的长连接）")
        except Exception as e:
            print(f" | ❌ {str(e)[:40]}")
            log_issue("ERROR", "Backend",
                f"SSE {endpoint} 异常",
                str(e))

def test_frontend_files():
    """检查前端文件"""
    print("\n[4] 前端文件完整性检查")
    import os
    
    frontend_files = [
        "1-后端代码/templates/admin.html",
        "1-后端代码/templates/patrol.html",
        "1-后端代码/templates/index.html",
    ]
    
    for file_path in frontend_files:
        full_path = f"d:\\MySQL Project\\highway-patrol-system\\{file_path}"
        exists = os.path.exists(full_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
        if not exists:
            log_issue("ERROR", "Frontend",
                f"文件不存在: {file_path}",
                "创建缺失的模板文件")

def test_database_connectivity():
    """测试数据库连接"""
    print("\n[5] 数据库连接诊断")
    
    # 通过 /health 或 /docs 检查
    try:
        res = requests.get(f"{BASE_URL}/docs", timeout=5)
        if res.status_code == 200:
            print("  ✅ 应用服务运行中")
        else:
            print(f"  ❌ 应用返回 {res.status_code}")
    except Exception as e:
        log_issue("CRITICAL", "Backend",
            f"无法连接服务: {str(e)}",
            "检查服务器是否启动")

def print_summary():
    """打印诊断总结"""
    print("\n" + "="*70)
    print("📊 诊断总结")
    print("="*70)
    
    if not ISSUES:
        print("✅ 未发现问题！")
        return
    
    critical = [i for i in ISSUES if i["severity"] == "CRITICAL"]
    errors = [i for i in ISSUES if i["severity"] == "ERROR"]
    warnings = [i for i in ISSUES if i["severity"] == "WARNING"]
    
    print(f"\n🔴 严重问题: {len(critical)}")
    for issue in critical:
        print(f"  • {issue['problem']}")
        print(f"    → {issue['solution']}")
    
    print(f"\n🟠 错误: {len(errors)}")
    for issue in errors:
        print(f"  • {issue['category']}: {issue['problem']}")
        print(f"    → {issue['solution']}")
    
    print(f"\n🟡 警告: {len(warnings)}")
    for issue in warnings:
        print(f"  • {issue['problem']}")
    
    print(f"\n📋 总计: {len(ISSUES)} 个问题需要处理")

# ============================================================
# 主流程
# ============================================================
if __name__ == "__main__":
    print("🚀 开始全面系统诊断...")
    print(f"📍 目标服务: {BASE_URL}")
    
    # 测试数据库连接
    test_database_connectivity()
    
    # 登录
    token = test_backend_endpoints()
    
    if token:
        # 测试 API 端点
        test_api_endpoints(token)
        
        # 测试 SSE 端点
        test_sse_endpoints(token)
    
    # 检查文件
    test_frontend_files()
    
    # 打印总结
    print_summary()
    
    # 导出问题列表为 JSON
    if ISSUES:
        with open("d:\\MySQL Project\\highway-patrol-system\\diagnostic_report.json", "w", encoding="utf-8") as f:
            json.dump(ISSUES, f, ensure_ascii=False, indent=2)
        print("\n💾 详细报告已保存至: diagnostic_report.json")
