"""
FastAPI Web Application - Environment Variable Manager
Follows MVC pattern: Model(lib) + View(templates) + Controller(routes)
"""
from pathlib import Path
from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import (
    EnvManager, 
    get_recommendations, 
    validate_config, 
    get_help_text, 
    view_ai_cache, 
    clear_ai_cache, 
    clear_ai_cache_item,
    submit_ai_feedback,
    record_ai_recommendation_applied,
    get_cache_with_confidence,
    get_adaptive_weights_info,
)

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
    
    response = templates.TemplateResponse("index.html", {
        "request": request,
        "config_data": config_data,
        "all_keys": list(all_keys),
        "envs": envs,
    })
    # 禁止浏览器缓存，确保数据实时更新
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def _render_analyze_page(request: Request, key: str):
    key = key.strip().upper()
    if not key:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "Key name cannot be empty"
        })

    current = manager.get_current_values(key)

    cached_entry = get_cache_with_confidence(key)
    if cached_entry and cached_entry.get("recommendations"):
        recommend = cached_entry["recommendations"]
        help_text = f"💡 使用缓存推荐值（置信度: {int(cached_entry.get('confidence', 0) * 100)}%）"
    else:
        recommend = get_recommendations(key, current_values=current, use_ai=False)
        help_text = get_help_text(key, use_ai=False)

    return templates.TemplateResponse("analyze.html", {
        "request": request,
        "key": key,
        "current": current,
        "recommend": recommend,
        "help_text": help_text,
        "ai_explanation": None,
        "ai_best_practices": None,
        "envs": ["dev", "test", "demo", "prod"],
    })


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, key: str = Form(...)):
    """分析配置项（不立即调用 AI）"""
    return _render_analyze_page(request, key)


@app.get("/analyze", response_class=HTMLResponse)
async def analyze_get(request: Request, key: str = Query(...)):
    """支持通过查询参数直接访问 analyze 页面，便于缓存页返回"""
    return _render_analyze_page(request, key)


@app.get("/analyze/{key}", response_class=HTMLResponse)
async def analyze_get_path(request: Request, key: str):
    """支持路径参数形式访问，兼容直接链接"""
    return _render_analyze_page(request, key)


