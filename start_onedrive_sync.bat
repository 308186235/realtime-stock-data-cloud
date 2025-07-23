@echo off
chcp 65001 >nul
echo ============================================================
echo 🔄 OneDrive交易数据同步工具
echo ============================================================
echo.

:menu
echo 请选择操作:
echo 1. 执行一次同步
echo 2. 启动定时同步服务
echo 3. 创建数据备份
echo 4. 查看同步状态
echo 5. 测试OneDrive连接
echo 6. 退出
echo.
set /p choice=请输入选择 (1-6): 

if "%choice%"=="1" goto sync_once
if "%choice%"=="2" goto sync_schedule
if "%choice%"=="3" goto backup
if "%choice%"=="4" goto status
if "%choice%"=="5" goto test
if "%choice%"=="6" goto exit
echo 无效选择，请重新输入
goto menu

:sync_once
echo.
echo 🔄 执行一次性同步...
python trading_onedrive_integration.py once
echo.
pause
goto menu

:sync_schedule
echo.
echo 🕐 启动定时同步服务...
echo 注意：这将持续运行，按Ctrl+C停止
python trading_onedrive_integration.py schedule
echo.
pause
goto menu

:backup
echo.
echo 💾 创建数据备份...
python trading_onedrive_integration.py backup
echo.
pause
goto menu

:status
echo.
echo 📊 查看同步状态...
python trading_onedrive_integration.py status
echo.
pause
goto menu

:test
echo.
echo 🔍 测试OneDrive连接...
"C:\Users\锋\Downloads\rclone-v1.70.2-windows-amd64 (1)\rclone-v1.70.2-windows-amd64\rclone.exe" ls onedrive_personal:
echo.
pause
goto menu

:exit
echo 再见！
exit /b 0
