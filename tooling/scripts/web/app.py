"""
FastAPI Web 应用 - 环境变量管理工具
遵循MVC模式：Model(lib) + View(templates) + Controller(routes)
"""
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.sessions import SessionMiddleware

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import EnvManager, get_recommendations, validate_config, get_help_text

ROOT = Path(__file__).resolve().parent.parent.parent.parent
STATIC = Path(__file__).resolve().parent / "static"
TEMPLATES = Path(__file__).resolve().parent / "templates"

app = FastAPI(title="环境变量管理工具")

# 中间件
app.add_middleware(SessionMiddleware, secret_key="env-manager-secure-key-2025")

# 静态文件
if STATIC.exists():
    app.mount("/static", StaticFiles(directory=STATIC), name="static")

# 初始化管理器
manager = EnvManager(ROOT)


@app.get("/", response_class=HTMLResponse)
async def index():
    """首页"""
    all_keys = manager.get_all_keys()
    return _render("index.html", {
        "all_keys": list(all_keys),
        "envs": ["dev", "test", "demo", "prod"],
    })


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(key: str = Form(...)):
    """分析指定键的当前值和推荐值"""
    key = key.strip().upper()
    
    if not key:
        return _error_page("键名不能为空")
    
    current = manager.get_current_values(key)
    recommend = get_recommendations(key)
    help_text = get_help_text(key)
    
    return _render("analyze.html", {
        "key": key,
        "current": current,
        "recommend": recommend,
        "help_text": help_text,
        "envs": ["dev", "test", "demo", "prod"],
    })


@app.post("/apply", response_class=HTMLResponse)
async def apply(request: Request):
    """应用推荐值到选定环境"""
    form = await request.form()
    key = form.get("key", "").strip().upper()
    envs = form.getlist("env")
    recommend = get_recommendations(key)
    
    if not key:
        return _error_page("键名缺失")
    
    if not envs:
        return _error_page("未选择任何环境")
    
    value = recommend.get(envs[0], "")
    is_valid, msg = validate_config(key, value)
    
    if not is_valid:
        return _error_page(f"配置验证失败: {msg}")
    
    updated, failed = manager.set_values_batch(key, envs, value)
    
    return _render("result.html", {
        "key": key,
        "updated": updated,
        "failed": failed,
        "total": len(envs),
        "value": value,
    })


@app.post("/custom", response_class=HTMLResponse)
async def apply_custom(request: Request):
    """应用自定义值"""
    form = await request.form()
    key = form.get("key", "").strip().upper()
    value = form.get("value", "").strip()
    envs = form.getlist("env")
    
    if not key:
        return _error_page("键名缺失")
    
    if not envs:
        return _error_page("未选择任何环境")
    
    # 验证
    is_valid, msg = validate_config(key, value)
    if not is_valid:
        return _error_page(f"配置验证失败: {msg}")
    
    updated, failed = manager.set_values_batch(key, envs, value)
    
    return _render("result.html", {
        "key": key,
        "updated": updated,
        "failed": failed,
        "total": len(envs),
        "value": value,
        "is_custom": True,
    })


@app.get("/list", response_class=HTMLResponse)
async def list_all():
    """列出所有环境文件的所有配置"""
    data = {}
    for env, path in manager.files.items():
        data[env] = _parse_env_file(path)
    
    return _render("list.html", {
        "data": data,
        "envs": ["dev", "test", "demo", "prod"],
    })


def _parse_env_file(path: Path) -> dict:
    """解析环境文件"""
    if not path.exists():
        return {}
    
    result = {}
    content = path.read_text(encoding="utf-8")
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            result[k.strip()] = v.strip()
    
    return result


def _render(template_name: str, context: dict) -> str:
    """简单的模板渲染（使用 f-string）"""
    # 这里实现简化的模板系统，或直接返回 HTML
    # 为了简洁，直接在此文件末尾定义模板
    if template_name == "index.html":
        return render_index(context)
    elif template_name == "analyze.html":
        return render_analyze(context)
    elif template_name == "result.html":
        return render_result(context)
    elif template_name == "list.html":
        return render_list(context)
    return "<h1>模板未找到</h1>"


