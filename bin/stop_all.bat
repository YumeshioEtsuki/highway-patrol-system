@echo off
chcp 65001 >nul
title 停止所有服务

echo ============================================================
echo 🛑 停止高速公路巡查系统所有服务
echo ============================================================
echo.

REM 停止 FastAPI (端口 5000)
echo [1/3] 停止 FastAPI 服务器...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000 "') do (
    taskkill /PID %%a /F >nul 2>&1
    echo [OK] 已停止 FastAPI 进程 (PID: %%a)
)

REM 停止 Celery Worker
echo.
echo [2/3] 停止 Celery Worker...
taskkill /FI "WINDOWTITLE eq Celery Worker*" /F >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Celery Worker 已停止
) else (
    echo [INFO] 没有运行中的 Celery Worker
)

REM 停止 Redis
echo.
echo [3/3] 停止 Redis 服务器...

REM 停止 Docker Redis
docker ps --filter "name=highway-redis" --format "{{.Names}}" | findstr "highway-redis" >nul 2>&1
if %errorlevel% == 0 (
    docker stop highway-redis >nul 2>&1
    if %errorlevel% == 0 (
        echo [OK] Docker Redis 已停止
    ) else (
        echo [INFO] Docker Redis 停止失败或不存在
    )
) else (
    REM 停止本地 Redis
    taskkill /IM redis-server.exe /F >nul 2>&1
    if %errorlevel% == 0 (
        echo [OK] 本地 Redis Server 已停止
    ) else (
        echo [INFO] 没有运行中的 Redis Server
    )
)

echo.
echo ============================================================
echo ✅ 所有服务已停止
echo ============================================================
pause
