@echo off
REM 环境变量管理工具启动脚本（Windows）
REM 用法: 双击运行或命令行运行 manage_env.bat

chcp 65001 >nul
cls

title 环境变量管理工具

setlocal enabledelayedexpansion

REM 获取当前目录
cd /d "%~dp0"

REM 检查是否在正确的目录
if not exist "add_config.py" (
    echo ❌ 错误: 未找到 add_config.py
    echo 请在 tooling\scripts 目录中运行此脚本
    pause
    exit /b 1
)

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    echo 请确保 Python 已安装并添加到 PATH
    pause
    exit /b 1
)

REM 运行管理工具
echo.
echo 🚀 启动环境变量管理工具...
echo.

python manage_env.py

pause
