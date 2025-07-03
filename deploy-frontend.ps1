# 前端部署脚本 - 部署到Cloudflare Pages

Write-Host "🚀 开始部署AI股票交易系统前端到Cloudflare Pages" -ForegroundColor Green
Write-Host "=" * 60

# 检查必要工具
Write-Host "🔍 检查必要工具..." -ForegroundColor Yellow

# 检查 Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js 已安装: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js 未安装，请先安装 Node.js" -ForegroundColor Red
    exit 1
}

# 检查 npm
try {
    $npmVersion = npm --version
    Write-Host "✅ npm 已安装: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm 未安装" -ForegroundColor Red
    exit 1
}

# 检查 wrangler
try {
    $wranglerVersion = wrangler --version
    Write-Host "✅ Wrangler CLI 已安装: $wranglerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Wrangler CLI 未安装，正在安装..." -ForegroundColor Yellow
    npm install -g wrangler
}

# 创建前端项目结构
Write-Host "`n📁 创建前端项目结构..." -ForegroundColor Yellow

$frontendDir = "frontend-production"
if (!(Test-Path $frontendDir)) {
    New-Item -ItemType Directory -Path $frontendDir
    Write-Host "✅ 创建目录: $frontendDir" -ForegroundColor Green
}

# 创建 package.json
$packageJson = @"
{
  "name": "ai-stock-trading-frontend",
  "version": "1.0.0",
  "description": "AI股票交易系统前端",
  "main": "index.html",
  "scripts": {
    "build": "echo 'Building frontend...'",
    "dev": "python -m http.server 8080",
    "deploy": "wrangler pages deploy dist --project-name ai-stock-trading-frontend"
  },
  "keywords": ["ai", "stock", "trading", "frontend"],
  "author": "AI Stock Trading System",
  "license": "MIT",
  "devDependencies": {
    "@cloudflare/workers-types": "^4.20231218.0"
  }
}
"@

$packageJson | Out-File -FilePath "$frontendDir/package.json" -Encoding UTF8
Write-Host "✅ 创建 package.json" -ForegroundColor Green

# 创建主页面
$indexHtml = @"
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI股票交易系统</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="app">
        <header class="header">
            <h1>🤖 AI股票交易系统</h1>
            <div class="status-bar">
                <div class="status-item" id="cloud-status">
                    <span class="status-label">云端:</span>
                    <span class="status-value" id="cloud-status-text">检查中...</span>
                </div>
                <div class="status-item" id="local-status">
                    <span class="status-label">本地:</span>
                    <span class="status-value" id="local-status-text">检查中...</span>
                </div>
                <div class="status-item" id="ws-status">
                    <span class="status-label">WebSocket:</span>
                    <span class="status-value" id="ws-status-text">未连接</span>
                </div>
            </div>
        </header>

        <main class="main">
            <div class="dashboard">
                <div class="card">
                    <h2>💰 账户信息</h2>
                    <div class="balance-info">
                        <div class="balance-item">
                            <span class="label">可用资金:</span>
                            <span class="value" id="available-cash">--</span>
                        </div>
                        <div class="balance-item">
                            <span class="label">总资产:</span>
                            <span class="value" id="total-assets">--</span>
                        </div>
                    </div>
                    <button class="btn btn-primary" onclick="getBalance()">刷新余额</button>
                </div>

                <div class="card">
                    <h2>📊 数据导出</h2>
                    <div class="export-controls">
                        <button class="btn btn-secondary" onclick="exportData('holdings')">导出持仓</button>
                        <button class="btn btn-secondary" onclick="exportData('transactions')">导出成交</button>
                        <button class="btn btn-secondary" onclick="exportData('orders')">导出委托</button>
                        <button class="btn btn-primary" onclick="exportData('all')">导出全部</button>
                    </div>
                </div>

                <div class="card">
                    <h2>🚀 交易操作</h2>
                    <div class="trade-form">
                        <input type="text" id="stock-code" placeholder="股票代码" value="000001">
                        <input type="number" id="quantity" placeholder="数量" value="100">
                        <div class="trade-buttons">
                            <button class="btn btn-success" onclick="executeTrade('buy')">买入</button>
                            <button class="btn btn-danger" onclick="executeTrade('sell')">卖出</button>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>🧠 AI分析</h2>
                    <div class="ai-controls">
                        <button class="btn btn-primary" onclick="requestAIAnalysis()">请求AI分析</button>
                        <button class="btn btn-success" onclick="executeAIDecision()">执行AI决策</button>
                    </div>
                    <div class="ai-result" id="ai-result">
                        等待AI分析结果...
                    </div>
                </div>
            </div>
        </main>

        <footer class="footer">
            <div class="log-panel">
                <h3>📝 操作日志</h3>
                <div class="log-content" id="log-content"></div>
                <button class="btn btn-small" onclick="clearLogs()">清空日志</button>
            </div>
        </footer>
    </div>

    <script type="module" src="app.js"></script>
