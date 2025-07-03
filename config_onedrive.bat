@echo off
echo 🚀 开始配置rclone OneDrive...
echo.

echo 步骤1: 启动rclone配置
echo 请按照以下步骤操作:
echo 1. 选择 "n" (新建配置)
echo 2. 名称输入: onedrive_trading
echo 3. 存储类型选择: onedrive (通常是选项 26)
echo 4. client_id: 留空 (直接按回车)
echo 5. client_secret: 留空 (直接按回车)
echo 6. region: 选择 1 (Microsoft Cloud Global)
echo 7. 选择 "y" 进行高级配置
echo 8. drive_type: 选择 1 (OneDrive Personal)
echo 9. 选择 "y" 使用自动配置
echo 10. 在浏览器中完成OAuth授权
echo 11. 选择 "y" 确认配置
echo 12. 选择 "q" 退出配置
echo.
pause

"E:\交易8\rclone\rclone-v1.70.2-windows-amd64\rclone.exe" config

echo.
echo 步骤2: 测试连接
echo 正在测试OneDrive连接...
"E:\交易8\rclone\rclone-v1.70.2-windows-amd64\rclone.exe" ls onedrive_trading:

echo.
echo 步骤3: 创建交易数据目录
"E:\交易8\rclone\rclone-v1.70.2-windows-amd64\rclone.exe" mkdir onedrive_trading:TradingData

echo.
echo 步骤4: 验证目录创建
"E:\交易8\rclone\rclone-v1.70.2-windows-amd64\rclone.exe" ls onedrive_trading:TradingData

echo.
echo ✅ rclone OneDrive配置完成！
echo 下一步请运行: start_onedrive_mount.bat
pause
