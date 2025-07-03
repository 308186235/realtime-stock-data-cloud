// 实时数据API处理器 - 对应Python的realtime_stock_simple和realtime_data_api

// 实时数据API处理
export async function handleRealtimeAPI(path, request, env) {
  const segments = path.split('/');
  const action = segments[3]; // /api/realtime/{action} 或 /api/realtime-data/{action}

  // 实时数据API
  if (path.startsWith('/api/realtime-data/')) {
    return handleRealtimeDataAPI(path, request, env);
  }

  // 简单实时股票API
  switch (action) {
    case 'stocks':
      return getRealtimeStocks(request, env);
    case 'quote':
      return getRealtimeQuote(request, env);
    case 'push':
      return handleRealtimePush(request, env);
    case 'subscribe':
      return subscribeRealtimeData(request, env);
    case 'unsubscribe':
      return unsubscribeRealtimeData(request, env);
    case 'status':
      return getRealtimeStatus(env);
    default:
      return createErrorResponse('实时数据API端点未找到', 404);
  }
}

// 实时数据详细API处理
async function handleRealtimeDataAPI(path, request, env) {
  const segments = path.split('/');
  const action = segments[3]; // /api/realtime-data/{action}

  switch (action) {
    case 'all':
      return getAllRealtimeData(env);
    case 'market':
      return getMarketRealtimeData(request, env);
    case 'sector':
      return getSectorRealtimeData(request, env);
    case 'top':
      return getTopStocks(request, env);
    case 'alerts':
      return getRealtimeAlerts(env);
    default:
      return createErrorResponse('实时数据详细API端点未找到', 404);
  }
}

// 获取实时股票数据
async function getRealtimeStocks(request, env) {
  try {
    const url = new URL(request.url);
    const codes = url.searchParams.get('codes'); // 股票代码列表，逗号分隔
    const limit = parseInt(url.searchParams.get('limit')) || 20;

    // 如果指定了股票代码
    if (codes) {
      const stockCodes = codes.split(',').slice(0, 50); // 最多50只股票
      const stocks = stockCodes.map(code => generateRealtimeStock(code.trim()));
      
      return createResponse({
        success: true,
        data: stocks,
        count: stocks.length,
        timestamp: new Date().toISOString()
      });
    }

    // 返回热门股票实时数据
    const popularStocks = [
      '000001', '000002', '000858', '600000', '600036', '600519', '600887',
      '000858', '002415', '300059', '300750', '688981', '688599', '688036'
    ];

    const stocks = popularStocks.slice(0, limit).map(code => generateRealtimeStock(code));

    return createResponse({
      success: true,
      data: stocks,
      count: stocks.length,
      timestamp: new Date().toISOString(),
      source: 'realtime_api'
    });

  } catch (error) {
    return createErrorResponse(`获取实时股票数据失败: ${error.message}`, 500);
  }
}

// 获取单只股票实时行情
async function getRealtimeQuote(request, env) {
  try {
    const url = new URL(request.url);
    const code = url.searchParams.get('code') || '000001';

    // 从KV缓存获取数据
    const cacheKey = `quote_${code}`;
    const cachedQuote = await env.TRADING_KV?.get(cacheKey);
    
    if (cachedQuote) {
      const quote = JSON.parse(cachedQuote);
      // 检查缓存是否过期（3秒）
      if (Date.now() - quote.timestamp < 3000) {
        return createResponse({
          success: true,
          data: quote.data,
          source: 'cache'
        });
      }
    }

    // 生成实时行情数据
    const quote = generateRealtimeStock(code);

    // 缓存数据
    await env.TRADING_KV?.put(cacheKey, JSON.stringify({
      data: quote,
      timestamp: Date.now()
    }), { expirationTtl: 10 }); // 10秒过期

    return createResponse({
      success: true,
      data: quote,
      source: 'realtime'
    });

  } catch (error) {
    return createErrorResponse(`获取实时行情失败: ${error.message}`, 500);
  }
}

// 处理实时数据推送
async function handleRealtimePush(request, env) {
  try {
    if (request.method !== 'POST') {
      return createErrorResponse('仅支持POST请求', 405);
    }

    const body = await request.json();
    const action = body.action || 'start';

    switch (action) {
      case 'start':
        return startRealtimePush(body, env);
      case 'stop':
        return stopRealtimePush(body, env);
      case 'status':
        return getRealtimePushStatus(env);
      default:
        return createErrorResponse('未知的推送操作', 400);
    }

  } catch (error) {
    return createErrorResponse(`处理实时推送失败: ${error.message}`, 500);
  }
}

// 启动实时数据推送
async function startRealtimePush(body, env) {
  try {
    const pushConfig = {
      api_key: CONFIG.STOCK_API_KEY,
      push_interval: 3000, // 3秒推送一次
      stock_count: 5000, // 推送5000只股票
      start_time: new Date().toISOString(),
      status: 'running',
      target_stocks: body.stocks || 'all', // 目标股票
      push_url: body.callback_url || null // 回调URL
    };

    // 保存推送配置
    await env.TRADING_KV?.put('realtime_push_config', JSON.stringify(pushConfig));

    // 模拟启动推送服务
    const pushStatus = {
      success: true,
      message: '实时数据推送已启动',
      config: pushConfig,
      estimated_data_rate: '5000 stocks × 3 seconds = 16,667 updates/minute',
      storage_recommendation: 'Redis队列推荐用于高频数据存储'
    };

    return createResponse(pushStatus);

  } catch (error) {
    return createErrorResponse(`启动实时推送失败: ${error.message}`, 500);
  }
}

