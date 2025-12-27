@echo off
chcp 65001 >nul
title 高速公路巡查系统 - 完整启动（Redis + Celery + FastAPI）

REM ==================================================================
REM 注意：如需在启动时自动应用数据库索引/审计表，请在命令行运行：
REM       set APPLY_INDEXES=1 && .\bin\startup_full.bat
REM 本脚本默认启用 SKIP_DB_INIT=1 以加快启动速度。
REM ==================================================================

echo ============================================================
echo 🚀 高速公路巡查系统 - 完整启动
echo ============================================================
echo.
echo This script will start in order:
echo   1. Redis Server (port 6379)
echo   2. Celery Worker (async tasks)
echo   3. FastAPI Server (port 5000)
echo.
echo ============================================================
echo.

REM ===============================
REM 检查 Redis 是否已安装
REM ===============================
echo [1/5] 检查 Redis...

REM 优先检查 Docker
where docker >nul 2>&1
if %errorlevel% == 0 (
    docker ps >nul 2>&1
    if %errorlevel% == 0 (
        echo [OK] Docker 可用，将使用 Docker Redis
        set USE_DOCKER_REDIS=1
        goto redis_check_done
    )
)

REM 检查本地 Redis
where redis-server >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] 未检测到 redis-server 或 Docker，建议安装！
    echo.
    echo 📥 快速安装方式（推荐）：
    echo    使用 Docker: .\bin\start_redis.bat
    echo.
    echo 📥 其他安装方式：
    echo    1. Windows版本: https://github.com/microsoftarchive/redis/releases
    echo    2. WSL2安装: sudo apt install redis-server
    echo    3. 查看完整指南: .\bin\REDIS_DOCKER_GUIDE.md
    echo.
    echo ⏭️  跳过 Redis，继续启动其他服务（功能会降级）
    timeout /t 5 /nobreak
    set USE_DOCKER_REDIS=0
) else (
    echo [OK] Redis 本地版本已安装
    set USE_DOCKER_REDIS=0
)

:redis_check_done

REM ===============================
REM 启动 Redis（后台运行）
REM ===============================
echo.
echo [2/5] 启动 Redis 服务器...

if "%USE_DOCKER_REDIS%"=="1" (
    REM 使用 Docker Redis
    docker ps --filter "name=highway-redis" --format "{{.Names}}" | findstr "highway-redis" >nul 2>&1
    if %errorlevel% == 0 (
        echo [OK] Docker Redis 已在运行
    ) else (
        docker ps -a --filter "name=highway-redis" --format "{{.Names}}" | findstr "highway-redis" >nul 2>&1
        if %errorlevel% == 0 (
            echo [INFO] 启动已存在的 Docker Redis 容器...
            docker start highway-redis >nul 2>&1
            timeout /t 2 /nobreak >nul
            echo [OK] Docker Redis 启动成功（端口 6379）
        ) else (
            echo [INFO] 创建并启动 Docker Redis 容器...
            docker run -d --name highway-redis -p 6379:6379 -v redis-data:/data --restart unless-stopped redis:7-alpine redis-server --appendonly yes >nul 2>&1
            timeout /t 3 /nobreak >nul
            echo [OK] Docker Redis 创建并启动成功（端口 6379）
        )
    )
) else (
    REM 使用本地 Redis
    tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
    if %errorlevel% == 0 (
        echo [OK] 本地 Redis 已在运行
    ) else (
        REM 尝试多种方式查找 Redis
        where redis-server >nul 2>&1
        if %errorlevel% == 0 (
            start "Redis Server" /MIN redis-server --port 6379
            timeout /t 2 /nobreak >nul
            echo [OK] 本地 Redis 启动成功（端口 6379）
        ) else (
            REM 检查常见安装路径
            if exist "C:\Redis\redis-server.exe" (
                start "Redis Server" /MIN "C:\Redis\redis-server.exe" --port 6379
                timeout /t 2 /nobreak >nul
                echo [OK] Redis 启动成功（从 C:\Redis）
            ) else if exist "C:\Program Files\Redis\redis-server.exe" (
                start "Redis Server" /MIN "C:\Program Files\Redis\redis-server.exe" --port 6379
                timeout /t 2 /nobreak >nul
                echo [OK] Redis 启动成功（从 Program Files）
            ) else (
                echo [SKIP] Redis 未找到，跳过（功能会降级到内存缓存）
                echo [TIP] 运行 .\bin\start_redis.bat 使用 Docker 快速安装
            )
        )
    )
)

REM ===============================
REM 检查端口 5000
REM ===============================
echo.
echo [3/5] 检查端口 5000...
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

REM ===============================
REM 切换到后端目录
REM ===============================
echo.
echo [4/5] 切换到后端目录...
cd /d "%~dp0..\1-后端代码"
if %errorlevel% neq 0 (
    echo [ERROR] 无法找到后端目录
    pause
    exit /b 1
)
echo [OK] 当前目录: %cd%

REM ===============================
REM 启动 Celery Worker（后台运行）
REM ===============================
echo.
echo [5/5] 启动 Celery Worker...

REM 检查是否已有 Celery Worker 运行
tasklist /FI "WINDOWTITLE eq Celery Worker*" 2>NUL | find /I /N "python">NUL
if %errorlevel% == 0 (
    echo [OK] Celery Worker 已在运行
) else (
    REM 启动 Celery Worker（新窗口）- 使用 python -m 方式避免 PATH 问题
    start "Celery Worker" cmd /k "title Celery Worker - 异步任务队列 && python -m celery -A celery_app worker --loglevel=info --pool=solo"
    timeout /t 3 /nobreak >nul
    echo [OK] Celery Worker 已启动（新窗口）
)

REM ===============================
REM 启动 FastAPI 服务器（当前窗口）
REM ===============================
echo.
echo ============================================================
echo ✅ 前置服务已启动：
echo    - Redis Server (端口 6379)
echo    - Celery Worker (异步任务)
echo.
echo 🚀 正在启动 FastAPI 服务器...
echo ============================================================
echo.
set SKIP_DB_INIT=1
set APPLY_INDEXES=1
setlocal
if "%APPLY_INDEXES%"=="1" (
    set APPLY_INDEXES_ON_START=1
)
python bin\start_server.py --skip-db-init
endlocal

REM 如果 FastAPI 退出，提示用户
echo.
echo [INFO] FastAPI 服务器已停止
pause
