"""
FastAPI Web Application - Environment Variable Manager
Follows MVC pattern: Model(lib) + View(templates) + Controller(routes)
"""
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import EnvManager, get_recommendations, validate_config, get_help_text, view_ai_cache, clear_ai_cache

ROOT = Path(__file__).resolve().parent.parent.parent.parent
STATIC = Path(__file__).resolve().parent / "static"
TEMPLATES = Path(__file__).resolve().parent / "templates"

app = FastAPI(title="Environment Variable Manager")

# Static files
if STATIC.exists():
    app.mount("/static", StaticFiles(directory=STATIC), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory=str(TEMPLATES))

# Initialize manager
manager = EnvManager(ROOT)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Home page - show all configuration keys with current values"""
    all_keys = manager.get_all_keys()
    envs = ["dev", "test", "demo", "prod"]
    
    # Get all current values for each key across all environments
    config_data = {}
    for key in all_keys:
        config_data[key] = manager.get_current_values(key)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "config_data": config_data,
        "all_keys": list(all_keys),
        "envs": envs,
    })


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, key: str = Form(...)):
    """Analyze current and recommended values for a key"""
    key = key.strip().upper()
    
    if not key:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "Key name cannot be empty"
        })
    
    # 获取当前值
    current = manager.get_current_values(key)
    
    # 使用 AI 生成推荐（传入当前值用于分析）
    recommend = get_recommendations(key, current_values=current, use_ai=True)
    
    # 获取帮助文本（尝试使用 AI）
    help_text = get_help_text(key, use_ai=True)
    
    return templates.TemplateResponse("analyze.html", {
        "request": request,
        "key": key,
        "current": current,
        "recommend": recommend,
        "help_text": help_text,
        "envs": ["dev", "test", "demo", "prod"],
    })


@app.post("/apply", response_class=HTMLResponse)
async def apply(request: Request):
    """Apply recommended values to selected environments"""
    form = await request.form()
    key = form.get("key", "").strip().upper()
    envs = form.getlist("env")
    
    # 获取当前值用于 AI 分析
    current = manager.get_current_values(key)
    recommend = get_recommendations(key, current_values=current, use_ai=True)
    
    if not key:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "Key name is missing"
        })
    
    if not envs:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "No environment selected"
        })
    
    value = recommend.get(envs[0], "")
    is_valid, msg = validate_config(key, value)
    
    if not is_valid:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Validation failed: {msg}"
        })
    
    updated, failed = manager.set_values_batch(key, envs, value)
    
    return templates.TemplateResponse("result.html", {
        "request": request,
        "key": key,
        "updated": updated,
        "failed": failed,
        "total": len(envs),
        "value": value,
        "is_custom": False,
    })


@app.post("/custom", response_class=HTMLResponse)
async def apply_custom(request: Request):
    """Apply custom value"""
    form = await request.form()
    key = form.get("key", "").strip().upper()
    value = form.get("value", "").strip()
    envs = form.getlist("env")
    
    if not key:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "Key name is missing"
        })
    
    if not envs:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "No environment selected"
        })
    
    # Validate
    is_valid, msg = validate_config(key, value)
    if not is_valid:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Validation failed: {msg}"
        })
    
    updated, failed = manager.set_values_batch(key, envs, value)
    
    return templates.TemplateResponse("result.html", {
        "request": request,
        "key": key,
        "updated": updated,
        "failed": failed,
        "total": len(envs),
        "value": value,
        "is_custom": True,
    })


@app.get("/list", response_class=HTMLResponse)
async def list_configs(request: Request):
    """列出所有环境文件的配置"""
    data = {"dev": {}, "test": {}, "demo": {}, "prod": {}}
    
    for env in ["dev", "test", "demo", "prod"]:
        values = manager.get_all_values(env)
        data[env] = values
    
    return templates.TemplateResponse("list.html", {
        "request": request,
        "data": data,
        "envs": ["dev", "test", "demo", "prod"]
    })


@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request):
    """帮助文档页面"""
    return templates.TemplateResponse("help.html", {
        "request": request
    })


@app.get("/ai-cache", response_class=HTMLResponse)
async def ai_cache_page(request: Request):
    """AI 缓存管理页面"""
    cache = view_ai_cache()
    
    return templates.TemplateResponse("ai_cache.html", {
        "request": request,
        "cache": cache,
        "cache_count": len(cache)
    })


@app.post("/ai-cache/clear")
async def clear_cache(request: Request):
    """清除 AI 缓存"""
    success = clear_ai_cache()
    
    if success:
        message = "✅ 已清除所有 AI 缓存"
    else:
        message = "ℹ️ 缓存为空或清除失败"
    
    return templates.TemplateResponse("ai_cache.html", {
        "request": request,
        "cache": {},
        "cache_count": 0,
        "message": message
    })


if __name__ == "__main__":
    import uvicorn
    import socket
    
    PORT = 5051
    HOST = "127.0.0.1"
    
    print("Starting Environment Variable Manager Web Tool...")
    print(f"Access URL: http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop")
    
    # 检查并释放端口
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(1)
        result = test_socket.connect_ex((HOST, PORT))
        test_socket.close()
        
        if result == 0:  # 端口被占用
            print(f"⚠️  Port {PORT} is in use, attempting to free it...")
            try:
                import psutil
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        for conn in proc.net_connections(kind='inet'):
                            if conn.laddr.port == PORT and conn.laddr.ip == HOST:
                                print(f"   Killing process {proc.pid} ({proc.name()})")
                                proc.kill()
                                proc.wait(timeout=3)
                                print(f"✅ Port {PORT} freed successfully")
                                break
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        pass
            except ImportError:
                print("⚠️  psutil not installed. Installing...")
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil", "-q"])
                print("✅ psutil installed, please restart the server")
                sys.exit(0)
    except Exception as e:
        print(f"⚠️  Error checking port: {e}")
    
    uvicorn.run(app, host=HOST, port=PORT)
