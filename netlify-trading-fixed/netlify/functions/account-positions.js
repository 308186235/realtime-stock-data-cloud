exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  const positionsData = {
    account_info: {
      account_id: "NTF888888",
      account_name: "Netlify交易账户"
    },
    summary: {
      total_positions: 3,
      total_market_value: 85000.00,
      total_cost: 82500.00,
      total_profit_loss: 2500.00,
      total_profit_loss_rate: 3.03,
      today_profit_loss: 850.00
    },
    positions: [
      {
        symbol: "000001",
        name: "平安银行",
        quantity: 2000,
        available_quantity: 2000,
        avg_price: 10.50,
        current_price: 11.20,
        cost_amount: 21000.00,
        market_value: 22400.00,
        profit_loss: 1400.00,
        profit_loss_rate: 6.67,
        today_profit_loss: 400.00,
        weight: 26.35
      },
      {
        symbol: "000002",
        name: "万科A",
        quantity: 1500,
        available_quantity: 1500,
        avg_price: 12.20,
        current_price: 13.60,
        cost_amount: 18300.00,
        market_value: 20400.00,
        profit_loss: 2100.00,
        profit_loss_rate: 11.48,
        today_profit_loss: 210.00,
        weight: 24.00
      },
      {
        symbol: "600519",
        name: "贵州茅台",
        quantity: 50,
        available_quantity: 50,
        avg_price: 1680.00,
        current_price: 1730.00,
        cost_amount: 84000.00,
        market_value: 86500.00,
        profit_loss: 2500.00,
        profit_loss_rate: 2.98,
        today_profit_loss: 250.00,
        weight: 101.76
      }
    ],
    server: "netlify-functions",
    timestamp: new Date().toISOString(),
    last_update: new Date().toISOString()
  };

  return {
    statusCode: 200,
    headers,
    body: JSON.stringify(positionsData, null, 2)
  };
};
