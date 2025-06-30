/**
 * 简化版 Cloudflare Worker - aigupiao.me 子域名路由
 * 适合快速测试和部署
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  const hostname = url.hostname
  
  console.log(`处理请求: ${hostname}${url.pathname}`)
  
  // 根据子域名返回不同内容
  switch(hostname) {
    case 'app.aigupiao.me':
      return getAppPage()
    
    case 'api.aigupiao.me':
      return getAPIPage()
    
    case 'mobile.aigupiao.me':
      return getMobilePage()
    
    case 'admin.aigupiao.me':
      return getAdminPage()
    
    case 'aigupiao.me':
    case 'www.aigupiao.me':
      return getMainPage()
    
    default:
      return new Response(`未配置的域名: ${hostname}`, { 
        status: 404,
        headers: { 'Content-Type': 'text/plain; charset=utf-8' }
      })
  }
}

// 主应用页面
function getAppPage() {
  return new Response(`
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>主应用 - AI股票交易系统</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; }
        .container { max-width: 800px; margin: 0 auto; text-align: center; }
        .card { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; margin: 20px 0; }
        .btn { background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI股票交易系统 - 主应用</h1>
        <p>app.aigupiao.me</p>
        
        <div class="card">
            <h2>✅ Worker 路由测试成功！</h2>
            <p>你现在访问的是主应用界面</p>
            <p>域名: app.aigupiao.me</p>
            <p>时间: ${new Date().toLocaleString('zh-CN')}</p>
        </div>
        
        <div class="card">
            <h3>🌐 其他子域名测试</h3>
            <button class="btn" onclick="window.open('https://api.aigupiao.me', '_blank')">API服务</button>
            <button class="btn" onclick="window.open('https://mobile.aigupiao.me', '_blank')">移动端</button>
            <button class="btn" onclick="window.open('https://admin.aigupiao.me', '_blank')">管理后台</button>
        </div>
    </div>
</body>
</html>
  `, {
    headers: { 'Content-Type': 'text/html; charset=utf-8' }
  })
}

// API服务页面
function getAPIPage() {
  return new Response(`
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API服务 - AI股票交易系统</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #2c3e50; color: white; }
        .container { max-width: 800px; margin: 0 auto; }
        .status { background: #34495e; padding: 15px; border-radius: 10px; margin: 10px 0; }
        .success { color: #27ae60; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 API服务状态</h1>
        <p>api.aigupiao.me</p>
        
        <div class="status">
            <h2>📊 服务状态</h2>
            <p><strong>状态:</strong> <span class="success">✅ Worker 路由正常</span></p>
            <p><strong>域名:</strong> api.aigupiao.me</p>
            <p><strong>时间:</strong> ${new Date().toLocaleString('zh-CN')}</p>
        </div>
        
        <div class="status">
            <h2>📋 测试端点</h2>
            <p>• GET /health - 健康检查</p>
            <p>• GET /test - 测试接口</p>
            <p>• GET /status - 状态查询</p>
        </div>
    </div>
</body>
</html>
  `, {
    headers: { 'Content-Type': 'text/html; charset=utf-8' }
  })
}

// 移动端页面
function getMobilePage() {
  return new Response(`
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>移动端 - AI股票交易系统</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .card { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 15px 0; text-align: center; }
    </style>
</head>
<body>
    <div class="card">
        <h1>📱 移动端界面</h1>
        <p>mobile.aigupiao.me</p>
    </div>
    
    <div class="card">
        <h2>✅ 移动端路由成功</h2>
        <p>Worker 正确识别了移动端域名</p>
        <p>时间: ${new Date().toLocaleString('zh-CN')}</p>
    </div>
    
    <div class="card">
        <h3>📱 移动端特性</h3>
        <p>• 触屏优化界面</p>
        <p>• 响应式设计</p>
        <p>• 移动端专用功能</p>
    </div>
</body>
</html>
  `, {
    headers: { 'Content-Type': 'text/html; charset=utf-8' }
  })
}

// 管理后台页面
function getAdminPage() {
  return new Response(`
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>管理后台 - AI股票交易系统</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #2c3e50; color: white; }
        .admin-panel { background: #34495e; padding: 20px; border-radius: 10px; margin: 15px 0; }
        .status-ok { color: #27ae60; }
    </style>
</head>
<body>
    <h1>🛠️ 管理后台</h1>
    <p>admin.aigupiao.me</p>
    
    <div class="admin-panel">
        <h2>📊 系统状态</h2>
        <p><strong>Worker 状态:</strong> <span class="status-ok">✅ 正常运行</span></p>
        <p><strong>路由状态:</strong> <span class="status-ok">✅ 配置正确</span></p>
        <p><strong>访问时间:</strong> ${new Date().toLocaleString('zh-CN')}</p>
    </div>
    
    <div class="admin-panel">
        <h2>🌐 域名监控</h2>
        <p>• app.aigupiao.me - 主应用</p>
        <p>• api.aigupiao.me - API服务</p>
        <p>• mobile.aigupiao.me - 移动端</p>
        <p>• admin.aigupiao.me - 管理后台</p>
    </div>
</body>
</html>
  `, {
    headers: { 'Content-Type': 'text/html; charset=utf-8' }
  })
}

// 主站页面
function getMainPage() {
  return new Response(`
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI股票交易系统 - 首页</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .container { max-width: 1000px; margin: 0 auto; text-align: center; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
        .card { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; }
        .btn { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 25px; margin: 10px; cursor: pointer; text-decoration: none; display: inline-block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI股票交易系统</h1>
        <p>aigupiao.me - 智能化A股交易平台</p>
        
        <div class="card">
            <h2>🎉 Worker 路由配置成功！</h2>
            <p>所有子域名都已正确配置并可以访问</p>
            <p>配置时间: ${new Date().toLocaleString('zh-CN')}</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🖥️ 主应用</h3>
                <p>完整的交易功能和数据分析</p>
                <a href="https://app.aigupiao.me" class="btn">访问主应用</a>
            </div>
            <div class="card">
                <h3>📱 移动端</h3>
                <p>移动端优化的交易界面</p>
                <a href="https://mobile.aigupiao.me" class="btn">访问移动端</a>
            </div>
            <div class="card">
                <h3>🔗 API服务</h3>
                <p>数据接口和服务状态</p>
                <a href="https://api.aigupiao.me" class="btn">查看API</a>
            </div>
            <div class="card">
                <h3>🛠️ 管理后台</h3>
                <p>系统管理和监控面板</p>
                <a href="https://admin.aigupiao.me" class="btn">管理后台</a>
            </div>
        </div>
    </div>
</body>
</html>
  `, {
    headers: { 'Content-Type': 'text/html; charset=utf-8' }
  })
}
