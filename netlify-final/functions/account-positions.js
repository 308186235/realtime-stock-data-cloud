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
      total_profit_loss_rate: 3.03
    },
    positions: [
      {
        symbol: "000001",
        name: "平安银行",
        quantity: 2000,
        avg_price: 10.50,
        current_price: 11.20,
        market_value: 22400.00,
        profit_loss: 1400.00,
        profit_loss_rate: 6.67
      },
      {
        symbol: "000002", 
        name: "万科A",
        quantity: 1500,
        avg_price: 12.20,
        current_price: 13.60,
        market_value: 20400.00,
        profit_loss: 2100.00,
        profit_loss_rate: 11.48
      },
      {
        symbol: "600519",
        name: "贵州茅台",
        quantity: 50,
        avg_price: 1680.00,
        current_price: 1730.00,
        market_value: 86500.00,
        profit_loss: 2500.00,
        profit_loss_rate: 2.98
      }
    ],
    server: "netlify-functions",
    timestamp: new Date().toISOString()
  };

  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    },
    body: JSON.stringify(positionsData, null, 2)
  };
};
