@echo off
echo 启动增强版WebSocket服务器...

rem 设置环境变量
set SERVER_HOST=0.0.0.0
set SERVER_PORT=8000
set DEBUG_MODE=true

rem 检查Python安装
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python未安装或不在PATH中，请安装Python 3.8+
    pause
    exit /b 1
)

rem 检查必要的Python包
echo 检查并安装必要的Python包...
python -m pip install fastapi uvicorn websockets pyjwt orjson -q

echo.
echo ==============================================
echo    增强版WebSocket服务器 - 启动配置
echo ==============================================
echo  监听地址: %SERVER_HOST%
echo  监听端口: %SERVER_PORT%
echo  调试模式: %DEBUG_MODE%
echo ==============================================
echo.

rem 启动服务器
cd backend
if "%DEBUG_MODE%"=="true" (
    echo 启动服务器(调试模式)...
    python enhance_websocket_server.py --host %SERVER_HOST% --port %SERVER_PORT% --debug
) else (
    echo 启动服务器(生产模式)...
    python enhance_websocket_server.py --host %SERVER_HOST% --port %SERVER_PORT%
)

rem 如果服务器异常退出，暂停以查看错误
if %ERRORLEVEL% neq 0 (
    echo.
    echo 服务器启动失败，错误代码: %ERRORLEVEL%
    pause
) 