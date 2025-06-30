/**
 * Cloudflare Worker for aigupiao.me subdomain routing
 * 实现真正的子域名路由控制
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  const hostname = url.hostname
  
  // 处理预检请求
  if (request.method === 'OPTIONS') {
    return handleCORS()
  }
  
  // 根据子域名路由到不同的服务
  switch(hostname) {
    case 'app.aigupiao.me':
      return handleAppRequest(request)
    
    case 'api.aigupiao.me':
      return handleAPIRequest(request)
    
    case 'mobile.aigupiao.me':
      return handleMobileRequest(request)
    
    case 'admin.aigupiao.me':
      return handleAdminRequest(request)
    
    case 'aigupiao.me':
    case 'www.aigupiao.me':
      return handleMainSiteRequest(request)
    
    default:
      return new Response(`Domain ${hostname} not configured`, { 
        status: 404,
        headers: getCORSHeaders()
      })
  }
}

// 主应用路由处理
async function handleAppRequest(request) {
  const url = new URL(request.url)
  
  // 代理到 Cloudflare Pages 主应用
  const targetUrl = `https://bei-fen.pages.dev/app.html${url.search}`
  
  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: getProxyHeaders(request.headers),
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined
    })
    
    return addCORSHeaders(response)
  } catch (error) {
    return new Response(`App service error: ${error.message}`, { 
      status: 502,
      headers: getCORSHeaders()
    })
  }
}

// API服务路由处理
async function handleAPIRequest(request) {
  const url = new URL(request.url)
  
  // 如果是根路径，显示API状态页面
  if (url.pathname === '/' || url.pathname === '') {
    return new Response(getAPIStatusPage(), {
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        ...getCORSHeaders()
      }
    })
  }
  
  // 代理到后端API服务
  const backendUrl = 'https://trading-system-api.netlify.app'
  const targetUrl = backendUrl + url.pathname + url.search
  
  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: getProxyHeaders(request.headers),
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined
    })
    
    return addCORSHeaders(response)
  } catch (error) {
    return new Response(`API service error: ${error.message}`, { 
      status: 502,
      headers: getCORSHeaders()
    })
  }
}

// 移动端路由处理
async function handleMobileRequest(request) {
  const url = new URL(request.url)
  
  // 代理到移动端页面
  const targetUrl = `https://bei-fen.pages.dev/mobile.html${url.search}`
  
  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: getProxyHeaders(request.headers),
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined
    })
    
    return addCORSHeaders(response)
  } catch (error) {
    return new Response(`Mobile service error: ${error.message}`, { 
      status: 502,
      headers: getCORSHeaders()
    })
  }
}

// 管理后台路由处理
async function handleAdminRequest(request) {
  const url = new URL(request.url)
  
  // 代理到管理后台页面
  const targetUrl = `https://bei-fen.pages.dev/admin.html${url.search}`
  
  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: getProxyHeaders(request.headers),
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined
    })
    
    return addCORSHeaders(response)
  } catch (error) {
    return new Response(`Admin service error: ${error.message}`, { 
      status: 502,
      headers: getCORSHeaders()
    })
  }
}

// 主站路由处理
async function handleMainSiteRequest(request) {
  const url = new URL(request.url)
  
  // 代理到主站页面
  const targetUrl = `https://bei-fen.pages.dev${url.pathname}${url.search}`
  
  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: getProxyHeaders(request.headers),
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined
    })
    
    return addCORSHeaders(response)
  } catch (error) {
    return new Response(`Main site error: ${error.message}`, { 
      status: 502,
      headers: getCORSHeaders()
    })
  }
}

// 获取代理请求头
function getProxyHeaders(originalHeaders) {
  const headers = new Headers()
  
  // 复制重要的请求头
  for (const [key, value] of originalHeaders.entries()) {
    if (!key.toLowerCase().startsWith('cf-') && 
        key.toLowerCase() !== 'host') {
      headers.set(key, value)
    }
  }
  
  return headers
}

// 获取CORS头
function getCORSHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
    'Access-Control-Max-Age': '86400'
  }
}

// 添加CORS头到响应
function addCORSHeaders(response) {
  const newResponse = new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: {
      ...Object.fromEntries(response.headers.entries()),
      ...getCORSHeaders()
    }
  })
  
  return newResponse
}

// 处理CORS预检请求
function handleCORS() {
  return new Response(null, {
    status: 200,
    headers: getCORSHeaders()
  })
}

// API状态页面
function getAPIStatusPage() {
  return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API服务状态 - aigupiao.me</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        .header { background: #667eea; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .status { background: white; padding: 20px; border-radius: 10px; margin: 10px 0; }
        .endpoint { background: #f8f9fa; padding: 10px; margin: 5px 0; border-left: 4px solid #667eea; }
        .success { color: #27ae60; }
        .link { color: #667eea; text-decoration: none; }
        .link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔗 API服务状态</h1>
        <p>api.aigupiao.me - AI股票交易系统API</p>
    </div>
    
    <div class="status">
        <h2>📊 服务状态</h2>
        <p><strong>域名:</strong> api.aigupiao.me</p>
        <p><strong>状态:</strong> <span class="success">✅ 服务正常</span></p>
        <p><strong>版本:</strong> v1.0.0</p>
        <p><strong>更新时间:</strong> ${new Date().toLocaleString('zh-CN')}</p>
    </div>
    
    <div class="status">
        <h2>📋 可用端点</h2>
        <div class="endpoint"><code>GET /health</code> - 健康检查</div>
        <div class="endpoint"><code>GET /test</code> - 测试接口</div>
        <div class="endpoint"><code>GET /account-balance</code> - 账户余额</div>
        <div class="endpoint"><code>GET /account-positions</code> - 持仓信息</div>
        <div class="endpoint"><code>POST /agent-analysis</code> - AI分析</div>
    </div>
    
    <div class="status">
        <h2>🌐 相关链接</h2>
        <p><a href="https://app.aigupiao.me" class="link">🚀 主应用</a></p>
        <p><a href="https://mobile.aigupiao.me" class="link">📱 移动端</a></p>
        <p><a href="https://admin.aigupiao.me" class="link">🛠️ 管理后台</a></p>
    </div>
</body>
</html>
  `
}
