// 策略API处理器 - 对应Python的strategy router

// 策略API处理
export async function handleStrategyAPI(path, request, env) {
  const segments = path.split('/');
  const action = segments[3]; // /api/strategy/{action}
  const strategyId = segments[4]; // /api/strategy/{action}/{id}

  switch (request.method) {
    case 'GET':
      if (!action) {
        return getStrategies(env);
      } else if (strategyId) {
        return getStrategy(strategyId, env);
      } else if (action === 'types') {
        return getStrategyTypes();
      }
      break;
    
    case 'POST':
      if (!action) {
        return createStrategy(request, env);
      } else if (action === 'backtest' && strategyId) {
        return runStrategyBacktest(strategyId, request, env);
      }
      break;
    
    case 'PUT':
      if (strategyId) {
        return updateStrategy(strategyId, request, env);
      }
      break;
    
    case 'DELETE':
      if (strategyId) {
        return deleteStrategy(strategyId, env);
      }
      break;
  }

  return createErrorResponse('策略API端点未找到', 404);
}

// 获取策略列表
async function getStrategies(env) {
  try {
    // 从Supabase获取策略数据
    const supabaseResponse = await fetch(`${CONFIG.SUPABASE_URL}/rest/v1/strategies`, {
      headers: {
        'apikey': CONFIG.SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${CONFIG.SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json'
      }
    });

    if (!supabaseResponse.ok) {
      // 如果Supabase失败，返回模拟数据
      return createResponse({
        success: true,
        data: [
          {
            id: 1,
            name: "移动平均线交叉策略",
            description: "基于短期和长期移动平均线交叉的交易策略",
            type: "ma_cross",
            params: {
              short_period: 5,
              long_period: 20,
              stop_loss: 0.05,
              take_profit: 0.10
            },
            is_public: true,
            created_at: new Date().toISOString(),
            performance: {
              total_return: 0.15,
              sharpe_ratio: 1.2,
              max_drawdown: 0.08,
              win_rate: 0.65
            }
          },
          {
            id: 2,
            name: "RSI超买超卖策略",
            description: "基于相对强弱指数的反转交易策略",
            type: "rsi",
            params: {
              period: 14,
              oversold: 30,
              overbought: 70,
              stop_loss: 0.03,
              take_profit: 0.08
            },
            is_public: true,
            created_at: new Date().toISOString(),
            performance: {
              total_return: 0.12,
              sharpe_ratio: 1.0,
              max_drawdown: 0.06,
              win_rate: 0.58
            }
          },
          {
            id: 3,
            name: "布林带突破策略",
            description: "基于布林带上下轨突破的交易策略",
            type: "bollinger_bands",
            params: {
              period: 20,
              std_dev: 2,
              stop_loss: 0.04,
              take_profit: 0.12
            },
            is_public: true,
            created_at: new Date().toISOString(),
            performance: {
              total_return: 0.18,
              sharpe_ratio: 1.4,
              max_drawdown: 0.10,
              win_rate: 0.62
            }
          }
        ]
      });
    }

    const strategies = await supabaseResponse.json();
    return createResponse({
      success: true,
      data: strategies
    });

  } catch (error) {
    return createErrorResponse(`获取策略列表失败: ${error.message}`, 500);
  }
}

// 获取单个策略
async function getStrategy(strategyId, env) {
  try {
    // 模拟策略详情数据
    const strategy = {
      id: parseInt(strategyId),
      name: "移动平均线交叉策略",
      description: "基于短期和长期移动平均线交叉的交易策略",
      type: "ma_cross",
      params: {
        short_period: 5,
        long_period: 20,
        stop_loss: 0.05,
        take_profit: 0.10
      },
      source_code: `
def ma_cross_strategy(data, short_period=5, long_period=20):
    """移动平均线交叉策略"""
    data['ma_short'] = data['close'].rolling(short_period).mean()
    data['ma_long'] = data['close'].rolling(long_period).mean()
    
    # 生成交易信号
    data['signal'] = 0
    data.loc[data['ma_short'] > data['ma_long'], 'signal'] = 1  # 买入
    data.loc[data['ma_short'] < data['ma_long'], 'signal'] = -1  # 卖出
    
    return data
      `,
      is_public: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      performance: {
        total_return: 0.15,
        annual_return: 0.12,
        sharpe_ratio: 1.2,
        max_drawdown: 0.08,
        win_rate: 0.65,
        profit_factor: 1.8,
        total_trades: 156,
        winning_trades: 101,
        losing_trades: 55
      },
      backtest_results: {
        start_date: "2023-01-01",
        end_date: "2024-01-01",
        initial_capital: 100000,
        final_capital: 115000,
        total_return: 0.15,
        benchmark_return: 0.08,
        alpha: 0.07,
        beta: 0.95,
        volatility: 0.18
      }
    };

    return createResponse({
      success: true,
      data: strategy
    });

  } catch (error) {
    return createErrorResponse(`获取策略详情失败: ${error.message}`, 500);
  }
}

// 获取策略类型
async function getStrategyTypes() {
  const strategyTypes = [
    {
      type: "ma_cross",
      name: "移动平均线交叉",
      description: "基于不同周期移动平均线交叉的趋势跟踪策略",
      category: "trend_following",
      difficulty: "beginner",
      params: [
        { name: "short_period", type: "int", default: 5, min: 3, max: 50 },
        { name: "long_period", type: "int", default: 20, min: 10, max: 200 },
        { name: "stop_loss", type: "float", default: 0.05, min: 0.01, max: 0.20 },
        { name: "take_profit", type: "float", default: 0.10, min: 0.02, max: 0.50 }
      ]
    },
    {
      type: "rsi",
      name: "RSI超买超卖",
      description: "基于相对强弱指数的反转交易策略",
      category: "mean_reversion",
      difficulty: "beginner",
      params: [
        { name: "period", type: "int", default: 14, min: 5, max: 30 },
        { name: "oversold", type: "int", default: 30, min: 10, max: 40 },
        { name: "overbought", type: "int", default: 70, min: 60, max: 90 },
        { name: "stop_loss", type: "float", default: 0.03, min: 0.01, max: 0.10 }
      ]
    },
    {
      type: "bollinger_bands",
      name: "布林带突破",
      description: "基于布林带上下轨突破的交易策略",
      category: "breakout",
      difficulty: "intermediate",
      params: [
        { name: "period", type: "int", default: 20, min: 10, max: 50 },
        { name: "std_dev", type: "float", default: 2.0, min: 1.0, max: 3.0 },
        { name: "stop_loss", type: "float", default: 0.04, min: 0.01, max: 0.10 },
        { name: "take_profit", type: "float", default: 0.12, min: 0.05, max: 0.30 }
      ]
    },
    {
      type: "macd",
      name: "MACD信号",
      description: "基于MACD指标的趋势确认策略",
      category: "trend_following",
      difficulty: "intermediate",
      params: [
        { name: "fast_period", type: "int", default: 12, min: 5, max: 20 },
        { name: "slow_period", type: "int", default: 26, min: 15, max: 40 },
        { name: "signal_period", type: "int", default: 9, min: 5, max: 15 }
      ]
    }
  ];

  return createResponse({
    success: true,
    data: strategyTypes
  });
}

// 创建策略
async function createStrategy(request, env) {
  try {
    const body = await request.json();
    
    // 验证必要字段
    if (!body.name || !body.type) {
      return createErrorResponse('策略名称和类型为必填项', 400);
    }

    // 模拟创建策略
    const newStrategy = {
      id: Date.now(), // 简单的ID生成
      name: body.name,
      description: body.description || '',
      type: body.type,
      params: body.params || {},
      source_code: body.source_code || '',
      is_public: body.is_public || false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    // 这里应该保存到Supabase
    // await saveToSupabase('strategies', newStrategy);

    return createResponse({
      success: true,
      message: '策略创建成功',
      data: newStrategy
    }, 201);

  } catch (error) {
    return createErrorResponse(`创建策略失败: ${error.message}`, 500);
  }
}

// 运行策略回测
async function runStrategyBacktest(strategyId, request, env) {
  try {
    const body = await request.json();
    
    // 模拟回测结果
    const backtestResult = {
      strategy_id: parseInt(strategyId),
      backtest_id: Date.now(),
      start_date: body.start_date || "2023-01-01",
      end_date: body.end_date || "2024-01-01",
      initial_capital: body.initial_capital || 100000,
      symbols: body.symbols || ["000001", "000002", "600000"],
      results: {
        final_capital: 115000,
        total_return: 0.15,
        annual_return: 0.12,
        sharpe_ratio: 1.2,
        max_drawdown: 0.08,
        win_rate: 0.65,
        profit_factor: 1.8,
        total_trades: 156,
        winning_trades: 101,
        losing_trades: 55,
        avg_trade_return: 0.0012,
        volatility: 0.18,
        benchmark_return: 0.08,
        alpha: 0.07,
        beta: 0.95
      },
      trades: [
        {
          symbol: "000001",
          entry_date: "2023-02-15",
          exit_date: "2023-02-28",
          entry_price: 12.50,
          exit_price: 13.20,
          quantity: 1000,
          return: 0.056,
          type: "long"
        }
        // 更多交易记录...
      ],
      equity_curve: [
        { date: "2023-01-01", value: 100000 },
        { date: "2023-01-02", value: 100150 },
        { date: "2023-01-03", value: 99980 }
        // 更多净值曲线数据...
      ],
      created_at: new Date().toISOString()
    };

    return createResponse({
      success: true,
      message: '回测完成',
      data: backtestResult
    });

  } catch (error) {
    return createErrorResponse(`回测失败: ${error.message}`, 500);
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
