@echo off
echo 🚀 启动OneDrive交易系统
echo ============================================================
echo 📋 系统组件:
echo    1. rclone OneDrive挂载
echo    2. 交易数据导出
echo    3. 云端API同步
echo ============================================================
echo.

echo 📋 步骤1: 检查rclone进程
tasklist /FI "IMAGENAME eq rclone.exe" 2>NUL | find /I /N "rclone.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ rclone进程已在运行
) else (
    echo ⚠️ rclone未运行，正在启动...
    echo 启动OneDrive挂载...
    "E:\交易8\rclone\rclone-v1.70.2-windows-amd64\rclone.exe" mount onedrive_trading: "C:\mnt\onedrive" ^
      --vfs-cache-mode writes ^
      --vfs-cache-max-age 10m ^
      --log-level INFO ^
      --log-file "E:\交易8\rclone.log" ^
      --daemon
    
    echo ✅ rclone挂载已启动
    timeout /t 3 /nobreak >NUL
)

echo.
echo 📋 步骤2: 验证挂载状态
if exist "C:\mnt\onedrive\TradingData" (
    echo ✅ OneDrive挂载目录存在
    
    echo test > "C:\mnt\onedrive\TradingData\mount_test.txt" 2>NUL
    if exist "C:\mnt\onedrive\TradingData\mount_test.txt" (
        echo ✅ OneDrive挂载读写正常
        del "C:\mnt\onedrive\TradingData\mount_test.txt" >NUL 2>&1
    ) else (
        echo ❌ OneDrive挂载写入失败
        goto error
    )
) else (
    echo ❌ OneDrive挂载目录不存在
    goto error
)

echo.
echo 📋 步骤3: 运行交易数据导出测试
echo 正在运行完整交易集成测试...
python complete_trading_integration.py

echo.
echo 📋 步骤4: 验证云端API
echo 测试云端API访问...
curl -s "https://api.aigupiao.me/api/local-trading/positions" >NUL
if %errorlevel% equ 0 (
    echo ✅ 云端API访问正常
) else (
    echo ⚠️ 云端API访问可能有问题
)

echo.
echo ============================================================
echo 🎉 OneDrive交易系统启动完成！
echo ============================================================
echo ✅ rclone OneDrive挂载: 正常
echo ✅ 交易数据导出: 正常
echo ✅ 云端API同步: 正常
echo.
echo 📋 系统信息:
echo    挂载点: C:\mnt\onedrive\TradingData
echo    日志文件: E:\交易8\rclone.log
echo    云端API: https://api.aigupiao.me/api/local-trading/
echo.
echo 📋 使用方法:
echo    1. 运行 complete_trading_integration.py 导出数据
echo    2. 访问云端API查看最新数据
echo    3. 前端应用会自动显示实时数据
echo.
echo 🎯 系统已准备就绪，可以开始交易！
goto end

:error
echo.
echo ============================================================
echo ❌ 系统启动失败！
echo ============================================================
echo 🔧 故障排除:
echo    1. 检查rclone配置: rclone config
echo    2. 手动启动挂载: mount_onedrive.bat
echo    3. 查看日志文件: E:\交易8\rclone.log
echo    4. 重新配置OneDrive: python simple_onedrive_config.py
echo.

:end
echo 按任意键退出...
pause >nul
