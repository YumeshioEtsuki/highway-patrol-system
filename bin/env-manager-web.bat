@echo off
chcp 65001 >nul

echo ============================================================
echo 🌐 环境变量管理工具 - Web 版
echo ============================================================
echo.
echo 📱 启动地址: http://127.0.0.1:5051
echo.
echo 按 Ctrl+C 停止服务器
echo ============================================================
echo.

REM 进入项目根目录
cd /d "%~dp0..\..\..\"

REM 检查虚拟环境
if not exist ".venv" (
    echo ❌ 虚拟环境不存在！
    echo 请先运行: python -m venv .venv
    pause
    exit /b 1
)

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 检查依赖
python -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo ⏳ 安装依赖中...
    pip install fastapi uvicorn -q
)

REM 启动Web服务
echo ⏳ 启动服务...
python tooling\scripts\web\app.py

pause
