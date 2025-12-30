@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

REM 统一到项目根目录（脚本位于 bin 下，上一级为项目根）
pushd "%~dp0.."

echo.
echo ========================================
echo   🔐 数据库密码配置向导
echo ========================================
echo.

REM 安全模式提示：启用后系统将忽略 .env，仅使用系统环境变量
if /i "%SECURE_MODE%"=="1" (
    echo [信息] 检测到已启用 SECURE_MODE=1（安全模式）
    echo [提示] 在安全模式下，应用不会读取 .env 文件，推荐直接设置环境变量：
    echo         set DB_PASSWORD=your_password  或  set DATABASE_PASSWORD=your_password
    set /p continue_secure="仍要创建/更新 .env 文件吗？(y/N): "
    if /i not "!continue_secure!"=="y" (
        echo [取消] 已按安全模式跳过 .env 写入。你可直接运行启动脚本。
        popd
        pause
        exit /b 0
    )
)

REM 检查 .env 文件是否存在
if exist ".env" (
    echo [信息] 检测到已存在 .env 文件
    set /p overwrite="是否覆盖？(y/N): "
    if /i not "!overwrite!"=="y" (
        echo [取消] 保持现有配置
        goto :CheckPassword
    )
)

REM 复制模板（根目录与后端目录各自维护 .env）
set "ROOT_ENV_EXAMPLE=.env.example"
set "ROOT_ENV_FILE=.env"
set "BACKEND_DIR=src"
set "BACKEND_ENV_EXAMPLE=%BACKEND_DIR%\.env.example"
set "BACKEND_ENV_FILE=%BACKEND_DIR%\.env"

echo [步骤 1/2] 从模板创建 .env 文件...

REM 根目录 .env
if not exist "%ROOT_ENV_FILE%" (
    if exist "%ROOT_ENV_EXAMPLE%" (
        copy /y "%ROOT_ENV_EXAMPLE%" "%ROOT_ENV_FILE%" >nul 2>&1
        if errorlevel 1 (
            echo [错误] 无法创建根 .env 文件
            pause
            exit /b 1
        )
        echo [完成] 根 .env 文件已创建
    ) else (
        echo [WARN] 根目录缺少 .env.example，跳过根 .env 创建
    )
) else (
    echo [信息] 根 .env 已存在
)

REM 后端目录 .env（应用实际读取此文件）
if not exist "%BACKEND_ENV_FILE%" (
echo [处理] 清理 .env 非 ASCII 注释，避免 Windows GBK 读取失败...
if exist "%ROOT_ENV_FILE%" (
    powershell -NoProfile -Command "Get-Content -LiteralPath '%CD%\\.env' | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } | Set-Content -LiteralPath '%CD%\\.env' -Encoding Ascii"
)
if exist "%BACKEND_ENV_FILE%" (
    powershell -NoProfile -Command "Get-Content -LiteralPath '%CD%\\%BACKEND_DIR%\\.env' | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } | Set-Content -LiteralPath '%CD%\\%BACKEND_DIR%\\.env' -Encoding Ascii"
)

    if exist "%BACKEND_ENV_EXAMPLE%" (
        copy /y "%BACKEND_ENV_EXAMPLE%" "%BACKEND_ENV_FILE%" >nul 2>&1
        if errorlevel 1 (
            echo [错误] 无法创建后端 .env 文件
            pause
            exit /b 1
        )
        echo [完成] 后端 .env 文件已创建
    ) else (
        echo [错误] 未找到 %BACKEND_ENV_EXAMPLE% ，请检查后端模板是否存在
        pause
        exit /b 1
    )
) else (
    echo [信息] 后端 .env 已存在
)

:CheckPassword
echo.
REM 若后端 .env 不存在，仍需确保创建（即使用户选择不覆盖根 .env）
if not exist "%BACKEND_ENV_FILE%" (
    if exist "%BACKEND_ENV_EXAMPLE%" (
        echo [信息] 检测到后端 .env 缺失，正在从模板创建...
        copy /y "%BACKEND_ENV_EXAMPLE%" "%BACKEND_ENV_FILE%" >nul 2>&1
        if errorlevel 1 (
            echo [错误] 无法创建后端 .env 文件
            pause
            exit /b 1
        )
        echo [完成] 后端 .env 文件已创建
    ) else (
        echo [错误] 未找到 %BACKEND_ENV_EXAMPLE% ，请检查后端模板是否存在
        pause
        exit /b 1
    )
)

echo [步骤 2/2] 设置数据库密码
echo.
echo 为安全起见，输入内容不会显示（隐式输入）。
set "db_password="
set "TMP_BASENAME=hp_pwd_%RANDOM%.txt"
powershell -NoProfile -Command "$p = Read-Host -AsSecureString '请输入您的 MySQL root 密码'; $b = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($p); $s = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($b); Set-Content -LiteralPath \"$env:TEMP\\%TMP_BASENAME%\" -Value $s -Encoding UTF8"
if exist "%TEMP%\%TMP_BASENAME%" (
    set /p db_password=<"%TEMP%\%TMP_BASENAME%"
    del /f /q "%TEMP%\%TMP_BASENAME%" >nul 2>&1
)

if "!db_password!"=="" (
    echo [提示] 未能获取隐式输入，回退到普通输入（本次将显示输入字符）。
    set /p db_password="密码(显示): "
)

if "!db_password!"=="" (
    echo [警告] 密码不能为空！
    goto :CheckPassword
)

REM 更新 .env 文件中的密码
echo [处理] 更新 DATABASE_PASSWORD...
REM 同步更新根目录与后端目录的密码（若不存在则追加）
if exist "%ROOT_ENV_FILE%" (
    powershell -Command "
        $f='%CD%\\.env';
        $c=Get-Content $f;
        $c = ($c -replace '^(DATABASE_PASSWORD)=[^\r\n]*','DATABASE_PASSWORD=!db_password!');
        $c = ($c -replace '^(DB_PASSWORD)=[^\r\n]*','DB_PASSWORD=!db_password!');
        if ($c -notmatch '^DATABASE_PASSWORD=') { $c += \"`r`nDATABASE_PASSWORD=!db_password!\" };
        if ($c -notmatch '^DB_PASSWORD=') { $c += \"`r`nDB_PASSWORD=!db_password!\" };
        Set-Content $f $c -Encoding UTF8
    "
)

if exist "%BACKEND_ENV_FILE%" (
    powershell -Command "
        $f='%CD%\\%BACKEND_DIR%\\.env';
        $c=Get-Content $f;
        $c = ($c -replace '^(DATABASE_PASSWORD)=[^\r\n]*','DATABASE_PASSWORD=!db_password!');
        $c = ($c -replace '^(DB_PASSWORD)=[^\r\n]*','DB_PASSWORD=!db_password!');
        if ($c -notmatch '^DATABASE_PASSWORD=') { $c += \"`r`nDATABASE_PASSWORD=!db_password!\" };
        if ($c -notmatch '^DB_PASSWORD=') { $c += \"`r`nDB_PASSWORD=!db_password!\" };
        Set-Content $f $c -Encoding UTF8
    "
)

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

popd
pause
