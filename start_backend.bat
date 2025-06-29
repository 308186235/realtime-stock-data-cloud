@echo off
echo ========================================
echo 启动智能交易Agent后端服务
echo ========================================
echo.

REM 激活虚拟环境
if exist venv (
    echo [信息] 激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo [警告] 未找到虚拟环境，使用全局Python环境
)

REM 进入backend目录
cd backend

REM 创建必要的目录
if not exist logs mkdir logs
if not exist ..\models mkdir ..\models
if not exist ..\data mkdir ..\data

REM 设置环境变量
set PYTHONPATH=%cd%;%cd%\..
set AGENT_CONFIG=..\config\agent_config.json

REM 启动后端服务
echo.
echo [信息] 启动智能交易Agent后端服务...
echo [信息] 服务地址: http://localhost:8000
echo [信息] API文档: http://localhost:8000/api/docs
echo [信息] Agent API: http://localhost:8000/api/agent
echo [信息] 按 Ctrl+C 停止服务
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 