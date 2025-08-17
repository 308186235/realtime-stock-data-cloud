# 本地系统完整性检查脚本
# 检查所有组件的运行状态和功能完整性

Write-Host "🚀 本地股票交易系统完整性检查" -ForegroundColor Green
Write-Host "=" * 60

# 配置
$localProxy = "http://127.0.0.1:8788"
$localWorker = "http://127.0.0.1:8787"
$cloudBackup = "https://api.aigupiao.me"

# 结果统计
$results = @{
    TotalTests = 0
    PassedTests = 0
    FailedTests = 0
    Details = @()
}

# 测试函数
function Test-Endpoint {
    param($name, $url, $expectedStatus = 200)
    
    $results.TotalTests++
    
    try {
        $start = Get-Date
        $response = Invoke-WebRequest -Uri $url -UserAgent "SystemCheck" -TimeoutSec 10
        $end = Get-Date
        $duration = ($end - $start).TotalMilliseconds
        
        if ($response.StatusCode -eq $expectedStatus) {
            $results.PassedTests++
            Write-Host "✅ $name : ${duration}ms" -ForegroundColor Green
            $results.Details += @{
                Test = $name
                Status = "PASS"
                Duration = $duration
                URL = $url
            }
            return $true
        } else {
            $results.FailedTests++
            Write-Host "❌ $name : 状态码 $($response.StatusCode)" -ForegroundColor Red
            return $false
        }
    }
    catch {
        $results.FailedTests++
        Write-Host "❌ $name : $($_.Exception.Message)" -ForegroundColor Red
        $results.Details += @{
            Test = $name
            Status = "FAIL"
            Error = $_.Exception.Message
            URL = $url
        }
        return $false
    }
}

