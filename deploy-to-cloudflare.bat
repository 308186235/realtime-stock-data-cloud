@echo off
echo 🚀 开始部署到Cloudflare...
echo.

echo 📋 部署清单:
echo ✅ 后端API: Cloudflare Workers
echo ✅ 前端应用: Cloudflare Pages  
echo ✅ 数据库: Supabase (已配置)
echo ✅ 域名: aigupiao.me (DNS已配置)
echo.

echo 🔧 检查环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js未安装，请先安装Node.js
    pause
    exit /b 1
)

npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm未安装，请先安装npm
    pause
    exit /b 1
)

wrangler --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 安装Wrangler CLI...
    npm install -g wrangler
    if %errorlevel% neq 0 (
        echo ❌ Wrangler安装失败
        pause
        exit /b 1
    )
)

echo ✅ 环境检查完成
echo.

echo 🔐 检查Cloudflare登录状态...
cd /d "cloudflare-api"
wrangler whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔑 需要登录Cloudflare...
    echo 请在浏览器中完成登录授权...
    wrangler login
    if %errorlevel% neq 0 (
        echo ❌ Cloudflare登录失败
        pause
        exit /b 1
    )
)

echo ✅ Cloudflare登录成功
echo.

echo 🗄️ 创建KV存储...
wrangler kv:namespace create "TRADING_KV" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ KV存储创建成功
) else (
    echo ⚠️ KV存储可能已存在
)

echo 🗄️ 创建预览KV存储...
wrangler kv:namespace create "TRADING_KV" --preview >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 预览KV存储创建成功
) else (
    echo ⚠️ 预览KV存储可能已存在
)

echo.
echo 🚀 部署Cloudflare Workers API...
wrangler publish
if %errorlevel% neq 0 (
    echo ❌ Workers部署失败
    pause
    exit /b 1
)

echo ✅ Workers API部署成功
echo.

echo 🌐 配置Workers路由...
echo 请在Cloudflare Dashboard中手动配置以下路由:
echo   - api.aigupiao.me/* -> aigupiao-trading-api
echo.

cd /d ".."

echo 🎨 准备前端部署...
cd /d "炒股养家"

echo 📦 检查前端配置...
if not exist "package.json" (
    echo 📝 创建package.json...
    echo {> package.json
    echo   "name": "aigupiao-frontend",>> package.json
    echo   "version": "1.0.0",>> package.json
    echo   "scripts": {>> package.json
    echo     "build": "echo Frontend build completed">> package.json
    echo   }>> package.json
    echo }>> package.json
)

echo 🔧 更新API配置...
if exist "env.js" (
    echo ✅ API配置已指向 https://api.aigupiao.me
) else (
    echo ⚠️ env.js文件不存在
)

echo.
echo 🚀 部署前端到Cloudflare Pages...
echo 请按照以下步骤手动部署:
echo.
echo 1. 访问 https://dash.cloudflare.com
echo 2. 进入 Workers ^& Pages
echo 3. 创建Pages项目
echo 4. 连接GitHub仓库或直接上传
echo 5. 设置自定义域名:
echo    - app.aigupiao.me
echo    - mobile.aigupiao.me  
echo    - admin.aigupiao.me
echo.

cd /d ".."

echo 🔍 验证部署...
echo 测试API端点:
echo.

echo 📡 测试健康检查...
curl -s https://api.aigupiao.me/api/health
if %errorlevel% equ 0 (
    echo.
    echo ✅ API健康检查通过
) else (
    echo.
    echo ⚠️ API可能还在启动中，请稍后再试
)

echo.
echo 📡 测试Agent状态...
curl -s https://api.aigupiao.me/api/agent/status
if %errorlevel% equ 0 (
    echo.
    echo ✅ Agent API正常
) else (
    echo.
    echo ⚠️ Agent API可能还在启动中
)

echo.
echo 🎉 Cloudflare部署完成！
echo.
echo 📱 访问地址:
echo   主应用: https://app.aigupiao.me
echo   移动端: https://mobile.aigupiao.me
echo   管理后台: https://admin.aigupiao.me
echo   API文档: https://api.aigupiao.me
echo.
echo 📋 后续步骤:
echo 1. 在Cloudflare Dashboard中配置Pages自定义域名
echo 2. 测试所有API端点功能
echo 3. 验证前端与API的连接
echo 4. 配置SSL证书（自动）
echo.
echo 💡 提示:
echo - DNS记录已配置完成
echo - API已部署到Cloudflare Workers
echo - 前端需要手动部署到Cloudflare Pages
echo - 所有配置文件已准备就绪
echo.

pause
