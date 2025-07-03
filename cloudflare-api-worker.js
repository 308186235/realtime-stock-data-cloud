/**
 * Cloudflare Workers API - 简化版本
 * 为前端应用提供所需的API端点
 */

// CORS配置
const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'Content-Type': 'application/json'
};

/**
 * Worker主入口
 */
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname;

  // 处理CORS预检请求
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: CORS_HEADERS
    });
  }

  try {
    // 路由分发
    if (path === '/') {
      return handleRoot();
    } else if (path.startsWith('/api/agent-analysis')) {
      return handleAgentAnalysis(path, request);
    } else if (path.startsWith('/api/account-balance')) {
      return handleAccountBalance(path, request);
    } else if (path.startsWith('/api/chagubang')) {
      return handleChaguBang(path, request);
    } else if (path.startsWith('/api/realtime-data')) {
      return handleRealtimeData(path, request);
    } else if (path.startsWith('/api/technical')) {
      return handleTechnical(path, request);
    } else {
      return createErrorResponse('API端点未找到', 404);
    }
  } catch (error) {
    console.error('Worker处理错误:', error);
    return createErrorResponse(`服务器错误: ${error.message}`, 500);
  }
}

/**
 * 根路径处理
 */
function handleRoot() {
  const welcomeData = {
    message: "🚀 AI股票交易系统 API",
    status: "running",
    platform: "Cloudflare Workers",
    timestamp: new Date().toISOString(),
    version: "1.0.0",
    endpoints: {
      agent: "/api/agent-analysis",
      balance: "/api/account-balance", 
      chagubang: "/api/chagubang",
      realtime: "/api/realtime-data",
      technical: "/api/technical"
    }
  };
  
  return createSuccessResponse(welcomeData);
}

/**
 * Agent分析API处理
 */
function handleAgentAnalysis(path, request) {
  const subPath = path.replace('/api/agent-analysis', '');
  
  if (subPath === '' || subPath === '/') {
    // GET /api/agent-analysis
    return createSuccessResponse({
      timestamp: new Date().toISOString(),
      market_sentiment: "neutral",
      confidence_score: 0.75,
      recommendations: [
        {
          action: "hold",
          stock_code: "000001",
          stock_name: "平安银行",
          reason: "技术指标显示横盘整理",
          confidence: 0.8
        },
        {
          action: "buy",
          stock_code: "000002",
          stock_name: "万科A", 
          reason: "突破关键阻力位",
          confidence: 0.7
        }
      ],
      market_analysis: {
        trend: "sideways",
        volatility: "medium",
        volume: "normal",
        risk_level: "medium"
      },
      performance_metrics: {
        total_trades: 156,
        win_rate: 0.68,
        profit_loss: 12580.50,
        max_drawdown: -2340.80,
        sharpe_ratio: 1.45
      }
    });
  } else if (subPath === '/status') {
    // GET /api/agent-analysis/status
    return createSuccessResponse({
      is_running: true,
      last_update: new Date().toISOString(),
      version: "1.0.0",
      uptime: "2天3小时45分钟",
      cpu_usage: 15.6,
      memory_usage: 234.5,
      active_strategies: 3,
      monitoring_stocks: 127,
      connection_status: {
        market_data: "connected",
        trading_api: "connected",
        database: "connected"
      }
    });
  } else if (subPath === '/metrics') {
    // GET /api/agent-analysis/metrics
    return createSuccessResponse({
      performance: {
        total_return: 15.67,
        annual_return: 23.45,
        max_drawdown: -8.92,
        sharpe_ratio: 1.78,
        win_rate: 68.5,
        profit_factor: 2.34
      },
      trading: {
        total_trades: 234,
        winning_trades: 160,
        losing_trades: 74,
        average_win: 156.78,
        average_loss: -89.45
      }
    });
  } else if (subPath === '/config') {
    // GET /api/agent-analysis/config
    return createSuccessResponse({
      risk_tolerance: "medium",
      max_position_size: 0.1,
      stop_loss_percent: 5.0,
      take_profit_percent: 10.0,
      analysis_interval: 300,
      enabled_strategies: ["momentum", "mean_reversion", "breakout"]
    });
  } else if (subPath === '/logs') {
    // GET /api/agent-analysis/logs
    const logs = [];
    for (let i = 0; i < 10; i++) {
      logs.push({
        timestamp: new Date().toISOString(),
        level: i % 3 === 0 ? "WARN" : "INFO",
        message: `Agent执行分析任务 #${i+1}`,
        module: "analysis_engine"
      });
    }
    return createSuccessResponse({ logs, total_count: logs.length });
  }
  
  return createErrorResponse('Agent分析子端点未找到', 404);
}

/**
 * 账户余额API处理
 */