@app.post("/ai-recommend", response_class=HTMLResponse)
async def ai_recommend(request: Request, key: str = Form(...)):
    """使用 AI 生成智能推荐"""
    key = key.strip().upper()
    
    if not key:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "Key name cannot be empty"
        })
    
    # 获取当前值
    current = manager.get_current_values(key)
    
    # 读取实际的 .env 文件作为上下文（包含注释）
    env_context = {}
    for env in ["dev", "test", "demo", "prod"]:
        env_context[env] = manager.get_all_values_with_comments(env)
    
    # 使用 AI 生成推荐（传入完整上下文和缓存参考）
    from lib.ai_helper import get_ai_helper
    ai_helper = get_ai_helper()
    
    ai_explanation = None
    ai_best_practices = None
    ai_corrections = None
    recommend = None
    
    if ai_helper.is_available():
        try:
            # 获取缓存的推荐信息作为参考（确保同一键）
            cache_info = get_cache_with_confidence(key)
            if cache_info and cache_info.get("key") not in (None, key):
                cache_info = None
            
            # 调用 AI，传入完整的环境上下文和缓存参考
            ai_result = ai_helper.get_env_recommendations_with_context(
                key, 
                current,
                env_context,
                cache_info=cache_info  # 传入缓存信息用于参考
            )
            
            if ai_result and "recommendations" in ai_result:
                recommend = ai_result["recommendations"]
                ai_explanation = ai_result.get('explanation')
                ai_best_practices = ai_result.get('best_practices')
                if isinstance(ai_best_practices, list):
                    ai_best_practices = "；".join([str(x).strip() for x in ai_best_practices if str(x).strip()])
                ai_corrections = ai_result.get('corrections')
                
                # 保存到缓存
                from lib.validators import _add_to_ai_cache
                metadata = {
                    'explanation': ai_explanation,
                    'best_practices': ai_best_practices,
                    'warnings': ai_result.get('warnings', [])
                }
                _add_to_ai_cache(key, recommend, metadata)
        except Exception as e:
            print(f"[AI] 生成失败: {e}")

    
    # 如果 AI 失败，使用静态推荐
    if not recommend:
        recommend = get_recommendations(key, current_values=current, use_ai=False)
    
    # 获取帮助文本
    help_text = get_help_text(key, use_ai=True)
    
    return templates.TemplateResponse("analyze.html", {
        "request": request,
        "key": key,
        "current": current,
        "recommend": recommend,
        "help_text": help_text,
        "ai_explanation": ai_explanation,
        "ai_best_practices": ai_best_practices,
        "ai_corrections": ai_corrections,
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
    
    # 为每个环境应用对应的推荐值
    updated = []
    failed = []
    skipped = []  # 已经是推荐值，无需更新
    
    for env in envs:
        raw_value = recommend.get(env, "")
        value = str(raw_value)
        
        # 验证值
        is_valid, msg = validate_config(key, value)
        if not is_valid:
            failed.append(env)
            continue
        
        # 检查当前值是否已经是推荐值
        current_value = manager.get_value(key, env)
        if current_value == value:
            skipped.append(env)
            continue
        
        # 应用值
        if manager.set_value(key, env, value):
            updated.append(env)
        else:
            failed.append(env)
    
    # 如果应用了推荐值，记录该应用
    if len(updated) > 0:
        record_ai_recommendation_applied(key)
    
    return templates.TemplateResponse("result.html", {
        "request": request,
        "key": key,
        "updated": updated,
        "failed": failed,
        "skipped": skipped,
        "total": len(envs),
        "value": ", ".join([f"{env}={recommend.get(env, '')}" for env in envs]),
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
    generation_count_total = sum(entry.get("generation_count", 0) for entry in cache.values())
    
    # 获取自适应权重信息
    weights_info = get_adaptive_weights_info()
    
    return templates.TemplateResponse("ai_cache.html", {
        "request": request,
        "cache": cache,
        "cache_count": len(cache),
        "generation_count_total": generation_count_total,
        "weights_info": weights_info,
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
        "generation_count_total": 0,
        "message": message
    })


@app.post("/ai-cache/clear-item")
async def clear_cache_item(request: Request, key: str = Form(...)):
    """清除单个键的 AI 缓存"""
    key_upper = key.strip().upper()
    success = clear_ai_cache_item(key_upper)

    # 重新加载页面数据
    cache = view_ai_cache()
    generation_count_total = sum(entry.get("generation_count", 0) for entry in cache.values())
    message = f"✅ 已清除 {key_upper} 的缓存" if success else "ℹ️ 未找到对应缓存或清除失败"

    # 获取自适应权重信息
    weights_info = get_adaptive_weights_info()

    return templates.TemplateResponse("ai_cache.html", {
        "request": request,
        "cache": cache,
        "cache_count": len(cache),
        "generation_count_total": generation_count_total,
        "weights_info": weights_info,
        "message": message,
    })


@app.post("/ai-feedback")
async def submit_feedback(request: Request):
    """提交 AI 推荐反馈"""
    form = await request.form()
    key = form.get("key", "").strip().upper()
    feedback_type = form.get("feedback", "")  # "positive" 或 "negative"
    
    if not key or not feedback_type:
        return {"success": False, "message": "参数错误"}
    
    is_positive = feedback_type == "positive"
    success = submit_ai_feedback(key, is_positive)
    
    if success:
        return {
            "success": True,
            "message": f"✅ 感谢反馈！{'正面' if is_positive else '负面'}评价已记录"
        }
    else:
        return {
            "success": False,
            "message": "❌ 提交反馈失败"
        }


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
