/**
 * Cloudflare Worker - aigupiao.me 子域名路由系统
 * 处理所有子域名的请求路由和代理
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  const hostname = url.hostname
  const pathname = url.pathname

  // 添加CORS头
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
  }

  // 处理预检请求
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: corsHeaders
    })
  }

  try {
    // 域名路由处理
    switch(hostname) {
      case 'api.aigupiao.me':
        return handleAPIDomain(pathname, request, corsHeaders)
      case 'app.aigupiao.me':
        return handleAppDomain(pathname, request, corsHeaders)
      case 'mobile.aigupiao.me':
        return handleMobileDomain(pathname, request, corsHeaders)
      case 'admin.aigupiao.me':
        return handleAdminDomain(pathname, request, corsHeaders)
      case 'aigupiao.me':
      case 'www.aigupiao.me':
        return handleMainDomain(pathname, request, corsHeaders)
      default:
        return createResponse(`Worker路由成功 - 域名: ${hostname}`, 200, corsHeaders)
    }
  } catch (error) {
    return createResponse(`路由错误: ${error.message}`, 500, corsHeaders)
  }
}

// 处理 api.aigupiao.me - 后端API
async function handleAPIDomain(pathname, request, corsHeaders) {
  const backendUrl = 'https://trading-system-api.netlify.app'
  return proxyRequest(backendUrl + pathname, request, corsHeaders)
}

// 处理 app.aigupiao.me - 前端应用
async function handleAppDomain(pathname, request, corsHeaders) {
  const frontendUrl = 'https://trading-system-frontend.netlify.app'
  return proxyRequest(frontendUrl + pathname, request, corsHeaders)
}



// 处理 mobile.aigupiao.me - 移动端
async function handleMobileDomain(pathname, request, corsHeaders) {
  const mobileUrl = 'https://trading-mobile-app.netlify.app'
  return proxyRequest(mobileUrl + pathname, request, corsHeaders)
}

// 处理 admin.aigupiao.me - 管理后台
async function handleAdminDomain(pathname, request, corsHeaders) {
  const adminUrl = 'https://trading-admin-panel.netlify.app'
  return proxyRequest(adminUrl + pathname, request, corsHeaders)
}

// 处理主域名 aigupiao.me
async function handleMainDomain(pathname, request, corsHeaders) {
  const mainContent = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI股票 - 智能交易系统</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
        .links { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 30px; }
        .link-card { background: #3498db; color: white; padding: 20px; border-radius: 8px; text-decoration: none; text-align: center; transition: transform 0.2s; }
        .link-card:hover { transform: translateY(-2px); background: #2980b9; }
        .status { background: #27ae60; color: white; padding: 10px; border-radius: 5px; text-align: center; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI股票 - 智能交易系统</h1>
        <div class="status">✅ Worker 路由系统运行正常</div>
        
        <div class="links">
            <a href="https://app.aigupiao.me" class="link-card">
                <h3>📱 交易应用</h3>
                <p>主要交易界面</p>
            </a>
            <a href="https://api.aigupiao.me" class="link-card">
                <h3>🔧 API接口</h3>
                <p>后端服务接口</p>
            </a>
            <a href="https://mobile.aigupiao.me" class="link-card">
                <h3>📲 移动端</h3>
                <p>手机应用界面</p>
            </a>
            <a href="https://admin.aigupiao.me" class="link-card">
                <h3>⚙️ 管理后台</h3>
                <p>系统管理界面</p>
            </a>
        </div>
        
        <div style="margin-top: 30px; text-align: center; color: #7f8c8d;">
            <p>当前时间: ${new Date().toLocaleString('zh-CN')}</p>
            <p>Worker 版本: v1.0.0</p>
        </div>
    </div>
</body>
</html>`
  
  return new Response(mainContent, {
    headers: {
      'Content-Type': 'text/html;charset=UTF-8',
      ...corsHeaders
    }
  })
}

// 代理请求函数
async function proxyRequest(targetUrl, request, corsHeaders) {
  try {
    const modifiedRequest = new Request(targetUrl, {
      method: request.method,
      headers: request.headers,
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null
    })
    
    const response = await fetch(modifiedRequest)
    const modifiedResponse = new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        ...Object.fromEntries(response.headers),
        ...corsHeaders
      }
    })
    
    return modifiedResponse
  } catch (error) {
    return createResponse(`代理错误: ${error.message}`, 502, corsHeaders)
  }
}

// 创建响应函数
function createResponse(data, status = 200, headers = {}) {
  // 如果data是字符串，包装成对象
  const responseData = typeof data === 'string' ? {
    message: data,
    timestamp: new Date().toISOString(),
    status: status
  } : {
    ...data,
    timestamp: data.timestamp || new Date().toISOString()
  }

  return new Response(JSON.stringify(responseData), {
    status: status,
    headers: {
      'Content-Type': 'application/json',
      ...headers
    }
  })
}
