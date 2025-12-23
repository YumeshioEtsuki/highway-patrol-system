# Celery 任务队列启动脚本

echo "="*60
echo "启动 Celery Worker 和 Beat"
echo "="*60

# 启动 Celery Worker（处理异步任务）
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; celery -A celery_app worker --loglevel=info --pool=solo -Q photo,ai,report,maintenance" -WindowStyle Normal

# 等待 2 秒
Start-Sleep -Seconds 2

# 启动 Celery Beat（定时任务调度器）
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; celery -A celery_app beat --loglevel=info" -WindowStyle Normal

# 等待 2 秒
Start-Sleep -Seconds 2

# 启动 Flower（任务监控界面）
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; celery -A celery_app flower --port=5555" -WindowStyle Normal

Write-Host ""
Write-Host "✓ Celery Worker 已启动（处理任务）" -ForegroundColor Green
Write-Host "✓ Celery Beat 已启动（定时任务）" -ForegroundColor Green
Write-Host "✓ Flower 已启动（监控界面）" -ForegroundColor Green
Write-Host ""
Write-Host "访问 Flower 监控: http://localhost:5555" -ForegroundColor Cyan
Write-Host ""
Write-Host "按任意键关闭此窗口..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
