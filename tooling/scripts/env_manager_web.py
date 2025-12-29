#!/usr/bin/env python3
"""
🌐 环境变量管理 Web 工具（简版）
- 列出各环境文件
- 输入键名，给出分组建议（AI可选）
- 勾选环境并一键应用推荐值

运行: python tooling/scripts/env_manager_web.py
访问: http://127.0.0.1:5051
"""
import re
import json
import os
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

ROOT = Path(__file__).resolve().parent.parent.parent
TOOLING_ENV = ROOT / "tooling" / "env"
ENV_EXAMPLE = ROOT / ".env.example"
FILES = {
    "dev": TOOLING_ENV / "local.dev.env",
    "test": TOOLING_ENV / "local.test.env",
    "demo": TOOLING_ENV / "local.demo.env",
    "prod": TOOLING_ENV / "production.env",
}

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="env-manager-secret")

def recommend(key: str):
    k = key.upper()
    if k == "SKIP_DB_INIT":
        return {"dev":"0","test":"0","demo":"0","prod":"1"}
    if k == "SECURE_MODE":
        return {"dev":"0","test":"0","demo":"0","prod":"1"}
    if k == "DEBUG":
        return {"dev":"True","test":"True","demo":"True","prod":"False"}
    if k == "DEFAULT_ADMIN_PASSWORD":
        return {"dev":"MIMASHI123","test":"MIMASHI123","demo":"MIMASHI123","prod":""}
    return {"dev":"","test":"","demo":"","prod":""}

async def ai_suggest(key: str, current: dict):
    url = os.getenv("ENV_AI_SUGGEST_URL")
    if not url:
        return None
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.post(url, json={"key": key, "current": current})
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict):
                    return data
    except Exception:
        return None
    return None

@app.get("/", response_class=HTMLResponse)
async def index():
    html = """
    <html><head><title>Env Manager</title>
    <style>body{font-family:Arial;margin:24px}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:6px}</style>
    </head><body>
    <h2>环境变量管理（Web简版）</h2>
    <form method="post" action="/analyze">
      <label>键名：</label>
      <input name="key" placeholder="如: SKIP_DB_INIT" style="width:280px" />
      <button type="submit">分析</button>
    </form>
    <p>环境文件位置：tooling/env/*.env</p>
    </body></html>
    """
    return HTMLResponse(html)

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(key: str = Form(...)):
    # 收集当前值
    current = {}
    for env, path in FILES.items():
        val = "(未配置)"
        if path.exists():
            content = path.read_text(encoding="utf-8")
            m = re.search(rf"^{re.escape(key)}=(.*)$", content, re.MULTILINE)
            if m:
                val = m.group(1)
        current[env] = val

    rec = await ai_suggest(key, current) or recommend(key)

    rows = "".join([f"<tr><td>{env}</td><td>{current.get(env)}</td><td>{rec.get(env,'')}</td><td><input type='checkbox' name='env' value='{env}' checked></td></tr>" for env in ("dev","test","demo","prod")])
    html = f"""
    <html><head><title>分析结果</title></head><body>
    <h3>键名：{key}</h3>
    <form method="post" action="/apply">
      <input type="hidden" name="key" value="{key}" />
      <table>
        <tr><th>环境</th><th>当前值</th><th>推荐值</th><th>应用</th></tr>
        {rows}
      </table>
      <p><button type="submit">应用推荐值</button> <a href='/'>返回</a></p>
    </form>
    </body></html>
    """
    return HTMLResponse(html)

@app.post("/apply")
async def apply(request: Request):
    form = await request.form()
    key = form.get("key")
    envs = form.getlist("env")
    rec = recommend(key)
    updated = 0
    for env in envs:
        path = FILES.get(env)
        if not path or not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        val = rec.get(env, "")
        if re.search(rf"^{re.escape(key)}=", content, re.MULTILINE):
            new_content = re.sub(rf"^{re.escape(key)}=.*$", f"{key}={val}", content, flags=re.MULTILINE)
        else:
            new_content = content + f"\n{key}={val}\n"
        if new_content != content:
            path.write_text(new_content, encoding="utf-8")
            updated += 1
    return RedirectResponse(url=f"/result?updated={updated}", status_code=302)

@app.get("/result", response_class=HTMLResponse)
async def result(updated: int = 0):
    return HTMLResponse(f"<html><body><h3>已更新 {updated} 个环境文件</h3><p><a href='/'>返回</a></p></body></html>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5051)
