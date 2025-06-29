// Vercel Edge Function - 账户余额
export default function handler(req, res) {
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const balanceData = {
    total_assets: 100000.00,
    available_cash: 50000.00,
    market_value: 50000.00,
    profit_loss: 5000.00,
    profit_loss_rate: 5.26,
    server: "vercel-edge",
    timestamp: new Date().toISOString()
  };

  res.status(200).json(balanceData);
}
