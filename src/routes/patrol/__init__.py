"""巡查相关路由"""
from .patrol_routes import router as patrol_router
from .sse_routes import router as sse_router
from .photo_routes import router as photo_router

__all__ = ["patrol_router", "sse_router", "photo_router"]
