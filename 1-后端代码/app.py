# app.py

import os
import time
import json
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from settings import settings
from utils.utils import initialize_database
from core.deps import get_current_user, CurrentUser
from core.logger import app_logger
from core.rate_limit import limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from celery_app import celery_app
from workers.report.tasks import export_large_excel, generate_monthly_report

# 加载 .env 文件
# 配置加载统一由 settings.py（基于 pydantic-settings）完成

# 导入路由
from routes.auth import router as auth_router
from routes.patrol import patrol_router, sse_router, photo_router
from routes.admin import admin_router, reports_router, monitor_router, tasks_router as admin_tasks_router
from routes.chat import router as chat_router
from routes.tasks import router as tasks_router
from routes.photos import router as photos_router  # 新增照片管理路由


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

# 挂载静态资源目录 /static（JS/CSS/Images）
static_dir = os.path.join(BASE_DIR, "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ========================
# 注册路由
# ========================

# ========================
# 注册路由
# ========================

app.include_router(auth_router)
app.include_router(patrol_router)
app.include_router(sse_router)
app.include_router(photo_router)
app.include_router(admin_router)
app.include_router(reports_router)
app.include_router(monitor_router)
app.include_router(admin_tasks_router)
app.include_router(chat_router)
app.include_router(tasks_router)
app.include_router(photos_router)  # 新增照片管理路由


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


@app.get("/dashboard.html", response_class=HTMLResponse, summary="运营总览")
async def dashboard_page(request: Request):
    """运营总览页面"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/tasks.html", response_class=HTMLResponse, summary="任务中心")
async def tasks_page(request: Request):
    """异步任务管理中心"""
    return templates.TemplateResponse("tasks.html", {"request": request})


@app.get("/reports.html", response_class=HTMLResponse, summary="报表中心")
async def reports_page(request: Request):
    """报表中心页面"""
    return templates.TemplateResponse("reports.html", {"request": request})

# ========================
# 用户信息 API
# ========================

@app.get("/api/user/profile", summary="获取用户信息")
async def get_user_profile(current_user: CurrentUser = Depends(get_current_user)):
    """获取当前登录用户的基本信息"""
    return {
        "username": getattr(current_user, "username", "admin"),
        "role": getattr(current_user, "role", "admin"),
        "is_superuser": getattr(current_user, "role", "") == "superuser"
    }

# ========================
# 报表 API（Celery 集成）
# ========================

@app.post("/api/reports/export/excel", summary="导出 Excel 报表")
async def export_excel_report(request: Request):
    """异步导出 Excel 报表，返回 task_id"""
    try:
        data = await request.json()
        start = data.get("start_date")
        end = data.get("end_date")
        include_photos = data.get("include_photos", "no")
        
        if not start or not end:
            return JSONResponse(status_code=422, content={"detail": "开始/结束日期必填"})
        
        # 提交 Celery 任务（使用现有的 export_large_excel）
        task = export_large_excel.apply_async(
            args=[start, end, None],
            expires=3600
        )
        
        return {
            "task_id": task.id,
            "status": "queued",
            "include_photos": include_photos
        }
    except Exception as e:
        app_logger.error(f"导出 Excel 失败: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.post("/api/reports/export/pdf", summary="导出 PDF 报表")
async def export_pdf_report(request: Request):
    """异步导出 PDF 报表，返回 task_id"""
    try:
        data = await request.json()
        start = data.get("start_date")
        end = data.get("end_date")
        title = data.get("title", "")
        
        if not start or not end:
            return JSONResponse(status_code=422, content={"detail": "开始/结束日期必填"})
        
        # 提交 Celery 任务（Excel 导出后可转 PDF）
        task = export_large_excel.apply_async(
            args=[start, end, None],
            expires=3600
        )
        
        return {
            "task_id": task.id,
            "status": "queued",
            "title": title
        }
    except Exception as e:
        app_logger.error(f"导出 PDF 失败: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.post("/api/reports/monthly/generate", summary="生成月报")
async def generate_monthly_report_api(request: Request):
    """异步生成月报，返回 task_id"""
    try:
        data = await request.json()
        year = data.get("year")
        month = data.get("month")
        
        try:
            year = int(year)
            month = int(month)
        except Exception:
            return JSONResponse(status_code=422, content={"detail": "年份/月必须为数字"})
        
        if year < 2020 or year > 2030 or month < 1 or month > 12:
            return JSONResponse(status_code=422, content={"detail": "年份或月份不在允许范围"})
        
        # 提交 Celery 任务
        task = generate_monthly_report.apply_async(
            args=[year, month],
            expires=3600
        )
        
        return {
            "task_id": task.id,
            "status": "queued",
            "year": year,
            "month": month
        }
    except Exception as e:
        app_logger.error(f"生成月报失败: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.get("/api/reports/task/{task_id}", summary="查询报表任务状态")
async def get_report_task_status(task_id: str):
    """查询异步任务的执行状态"""
    try:
        task = celery_app.AsyncResult(task_id)
        return {
            "task_id": task_id,
            "state": task.state,
            "result": task.result if task.state == "SUCCESS" else None,
            "error": str(task.info) if task.state == "FAILURE" else None
        }
    except Exception as e:
        app_logger.error(f"查询任务状态失败: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.get("/api/reports/download", summary="下载报表文件")
async def download_report(file_path: str):
    """下载生成的报表文件"""
    try:
        from fastapi.responses import FileResponse
        
        # 防止路径遍历攻击
        safe_path = Path(file_path).resolve()
        base_dir = Path("exports").resolve()
        
        if not str(safe_path).startswith(str(base_dir)):
            return JSONResponse(status_code=403, content={"detail": "禁止访问"})
        
        if not safe_path.exists():
            return JSONResponse(status_code=404, content={"detail": "文件不存在"})
        
        return FileResponse(
            path=safe_path,
            filename=safe_path.name,
            media_type="application/octet-stream"
        )
    except Exception as e:
        app_logger.error(f"下载报表失败: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

# ========================
# 仪表盘 KPI API（数据库驱动）
# ========================

@app.get("/api/dashboard/kpi/today_tasks", summary="今日任务数（mock）")
async def kpi_today_tasks():
    """Mock：返回今日任务数"""
    try:
        return {"label": "今日任务", "value": 26}
    except Exception as e:
        app_logger.error(f"查询今日任务失败: {e}")
        return {"label": "今日任务", "value": 0}

@app.get("/api/dashboard/kpi/success_rate", summary="任务成功率（mock）")
async def kpi_success_rate():
    """Mock：返回任务成功率"""
    try:
        return {"label": "成功率", "value": "96%"}
    except Exception as e:
        app_logger.error(f"查询成功率失败: {e}")
        return {"label": "成功率", "value": "0%"}

@app.get("/api/dashboard/kpi/avg_latency", summary="平均耗时（mock）")
async def kpi_avg_latency():
    """Mock：返回平均耗时"""
    try:
        return {"label": "平均耗时", "value": "1.3s"}
    except Exception as e:
        app_logger.error(f"查询平均耗时失败: {e}")
        return {"label": "平均耗时", "value": "0s"}

@app.get("/api/dashboard/kpi/active_users", summary="活跃用户（mock）")
async def kpi_active_users():
    """Mock：返回活跃用户数"""
    try:
        return {"label": "活跃用户", "value": 14}
    except Exception as e:
        app_logger.error(f"查询活跃用户失败: {e}")
        return {"label": "活跃用户", "value": 0}

@app.get("/api/dashboard/recent-tasks", summary="最近任务")
async def get_recent_tasks(limit: int = 10):
    """获取最近的任务列表"""
    try:
        # 占位实现：实际应从数据库查询最近任务
        # 示例：SELECT id, status, name FROM tasks ORDER BY created_at DESC LIMIT ?
        return {
            "recent_tasks": [
                {"task_id": f"TASK-{1000+i}", "name": f"任务 {i+1}", "state": "SUCCESS" if i % 2 == 0 else "PENDING"}
                for i in range(min(limit, 5))
            ]
        }
    except Exception as e:
        app_logger.error(f"查询最近任务失败: {e}")
        return {"recent_tasks": []}


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