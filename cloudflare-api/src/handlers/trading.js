// 交易API处理器 - 对应Python的trading_api和t_trading_api

// 交易API处理
export async function handleTradingAPI(path, request, env) {
  const segments = path.split('/');
  const action = segments[3]; // /api/trading/{action} 或 /api/t-trading/{action}

  // T+0交易API
  if (path.startsWith('/api/t-trading/')) {
    return handleTTradingAPI(path, request, env);
  }

  // 普通交易API
  switch (action) {
    case 'balance':
      return getTradingBalance(env);
    case 'buy':
      return executeBuy(request, env);
    case 'sell':
      return executeSell(request, env);
    case 'orders':
      return getTradingOrders(env);
    case 'summary':
      return getTradingSummary(env);
    case 'execute-trade':
      return executeLocalTrade(request, env);
    case 'export-data':
      return exportLocalData(request, env);
    case 'positions':
      return getTradingPositions(env);
    case 'history':
      return getTradingHistory(request, env);
    default:
      return createErrorResponse('交易API端点未找到', 404);
  }
}

// T+0交易API处理
async function handleTTradingAPI(path, request, env) {
  const segments = path.split('/');
  const action = segments[3]; // /api/t-trading/{action}

  switch (action) {
    case 'evaluate-opportunity':
      return evaluateTTradingOpportunity(request, env);
    case 'record-trade':
      return recordTTrade(request, env);
    case 'statistics':
      return getTTradingStatistics(env);
    default:
      return createErrorResponse('T+0交易API端点未找到', 404);
  }
}

// 获取账户余额
async function getTradingBalance(env) {
  try {
    // 从KV存储获取缓存的余额数据
    const cachedBalance = await env.TRADING_KV?.get('account_balance');
    
    if (cachedBalance) {
      const balance = JSON.parse(cachedBalance);
      // 检查缓存是否过期（5分钟）
      if (Date.now() - balance.timestamp < 5 * 60 * 1000) {
        return createResponse({
          success: true,
          data: balance.data,
          source: 'cache'
        });
      }
    }

    // 模拟从交易软件获取实时余额
    const balance = {
      account_name: "东吴秀才",
      broker_type: "dongwu",
      total_assets: 158765.43,
      available_cash: 98765.43,
      market_value: 60000.00,
      frozen_amount: 0.00,
      profit_loss: 8765.43,
      profit_loss_ratio: 0.0588,
      today_profit: 1234.56,
      today_profit_ratio: 0.0079,
      positions_count: 3,
      last_sync_time: new Date().toISOString(),
      data_source: "trading_software"
    };

    // 缓存余额数据
    await env.TRADING_KV?.put('account_balance', JSON.stringify({
      data: balance,
      timestamp: Date.now()
    }), { expirationTtl: 300 }); // 5分钟过期

    return createResponse({
      success: true,
      data: balance,
      source: 'real_time'
    });

  } catch (error) {
    return createErrorResponse(`获取账户余额失败: ${error.message}`, 500);
  }
}

// 执行买入操作
async function executeBuy(request, env) {
  try {
    const body = await request.json();
    
    // 验证必要参数
    if (!body.stock_code || !body.quantity || !body.price) {
      return createErrorResponse('股票代码、数量和价格为必填项', 400);
    }

    // 模拟本地交易执行
    const tradeOrder = {
      order_id: `BUY_${Date.now()}`,
      stock_code: body.stock_code,
      stock_name: body.stock_name || `股票${body.stock_code}`,
      action: 'BUY',
      quantity: parseInt(body.quantity),
      price: parseFloat(body.price),
      order_type: body.order_type || 'LIMIT',
      status: 'PENDING',
      created_at: new Date().toISOString(),
      broker: 'dongwu_xiucai',
      estimated_amount: parseInt(body.quantity) * parseFloat(body.price),
      commission: parseInt(body.quantity) * parseFloat(body.price) * 0.0003, // 万三手续费
      execution_method: 'local_software'
    };

    // 这里应该调用本地交易软件API
    // const result = await executeLocalTradeCommand(tradeOrder);

    // 模拟执行结果
    tradeOrder.status = 'EXECUTED';
    tradeOrder.executed_at = new Date().toISOString();
    tradeOrder.executed_price = tradeOrder.price;
    tradeOrder.executed_quantity = tradeOrder.quantity;

    // 保存交易记录到KV
    await env.TRADING_KV?.put(`trade_${tradeOrder.order_id}`, JSON.stringify(tradeOrder));

    return createResponse({
      success: true,
      message: '买入订单已提交',
      data: tradeOrder
    });

  } catch (error) {
    return createErrorResponse(`执行买入失败: ${error.message}`, 500);
  }
}

// 执行卖出操作
async function executeSell(request, env) {
  try {
    const body = await request.json();
    
    // 验证必要参数
    if (!body.stock_code || !body.quantity || !body.price) {
      return createErrorResponse('股票代码、数量和价格为必填项', 400);
    }

    // 模拟本地交易执行
    const tradeOrder = {
      order_id: `SELL_${Date.now()}`,
      stock_code: body.stock_code,
      stock_name: body.stock_name || `股票${body.stock_code}`,
      action: 'SELL',
      quantity: parseInt(body.quantity),
      price: parseFloat(body.price),
      order_type: body.order_type || 'LIMIT',
      status: 'PENDING',
      created_at: new Date().toISOString(),
      broker: 'dongwu_xiucai',
      estimated_amount: parseInt(body.quantity) * parseFloat(body.price),
      commission: parseInt(body.quantity) * parseFloat(body.price) * 0.0003,
      stamp_tax: parseInt(body.quantity) * parseFloat(body.price) * 0.001, // 千一印花税
      execution_method: 'local_software'
    };

    // 模拟执行结果
    tradeOrder.status = 'EXECUTED';
    tradeOrder.executed_at = new Date().toISOString();
    tradeOrder.executed_price = tradeOrder.price;
    tradeOrder.executed_quantity = tradeOrder.quantity;

    // 保存交易记录到KV
    await env.TRADING_KV?.put(`trade_${tradeOrder.order_id}`, JSON.stringify(tradeOrder));

    return createResponse({
      success: true,
      message: '卖出订单已提交',
      data: tradeOrder
    });

  } catch (error) {
    return createErrorResponse(`执行卖出失败: ${error.message}`, 500);
  }
}

