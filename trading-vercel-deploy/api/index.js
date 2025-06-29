// 主页API端点
export default function handler(req, res) {
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const welcomeData = {
    message: "🎉 交易系统API已成功部署到Vercel！",
    status: "running",
    server: "vercel-edge-functions",
    timestamp: new Date().toISOString(),
    version: "1.0.0",
    endpoints: {
      health: "/api/health",
      account: {
        balance: "/api/account/balance",
        positions: "/api/account/positions"
      },
      trading: {
        orders: "/api/trading/orders"
      },
      agent: {
        analysis: "/api/agent/analysis",
        trade: "/api/agent/trade"
      },
      stocks: "/api/stocks/[symbol]"
    },
    features: [
      "✅ 账户余额查询",
      "✅ 持仓信息管理", 
      "✅ 交易订单处理",
      "✅ AI智能分析",
      "✅ 实时股票数据",
      "✅ 全球CDN加速",
      "✅ 自动HTTPS加密"
    ]
  };

  res.status(200).json(welcomeData);
}
