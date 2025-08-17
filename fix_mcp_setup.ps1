# 修复MCP配置脚本
Write-Host "🔧 修复MCP服务器配置..." -ForegroundColor Green

# 1. 首先检查uv是否已安装
Write-Host "📦 检查uv工具..." -ForegroundColor Yellow
try {
    $uvVersion = uv --version 2>$null
    if ($uvVersion) {
        Write-Host "✅ uv已安装: $uvVersion" -ForegroundColor Green
    } else {
        throw "uv未安装"
    }
} catch {
    Write-Host "📥 安装uv工具..." -ForegroundColor Yellow
    pip install uv
    Write-Host "✅ uv安装完成" -ForegroundColor Green
}

# 2. 测试单个MCP服务器
Write-Host "🧪 测试mcp-feedback-enhanced..." -ForegroundColor Yellow
try {
    # 先尝试安装
    uvx mcp-feedback-enhanced@latest --help 2>$null
    Write-Host "✅ mcp-feedback-enhanced可用" -ForegroundColor Green
} catch {
    Write-Host "⚠️ mcp-feedback-enhanced需要首次使用时安装" -ForegroundColor Yellow
}

# 3. 创建简化配置
$configContent = @"
{
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uvx",
      "args": ["mcp-feedback-enhanced@latest"]
    }
  }
}
"@

$configPath = ".\mcp_simple_config.json"
$configContent | Out-File -FilePath $configPath -Encoding UTF8
Write-Host "📝 创建简化配置: $configPath" -ForegroundColor Green

Write-Host "`n🎯 下一步操作：" -ForegroundColor Cyan
Write-Host "1. 在Augment中删除之前失败的MCP配置" -ForegroundColor White
Write-Host "2. 导入新的配置文件: $configPath" -ForegroundColor White
Write-Host "3. 或者手动添加单个服务器：" -ForegroundColor White
Write-Host "   - 名称: mcp-feedback-enhanced" -ForegroundColor Gray
Write-Host "   - 命令: uvx" -ForegroundColor Gray
Write-Host "   - 参数: mcp-feedback-enhanced@latest" -ForegroundColor Gray
Write-Host "4. 保存配置并重启Augment" -ForegroundColor White

Write-Host "`n💡 故障排除提示：" -ForegroundColor Cyan
Write-Host "- 确保网络连接正常" -ForegroundColor White
Write-Host "- 以管理员权限运行Augment" -ForegroundColor White
Write-Host "- 如果仍有问题，尝试手动添加而不是导入配置" -ForegroundColor White

pause
