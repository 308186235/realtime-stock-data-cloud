# 混合架构性能压力测试脚本
# 测试本地代理服务器的高并发和稳定性

Write-Host "🚀 混合架构性能压力测试开始" -ForegroundColor Green
Write-Host "=" * 50

# 测试配置
$baseUrl = "http://127.0.0.1:8788"
$endpoints = @(
    "/api/health",
    "/api/virtual-account/accounts", 
    "/api/chagubang/status",
    "/api/agent-analysis"
)

$concurrentRequests = 10
$totalRequests = 50
$testDuration = 30 # 秒

# 结果统计
$results = @{
    TotalRequests = 0
    SuccessfulRequests = 0
    FailedRequests = 0
    AverageResponseTime = 0
    MinResponseTime = [double]::MaxValue
    MaxResponseTime = 0
    ResponseTimes = @()
}

Write-Host "📊 测试配置:" -ForegroundColor Yellow
Write-Host "   并发请求数: $concurrentRequests"
Write-Host "   总请求数: $totalRequests"
Write-Host "   测试时长: $testDuration 秒"
Write-Host "   测试端点: $($endpoints.Count) 个"
Write-Host ""

# 单个请求测试函数
function Test-SingleRequest {
    param($url)
    
    try {
        $start = Get-Date
        $response = Invoke-WebRequest -Uri $url -UserAgent "StressTest/1.0" -TimeoutSec 10
        $end = Get-Date
        $duration = ($end - $start).TotalMilliseconds
        
        return @{
            Success = $true
            ResponseTime = $duration
            StatusCode = $response.StatusCode
        }
    }
    catch {
        return @{
            Success = $false
            ResponseTime = 0
            Error = $_.Exception.Message
        }
    }
}

# 并发测试函数
function Test-ConcurrentRequests {
    param($endpoint, $count)
    
    $jobs = @()
    $url = "$baseUrl$endpoint"
    
    Write-Host "🔄 测试端点: $endpoint (并发数: $count)" -ForegroundColor Cyan
    
    # 启动并发任务
    for ($i = 1; $i -le $count; $i++) {
        $job = Start-Job -ScriptBlock {
            param($testUrl)
            
            try {
                $start = Get-Date
                $response = Invoke-WebRequest -Uri $testUrl -UserAgent "StressTest/1.0" -TimeoutSec 10
                $end = Get-Date
                $duration = ($end - $start).TotalMilliseconds
                
                return @{
                    Success = $true
                    ResponseTime = $duration
                    StatusCode = $response.StatusCode
                }
            }
            catch {
                return @{
                    Success = $false
                    ResponseTime = 0
                    Error = $_.Exception.Message
                }
            }
        } -ArgumentList $url
        
        $jobs += $job
    }
    
    # 等待所有任务完成
    $jobResults = $jobs | Wait-Job | Receive-Job
    $jobs | Remove-Job
    
    return $jobResults
}

Write-Host "🎯 开始压力测试..." -ForegroundColor Green
Write-Host ""

$overallStart = Get-Date

# 对每个端点进行测试
foreach ($endpoint in $endpoints) {
    Write-Host "📍 测试端点: $endpoint" -ForegroundColor Yellow
    
    # 并发测试
    $concurrentResults = Test-ConcurrentRequests -endpoint $endpoint -count $concurrentRequests
    
    # 统计结果
    foreach ($result in $concurrentResults) {
        $results.TotalRequests++
        
        if ($result.Success) {
            $results.SuccessfulRequests++
            $results.ResponseTimes += $result.ResponseTime
            
            if ($result.ResponseTime -lt $results.MinResponseTime) {
                $results.MinResponseTime = $result.ResponseTime
            }
            if ($result.ResponseTime -gt $results.MaxResponseTime) {
                $results.MaxResponseTime = $result.ResponseTime
            }
        } else {
            $results.FailedRequests++
            Write-Host "   ❌ 请求失败: $($result.Error)" -ForegroundColor Red
        }
    }
    
    # 显示端点结果
    $successCount = ($concurrentResults | Where-Object { $_.Success }).Count
    $avgTime = if ($successCount -gt 0) { 
        ($concurrentResults | Where-Object { $_.Success } | Measure-Object -Property ResponseTime -Average).Average 
    } else { 0 }
    
    Write-Host "   ✅ 成功: $successCount/$concurrentRequests" -ForegroundColor Green
    Write-Host "   ⏱️  平均响应时间: $([math]::Round($avgTime, 2))ms" -ForegroundColor Cyan
    Write-Host ""
}

$overallEnd = Get-Date
$totalTestTime = ($overallEnd - $overallStart).TotalSeconds

# 计算最终统计
if ($results.ResponseTimes.Count -gt 0) {
    $results.AverageResponseTime = ($results.ResponseTimes | Measure-Object -Average).Average
}

Write-Host "📊 最终测试结果" -ForegroundColor Green
Write-Host "=" * 50
Write-Host "总请求数: $($results.TotalRequests)" -ForegroundColor White
Write-Host "成功请求: $($results.SuccessfulRequests)" -ForegroundColor Green
Write-Host "失败请求: $($results.FailedRequests)" -ForegroundColor Red
Write-Host "成功率: $([math]::Round(($results.SuccessfulRequests / $results.TotalRequests) * 100, 2))%" -ForegroundColor Yellow

if ($results.ResponseTimes.Count -gt 0) {
    Write-Host "平均响应时间: $([math]::Round($results.AverageResponseTime, 2))ms" -ForegroundColor Cyan
    Write-Host "最快响应时间: $([math]::Round($results.MinResponseTime, 2))ms" -ForegroundColor Green
    Write-Host "最慢响应时间: $([math]::Round($results.MaxResponseTime, 2))ms" -ForegroundColor Yellow
}

Write-Host "总测试时间: $([math]::Round($totalTestTime, 2))秒" -ForegroundColor White
Write-Host "请求吞吐量: $([math]::Round($results.TotalRequests / $totalTestTime, 2)) 请求/秒" -ForegroundColor Magenta

# 性能评级
$successRate = ($results.SuccessfulRequests / $results.TotalRequests) * 100
$avgResponseTime = $results.AverageResponseTime

Write-Host ""
Write-Host "🏆 性能评级:" -ForegroundColor Green

if ($successRate -ge 95 -and $avgResponseTime -le 100) {
    Write-Host "   ⭐⭐⭐⭐⭐ 优秀 (成功率: $([math]::Round($successRate, 1))%, 响应时间: $([math]::Round($avgResponseTime, 1))ms)" -ForegroundColor Green
} elseif ($successRate -ge 90 -and $avgResponseTime -le 200) {
    Write-Host "   ⭐⭐⭐⭐ 良好 (成功率: $([math]::Round($successRate, 1))%, 响应时间: $([math]::Round($avgResponseTime, 1))ms)" -ForegroundColor Yellow
} elseif ($successRate -ge 80 -and $avgResponseTime -le 500) {
    Write-Host "   ⭐⭐⭐ 一般 (成功率: $([math]::Round($successRate, 1))%, 响应时间: $([math]::Round($avgResponseTime, 1))ms)" -ForegroundColor Orange
} else {
    Write-Host "   ⭐⭐ 需要优化 (成功率: $([math]::Round($successRate, 1))%, 响应时间: $([math]::Round($avgResponseTime, 1))ms)" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ 混合架构性能压力测试完成！" -ForegroundColor Green
