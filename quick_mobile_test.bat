@echo off
echo 📱 快速移动应用测试
echo.

echo 1. 检查后端服务...
netstat -ano | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo ✅ 后端服务运行中
) else (
    echo ❌ 后端服务未运行
    echo 正在启动后端服务...
    cd /d "e:\交易8\backend"
    start /b python simple_app.py
    timeout /t 3 /nobreak >nul
)

echo.
echo 2. 检查Cloudflare隧道...
tasklist | findstr cloudflared.exe >nul
if %errorlevel% equ 0 (
    echo ✅ Cloudflare隧道运行中
) else (
    echo ❌ Cloudflare隧道未运行
    echo 正在启动隧道...
    cd /d "e:\交易8"
    start /b cloudflared tunnel --config config-new.yml run
    timeout /t 5 /nobreak >nul
)

echo.
echo 3. 测试API连接...
curl -s https://api.aigupiao.me/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ API连接正常
) else (
    echo ❌ API连接失败
)

echo.
echo 4. 检查移动应用文件...
if exist "e:\交易8\炒股养家\manifest.json" (
    echo ✅ manifest.json 存在
) else (
    echo ❌ manifest.json 缺失
)

if exist "e:\交易8\炒股养家\pages.json" (
    echo ✅ pages.json 存在
) else (
    echo ❌ pages.json 缺失
)

echo.
echo 5. 打开测试页面...
start "" "file:///e:/交易8/mobile_app_test.html"

echo.
echo 📋 下一步操作建议:
echo.
echo 1. 查看刚打开的测试页面，确认API连接状态
echo 2. 打开HBuilderX，导入项目: e:\交易8\炒股养家
echo 3. 在HBuilderX中运行到浏览器或手机
echo 4. 如果有错误，查看HBuilderX控制台日志
echo.
echo 按任意键退出...
pause >nul
