@echo off
chcp 65001 >nul
echo ============================================================
echo 🔧 OneDrive同步服务安装程序
echo ============================================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ 管理员权限确认
) else (
    echo ❌ 需要管理员权限运行此脚本
    echo 请右键点击"以管理员身份运行"
    pause
    exit /b 1
)

echo.
echo 📋 服务配置信息:
echo 服务名称: OneDriveTradingSync
echo 显示名称: OneDrive交易数据同步服务
echo 描述: 自动同步交易数据到OneDrive个人账户
echo 启动类型: 自动
echo.

set /p confirm=是否继续安装服务? (Y/N): 
if /i not "%confirm%"=="Y" (
    echo 安装已取消
    exit /b 0
)

echo.
echo 🔧 创建服务脚本...

REM 创建服务启动脚本
echo @echo off > onedrive_service.bat
echo cd /d "%~dp0" >> onedrive_service.bat
echo python trading_onedrive_integration.py schedule >> onedrive_service.bat

echo ✅ 服务脚本已创建

echo.
echo 🔧 注册Windows服务...

REM 使用sc命令创建服务
sc create OneDriveTradingSync binPath= "\"%CD%\onedrive_service.bat\"" DisplayName= "OneDrive交易数据同步服务" start= auto

if %errorLevel% == 0 (
    echo ✅ 服务注册成功
    
    echo.
    echo 🔧 配置服务描述...
    sc description OneDriveTradingSync "自动同步交易数据到OneDrive个人账户，每5分钟检查一次数据变更"
    
    echo.
    echo 🚀 启动服务...
    sc start OneDriveTradingSync
    
    if %errorLevel% == 0 (
        echo ✅ 服务启动成功
        echo.
        echo 📊 服务状态:
        sc query OneDriveTradingSync
    ) else (
        echo ❌ 服务启动失败
        echo 可以稍后手动启动服务: sc start OneDriveTradingSync
    )
    
    echo.
    echo ============================================================
    echo ✅ OneDrive同步服务安装完成!
    echo ============================================================
    echo.
    echo 📋 服务管理命令:
    echo 启动服务: sc start OneDriveTradingSync
    echo 停止服务: sc stop OneDriveTradingSync
    echo 查看状态: sc query OneDriveTradingSync
    echo 删除服务: sc delete OneDriveTradingSync
    echo.
    echo 📁 日志文件: %CD%\onedrive_sync.log
    echo 🔧 配置文件: %CD%\trading_onedrive_integration.py
    echo.
    
) else (
    echo ❌ 服务注册失败
    echo 错误代码: %errorLevel%
)

echo.
pause
