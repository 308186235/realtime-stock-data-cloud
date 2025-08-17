# PowerShell脚本：创建桌面快捷方式
Write-Host "========================================" -ForegroundColor Green
Write-Host "   创建AI股票交易系统桌面快捷方式" -ForegroundColor Green  
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 获取当前目录
$currentDir = Get-Location
Write-Host "当前目录: $currentDir" -ForegroundColor Yellow

# 获取桌面路径
$desktop = [Environment]::GetFolderPath("Desktop")
Write-Host "桌面路径: $desktop" -ForegroundColor Yellow
Write-Host ""

# 快捷方式路径
$shortcutPath = Join-Path $desktop "AI股票交易系统.lnk"
$targetPath = Join-Path $currentDir "start_tunnel.bat"

Write-Host "正在创建快捷方式..." -ForegroundColor Cyan

try {
    # 创建WScript.Shell对象
    $WshShell = New-Object -ComObject WScript.Shell
    
    # 创建快捷方式
    $Shortcut = $WshShell.CreateShortcut($shortcutPath)
    $Shortcut.TargetPath = $targetPath
    $Shortcut.WorkingDirectory = $currentDir
    $Shortcut.Description = "AI股票交易系统 - 一键启动Cloudflare隧道"
    $Shortcut.IconLocation = "shell32.dll,137"
    $Shortcut.WindowStyle = 1
    $Shortcut.Save()
    
    Write-Host ""
    Write-Host "✅ 桌面快捷方式创建成功！" -ForegroundColor Green
    Write-Host "📍 快捷方式名称: AI股票交易系统" -ForegroundColor White
    Write-Host "🚀 双击即可启动整个系统" -ForegroundColor White
    Write-Host ""
    Write-Host "快捷方式功能:" -ForegroundColor Yellow
    Write-Host "- 启动测试服务器 (端口8081)" -ForegroundColor White
    Write-Host "- 启动Cloudflare隧道" -ForegroundColor White  
    Write-Host "- 域名访问: https://aigupiao.me" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "❌ 创建快捷方式失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "按任意键继续..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
