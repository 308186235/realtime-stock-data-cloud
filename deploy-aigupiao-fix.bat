@echo off
echo ========================================
echo 🚀 AI股票交易系统 - aigupiao.me API修复
echo ========================================

echo.
echo 📋 检查文件...
if not exist "aigupiao-api-fix-worker.js" (
    echo ❌ 错误: aigupiao-api-fix-worker.js 文件不存在
    pause
    exit /b 1
)

if not exist "wrangler-aigupiao-fix.toml" (
    echo ❌ 错误: wrangler-aigupiao-fix.toml 文件不存在
    pause
    exit /b 1
)

echo ✅ 文件检查完成

echo.
echo 🔑 检查Cloudflare认证...
wrangler whoami
if %errorlevel% neq 0 (
    echo ❌ 错误: Cloudflare认证失败
    echo 💡 请运行: wrangler login
    pause
    exit /b 1
)

echo.
echo 🗑️ 删除现有Worker (如果存在)...
wrangler delete aigupiao-api-fix --config wrangler-aigupiao-fix.toml --force
echo ℹ️ 删除操作完成 (如果Worker不存在会显示错误，这是正常的)

echo.
echo 🚀 部署新的Worker...
wrangler deploy --config wrangler-aigupiao-fix.toml

if %errorlevel% equ 0 (
    echo.
    echo ✅ 部署成功！
    echo.
    echo 📋 修复的API端点:
    echo    - GET https://aigupiao.me/api/health
    echo    - GET https://aigupiao.me/api/virtual-account/accounts
    echo    - GET https://aigupiao.me/api/stock-data
    echo    - GET https://aigupiao.me/api/realtime
    echo    - GET https://aigupiao.me/api/agent-analysis
    echo.
    echo 🧪 测试API...
    echo.
    
    echo 测试健康检查...
    curl -s https://aigupiao.me/api/health
    echo.
    echo.
    
    echo 测试虚拟账户API...
    curl -s https://aigupiao.me/api/virtual-account/accounts
    echo.
    echo.
    
    echo 🎉 部署和测试完成！
    echo 📱 现在移动端应该能够正常连接了
    echo 📊 延迟问题应该得到显著改善
) else (
    echo.
    echo ❌ 部署失败
    echo 请检查wrangler配置和网络连接
)

echo.
echo 按任意键退出...
pause > nul
