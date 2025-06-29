exports.handler = async (event, context) => {
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

  const balanceData = {
    account_info: {
      account_id: "NTF888888",
      account_name: "Netlify交易账户",
      account_type: "云端模拟账户"
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
    server: "netlify-functions",
    timestamp: new Date().toISOString()
  };

  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    },
    body: JSON.stringify(balanceData, null, 2)
  };
};
