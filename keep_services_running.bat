@echo off
echo 🚀 启动服务监控脚本...
echo.

:MAIN_LOOP
echo [%date% %time%] 检查服务状态...

REM 检查后端服务
netstat -ano | findstr :8000 >nul
if %errorlevel% neq 0 (
    echo ❌ 后端服务未运行，正在启动...
    cd /d "e:\交易8\backend"
    start /b python simple_app.py
    timeout /t 5 /nobreak >nul
) else (
    echo ✅ 后端服务正常运行
)

REM 检查Cloudflare隧道
tasklist | findstr cloudflared.exe >nul
if %errorlevel% neq 0 (
    echo ❌ Cloudflare隧道未运行，正在启动...
    cd /d "e:\交易8"
    start /b cloudflared tunnel --config config-new.yml run
    timeout /t 10 /nobreak >nul
) else (
    echo ✅ Cloudflare隧道正常运行
)

REM 测试API连接
curl -s https://api.aigupiao.me/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  API连接测试失败，可能需要重启隧道
    taskkill /f /im cloudflared.exe >nul 2>&1
    timeout /t 3 /nobreak >nul
    cd /d "e:\交易8"
    start /b cloudflared tunnel --config config-new.yml run
    timeout /t 10 /nobreak >nul
) else (
    echo ✅ API连接正常
)

echo.
echo 等待60秒后再次检查...
timeout /t 60 /nobreak >nul
goto MAIN_LOOP
