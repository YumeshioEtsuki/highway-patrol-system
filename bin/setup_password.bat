@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo.
echo ========================================
echo   🔐 数据库密码配置向导
echo ========================================
echo.

REM 检查 .env 文件是否存在
if exist ".env" (
    echo [信息] 检测到已存在 .env 文件
    set /p overwrite="是否覆盖？(y/N): "
    if /i not "!overwrite!"=="y" (
        echo [取消] 保持现有配置
        goto :CheckPassword
    )
)

REM 复制模板
echo [步骤 1/2] 从 .env.example 创建 .env 文件...
copy /y ".env.example" ".env" >nul 2>&1
if errorlevel 1 (
    echo [错误] 无法创建 .env 文件，请检查 .env.example 是否存在
    pause
    exit /b 1
)
echo [完成] .env 文件已创建

:CheckPassword
echo.
echo [步骤 2/2] 设置数据库密码
echo.
echo 请输入您的 MySQL root 密码:
set /p db_password="密码: "

if "!db_password!"=="" (
    echo [警告] 密码不能为空！
    goto :CheckPassword
)

REM 更新 .env 文件中的密码
echo [处理] 更新 DATABASE_PASSWORD...
powershell -Command "(Get-Content .env) -replace 'DATABASE_PASSWORD=.*', 'DATABASE_PASSWORD=!db_password!' | Set-Content .env"

if errorlevel 1 (
    echo [错误] 更新失败，请手动编辑 .env 文件
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✅ 配置完成！
echo ========================================
echo.
echo 下一步：启动系统
echo   bin\startup_full.bat   (完整功能)
echo   bin\startup.bat        (基础功能)
echo.
echo ⚠️ 重要提示：
echo   - .env 文件已被 .gitignore 排除
echo   - 永远不要提交 .env 到 Git
echo   - 如需团队共享配置，请通过安全渠道传递
echo.

pause
