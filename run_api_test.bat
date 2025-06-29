@echo off
echo Starting stock trading system test workflow
echo ==============================

REM 激活虚拟环境 (如果存在)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM 启动简化API服务器
echo Starting simplified API server...
echo Server will run on http://localhost:8000
echo API docs available at http://localhost:8000/api/docs
echo.

REM 在后台启动服务器
start cmd /k python simple_api_server.py

REM 等待服务器启动
echo Waiting for server to start...
timeout /t 5 /nobreak > nul

REM 运行测试脚本
echo Running API test script...
python test_full_api_flow.py

echo.
echo ==============================
echo Test completed.
echo Press any key to exit and stop the server.
pause > nul

REM 找到并结束API服务器进程
taskkill /f /im python.exe /fi "WINDOWTITLE eq Administrator:*simple_api_server.py*" > nul 2>&1

echo Server stopped. 