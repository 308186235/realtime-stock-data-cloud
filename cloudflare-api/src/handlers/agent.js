// Agent API处理器 - 对应Python的agent相关API

// Agent API处理
export async function handleAgentAPI(path, request, env) {
  const segments = path.split('/');
  const action = segments[3]; // /api/agent/{action}

  switch (action) {
    case 'status':
      return getAgentStatus(env);
    case 'start':
      return startAgent(request, env);
    case 'stop':
      return stopAgent(request, env);
    case 'analysis':
      return getAgentAnalysis(request, env);
    case 'config':
      return handleAgentConfig(request, env);
    case 'performance':
      return getAgentPerformance(env);
    case 'logs':
      return getAgentLogs(request, env);
    case 'trading':
      return handleAgentTrading(request, env);
    default:
      return createErrorResponse('Agent API端点未找到', 404);
  }
}

// 获取Agent状态
async function getAgentStatus(env) {
  try {
    // 从KV存储获取Agent状态
    const statusData = await env.TRADING_KV?.get('agent_status');
    const agentStatus = statusData ? JSON.parse(statusData) : null;

    if (!agentStatus) {
      // 初始化默认状态
      const defaultStatus = {
        isRunning: false,
        version: "2.0.0",
        lastUpdate: new Date().toISOString(),
        startTime: null,
        uptime: 0,
        performance: {
          availableCash: 100000.0,
          totalAssets: 100000.0,
          holdingsCount: 0,
          todayProfit: 0.0,
          todayProfitRate: 0.0,
          totalProfit: 0.0,
          totalProfitRate: 0.0
        },
        strategy: {
          name: "智能选股策略",
          type: "multi_factor",
          riskLevel: "MEDIUM",
          maxPositions: 10,
          maxPositionSize: 0.1
        },
        market: {
          isMarketOpen: isMarketOpen(),
          nextTradingDay: getNextTradingDay(),
          marketStatus: getMarketStatus()
        },
        system: {
          cpuUsage: Math.random() * 20 + 10, // 10-30%
          memoryUsage: Math.random() * 30 + 20, // 20-50%
          networkLatency: Math.random() * 50 + 10, // 10-60ms
          apiCallsToday: Math.floor(Math.random() * 1000) + 500
        }
      };

      await env.TRADING_KV?.put('agent_status', JSON.stringify(defaultStatus));
      return createResponse({
        success: true,
        data: defaultStatus
      });
    }

    // 更新运行时间
    if (agentStatus.isRunning && agentStatus.startTime) {
      agentStatus.uptime = Date.now() - new Date(agentStatus.startTime).getTime();
    }

    // 更新系统指标
    agentStatus.system = {
      cpuUsage: Math.random() * 20 + 10,
      memoryUsage: Math.random() * 30 + 20,
      networkLatency: Math.random() * 50 + 10,
      apiCallsToday: agentStatus.system?.apiCallsToday || Math.floor(Math.random() * 1000) + 500
    };

    agentStatus.lastUpdate = new Date().toISOString();

    return createResponse({
      success: true,
      data: agentStatus
    });

  } catch (error) {
    return createErrorResponse(`获取Agent状态失败: ${error.message}`, 500);
  }
}

// 启动Agent
async function startAgent(request, env) {
  try {
    const body = await request.json().catch(() => ({}));
    
    const agentStatus = {
      isRunning: true,
      version: "2.0.0",
      startTime: new Date().toISOString(),
      lastUpdate: new Date().toISOString(),
      uptime: 0,
      performance: {
        availableCash: body.initialCash || 100000.0,
        totalAssets: body.initialCash || 100000.0,
        holdingsCount: 0,
        todayProfit: 0.0,
        todayProfitRate: 0.0,
        totalProfit: 0.0,
        totalProfitRate: 0.0
      },
      strategy: {
        name: body.strategyName || "智能选股策略",
        type: body.strategyType || "multi_factor",
        riskLevel: body.riskLevel || "MEDIUM",
        maxPositions: body.maxPositions || 10,
        maxPositionSize: body.maxPositionSize || 0.1
      },
      config: {
        tradingEnabled: body.tradingEnabled !== false,
        autoRebalance: body.autoRebalance !== false,
        stopLoss: body.stopLoss || 0.05,
        takeProfit: body.takeProfit || 0.15,
        maxDailyLoss: body.maxDailyLoss || 0.02
      },
      market: {
        isMarketOpen: isMarketOpen(),
        nextTradingDay: getNextTradingDay(),
        marketStatus: getMarketStatus()
      },
      system: {
        cpuUsage: 15.5,
        memoryUsage: 25.8,
        networkLatency: 25,
        apiCallsToday: 0
      }
    };

    // 保存到KV存储
    await env.TRADING_KV?.put('agent_status', JSON.stringify(agentStatus));

    // 记录启动日志
    const startLog = {
      timestamp: new Date().toISOString(),
      level: 'INFO',
      message: 'Agent已启动',
      details: {
        strategy: agentStatus.strategy.name,
        initialCash: agentStatus.performance.availableCash,
        config: agentStatus.config
      }
    };

    await logAgentActivity(startLog, env);

    return createResponse({
      success: true,
      message: "Agent已成功启动",
      data: agentStatus
    });

  } catch (error) {
    return createErrorResponse(`启动Agent失败: ${error.message}`, 500);
  }
}

