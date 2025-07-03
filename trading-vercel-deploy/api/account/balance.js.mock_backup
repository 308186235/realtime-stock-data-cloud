// 账户余额API
export default function handler(req, res) {
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // 模拟账户余额数据
  const balanceData = {
    account_info: {
      account_id: "VCL888888",
      account_name: "Vercel交易账户",
      account_type: "普通账户"
    },
    balance: {
      total_assets: 150000.00,
      available_cash: 65000.00,
      market_value: 85000.00,
      frozen_amount: 0.00,
      profit_loss: 15000.00,
      profit_loss_rate: 11.11
    },
    daily_stats: {
      today_profit_loss: 2500.00,
      today_profit_loss_rate: 1.69,
      today_turnover: 25000.00,
      today_commission: 15.50
    },
    risk_info: {
      risk_level: "低风险",
      margin_ratio: 0.00,
      available_margin: 0.00,
      position_ratio: 56.67
    },
    server: "vercel-edge",
    timestamp: new Date().toISOString(),
    last_update: new Date().toISOString()
  };

  res.status(200).json(balanceData);
}
