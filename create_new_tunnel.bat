@echo off
chcp 65001 >nul
echo ========================================
echo   创建新的Cloudflare隧道
echo ========================================
echo.

echo 🔧 创建新隧道: aigupiao-new
cloudflared.exe tunnel create aigupiao-new

echo.
echo 🌐 配置DNS路由...
cloudflared.exe tunnel route dns aigupiao-new aigupiao.me

echo.
echo 📝 更新配置文件...
echo tunnel: aigupiao-new > config-new.yml
echo credentials-file: C:\Users\锋\.cloudflared\aigupiao-new.json >> config-new.yml
echo. >> config-new.yml
echo ingress: >> config-new.yml
echo   - hostname: aigupiao.me >> config-new.yml
echo     service: http://localhost:8081 >> config-new.yml
echo   - service: http_status:404 >> config-new.yml

echo.
echo ✅ 新隧道配置完成！
echo 💡 使用以下命令启动新隧道:
echo cloudflared.exe tunnel --config config-new.yml run aigupiao-new
echo.
pause
