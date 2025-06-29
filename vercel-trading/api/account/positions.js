// Vercel Edge Function - 持仓信息
export default function handler(req, res) {
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const positionsData = {
    positions: [
      {
        symbol: "000001",
        name: "平安银行",
        quantity: 1000,
        avg_price: 12.50,
        current_price: 13.15,
        market_value: 13150.00,
        profit_loss: 650.00,
        profit_loss_rate: 5.20
      },
      {
        symbol: "600000",
        name: "浦发银行", 
        quantity: 2000,
        avg_price: 8.80,
        current_price: 9.20,
        market_value: 18400.00,
        profit_loss: 800.00,
        profit_loss_rate: 4.55
      },
      {
        symbol: "000002",
        name: "万科A",
        quantity: 1500,
        avg_price: 15.20,
        current_price: 16.80,
        market_value: 25200.00,
        profit_loss: 2400.00,
        profit_loss_rate: 10.53
      }
    ],
    total_positions: 3,
    total_market_value: 56750.00,
    total_profit_loss: 3850.00,
    server: "vercel-edge",
    timestamp: new Date().toISOString()
  };

  res.status(200).json(positionsData);
}
