/**
 * Agent交易服务
 * 与后端Agent交易API通信
 */

import env from '../env';
import agentDataService from './agentDataService.js';

// 基础URL
const API_BASE_URL = env.apiBaseUrl + '/api/agent-trading';
const T_TRADING_API_URL = env.apiBaseUrl + '/api/t-trading';  // 添加T交易API URL

// 检测是否处于开发环境
const isDevelopment = process.env.NODE_ENV === 'development' || typeof process.env.NODE_ENV === 'undefined';

// 随机延迟函数，模拟网络请求
const delay = (ms = 300) => new Promise(resolve => setTimeout(resolve, Math.random() * ms + ms));

// 全局存储WebSocket连接
let _aiTradingWebsocket = null;

// T+0池更新配置
const T0_POOL_UPDATE_CONFIG = {
  regularInterval: 30, // 常规更新间隔(分钟)
  eodModeStartTime: '14:30:00', // 尾盘模式开始时间
  eodScanInterval: 5, // 尾盘扫描间隔(分钟)
  marketOpenTime: '09:30:00',
  marketCloseTime: '15:00:00',
  autoUpdateEnabled: true, // 是否启用自动更新
  lastUpdateTime: null, // 上次更新时间
  updateTimer: null, // 更新定时器
};

/**
 * 获取Agent交易系统设置
 * @returns {Promise<Object>} 包含系统设置的响应对象，包括策略ID、最大持仓数、风险等级等
 */
export async function getSettings() {
  try {
    // 首先尝试从本地存储获取设置
    const localSettings = uni.getStorageSync('ai_trading_settings');
    let settings = null;
    
    if (localSettings) {
      try {
        settings = JSON.parse(localSettings);
      } catch (e) {
        console.error('解析本地AI设置失败:', e);
      }
    }
    
    if (isDevelopment) {
      await delay();
      return {
        success: true,
        data: settings || {
          strategy_id: "trend_following_v2",
          max_positions: 5,
          risk_level: "medium",
          auto_trade: true,
          notifications: true
        }
      };
    }
    
    // 先尝试从本地存储返回，如果没有再请求服务器
    if (settings) {
      return {
        success: true,
        data: settings
      };
    }
    
    const response = await uni.request({
      url: `${API_BASE_URL}/settings`,
      method: 'GET'
    });
    
    return response.data;
  } catch (error) {
    console.error('获取Agent交易设置失败:', error);
    if (isDevelopment) {
      return {
        success: false,
        message: '获取Agent交易设置失败',
        data: {}
      };
    }
    throw error;
  }
}

/**
 * 更新Agent交易系统设置
 * @param {Object} settings 设置对象，包含以下属性:
 * @param {string} settings.strategy_id - 策略ID
 * @param {number} settings.max_positions - 最大持仓数量
 * @param {string} settings.risk_level - 风险等级 (low/medium/high)
 * @param {boolean} settings.auto_trade - 是否自动交易
 * @param {boolean} settings.notifications - 是否开启通知
 * @returns {Promise<Object>} 更新结果
 */
export async function updateSettings(settings) {
  try {
    // 将设置保存到本地存储
    uni.setStorageSync('ai_trading_settings', JSON.stringify(settings));
    
    if (isDevelopment) {
      await delay();
      
      // 如果启用了WebSocket，发送设置更新消息
      if (_aiTradingWebsocket) {
        try {
          _aiTradingWebsocket.send(JSON.stringify({
            type: 'settings_updated',
            data: settings
          }));
        } catch (e) {
          console.warn('发送WebSocket设置更新失败:', e);
        }
      }
      
      return {
        success: true,
        message: '设置已更新',
        data: settings
      };
    }
    
    const response = await uni.request({
      url: `${API_BASE_URL}/settings`,
      method: 'POST',
      data: settings
    });
    
    return response.data;
  } catch (error) {
    console.error('更新Agent交易设置失败:', error);
    if (isDevelopment) {
      return {
        success: false,
        message: '更新Agent交易设置失败',
        data: {}
      };
    }
    throw error;
  }
}

/**
 * 启动Agent交易系统
 * @param {String} sessionId 交易会话ID
 * @returns {Promise<Object>} 启动结果
 */
