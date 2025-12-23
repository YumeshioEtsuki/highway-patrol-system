#!/usr/bin/env powershell
# Celery 任务队列完整测试脚本

Write-Host ""
Write-Host "█" * 60 -ForegroundColor Cyan
Write-Host "  Celery 任务队列启动和测试" -ForegroundColor Cyan
Write-Host "█" * 60 -ForegroundColor Cyan
Write-Host ""

# Step 1: 验证 Redis
Write-Host "Step 1: 验证 Redis 连接..." -ForegroundColor Yellow
$redisCheck = python -c "import redis; r = redis.Redis(host='localhost', port=6379); r.ping()" 2>&1
if ($redisCheck -eq "True") {
    Write-Host "✓ Redis 连接成功" -ForegroundColor Green
} else {
    Write-Host "✗ Redis 连接失败" -ForegroundColor Red
    Write-Host "  请确保 Redis 已启动"
    exit 1
}

# Step 2: 启动后端
Write-Host ""
Write-Host "Step 2: 启动 FastAPI 后端..." -ForegroundColor Yellow
Write-Host "  服务地址: http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "  Swagger UI: http://127.0.0.1:5000/docs" -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; Set-Item env:SKIP_DB_INIT 1; uvicorn app:app --host 0.0.0.0 --port 5000 --log-level warning" -WindowStyle Minimized

Write-Host "✓ 后端已在后台启动（最小化窗口）" -ForegroundColor Green

# Step 3: 启动 Worker
Write-Host ""
Write-Host "Step 3: 启动 Celery Worker..." -ForegroundColor Yellow
Write-Host "  队列: photo, ai, report, maintenance" -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; celery -A celery_app worker --loglevel=warning --pool=solo -Q photo,ai,report,maintenance" -WindowStyle Minimized

Write-Host "✓ Worker 已在后台启动（最小化窗口）" -ForegroundColor Green

# Step 4: 等待服务启动
Write-Host ""
Write-Host "Step 4: 等待服务完全启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Step 5: 运行测试
Write-Host ""
Write-Host "Step 5: 运行功能测试..." -ForegroundColor Yellow
Write-Host "─" * 60

python test_celery_tasks.py

Write-Host ""
Write-Host "─" * 60
Write-Host ""
Write-Host "测试完成！" -ForegroundColor Green
Write-Host ""
Write-Host "后续步骤:" -ForegroundColor Cyan
Write-Host "  1. 查看 Flower 监控面板: http://127.0.0.1:5555" -ForegroundColor White
Write-Host "  2. 测试 API: http://127.0.0.1:5000/docs" -ForegroundColor White
Write-Host "  3. 在浏览器中尝试提交任务并查看实时进度" -ForegroundColor White
Write-Host ""
Write-Host "如需停止服务:" -ForegroundColor Yellow
Write-Host "  关闭上面打开的两个最小化窗口（后端和 Worker）" -ForegroundColor White
Write-Host ""
