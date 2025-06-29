@echo off
echo Starting stock trading system backend with database initialization
echo =========================================================

REM 激活虚拟环境 (如果存在)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM 创建数据目录
if not exist backend\data mkdir backend\data
if not exist backend\data\historical mkdir backend\data\historical

REM 初始化数据库
echo Initializing database...
python backend\init_db.py

REM 检查数据库初始化是否成功
if %ERRORLEVEL% neq 0 (
    echo Failed to initialize database!
    echo Press any key to exit...
    pause > nul
    exit /b 1
)

REM 启动后端服务器
echo Starting backend server...
echo The server will run on http://localhost:8000
echo API docs will be available at http://localhost:8000/api/docs
echo Press Ctrl+C to stop the server
echo.

python run_server.py 