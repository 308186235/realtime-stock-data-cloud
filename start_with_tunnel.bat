@echo off
chcp 65001 >nul
echo ============================================================
echo 🚀 启动股票交易系统（手机热点版）
echo ============================================================
echo.

echo 📱 检测到您使用手机热点网络
echo 💡 需要使用内网穿透服务将本地服务暴露到公网
echo.

echo 🔧 可用的内网穿透方案：
echo    1. ngrok（推荐）- 稳定快速
echo    2. localtunnel - 简单易用
echo    3. 手动配置其他服务
echo.

set /p choice="请选择方案 (1-3): "

if "%choice%"=="1" goto ngrok
if "%choice%"=="2" goto localtunnel
if "%choice%"=="3" goto manual
goto invalid

:ngrok
echo.
echo 🌐 使用ngrok方案
echo ============================================================
echo 📋 ngrok设置步骤：
echo    1. 访问 https://ngrok.com/download
echo    2. 下载Windows版本并解压到当前目录
echo    3. 注册账号获取authtoken
echo    4. 运行: ngrok authtoken ^<your-token^>
echo.

if not exist "ngrok.exe" (
    echo ❌ 未找到ngrok.exe
    echo 💡 请先下载ngrok并放到当前目录
    echo 🔗 下载地址: https://ngrok.com/download
    pause
    goto end
)

echo ✅ 找到ngrok.exe
echo.

echo 🚀 启动后端服务...
start "Backend Server" cmd /k "cd backend && python start_server.py"

echo ⏳ 等待后端服务启动...
timeout /t 5 /nobreak >nul

echo 🌐 启动ngrok隧道...
start "Ngrok Tunnel" cmd /k "ngrok http 8000"

echo.
echo ✅ 服务启动完成！
echo.
echo 📊 请查看ngrok窗口获取公网地址
echo 🔧 然后在Cloudflare中配置DNS记录
echo.
goto end

:localtunnel
echo.
echo 🌐 使用localtunnel方案
echo ============================================================

where node >nul 2>nul
if errorlevel 1 (
    echo ❌ 未找到Node.js
    echo 💡 请先安装Node.js: https://nodejs.org/
    pause
    goto end
)

echo ✅ 找到Node.js
echo 📦 安装localtunnel...
npm install -g localtunnel

echo 🚀 启动后端服务...
start "Backend Server" cmd /k "cd backend && python start_server.py"

echo ⏳ 等待后端服务启动...
timeout /t 5 /nobreak >nul

echo 🌐 启动localtunnel...
start "LocalTunnel" cmd /k "lt --port 8000 --subdomain aigupiao"

echo.
echo ✅ 服务启动完成！
echo 🌐 公网地址: https://aigupiao.loca.lt
echo.
goto end

:manual
echo.
echo 🔧 手动配置说明
echo ============================================================
echo 📋 您可以使用以下任一服务：
echo.
echo 🌐 ngrok:
echo    - 下载: https://ngrok.com/download
echo    - 命令: ngrok http 8000
echo.
echo 🌐 花生壳:
echo    - 下载: https://hsk.oray.com/
echo    - 配置内网穿透到端口8000
echo.
echo 🌐 其他服务:
echo    - frp, natapp, sunny-ngrok等
echo.

echo 🚀 启动后端服务...
start "Backend Server" cmd /k "cd backend && python start_server.py"

echo.
echo ✅ 后端服务已启动在 http://localhost:8000
echo 💡 请手动配置内网穿透服务
echo.
goto end

:invalid
echo ❌ 无效选择，请重新运行脚本
goto end

:end
echo.
echo 📋 下一步操作：
echo    1. 获取内网穿透提供的公网地址
echo    2. 登录Cloudflare控制台
echo    3. 更新DNS记录指向公网地址
echo    4. 测试移动前端连接
echo.
echo 🔗 Cloudflare控制台: https://dash.cloudflare.com
echo 📱 移动前端测试: 设置 → 网络连接测试
echo.
pause
