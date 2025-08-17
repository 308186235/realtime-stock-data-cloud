@echo off
chcp 65001 >nul
title 实时股票数据测试启动器

echo.
echo ================================================================================
echo 🚀 实时股票数据测试启动器
echo API Key: QT_wat5QfcJ6N9pDZM5
echo ================================================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 显示当前时间
echo 📅 当前时间: %date% %time%
echo 📂 工作目录: %cd%
echo.

REM 检查是否在交易时间
for /f "tokens=1-3 delims=:" %%a in ('time /t') do (
    set hour=%%a
    set minute=%%b
)

REM 去除空格
set hour=%hour: =%

if %hour% geq 9 if %hour% lss 15 (
    echo ✅ 当前在交易时间 ^(9:00-15:00^)，可以测试真实数据推送
) else (
    echo ⏰ 当前非交易时间
    echo 🕐 交易时间: 9:00-15:00
    echo 💡 在非交易时间可能只能接收到模拟数据
)
echo.

REM 检查必要文件
if not exist "backend\app.py" (
    echo ❌ 错误: 未找到后端文件 backend\app.py
    pause
    exit /b 1
)

if not exist "realtime_data_connection_tester.py" (
    echo ❌ 错误: 未找到测试文件 realtime_data_connection_tester.py
    pause
    exit /b 1
)

echo 📋 可用的测试选项:
echo 1. 🔍 运行连接测试 ^(快速测试^)
echo 2. 📊 启动实时监控器 ^(持续监控^)
echo 3. 🌐 打开Web监控页面 ^(浏览器监控^)
echo 4. 🚀 使用Python启动器 ^(推荐^)
echo 5. ❌ 退出
echo.

:menu
set /p choice="请选择操作 (1-5): "

if "%choice%"=="1" goto test_connection
if "%choice%"=="2" goto start_monitor
if "%choice%"=="3" goto open_web
if "%choice%"=="4" goto python_launcher
if "%choice%"=="5" goto exit
echo ❌ 无效选择，请重新输入
goto menu

:test_connection
echo.
echo 🔍 启动后端服务并运行连接测试...
echo.

REM 启动后端服务
echo 🔄 启动后端服务...
start "后端服务" cmd /c "set PORT=8001 && python backend\app.py"

REM 等待后端启动
echo ⏳ 等待后端服务启动...
timeout /t 10 /nobreak >nul

REM 运行连接测试
echo 🔍 运行连接测试...
python realtime_data_connection_tester.py
pause
goto menu

:start_monitor
echo.
echo 📊 启动实时监控器...
echo.

REM 启动后端服务
echo 🔄 启动后端服务...
start "后端服务" cmd /c "set PORT=8001 && python backend\app.py"

REM 等待后端启动
echo ⏳ 等待后端服务启动...
timeout /t 10 /nobreak >nul

REM 启动监控器
echo 📊 启动监控器...
start "实时监控器" cmd /c "python realtime_monitor.py"

echo ✅ 监控器已启动
echo 💡 监控器在新窗口中运行，关闭窗口可停止监控
pause
goto menu

:open_web
echo.
echo 🌐 打开Web监控页面...
echo.

REM 启动后端服务
echo 🔄 启动后端服务...
start "后端服务" cmd /c "set PORT=8001 && python backend\app.py"

REM 等待后端启动
echo ⏳ 等待后端服务启动...
timeout /t 5 /nobreak >nul

REM 打开Web页面
if exist "frontend\realtime_data_monitor.html" (
    echo 🌐 打开Web监控页面...
    start "" "frontend\realtime_data_monitor.html"
    echo ✅ Web监控页面已打开
) else (
    echo ❌ 错误: 未找到Web监控页面文件
)
pause
goto menu

:python_launcher
echo.
echo 🚀 启动Python启动器...
echo.
python start_realtime_test.py
pause
goto menu

:exit
echo.
echo 👋 感谢使用实时股票数据测试工具！
echo.

REM 尝试关闭可能启动的进程
taskkill /f /im python.exe /fi "WINDOWTITLE eq 后端服务*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq 实时监控器*" >nul 2>&1

pause
exit /b 0
