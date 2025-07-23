@echo off
echo 正在下载rclone...

:: 创建临时目录
if not exist "C:\temp" mkdir "C:\temp"

:: 下载rclone
powershell -Command "Invoke-WebRequest -Uri 'https://downloads.rclone.org/rclone-current-windows-amd64.zip' -OutFile 'C:\temp\rclone.zip'"

:: 解压rclone
powershell -Command "Expand-Archive -Path 'C:\temp\rclone.zip' -DestinationPath 'C:\temp\rclone' -Force"

:: 复制rclone.exe到当前目录
for /r "C:\temp\rclone" %%i in (rclone.exe) do copy "%%i" "."

echo rclone下载完成！
echo 现在运行授权命令...
echo.

:: 运行授权命令
rclone.exe authorize "onedrive"

pause
