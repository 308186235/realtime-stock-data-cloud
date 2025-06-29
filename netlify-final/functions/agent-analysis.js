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

  const analysisData = {
    analysis: {
      market_trend: "震荡上涨",
      confidence: 0.78,
      recommendation: "适度买入",
      key_factors: [
        "技术指标MACD金叉",
        "成交量温和放大", 
        "北向资金净流入",
        "板块轮动活跃"
      ],
      risk_level: "中等"
    },
    learning_progress: {
      accuracy: 0.72,
      total_trades: 189,
      win_rate: 0.67,
      profit_factor: 1.45,
      status: "持续学习中"
    },
    market_sentiment: {
      overall: "乐观",
      fear_greed_index: 65,
      volatility: "低",
      momentum: "正向"
    },
    recommendations: [
      {
        symbol: "000001",
        action: "买入",
        confidence: 0.75,
        reason: "技术面突破，基本面稳健"
      },
      {
        symbol: "600519",
        action: "持有", 
        confidence: 0.68,
        reason: "估值合理，长期看好"
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
    body: JSON.stringify(analysisData, null, 2)
  };
};
