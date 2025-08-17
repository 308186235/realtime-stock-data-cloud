# Cloudflare Worker 后端部署脚本

Write-Host "🚀 开始部署AI股票交易系统后端到Cloudflare" -ForegroundColor Green
Write-Host "=" * 60

# 检查 wrangler CLI
Write-Host "🔍 检查 Wrangler CLI..." -ForegroundColor Yellow
try {
    $wranglerVersion = wrangler --version
    Write-Host "✅ Wrangler CLI 已安装: $wranglerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Wrangler CLI 未安装，请先安装:" -ForegroundColor Red
    Write-Host "npm install -g wrangler" -ForegroundColor Cyan
    exit 1
}

# 检查登录状态
Write-Host "`n🔐 检查 Cloudflare 登录状态..." -ForegroundColor Yellow
try {
    $authStatus = wrangler whoami 2>&1
    if ($authStatus -match "You are not authenticated") {
        Write-Host "❌ 未登录 Cloudflare，请先登录:" -ForegroundColor Red
        Write-Host "wrangler login" -ForegroundColor Cyan
        exit 1
    } else {
        Write-Host "✅ Cloudflare 登录状态正常" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ 无法检查登录状态，继续部署..." -ForegroundColor Yellow
}

# 检查必要文件
Write-Host "`n📁 检查部署文件..." -ForegroundColor Yellow
$requiredFiles = @(
    "cloudflare-worker-backend.js",
    "wrangler.toml"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file 存在" -ForegroundColor Green
    } else {
        Write-Host "❌ $file 不存在" -ForegroundColor Red
        exit 1
    }
}

# 部署到开发环境
Write-Host "`n🧪 部署到开发环境..." -ForegroundColor Yellow
try {
    wrangler deploy --env development
    Write-Host "✅ 开发环境部署成功" -ForegroundColor Green
} catch {
    Write-Host "❌ 开发环境部署失败: $_" -ForegroundColor Red
    Write-Host "继续尝试生产环境部署..." -ForegroundColor Yellow
}

# 部署到生产环境
Write-Host "`n🌐 部署到生产环境..." -ForegroundColor Yellow
try {
    wrangler deploy --env production
    Write-Host "✅ 生产环境部署成功" -ForegroundColor Green
} catch {
    Write-Host "❌ 生产环境部署失败: $_" -ForegroundColor Red
    exit 1
}

# 测试部署
Write-Host "`n🧪 测试部署..." -ForegroundColor Yellow
$testUrl = "https://api.aigupiao.me/api/health"

try {
    $response = Invoke-WebRequest -Uri $testUrl -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        $data = $response.Content | ConvertFrom-Json
        Write-Host "✅ 后端API测试成功" -ForegroundColor Green
        Write-Host "   状态: $($data.status)" -ForegroundColor Cyan
        Write-Host "   版本: $($data.version)" -ForegroundColor Cyan
        Write-Host "   时间: $($data.timestamp)" -ForegroundColor Cyan
    } else {
        Write-Host "❌ 后端API测试失败: HTTP $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ 后端API测试失败: $_" -ForegroundColor Red
    Write-Host "⚠️ 可能需要等待几分钟让部署生效" -ForegroundColor Yellow
}

# 显示部署信息
Write-Host "`n" + "=" * 60
Write-Host "🎉 后端部署完成!" -ForegroundColor Green
Write-Host "📡 API地址: https://api.aigupiao.me" -ForegroundColor Cyan
Write-Host "🔗 WebSocket: wss://api.aigupiao.me/ws" -ForegroundColor Cyan
Write-Host "📋 可用端点:" -ForegroundColor Yellow
Write-Host "   GET  /api/health - 健康检查" -ForegroundColor White
Write-Host "   POST /api/local/* - 本地API代理" -ForegroundColor White
Write-Host "   POST /api/agent/analysis - AI分析" -ForegroundColor White
Write-Host "   POST /api/agent/decision - AI决策" -ForegroundColor White
Write-Host "   POST /api/agent/execute - 执行交易" -ForegroundColor White
Write-Host "   WS   /ws - WebSocket连接" -ForegroundColor White

Write-Host "`n📝 下一步:" -ForegroundColor Yellow
Write-Host "1. 更新前端配置指向新的API地址" -ForegroundColor White
Write-Host "2. 测试前端-后端连接" -ForegroundColor White
Write-Host "3. 配置本地系统连接到云端" -ForegroundColor White

Write-Host "`n✅ 后端部署任务完成!" -ForegroundColor Green
