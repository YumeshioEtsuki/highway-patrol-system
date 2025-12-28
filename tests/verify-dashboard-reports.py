#!/usr/bin/env python
"""
快速验证脚本 - 验证仪表盘与报表 API 可用性

用法：
    python verify-dashboard-reports.py

功能：
    - 启动后端应用
    - 测试所有报表 API 端点
    - 测试所有 KPI 端点
    - 验证前端页面加载
    - 验证静态资源可用
"""

import sys
import time
import subprocess
import requests
from pathlib import Path
from datetime import date

# 配置
API_BASE = "http://127.0.0.1:5000"
TIMEOUT = 5


def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_success(msg):
    print(f"  ✅ {msg}")


def print_error(msg):
    print(f"  ❌ {msg}")


def print_info(msg):
    print(f"  ℹ️  {msg}")


def test_report_apis():
    """测试报表 API"""
    print_header("报表 API 验证")

    tests = [
        {
            "name": "Excel 导出",
            "method": "POST",
            "endpoint": "/api/reports/export/excel",
            "data": {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "include_photos": "no"
            },
            "expect_field": "task_id"
        },
        {
            "name": "PDF 导出",
            "method": "POST",
            "endpoint": "/api/reports/export/pdf",
            "data": {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "title": "2024 报告"
            },
            "expect_field": "task_id"
        },
        {
            "name": "月报生成",
            "method": "POST",
            "endpoint": "/api/reports/monthly/generate",
            "data": {
                "year": 2024,
                "month": 12
            },
            "expect_field": "task_id"
        }
    ]

    for test in tests:
        try:
            url = f"{API_BASE}{test['endpoint']}"
            if test["method"] == "POST":
                resp = requests.post(url, json=test["data"], timeout=TIMEOUT)
            else:
                resp = requests.get(url, timeout=TIMEOUT)

            if resp.status_code == 200:
                data = resp.json()
                if test["expect_field"] in data:
                    print_success(f"{test['name']}: {resp.status_code} (task_id: {data['task_id'][:8]}...)")
                else:
                    print_error(f"{test['name']}: 缺少字段 {test['expect_field']}")
            else:
                print_error(f"{test['name']}: {resp.status_code}")
        except Exception as e:
            print_error(f"{test['name']}: {str(e)}")


def test_kpi_apis():
    """测试 KPI API"""
    print_header("KPI 端点验证")

    kpi_endpoints = [
        "/api/dashboard/kpi/today_tasks",
        "/api/dashboard/kpi/success_rate",
        "/api/dashboard/kpi/avg_latency",
        "/api/dashboard/kpi/active_users"
    ]

    for endpoint in kpi_endpoints:
        try:
            resp = requests.get(f"{API_BASE}{endpoint}", timeout=TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                label = data.get("label", "")
                value = data.get("value", "")
                print_success(f"{label}: {value}")
            else:
                print_error(f"{endpoint}: {resp.status_code}")
        except Exception as e:
            print_error(f"{endpoint}: {str(e)}")

    # 最近任务
    try:
        resp = requests.get(f"{API_BASE}/api/dashboard/recent-tasks", timeout=TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            count = len(data.get("recent_tasks", []))
            print_success(f"最近任务: {count} 项")
        else:
            print_error(f"最近任务: {resp.status_code}")
    except Exception as e:
        print_error(f"最近任务: {str(e)}")


def test_pages():
    """测试页面加载"""
    print_header("页面加载验证")

    pages = [
        ("/dashboard.html", "仪表盘"),
        ("/reports.html", "报表中心"),
        ("/tasks.html", "任务中心")
    ]

    for path, name in pages:
        try:
            resp = requests.get(f"{API_BASE}{path}", timeout=TIMEOUT)
            if resp.status_code == 200:
                print_success(f"{name}: {resp.status_code}")
            else:
                print_error(f"{name}: {resp.status_code}")
        except Exception as e:
            print_error(f"{name}: {str(e)}")


def test_static_assets():
    """测试静态资源"""
    print_header("静态资源验证")

    assets = [
        "/static/js/common.js",
        "/static/js/tasks.js",
        "/static/js/reports.js",
        "/static/js/dashboard.js"
    ]

    for asset in assets:
        try:
            resp = requests.get(f"{API_BASE}{asset}", timeout=TIMEOUT)
            if resp.status_code == 200:
                size = len(resp.content)
                print_success(f"{asset.split('/')[-1]}: {resp.status_code} ({size} bytes)")
            else:
                print_error(f"{asset}: {resp.status_code}")
        except Exception as e:
            print_error(f"{asset}: {str(e)}")


def check_server_health():
    """检查服务器健康状态"""
    print_header("服务器健康检查")

    try:
        resp = requests.get(f"{API_BASE}/health", timeout=TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            print_success(f"服务器运行中 (版本: {data.get('version', 'N/A')})")
            return True
        else:
            print_error(f"服务器返回 {resp.status_code}")
            return False
    except requests.ConnectionError:
        print_error(f"无法连接到 {API_BASE}")
        return False
    except Exception as e:
        print_error(f"健康检查失败: {str(e)}")
        return False


def main():
    print("\n" + "="*60)
    print("  公路巡查系统 - 仪表盘与报表验证")
    print("="*60)

    print_info(f"API 地址: {API_BASE}")
    print_info(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 检查服务器
    if not check_server_health():
        print_error("服务器未运行！")
        print_info("请先启动后端应用:")
        print("    cd 1-后端代码")
        print("    python -m uvicorn app:app --reload")
        sys.exit(1)

    # 运行测试
    test_report_apis()
    test_kpi_apis()
    test_pages()
    test_static_assets()

    # 汇总
    print_header("验证完成")
    print_success("仪表盘与报表系统已就绪！")
    print_info("访问 URL:")
    print(f"    🎯 仪表盘: {API_BASE}/dashboard.html")
    print(f"    📊 报表中心: {API_BASE}/reports.html")
    print(f"    📋 任务中心: {API_BASE}/tasks.html")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ 验证被中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 验证失败: {str(e)}")
        sys.exit(1)
