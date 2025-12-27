"""管理员路由"""
from .admin_routes import router as admin_router
from .reports_routes import router as reports_router
from .monitor_routes import router as monitor_router
from .tasks_routes import router as tasks_router

__all__ = ["admin_router", "reports_router", "monitor_router", "tasks_router"]
