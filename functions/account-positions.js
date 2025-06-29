const { withErrorHandling, validateRequest, checkRateLimit } = require('./utils/error-handler');

// 持仓数据缓存
let cachedPositions = null;
let positionsCacheTime = null;
const POSITIONS_CACHE_DURATION = 3 * 60 * 1000; // 3分钟缓存

async function handleAccountPositions(event, context, requestId) {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json',
    'Cache-Control': 'public, max-age=180', // 3分钟浏览器缓存
    'X-Content-Type-Options': 'nosniff'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  // 检查请求方法
  if (event.httpMethod !== 'GET') {
    throw new Error(`不支持的请求方法: ${event.httpMethod}`);
  }

  // 频率限制检查
  const clientIP = event.headers['x-forwarded-for'] || event.headers['x-real-ip'] || 'unknown';
  if (checkRateLimit(clientIP, 100, 3600)) { // 每小时100次
    const error = new Error('请求过于频繁，请稍后再试');
    error.name = 'RateLimitError';
    throw error;
  }

  // 检查缓存
  const now = Date.now();
  if (cachedPositions && positionsCacheTime && (now - positionsCacheTime) < POSITIONS_CACHE_DURATION) {
    return {
      statusCode: 200,
      headers: { ...headers, 'X-Cache': 'HIT', 'X-Request-ID': requestId },
      body: JSON.stringify(cachedPositions, null, 2)
    };
  }

  const positionsData = {
    account_info: {
      account_id: "NTF888888",
      account_name: "Netlify交易账户",
      account_type: "云端模拟账户",
      broker: "Netlify Functions"
    },
    summary: {
      total_positions: 3,
      total_market_value: 85000.00,
      total_cost: 82500.00,
      total_profit_loss: 2500.00,
      total_profit_loss_rate: 3.03,
      today_profit_loss: 850.00,
      currency: "CNY"
    },
    positions: [
      {
        symbol: "000001",
        name: "平安银行",
        exchange: "SZSE",
        quantity: 2000,
        available_quantity: 2000,
        avg_price: 10.50,
        current_price: 11.20,
        cost_amount: 21000.00,
        market_value: 22400.00,
        profit_loss: 1400.00,
        profit_loss_rate: 6.67,
        today_profit_loss: 400.00,
        weight: 26.35,
        sector: "金融"
      },
      {
        symbol: "000002", 
        name: "万科A",
        exchange: "SZSE",
        quantity: 1500,
        available_quantity: 1500,
        avg_price: 12.20,
        current_price: 13.60,
        cost_amount: 18300.00,
        market_value: 20400.00,
        profit_loss: 2100.00,
        profit_loss_rate: 11.48,
        today_profit_loss: 210.00,
        weight: 24.00,
        sector: "房地产"
      },
      {
        symbol: "600519",
        name: "贵州茅台",
        exchange: "SSE",
        quantity: 50,
        available_quantity: 50,
        avg_price: 1680.00,
        current_price: 1730.00,
        cost_amount: 84000.00,
        market_value: 86500.00,
        profit_loss: 2500.00,
        profit_loss_rate: 2.98,
        today_profit_loss: 250.00,
        weight: 101.76,
        sector: "消费"
      }
    ],
    server: "netlify-functions",
    deployment: "git-connected",
    timestamp: new Date().toISOString(),
    last_update: new Date().toISOString(),
    cache_info: {
      cache_duration: POSITIONS_CACHE_DURATION / 1000 + 's',
      cached: false
    }
  };

  // 更新缓存
  cachedPositions = positionsData;
  positionsCacheTime = now;

  return {
    statusCode: 200,
    headers: { ...headers, 'X-Cache': 'MISS', 'X-Request-ID': requestId },
    body: JSON.stringify(positionsData, null, 2)
  };
}

// 导出包装后的处理函数
exports.handler = async (event, context) => {
  return withErrorHandling(handleAccountPositions, event, context);
};