function handleAccountBalance(path, request) {
  const subPath = path.replace('/api/account-balance', '');
  
  if (subPath === '' || subPath === '/') {
    // GET /api/account-balance
    return createSuccessResponse({
      account_info: {
        account_id: "DW123456789",
        account_name: "东吴秀才账户",
        account_type: "股票账户",
        status: "正常",
        last_update: new Date().toISOString()
      },
      balance: {
        total_assets: 125680.50,
        available_cash: 23450.80,
        frozen_cash: 1200.00,
        market_value: 101029.70,
        total_profit_loss: 8650.30,
        profit_loss_percent: 7.38
      },
      positions: [
        {
          stock_code: "000001",
          stock_name: "平安银行",
          quantity: 1000,
          cost_price: 12.50,
          current_price: 13.20,
          market_value: 13200.00,
          profit_loss: 700.00,
          profit_loss_percent: 5.60
        },
        {
          stock_code: "000002",
          stock_name: "万科A",
          quantity: 2000,
          cost_price: 18.80,
          current_price: 19.45,
          market_value: 38900.00,
          profit_loss: 1300.00,
          profit_loss_percent: 3.46
        }
      ]
    });
  } else if (subPath === '/summary') {
    // GET /api/account-balance/summary
    return createSuccessResponse({
      total_assets: 125680.50,
      available_cash: 23450.80,
      market_value: 101029.70,
      today_profit_loss: 1250.30,
      total_profit_loss: 8650.30,
      profit_loss_percent: 7.38,
      position_count: 3,
      last_update: new Date().toISOString()
    });
  } else if (subPath === '/positions') {
    // GET /api/account-balance/positions
    return createSuccessResponse({
      positions: [
        {
          stock_code: "000001",
          stock_name: "平安银行",
          quantity: 1000,
          cost_price: 12.50,
          current_price: 13.20,
          market_value: 13200.00,
          profit_loss: 700.00,
          profit_loss_percent: 5.60
        },
        {
          stock_code: "000002", 
          stock_name: "万科A",
          quantity: 2000,
          cost_price: 18.80,
          current_price: 19.45,
          market_value: 38900.00,
          profit_loss: 1300.00,
          profit_loss_percent: 3.46
        }
      ],
      total_count: 2,
      total_market_value: 52100.00,
      total_profit_loss: 2000.00
    });
  } else if (subPath === '/performance') {
    // GET /api/account-balance/performance
    return createSuccessResponse({
      returns: {
        total_return: 7.38,
        annual_return: 15.67,
        monthly_return: 1.23,
        weekly_return: 0.45
      },
      risk: {
        volatility: 18.45,
        max_drawdown: -8.92,
        sharpe_ratio: 1.34,
        sortino_ratio: 1.78
      },
      trading: {
        win_rate: 68.5,
        profit_factor: 2.34,
        total_trades: 234,
        winning_trades: 160
      }
    });
  }
  
  return createErrorResponse('账户余额子端点未找到', 404);
}

/**
 * 茶股帮API处理
 */
function handleChaguBang(path, request) {
  const subPath = path.replace('/api/chagubang', '');
  
  if (subPath === '/health') {
    return createSuccessResponse({
      status: "healthy",
      service: "chagubang",
      connection_status: "connected",
      total_received: 15420,
      unique_stocks: 4521,
      last_update: new Date().toISOString()
    });
  } else if (subPath === '/stats') {
    return createSuccessResponse({
      total_stocks: 4521,
      last_update: new Date().toISOString(),
      status: "running"
    });
  } else if (subPath.startsWith('/stocks')) {
    return createSuccessResponse({
      data: [
        {
          stock_code: "000001",
          stock_name: "平安银行",
          last_price: 13.20,
          change_pct: 2.34,
          volume: 1500000,
          market: "SZ"
        },
        {
          stock_code: "000002",
          stock_name: "万科A", 
          last_price: 19.45,
          change_pct: -1.23,
          volume: 2300000,
          market: "SZ"
        }
      ],
      total: 2,
      returned: 2
    });
  } else if (subPath === '/market/overview') {
    return createSuccessResponse({
      total_stocks: 4521,
      avg_change: 0.45,
      rising_stocks: 2341,
      falling_stocks: 1876,
      flat_stocks: 304,
      last_update: new Date().toISOString()
    });
  }
  
  return createErrorResponse('茶股帮子端点未找到', 404);
}

/**
 * 实时数据API处理
 */
function handleRealtimeData(path, request) {
  const subPath = path.replace('/api/realtime-data', '');
  
  if (subPath === '/stocks') {
    return createSuccessResponse({
      stocks: [
        {
          code: "000001",
          name: "平安银行",
          price: 13.20,
          change: 0.30,
          change_pct: 2.34
        },
        {
          code: "000002",
          name: "万科A",
          price: 19.45,
          change: -0.24,
          change_pct: -1.23
        }
      ],
      timestamp: new Date().toISOString()
    });
  }
  
  return createErrorResponse('实时数据子端点未找到', 404);
}

/**
 * 技术指标API处理
 */
function handleTechnical(path, request) {
  const subPath = path.replace('/api/technical', '');
  
  if (subPath === '/indicators') {
    return createSuccessResponse({
      indicators: {
        ma5: 13.15,
        ma10: 13.08,
        ma20: 12.95,
        rsi: 65.4,
        macd: 0.12,
        kdj_k: 78.5,
        kdj_d: 72.3
      },
      timestamp: new Date().toISOString()
    });
  }
  
  return createErrorResponse('技术指标子端点未找到', 404);
}

/**
 * 创建成功响应
 */
function createSuccessResponse(data) {
  return new Response(JSON.stringify({
    success: true,
    data: data,
    timestamp: new Date().toISOString()
  }), {
    status: 200,
    headers: CORS_HEADERS
  });
}

/**
 * 创建错误响应
 */
function createErrorResponse(message, status = 500) {
  return new Response(JSON.stringify({
    success: false,
    error: message,
    timestamp: new Date().toISOString()
  }), {
    status: status,
    headers: CORS_HEADERS
  });
}
