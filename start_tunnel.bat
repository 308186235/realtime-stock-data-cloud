@echo off
echo ========================================
echo    AI股票交易系统 - Cloudflare隧道启动
echo ========================================
echo.

echo [1/3] 启动测试服务器...
start "AI股票服务器" python simple_tunnel_server.py

echo [2/3] 等待服务器启动...
timeout /t 3 /nobreak >nul

echo [3/3] 启动Cloudflare隧道...
start "Cloudflare隧道" cloudflared.exe tunnel run aigupiao

echo.
echo ========================================
echo 启动完成！
echo 域名访问: https://aigupiao.me
echo 本地访问: http://localhost:8081
echo ========================================
echo.
echo 按任意键退出...
pause >nul
