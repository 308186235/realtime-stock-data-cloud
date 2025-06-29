const { withErrorHandling } = require('./utils/error-handler');

async function handleHealth(event, context, requestId) {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json',
    'Cache-Control': 'public, max-age=60', // 1分钟缓存
    'X-Request-ID': requestId
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  // 检查请求方法
  if (event.httpMethod !== 'GET') {
    throw new Error(`不支持的请求方法: ${event.httpMethod}`);
  }

  const healthData = {
    status: "healthy",
    server: "netlify-functions",
    timestamp: new Date().toISOString(),
    message: "🎉 交易系统API运行正常！[MCP修复版本]",
    api_version: "1.2.0",
    deployment: "git-connected",
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    endpoints: {
      health: "/api/health",
      account_balance: "/api/account-balance",
      account_positions: "/api/account-positions",
      agent_analysis: "/api/agent-analysis"
    },
    cors_enabled: true,
    last_updated: new Date().toISOString()
  };

  return {
    statusCode: 200,
    headers,
    body: JSON.stringify(healthData, null, 2)
  };
}

// 导出包装后的处理函数
exports.handler = async (event, context) => {
  return withErrorHandling(handleHealth, event, context);
};