export async function startAITrading(sessionId) {
  try {
    if (isDevelopment) {
      await delay();
      return {
        success: true,
        message: 'Agent交易系统已启动',
        data: {
          status: 'running',
          session_id: sessionId || 'mock-session-123'
        }
      };
    }
    
    const response = await uni.request({
      url: `${API_BASE_URL}/start`,
      method: 'POST',
      data: { 
        session_id: sessionId 
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('启动Agent交易系统失败:', error);
    if (isDevelopment) {
      return {
        success: false,
        message: '启动Agent交易系统失败',
        data: {}
      };
    }
    throw error;
  }
}

/**
 * 停止Agent交易系统
 * @returns {Promise<Object>} 停止结果
 */
export async function stopAITrading() {
  try {
    if (isDevelopment) {
      await delay();
      return {
        success: true,
        message: 'Agent交易系统已停止',
        data: {
          status: 'stopped'
        }
      };
    }
    
    const response = await uni.request({
      url: `${API_BASE_URL}/stop`,
      method: 'POST'
    });
    
    return response.data;
  } catch (error) {
    console.error('停止Agent交易系统失败:', error);
    if (isDevelopment) {
      return {
        success: false,
        message: '停止Agent交易系统失败',
        data: {}
      };
    }
    throw error;
  }
}

/**
 * 获取Agent交易系统状态
 * @returns {Promise<Object>} 系统状态
 */
export async function getAITradingStatus() {
  try {
    if (isDevelopment) {
      await delay();
      return {
        success: true,
        data: {
          status: 'running',
          running_time: '02:34:15',
          trade_count: 8,
          active_strategies: ['趋势跟踪', '量价分析']
        }
      };
    }
    
    const response = await uni.request({
      url: `${API_BASE_URL}/status`,
      method: 'GET'
    });
    
    return response.data;
  } catch (error) {
    console.error('获取Agent交易系统状态失败:', error);
    if (isDevelopment) {
      return {
        success: false,
        message: '获取状态失败',
        data: {
          status: 'unknown'
        }
      };
    }
    throw error;
  }
}

/**
 * 获取系统状态
 * @returns {Promise<Object>} 系统状态
 */
export async function getSystemStatus() {
  try {
    // 🚨 禁用开发环境模拟数据 - 只允许真实数据
    let actualProfit = null;

    try {
      // 导入tradingService获取真实数据
      const tradingServiceModule = await import('./tradingService.js');
      const tradingService = tradingServiceModule.default;

      // 获取真实账户余额
      const accountResult = await tradingService.getDongwuXiucaiBalance();

      if (accountResult.success && accountResult.data) {
        // 基于真实数据计算系统状态
        actualProfit = accountResult.data.profit_loss || 0;
      }
    } catch (error) {
      console.error('获取真实账户数据失败:', error);
      // 在开发环境下允许继续，生产环境下抛出错误
      if (!isDevelopment) {
        throw new Error('❌ 系统状态需要真实数据，无法获取时拒绝返回模拟状态');
      }
    }

    // 如果是开发环境且无法获取真实数据，返回模拟数据
    if (isDevelopment) {
      return {
        success: true,
        data: {
          isRunning: true,
          isConnected: true,
          brokerName: '东吴证券',
          runningTime: '03:45:21',
          tradeCount: 12,
          // 如果获取到了实际盈亏数据，则使用，否则要求真实数据
          dailyProfit: actualProfit !== null ? actualProfit : Math.random() > 0.5 ? Math.random() * 1000 + 500 : -Math.random() * 500,
          currentStrategies: ['趋势跟踪', '量价分析'],
          t0Enabled: Math.random() > 0.5,
          tradeTimeMode: Math.random() > 0.5 ? 'EOD' : 'INTRADAY',
          lastEodUpdateTime: new Date().toLocaleTimeString(),
          t0StocksPool: [
            {
              symbol: 'SH600519',
              name: '贵州茅台',
              price: 1476.80,
              changePercent: 1.25,
              t0Signal: '尾盘异动',
              t0Reason: '尾盘成交量放大2倍，技术指标MACD金叉，次日有望高开冲高'
            },
            {
              symbol: 'SZ300750',
              name: '宁德时代',
              price: 143.25,
              changePercent: -2.34,
              t0Signal: '题材预期',
              t0Reason: '新能源政策利好，市场情绪回暖，高位回调构筑支撑，次日有补涨机会'
            },
            {
              symbol: 'SH601318',
              name: '中国平安',
              price: 47.32,
              changePercent: 0.85,
              t0Signal: '突破形态',
              t0Reason: '突破前期盘整区间上轨，成交量配合，形成短期突破形态，次日有望延续'
            },
            {
              symbol: 'SZ000858',
              name: '五粮液',
              price: 165.42,
              changePercent: -0.56,
              t0Signal: '反弹机会',
              t0Reason: '在重要支撑位止跌回升，尾盘资金净流入明显，次日可能迎来技术性反弹'
            },
            {
              symbol: 'SH600036',
              name: '招商银行',
              price: 39.86,
              changePercent: 0.32,
              t0Signal: '板块轮动',
              t0Reason: '金融板块轮动启动，该股尾盘资金流入增加，走势强于大盘，次日有望高开'
            },
            {
              symbol: 'SH601888',
              name: '中国中免',
              price: 142.17,
              changePercent: 1.89,
              t0Signal: '强势延续',
              t0Reason: '消费板块龙头走势强劲，尾盘拉升3%，量价配合，动能强劲有望延续至次日'
            }
          ]
        }
      };
    }

    // 正式环境
    const response = await uni.request({
      url: `${API_BASE_URL}/system/status`,
      method: 'GET'
    });
    
    // 尝试从东吴秀才账户获取实际盈亏数据
    if (response.data.success) {
      try {
        // 导入tradingService
        const tradingServiceModule = await import('./tradingService.js');
        const tradingService = tradingServiceModule.default;
        
        // 获取东吴秀才账户余额和持仓
        const dongwuAccountResult = await tradingService.getDongwuXiucaiBalance();
        const positionsResult = await tradingService.getPositions();
        
        if (dongwuAccountResult.success && dongwuAccountResult.data &&
            positionsResult.success && positionsResult.data) {
          
          // 计算持仓盈亏
          let positionProfit = 0;
          if (Array.isArray(positionsResult.data)) {
            positionProfit = positionsResult.data.reduce((sum, position) => 
              sum + (position.profit_loss || 0), 0);
          }
          
          // 更新盈亏数据
          response.data.data.dailyProfit = positionProfit;
        }
      } catch (error) {
        console.warn('获取东吴秀才账户盈亏数据失败:', error);
      }
    }

    return response.data;

  } catch (error) {
    console.error('获取系统状态失败:', error);
    if (isDevelopment) {
      return {
        success: false,
        message: '获取系统状态失败',
        data: {
          isRunning: false,
          isConnected: false,
          runningTime: '00:00:00',
          tradeCount: 0,
          dailyProfit: 0,
          currentStrategies: []
        }
      };
    }
    throw error;
  }
}

/**
 * 更新T+0配置
 * @param {Object} config T+0配置对象
 * @returns {Promise<Object>} 更新结果
 */
export async function updateT0Config(config) {
  try {
    // 保存到本地存储
    uni.setStorageSync('ai_trading_t0_config', config);
    
    return {
      success: true,
      message: 'T+0配置已更新',
      data: config
    };
  } catch (error) {
    console.error('更新T+0配置失败:', error);
    return {
      success: false,
      message: error.message || '更新配置失败'
    };
  }
}

/**
 * 执行交易决策
 * @param {Object} decision 交易决策对象
 * @param {Boolean} verify 是否验证
 * @returns {Promise<Object>} 执行结果
 */
export async function executeTradeDecision(decision, verify = true) {
  try {
    if (isDevelopment) {
      await delay(500); // 稍长延迟模拟交易执行
      return {
        success: true,
        message: '交易决策已执行',
        data: {
          order_id: 'mock-order-' + Date.now(),
          symbol: decision.symbol,
          action: decision.action,
          quantity: decision.quantity,
          price: decision.price,
          status: 'executed',
          timestamp: new Date().toISOString()
        }
      };
    }
    
    const response = await uni.request({
      url: `${API_BASE_URL}/execute-decision`,
      method: 'POST',
      data: {
        ...decision,
        verify
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('执行交易决策失败:', error);
    if (isDevelopment) {
      return {
        success: false,
        message: '执行交易决策失败',
        data: {}
      };
    }
    throw error;
  }
}

/**
 * 获取交易历史
 * @param {Number} limit 限制数量
 * @param {Number} offset 偏移量
 * @returns {Promise<Object>} 交易历史
 */
export async function getTradeHistory(limit = 20, offset = 0) {
  try {
    if (isDevelopment) {
      await delay();
      return {
        success: true,
        data: {
          total: 8,
          records: [
            {
              id: 'mock-trade-1',
              symbol: 'SH600519',
              name: '贵州茅台',
              action: 'BUY',
              quantity: 100,
              price: 1680.28,
              amount: 168028,
              status: 'completed',
              strategy: '趋势跟踪',
              timestamp: '2023-07-15T09:32:45'
            },
            {
              id: 'mock-trade-2',
              symbol: 'SZ300750',
              name: '宁德时代',
              action: 'SELL',
              quantity: 200,
              price: 242.36,
              amount: 48472,
              status: 'completed',
              strategy: '量价分析',
              timestamp: '2023-07-15T10:15:30'
            },
            {
              id: 'mock-trade-3',
              symbol: 'SH601318',
              name: '中国平安',
              action: 'BUY',
              quantity: 500,
              price: 46.35,
              amount: 23175,
              status: 'completed',
              strategy: '价值投资',
              timestamp: '2023-07-15T11:05:12'
            }
          ]
        }
      };
    }
    
    const response = await uni.request({
      url: `${API_BASE_URL}/history`,
      method: 'GET',
      data: {
        limit,
        offset
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('获取交易历史失败:', error);
    if (isDevelopment) {
      return {
        success: false,
        message: '获取交易历史失败',
        data: {
          total: 0,
          records: []
        }
      };
    }
    throw error;
  }
}

/**
 * 创建WebSocket连接以获取实时Agent交易更新
 * @param {Function} onMessage 消息处理函数
 * @param {Function} onError 错误处理函数
 * @param {Function} onClose 关闭处理函数
 * @returns {WebSocket} WebSocket实例
 */
export function createWebSocketConnection(onMessage, onError, onClose) {
  if (isDevelopment) {
    console.log('开发环境下，WebSocket连接模拟启用');
    // 模拟周期性消息
    const interval = setInterval(() => {
      if (typeof onMessage === 'function') {
        onMessage({
          data: JSON.stringify({
            type: 'status_update',
            data: {
              isRunning: true,
              tradeCount: Math.floor(Math.random() * 10) + 5,
              dailyProfit: (Math.random() * 2000 - 1000).toFixed(2)
            }
          })
        });
      }
    }, 5000);
    
    // 返回模拟的WebSocket对象
    const mockSocket = {
      send: (data) => console.log('模拟WebSocket发送:', data),
      close: () => {
        console.log('模拟WebSocket关闭');
        clearInterval(interval);
        if (typeof onClose === 'function') {
          onClose();
        }
        // 清除全局引用
        if (_aiTradingWebsocket === mockSocket) {
          _aiTradingWebsocket = null;
        }
      }
    };
    
    // 存储全局引用，以便在更新设置时通知
    _aiTradingWebsocket = mockSocket;
    
    return mockSocket;
  }
  
  let host = 'localhost';
  try {
    const sysInfo = uni.getSystemInfoSync();
    if (sysInfo && sysInfo.host) {
      host = sysInfo.host;
    }
  } catch (e) {
    console.warn('获取系统信息失败:', e);
  }
  
  const websocketUrl = `ws://${host}${API_BASE_URL}/ws`;
  
  try {
    const socket = new WebSocket(websocketUrl);
    
    socket.onmessage = onMessage;
    socket.onerror = onError;
    socket.onclose = (event) => {
      // 清除全局引用
      if (_aiTradingWebsocket === socket) {
        _aiTradingWebsocket = null;
      }
      
      if (typeof onClose === 'function') {
        onClose(event);
      }
    };
    
    // 存储全局引用，以便在更新设置时通知
    _aiTradingWebsocket = socket;
    
    return socket;
  } catch (error) {
    console.error('创建WebSocket连接失败:', error);
    throw error;
  }
}

/**
 * 获取学习进度
 * @returns {Promise<Object>} 学习进度信息
 */
export async function getLearningProgress() {
  try {
    if (isDevelopment) {
      await delay();
      return {
        success: true,
        data: {
          progress: 78,
          metrics: {
            samples: 24680,
            accuracy: 85.6,
            iterations: 42
          },
          models: [
            { 
              name: '趋势跟踪模型 v3.2', 
              date: '2023-06-15', 
              accuracy: 87.5, 
              performance: 15.2 
            },
            { 
              name: '形态识别模型 v2.8', 
              date: '2023-05-28', 
              accuracy: 82.1, 
              performance: 9.6 
            },
            { 
              name: '量价关系模型 v1.5', 
              date: '2023-04-10', 
              accuracy: 76.8, 
              performance: -2.3 
            }
          ]
        }
      };
    }
    
    const response = await uni.request({
      url: `${API_BASE_URL}/learning/progress`,
      method: 'GET'
    });
    
    return response.data;
  } catch (error) {
    console.error('获取学习进度失败:', error);
    if (isDevelopment) {
      return {
        success: false,
        message: '获取学习进度失败',
        data: {}
      };
    }
    throw error;
  }
}

/**
 * 检查市场数据状态
 * @returns {Promise<Object>} 市场数据状态
 */
export async function checkMarketDataStatus() {
  try {
    if (isDevelopment) {
      await delay();
      
      // 生成随机延迟数据
      const tdxDelay = Math.floor(Math.random() * 1000) + 50; // 50-1050ms
      const thsDelay = Math.floor(Math.random() * 800) + 100; // 100-900ms
      
      return {
        success: true,
        data: {
          lastUpdate: new Date().toISOString(),
          indices: [
            { name: '上证指数', code: '000001', price: 3458.23, change: 1.35 },
            { name: '深证成指', code: '399001', price: 14256.89, change: 1.62 },
            { name: '创业板指', code: '399006', price: 2876.45, change: -0.32 },
            { name: '沪深300', code: '000300', price: 4652.78, change: 1.18 }
          ],
          sectors: [
            { name: '食品饮料', change: 2.15, strength: 8 },
            { name: '银行', change: 0.87, strength: 6 },
            { name: '医药生物', change: -0.35, strength: 4 },
            { name: '新能源', change: -1.25, strength: 3 },
            { name: '电子科技', change: 1.48, strength: 7 }
          ],
          marketStatus: 'normal',
          tradeDate: new Date().toISOString().split('T')[0],
          // 添加数据源延迟信息
          dataSourceDelays: {
            tdx: tdxDelay,  // 通达信延迟
            ths: thsDelay   // 同花顺延迟
          },
          connected: true
        }
      };
    }
    
    const response = await uni.request({
      url: `/api/v1/market-data/status`,  // 修正为使用市场数据API的status端点
      method: 'GET'
    });
    
    return response.data;
  } catch (error) {
    console.error('检查市场追踪数据状态失败:', error);
    if (isDevelopment) {
      return {
        success: false,
        message: '获取市场数据失败',
        data: {}
      };
    }
    throw error;
  }
}

/**
 * 开始模型训练
 * @param {Object} options 训练选项
 * @returns {Promise<Object>} 训练结果
 */
export async function startModelTraining(options = {}) {
  try {
    if (isDevelopment) {
      await delay(800);
      return {
        success: true,
        message: '模型训练已启动',
        data: {
          trainingId: 'mock-training-' + Date.now(),
          estimatedTime: '25分钟'
        }
      };
    }
    
    const response = await uni.request({
      url: `${API_BASE_URL}/learning/start-training`,
      method: 'POST',
      data: options
    });
    
    return response.data;
  } catch (error) {
    console.error('启动模型训练失败:', error);
    if (isDevelopment) {
      return {
        success: false,
        message: '启动模型训练失败',
        data: {}
      };
    }
    throw error;
  }
}

/**
 * 获取T+0股票池
 * @returns {Promise<Object>} T+0股票池 - 适合当日尾盘买入次日早盘卖出的超短线交易标的
 */
export async function getT0StocksPool() {
  try {
    if (isDevelopment) {
      await delay();
      return {
        success: true,
        data: {
          stocks: [
            {
              symbol: 'SH600519',
              name: '贵州茅台',
              price: 1476.80,
              changePercent: 1.25,
              t0Signal: '尾盘异动',
              t0Reason: '尾盘成交量放大2倍，技术指标MACD金叉，次日有望高开冲高'
            },
            {
              symbol: 'SZ300750',
              name: '宁德时代',
              price: 143.25,
              changePercent: -2.34,
              t0Signal: '题材预期',
              t0Reason: '新能源政策利好，市场情绪回暖，高位回调构筑支撑，次日有补涨机会'
            },
            {
              symbol: 'SH601318',
              name: '中国平安',
              price: 47.32,
              changePercent: 0.85,
              t0Signal: '突破形态',
              t0Reason: '突破前期盘整区间上轨，成交量配合，形成短期突破形态，次日有望延续'
            },
            {
              symbol: 'SZ000858',
              name: '五粮液',
              price: 165.42,
              changePercent: -0.56,
              t0Signal: '反弹机会',
              t0Reason: '在重要支撑位止跌回升，尾盘资金净流入明显，次日可能迎来技术性反弹'
            },
            {
              symbol: 'SH600036',
              name: '招商银行',
              price: 39.86,
              changePercent: 0.32,
              t0Signal: '板块轮动',
              t0Reason: '金融板块轮动启动，该股尾盘资金流入增加，走势强于大盘，次日有望高开'
            },
            {
              symbol: 'SH601888',
              name: '中国中免',
              price: 142.17,
              changePercent: 1.89,
              t0Signal: '强势延续',
              t0Reason: '消费板块龙头走势强劲，尾盘拉升3%，量价配合，动能强劲有望延续至次日'
            }
          ],
          lastUpdated: new Date().toISOString(),
          marketStatus: 'normal'
        }
      };
    }
    
    const response = await uni.request({
      url: `${API_BASE_URL}/t0-stocks-pool`,
      method: 'GET'
    });
    
    return response.data;
  } catch (error) {
    console.error('获取T+0股票池失败:', error);
    if (isDevelopment) {
      return {
        success: false,
        message: '获取T+0股票池失败',
        data: { stocks: [] }
      };
    }
    throw error;
  }
}

/**
 * 执行快速交易
 * @param {Object} stock 股票信息
 * @param {String} action 交易动作
 * @returns {Promise<Object>} 交易结果
 */
export async function executeQuickTrade(stock, action) {
  try {
    if (isDevelopment) {
      await delay(700);
      // 确保必填参数
      if (!stock || !stock.symbol || !action) {
        throw new Error('股票信息或交易动作不完整');
      }
      
      // 根据交易方向设置价格
      let price = stock.price;
      if (action === 'BUY') {
        // 买入价略高于当前价
        price = (stock.price * 1.002).toFixed(2);
      } else {
        // 卖出价略低于当前价
        price = (stock.price * 0.998).toFixed(2);
      }
      
      const quantity = 100; // 默认数量
      
      return {
        success: true,
        message: `${action === 'BUY' ? '买入' : '卖出'}交易已执行`,
        data: {
          orderId: 'mock-quick-' + Date.now(),
          symbol: stock.symbol,
          name: stock.name,
          action: action,
          price: price,
          quantity: quantity,
          amount: (price * quantity).toFixed(2),
          status: 'completed',
          timestamp: new Date().toISOString()
        }
      };
    }
    
    const response = await uni.request({
      url: `${API_BASE_URL}/execute-quick-trade`,
      method: 'POST',
      data: {
        symbol: stock.symbol,
        action: action
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('执行快速交易失败:', error);
    if (isDevelopment) {
      return {
        success: false,
        message: error.message || '执行快速交易失败',
        data: {}
      };
    }
    throw error;
  }
}

/**
 * 获取Agent交易历史记录
 * @param {number} limit 返回的历史记录数量
 * @param {number} offset 分页偏移量
 * @returns {Promise<Object>} 包含Agent交易历史的响应对象
 */
export async function getAITradeHistory(limit = 20, offset = 0) {
  try {
    if (isDevelopment) {
      await delay();
      return {
        success: true,
        data: {
          trades: [
            {
              id: 'ai-trade-001',
              stockCode: '601318',
              stockName: '中国平安',
              action: 'buy',
              price: 45.30,
              quantity: 200,
              amount: 9060.00,
              tradeTime: '2023-07-03 10:15:32',
              strategy: 'trend_following_v2',
              tradeSource: 'ai',
              reason: '上涨趋势确认，MACD金叉，AI推荐买入'
            },
            {
              id: 'ai-trade-002',
              stockCode: '300750',
              stockName: '宁德时代',
              action: 'buy',
              price: 200.40,
              quantity: 50,
              amount: 10020.00,
              tradeTime: '2023-04-18 14:22:05',
              strategy: 'growth_selection_v1',
              tradeSource: 'ai',
              reason: 'ROE高，市值处于底部区域，AI判断具有长期增长潜力'
            },
            {
              id: 'ai-trade-003',
              stockCode: '600519',
              stockName: '贵州茅台',
              action: 'sell',
              price: 1820.50,
              quantity: 5,
              amount: 9102.50,
              tradeTime: '2023-06-20 09:45:18',
              strategy: 'profit_taking_v1',
              tradeSource: 'ai',
              reason: '获利目标达成，RSI超买，AI决定部分止盈'
            }
          ],
          total: 3,
          hasMore: false
        }
      };
    }
    
    const response = await uni.request({
      url: `${API_BASE_URL}/trade-history`,
      method: 'GET',
      data: {
        limit,
        offset
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('获取Agent交易历史失败:', error);
    if (isDevelopment) {
      return {
        success: false,
        message: '获取Agent交易历史失败',
        data: {
          trades: [],
          total: 0,
          hasMore: false
        }
      };
    }
    throw error;
  }
}

/**
 * 将Agent交易添加到本地持仓中
 * @param {Object} trade Agent交易对象
 * @returns {Promise<Object>} 结果对象
 */
export async function addAITradeToPortfolio(trade) {
  try {
    // 获取当前持仓
    let portfolio = uni.getStorageSync('portfolio');
    if (!portfolio) {
      portfolio = [];
    } else {
      try {
        portfolio = JSON.parse(portfolio);
      } catch (e) {
        console.error('解析持仓数据失败:', e);
        portfolio = [];
      }
    }
    
    // 检查是否已有该股票持仓
    const stockIndex = portfolio.findIndex(item => item.code === trade.stockCode);
    
    if (trade.action === 'buy') {
      if (stockIndex >= 0) {
        // 更新现有持仓
        const currentHolding = portfolio[stockIndex];
        const newQuantity = currentHolding.quantity + trade.quantity;
        const newCost = (currentHolding.costPrice * currentHolding.quantity + trade.price * trade.quantity) / newQuantity;
        
        portfolio[stockIndex] = {
          ...currentHolding,
          quantity: newQuantity,
          costPrice: newCost.toFixed(2),
          tradeSource: 'ai',
          buyDate: trade.tradeTime.split(' ')[0]
        };
      } else {
        // 添加新持仓
        portfolio.push({
          name: trade.stockName,
          code: trade.stockCode,
          currentPrice: trade.price.toFixed(2),
          priceChange: 0,
          quantity: trade.quantity,
          costPrice: trade.price.toFixed(2),
          marketValue: (trade.price * trade.quantity).toFixed(2),
          profit: 0,
          profitRate: 0,
          isRecommended: true,
          isWarning: false,
          buyDate: trade.tradeTime.split(' ')[0],
          tradeSource: 'ai'
        });
      }
    } else if (trade.action === 'sell' && stockIndex >= 0) {
      // 处理卖出
      const currentHolding = portfolio[stockIndex];
      const newQuantity = currentHolding.quantity - trade.quantity;
      
      if (newQuantity <= 0) {
        // 完全卖出，从持仓中移除
        portfolio.splice(stockIndex, 1);
      } else {
        // 部分卖出，更新持仓
        portfolio[stockIndex] = {
          ...currentHolding,
          quantity: newQuantity,
          marketValue: (currentHolding.currentPrice * newQuantity).toFixed(2),
          tradeSource: 'ai'
        };
      }
    }
    
    // 保存更新后的持仓
    uni.setStorageSync('portfolio', JSON.stringify(portfolio));
    
    return {
      success: true,
      message: 'Agent交易已更新到持仓',
      data: portfolio
    };
  } catch (error) {
    console.error('更新Agent交易到持仓失败:', error);
    return {
      success: false,
      message: '更新Agent交易到持仓失败',
      data: null
    };
  }
}

/**
 * 分析成交量模式，用于T+0交易辅助决策
 * @param {String} symbol 股票代码
 * @returns {Promise<Object>} 成交量分析结果
 */
export async function analyzeVolumePattern(symbol) {
  try {
    if (isDevelopment) {
      await delay();
      
      // 模拟数据
      const volumePatterns = [
        { name: '放量突破', description: '价格突破阻力位同时成交量显著放大', signal: 'bullish', strength: 9 },
        { name: '缩量回调', description: '价格回调但成交量萎缩，表明卖压减弱', signal: 'bullish', strength: 6 },
        { name: '量价背离', description: '价格创新高但成交量未配合，可能即将回调', signal: 'bearish', strength: 7 },
        { name: '尾盘放量', description: '尾盘阶段成交量显著放大，说明资金积极进场', signal: 'bullish', strength: 8 },
        { name: '巨量滞涨', description: '成交量异常放大但价格涨幅有限，说明存在较大抛压', signal: 'bearish', strength: 8 },
        { name: '量能衰竭', description: '连续放量后成交量开始萎缩，上涨动能减弱', signal: 'bearish', strength: 7 }
      ];
      
      // 为不同股票返回不同的分析结果
      let result;
      if (symbol.includes('600519')) { // 贵州茅台
        result = {
          pattern: volumePatterns[3], // 尾盘放量
          volumeRatio: 2.35, // 相比5日平均量比
          mainNetInflow: 1256.8, // 主力资金净流入(万元)
          volumeAnalysis: {
            largeOrders: 58, // 大单占比%
            volumeTrend: [125, 142, 156, 187, 235], // 最近5日量比变化趋势
            keyTimeSlots: [
              { time: '14:30-15:00', volume: 1.25e6, ratio: 28 }, // 尾盘成交量及占比
              { time: '13:00-14:30', volume: 1.87e6, ratio: 42 },
              { time: '11:30-13:00', volume: 0.35e6, ratio: 8 },
              { time: '10:00-11:30', volume: 0.65e6, ratio: 15 },
              { time: '9:30-10:00', volume: 0.31e6, ratio: 7 }
            ]
          }
        };
      } else if (symbol.includes('300750')) { // 宁德时代
        result = {
          pattern: volumePatterns[1], // 缩量回调
          volumeRatio: 0.78,
          mainNetInflow: -342.5,
          volumeAnalysis: {
            largeOrders: 48,
            volumeTrend: [110, 105, 95, 82, 78],
            keyTimeSlots: [
              { time: '14:30-15:00', volume: 0.75e6, ratio: 22 },
              { time: '13:00-14:30', volume: 0.95e6, ratio: 28 },
              { time: '11:30-13:00', volume: 0.45e6, ratio: 13 },
              { time: '10:00-11:30', volume: 0.85e6, ratio: 25 },
              { time: '9:30-10:00', volume: 0.40e6, ratio: 12 }
            ]
          }
        };
      } else if (symbol.includes('601318')) { // 中国平安
        result = {
          pattern: volumePatterns[0], // 放量突破
          volumeRatio: 1.85,
          mainNetInflow: 985.3,
          volumeAnalysis: {
            largeOrders: 62,
            volumeTrend: [95, 110, 125, 156, 185],
            keyTimeSlots: [
              { time: '14:30-15:00', volume: 1.15e6, ratio: 25 },
              { time: '13:00-14:30', volume: 1.45e6, ratio: 31 },
              { time: '11:30-13:00', volume: 0.55e6, ratio: 12 },
              { time: '10:00-11:30', volume: 0.95e6, ratio: 20 },
              { time: '9:30-10:00', volume: 0.56e6, ratio: 12 }
            ]
          }
        };
      } else {
        // 默认返回随机模式
        const randomPattern = volumePatterns[Math.floor(Math.random() * volumePatterns.length)];
        const volumeRatio = (Math.random() * 2 + 0.5).toFixed(2);
        const mainNetInflow = (Math.random() * 2000 - 1000).toFixed(1);
        
        result = {
          pattern: randomPattern,
          volumeRatio: parseFloat(volumeRatio),
          mainNetInflow: parseFloat(mainNetInflow),
          volumeAnalysis: {
            largeOrders: Math.floor(Math.random() * 30 + 40),
            volumeTrend: Array(5).fill(0).map(() => Math.floor(Math.random() * 100 + 50)),
            keyTimeSlots: [
              { time: '14:30-15:00', volume: Math.random() * 1e6, ratio: Math.floor(Math.random() * 20 + 15) },
              { time: '13:00-14:30', volume: Math.random() * 2e6, ratio: Math.floor(Math.random() * 20 + 25) },
              { time: '11:30-13:00', volume: Math.random() * 0.5e6, ratio: Math.floor(Math.random() * 10 + 5) },
              { time: '10:00-11:30', volume: Math.random() * 1.5e6, ratio: Math.floor(Math.random() * 15 + 15) },
              { time: '9:30-10:00', volume: Math.random() * 0.8e6, ratio: Math.floor(Math.random() * 10 + 10) }
            ]
          }
        };
      }
      
      return {
        success: true,
        data: result
      };
    }
    
    // 正式环境API调用
    const response = await uni.request({
      url: `${API_BASE_URL}/analyze/volume-pattern`,
      method: 'GET',
      data: {
        symbol: symbol
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('分析成交量模式失败:', error);
    if (isDevelopment) {
      return {
        success: false,
        message: '分析成交量模式失败',
        data: null
      };
    }
    throw error;
  }
}

/**
 * 获取增强版T+0股票池
 * @returns {Promise<Object>} 增强版T+0股票池，包含成交量分析结果
 */
export async function getEnhancedT0StocksPool() {
  try {
    // 先获取常规T+0股票池
    const poolResult = await getT0StocksPool();
    
    if (!poolResult.success || !poolResult.data || !poolResult.data.stocks) {
      return poolResult;
    }
    
    // 股票池
    const stocks = poolResult.data.stocks;
    
    // 为每只股票添加成交量分析
    const enhancedStocks = await Promise.all(stocks.map(async (stock) => {
      try {
        const volumeAnalysis = await analyzeVolumePattern(stock.symbol);
        return {
          ...stock,
          volumeAnalysis: volumeAnalysis.success ? volumeAnalysis.data : null
        };
      } catch (e) {
        console.error(`获取${stock.symbol}成交量分析失败:`, e);
        return stock;
      }
    }));
    
    // 更新最后一次扫描时间
    T0_POOL_UPDATE_CONFIG.lastUpdateTime = new Date();
    
    return {
      success: true,
      data: {
        ...poolResult.data,
        stocks: enhancedStocks,
        lastUpdateTime: T0_POOL_UPDATE_CONFIG.lastUpdateTime,
        updateMode: isInEodMode() ? 'EOD' : 'regular'
      }
    };
  } catch (error) {
    console.error('获取增强版T+0股票池失败:', error);
    return {
      success: false,
      message: '获取增强版T+0股票池失败',
      data: { stocks: [] }
    };
  }
}

/**
 * 启动T+0股票池自动更新
 * @param {Object} config 更新配置
 * @returns {Boolean} 是否成功启动更新
 */
export function startT0PoolAutoUpdate(config = {}) {
  // 停止可能存在的定时器
  stopT0PoolAutoUpdate();
  
  // 更新配置
  if (config.regularInterval) T0_POOL_UPDATE_CONFIG.regularInterval = config.regularInterval;
  if (config.eodScanInterval) T0_POOL_UPDATE_CONFIG.eodScanInterval = config.eodScanInterval;
  if (config.eodModeStartTime) T0_POOL_UPDATE_CONFIG.eodModeStartTime = config.eodModeStartTime;
  
  T0_POOL_UPDATE_CONFIG.autoUpdateEnabled = true;
  
  // 立即执行一次更新
  updateT0StocksPool();
  
  // 设置定时器，根据当前时间决定更新间隔
  scheduleNextUpdate();
  
  return true;
}

/**
 * 停止T+0股票池自动更新
 */
export function stopT0PoolAutoUpdate() {
  if (T0_POOL_UPDATE_CONFIG.updateTimer) {
    clearTimeout(T0_POOL_UPDATE_CONFIG.updateTimer);
    T0_POOL_UPDATE_CONFIG.updateTimer = null;
  }
  T0_POOL_UPDATE_CONFIG.autoUpdateEnabled = false;
}

/**
 * 调度下一次更新
 */
function scheduleNextUpdate() {
  if (!T0_POOL_UPDATE_CONFIG.autoUpdateEnabled) return;
  
  // 清除可能存在的定时器
  if (T0_POOL_UPDATE_CONFIG.updateTimer) {
    clearTimeout(T0_POOL_UPDATE_CONFIG.updateTimer);
  }
  
  // 确定更新间隔
  const updateInterval = isInEodMode() ? 
    T0_POOL_UPDATE_CONFIG.eodScanInterval : 
    T0_POOL_UPDATE_CONFIG.regularInterval;
  
  // 设置下一次更新定时器
  T0_POOL_UPDATE_CONFIG.updateTimer = setTimeout(() => {
    updateT0StocksPool();
    scheduleNextUpdate(); // 递归调度下一次更新
  }, updateInterval * 60 * 1000); // 转换为毫秒
}

/**
 * 检查是否在尾盘模式
 * @returns {Boolean} 是否处于尾盘模式
 */
function isInEodMode() {
  const now = new Date();
  const currentTime = now.toTimeString().substring(0, 8);
  return currentTime >= T0_POOL_UPDATE_CONFIG.eodModeStartTime && 
         currentTime <= T0_POOL_UPDATE_CONFIG.marketCloseTime;
}

/**
 * 检查是否在交易时间内
 * @returns {Boolean} 是否在交易时间内
 */
function isWithinTradingHours() {
  const now = new Date();
  const currentTime = now.toTimeString().substring(0, 8);
  return currentTime >= T0_POOL_UPDATE_CONFIG.marketOpenTime && 
         currentTime <= T0_POOL_UPDATE_CONFIG.marketCloseTime;
}

/**
 * 更新T+0股票池
 * @returns {Promise<Object>} 更新结果
 */
export async function updateT0StocksPool() {
  try {
    // 检查是否在交易时间内
    const config = getT0PoolUpdateConfig();
    if (!config.isWithinTradingHours) {
      console.log('非交易时间，跳过T+0股票池更新');
      return {
        success: false,
        message: '非交易时间',
        data: null
      };
    }
    
    // 在开发环境中，模拟API调用
    if (isDevelopment) {
      await delay(800); // 模拟网络延迟
      
      // 创建更新事件
      const isEod = isInEodMode();
      const result = await getEnhancedT0StocksPool();
      
      // 手动触发更新事件
      const event = new CustomEvent('t0pool-updated', { 
        detail: {
          result: result,
          isEodMode: isEod,
          updateTime: new Date()
        }
      });
      window.dispatchEvent(event);
      
      return result;
    }
    
    // 实际环境的API调用
    const response = await uni.request({
      url: `${API_BASE_URL}/update-t0-pool`,
      method: 'POST'
    });
    
    return response.data;
  } catch (error) {
    console.error('更新T+0股票池失败:', error);
    return {
      success: false,
      message: '更新失败: ' + error.message,
      data: null
    };
  }
}

/**
 * 获取T+0股票池更新配置
 * @returns {Object} 当前更新配置
 */
export function getT0PoolUpdateConfig() {
  return {
    ...T0_POOL_UPDATE_CONFIG,
    isAutoUpdateEnabled: T0_POOL_UPDATE_CONFIG.autoUpdateEnabled,
    isInEodMode: isInEodMode(),
    isWithinTradingHours: isWithinTradingHours()
  };
}

/**
 * 配置T+0股票池更新参数
 * @param {Object} config 配置对象
 * @returns {Object} 更新后的配置
 */
export function configureT0PoolUpdate(config) {
  const previousConfig = {...T0_POOL_UPDATE_CONFIG};
  
  // 更新配置
  if (config.regularInterval !== undefined) T0_POOL_UPDATE_CONFIG.regularInterval = config.regularInterval;
  if (config.eodScanInterval !== undefined) T0_POOL_UPDATE_CONFIG.eodScanInterval = config.eodScanInterval;
  if (config.eodModeStartTime !== undefined) T0_POOL_UPDATE_CONFIG.eodModeStartTime = config.eodModeStartTime;
  if (config.autoUpdateEnabled !== undefined) {
    const wasEnabled = T0_POOL_UPDATE_CONFIG.autoUpdateEnabled;
    T0_POOL_UPDATE_CONFIG.autoUpdateEnabled = config.autoUpdateEnabled;
    
    // 如果从禁用转为启用，启动自动更新
    if (!wasEnabled && config.autoUpdateEnabled) {
      startT0PoolAutoUpdate();
    }
    // 如果从启用转为禁用，停止自动更新
    else if (wasEnabled && !config.autoUpdateEnabled) {
      stopT0PoolAutoUpdate();
    }
  }
  
  return getT0PoolUpdateConfig();
}

/**
 * 获取AI综合决策
 * 通过统一AI决策模型获取所有因素整合后的交易决策
 * @param {Object} stockInfo - 股票信息
 * @param {Array} historicalData - 历史数据（可选）
 * @returns {Promise} - 返回AI决策结果
 */
async function getUnifiedAIDecision(stockInfo, historicalData = null) {
  try {
    const response = await uni.request({
      url: env.apiBaseUrl + '/api/t-trading/ai-trade-decision',
      method: 'POST',
      data: {
        stock_info: {
          code: stockInfo.code,
          name: stockInfo.name, 
          current_price: stockInfo.currentPrice,
          open_price: stockInfo.open,
          intraday_high: stockInfo.high,
          intraday_low: stockInfo.low,
          avg_volume: stockInfo.avgVolume || stockInfo.volume * 0.8,
          current_volume: stockInfo.volume,
          base_position: stockInfo.basePosition,
          base_cost: stockInfo.baseCost
        },
        historical_data: historicalData
      }
    });

    if (response.statusCode === 200) {
      return response.data;
    } else {
      console.error('获取AI综合决策失败:', response.statusCode, response.data);
      return {
        success: false,
        message: '获取决策失败: ' + (response.data.message || '未知错误'),
        data: null
      };
    }
  } catch (error) {
    console.error('获取AI决策异常:', error);
    return {
      success: false,
      message: '获取决策异常: ' + error.message,
      data: null
    };
  }
}

/**
 * 设置交易环境（回测或实盘）
 * @param {String} environment 交易环境，可选值："backtest"或"live"
 * @returns {Promise<Object>} 设置结果
 */
export async function setTradingEnvironment(environment) {
  try {
    if (isDevelopment) {
      await delay();
      return {
        success: true,
        message: `交易环境已切换为: ${environment}`,
        environment: environment
      };
    }
    
    const response = await uni.request({
      url: `${T_TRADING_API_URL}/set-environment`,
      method: 'POST',
      data: { environment }
    });
    
    return response.data;
  } catch (error) {
    console.error('设置交易环境失败:', error);
    return {
      success: false,
      message: '设置交易环境失败: ' + error.message,
      data: {}
    };
  }
}

/**
 * 获取当前交易环境
 * @returns {Promise<Object>} 当前环境信息
 */
export async function getCurrentEnvironment() {
  try {
    if (isDevelopment) {
      await delay();
      return {
        success: true,
        environment: Math.random() > 0.5 ? "live" : "backtest",
        parameters: {
          max_trade_amount: 10000,
          risk_level: "medium"
        }
      };
    }
    
    const response = await uni.request({
      url: `${T_TRADING_API_URL}/current-environment`,
      method: 'GET'
    });
    
    return response.data;
  } catch (error) {
    console.error('获取当前环境失败:', error);
    return {
      success: false,
      message: '获取当前环境失败: ' + error.message,
      data: {}
    };
  }
}

/**
 * 加载回测数据
 * @param {String} stockCode 股票代码
 * @returns {Promise<Object>} 加载结果
 */
export async function loadBacktestData(stockCode) {
  try {
    if (isDevelopment) {
      await delay();
      return {
        success: true,
        message: `成功加载 ${stockCode} 的回测数据`,
        data_points: 252
      };
    }
    
    const response = await uni.request({
      url: `${T_TRADING_API_URL}/load-backtest-data`,
      method: 'POST',
      data: { stock_code: stockCode }
    });
    
    return response.data;
  } catch (error) {
    console.error('加载回测数据失败:', error);
    return {
      success: false,
      message: '加载回测数据失败: ' + error.message,
      data: {}
    };
  }
}

/**
 * 运行回测
 * @param {Object} config 回测配置
 * @param {String} config.start_date 开始日期
 * @param {String} config.end_date 结束日期
 * @param {Number} config.initial_capital 初始资金
 * @param {String} config.stock_code 股票代码
 * @param {Object} config.strategy_params 策略参数
 * @returns {Promise<Object>} 回测结果
 */
export async function runBacktest(config) {
  try {
    if (isDevelopment) {
      await delay(800); // 回测需要更长时间
      return {
        success: true,
        message: "回测完成",
        result: {
          trades: Array(10).fill(0).map((_, i) => ({
            date: `2023-${String(i % 12 + 1).padStart(2, '0')}-${String(i % 28 + 1).padStart(2, '0')}`,
            stock_code: config.stock_code,
            action: i % 2 === 0 ? 'buy' : 'sell',
            price: 100 + Math.random() * 20,
            quantity: 100 * (i % 5 + 1),
            profit: i % 2 === 1 ? Math.random() * 1000 - 500 : 0
          })),
          metrics: {
            total_return: Math.random() * 0.3 - 0.1,
            annual_return: Math.random() * 0.25 - 0.05,
            max_drawdown: Math.random() * 0.15,
            sharpe_ratio: Math.random() * 2,
            win_rate: Math.random() * 0.4 + 0.4
          }
        }
      };
    }
    
    const response = await uni.request({
      url: `${T_TRADING_API_URL}/run-backtest`,
      method: 'POST',
      data: config
    });
    
    return response.data;
  } catch (error) {
    console.error('运行回测失败:', error);
    return {
      success: false,
      message: '运行回测失败: ' + error.message,
      data: {}
    };
  }
}

/**
 * 获取回测结果
 * @param {String} format 结果格式，可选值："json"或"csv"
 * @returns {Promise<Object>} 回测结果
 */
export async function getBacktestResults(format = "json") {
  try {
    if (isDevelopment) {
      await delay();
      return {
        success: true,
        message: "成功获取回测结果",
        data: {
          trades: Array(10).fill(0).map((_, i) => ({
            date: `2023-${String(i % 12 + 1).padStart(2, '0')}-${String(i % 28 + 1).padStart(2, '0')}`,
            stock_code: "SH600000",
            action: i % 2 === 0 ? 'buy' : 'sell',
            price: 100 + Math.random() * 20,
            quantity: 100 * (i % 5 + 1),
            profit: i % 2 === 1 ? Math.random() * 1000 - 500 : 0
          })),
          performance: {
            total_return: Math.random() * 0.3 - 0.1,
            win_rate: Math.random() * 0.4 + 0.4,
            max_drawdown: Math.random() * 0.15,
            sharpe_ratio: Math.random() * 2
          }
        }
      };
    }
    
    const response = await uni.request({
      url: `${T_TRADING_API_URL}/backtest-results?format=${format}`,
      method: 'GET'
    });
    
    return response.data;
  } catch (error) {
    console.error('获取回测结果失败:', error);
    return {
      success: false,
      message: '获取回测结果失败: ' + error.message,
      data: {}
    };
  }
}

/**
 * 配置实盘风险控制参数
 * @param {Object} config 风险控制配置
 * @param {String} config.risk_level 风险级别，可选值："low", "medium", "high"
 * @param {Number} config.max_position_per_stock 单只股票最大仓位比例
 * @param {Number} config.daily_loss_limit 日亏损限制比例
 * @param {String} config.position_sizing_method 仓位确定方法，可选值："fixed", "confidence", "kelly"
 * @returns {Promise<Object>} 配置结果
 */
export async function configureRiskControl(config) {
  try {
    if (isDevelopment) {
      await delay();
      return {
        success: true,
        message: "风险控制参数已更新",
        settings: config
      };
    }
    
    const response = await uni.request({
      url: `${T_TRADING_API_URL}/configure-risk-control`,
      method: 'POST',
      data: config
    });
    
    return response.data;
  } catch (error) {
    console.error('配置风险控制失败:', error);
    return {
      success: false,
      message: '配置风险控制失败: ' + error.message,
      data: {}
    };
  }
}

/**
 * 获取Agent性能统计
 * @param {String} timeRange 时间范围 ('1d', '1w', '1m', '3m', '1y')
 * @returns {Promise<Object>} 性能统计结果
 */
export async function getPerformanceStats(timeRange = '1d') {
  try {
    if (isDevelopment) {
      await delay();
      return {
        success: true,
        data: {
          decisionAccuracy: 85.6 + Math.random() * 10,
          executionSuccess: 98.2 + Math.random() * 1.5,
          avgResponseTime: 200 + Math.random() * 100,
          systemStability: 99.1 + Math.random() * 0.8,
          profitableTradeRatio: 67.8 + Math.random() * 15,
          avgHoldingTime: 4.2 + Math.random() * 2
        }
      };
    }

    const response = await uni.request({
      url: `${API_BASE_URL}/performance`,
      method: 'GET',
      data: { range: timeRange }
    });

    return response.data;
  } catch (error) {
    console.error('获取性能统计失败:', error);
    throw error;
  }
}

/**
 * 请求AI决策
 * @param {Object} context 决策上下文
 * @returns {Promise<Object>} 决策结果
 */
export async function requestDecision(context = {}) {
  try {
    if (isDevelopment) {
      await delay();
      return {
        success: true,
        data: {
          decisionId: 'decision_' + Date.now(),
          action: Math.random() > 0.5 ? 'BUY' : 'SELL',
          confidence: 0.7 + Math.random() * 0.3,
          reasoning: '基于技术分析和市场情绪的综合判断'
        }
      };
    }

    const response = await uni.request({
      url: `${API_BASE_URL}/decision`,
      method: 'POST',
      data: { context }
    });

    return response.data;
  } catch (error) {
    console.error('请求AI决策失败:', error);
    throw error;
  }
}

/**
 * 提供决策反馈
 * @param {String} decisionId 决策ID
 * @param {Object} feedback 反馈信息
 * @returns {Promise<Object>} 反馈结果
 */
export async function provideFeedback(decisionId, feedback) {
  try {
    if (isDevelopment) {
      await delay();
      return {
        success: true,
        message: '反馈已收到，将用于改进AI决策'
      };
    }

    const response = await uni.request({
      url: `${API_BASE_URL}/feedback`,
      method: 'POST',
      data: {
        decision_id: decisionId,
        feedback: feedback
      }
    });

    return response.data;
  } catch (error) {
    console.error('提供反馈失败:', error);
    throw error;
  }
}

// 默认导出
export default {
  getSettings,
  updateSettings,
  startAITrading,
  stopAITrading,
  getAITradingStatus,
  getSystemStatus,
  executeTradeDecision,
  getTradeHistory,
  createWebSocketConnection,
  getLearningProgress,
  checkMarketDataStatus,
  startModelTraining,
  updateT0Config,
  getT0StocksPool,
  executeQuickTrade,
  getAITradeHistory,
  addAITradeToPortfolio,
  analyzeVolumePattern,
  getEnhancedT0StocksPool,
  getUnifiedAIDecision,
  setTradingEnvironment,
  getCurrentEnvironment,
  loadBacktestData,
  runBacktest,
  getBacktestResults,
  configureRiskControl,
  getT0PoolUpdateConfig,
  configureT0PoolUpdate,
  startT0PoolAutoUpdate,
  stopT0PoolAutoUpdate,
  updateT0StocksPool,
  getPerformanceStats,
  requestDecision,
  provideFeedback
};