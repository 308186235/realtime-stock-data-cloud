const { withErrorHandling, validateRequest, checkRateLimit } = require('./utils/error-handler');

// 缓存机制
let cachedBalance = null;
let balanceCacheTime = null;
const BALANCE_CACHE_DURATION = 2 * 60 * 1000; // 2分钟缓存（余额更新频率较高）

async function handleAccountBalance(event, context, requestId) {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json',
    'Cache-Control': 'public, max-age=120', // 2分钟浏览器缓存
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
  if (checkRateLimit(clientIP, 120, 3600)) { // 每小时120次（余额查询频率较高）
    const error = new Error('请求过于频繁，请稍后再试');
    error.name = 'RateLimitError';
    throw error;
  }

  // 检查缓存
  const now = Date.now();
  if (cachedBalance && balanceCacheTime && (now - balanceCacheTime) < BALANCE_CACHE_DURATION) {
    return {
      statusCode: 200,
      headers: { ...headers, 'X-Cache': 'HIT', 'X-Request-ID': requestId },
      body: JSON.stringify(cachedBalance, null, 2)
    };
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
    last_update: new Date().toISOString(),
    cache_info: {
      cache_duration: BALANCE_CACHE_DURATION / 1000 + 's',
      cached: false
    }
  };

  // 更新缓存
  cachedBalance = balanceData;
  balanceCacheTime = now;

  return {
    statusCode: 200,
    headers: { ...headers, 'X-Cache': 'MISS', 'X-Request-ID': requestId },
    body: JSON.stringify(balanceData, null, 2)
  };
}

// 导出包装后的处理函数
exports.handler = async (event, context) => {
  return withErrorHandling(handleAccountBalance, event, context);
};
