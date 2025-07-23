@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo 🌐 Cloudflare Zero Trust 快速启动脚本
echo ============================================================
echo.

echo 📋 此脚本将启动完整的Zero Trust系统
echo 💡 包括隧道服务、监控系统和健康检查
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.

REM 检查必要文件
if not exist "cloudflared.exe" (
    echo ❌ 未找到 cloudflared.exe
    echo 📥 请从 https://github.com/cloudflare/cloudflared/releases 下载
    pause
    exit /b 1
)

if not exist "config.yml" (
    echo ❌ 未找到配置文件 config.yml
    echo 📝 请先运行部署脚本: python deploy_zero_trust.py
    pause
    exit /b 1
)

echo ✅ 必要文件检查通过
echo.

echo 🚀 启动Zero Trust系统...
echo.

REM 1. 启动隧道服务
echo 1️⃣ 启动Cloudflare隧道...
start "Cloudflare隧道" cloudflared.exe tunnel --config config.yml run
timeout /t 8 /nobreak >nul

REM 2. 检查隧道状态
echo 2️⃣ 检查隧道状态...
python zero_trust_manager.py status

REM 3. 启动监控服务
echo 3️⃣ 启动监控服务...
start "Zero Trust监控" python zero_trust_connection_monitor.py

REM 4. 等待服务启动
echo 4️⃣ 等待服务完全启动...
timeout /t 10 /nobreak >nul

REM 5. 运行系统测试
echo 5️⃣ 运行系统测试...
python test_zero_trust_system.py

echo.
echo ============================================================
echo 🎉 Zero Trust系统启动完成！
echo ============================================================
echo.
echo 📊 系统状态:
echo   - Cloudflare隧道: 运行中
echo   - 连接监控: 运行中
echo   - 系统测试: 已完成
echo.
echo 🌐 可访问的域名:
echo   - https://api.aigupiao.me
echo   - https://trading.aigupiao.me
echo   - https://agent.aigupiao.me
echo   - https://realtime.aigupiao.me
echo   - https://monitor.aigupiao.me
echo   - https://backup.aigupiao.me
echo.
echo 🔧 管理命令:
echo   - 查看状态: python zero_trust_manager.py status
echo   - 重启服务: python zero_trust_manager.py restart
echo   - 健康检查: python zero_trust_manager.py health
echo   - 生成报告: python zero_trust_manager.py report
echo.
echo 📝 日志文件:
echo   - 隧道日志: 查看Cloudflare隧道窗口
echo   - 监控日志: zero_trust_monitor.log
echo   - 测试日志: zero_trust_test.log
echo   - 管理日志: zero_trust_manager.log
echo.

pause
