# app.py

import os
import time
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from utils.utils import initialize_database
from utils.config import settings
from utils.deps import get_current_user, CurrentUser
from utils.logger import app_logger
from utils.rate_limit import limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

# 加载 .env 文件
# 配置加载统一由 utils.config.Settings 完成；此处不再重复加载 .env

# 导入路由
from routes import user, patrol, admin, photo, patrol_sse, chat, tasks, monitor


# 定义生命周期事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭事件"""
    # 启动时：初始化数据库（可通过环境变量跳过以便重复测试）
    print("\n" + "=" * 50)
    print("[INFO] Starting application...")
    skip_db_init = os.getenv("SKIP_DB_INIT", "0") == "1"
    if skip_db_init:
        print("[INFO] SKIP_DB_INIT=1 detected, skipping database init")
    else:
        try:
            if not initialize_database(step='all', skip_read_only_queries=True):
                print("[WARN] Database initialization failed, but continuing...")
        except Exception as e:
            print(f"[WARN] Database init error: {e}")
            print("[WARN] Continuing (ensure database server is running)...")
    print("[OK] Application started successfully!")
    print("[INFO] Visit http://127.0.0.1:5000")
    print("[INFO] API docs http://127.0.0.1:5000/docs")
    print("=" * 50 + "\n")
    
    yield
    
    # 关闭时：清理资源
    print("\n[INFO] Application shutting down...")


# 创建 FastAPI 应用
app = FastAPI(
    title="公路巡查系统",
    description="基于 FastAPI 的公路巡查管理系统",
    version="2.0.0",
    lifespan=lifespan
)


# ========================
# 中间件配置
# ========================

# CORS 中间件（如需前后端分离）
# 规则：
# - 若 ALLOW_ORIGINS 为空且为开发模式，则提供常见本地地址白名单
# - 若允许 "*" 通配符，则自动关闭 allow_credentials 以符合浏览器规范
dev_mode = settings.DEBUG
allow_origins = settings.ALLOW_ORIGINS[:]
if not allow_origins and dev_mode:
    allow_origins = [
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:5000",
        "http://localhost:5000",
    ]
allow_credentials = True
if any(o == "*" for o in allow_origins):
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 限流中间件
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# 请求耗时日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = int((time.time() - start) * 1000)
    try:
        app_logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms} ms)"
        )
    except Exception:
        # 保底：避免日志异常影响请求
        pass
    return response


# ========================
# 全局异常处理
# ========================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求数据验证错误"""
    # 规避非JSON可序列化对象（如 UploadFile ）导致的序列化异常
    safe_errors = []
    for err in exc.errors():
        item = err.copy()
        val = item.get("input")
        # 对无法序列化的对象做字符串化
        try:
            json.dumps(val)  # type: ignore
        except Exception:
            item["input"] = str(val)
        safe_errors.append(item)

    return JSONResponse(
        status_code=422,
        content={
            "detail": "数据验证失败",
            "errors": safe_errors
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理 HTTP 异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """处理未捕获的异常"""
    print(f"❌ 未捕获的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"}
    )


# ========================
# 静态文件和模板
# ========================

# 获取当前文件所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 挂载照片目录到 /photos 路由（使用配置中的绝对路径）
photos_dir = settings.UPLOAD_FOLDER
os.makedirs(photos_dir, exist_ok=True)
app.mount("/photos", StaticFiles(directory=photos_dir), name="photos")

# 额外挂载前端资源目录（如地图GeoJSON）
assets_dir = os.path.join(BASE_DIR, "assets")
if not os.path.exists(assets_dir):
    os.makedirs(assets_dir, exist_ok=True)
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# 配置模板（使用绝对路径）
templates_dir = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=templates_dir)


# ========================
# 注册路由
# ========================

app.include_router(user.router)
app.include_router(patrol.router)
app.include_router(admin.router)
app.include_router(photo.router)
app.include_router(patrol_sse.router)
app.include_router(chat.router)
app.include_router(tasks.router)
app.include_router(monitor.router)


# ========================
# HTML 页面路由
# ========================

@app.get("/", response_class=HTMLResponse, summary="首页")
async def home(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/patrol.html", response_class=HTMLResponse, summary="巡查页面")
async def patrol_page(request: Request):
    """巡查页面"""
    return templates.TemplateResponse("patrol.html", {"request": request})


@app.get("/admin.html", response_class=HTMLResponse, summary="管理员页面")
async def admin_page(request: Request):
    """管理员页面（客户端通过登录获取 token 后访问）"""
    return templates.TemplateResponse("admin.html", {"request": request})


@app.get("/map.html", response_class=HTMLResponse, summary="世界地图分析")
async def map_page(request: Request):
    """世界地图分析页（点击地区呈现统计图表）"""
    return templates.TemplateResponse("map.html", {"request": request})


@app.get("/map_simple.html", response_class=HTMLResponse, summary="简化版地图")
async def map_simple_page(request: Request):
    """简化版世界地图（用于测试）"""
    return templates.TemplateResponse("map_simple.html", {"request": request})


@app.get("/monitor", response_class=HTMLResponse, summary="数据库监控仪表板")
async def monitor_page(request: Request):
    """数据库性能监控仪表板"""
    return templates.TemplateResponse("monitor.html", {"request": request})


# ========================
# 健康检查接口
# ========================

@app.get("/health", summary="健康检查")
async def health():
    """简单健康检查：用于部署监控与环境校验"""
    return {
        "ok": True,
        "version": app.version,
        "debug": settings.DEBUG,
        "allow_origins": settings.ALLOW_ORIGINS,
        "skip_db_init": os.getenv("SKIP_DB_INIT", "0") == "1"
    }


# ========================
# 健康检查
# ========================

@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "message": "公路巡查系统运行正常",
        "version": "2.0.0"
    }


# ========================
# 启动入口
# ========================

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=5000,
        reload=True,  # 开发模式：代码改动自动重载
        log_level="info"
    )