// 获取交易订单
async function getTradingOrders(env) {
  try {
    // 模拟订单数据
    const orders = [
      {
        order_id: "BUY_1704067200000",
        stock_code: "000001",
        stock_name: "平安银行",
        action: "BUY",
        quantity: 1000,
        price: 12.50,
        executed_price: 12.48,
        executed_quantity: 1000,
        status: "EXECUTED",
        order_type: "LIMIT",
        created_at: "2024-01-01T09:30:00Z",
        executed_at: "2024-01-01T09:30:15Z",
        commission: 3.75,
        amount: 12480.00
      },
      {
        order_id: "SELL_1704153600000",
        stock_code: "000002",
        stock_name: "万科A",
        action: "SELL",
        quantity: 500,
        price: 18.20,
        executed_price: 18.15,
        executed_quantity: 500,
        status: "EXECUTED",
        order_type: "LIMIT",
        created_at: "2024-01-02T14:30:00Z",
        executed_at: "2024-01-02T14:30:08Z",
        commission: 2.72,
        stamp_tax: 9.08,
        amount: 9075.00
      }
    ];

    return createResponse({
      success: true,
      data: orders
    });

  } catch (error) {
    return createErrorResponse(`获取交易订单失败: ${error.message}`, 500);
  }
}

// 获取交易汇总
async function getTradingSummary(env) {
  try {
    const summary = {
      today: {
        trades_count: 5,
        buy_count: 3,
        sell_count: 2,
        total_amount: 125000.00,
        profit_loss: 1234.56,
        profit_loss_ratio: 0.0099,
        commission: 37.50,
        stamp_tax: 62.50
      },
      this_week: {
        trades_count: 23,
        buy_count: 12,
        sell_count: 11,
        total_amount: 580000.00,
        profit_loss: 5678.90,
        profit_loss_ratio: 0.0098,
        commission: 174.00,
        stamp_tax: 290.00
      },
      this_month: {
        trades_count: 89,
        buy_count: 45,
        sell_count: 44,
        total_amount: 2150000.00,
        profit_loss: 18765.43,
        profit_loss_ratio: 0.0087,
        commission: 645.00,
        stamp_tax: 1075.00
      },
      statistics: {
        win_rate: 0.65,
        avg_profit: 1250.00,
        avg_loss: -680.00,
        max_profit: 5600.00,
        max_loss: -2100.00,
        profit_factor: 1.84,
        sharpe_ratio: 1.23
      }
    };

    return createResponse({
      success: true,
      data: summary
    });

  } catch (error) {
    return createErrorResponse(`获取交易汇总失败: ${error.message}`, 500);
  }
}

// T+0交易机会评估
async function evaluateTTradingOpportunity(request, env) {
  try {
    const body = await request.json();
    const stockCode = body.stock_code || '000001';

    // 模拟T+0交易机会分析
    const evaluation = {
      stock_code: stockCode,
      stock_name: `股票${stockCode}`,
      current_price: 12.50 + Math.random() * 2,
      evaluation_time: new Date().toISOString(),
      opportunity_score: 0.7 + Math.random() * 0.3, // 0.7-1.0
      recommendation: Math.random() > 0.5 ? 'BUY' : 'HOLD',
      factors: {
        technical_score: 0.8,
        volume_score: 0.7,
        momentum_score: 0.6,
        volatility_score: 0.9
      },
      risk_assessment: {
        risk_level: 'MEDIUM',
        max_position_size: 1000,
        stop_loss_price: 12.00,
        take_profit_price: 13.20
      },
      market_conditions: {
        market_trend: 'BULLISH',
        sector_performance: 'POSITIVE',
        volume_ratio: 1.2,
        volatility: 0.025
      }
    };

    return createResponse({
      success: true,
      data: evaluation
    });

  } catch (error) {
    return createErrorResponse(`T+0机会评估失败: ${error.message}`, 500);
  }
}

// 记录T+0交易
async function recordTTrade(request, env) {
  try {
    const body = await request.json();

    const tTrade = {
      trade_id: `T_${Date.now()}`,
      stock_code: body.stock_code,
      stock_name: body.stock_name,
      buy_price: body.buy_price,
      sell_price: body.sell_price,
      quantity: body.quantity,
      buy_time: body.buy_time,
      sell_time: body.sell_time,
      profit_loss: (body.sell_price - body.buy_price) * body.quantity,
      profit_loss_ratio: (body.sell_price - body.buy_price) / body.buy_price,
      commission: body.quantity * (body.buy_price + body.sell_price) * 0.0003,
      stamp_tax: body.quantity * body.sell_price * 0.001,
      net_profit: 0, // 计算后填入
      created_at: new Date().toISOString()
    };

    // 计算净利润
    tTrade.net_profit = tTrade.profit_loss - tTrade.commission - tTrade.stamp_tax;

    // 保存到KV存储
    await env.TRADING_KV?.put(`t_trade_${tTrade.trade_id}`, JSON.stringify(tTrade));

    return createResponse({
      success: true,
      message: 'T+0交易记录已保存',
      data: tTrade
    });

  } catch (error) {
    return createErrorResponse(`记录T+0交易失败: ${error.message}`, 500);
  }
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