// 订阅实时数据
async function subscribeRealtimeData(request, env) {
  try {
    const body = await request.json();
    const subscription = {
      subscription_id: `sub_${Date.now()}`,
      stocks: body.stocks || [],
      callback_url: body.callback_url,
      interval: body.interval || 3000,
      fields: body.fields || ['price', 'volume', 'change'],
      created_at: new Date().toISOString(),
      status: 'active'
    };

    // 保存订阅信息
    await env.TRADING_KV?.put(`subscription_${subscription.subscription_id}`, JSON.stringify(subscription));

    return createResponse({
      success: true,
      message: '实时数据订阅成功',
      data: subscription
    });

  } catch (error) {
    return createErrorResponse(`订阅实时数据失败: ${error.message}`, 500);
  }
}

// 获取所有实时数据
async function getAllRealtimeData(env) {
  try {
    // 模拟获取全市场实时数据
    const marketData = {
      total_stocks: 5000,
      active_stocks: 4856,
      market_status: 'TRADING', // TRADING, CLOSED, PRE_MARKET, AFTER_MARKET
      last_update: new Date().toISOString(),
      market_indices: {
        shanghai: {
          code: '000001',
          name: '上证指数',
          value: 3200.50,
          change: 15.20,
          change_percent: 0.48
        },
        shenzhen: {
          code: '399001',
          name: '深证成指',
          value: 12500.80,
          change: -25.60,
          change_percent: -0.20
        },
        chinext: {
          code: '399006',
          name: '创业板指',
          value: 2800.30,
          change: 8.90,
          change_percent: 0.32
        }
      },
      market_summary: {
        advancing: 2856,
        declining: 1890,
        unchanged: 110,
        total_volume: 285600000000, // 总成交量
        total_turnover: 456800000000 // 总成交额
      },
      top_gainers: generateTopStocks('gainers'),
      top_losers: generateTopStocks('losers'),
      most_active: generateTopStocks('active')
    };

    return createResponse({
      success: true,
      data: marketData
    });

  } catch (error) {
    return createErrorResponse(`获取全市场数据失败: ${error.message}`, 500);
  }
}

// 生成实时股票数据
function generateRealtimeStock(code) {
  const basePrice = 10 + (parseInt(code) % 100);
  const change = (Math.random() - 0.5) * 2; // -1 到 1
  const price = Math.max(0.01, basePrice + change);
  
  return {
    code: code,
    name: getStockName(code),
    price: parseFloat(price.toFixed(2)),
    change: parseFloat(change.toFixed(2)),
    change_percent: parseFloat(((change / basePrice) * 100).toFixed(2)),
    volume: Math.floor(Math.random() * 1000000) + 100000,
    turnover: Math.floor(Math.random() * 100000000) + 10000000,
    high: parseFloat((price + Math.random() * 2).toFixed(2)),
    low: parseFloat((price - Math.random() * 2).toFixed(2)),
    open: parseFloat((price + (Math.random() - 0.5)).toFixed(2)),
    pre_close: parseFloat(basePrice.toFixed(2)),
    bid_price: parseFloat((price - 0.01).toFixed(2)),
    ask_price: parseFloat((price + 0.01).toFixed(2)),
    bid_volume: Math.floor(Math.random() * 10000) + 1000,
    ask_volume: Math.floor(Math.random() * 10000) + 1000,
    timestamp: new Date().toISOString(),
    market: code.startsWith('6') ? 'SH' : 'SZ'
  };
}

// 获取股票名称
function getStockName(code) {
  const stockNames = {
    '000001': '平安银行',
    '000002': '万科A',
    '000858': '五粮液',
    '600000': '浦发银行',
    '600036': '招商银行',
    '600519': '贵州茅台',
    '600887': '伊利股份',
    '002415': '海康威视',
    '300059': '东方财富',
    '300750': '宁德时代'
  };
  
  return stockNames[code] || `股票${code}`;
}

// 生成排行榜数据
function generateTopStocks(type) {
  const stocks = [];
  const codes = ['000001', '000002', '000858', '600000', '600036', '600519', '600887', '002415', '300059', '300750'];
  
  for (let i = 0; i < 10; i++) {
    const code = codes[i] || `00000${i}`;
    const stock = generateRealtimeStock(code);
    
    // 根据类型调整数据
    if (type === 'gainers') {
      stock.change = Math.random() * 5 + 2; // 2-7%涨幅
      stock.change_percent = (stock.change / stock.price) * 100;
    } else if (type === 'losers') {
      stock.change = -(Math.random() * 5 + 2); // 2-7%跌幅
      stock.change_percent = (stock.change / stock.price) * 100;
    } else if (type === 'active') {
      stock.volume = Math.floor(Math.random() * 10000000) + 5000000; // 高成交量
      stock.turnover = stock.volume * stock.price;
    }
    
    stocks.push(stock);
  }
  
  return stocks;
}

// 工具函数
function createResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status: status,
    headers: CONFIG.CORS_HEADERS
  });
}

function createErrorResponse(message, status = 500) {
  return createResponse({
    success: false,
    error: message,
    timestamp: new Date().toISOString()
  }, status);
}
