#!/usr/bin/env pwsh
<#
环境变量管理工具启动脚本（PowerShell）
用法: .\manage_env.ps1 或直接运行
#>

# 获取当前目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 检查是否在正确的目录
if (-not (Test-Path "add_config.py")) {
    Write-Host "❌ 错误: 未找到 add_config.py" -ForegroundColor Red
    Write-Host "请在 tooling\scripts 目录中运行此脚本"
    Read-Host "按 Enter 退出"
    exit 1
}

# 检查Python
try {
    python --version | Out-Null
} catch {
    Write-Host "❌ 错误: 未找到 Python" -ForegroundColor Red
    Write-Host "请确保 Python 已安装并添加到 PATH"
    Read-Host "按 Enter 退出"
    exit 1
}

# 运行管理工具
Write-Host ""
Write-Host "🚀 启动环境变量管理工具..." -ForegroundColor Green
Write-Host ""

python manage_env.py

Read-Host "按 Enter 退出"
