@echo off
chcp 65001 >nul

echo.
echo ============================================================
echo � 公路巡查系统 - 快速启动菜单
echo ============================================================
echo.
echo 【核心功能】
echo   1. 🚀 快速启动（开发模式）
echo   2. 🚀 完整启动（Redis + Celery + FastAPI）
echo   3. 📊 数据库检查
echo.
echo 【开发工具】
echo   4. 🔧 配置管理工具（Web/CLI）
echo.
echo   0. 退出
echo.
echo ============================================================
echo.

set /p choice="请选择 (0-4): "

if "%choice%"=="1" (
    call "%~dp0startup.bat"
) else if "%choice%"=="2" (
    call "%~dp0startup_full.bat"
) else if "%choice%"=="3" (
    cd /d "%~dp0.."
    python check_db.py
    pause
) else if "%choice%"=="4" (
    echo.
    echo ============================================================
    echo 🔧 配置管理工具
    echo ============================================================
    echo   1. 🌐 Web 界面（推荐）
    echo   2. 📟 命令行界面
    echo   0. 返回主菜单
    echo ============================================================
    set /p tool_choice="请选择: "
    if "!tool_choice!"=="1" (
        call "%~dp0env-manager-web.bat"
    ) else if "!tool_choice!"=="2" (
        cd /d "%~dp0..\tooling\scripts"
        python manage_env.py
        pause
    )
    goto :start
) else if "%choice%"=="0" (
    exit /b 0
) else (
    echo ❌ 无效选择
    pause
    goto :start
)
