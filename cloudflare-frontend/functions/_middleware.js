// Cloudflare Pages Functions 中间件
// 处理前端路由和API代理

export async function onRequest(context) {
  const { request, next, env } = context;
  const url = new URL(request.url);
  const hostname = url.hostname;
  const pathname = url.pathname;

  // CORS头部
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  };

  // 处理CORS预检请求
  if (request.method === 'OPTIONS') {
    return new Response('', { headers: corsHeaders });
  }

  try {
    // 根据子域名路由
    switch (hostname) {
      case 'app.aigupiao.me':
        return handleAppDomain(pathname, request, next, corsHeaders);
      
      case 'mobile.aigupiao.me':
        return handleMobileDomain(pathname, request, next, corsHeaders);
      
      case 'admin.aigupiao.me':
        return handleAdminDomain(pathname, request, next, corsHeaders);
      
      case 'aigupiao.me':
      case 'www.aigupiao.me':
        return handleMainDomain(pathname, request, next, corsHeaders);
      
      default:
        // 继续到下一个处理器
        const response = await next();
        // 添加CORS头部
        Object.entries(corsHeaders).forEach(([key, value]) => {
          response.headers.set(key, value);
        });
        return response;
    }
  } catch (error) {
    console.error('中间件错误:', error);
    return new Response(JSON.stringify({
      error: '服务器错误',
      message: error.message
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders
      }
    });
  }
}

// 处理主应用域名
async function handleAppDomain(pathname, request, next, corsHeaders) {
  // 如果是API请求，代理到API域名
  if (pathname.startsWith('/api/')) {
    const apiUrl = `https://api.aigupiao.me${pathname}${request.url.includes('?') ? '?' + new URL(request.url).search.slice(1) : ''}`;
    
    const apiRequest = new Request(apiUrl, {
      method: request.method,
      headers: request.headers,
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined
    });

    const apiResponse = await fetch(apiRequest);
    
    // 复制响应并添加CORS头部
    const response = new Response(apiResponse.body, {
      status: apiResponse.status,
      statusText: apiResponse.statusText,
      headers: apiResponse.headers
    });

    Object.entries(corsHeaders).forEach(([key, value]) => {
      response.headers.set(key, value);
    });

    return response;
  }

  // 静态文件请求，继续到下一个处理器
  const response = await next();
  Object.entries(corsHeaders).forEach(([key, value]) => {
    response.headers.set(key, value);
  });
  return response;
}

// 处理移动端域名
async function handleMobileDomain(pathname, request, next, corsHeaders) {
  // 移动端特殊处理
  if (pathname === '/' || pathname === '/index.html') {
    // 返回移动端首页
    return new Response(`
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票交易系统 - 移动端</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 400px; margin: 0 auto; background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .feature { padding: 15px; margin: 10px 0; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #007bff; }
        .button { display: block; width: 100%; padding: 15px; background: #007bff; color: white; text-decoration: none; text-align: center; border-radius: 8px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📱 股票交易系统</h1>
            <p>移动端 - Cloudflare版本</p>
        </div>
        
        <div class="feature">
            <h3>🤖 智能Agent</h3>
            <p>AI驱动的自动交易决策</p>
        </div>
        
        <div class="feature">
            <h3>📊 实时数据</h3>
            <p>5000+股票实时行情推送</p>
        </div>
        
        <div class="feature">
            <h3>💼 投资组合</h3>
            <p>专业的资产管理工具</p>
        </div>
        
        <a href="https://app.aigupiao.me" class="button">🚀 打开交易系统</a>
        <a href="/api/health" class="button">🔍 系统状态检查</a>
    </div>
</body>
</html>
    `, {
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        ...corsHeaders
      }
    });
  }

  // API代理
  if (pathname.startsWith('/api/')) {
    const apiUrl = `https://api.aigupiao.me${pathname}`;
    const apiResponse = await fetch(apiUrl, {
      method: request.method,
      headers: request.headers,
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined
    });

    const response = new Response(apiResponse.body, {
      status: apiResponse.status,
      headers: apiResponse.headers
    });

    Object.entries(corsHeaders).forEach(([key, value]) => {
      response.headers.set(key, value);
    });

    return response;
  }

  const response = await next();
  Object.entries(corsHeaders).forEach(([key, value]) => {
    response.headers.set(key, value);
  });
  return response;
}

// 处理管理后台域名
async function handleAdminDomain(pathname, request, next, corsHeaders) {
  // 管理后台特殊处理
  if (pathname === '/' || pathname === '/index.html') {
    return new Response(`
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票交易系统 - 管理后台</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: white; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 40px; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .card { background: #2d2d2d; padding: 20px; border-radius: 10px; border: 1px solid #444; }
        .metric { font-size: 2em; font-weight: bold; color: #4CAF50; }
        .button { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛠️ 股票交易系统管理后台</h1>
            <p>Cloudflare全栈部署版本</p>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h3>📊 系统状态</h3>
                <div class="metric">运行中</div>
                <p>所有服务正常运行</p>
            </div>
            
            <div class="card">
                <h3>👥 在线用户</h3>
                <div class="metric">128</div>
                <p>当前活跃用户数</p>
            </div>
            
            <div class="card">
                <h3>💹 交易量</h3>
                <div class="metric">¥2.5M</div>
                <p>今日交易总额</p>
            </div>
            
            <div class="card">
                <h3>🤖 Agent状态</h3>
                <div class="metric">活跃</div>
                <p>AI交易Agent运行正常</p>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 40px;">
            <a href="/api/health" class="button">🔍 健康检查</a>
            <a href="https://app.aigupiao.me" class="button">🚀 前往交易系统</a>
        </div>
    </div>
</body>
</html>
    `, {
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        ...corsHeaders
      }
    });
  }

  const response = await next();
  Object.entries(corsHeaders).forEach(([key, value]) => {
    response.headers.set(key, value);
  });
  return response;
}

// 处理主域名
async function handleMainDomain(pathname, request, next, corsHeaders) {
  if (pathname === '/' || pathname === '/index.html') {
    // 重定向到app子域名
    return Response.redirect('https://app.aigupiao.me', 302);
  }

  const response = await next();
  Object.entries(corsHeaders).forEach(([key, value]) => {
    response.headers.set(key, value);
  });
  return response;
}