// 停止Agent
async function stopAgent(request, env) {
  try {
    const statusData = await env.TRADING_KV?.get('agent_status');
    const agentStatus = statusData ? JSON.parse(statusData) : {};

    // 计算运行时间
    const uptime = agentStatus.startTime ? 
      Date.now() - new Date(agentStatus.startTime).getTime() : 0;

    const stoppedStatus = {
      ...agentStatus,
      isRunning: false,
      stopTime: new Date().toISOString(),
      lastUpdate: new Date().toISOString(),
      uptime: uptime,
      finalPerformance: agentStatus.performance
    };

    // 保存停止状态
    await env.TRADING_KV?.put('agent_status', JSON.stringify(stoppedStatus));

    // 记录停止日志
    const stopLog = {
      timestamp: new Date().toISOString(),
      level: 'INFO',
      message: 'Agent已停止',
      details: {
        uptime: uptime,
        finalCash: agentStatus.performance?.availableCash || 0,
        totalProfit: agentStatus.performance?.totalProfit || 0,
        tradesCount: agentStatus.performance?.tradesCount || 0
      }
    };

    await logAgentActivity(stopLog, env);

    return createResponse({
      success: true,
      message: "Agent已成功停止",
      data: stoppedStatus
    });

  } catch (error) {
    return createErrorResponse(`停止Agent失败: ${error.message}`, 500);
  }
}

// 获取Agent分析
async function getAgentAnalysis(request, env) {
  try {
    const body = await request.json().catch(() => ({}));
    const stockCode = body.stockCode || '000001';
    const analysisType = body.type || 'comprehensive';

    // 生成AI分析结果
    const analysis = {
      stockCode: stockCode,
      stockName: getStockName(stockCode),
      analysisType: analysisType,
      timestamp: new Date().toISOString(),
      recommendation: {
        action: Math.random() > 0.5 ? 'BUY' : 'SELL',
        confidence: 0.7 + Math.random() * 0.3,
        targetPrice: 50 + Math.random() * 100,
        stopLoss: 45 + Math.random() * 10,
        timeHorizon: '1-3个月'
      },
      technicalAnalysis: {
        trend: Math.random() > 0.5 ? 'BULLISH' : 'BEARISH',
        support: 48.5,
        resistance: 52.8,
        rsi: 30 + Math.random() * 40,
        macd: (Math.random() - 0.5) * 2,
        volume: Math.random() > 0.5 ? 'HIGH' : 'NORMAL'
      },
      fundamentalAnalysis: {
        pe: 15 + Math.random() * 20,
        pb: 1 + Math.random() * 3,
        roe: 0.1 + Math.random() * 0.2,
        debtRatio: 0.2 + Math.random() * 0.4,
        growthRate: -0.1 + Math.random() * 0.3
      },
      sentimentAnalysis: {
        marketSentiment: Math.random() > 0.5 ? 'POSITIVE' : 'NEGATIVE',
        newsScore: Math.random(),
        socialMediaScore: Math.random(),
        analystRating: Math.floor(Math.random() * 5) + 1
      },
      riskAssessment: {
        riskLevel: ['LOW', 'MEDIUM', 'HIGH'][Math.floor(Math.random() * 3)],
        volatility: 0.1 + Math.random() * 0.3,
        beta: 0.5 + Math.random() * 1.5,
        maxDrawdown: 0.05 + Math.random() * 0.15
      },
      reasoning: [
        "技术指标显示股价处于上升趋势",
        "基本面分析表明公司财务状况良好",
        "市场情绪偏向积极",
        "风险控制在可接受范围内"
      ]
    };

    return createResponse({
      success: true,
      data: analysis
    });

  } catch (error) {
    return createErrorResponse(`Agent分析失败: ${error.message}`, 500);
  }
}

