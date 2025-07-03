// Cloudflare Pages Functions - Health Check
export async function onRequest(context) {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json',
    'Cache-Control': 'public, max-age=60' // 1分钟缓存
  };

  if (context.request.method === 'OPTIONS') {
    return new Response('', { headers });
  }

  // 检查请求方法
  if (context.request.method !== 'GET') {
    return new Response(JSON.stringify({
      error: `不支持的请求方法: ${context.request.method}`
    }), {
      status: 405,
      headers
    });
  }

  const healthData = {
    status: "healthy",
    server: "cloudflare-pages",
    timestamp: new Date().toISOString(),
    message: "🎉 交易系统API运行正常！[Cloudflare Pages版本]",
    api_version: "2.1.0",
    deployment: "cloudflare-pages",
    endpoints: {
      health: "/api/health",
      account_balance: "/api/account-balance",
      account_positions: "/api/account-positions",
      agent_analysis: "/api/agent-analysis",
      real_stock_api: "/api/real-stock-api",
      quotes: "/api/quotes"
    },
    cors_enabled: true,
    last_updated: new Date().toISOString(),
    platform: "Cloudflare Pages Functions"
  };

  return new Response(JSON.stringify(healthData, null, 2), {
    headers
  });
}