</body>
</html>
"@

$indexHtml | Out-File -FilePath "$frontendDir/index.html" -Encoding UTF8
Write-Host "✅ 创建 index.html" -ForegroundColor Green

# 复制配置文件
Copy-Item "frontend-config-production.js" "$frontendDir/config.js"
Copy-Item "frontend-api-client.js" "$frontendDir/api-client.js"
Write-Host "✅ 复制配置文件" -ForegroundColor Green

# 创建简单的CSS
$css = @"
/* AI股票交易系统样式 */
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f5f5f5;
    color: #333;
}

.header {
    background: #2c3e50;
    color: white;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header h1 { margin-bottom: 0.5rem; }

.status-bar {
    display: flex;
    gap: 2rem;
    font-size: 0.9rem;
}

.status-item {
    display: flex;
    gap: 0.5rem;
}

.status-value {
    font-weight: bold;
}

.main {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
}

.dashboard {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

.card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card h2 {
    margin-bottom: 1rem;
    color: #2c3e50;
}

.btn {
    background: #3498db;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: background 0.3s;
}

.btn:hover { background: #2980b9; }
.btn-primary { background: #3498db; }
.btn-secondary { background: #95a5a6; }
.btn-success { background: #27ae60; }
.btn-danger { background: #e74c3c; }
.btn-small { padding: 0.25rem 0.5rem; font-size: 0.8rem; }

.balance-info, .export-controls, .trade-form, .ai-controls {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.trade-form input {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.trade-buttons {
    display: flex;
    gap: 0.5rem;
}

.footer {
    background: white;
    margin-top: 2rem;
    padding: 1rem;
}

.log-panel {
    max-width: 1200px;
    margin: 0 auto;
}

.log-content {
    background: #1e1e1e;
    color: #fff;
    padding: 1rem;
    border-radius: 4px;
    height: 200px;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    font-size: 0.8rem;
    margin-bottom: 0.5rem;
}

.log-entry {
    margin-bottom: 0.25rem;
}

.log-success { color: #27ae60; }
.log-error { color: #e74c3c; }
.log-warning { color: #f39c12; }
.log-info { color: #3498db; }
"@

$css | Out-File -FilePath "$frontendDir/styles.css" -Encoding UTF8
Write-Host "✅ 创建 styles.css" -ForegroundColor Green

# 创建主应用脚本
$appJs = @"
// AI股票交易系统前端应用
import apiManager from './api-client.js';

// 全局状态
let connectionStatus = {
    cloud: false,
    local: false,
    websocket: false
};

// 日志函数
function log(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const logContent = document.getElementById('log-content');
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${type}`;
    logEntry.textContent = `[${timestamp}] ${message}`;
    logContent.appendChild(logEntry);
    logContent.scrollTop = logContent.scrollHeight;
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// 更新状态显示
function updateStatus(service, status) {
    const statusElement = document.getElementById(`${service}-status-text`);
    if (statusElement) {
        statusElement.textContent = status ? '✅ 已连接' : '❌ 断开';
        statusElement.className = `status-value ${status ? 'connected' : 'disconnected'}`;
    }
}

// 检查所有连接
async function checkConnections() {
    log('🔍 检查所有连接状态...');
    
    try {
        connectionStatus = await apiManager.checkAllConnections();
        
        updateStatus('cloud', connectionStatus.cloud);
        updateStatus('local', connectionStatus.local);
        updateStatus('ws', connectionStatus.websocket);
        
        if (connectionStatus.cloud && connectionStatus.local) {
            log('🎉 所有连接正常，系统就绪！', 'success');
        } else {
            log('⚠️ 部分连接失败，请检查服务状态', 'warning');
        }
    } catch (error) {
        log(`❌ 连接检查失败: ${error.message}`, 'error');
    }
}

// 获取余额
window.getBalance = async function() {
    try {
        log('💰 获取账户余额...');
        const response = await apiManager.local.getBalance();
        
        if (response.success) {
            const balance = response.data;
            document.getElementById('available-cash').textContent = 
                `¥${balance.available_cash.toLocaleString()}`;
            document.getElementById('total-assets').textContent = 
                `¥${balance.total_assets.toLocaleString()}`;
            log(`✅ 余额获取成功: ¥${balance.available_cash.toLocaleString()}`, 'success');
        } else {
            log(`❌ 余额获取失败: ${response.error}`, 'error');
        }
    } catch (error) {
        log(`❌ 余额获取异常: ${error.message}`, 'error');
    }
};

// 导出数据
window.exportData = async function(type) {
    try {
        log(`📊 导出${type}数据...`);
        const response = await apiManager.local.exportData(type);
        
        if (response.success) {
            log(`✅ ${type}数据导出成功`, 'success');
        } else {
            log(`❌ ${type}数据导出失败: ${response.error}`, 'error');
        }
    } catch (error) {
        log(`❌ 数据导出异常: ${error.message}`, 'error');
    }
};

// 执行交易
window.executeTrade = async function(action) {
    try {
        const code = document.getElementById('stock-code').value;
        const quantity = document.getElementById('quantity').value;
        
        if (!code || !quantity) {
            log('❌ 请输入股票代码和数量', 'error');
            return;
        }
        
        log(`🚀 执行${action === 'buy' ? '买入' : '卖出'}操作: ${code} ${quantity}股`);
        const response = await apiManager.local.executeTrade(action, code, quantity);
        
        if (response.success) {
            log(`✅ ${action === 'buy' ? '买入' : '卖出'}指令发送成功`, 'success');
        } else {
            log(`❌ 交易指令失败: ${response.error}`, 'error');
        }
    } catch (error) {
        log(`❌ 交易操作异常: ${error.message}`, 'error');
    }
};

// 请求AI分析
window.requestAIAnalysis = async function() {
    try {
        log('🧠 请求AI分析...');
        const response = await apiManager.cloud.requestAnalysis({
            timestamp: new Date().toISOString()
        });
        
        if (response.success) {
            document.getElementById('ai-result').textContent = 
                JSON.stringify(response.analysis, null, 2);
            log('✅ AI分析完成', 'success');
        } else {
            log('❌ AI分析失败', 'error');
        }
    } catch (error) {
        log(`❌ AI分析异常: ${error.message}`, 'error');
    }
};

// 执行AI决策
window.executeAIDecision = async function() {
    try {
        log('🎯 执行AI决策...');
        const response = await apiManager.cloud.executeTrading({
            action_data: {
                action: 'buy',
                code: '000001',
                quantity: 100
            }
        });
        
        if (response.success) {
            log('✅ AI决策执行成功', 'success');
        } else {
            log('❌ AI决策执行失败', 'error');
        }
    } catch (error) {
        log(`❌ AI决策异常: ${error.message}`, 'error');
    }
};

// 清空日志
window.clearLogs = function() {
    document.getElementById('log-content').innerHTML = '';
};

// 初始化应用
document.addEventListener('DOMContentLoaded', function() {
    log('🚀 AI股票交易系统启动');
    checkConnections();
    
    // 定期检查连接状态
    setInterval(checkConnections, 30000);
});
"@

$appJs | Out-File -FilePath "$frontendDir/app.js" -Encoding UTF8
Write-Host "✅ 创建 app.js" -ForegroundColor Green

# 创建构建目录
$distDir = "$frontendDir/dist"
if (!(Test-Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir
}

# 复制文件到构建目录
Copy-Item "$frontendDir/*" $distDir -Recurse -Force
Write-Host "✅ 构建前端文件" -ForegroundColor Green

# 部署到Cloudflare Pages
Write-Host "`n🌐 部署到Cloudflare Pages..." -ForegroundColor Yellow

try {
    Set-Location $frontendDir
    
    # 初始化项目
    if (!(Test-Path "package-lock.json")) {
        npm install
    }
    
    # 部署
    wrangler pages deploy dist --project-name ai-stock-trading-frontend --compatibility-date 2024-01-01
    
    Write-Host "✅ 前端部署成功" -ForegroundColor Green
    
} catch {
    Write-Host "❌ 前端部署失败: $_" -ForegroundColor Red
    Set-Location ..
    exit 1
} finally {
    Set-Location ..
}

# 显示部署信息
Write-Host "`n" + "=" * 60
Write-Host "🎉 前端部署完成!" -ForegroundColor Green
Write-Host "🌐 前端地址: https://ai-stock-trading-frontend.pages.dev" -ForegroundColor Cyan
Write-Host "🔗 自定义域名: https://app.aigupiao.me (需要配置)" -ForegroundColor Cyan

Write-Host "`n📝 下一步:" -ForegroundColor Yellow
Write-Host "1. 配置自定义域名 app.aigupiao.me" -ForegroundColor White
Write-Host "2. 测试前端-后端连接" -ForegroundColor White
Write-Host "3. 启动本地交易系统" -ForegroundColor White

Write-Host "`n✅ 前端部署任务完成!" -ForegroundColor Green
