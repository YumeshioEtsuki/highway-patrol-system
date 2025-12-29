@echo off
chcp 65001 >nul
title Redis Docker 启动脚本

echo ============================================================
echo 🐳 Redis Docker 启动脚本
echo ============================================================
echo.

REM 检查 Docker 是否安装
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker 未安装！
    echo.
    echo 请先安装 Docker Desktop for Windows:
    echo https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

echo [OK] Docker 已安装
echo.

REM 检查 Docker 是否运行
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker 未运行！
    echo.
    echo 请先启动 Docker Desktop，然后重试
    echo.
    pause
    exit /b 1
)

echo [OK] Docker 正在运行
echo.

REM 检查是否已有 highway-redis 容器
docker ps -a --filter "name=highway-redis" --format "{{.Names}}" | findstr "highway-redis" >nul 2>&1
if %errorlevel% == 0 (
    echo [INFO] 检测到已存在的 Redis 容器
    
    REM 检查容器是否在运行
    docker ps --filter "name=highway-redis" --format "{{.Names}}" | findstr "highway-redis" >nul 2>&1
    if %errorlevel% == 0 (
        echo [OK] Redis 容器已在运行
        docker ps --filter "name=highway-redis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    ) else (
        echo [INFO] 启动已存在的 Redis 容器...
        docker start highway-redis
        if %errorlevel% == 0 (
            echo [OK] Redis 容器启动成功
        ) else (
            echo [ERROR] Redis 容器启动失败
            pause
            exit /b 1
        )
    )
) else (
    echo [INFO] 创建并启动新的 Redis 容器...
    echo.
    echo 容器配置:
    echo   - 名称: highway-redis
    echo   - 镜像: redis:7-alpine
    echo   - 端口: 6379:6379
    echo   - 持久化: 已启用 (AOF)
    echo   - 自动重启: 是
    echo.
    
    docker run -d ^
        --name highway-redis ^
        -p 6379:6379 ^
        -v redis-data:/data ^
        --restart unless-stopped ^
        redis:7-alpine redis-server --appendonly yes
    
    if %errorlevel% == 0 (
        echo [OK] Redis 容器创建成功
        timeout /t 2 /nobreak >nul
    ) else (
        echo [ERROR] Redis 容器创建失败
        pause
        exit /b 1
    )
)

echo.
echo ============================================================
echo ✅ Redis 已就绪
echo ============================================================
echo.
echo 📊 容器信息:
docker ps --filter "name=highway-redis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo 🔧 测试连接...
docker exec highway-redis redis-cli ping >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Redis 连接测试成功 (PONG)
) else (
    echo [WARN] Redis 连接测试失败
)

echo.
echo 📖 常用命令:
echo   - 查看日志: docker logs highway-redis
echo   - 进入CLI:  docker exec -it highway-redis redis-cli
echo   - 停止容器: docker stop highway-redis
echo   - 启动容器: docker start highway-redis
echo.
echo 访问地址: localhost:6379
echo.
pause
