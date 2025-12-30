@echo off
chcp 65001 >nul
title 高速公路巡查系统 - 完整启动（Redis + Celery + FastAPI）

REM ==================================================================
REM 注意：如需在启动时自动应用数据库索引/审计表，请在命令行运行：
REM       set APPLY_INDEXES=1 && .\bin\startup_full.bat
REM 可通过 .env 的 SKIP_DB_INIT 或命令行 --skip-db-init 控制是否跳过数据库初始化。
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
REM 检查环境配置
REM ===============================
echo [0/6] 检查环境配置...

REM BOOTSTRAP_ADMIN 提示：仅限开发/初始化场景
if "%BOOTSTRAP_ADMIN%"=="1" (
    if "%SECURE_MODE%"=="1" (
        powershell -Command "Write-Host '[警告] BOOTSTRAP_ADMIN=1 在 SECURE_MODE 下会被忽略，请改回 0 并改用 bin/create_admin.py 创建管理员' -ForegroundColor Red"
    ) else (
        powershell -Command "Write-Host '[提示] BOOTSTRAP_ADMIN=1：将在启动时创建默认管理员' -ForegroundColor Yellow"
    )
    echo.
) else (
    echo [OK] BOOTSTRAP_ADMIN=0（使用 bin/create_admin.py 显式创建管理员）
    echo.
)

REM 同步检查后端目录下的 .env（后端实际读取此文件）
if "%SECURE_MODE%"=="1" (
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
    if not exist "%~dp0..\src\.env" (
        echo [错误] 未检测到 ..\src\.env 配置文件！
        echo.
        echo 请先运行配置向导：
        echo    bin\setup_password.bat
        echo.
        echo 或手动创建：
        echo    copy ..\\src\.env.example ..\\src\.env
        echo    然后编辑 ..\\src\.env 设置 DATABASE_PASSWORD
        echo.
        pause
        exit /b 1
    )
)

REM ===============================
REM 检查 Redis 是否已安装
REM ===============================
echo [1/6] 检查 Redis...

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
    echo    3. 查看完整指南: .\docs\ops\REDIS_DOCKER_GUIDE.md
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
echo [2/6] 启动 Redis 服务器...

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
            echo [INFO] 等待 Redis 完全启动...
            timeout /t 3 /nobreak >nul
        ) else (
            echo [INFO] 创建并启动 Docker Redis 容器...
            docker run -d --name highway-redis -p 6379:6379 -v redis-data:/data --restart unless-stopped redis:7-alpine redis-server --appendonly yes >nul 2>&1
            echo [INFO] 等待 Redis 完全启动...
            timeout /t 4 /nobreak >nul
        )
    )
    REM 确认 Redis 就绪（ping 检查）
    echo [INFO] 等待 Redis 就绪...
    for /L %%i in (1,1,15) do (
        docker exec highway-redis redis-cli ping >nul 2>&1
        if %errorlevel% == 0 (
            echo [OK] Docker Redis 已就绪（端口 6379）
            timeout /t 2 /nobreak >nul
            goto redis_ready
        )
        echo [INFO] Redis 初始化中... (%%i/15)
        timeout /t 1 /nobreak >nul
    )
    echo [WARN] Redis 启动超时，继续启动应用（缓存功能可能不可用）
    :redis_ready
    goto skip_redis_check
) else (
    REM 使用本地 Redis（如果 Docker 不可用）
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

:skip_redis_check
REM ===============================
REM 检查端口 5000
REM ===============================
echo.
echo [3/6] 检查端口 5000...
:port_check
netstat -ano | findstr ":5000 " >nul 2>&1
if %errorlevel% == 0 (
    echo [WARN] 端口 5000 被占用，正在清理...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000 "') do (
        taskkill /PID %%a /F >nul 2>&1
        echo [OK] 已停止进程 %%a
    )
    timeout /t 2 /nobreak >nul
    goto port_check
) else (
    echo [OK] 端口 5000 可用
)

