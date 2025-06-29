// Netlify Function - 持仓信息
exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  const positionsData = {
    summary: {
      total_positions: 4,
      total_market_value: 85000.00,
      total_cost: 70000.00,
      total_profit_loss: 15000.00,
      total_profit_loss_rate: 21.43,
      position_ratio: 56.67
    },
    positions: [
      {
        symbol: "000001",
        name: "平安银行",
        quantity: 2000,
        available_quantity: 2000,
        avg_price: 12.50,
        current_price: 13.85,
        cost_amount: 25000.00,
        market_value: 27700.00,
        profit_loss: 2700.00,
        profit_loss_rate: 10.80,
        today_profit_loss: 270.00,
        weight: 32.59
      },
      {
        symbol: "600000",
        name: "浦发银行",
        quantity: 3000,
        available_quantity: 3000,
        avg_price: 8.80,
        current_price: 9.45,
        cost_amount: 26400.00,
        market_value: 28350.00,
        profit_loss: 1950.00,
        profit_loss_rate: 7.39,
        today_profit_loss: 195.00,
        weight: 33.35
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
    body: JSON.stringify(positionsData)
  };
};
