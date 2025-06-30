/**
 * 简化版 Cloudflare Worker - aigupiao.me 路由系统
 * MCP 修复版本
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
    // 路由处理
    switch(hostname) {
      case 'app.aigupiao.me':
        return handleAppDomain(pathname, request, corsHeaders)
      case 'api.aigupiao.me':
        return handleAPIDomain(pathname, request, corsHeaders)
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

// 主应用域名处理
async function handleAppDomain(pathname, request, corsHeaders) {
  if (pathname === '/test') {
    return createResponse('App域名测试成功', 200, corsHeaders)
  }
  
  // 代理到 Pages
  return proxyToPages(pathname, request, corsHeaders)
}

// API域名处理
async function handleAPIDomain(pathname, request, corsHeaders) {
  if (pathname === '/health') {
    return createResponse(JSON.stringify({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      worker: 'aigupiao-subdomain-router',
      version: '1.0.0-mcp-fix'
    }), 200, corsHeaders, 'application/json')
  }
  
  if (pathname === '/test') {
    return createResponse('API域名测试成功', 200, corsHeaders)
  }
  
  // 代理到后端API
  return proxyToBackend(pathname, request, corsHeaders)
}

// 移动端域名处理
async function handleMobileDomain(pathname, request, corsHeaders) {
  if (pathname === '/test') {
    return createResponse('Mobile域名测试成功', 200, corsHeaders)
  }
  
  return proxyToPages('/mobile.html', request, corsHeaders)
}

// 管理后台域名处理
async function handleAdminDomain(pathname, request, corsHeaders) {
  if (pathname === '/test') {
    return createResponse('Admin域名测试成功', 200, corsHeaders)
  }
  
  return proxyToPages('/admin.html', request, corsHeaders)
}

// 主站域名处理
async function handleMainDomain(pathname, request, corsHeaders) {
  if (pathname === '/test') {
    return createResponse('主站域名测试成功', 200, corsHeaders)
  }
  
  return proxyToPages(pathname, request, corsHeaders)
}

// 代理到 Cloudflare Pages
async function proxyToPages(pathname, request, corsHeaders) {
  const targetUrl = `https://bei-fen.pages.dev${pathname}`
  
  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: request.headers,
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined
    })
    
    const newResponse = new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        ...Object.fromEntries(response.headers.entries()),
        ...corsHeaders
      }
    })
    
    return newResponse
  } catch (error) {
    return createResponse(`Pages代理错误: ${error.message}`, 502, corsHeaders)
  }
}

// 代理到后端API
async function proxyToBackend(pathname, request, corsHeaders) {
  const backendUrl = `https://trading-system-api.netlify.app${pathname}`
  
  try {
    const response = await fetch(backendUrl, {
      method: request.method,
      headers: request.headers,
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined
    })
    
    const newResponse = new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        ...Object.fromEntries(response.headers.entries()),
        ...corsHeaders
      }
    })
    
    return newResponse
  } catch (error) {
    return createResponse(`API代理错误: ${error.message}`, 502, corsHeaders)
  }
}

// 创建响应
function createResponse(content, status = 200, headers = {}, contentType = 'text/plain') {
  return new Response(content, {
    status: status,
    headers: {
      'Content-Type': `${contentType}; charset=utf-8`,
      ...headers
    }
  })
}