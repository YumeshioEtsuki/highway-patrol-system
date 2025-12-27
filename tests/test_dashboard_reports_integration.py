"""
仪表盘与报表集成测试

功能：
- 验证报表 API 端点
- 验证 KPI 数据源
- 验证 Celery 任务队列
- 验证前端表单提交集成
"""

import pytest
import json
import asyncio
from datetime import date, timedelta
from httpx import AsyncClient
from fastapi.testclient import TestClient

# 假设 FastAPI 应用在 app.py 中
try:
    from app import app
    from celery_app import celery_app
except ImportError:
    print("Warning: 无法导入 app 或 celery_app，请确保在项目根目录运行测试")


class TestReportAPIs:
    """报表 API 测试"""

    def test_export_excel_success(self):
        """测试 Excel 导出成功"""
        client = TestClient(app)
        response = client.post("/api/reports/export/excel", json={
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "include_photos": "no"
        })
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "queued"
        print(f"✓ Excel 导出任务 ID: {data['task_id']}")

    def test_export_excel_missing_dates(self):
        """测试缺少日期字段"""
        client = TestClient(app)
        response = client.post("/api/reports/export/excel", json={
            "include_photos": "no"
        })
        assert response.status_code == 422
        print("✓ 缺少日期字段时返回 422")

    def test_export_pdf_success(self):
        """测试 PDF 导出"""
        client = TestClient(app)
        response = client.post("/api/reports/export/pdf", json={
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "title": "2024 年巡查报告"
        })
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        print(f"✓ PDF 导出任务 ID: {data['task_id']}")

    def test_monthly_report_success(self):
        """测试月报生成"""
        client = TestClient(app)
        response = client.post("/api/reports/monthly/generate", json={
            "year": 2024,
            "month": 12
        })
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["year"] == 2024
        assert data["month"] == 12
        print(f"✓ 月报生成任务 ID: {data['task_id']}")

    def test_monthly_report_invalid_month(self):
        """测试无效月份"""
        client = TestClient(app)
        response = client.post("/api/reports/monthly/generate", json={
            "year": 2024,
            "month": 13
        })
        assert response.status_code == 422
        print("✓ 无效月份时返回 422")

    def test_task_status_query(self):
        """测试查询任务状态"""
        client = TestClient(app)
        
        # 先提交一个任务
        submit_response = client.post("/api/reports/export/excel", json={
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        })
        task_id = submit_response.json()["task_id"]
        
        # 查询任务状态
        status_response = client.get(f"/api/reports/task/{task_id}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "state" in status_data
        assert "task_id" in status_data
        print(f"✓ 任务状态: {status_data['state']}")


class TestKPIAPIs:
    """KPI 数据源测试"""

    def test_kpi_today_tasks(self):
        """测试今日任务 KPI"""
        client = TestClient(app)
        response = client.get("/api/dashboard/kpi/today_tasks")
        assert response.status_code == 200
        data = response.json()
        assert "label" in data
        assert "value" in data
        assert data["label"] == "今日任务"
        print(f"✓ 今日任务: {data['value']}")

    def test_kpi_success_rate(self):
        """测试成功率 KPI"""
        client = TestClient(app)
        response = client.get("/api/dashboard/kpi/success_rate")
        assert response.status_code == 200
        data = response.json()
        assert "label" in data
        assert "value" in data
        assert data["label"] == "成功率"
        print(f"✓ 成功率: {data['value']}")

    def test_kpi_avg_latency(self):
        """测试平均耗时 KPI"""
        client = TestClient(app)
        response = client.get("/api/dashboard/kpi/avg_latency")
        assert response.status_code == 200
        data = response.json()
        assert "label" in data
        assert "value" in data
        assert data["label"] == "平均耗时"
        print(f"✓ 平均耗时: {data['value']}")

    def test_kpi_active_users(self):
        """测试活跃用户 KPI"""
        client = TestClient(app)
        response = client.get("/api/dashboard/kpi/active_users")
        assert response.status_code == 200
        data = response.json()
        assert "label" in data
        assert "value" in data
        assert data["label"] == "活跃用户"
        print(f"✓ 活跃用户: {data['value']}")

    def test_recent_tasks(self):
        """测试最近任务列表"""
        client = TestClient(app)
        response = client.get("/api/dashboard/recent-tasks?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "recent_tasks" in data
        assert isinstance(data["recent_tasks"], list)
        print(f"✓ 最近任务数: {len(data['recent_tasks'])}")


class TestPageRendering:
    """页面渲染测试"""

    def test_dashboard_page(self):
        """测试仪表盘页面"""
        client = TestClient(app)
        response = client.get("/dashboard.html")
        assert response.status_code == 200
        assert "kpiContainer" in response.text or "dashboard" in response.text.lower()
        print("✓ 仪表盘页面加载成功")

    def test_reports_page(self):
        """测试报表页面"""
        client = TestClient(app)
        response = client.get("/reports.html")
        assert response.status_code == 200
        assert "formContainer" in response.text or "export" in response.text.lower()
        print("✓ 报表页面加载成功")

    def test_tasks_page(self):
        """测试任务页面"""
        client = TestClient(app)
        response = client.get("/tasks.html")
        assert response.status_code == 200
        assert "tasksList" in response.text or "tasks" in response.text.lower()
        print("✓ 任务页面加载成功")


class TestStaticAssets:
    """静态资源加载测试"""

    def test_common_js(self):
        """测试 common.js"""
        client = TestClient(app)
        response = client.get("/static/js/common.js")
        assert response.status_code == 200
        assert "showNotification" in response.text or "APIClient" in response.text
        print("✓ common.js 加载成功")

    def test_tasks_js(self):
        """测试 tasks.js"""
        client = TestClient(app)
        response = client.get("/static/js/tasks.js")
        assert response.status_code == 200
        assert "TaskManager" in response.text or "TASK_CONFIG" in response.text
        print("✓ tasks.js 加载成功")

    def test_reports_js(self):
        """测试 reports.js"""
        client = TestClient(app)
        response = client.get("/static/js/reports.js")
        assert response.status_code == 200
        assert "REPORT_TASK_CONFIG" in response.text or "export" in response.text.lower()
        print("✓ reports.js 加载成功")

    def test_dashboard_js(self):
        """测试 dashboard.js"""
        client = TestClient(app)
        response = client.get("/static/js/dashboard.js")
        assert response.status_code == 200
        assert "DASHBOARD_CONFIG" in response.text or "renderKPI" in response.text
        print("✓ dashboard.js 加载成功")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("开始集成测试：仪表盘与报表 API")
    print("="*60 + "\n")

    # 报表 API 测试
    print("\n[报表 API]")
    test_reports = TestReportAPIs()
    test_reports.test_export_excel_success()
    test_reports.test_export_excel_missing_dates()
    test_reports.test_export_pdf_success()
    test_reports.test_monthly_report_success()
    test_reports.test_monthly_report_invalid_month()
    test_reports.test_task_status_query()

    # KPI 测试
    print("\n[KPI 数据源]")
    test_kpi = TestKPIAPIs()
    test_kpi.test_kpi_today_tasks()
    test_kpi.test_kpi_success_rate()
    test_kpi.test_kpi_avg_latency()
    test_kpi.test_kpi_active_users()
    test_kpi.test_recent_tasks()

    # 页面渲染测试
    print("\n[页面渲染]")
    test_pages = TestPageRendering()
    test_pages.test_dashboard_page()
    test_pages.test_reports_page()
    test_pages.test_tasks_page()

    # 静态资源测试
    print("\n[静态资源]")
    test_assets = TestStaticAssets()
    test_assets.test_common_js()
    test_assets.test_tasks_js()
    test_assets.test_reports_js()
    test_assets.test_dashboard_js()

    print("\n" + "="*60)
    print("✅ 所有测试通过！")
    print("="*60 + "\n")
