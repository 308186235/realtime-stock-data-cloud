@echo off
echo 🚀 启动OneDrive挂载...

echo 检查挂载点...
if not exist "C:\mnt\onedrive" (
    mkdir "C:\mnt\onedrive"
    echo ✅ 挂载点已创建: C:\mnt\onedrive
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
echo 测试挂载状态...
timeout /t 3 /nobreak >nul
dir "C:\mnt\onedrive"

echo.
echo 测试文件操作...
echo test > "C:\mnt\onedrive\TradingData/test.txt"
type "C:\mnt\onedrive\TradingData/test.txt"
del "C:\mnt\onedrive\TradingData/test.txt"

echo.
echo ✅ OneDrive挂载测试完成！
pause
