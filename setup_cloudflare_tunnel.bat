@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo 🌐 Cloudflare Tunnel 设置脚本
echo ============================================================
echo.

echo 📋 此脚本将帮助您设置Cloudflare Tunnel
echo 💡 无需配置路由器端口转发，直接通过域名访问
echo.

echo 🔧 设置步骤：
echo.
echo 1️⃣ 安装 cloudflared
echo    下载地址: https://github.com/cloudflare/cloudflared/releases
echo    将 cloudflared.exe 放到当前目录
echo.
echo 2️⃣ 登录 Cloudflare
echo    运行: cloudflared tunnel login
echo.
echo 3️⃣ 创建隧道
echo    运行: cloudflared tunnel create aigupiao-tunnel
echo.
echo 4️⃣ 配置DNS
echo    运行: cloudflared tunnel route dns aigupiao-tunnel aigupiao.me
echo.
echo 5️⃣ 启动隧道
echo    运行: cloudflared tunnel run --url http://localhost:8082 aigupiao-tunnel
echo.

pause

echo.
echo 🚀 开始自动设置...
echo.

REM 检查 cloudflared 是否存在
if not exist "cloudflared.exe" (
    echo ❌ 未找到 cloudflared.exe
    echo.
    echo 📥 请下载 cloudflared:
    echo 🔗 https://github.com/cloudflare/cloudflared/releases
    echo 📁 下载后将 cloudflared.exe 放到当前目录
    echo.
    pause
    exit /b 1
)

echo ✅ 找到 cloudflared.exe
echo.

echo 🔐 请在浏览器中完成 Cloudflare 登录...
cloudflared tunnel login

echo.
echo 🏗️ 创建隧道...
cloudflared tunnel create aigupiao-tunnel

echo.
echo 🌐 配置DNS路由...
cloudflared tunnel route dns aigupiao-tunnel aigupiao.me

echo.
echo ✅ 设置完成！
echo.
echo 🚀 现在启动隧道服务...
echo 💡 保持此窗口打开，隧道将持续运行
echo.

cloudflared tunnel run --url http://localhost:8082 aigupiao-tunnel

pause
