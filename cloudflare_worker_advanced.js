/**
 * 高级 Cloudflare Worker - aigupiao.me 多域名路由系统
 * 使用 MCP 模式处理复杂路由逻辑
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

// 主请求处理器
async function handleRequest(request) {
  const url = new URL(request.url)
  const hostname = url.hostname
  const pathname = url.pathname
  
  // 记录访问日志
  console.log(`[${new Date().toISOString()}] ${request.method} ${hostname}${pathname}`)
  
  // 处理预检请求
  if (request.method === 'OPTIONS') {
    return handleCORS()
  }
  
  try {
    // 路由分发
    const response = await routeRequest(hostname, pathname, request)
    return addSecurityHeaders(response)
  } catch (error) {
    console.error('路由处理错误:', error)
    return createErrorResponse(error.message, 500)
  }
}

// 路由分发器
async function routeRequest(hostname, pathname, request) {
  const routeConfig = {
    'app.aigupiao.me': {
      handler: handleAppDomain,
      description: '主应用域名'
    },
    'api.aigupiao.me': {
      handler: handleAPIDomain,
      description: 'API服务域名'
    },
    'mobile.aigupiao.me': {
      handler: handleMobileDomain,
      description: '移动端域名'
    },
    'admin.aigupiao.me': {
      handler: handleAdminDomain,
      description: '管理后台域名'
    },
    'aigupiao.me': {
      handler: handleMainDomain,
      description: '主站域名'
    },
    'www.aigupiao.me': {
      handler: handleMainDomain,
      description: '主站域名(www)'
    }
  }
  
  const route = routeConfig[hostname]
  if (!route) {
    return createErrorResponse(`未配置的域名: ${hostname}`, 404)
  }
  
  return await route.handler(pathname, request)
}

// 主应用域名处理
async function handleAppDomain(pathname, request) {
  // 如果是静态资源，代理到 Pages
  if (isStaticResource(pathname)) {
    return proxyToPages(pathname, request)
  }
  
  // 动态路由处理
  switch(pathname) {
    case '/':
    case '/index.html':
      return getAppHomePage()
    case '/trading':
      return getAppTradingPage()
    case '/portfolio':
      return getAppPortfolioPage()
    case '/analysis':
      return getAppAnalysisPage()
    default:
      return proxyToPages(pathname, request)
  }
}

// API域名处理
async function handleAPIDomain(pathname, request) {
  // API路由映射
  const apiRoutes = {
    '/': () => getAPIStatusPage(),
    '/health': () => getHealthCheck(),
    '/test': () => getTestResponse(),
    '/account-balance': () => proxyToBackend('/account-balance', request),
    '/account-positions': () => proxyToBackend('/account-positions', request),
    '/agent-analysis': () => proxyToBackend('/agent-analysis', request),
    '/stock-data': () => proxyToBackend('/stock-data', request)
  }
  
  const handler = apiRoutes[pathname]
  if (handler) {
    return await handler()
  }
  
  // 默认代理到后端API
  return proxyToBackend(pathname, request)
}

// 移动端域名处理
async function handleMobileDomain(pathname, request) {
  // 移动端优化的页面
  switch(pathname) {
    case '/':
    case '/index.html':
      return getMobileHomePage()
    case '/trade':
      return getMobileTradePage()
    case '/portfolio':
      return getMobilePortfolioPage()
    default:
      return proxyToPages('/mobile.html', request)
  }
}

// 管理后台域名处理
async function handleAdminDomain(pathname, request) {
  // 管理后台路由
  switch(pathname) {
    case '/':
    case '/index.html':
      return getAdminHomePage()
    case '/dashboard':
      return getAdminDashboard()
    case '/users':
      return getAdminUsers()
    case '/system':
      return getAdminSystem()
    default:
      return proxyToPages('/admin.html', request)
  }
}

// 主站域名处理
async function handleMainDomain(pathname, request) {
  switch(pathname) {
    case '/':
    case '/index.html':
      return getMainHomePage()
    default:
      return proxyToPages(pathname, request)
  }
}

// 代理到 Cloudflare Pages
async function proxyToPages(pathname, request) {
  const targetUrl = `https://bei-fen.pages.dev${pathname}`
  
  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: getProxyHeaders(request.headers),
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined
    })
    
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers
    })
  } catch (error) {
    return createErrorResponse(`Pages代理错误: ${error.message}`, 502)
  }
}

// 代理到后端API
async function proxyToBackend(pathname, request) {
  const backendUrl = `https://trading-system-api.netlify.app${pathname}`
  
  try {
    const response = await fetch(backendUrl, {
      method: request.method,
      headers: getProxyHeaders(request.headers),
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined
    })
    
    return addCORSHeaders(response)
  } catch (error) {
    return createErrorResponse(`API代理错误: ${error.message}`, 502)
  }
}

// 判断是否为静态资源
function isStaticResource(pathname) {
  const staticExtensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf']
  return staticExtensions.some(ext => pathname.toLowerCase().endsWith(ext))
}

// 获取代理请求头
function getProxyHeaders(originalHeaders) {
  const headers = new Headers()
  
  for (const [key, value] of originalHeaders.entries()) {
    if (!key.toLowerCase().startsWith('cf-') && 
        key.toLowerCase() !== 'host') {
      headers.set(key, value)
    }
  }
  
  return headers
}

// 添加安全头
function addSecurityHeaders(response) {
  const newResponse = new Response(response.body, response)
  
  // 安全头
  newResponse.headers.set('X-Frame-Options', 'DENY')
  newResponse.headers.set('X-Content-Type-Options', 'nosniff')
  newResponse.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  
  // CORS头
  newResponse.headers.set('Access-Control-Allow-Origin', '*')
  newResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
  newResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
  
  return newResponse
}

// 添加CORS头
function addCORSHeaders(response) {
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: {
      ...Object.fromEntries(response.headers.entries()),
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
    }
  })
}

// 处理CORS预检请求
function handleCORS() {
  return new Response(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
      'Access-Control-Max-Age': '86400'
    }
  })
}

// 创建错误响应
function createErrorResponse(message, status = 500) {
  return new Response(JSON.stringify({
    error: true,
    message: message,
    timestamp: new Date().toISOString()
  }), {
    status: status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Access-Control-Allow-Origin': '*'
    }
  })
}

// 健康检查
function getHealthCheck() {
  return new Response(JSON.stringify({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    worker: 'aigupiao-subdomain-router'
  }), {
    headers: { 'Content-Type': 'application/json; charset=utf-8' }
  })
}

// 测试响应
function getTestResponse() {
  return new Response(JSON.stringify({
    message: 'Worker路由测试成功',
    timestamp: new Date().toISOString(),
    routes: ['app.aigupiao.me', 'api.aigupiao.me', 'mobile.aigupiao.me', 'admin.aigupiao.me']
  }), {
    headers: { 'Content-Type': 'application/json; charset=utf-8' }
  })
}

// API状态页面
function getAPIStatusPage() {
  return new Response(`
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API服务状态 - aigupiao.me</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        .header { background: #667eea; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .status { background: white; padding: 20px; border-radius: 10px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .endpoint { background: #f8f9fa; padding: 10px; margin: 5px 0; border-left: 4px solid #667eea; font-family: monospace; }
        .success { color: #27ae60; font-weight: bold; }
        .btn { background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin: 5px; cursor: pointer; text-decoration: none; display: inline-block; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔗 API服务状态</h1>
        <p>api.aigupiao.me - AI股票交易系统API</p>
    </div>
    
    <div class="status">
        <h2>📊 服务状态</h2>
        <p><strong>状态:</strong> <span class="success">✅ Worker路由正常运行</span></p>
        <p><strong>版本:</strong> v1.0.0-advanced</p>
        <p><strong>更新时间:</strong> ${new Date().toLocaleString('zh-CN')}</p>
    </div>
    
    <div class="status">
        <h2>📋 可用端点</h2>
        <div class="endpoint">GET /health - 健康检查</div>
        <div class="endpoint">GET /test - 测试接口</div>
        <div class="endpoint">GET /account-balance - 账户余额</div>
        <div class="endpoint">GET /account-positions - 持仓信息</div>
        <div class="endpoint">POST /agent-analysis - AI分析</div>
        <div class="endpoint">GET /stock-data - 股票数据</div>
    </div>
    
    <div class="status">
        <h2>🌐 快速测试</h2>
        <a href="/health" class="btn">健康检查</a>
        <a href="/test" class="btn">测试接口</a>
        <a href="https://app.aigupiao.me" class="btn">主应用</a>
    </div>
</body>
</html>
  `, {
    headers: { 'Content-Type': 'text/html; charset=utf-8' }
  })
}

// 其他页面生成函数...
function getAppHomePage() {
  return new Response('主应用首页 - Worker路由成功', {
    headers: { 'Content-Type': 'text/html; charset=utf-8' }
  })
}

function getMobileHomePage() {
  return new Response('移动端首页 - Worker路由成功', {
    headers: { 'Content-Type': 'text/html; charset=utf-8' }
  })
}

function getAdminHomePage() {
  return new Response('管理后台首页 - Worker路由成功', {
    headers: { 'Content-Type': 'text/html; charset=utf-8' }
  })
}

function getMainHomePage() {
  return new Response('主站首页 - Worker路由成功', {
    headers: { 'Content-Type': 'text/html; charset=utf-8' }
  })
}
