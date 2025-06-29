@echo off
echo ======================================================
echo             东吴证券快捷键交易启动程序
echo ======================================================
echo.

REM 设置环境变量
set PYTHONPATH=%~dp0

REM 检查Python环境
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到Python环境，请确保已安装Python 3.7+
    goto :end
)

REM 检查虚拟环境
if exist venv\Scripts\activate.bat (
    echo [信息] 正在激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo [警告] 未找到虚拟环境，将使用系统Python
)

REM 检查配置文件
set CONFIG_FILE=config\hotkey_trader_config.json
if not exist %CONFIG_FILE% (
    echo [错误] 未找到配置文件: %CONFIG_FILE%
    goto :end
)

REM 检查必要的Python包
echo [信息] 检查依赖项...
python -c "import pyautogui, keyboard, win32gui" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [警告] 可能缺少必要的Python包，尝试安装...
    pip install pyautogui keyboard pywin32
)

echo [信息] 启动快捷键交易系统...
echo.
echo 提示: 请确保东吴证券交易软件已经打开并登录
echo 使用Ctrl+C可以退出程序
echo.

REM 启动快捷键交易程序
python backend\utils\hotkey_trader.py %CONFIG_FILE%

:end
echo.
echo ======================================================
echo              快捷键交易系统已关闭
echo ======================================================
pause 