# 测试JSON响应
function Test-JsonEndpoint {
    param($name, $url, $expectedFields = @())
    
    $results.TotalTests++
    
    try {
        $start = Get-Date
        $response = Invoke-WebRequest -Uri $url -UserAgent "SystemCheck" -TimeoutSec 10
        $end = Get-Date
        $duration = ($end - $start).TotalMilliseconds
        
        $data = $response.Content | ConvertFrom-Json
        
        $missingFields = @()
        foreach ($field in $expectedFields) {
            if (-not $data.$field) {
                $missingFields += $field
            }
        }
        
        if ($missingFields.Count -eq 0) {
            $results.PassedTests++
            Write-Host "✅ $name : ${duration}ms (JSON有效)" -ForegroundColor Green
            return $data
        } else {
            $results.FailedTests++
            Write-Host "❌ $name : 缺少字段 $($missingFields -join ', ')" -ForegroundColor Red
            return $null
        }
    }
    catch {
        $results.FailedTests++
        Write-Host "❌ $name : $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

Write-Host "`n🔍 1. 基础服务检查" -ForegroundColor Yellow
Write-Host "-" * 30

# 检查本地代理服务器
Test-Endpoint "本地代理服务器" "$localProxy/api/health"

# 检查本地Worker
Test-Endpoint "本地Worker" "$localWorker/api/health"

# 检查云端备份
Test-Endpoint "云端备份服务" "$cloudBackup/api/health"

Write-Host "`n🧠 2. AI功能检查" -ForegroundColor Yellow
Write-Host "-" * 30

# 检查Agent分析功能
$agentData = Test-JsonEndpoint "Agent分析" "$localWorker/api/agent-analysis" @("success", "data")
if ($agentData) {
    Write-Host "   📊 分析状态: $($agentData.data.analysis_status)" -ForegroundColor Cyan
    Write-Host "   🎯 成功率: $($agentData.data.success_rate)%" -ForegroundColor Cyan
    Write-Host "   📈 当前策略: $($agentData.data.current_strategy)" -ForegroundColor Cyan
}

Write-Host "`n💰 3. 虚拟账户检查" -ForegroundColor Yellow
Write-Host "-" * 30

# 检查虚拟账户
$accountData = Test-JsonEndpoint "虚拟账户" "$localWorker/api/virtual-account/accounts" @("success", "data")
if ($accountData) {
    Write-Host "   👥 账户数量: $($accountData.data.Count)" -ForegroundColor Cyan
    if ($accountData.data.Count -gt 0) {
        $account = $accountData.data[0]
        Write-Host "   💵 账户余额: ¥$($account.balance)" -ForegroundColor Cyan
        Write-Host "   💳 可用资金: ¥$($account.available)" -ForegroundColor Cyan
        Write-Host "   📋 持仓数量: $($account.positions.Count)" -ForegroundColor Cyan
    }
}

Write-Host "`n📡 4. 数据源检查" -ForegroundColor Yellow
Write-Host "-" * 30

# 检查茶股帮连接
$chaguData = Test-JsonEndpoint "茶股帮状态" "$localWorker/api/chagubang/status" @("success")
if ($chaguData) {
    Write-Host "   🔗 连接状态: $($chaguData.connection.status)" -ForegroundColor Cyan
    Write-Host "   📊 数据流: $($chaguData.data_flow.status)" -ForegroundColor Cyan
}

# 尝试启动茶股帮连接
Write-Host "   🚀 尝试启动茶股帮连接..." -ForegroundColor Cyan
try {
    $startResponse = Invoke-WebRequest -Uri "$localWorker/api/chagubang/start" -Method POST -ContentType "application/json" -Body "{}" -TimeoutSec 10
    if ($startResponse.StatusCode -eq 200) {
        Write-Host "   ✅ 茶股帮启动成功" -ForegroundColor Green
        $results.PassedTests++
    }
    $results.TotalTests++
}
catch {
    Write-Host "   ❌ 茶股帮启动失败: $($_.Exception.Message)" -ForegroundColor Red
    $results.FailedTests++
    $results.TotalTests++
}

Write-Host "`n🎯 5. 前端集成检查" -ForegroundColor Yellow
Write-Host "-" * 30

# 检查前端配置文件
$frontendConfigPath = "E:\正式\移动端\services\config.js"
if (Test-Path $frontendConfigPath) {
    Write-Host "✅ 前端配置文件存在" -ForegroundColor Green
    $configContent = Get-Content $frontendConfigPath -Raw
    if ($configContent -match "127\.0\.0\.1:8788") {
        Write-Host "✅ 前端已配置为使用本地代理" -ForegroundColor Green
        $results.PassedTests += 2
    } else {
        Write-Host "❌ 前端配置未指向本地代理" -ForegroundColor Red
        $results.FailedTests++
    }
    $results.TotalTests += 2
} else {
    Write-Host "❌ 前端配置文件不存在" -ForegroundColor Red
    $results.FailedTests++
    $results.TotalTests++
}

# 检查前端主要页面
$frontendPages = @(
    "E:\正式\移动端\pages\index\index.vue",
    "E:\正式\移动端\pages\agent-analysis\index.vue",
    "E:\正式\移动端\pages\trade\index.vue"
)

foreach ($page in $frontendPages) {
    if (Test-Path $page) {
        Write-Host "✅ 页面存在: $(Split-Path $page -Leaf)" -ForegroundColor Green
        $results.PassedTests++
    } else {
        Write-Host "❌ 页面缺失: $(Split-Path $page -Leaf)" -ForegroundColor Red
        $results.FailedTests++
    }
    $results.TotalTests++
}

Write-Host "`n📊 6. 性能测试" -ForegroundColor Yellow
Write-Host "-" * 30

# 性能测试
$performanceResults = @()
for ($i = 1; $i -le 5; $i++) {
    $start = Get-Date
    try {
        $response = Invoke-WebRequest -Uri "$localProxy/api/health" -UserAgent "PerfTest" -TimeoutSec 5
        $end = Get-Date
        $duration = ($end - $start).TotalMilliseconds
        $performanceResults += $duration
        Write-Host "   测试 $i : ${duration}ms" -ForegroundColor Cyan
    }
    catch {
        Write-Host "   测试 $i : 失败" -ForegroundColor Red
    }
}

if ($performanceResults.Count -gt 0) {
    $avgPerformance = ($performanceResults | Measure-Object -Average).Average
    Write-Host "   📈 平均响应时间: $([math]::Round($avgPerformance, 2))ms" -ForegroundColor Green
    
    if ($avgPerformance -lt 100) {
        Write-Host "   🏆 性能评级: 优秀" -ForegroundColor Green
    } elseif ($avgPerformance -lt 500) {
        Write-Host "   👍 性能评级: 良好" -ForegroundColor Yellow
    } else {
        Write-Host "   ⚠️  性能评级: 需要优化" -ForegroundColor Red
    }
}

Write-Host "`n📋 最终报告" -ForegroundColor Green
Write-Host "=" * 60

$successRate = if ($results.TotalTests -gt 0) { 
    [math]::Round(($results.PassedTests / $results.TotalTests) * 100, 1) 
} else { 0 }

Write-Host "总测试数: $($results.TotalTests)" -ForegroundColor White
Write-Host "通过测试: $($results.PassedTests)" -ForegroundColor Green
Write-Host "失败测试: $($results.FailedTests)" -ForegroundColor Red
Write-Host "成功率: $successRate%" -ForegroundColor $(if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 60) { "Yellow" } else { "Red" })

Write-Host "`n🎯 系统状态评估:" -ForegroundColor Green
if ($successRate -ge 90) {
    Write-Host "系统状态: 优秀 - 所有功能正常运行" -ForegroundColor Green
} elseif ($successRate -ge 75) {
    Write-Host "系统状态: 良好 - 主要功能正常，部分功能需要关注" -ForegroundColor Yellow
} elseif ($successRate -ge 50) {
    Write-Host "系统状态: 一般 - 存在一些问题，需要修复" -ForegroundColor DarkYellow
} else {
    Write-Host "系统状态: 需要修复 - 存在严重问题" -ForegroundColor Red
}

Write-Host "`n💡 建议:" -ForegroundColor Cyan
Write-Host "1. 保持本地代理服务器运行 (127.0.0.1:8788)"
Write-Host "2. 确保本地Worker正常启动 (127.0.0.1:8787)"
Write-Host "3. 定期检查云端备份服务状态"
Write-Host "4. 监控系统性能和响应时间"

Write-Host "`n✅ 本地系统检查完成！" -ForegroundColor Green
