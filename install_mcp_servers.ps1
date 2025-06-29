# Augment MCP服务器安装脚本
# 运行方式：以管理员身份运行PowerShell，然后执行此脚本

Write-Host "🚀 开始安装Augment MCP服务器..." -ForegroundColor Green

# 1. 安装uv工具（Python包管理器）
Write-Host "📦 安装uv工具..." -ForegroundColor Yellow
try {
    pip install uv
    Write-Host "✅ uv安装成功" -ForegroundColor Green
} catch {
    Write-Host "❌ uv安装失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. 验证uv安装
Write-Host "🔍 验证uv安装..." -ForegroundColor Yellow
try {
    $uvVersion = uv --version
    Write-Host "✅ uv版本: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ uv验证失败" -ForegroundColor Red
    exit 1
}

# 3. 安装核心MCP服务器
$mcpServers = @(
    "context7-mcp-server@latest",
    "mcp-feedback-enhanced@latest", 
    "browsertools-mcp@latest"
)

foreach ($server in $mcpServers) {
    Write-Host "📥 安装 $server..." -ForegroundColor Yellow
    try {
        uvx $server --help | Out-Null
        Write-Host "✅ $server 安装成功" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ $server 安装可能失败，但将在首次使用时自动安装" -ForegroundColor Yellow
    }
}

# 4. 创建配置目录
$configDir = "$env:USERPROFILE\.augment\mcp"
if (!(Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force
    Write-Host "📁 创建配置目录: $configDir" -ForegroundColor Green
}

# 5. 复制配置文件
$configSource = ".\augment_mcp_config.json"
$configTarget = "$configDir\config.json"
if (Test-Path $configSource) {
    Copy-Item $configSource $configTarget -Force
    Write-Host "📋 配置文件已复制到: $configTarget" -ForegroundColor Green
} else {
    Write-Host "⚠️ 配置文件不存在: $configSource" -ForegroundColor Yellow
}

Write-Host "`n🎉 MCP服务器安装完成！" -ForegroundColor Green
Write-Host "📝 下一步操作：" -ForegroundColor Cyan
Write-Host "1. 打开Augment Settings" -ForegroundColor White
Write-Host "2. 导航到MCP Servers部分" -ForegroundColor White  
Write-Host "3. 导入配置文件: $configTarget" -ForegroundColor White
Write-Host "4. 验证所有服务器状态为绿色" -ForegroundColor White
Write-Host "5. 重启Augment以激活MCP服务器" -ForegroundColor White

Write-Host "`n🔧 故障排除：" -ForegroundColor Cyan
Write-Host "- 如果服务器状态为红色，请检查网络连接" -ForegroundColor White
Write-Host "- 确保以管理员权限运行Augment" -ForegroundColor White
Write-Host "- 查看Augment日志获取详细错误信息" -ForegroundColor White

pause
