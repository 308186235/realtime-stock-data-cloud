@echo off
echo 正在下载frp...
curl -L -o frp.zip https://github.com/fatedier/frp/releases/download/v0.52.3/frp_0.52.3_windows_amd64.zip
echo 正在解压...
powershell -command "Expand-Archive -Path frp.zip -DestinationPath . -Force"
echo frp下载完成！
pause
