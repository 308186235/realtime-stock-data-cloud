exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  const healthData = {
    status: "healthy",
    server: "netlify-functions",
    timestamp: new Date().toISOString(),
    message: "🎉 交易系统API运行正常！",
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
};
