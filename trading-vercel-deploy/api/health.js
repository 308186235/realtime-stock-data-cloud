// 健康检查API
export default function handler(req, res) {
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const healthData = {
    status: "healthy",
    server: "vercel-edge",
    timestamp: new Date().toISOString(),
    uptime: "running",
    region: process.env.VERCEL_REGION || "unknown",
    memory_usage: process.memoryUsage ? process.memoryUsage() : "unavailable",
    system_info: {
      platform: process.platform || "vercel",
      node_version: process.version || "unknown",
      environment: process.env.NODE_ENV || "production"
    },
    api_status: {
      account_api: "operational",
      trading_api: "operational", 
      agent_api: "operational",
      stock_api: "operational"
    }
  };

  res.status(200).json(healthData);
}
