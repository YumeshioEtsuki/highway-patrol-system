@echo off
chcp 65001 >nul
title 公路巡查系统 - 一键启动

echo ============================================================
echo 🚀 公路巡查系统快速启动
echo ============================================================
echo.

echo [1/3] 检查端口 5000...
netstat -ano | findstr ":5000 " >nul 2>&1
if %errorlevel% == 0 (
    echo [WARN] 端口 5000 被占用，正在清理...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000 "') do (
        taskkill /PID %%a /F >nul 2>&1
        echo [OK] 已停止进程 %%a
    )
    timeout /t 2 /nobreak >nul
) else (
    echo [OK] 端口 5000 可用
)

echo.
echo [2/3] 切换到后端目录...
cd /d "%~dp01-后端代码"
if %errorlevel% neq 0 (
    echo [ERROR] 无法找到后端目录
    pause
    exit /b 1
)
echo [OK] 当前目录: %cd%

echo.
echo [3/3] 启动 FastAPI 服务器...
echo ============================================================
echo.
set SKIP_DB_INIT=1
python -m uvicorn app:app --host 0.0.0.0 --port 5000

pause