def _error_page(message: str) -> str:
    """错误页面"""
    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }}
            .error {{ background: #fee; border: 1px solid #fcc; padding: 20px; border-radius: 4px; color: #c00; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="error">
            <h2>❌ 错误</h2>
            <p>{message}</p>
            <p><a href="/">← 返回首页</a></p>
        </div>
    </body>
    </html>
    """


# 简单的模板函数
def render_index(ctx):
    return """
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>环境变量管理工具</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
            .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
            .card { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 30px; margin-bottom: 20px; }
            h1 { color: #333; margin-bottom: 10px; font-size: 28px; }
            .subtitle { color: #666; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; color: #333; font-weight: 500; }
            input[type="text"], select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
            input[type="text"]:focus { outline: none; border-color: #0066cc; box-shadow: 0 0 0 3px rgba(0,102,204,0.1); }
            button { background: #0066cc; color: white; padding: 10px 24px; border: none; border-radius: 4px; font-size: 14px; cursor: pointer; font-weight: 500; }
            button:hover { background: #0052a3; }
            .menu { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px; }
            .menu-item { padding: 20px; background: #f9f9f9; border-radius: 4px; border-left: 4px solid #0066cc; }
            .menu-item h3 { color: #333; margin-bottom: 10px; }
            .menu-item p { color: #666; font-size: 14px; margin-bottom: 10px; }
            .menu-item a { color: #0066cc; text-decoration: none; font-weight: 500; }
            .menu-item a:hover { text-decoration: underline; }
            .tip { background: #fffacd; border-left: 4px solid #ffa500; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
            .tip strong { color: #ff6600; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h1>🔧 环境变量管理工具</h1>
                <p class="subtitle">可视化修改 .env 配置</p>
                
                <div class="tip">
                    <strong>💡 提示：</strong>此工具用于快速管理 dev/test/demo/prod 环境的配置文件。每次修改后自动保存到对应的 .env 文件。
                </div>
                
                <form method="post" action="/analyze">
                    <div class="form-group">
                        <label for="key">📝 配置键名</label>
                        <input type="text" id="key" name="key" placeholder="例如: SKIP_DB_INIT, DEBUG, LOG_LEVEL" required>
                    </div>
                    <button type="submit">🔍 分析与应用推荐值</button>
                </form>
                
                <div class="menu" style="margin-top: 40px;">
                    <div class="menu-item">
                        <h3>📋 查看所有配置</h3>
                        <p>查看当前所有环境的完整配置列表</p>
                        <a href="/list">查看列表 →</a>
                    </div>
                    <div class="menu-item">
                        <h3>📚 使用帮助</h3>
                        <p>了解各配置项的含义和最佳实践</p>
                        <a href="#help">帮助文档 →</a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

def render_analyze(ctx):
    key = ctx.get("key", "")
    current = ctx.get("current", {})
    recommend = ctx.get("recommend", {})
    help_text = ctx.get("help_text", "")
    envs = ctx.get("envs", [])
    
    rows = ""
    for env in envs:
        curr = current.get(env, "(未配置)")
        rec = recommend.get(env, "")
        rows += f"""
        <tr>
            <td style="font-weight: bold; color: #333;">{env}</td>
            <td style="font-family: monospace; color: #666;">{curr}</td>
            <td style="font-family: monospace; color: #0066cc; font-weight: bold;">{rec}</td>
            <td><input type="checkbox" name="env" value="{env}" checked></td>
        </tr>
        """
    
    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; margin: 0; }}
            .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
            .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 30px; }}
            h2 {{ color: #333; margin-bottom: 20px; }}
            .help-box {{ background: #e8f4f8; border-left: 4px solid #0066cc; padding: 15px; margin-bottom: 20px; border-radius: 4px; }}
            .help-box p {{ color: #333; margin: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f9f9f9; font-weight: 600; color: #333; }}
            tr:hover {{ background: #f5f5f5; }}
            input[type="checkbox"] {{ width: 18px; height: 18px; cursor: pointer; }}
            .button-group {{ display: flex; gap: 10px; margin-top: 20px; }}
            button {{ padding: 10px 24px; border: none; border-radius: 4px; font-size: 14px; cursor: pointer; font-weight: 500; }}
            .btn-primary {{ background: #0066cc; color: white; }}
            .btn-primary:hover {{ background: #0052a3; }}
            .btn-secondary {{ background: #f0f0f0; color: #333; }}
            .btn-secondary:hover {{ background: #e0e0e0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h2>🔍 分析: <code style="color: #0066cc;">{key}</code></h2>
                
                <div class="help-box">
                    <p><strong>ℹ️ 说明：</strong> {help_text}</p>
                </div>
                
                <h3>当前值 vs 推荐值</h3>
                <table>
                    <tr>
                        <th>环境</th>
                        <th>当前值</th>
                        <th>推荐值</th>
                        <th>应用</th>
                    </tr>
                    {rows}
                </table>
                
                <form method="post" action="/apply">
                    <input type="hidden" name="key" value="{key}">
                    <div class="button-group">
                        <button type="submit" class="btn-primary">✅ 应用推荐值</button>
                        <a href="/"><button type="button" class="btn-secondary">← 返回</button></a>
                    </div>
                </form>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                
                <h3>🛠️ 应用自定义值</h3>
                <form method="post" action="/custom">
                    <input type="hidden" name="key" value="{key}">
                    <div style="margin-bottom: 20px;">
                        <label>自定义值：</label>
                        <input type="text" name="value" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;">
                    </div>
                    <div style="margin-bottom: 20px;">
                        <label>选择环境：</label>
                        {' '.join(f'<label style="display: inline-block; margin-right: 20px;"><input type="checkbox" name="env" value="{env}" checked> {env}</label>' for env in envs)}
                    </div>
                    <button type="submit" class="btn-primary">🎯 应用自定义值</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

def render_result(ctx):
    key = ctx.get("key", "")
    updated = ctx.get("updated", 0)
    failed = ctx.get("failed", [])
    total = ctx.get("total", 0)
    value = ctx.get("value", "")
    is_custom = ctx.get("is_custom", False)
    
    failed_html = ""
    if failed:
        failed_html = f"<p style='color: #c00; margin-top: 10px;'>⚠️ 失败环境: {', '.join(failed)}</p>"
    
    mode = "自定义值" if is_custom else "推荐值"
    
    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; margin: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
            .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 30px; text-align: center; }}
            .success {{ color: #00aa00; font-size: 48px; margin-bottom: 20px; }}
            h2 {{ color: #333; margin: 0 0 10px 0; }}
            .summary {{ background: #f9f9f9; padding: 20px; border-radius: 4px; margin: 20px 0; }}
            .summary p {{ margin: 8px 0; color: #666; }}
            .summary strong {{ color: #333; }}
            a {{ color: #0066cc; text-decoration: none; font-weight: 500; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <div class="success">✅</div>
                <h2>配置已应用</h2>
                <div class="summary">
                    <p><strong>键名:</strong> {key}</p>
                    <p><strong>值:</strong> <code>{value}</code></p>
                    <p><strong>模式:</strong> {mode}</p>
                    <p><strong>更新:</strong> {updated}/{total} 个环境</p>
                    {failed_html}
                </div>
                <p><a href="/">← 返回首页</a> | <a href="/list">查看所有配置</a></p>
            </div>
        </div>
    </body>
    </html>
    """

def render_list(ctx):
    data = ctx.get("data", {})
    envs = ctx.get("envs", [])
    
    envs_html = ""
    for env in envs:
        env_data = data.get(env, {})
        rows = "".join([
            f"<tr><td>{k}</td><td style='font-family: monospace;'>{v}</td></tr>"
            for k, v in sorted(env_data.items())
        ])
        
        envs_html += f"""
        <h3 style="margin-top: 30px; color: #333;">{env.upper()}</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
            <tr style="background: #f9f9f9;">
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;">键</th>
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;">值</th>
            </tr>
            {rows}
        </table>
        """
    
    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
            .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
            .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 30px; }}
            h1 {{ color: #333; }}
            p {{ color: #666; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h1>📋 所有环境配置</h1>
                <p><a href="/">← 返回首页</a></p>
                {envs_html}
                <p style="margin-top: 30px;"><a href="/">← 返回首页</a></p>
            </div>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    print("🚀 启动环境变量管理 Web 工具...")
    print("📱 访问地址: http://127.0.0.1:5051")
    print("⚠️  按 Ctrl+C 停止服务器\n")
    uvicorn.run(app, host="127.0.0.1", port=5051)
