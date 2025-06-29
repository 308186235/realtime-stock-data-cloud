@echo off
echo 股票交易系统服务器环境设置脚本
echo ==============================

REM 检查是否以管理员身份运行
NET SESSION >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 请以管理员身份运行此脚本！
    pause
    exit /b 1
)

echo 正在检查 Python 是否已安装...
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python 未安装。请安装 Python 3.10 或更高版本。
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH" 选项。
    pause
    exit /b 1
)

echo 正在检查 Node.js 是否已安装...
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Node.js 未安装。请安装 Node.js LTS 版本。
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo 创建 Python 虚拟环境...
if not exist venv (
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo 创建虚拟环境失败！
        pause
        exit /b 1
    )
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 安装后端依赖...
cd backend
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo 安装后端依赖失败！
    pause
    exit /b 1
)
cd ..

echo 创建环境配置文件...
if not exist .env (
    copy backend\dongwu_broker_env.example .env
    echo 已创建 .env 文件，请编辑该文件并填入您的配置信息。
)

echo 创建日志目录...
if not exist backend\logs mkdir backend\logs

echo 检查前端目录...
if exist frontend\股票 (
    echo 安装前端依赖...
    cd frontend\股票
    npm install
    if %ERRORLEVEL% neq 0 (
        echo 安装前端依赖失败！
        pause
        exit /b 1
    )
    cd ..\..
)

echo ==============================
echo 环境设置完成！
echo.
echo 启动服务器：
echo 1. 启动后端: 在项目根目录运行 "start_backend.bat"
echo 2. 启动前端: 在项目根目录运行 "start_frontend.bat"
echo.
echo 请确保编辑 .env 文件并填入正确的配置信息。
pause 