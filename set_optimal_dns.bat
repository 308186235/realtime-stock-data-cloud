@echo off
echo 🔍 设置DNS优化...
echo.
echo 当前DNS设置:
ipconfig /all | findstr "DNS"
echo.
echo 设置为Google DNS (8.8.8.8, 8.8.4.4)...
netsh interface ip set dns "WLAN" static 8.8.8.8
netsh interface ip add dns "WLAN" 8.8.4.4 index=2
echo.
echo ✅ DNS设置完成！
echo 💡 如果网络接口名称不是WLAN，请手动修改脚本
pause
