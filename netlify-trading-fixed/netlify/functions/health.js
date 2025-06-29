exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  const healthData = {
    status: "healthy",
    server: "netlify-functions",
    timestamp: new Date().toISOString(),
    uptime: "running",
    region: process.env.AWS_REGION || "unknown",
    environment: "production",
    api_version: "1.0.0",
    message: "🎉 交易系统API运行正常！",
    endpoints: {
      health: "/api/health",
      account_balance: "/api/account-balance",
      account_positions: "/api/account-positions", 
      trading_orders: "/api/trading-orders",
      agent_analysis: "/api/agent-analysis"
    }
  };

  return {
    statusCode: 200,
    headers,
    body: JSON.stringify(healthData, null, 2)
  };
};
