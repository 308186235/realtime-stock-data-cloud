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

  const balanceData = {
    account_info: {
      account_id: "NTF888888",
      account_name: "Netlify交易账户",
      account_type: "云端模拟账户",
      broker: "Netlify Functions",
      region: "Global"
    },
    balance: {
      total_assets: 150000.00,
      available_cash: 65000.00,
      market_value: 85000.00,
      frozen_amount: 0.00,
      profit_loss: 15000.00,
      profit_loss_rate: 11.11,
      currency: "CNY"
    },
    daily_stats: {
      today_profit_loss: 2500.00,
      today_profit_loss_rate: 1.69,
      today_turnover: 25000.00,
      today_commission: 15.50,
      trade_count: 8
    },
    risk_info: {
      risk_level: "低风险",
      margin_ratio: 0.00,
      available_margin: 0.00,
      position_ratio: 56.67
    },
    server: "netlify-functions",
    deployment: "git-connected",
    timestamp: new Date().toISOString(),
    last_update: new Date().toISOString()
  };

  return {
    statusCode: 200,
    headers,
    body: JSON.stringify(balanceData, null, 2)
  };
};