REM ===============================
REM 检查 Python
REM ===============================
echo.
echo [4/6] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未检测到 Python，请安装 Python 3.10+ 并加入 PATH
    pause
    exit /b 1
)
echo [OK] Python 已安装
echo.

REM ===============================
REM 检查 Ollama（AI 模型服务）- 可选
REM ===============================
echo [4.5/6] 检查 Ollama（AI 模型服务 - 可选）...

REM 检查 Ollama 服务是否运行
timeout /t 1 /nobreak >nul
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Ollama 服务已在运行，AI 功能可用
) else (
    echo [INFO] Ollama 服务未运行（AI 聊天功能将不可用，其他功能正常）
    echo.
    echo 📥 如需使用 AI 功能，请启动 Ollama：
    echo    1. 下载和安装：https://ollama.ai
    echo    2. 启动服务：ollama serve
    echo    3. 拉取模型（首次）：ollama pull qwen:7b
    echo.
)
echo.

echo [5/6] 启动 Celery Worker...

REM 检查是否已有 Celery Worker 运行
tasklist /FI "WINDOWTITLE eq Celery Worker*" 2>NUL | find /I /N "python">NUL
if %errorlevel% == 0 (
    echo [OK] Celery Worker 已在运行
) else (
    REM 启动 Celery Worker（新窗口）- 使用 python -m 方式避免 PATH 问题
    pushd "%~dp0..\\src"
    start "Celery Worker" cmd /k "title Celery Worker - 异步任务队列 && python -m celery -A celery_app worker --loglevel=info --pool=solo"
    popd
    timeout /t 3 /nobreak >nul
    echo [OK] Celery Worker 已启动（新窗口）
)

REM ===============================
REM Wait for Redis to be ready
REM ===============================
echo.
echo [6/6] 检查 Redis 稳定性...

setlocal enabledelayedexpansion

if "%USE_DOCKER_REDIS%"=="1" (
    set "redis_ready=0"
    
    for /L %%i in (1,1,30) do (
        docker exec highway-redis redis-cli ping >nul 2>&1
        if !errorlevel! == 0 (
            set "redis_ready=1"
            echo [OK] Redis is ready
            timeout /t 3 /nobreak >nul
            goto start_fastapi
        )
        timeout /t 1 /nobreak >nul
    )
    
    if !redis_ready! == 0 (
        echo [WARN] Redis not responding - using memory cache
    )
) else (
    echo [INFO] Local Redis mode
)

:start_fastapi
endlocal

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

REM 切换到项目根目录（本脚本位于 bin/，根目录为上一层）
pushd "%~dp0\.."

REM 默认使用 dev 环境，可通过第一个参数覆盖
set ENV=%1
if "%ENV%"=="" set ENV=dev

REM 展示当前 .env 的 SKIP_DB_INIT 值（仅用于提示，不强制覆盖）
for /f "tokens=1,* delims==" %%A in ('type "%~dp0\..\.env" ^| findstr /R /C:"^SKIP_DB_INIT="') do set SKIP_DB_INIT_DISPLAY=%%B
if "%SKIP_DB_INIT_DISPLAY%"=="" set SKIP_DB_INIT_DISPLAY=(未设置)
echo [INFO] 当前 .env 中 SKIP_DB_INIT=%SKIP_DB_INIT_DISPLAY%
if "%SKIP_DB_INIT_DISPLAY%"=="1" (
    echo [WARN] 将跳过数据库初始化（可通过 --skip-db-init 或修改 .env 调整）
) else (
    echo [INFO] 将执行启动期数据库初始化检查
)

REM 透传命令行参数（例如 --skip-db-init），统一到 scripts/start_server.py 处理
set START_ENTRY=scripts\start_server.py
if not exist "%START_ENTRY%" (
    echo [ERROR] 找不到启动入口 %START_ENTRY%
    popd
    pause
    exit /b 1
)
python %START_ENTRY% --env %ENV% %*

popd

REM 如果 FastAPI 退出，提示用户
echo.
echo [INFO] FastAPI 服务器已停止
pause
