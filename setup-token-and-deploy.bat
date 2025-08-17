@echo off
echo ========================================
echo 🔑 设置Cloudflare API Token并部署Worker
echo ========================================

echo.
echo 📋 请输入您的Cloudflare API Token:
set /p CLOUDFLARE_API_TOKEN="Token: "

if "%CLOUDFLARE_API_TOKEN%"=="" (
    echo ❌ 错误: Token不能为空
    pause
    exit /b 1
)

echo.
echo 🔧 设置环境变量...
set CLOUDFLARE_API_TOKEN=%CLOUDFLARE_API_TOKEN%

echo.
echo ✅ 验证Token...
wrangler whoami
if %errorlevel% neq 0 (
    echo ❌ 错误: Token验证失败
    pause
    exit /b 1
)

echo.
echo 🗑️ 删除现有Worker (如果存在)...
wrangler delete ai-stock-trading-agent --config wrangler-clean.toml --force
echo ℹ️ 删除操作完成

echo.
echo 🚀 部署新的Worker...
wrangler deploy --config wrangler-clean.toml

if %errorlevel% equ 0 (
    echo.
    echo ✅ 部署成功！
    echo.
    echo 🌐 访问地址:
    echo    - https://api.aigupiao.me/api/health
    echo    - https://ai-stock-trading-agent.your-subdomain.workers.dev/api/health
    echo.
    echo 🧪 测试API:
    curl https://api.aigupiao.me/api/health
    echo.
    echo 🎉 云端智能Agent系统已成功部署！
) else (
    echo.
    echo ❌ 部署失败！
    echo 💡 请检查错误信息并重试
)

echo.
pause
