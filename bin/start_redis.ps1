# Redis Docker 启动脚本 (PowerShell)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🐳 Redis Docker 启动脚本" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# 检查 Docker 是否安装
$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerInstalled) {
    Write-Host "[ERROR] Docker 未安装！" -ForegroundColor Red
    Write-Host "`n请先安装 Docker Desktop for Windows:" -ForegroundColor Yellow
    Write-Host "https://www.docker.com/products/docker-desktop/`n" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "[OK] Docker 已安装`n" -ForegroundColor Green

# 检查 Docker 是否运行
try {
    docker ps | Out-Null
    Write-Host "[OK] Docker 正在运行`n" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker 未运行！" -ForegroundColor Red
    Write-Host "`n请先启动 Docker Desktop，然后重试`n" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

# 检查是否已有容器
$existingContainer = docker ps -a --filter "name=highway-redis" --format "{{.Names}}"

if ($existingContainer -eq "highway-redis") {
    Write-Host "[INFO] 检测到已存在的 Redis 容器" -ForegroundColor Yellow
    
    # 检查容器是否在运行
    $runningContainer = docker ps --filter "name=highway-redis" --format "{{.Names}}"
    
    if ($runningContainer -eq "highway-redis") {
        Write-Host "[OK] Redis 容器已在运行" -ForegroundColor Green
        docker ps --filter "name=highway-redis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    } else {
        Write-Host "[INFO] 启动已存在的 Redis 容器..." -ForegroundColor Yellow
        docker start highway-redis | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Redis 容器启动成功" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Redis 容器启动失败" -ForegroundColor Red
            Read-Host "按回车键退出"
            exit 1
        }
    }
} else {
    Write-Host "[INFO] 创建并启动新的 Redis 容器...`n" -ForegroundColor Yellow
    Write-Host "容器配置:" -ForegroundColor Cyan
    Write-Host "  - 名称: highway-redis" -ForegroundColor White
    Write-Host "  - 镜像: redis:7-alpine" -ForegroundColor White
    Write-Host "  - 端口: 6379:6379" -ForegroundColor White
    Write-Host "  - 持久化: 已启用 (AOF)" -ForegroundColor White
    Write-Host "  - 自动重启: 是`n" -ForegroundColor White
    
    docker run -d `
        --name highway-redis `
        -p 6379:6379 `
        -v redis-data:/data `
        --restart unless-stopped `
        redis:7-alpine redis-server --appendonly yes | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Redis 容器创建成功" -ForegroundColor Green
        Start-Sleep -Seconds 2
    } else {
        Write-Host "[ERROR] Redis 容器创建失败" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "✅ Redis 已就绪" -ForegroundColor Green
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "📊 容器信息:" -ForegroundColor Cyan
docker ps --filter "name=highway-redis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`n🔧 测试连接..." -ForegroundColor Cyan
$testResult = docker exec highway-redis redis-cli ping 2>$null
if ($testResult -eq "PONG") {
    Write-Host "[OK] Redis 连接测试成功 (PONG)" -ForegroundColor Green
} else {
    Write-Host "[WARN] Redis 连接测试失败" -ForegroundColor Yellow
}

Write-Host "`n📖 常用命令:" -ForegroundColor Cyan
Write-Host "  - 查看日志: docker logs highway-redis" -ForegroundColor White
Write-Host "  - 进入CLI:  docker exec -it highway-redis redis-cli" -ForegroundColor White
Write-Host "  - 停止容器: docker stop highway-redis" -ForegroundColor White
Write-Host "  - 启动容器: docker start highway-redis" -ForegroundColor White
Write-Host "`n访问地址: localhost:6379`n" -ForegroundColor Yellow

Read-Host "按回车键继续"
