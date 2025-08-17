@echo off
echo ========================================
echo   AI股票交易系统 - 主域名部署脚本
echo   域名: aigupiao.me
echo ========================================

echo.
echo [1/5] 检查环境...
where wrangler >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 Wrangler CLI
    echo 请先安装: npm install -g wrangler
    pause
    exit /b 1
)

echo [2/5] 登录 Cloudflare...
wrangler auth login

echo [3/5] 创建 KV 命名空间...
echo 创建股票缓存 KV...
wrangler kv:namespace create "STOCK_CACHE" --preview false
wrangler kv:namespace create "STOCK_CACHE" --preview true

echo [4/5] 部署 Worker...
wrangler deploy --config wrangler-main-domain.toml

echo [5/5] 配置自定义域名...
echo.
echo 请在 Cloudflare 控制台完成以下步骤:
echo 1. 添加域名 aigupiao.me 到 Cloudflare
echo 2. 在 Workers 页面绑定自定义域名
echo 3. 配置 DNS 记录指向 Worker

echo.
echo ========================================
echo   部署完成！
echo   主域名: https://aigupiao.me
echo   移动端: https://aigupiao.me/mobile/
echo   管理后台: https://aigupiao.me/admin/
echo ========================================

pause
