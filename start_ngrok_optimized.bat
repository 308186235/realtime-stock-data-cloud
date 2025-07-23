@echo off
echo 🚀 启动ngrok隧道 (亚太区域优化)...
echo.

echo 1️⃣ 启动API隧道 (端口8000)...
start "ngrok-api" cmd /k "ngrok http 8000 --region=ap --log=stdout"

timeout /t 3 /nobreak >nul

echo 2️⃣ 启动交易隧道 (端口8888)...
start "ngrok-trading" cmd /k "ngrok http 8888 --region=ap --log=stdout"

echo.
echo ✅ ngrok隧道启动完成！
echo.
echo 📋 请查看ngrok窗口获取公网地址，然后：
echo    1. 复制HTTPS地址
echo    2. 在Cloudflare DNS中创建CNAME记录
echo    3. 指向ngrok提供的地址
echo.
echo 💡 这样可以保留Cloudflare的SSL和CDN功能
echo    同时使用更快的ngrok隧道
pause
