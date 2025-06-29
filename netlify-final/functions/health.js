exports.handler = async (event, context) => {
  // 处理CORS预检请求
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
      },
      body: ''
    };
  }

  const healthData = {
    status: "healthy",
    server: "netlify-functions",
    timestamp: new Date().toISOString(),
    message: "🎉 交易系统API运行正常！",
    api_version: "1.0.0",
    endpoints: {
      health: "/api/health",
      account_balance: "/api/account-balance",
      account_positions: "/api/account-positions",
      agent_analysis: "/api/agent-analysis"
    }
  };

  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    },
    body: JSON.stringify(healthData, null, 2)
  };
};