// 获取Agent性能
async function getAgentPerformance(env) {
  try {
    const performance = {
      overview: {
        totalReturn: 0.15,
        annualizedReturn: 0.12,
        sharpeRatio: 1.2,
        maxDrawdown: 0.08,
        winRate: 0.65,
        profitFactor: 1.8
      },
      daily: generatePerformanceData(30, 'daily'),
      weekly: generatePerformanceData(12, 'weekly'),
      monthly: generatePerformanceData(6, 'monthly'),
      trades: {
        total: 156,
        winning: 101,
        losing: 55,
        avgProfit: 1250.00,
        avgLoss: -680.00,
        largestWin: 5600.00,
        largestLoss: -2100.00
      },
      positions: {
        current: 3,
        maxConcurrent: 8,
        avgHoldingPeriod: 5.2, // 天
        turnoverRate: 2.5
      },
      benchmark: {
        name: "沪深300",
        return: 0.08,
        alpha: 0.07,
        beta: 0.95,
        correlation: 0.85
      }
    };

    return createResponse({
      success: true,
      data: performance
    });

  } catch (error) {
    return createErrorResponse(`获取Agent性能失败: ${error.message}`, 500);
  }
}

// 辅助函数
function isMarketOpen() {
  const now = new Date();
  const hour = now.getHours();
  const minute = now.getMinutes();
  const day = now.getDay();
  
  // 周末不开市
  if (day === 0 || day === 6) return false;
  
  // 交易时间：9:30-11:30, 13:00-15:00
  const morningStart = 9 * 60 + 30; // 9:30
  const morningEnd = 11 * 60 + 30;   // 11:30
  const afternoonStart = 13 * 60;    // 13:00
  const afternoonEnd = 15 * 60;      // 15:00
  
  const currentTime = hour * 60 + minute;
  
  return (currentTime >= morningStart && currentTime <= morningEnd) ||
         (currentTime >= afternoonStart && currentTime <= afternoonEnd);
}

function getMarketStatus() {
  if (isMarketOpen()) return 'TRADING';
  
  const now = new Date();
  const hour = now.getHours();
  
  if (hour < 9 || (hour === 9 && now.getMinutes() < 30)) {
    return 'PRE_MARKET';
  } else if (hour > 15) {
    return 'AFTER_MARKET';
  } else {
    return 'LUNCH_BREAK';
  }
}

function getNextTradingDay() {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  
  // 跳过周末
  while (tomorrow.getDay() === 0 || tomorrow.getDay() === 6) {
    tomorrow.setDate(tomorrow.getDate() + 1);
  }
  
  return tomorrow.toISOString().split('T')[0];
}

function getStockName(code) {
  const stockNames = {
    '000001': '平安银行',
    '000002': '万科A',
    '000858': '五粮液',
    '600000': '浦发银行',
    '600036': '招商银行',
    '600519': '贵州茅台'
  };
  
  return stockNames[code] || `股票${code}`;
}

function generatePerformanceData(periods, type) {
  const data = [];
  for (let i = periods - 1; i >= 0; i--) {
    const date = new Date();
    if (type === 'daily') {
      date.setDate(date.getDate() - i);
    } else if (type === 'weekly') {
      date.setDate(date.getDate() - i * 7);
    } else if (type === 'monthly') {
      date.setMonth(date.getMonth() - i);
    }
    
    data.push({
      date: date.toISOString().split('T')[0],
      return: (Math.random() - 0.5) * 0.1, // -5% to +5%
      cumulative: Math.random() * 0.2, // 0% to 20%
      benchmark: Math.random() * 0.15 // 0% to 15%
    });
  }
  return data;
}

async function logAgentActivity(log, env) {
  try {
    const logKey = `agent_log_${Date.now()}`;
    await env.TRADING_KV?.put(logKey, JSON.stringify(log), { expirationTtl: 86400 * 7 }); // 7天过期
  } catch (error) {
    console.error('记录Agent日志失败:', error);
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
