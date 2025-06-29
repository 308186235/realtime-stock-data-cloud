@echo off
setlocal enabledelayedexpansion

REM 设置环境变量
set BASE_DIR=%~dp0
set PYTHON=python
set VENV_DIR=%BASE_DIR%venv
set AGENT_SCRIPT=%BASE_DIR%backend\ai\run_agent.py
set CONFIG_FILE=%BASE_DIR%config\agent_config.json
set ENABLE_AUTO_TRADE=true

REM 定义颜色代码
set RED=31
set GREEN=32
set YELLOW=33
set BLUE=34
set MAGENTA=35
set CYAN=36

REM 打印彩色文本的函数
call :print_colored %CYAN% "====================================="
call :print_colored %CYAN% "       Trading Agent 启动脚本        "
call :print_colored %CYAN% "====================================="
echo.

REM 检查虚拟环境
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    call :print_colored %YELLOW% "虚拟环境未找到，正在创建..."
    %PYTHON% -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        call :print_colored %RED% "创建虚拟环境失败。请确保已安装Python 3.8或更高版本。"
        goto :end
    )
    call :print_colored %GREEN% "虚拟环境创建成功。"
)

REM 激活虚拟环境
call :print_colored %BLUE% "正在激活虚拟环境..."
call "%VENV_DIR%\Scripts\activate.bat"

REM 安装依赖
call :print_colored %BLUE% "正在检查和安装依赖..."
pip install -r "%BASE_DIR%requirements.txt"
if %errorlevel% neq 0 (
    call :print_colored %RED% "安装依赖失败。请检查requirements.txt文件。"
    goto :end
)

REM 询问是否启用自动交易功能
set /p CHOICE="是否启用自动交易功能? (y/n): "
if /i "%CHOICE%"=="y" (
    set ENABLE_AUTO_TRADE=true
    call :print_colored %GREEN% "已启用自动交易功能"
) else (
    set ENABLE_AUTO_TRADE=false
    call :print_colored %YELLOW% "已禁用自动交易功能 - 仅运行模拟模式"
)

REM 设置环境变量
set PYTHONPATH=%BASE_DIR%;%PYTHONPATH%
set AGENT_AUTO_TRADE=%ENABLE_AUTO_TRADE%
set AGENT_CONFIG_FILE=%CONFIG_FILE%

REM 启动Agent
call :print_colored %GREEN% "正在启动Trading Agent..."
%PYTHON% "%AGENT_SCRIPT%" --config "%CONFIG_FILE%" --auto-trade %ENABLE_AUTO_TRADE%

if %errorlevel% neq 0 (
    call :print_colored %RED% "Agent启动失败。请检查日志获取详细信息。"
) else (
    call :print_colored %GREEN% "Agent已成功启动。"
)

goto :end

:print_colored
echo [%~1m%~2[0m
goto :eof

:end
endlocal 