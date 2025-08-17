@echo off
echo 🚀 启动所有服务...
echo.

echo 1. 启动后端服务...
cd /d "e:\交易8\backend"
start "后端服务" cmd /k "python simple_app.py"
timeout /t 3 /nobreak >nul

echo 2. 启动Cloudflare隧道...
cd /d "e:\交易8"
start "Cloudflare隧道" cmd /k "cloudflared tunnel --config config-new.yml run"
timeout /t 5 /nobreak >nul

echo 3. 等待服务启动完成...
timeout /t 10 /nobreak >nul

echo 4. 测试服务连接...
curl -s https://api.aigupiao.me/health
if %errorlevel% equ 0 (
    echo ✅ 所有服务启动成功！
    echo.
    echo 📱 现在可以使用移动应用了
    echo 🌐 API地址: https://api.aigupiao.me
    echo 📡 WebSocket地址: wss://api.aigupiao.me/ws
) else (
    echo ❌ 服务启动可能有问题，请检查窗口
)

echo.
echo 按任意键退出...
pause >nul
