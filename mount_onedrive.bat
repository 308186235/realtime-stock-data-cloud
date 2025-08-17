@echo off
echo 🚀 启动OneDrive挂载...

echo 检查现有rclone进程...
tasklist /FI "IMAGENAME eq rclone.exe" 2>NUL | find /I /N "rclone.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ⚠️ rclone进程已在运行，正在停止...
    taskkill /F /IM rclone.exe >NUL 2>&1
    timeout /t 2 /nobreak >NUL
)

echo 启动rclone挂载...
"E:\交易8\rclone\rclone-v1.70.2-windows-amd64\rclone.exe" mount onedrive_trading: "C:\mnt\onedrive" ^
  --vfs-cache-mode writes ^
  --vfs-cache-max-age 10m ^
  --log-level INFO ^
  --log-file "E:\交易8/rclone.log" ^
  --daemon

echo ✅ OneDrive挂载已启动！
echo 挂载点: C:\mnt\onedrive
echo 日志文件: E:\交易8/rclone.log

echo.
echo 等待挂载完成...
timeout /t 5 /nobreak >NUL

echo 测试挂载状态...
if exist "C:\mnt\onedrive" (
    dir "C:\mnt\onedrive" >NUL 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo ✅ 挂载测试成功！
        echo 目录内容:
        dir "C:\mnt\onedrive"
    ) else (
        echo ❌ 挂载测试失败
    )
) else (
    echo ❌ 挂载点不存在
)

echo.
echo 测试文件操作...
echo test > "C:\mnt\onedrive\TradingData\test.txt" 2>NUL
if exist "C:\mnt\onedrive\TradingData\test.txt" (
    echo ✅ 文件写入测试成功
    type "C:\mnt\onedrive\TradingData\test.txt"
    del "C:\mnt\onedrive\TradingData\test.txt" >NUL 2>&1
    echo ✅ 文件删除测试成功
) else (
    echo ❌ 文件写入测试失败
)

echo.
echo 🎉 OneDrive挂载配置完成！
echo 📁 交易数据目录: C:\mnt\onedrive\TradingData
echo 📋 现在可以将交易软件导出路径设置为: C:\mnt\onedrive\TradingData
pause
