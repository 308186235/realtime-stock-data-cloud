@echo off
chcp 65001 >nul
echo ========================================
echo   创建桌面快捷方式
echo ========================================
echo.

REM 获取当前目录
set "CURRENT_DIR=%cd%"

REM 获取桌面路径
for /f "tokens=3*" %%i in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop 2^>nul') do set "DESKTOP=%%i %%j"

REM 如果上面的方法失败，使用默认路径
if not defined DESKTOP set "DESKTOP=%USERPROFILE%\Desktop"

echo 当前目录: %CURRENT_DIR%
echo 桌面路径: %DESKTOP%
echo.

REM 创建VBS脚本来生成快捷方式
echo 正在创建快捷方式...

(
echo Set WshShell = WScript.CreateObject^("WScript.Shell"^)
echo Set oShellLink = WshShell.CreateShortcut^("%DESKTOP%\AI股票交易系统.lnk"^)
echo oShellLink.TargetPath = "%CURRENT_DIR%\start_tunnel.bat"
echo oShellLink.WorkingDirectory = "%CURRENT_DIR%"
echo oShellLink.Description = "AI股票交易系统 - 一键启动Cloudflare隧道"
echo oShellLink.IconLocation = "shell32.dll,137"
echo oShellLink.WindowStyle = 1
echo oShellLink.Save
) > temp_shortcut.vbs

REM 执行VBS脚本
cscript //nologo temp_shortcut.vbs

REM 删除临时文件
del temp_shortcut.vbs

echo.
echo ✅ 桌面快捷方式创建成功！
echo 📍 快捷方式名称: AI股票交易系统
echo 🚀 双击即可启动整个系统
echo.
echo 快捷方式功能:
echo - 启动测试服务器 (端口8081)
echo - 启动Cloudflare隧道
echo - 域名访问: https://aigupiao.me
echo.
pause
