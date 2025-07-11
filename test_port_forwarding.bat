@echo off
echo ========================================
echo 端口转发配置测试脚本
echo ========================================
echo.
echo 配置信息：
echo 内网IP: 192.168.10.102
echo 路由器IP: 192.168.10.1
echo 公网IP: 223.166.23.144
echo 服务端口: 8000
echo.
echo ========================================
echo 测试本地服务器...
echo ========================================
curl http://127.0.0.1:8000/api/auth/test
echo.
echo.
echo ========================================
echo 测试内网访问...
echo ========================================
curl http://192.168.10.102:8000/api/auth/test
echo.
echo.
echo ========================================
echo 测试公网访问（需要配置端口转发后才能成功）...
echo ========================================
curl http://223.166.23.144:8000/api/auth/test
echo.
echo.
echo ========================================
echo 测试完成！
echo 如果公网访问失败，请检查路由器端口转发配置
echo ========================================
pause
