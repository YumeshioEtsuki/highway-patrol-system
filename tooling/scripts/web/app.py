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

from lib import EnvManager, get_recommendations, validate_config, get_help_text

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
    """Home page"""
    all_keys = manager.get_all_keys()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "all_keys": list(all_keys),
        "envs": ["dev", "test", "demo", "prod"],
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
    
    current = manager.get_current_values(key)
    recommend = get_recommendations(key)
    help_text = get_help_text(key)
    
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
    recommend = get_recommendations(key)
    
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


if __name__ == "__main__":
    import uvicorn
    print("Starting Environment Variable Manager Web Tool...")
    print("Access URL: http://127.0.0.1:5051")
    print("Press Ctrl+C to stop")
    uvicorn.run(app, host="127.0.0.1", port=5051)
