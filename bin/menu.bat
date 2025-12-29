@echo off
chcp 65001 >nul

echo.
echo ============================================================
echo 🔧 开发工具菜单
echo ============================================================
echo.
echo 选择要启动的工具：
echo.
echo   1. 🌐 Web 环境变量管理工具 (推荐)
echo   2. 📟 CLI 环境变量管理工具
echo   3. 🚀 项目启动（快速开发）
echo   4. 🚀 项目启动（完整）
echo   5. 📊 数据库检查
echo.
echo   0. 退出
echo.
echo ============================================================
echo.

set /p choice="请选择 (0-5): "

if "%choice%"=="1" (
    call "%~dp0env-manager-web.bat"
) else if "%choice%"=="2" (
    cd /d "%~dp0..\tooling\scripts"
    python manage_env.py
    pause
) else if "%choice%"=="3" (
    call "%~dp0startup.bat"
) else if "%choice%"=="4" (
    call "%~dp0startup_full.bat"
) else if "%choice%"=="5" (
    cd /d "%~dp0.."
    python check_db.py
    pause
) else if "%choice%"=="0" (
    exit /b 0
) else (
    echo ❌ 无效选择
    pause
    goto :start
)
