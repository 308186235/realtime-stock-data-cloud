# 简化版本地系统检查脚本

Write-Host "🚀 本地股票交易系统状态检查" -ForegroundColor Green
Write-Host "=" * 50

$tests = @()
$passed = 0
$total = 0

# 测试函数
function Test-Service {
    param($name, $url)
    
    $global:total++
    try {
        $start = Get-Date
        $response = Invoke-WebRequest -Uri $url -UserAgent "Check" -TimeoutSec 8
        $end = Get-Date
        $duration = ($end - $start).TotalMilliseconds
        
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $name : ${duration}ms" -ForegroundColor Green
            $global:passed++
            return $true
        }
    }
    catch {
        Write-Host "❌ $name : 失败" -ForegroundColor Red
    }
    return $false
}

Write-Host "`n🔍 基础服务检查:" -ForegroundColor Yellow

# 检查本地代理
Test-Service "本地代理服务器" "http://127.0.0.1:8788/api/health"

# 检查本地Worker
Test-Service "本地Worker" "http://127.0.0.1:8787/api/health"

# 检查云端备份
Test-Service "云端备份" "https://api.aigupiao.me/api/health"

Write-Host "`n🧠 功能检查:" -ForegroundColor Yellow

# 检查虚拟账户
Test-Service "虚拟账户API" "http://127.0.0.1:8787/api/virtual-account/accounts"

# 检查Agent分析
Test-Service "Agent分析" "http://127.0.0.1:8787/api/agent-analysis"

# 检查茶股帮状态
Test-Service "茶股帮状态" "http://127.0.0.1:8787/api/chagubang/status"

Write-Host "`n📁 前端检查:" -ForegroundColor Yellow

# 检查前端配置
$configPath = "E:\正式\移动端\services\config.js"
$total++
if (Test-Path $configPath) {
    $config = Get-Content $configPath -Raw
    if ($config -match "127\.0\.0\.1:8788") {
        Write-Host "✅ 前端配置: 已指向本地代理" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "❌ 前端配置: 未指向本地代理" -ForegroundColor Red
    }
} else {
    Write-Host "❌ 前端配置: 文件不存在" -ForegroundColor Red
}

# 检查主要页面
$pages = @(
    "E:\正式\移动端\pages\index\index.vue",
    "E:\正式\移动端\pages\agent-analysis\index.vue"
)

foreach ($page in $pages) {
    $total++
    if (Test-Path $page) {
        Write-Host "✅ 页面: $(Split-Path $page -Leaf)" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "❌ 页面: $(Split-Path $page -Leaf) 缺失" -ForegroundColor Red
    }
}

Write-Host "`n⚡ 性能测试:" -ForegroundColor Yellow

# 快速性能测试
$times = @()
for ($i = 1; $i -le 3; $i++) {
    try {
        $start = Get-Date
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8788/api/health" -UserAgent "Perf" -TimeoutSec 5
        $end = Get-Date
        $duration = ($end - $start).TotalMilliseconds
        $times += $duration
        Write-Host "  测试 $i : ${duration}ms" -ForegroundColor Cyan
    }
    catch {
        Write-Host "  测试 $i : 失败" -ForegroundColor Red
    }
}

if ($times.Count -gt 0) {
    $avg = ($times | Measure-Object -Average).Average
    Write-Host "  平均响应: $([math]::Round($avg, 1))ms" -ForegroundColor Green
}

Write-Host "`n📊 最终结果:" -ForegroundColor Green
Write-Host "-" * 30

$successRate = if ($total -gt 0) { [math]::Round(($passed / $total) * 100, 1) } else { 0 }

Write-Host "通过测试: $passed / $total" -ForegroundColor White
Write-Host "成功率: $successRate%" -ForegroundColor $(if ($successRate -ge 80) { "Green" } else { "Yellow" })

if ($successRate -ge 90) {
    Write-Host "🎉 系统状态: 优秀" -ForegroundColor Green
} elseif ($successRate -ge 70) {
    Write-Host "👍 系统状态: 良好" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  系统状态: 需要修复" -ForegroundColor Red
}

Write-Host "`n💡 建议:" -ForegroundColor Cyan
Write-Host "1. 确保本地代理服务器运行: http://127.0.0.1:8788"
Write-Host "2. 确保本地Worker运行: http://127.0.0.1:8787"
Write-Host "3. 前端已配置使用混合架构"

Write-Host "`n检查完成！" -ForegroundColor Green
