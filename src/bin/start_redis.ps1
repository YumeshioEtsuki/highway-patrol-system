# Redis 启动脚本（PowerShell）
# 用于快速启动 Redis 服务

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Redis 启动脚本" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 是否安装
Write-Host "[→] 检查 Docker 环境..." -ForegroundColor Yellow
$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue

if ($dockerInstalled) {
    Write-Host "[✓] Docker 已安装" -ForegroundColor Green
    
    # 检查 Redis 容器是否存在
    Write-Host "[→] 检查 Redis 容器..." -ForegroundColor Yellow
    $redisContainer = docker ps -a --filter "name=redis-celery" --format "{{.Names}}"
    
    if ($redisContainer -eq "redis-celery") {
        Write-Host "[✓] Redis 容器已存在" -ForegroundColor Green
        
        # 检查容器是否运行
        $isRunning = docker ps --filter "name=redis-celery" --format "{{.Names}}"
        
        if ($isRunning -eq "redis-celery") {
            Write-Host "[!] Redis 容器已在运行" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "如需重启，请运行:" -ForegroundColor Yellow
            Write-Host "  docker restart redis-celery" -ForegroundColor White
        } else {
            Write-Host "[→] 启动 Redis 容器..." -ForegroundColor Yellow
            docker start redis-celery
            Start-Sleep -Seconds 2
            Write-Host "[✓] Redis 容器已启动" -ForegroundColor Green
        }
    } else {
        Write-Host "[→] 创建并启动 Redis 容器..." -ForegroundColor Yellow
        docker run -d --name redis-celery -p 6379:6379 redis:7-alpine
        Start-Sleep -Seconds 3
        Write-Host "[✓] Redis 容器已创建并启动" -ForegroundColor Green
    }
    
    # 验证 Redis 连接
    Write-Host ""
    Write-Host "[→] 验证 Redis 连接..." -ForegroundColor Yellow
    Start-Sleep -Seconds 1
    
    $pingResult = redis-cli ping 2>&1
    if ($pingResult -match "PONG") {
        Write-Host "[✓] Redis 连接成功！" -ForegroundColor Green
        Write-Host ""
        Write-Host "Redis 服务信息:" -ForegroundColor Cyan
        Write-Host "  地址: localhost:6379" -ForegroundColor White
        Write-Host "  容器: redis-celery" -ForegroundColor White
        Write-Host ""
        Write-Host "管理命令:" -ForegroundColor Cyan
        Write-Host "  查看日志: docker logs redis-celery" -ForegroundColor White
        Write-Host "  停止服务: docker stop redis-celery" -ForegroundColor White
        Write-Host "  重启服务: docker restart redis-celery" -ForegroundColor White
    } else {
        Write-Host "[✗] Redis 连接失败" -ForegroundColor Red
        Write-Host "错误信息: $pingResult" -ForegroundColor Red
        Write-Host ""
        Write-Host "故障排查:" -ForegroundColor Yellow
        Write-Host "  1. 检查容器状态: docker ps -a" -ForegroundColor White
        Write-Host "  2. 查看容器日志: docker logs redis-celery" -ForegroundColor White
        Write-Host "  3. 检查端口占用: netstat -ano | findstr :6379" -ForegroundColor White
    }
} else {
    Write-Host "[✗] Docker 未安装" -ForegroundColor Red
    Write-Host ""
    Write-Host "请选择以下方式之一安装 Redis:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "方式 1: 安装 Docker Desktop（推荐）" -ForegroundColor Cyan
    Write-Host "  1. 下载: https://www.docker.com/products/docker-desktop" -ForegroundColor White
    Write-Host "  2. 安装后重启计算机" -ForegroundColor White
    Write-Host "  3. 重新运行此脚本" -ForegroundColor White
    Write-Host ""
    Write-Host "方式 2: 使用 Memurai（Windows 原生 Redis）" -ForegroundColor Cyan
    Write-Host "  1. 下载: https://www.memurai.com/get-memurai" -ForegroundColor White
    Write-Host "  2. 安装后自动作为服务运行" -ForegroundColor White
    Write-Host "  3. 默认监听 127.0.0.1:6379" -ForegroundColor White
    Write-Host ""
    Write-Host "方式 3: 使用 WSL2 + Redis（Linux 环境）" -ForegroundColor Cyan
    Write-Host "  1. 启用 WSL2: wsl --install" -ForegroundColor White
    Write-Host "  2. 安装 Redis: sudo apt install redis-server" -ForegroundColor White
    Write-Host "  3. 启动服务: sudo service redis-server start" -ForegroundColor White
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
