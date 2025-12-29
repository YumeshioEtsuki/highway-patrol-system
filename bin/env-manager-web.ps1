# 环境变量管理工具 - Web 版启动脚本（PowerShell）

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🌐 环境变量管理工具 - Web 版" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📱 启动地址: http://127.0.0.1:5051" -ForegroundColor Green
Write-Host ""
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host "============================================================"
Write-Host ""

Set-Location $ProjectRoot

# 检查虚拟环境
if (-not (Test-Path ".venv")) {
    Write-Host "❌ 虚拟环境不存在！" -ForegroundColor Red
    Write-Host "请先运行: python -m venv .venv"
    exit 1
}

# 激活虚拟环境
& ".venv/Scripts/Activate.ps1"

# 检查依赖
try {
    python -c "import fastapi, uvicorn" 2>$null
} catch {
    Write-Host "⏳ 安装依赖中..."
    pip install fastapi uvicorn -q
}

# 启动Web服务
Write-Host "⏳ 启动服务..."
python tooling\scripts\web\app.py
