@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:start
echo.
echo ============================================================
echo Highway Patrol System - Quick Start Menu
echo ============================================================
echo.
echo [Core Functions]
echo   1. Quick Start (Dev Mode)
echo   2. Full Start (Redis + Celery + FastAPI)
echo   3. Database Check
echo.
echo [Dev Tools]
echo   4. Config Manager (Web/CLI)
echo.
echo   0. Exit
echo.
echo ============================================================
echo.

set /p choice="Select (0-4): "

if "%choice%"=="1" (
    call "%~dp0startup.bat"
    goto :start
) else if "%choice%"=="2" (
    call "%~dp0startup_full.bat"
    goto :start
) else if "%choice%"=="3" (
    cd /d "%~dp0.."
    python check_db.py
    pause
    goto :start
) else if "%choice%"=="4" (
    echo.
    echo ============================================================
    echo Config Manager
    echo ============================================================
    echo   1. Web UI (Recommended)
    echo   2. CLI
    echo   0. Back to Main Menu
    echo ============================================================
    set /p tool_choice="Select: "
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
    echo Invalid choice
    pause
    goto :start
)
