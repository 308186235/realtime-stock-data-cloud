/**
 * Cloudflare Worker - API代理
 * 将 api.aigupiao.me 的请求代理到后端服务
 */

// 后端服务地址 - 当前使用ngrok隧道
const BACKEND_URL = 'https://1591-39-188-128-188.ngrok-free.app';

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // 获取请求的URL
  const url = new URL(request.url)
  
  // 构建目标URL - 将域名替换为后端地址
  const targetUrl = new URL(url.pathname + url.search, BACKEND_URL)
  
  // 复制请求头，但移除Host头
  const headers = new Headers(request.headers)
  headers.delete('host')
  
  // 添加ngrok需要的头部
  headers.set('ngrok-skip-browser-warning', 'true')
  
  // 创建新的请求
  const newRequest = new Request(targetUrl, {
    method: request.method,
    headers: headers,
    body: request.body
  })
  
  try {
    // 发送请求到后端服务
    const response = await fetch(newRequest)
    
    // 创建新的响应，添加CORS头
    const newResponse = new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        ...Object.fromEntries(response.headers),
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      }
    })
    
    return newResponse
    
  } catch (error) {
    // 错误处理
    return new Response(JSON.stringify({
      error: 'Proxy Error',
      message: error.message,
      target: targetUrl.toString()
    }), {
      status: 502,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    })
  }
}

// 处理OPTIONS预检请求
addEventListener('fetch', event => {
  if (event.request.method === 'OPTIONS') {
    event.respondWith(new Response(null, {
      status: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      }
    }))
  }
})
