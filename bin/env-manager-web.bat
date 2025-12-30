@echo off
chcp 65001 >nul

echo ============================================================
echo Environment Variable Manager - Web Version
echo ============================================================
echo.
echo Access: http://127.0.0.1:5051
echo.
echo Press Ctrl+C to stop server
echo ============================================================
echo.

cd /d "%~dp0.."

if not exist ".venv" (
    echo [ERROR] Virtual environment not found
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

python -c "import fastapi, uvicorn, jinja2" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install fastapi uvicorn jinja2 -q
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [INFO] Starting web server...
python tooling\scripts\web\env_manager_app.py

pause
