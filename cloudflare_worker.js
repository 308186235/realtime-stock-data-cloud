/**
 * Cloudflare Worker - 端口转发脚本
 * 将 https://aigupiao.me 的请求转发到 116.169.10.245:8081
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // 目标服务器配置
  const TARGET_HOST = '116.169.10.245'
  const TARGET_PORT = '8081'
  const TARGET_PROTOCOL = 'http'
  
  // 构建目标URL
  const url = new URL(request.url)
  const targetUrl = `${TARGET_PROTOCOL}://${TARGET_HOST}:${TARGET_PORT}${url.pathname}${url.search}`
  
  console.log(`转发请求: ${request.url} -> ${targetUrl}`)
  
  try {
    // 创建新的请求
    const modifiedRequest = new Request(targetUrl, {
      method: request.method,
      headers: request.headers,
      body: request.body
    })
    
    // 发送请求到目标服务器
    const response = await fetch(modifiedRequest)
    
    // 创建新的响应，添加CORS头
    const modifiedResponse = new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        ...response.headers,
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Credentials': 'true'
      }
    })
    
    return modifiedResponse
    
  } catch (error) {
    console.error('转发请求失败:', error)
    
    return new Response(JSON.stringify({
      error: '服务器连接失败',
      message: error.message,
      target: targetUrl,
      timestamp: new Date().toISOString()
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
    event.respondWith(handleOptions(event.request))
  }
})

async function handleOptions(request) {
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
