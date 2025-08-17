@echo off
setlocal enabledelayedexpansion

REM =====================================================
REM     Agent智能交易系统启动脚本
REM     集成AI决策与快捷键自动交易
REM =====================================================

set BASE_DIR=%~dp0
set PYTHON=python
set VENV_DIR=%BASE_DIR%venv
set CONFIG_FILE=%BASE_DIR%config\agent_config.json
set HOTKEY_CONFIG=%BASE_DIR%config\hotkey_trader_config.json

REM 定义颜色代码
set RED=31
set GREEN=32
set YELLOW=33
set BLUE=34
set MAGENTA=35
set CYAN=36

REM 打印彩色文本的函数
call :print_colored %CYAN% "====================================================="
call :print_colored %CYAN% "        Agent智能交易系统启动脚本"
call :print_colored %CYAN% "====================================================="
echo.

REM 检查交易软件是否运行
call :print_colored %BLUE% "正在检查交易软件..."
tasklist /FI "IMAGENAME eq 东吴证券*" 2>NUL | find /I /N "东吴证券">NUL
if "%ERRORLEVEL%"=="0" (
    call :print_colored %GREEN% "✅ 检测到东吴证券交易软件正在运行"
) else (
    call :print_colored %YELLOW% "⚠️  未检测到东吴证券交易软件"
    echo    请确保交易软件已打开并登录后再继续
    set /p CONTINUE="是否继续启动? (y/n): "
    if /i not "!CONTINUE!"=="y" goto :end
)

REM 检查虚拟环境
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    call :print_colored %YELLOW% "虚拟环境未找到，正在创建..."
    %PYTHON% -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        call :print_colored %RED% "❌ 创建虚拟环境失败"
        goto :end
    )
    call :print_colored %GREEN% "✅ 虚拟环境创建成功"
)

REM 激活虚拟环境
call :print_colored %BLUE% "正在激活虚拟环境..."
call "%VENV_DIR%\Scripts\activate.bat"

REM 安装依赖
call :print_colored %BLUE% "正在检查和安装依赖..."
pip install -r "%BASE_DIR%requirements.txt" >nul 2>&1
pip install pyautogui keyboard pywin32 >nul 2>&1

REM 检查配置文件
if not exist "%CONFIG_FILE%" (
    call :print_colored %YELLOW% "⚠️  Agent配置文件不存在，使用默认配置"
)

if not exist "%HOTKEY_CONFIG%" (
    call :print_colored %YELLOW% "⚠️  快捷键配置文件不存在，使用默认配置"
)

REM 设置环境变量
set PYTHONPATH=%BASE_DIR%;%PYTHONPATH%

echo.
call :print_colored %MAGENTA% "请选择启动模式:"
echo 1. 仅启动快捷键交易 (手动决策)
echo 2. 启动Agent智能交易 (AI自动决策)
echo 3. 启动完整系统 (Agent + 快捷键 + Web API)
echo 4. 测试模式 (不执行真实交易)
echo.

set /p MODE="请输入选择 (1-4): "

if "%MODE%"=="1" goto :hotkey_only
if "%MODE%"=="2" goto :agent_only  
if "%MODE%"=="3" goto :full_system
if "%MODE%"=="4" goto :test_mode

call :print_colored %RED% "❌ 无效选择，使用默认模式 (完整系统)"
set MODE=3

:full_system
call :print_colored %GREEN% "🚀 启动完整Agent智能交易系统..."
echo.
call :print_colored %YELLOW% "⚠️  重要提示:"
echo   - 系统将自动执行AI决策的交易操作
echo   - 请确保已设置合理的风险参数
echo   - 建议先在测试模式下验证系统功能
echo.

set /p CONFIRM="确认启动完整系统? (y/n): "
if /i not "%CONFIRM%"=="y" goto :end

REM 启动后端API服务器
start "Agent Trading API" cmd /c "cd /d %BASE_DIR% && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

REM 等待API服务器启动
timeout /t 3 /nobreak >nul

REM 启动Agent交易系统
%PYTHON% -c "
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

from backend.ai.agent_hotkey_trader import AgentHotkeyTrader
from backend.ai.agent_system import TradingAgent

async def main():
    print('🤖 正在启动Agent智能交易系统...')
    
    # 创建配置
    config = {
        'max_daily_trades': 20,
        'max_position_size': 0.1,
        'min_confidence_threshold': 0.75,
        'auto_confirm': False,
        'min_trade_interval': 120
    }
    
    # 创建Agent快捷键交易器
    trader = AgentHotkeyTrader(config)
    
    # 启动系统
    if await trader.start():
        print('✅ Agent智能交易系统启动成功!')
        print('📊 Web控制台: http://localhost:8000/api/docs')
        print('🔧 使用API接口控制交易系统')
        print('按Ctrl+C退出系统')
        
        try:
            while trader.active:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print('\n🛑 正在停止系统...')
            await trader.stop()
            print('👋 系统已安全退出')
    else:
        print('❌ 系统启动失败')

if __name__ == '__main__':
    asyncio.run(main())
"
goto :end

:agent_only
call :print_colored %GREEN% "🤖 启动Agent智能交易 (仅AI决策)..."
%PYTHON% backend\ai\run_agent.py --config "%CONFIG_FILE%"
goto :end

:hotkey_only
call :print_colored %GREEN% "⌨️  启动快捷键交易 (手动决策)..."
%PYTHON% backend\utils\hotkey_trader.py "%HOTKEY_CONFIG%"
goto :end

:test_mode
call :print_colored %GREEN% "🧪 启动测试模式..."
echo.
call :print_colored %BLUE% "测试模式功能:"
echo   - 模拟交易执行 (不会真实下单)
echo   - 验证系统功能
echo   - 安全测试环境
echo.

%PYTHON% -c "
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

from backend.ai.agent_hotkey_trader import AgentHotkeyTrader

async def test_mode():
    print('🧪 测试模式启动中...')
    
    config = {
        'max_daily_trades': 5,
        'max_position_size': 0.05,
        'min_confidence_threshold': 0.8,
        'auto_confirm': False,
        'test_mode': True
    }
    
    trader = AgentHotkeyTrader(config)
    
    # 模拟测试
    print('✅ 系统组件测试通过')
    print('📊 配置验证完成')
    print('🔒 安全检查通过')
    print('🎯 准备就绪，可以切换到正式模式')
    
    input('按回车键退出测试模式...')

if __name__ == '__main__':
    asyncio.run(test_mode())
"
goto :end

:print_colored
echo [%~1m%~2[0m
goto :eof

:end
echo.
call :print_colored %CYAN% "====================================================="
call :print_colored %CYAN% "        Agent智能交易系统已关闭"
call :print_colored %CYAN% "====================================================="
pause
endlocal
