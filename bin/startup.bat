@echo off
chcp 65001 >nul
title 公路巡查系统 - 一键启动

echo ============================================================
echo 🚀 公路巡查系统快速启动（开发模式）
echo ============================================================
echo.

REM 统一到项目根目录，避免从 system32 等目录运行导致找不到 .env
cd /d "%~dp0.."

REM 检查配置文件（后端实际读取 1-后端代码/.env）
echo [0/3] 检查环境配置...
if "%BOOTSTRAP_ADMIN%"=="1" (
    if "%SECURE_MODE%"=="1" (
        powershell -Command "Write-Host '[警告] BOOTSTRAP_ADMIN=1 在 SECURE_MODE 下会被忽略，请改回 0 并改用 bin/create_admin.py 创建管理员' -ForegroundColor Red"
    ) else (
        powershell -Command "Write-Host '[提示] BOOTSTRAP_ADMIN=1 仅用于临时创建默认管理员，完成后请改回 0；若已存在 admin 会被初始化逻辑自动跳过' -ForegroundColor Yellow"
    )
)

if "%SECURE_MODE%"=="1" (
    echo [INFO] 安全模式已启用：跳过 .env 文件读取，改为使用系统环境变量
    if "%DB_PASSWORD%"=="" if "%DATABASE_PASSWORD%"=="" (
        echo [错误] 安全模式下未检测到 DB_PASSWORD 或 DATABASE_PASSWORD 环境变量！
        echo 请在当前会话或系统中设置其中一个变量后再启动。
        echo 例如：
        echo   set DB_PASSWORD=your_password
        echo 或:
        echo   set DATABASE_PASSWORD=your_password
        pause
        exit /b 1
    )
) else (
    if not exist "1-后端代码\.env" (
        echo [错误] 未检测到 1-后端代码\.env 配置文件！
        echo.
        echo 请先运行配置向导：
        echo    bin\setup_password.bat
        echo.
        echo 或手动创建：
        echo    copy 1-后端代码\.env.example 1-后端代码\.env
        echo    然后编辑 1-后端代码\.env 设置 DATABASE_PASSWORD
        echo.
        pause
        exit /b 1
    )
    echo [OK] 后端 .env 配置文件已存在
    echo.
)

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
cd /d "%~dp0..\1-后端代码"
if %errorlevel% neq 0 (
    echo [ERROR] 无法找到后端目录
    pause
    exit /b 1
)
echo [OK] 当前目录: %cd%

echo.
echo [3/3] 启动 FastAPI 服务器（开发模式，自动重载）...
echo ============================================================
echo.
set SKIP_DB_INIT=1
python -m uvicorn app:app --host 0.0.0.0 --port 5000 --reload --log-level debug

pause
