@echo off
chcp 65001 >nul
echo Starting OneDrive Trading System...
echo ============================================================

echo Step 1: Check rclone process
tasklist /FI "IMAGENAME eq rclone.exe" 2>NUL | find /I /N "rclone.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo rclone process is running
) else (
    echo Starting rclone mount...
    "E:\交易8\rclone\rclone-v1.70.2-windows-amd64\rclone.exe" mount onedrive_trading: "C:\mnt\onedrive" --vfs-cache-mode writes --vfs-cache-max-age 10m --log-level INFO --log-file "E:\交易8\rclone.log" --daemon
    echo rclone mount started
    timeout /t 3 /nobreak >NUL
)

echo.
echo Step 2: Test mount
if exist "C:\mnt\onedrive\TradingData" (
    echo OneDrive mount directory exists
    echo test > "C:\mnt\onedrive\TradingData\mount_test.txt" 2>NUL
    if exist "C:\mnt\onedrive\TradingData\mount_test.txt" (
        echo OneDrive mount read/write OK
        del "C:\mnt\onedrive\TradingData\mount_test.txt" >NUL 2>&1
    ) else (
        echo OneDrive mount write failed
    )
) else (
    echo OneDrive mount directory not found
)

echo.
echo Step 3: Run trading integration test
python complete_trading_integration.py

echo.
echo ============================================================
echo OneDrive Trading System Ready!
echo ============================================================
echo Mount point: C:\mnt\onedrive\TradingData
echo Log file: E:\交易8\rclone.log
echo Cloud API: https://api.aigupiao.me/api/local-trading/
echo.
echo System is ready for trading!
pause
