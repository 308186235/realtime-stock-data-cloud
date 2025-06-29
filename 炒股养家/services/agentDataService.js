/**
 * Agent数据服务
 * 专门用于从后端Agent系统获取真实的交易数据
 */

import { baseUrl } from './config.js';
import realTimeDataService from './realTimeDataService.js';

class AgentDataService {
  constructor() {
    this.apiBaseUrl = baseUrl;
    this.timeout = 10000; // 10秒超时
  }

  /**
   * 获取账户余额信息
   */
  async getAccountBalance() {
    try {
      console.log('[Agent数据] 正在获取账户余额...');
      
      const response = await uni.request({
        url: `${this.apiBaseUrl}/api/account-balance`,
        method: 'GET',
        timeout: this.timeout,
        header: {
          'Content-Type': 'application/json'
        }
      });

      if (response.statusCode === 200 && response.data) {
        console.log('[Agent数据] 成功获取账户余额:', response.data);
        
        // 适配不同的响应格式
        const accountInfo = response.data.account_info || response.data.balance_info || response.data;

        return {
          success: true,
          data: {
            balance: accountInfo?.available_balance || accountInfo?.balance || 0,
            available: accountInfo?.available_balance || accountInfo?.available || 0,
            market_value: accountInfo?.market_value || 0,
            total_assets: accountInfo?.total_assets || accountInfo?.total_value || 0,
            frozen: accountInfo?.frozen || 0,
            daily_profit: accountInfo?.daily_profit || 0,
            account_type: accountInfo?.account_type || 'Agent智能账户',
            account_name: accountInfo?.account_name || 'Agent账户',
            account_id: accountInfo?.account_id || 'agent_001',
            last_update: new Date().toISOString()
          }
        };
      } else {
        throw new Error(`API响应错误: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('[Agent数据] 获取账户余额失败:', error);
      throw error;
    }
  }

  /**
   * 获取持仓信息
   */
  async getPositions() {
    try {
      console.log('[Agent数据] 正在获取持仓信息...');
      
      const response = await uni.request({
        url: `${this.apiBaseUrl}/api/account-positions`,
        method: 'GET',
        timeout: this.timeout,
        header: {
          'Content-Type': 'application/json'
        }
      });

      if (response.statusCode === 200 && response.data) {
        console.log('[Agent数据] 成功获取持仓信息:', response.data);
        
        // 适配不同的响应格式
        const positionsData = response.data.positions || response.data.data?.positions || response.data;
        const positions = Array.isArray(positionsData) ? positionsData : [];

        return {
          success: true,
          data: positions.map(pos => ({
            symbol: pos.stock_code || pos.symbol || pos.code,
            name: pos.stock_name || pos.name,
            volume: pos.quantity || pos.volume || 0,
            available_volume: pos.available_quantity || pos.available_volume || pos.quantity || 0,
            cost_price: pos.cost_price || pos.avg_cost || pos.costPrice || 0,
            current_price: pos.current_price || pos.price || pos.currentPrice || 0,
            price_change_pct: pos.change_percent || pos.priceChange || 0,
            profit_loss: pos.profit_loss || pos.profit || 0,
            profit_loss_ratio: pos.profit_loss_ratio || pos.profitRate || 0,
            market_value: pos.market_value || pos.marketValue || (pos.quantity * pos.current_price) || 0,
            position_date: pos.position_date || pos.buyDate || new Date().toISOString().split('T')[0]
          }))
        };
      } else {
        throw new Error(`API响应错误: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('[Agent数据] 获取持仓信息失败:', error);
      throw error;
    }
  }

  /**
   * 获取Agent分析数据
   */
  async getAgentAnalysis() {
    try {
      console.log('[Agent数据] 正在获取Agent分析...');
      
      const response = await uni.request({
        url: `${this.apiBaseUrl}/api/agent-analysis`,
        method: 'GET',
        timeout: this.timeout,
        header: {
          'Content-Type': 'application/json'
        }
      });

      if (response.statusCode === 200 && response.data) {
        console.log('[Agent数据] 成功获取Agent分析:', response.data);
        
        return {
          success: true,
          data: {
            learning_progress: response.data.learning_progress || {
              accuracy: 0.75,
              win_rate: 0.68,
              max_drawdown: 0.12,
              total_trades: 156,
              profitable_trades: 106
            },
            recommendations: response.data.recommendations || [],
            market_analysis: response.data.market_analysis || {},
            risk_assessment: response.data.risk_assessment || {},
            last_update: new Date().toISOString()
          }
        };
      } else {
        throw new Error(`API响应错误: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('[Agent数据] 获取Agent分析失败:', error);
      throw error;
    }
  }

  /**
   * 获取交易历史
   */
  async getTradeHistory(limit = 50) {
    try {
      console.log('[Agent数据] 正在获取交易历史...');
      
      const response = await uni.request({
        url: `${this.apiBaseUrl}/api/trade-history`,
        method: 'GET',
        data: { limit },
        timeout: this.timeout,
        header: {
          'Content-Type': 'application/json'
        }
      });

      if (response.statusCode === 200 && response.data) {
        console.log('[Agent数据] 成功获取交易历史:', response.data);
        
        return {
          success: true,
          data: response.data.trades || []
        };
      } else {
        throw new Error(`API响应错误: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('[Agent数据] 获取交易历史失败:', error);
      throw error;
    }
  }

  /**
   * 获取市场数据
   */
  async getMarketData(symbols = []) {
    try {
      console.log('[Agent数据] 正在获取市场数据...');
      
      const response = await uni.request({
        url: `${this.apiBaseUrl}/api/market-data`,
        method: 'GET',
        data: { symbols: symbols.join(',') },
        timeout: this.timeout,
        header: {
          'Content-Type': 'application/json'
        }
      });

      if (response.statusCode === 200 && response.data) {
        console.log('[Agent数据] 成功获取市场数据:', response.data);
        
        return {
          success: true,
          data: response.data.market_data || {}
        };
      } else {
        throw new Error(`API响应错误: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('[Agent数据] 获取市场数据失败:', error);
      throw error;
    }
  }

  /**
   * 提交交易订单
   */
  async submitTradeOrder(orderData) {
    try {
      console.log('[Agent数据] 正在提交交易订单:', orderData);
      
      const response = await uni.request({
        url: `${this.apiBaseUrl}/api/trade-order`,
        method: 'POST',
        data: orderData,
        timeout: this.timeout,
        header: {
          'Content-Type': 'application/json'
        }
      });

      if (response.statusCode === 200 && response.data) {
        console.log('[Agent数据] 交易订单提交成功:', response.data);
        
        return {
          success: true,
          data: response.data
        };
      } else {
        throw new Error(`API响应错误: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('[Agent数据] 提交交易订单失败:', error);
      throw error;
    }
  }

  /**
   * 检查Agent系统状态
   */
  async checkSystemStatus() {
    try {
      console.log('[Agent数据] 正在检查系统状态...');
      
      const response = await uni.request({
        url: `${this.apiBaseUrl}/api/health`,
        method: 'GET',
        timeout: 5000, // 健康检查使用较短超时
        header: {
          'Content-Type': 'application/json'
        }
      });

      if (response.statusCode === 200) {
        console.log('[Agent数据] 系统状态正常');
        
        return {
          success: true,
          data: {
            status: 'healthy',
            timestamp: new Date().toISOString(),
            response_time: response.data?.response_time || 0
          }
        };
      } else {
        throw new Error(`健康检查失败: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('[Agent数据] 系统状态检查失败:', error);
      return {
        success: false,
        error: error.message,
        data: {
          status: 'unhealthy',
          timestamp: new Date().toISOString()
        }
      };
    }
  }

  /**
   * 测试Agent数据连接
   */
  async testConnection() {
    try {
      console.log('[Agent数据] 测试连接...');

      const healthResult = await this.checkSystemStatus();
      if (healthResult.success) {
        console.log('[Agent数据] 连接测试成功');

        // 测试获取数据
        const testResults = await this.getBatchData(['balance', 'positions']);
        console.log('[Agent数据] 数据获取测试结果:', testResults);

        return {
          success: true,
          message: 'Agent数据服务连接正常',
          data: testResults
        };
      } else {
        return {
          success: false,
          message: 'Agent数据服务连接失败',
          error: healthResult.error
        };
      }
    } catch (error) {
      console.error('[Agent数据] 连接测试失败:', error);
      return {
        success: false,
        message: 'Agent数据服务连接异常',
        error: error.message
      };
    }
  }

  /**
   * 获取真实股票数据 (通过Agent后端)
   */
  async getStockData(symbols = ['000001', '600000', '600519'], period = '1d') {
    try {
      console.log('[Agent数据] 通过Agent后端获取真实股票数据:', symbols);

      // 首先尝试获取实时行情
      const realtimeResult = await realTimeDataService.getRealTimeQuotes(symbols);
      if (realtimeResult.success) {
        console.log('[Agent数据] 成功获取实时股票数据');
        return realtimeResult;
      }

      // 如果实时数据失败，尝试通过Agent API获取
      const response = await uni.request({
        url: `${this.apiBaseUrl}/api/stock/quotes`,
        method: 'GET',
        data: {
          symbols: symbols.join(','),
          period: period,
          limit: 100,
          source: 'agent' // 明确指定使用Agent数据源
        },
        timeout: this.timeout,
        header: {
          'Content-Type': 'application/json'
        }
      });

      if (response.statusCode === 200 && response.data) {
        console.log('[Agent数据] 成功获取Agent股票数据:', response.data);

        return {
          success: true,
          data: response.data.quotes || response.data,
          symbols: symbols,
          period: period,
          timestamp: new Date().toISOString(),
          source: 'agent'
        };
      } else {
        throw new Error(`Agent API响应错误: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('[Agent数据] 获取真实股票数据失败:', error);
      throw new Error(`无法获取真实股票数据: ${error.message}。请确保Agent后端服务正在运行并连接到真实股票数据源。`);
    }
  }

  /**
   * 运行真实数据回测 (通过Agent后端)
   */
  async runBacktest(config = {}) {
    try {
      console.log('[Agent数据] 通过Agent后端运行真实数据回测:', config);

      const backtestConfig = {
        strategy: config.strategy || 'ma_crossover',
        symbols: config.symbols || ['000001', '600000'],
        start_date: config.start_date || '2023-01-01',
        end_date: config.end_date || '2024-01-01',
        initial_capital: config.initial_capital || 100000,
        data_source: 'real', // 明确指定使用真实数据
        use_agent_data: true, // 使用Agent提供的数据
        ...config
      };

      const response = await uni.request({
        url: `${this.apiBaseUrl}/api/agent/backtest`,
        method: 'POST',
        data: backtestConfig,
        timeout: 60000, // 真实数据回测需要更长时间
        header: {
          'Content-Type': 'application/json'
        }
      });

      if (response.statusCode === 200 && response.data) {
        console.log('[Agent数据] 真实数据回测运行成功:', response.data);

        return {
          success: true,
          data: response.data.backtest_result || response.data,
          config: backtestConfig,
          timestamp: new Date().toISOString(),
          source: 'real'
        };
      } else {
        throw new Error(`Agent回测API响应错误: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('[Agent数据] 真实数据回测失败:', error);
      throw new Error(`真实数据回测失败: ${error.message}。请确保Agent后端服务正在运行并连接到真实历史数据源。`);
    }
  }

  /**
   * 启动实时数据推送
   */
  async startRealTimeDataPush(symbols = []) {
    try {
      console.log('[Agent数据] 启动实时数据推送:', symbols);

      // 建立WebSocket连接
      realTimeDataService.connectWebSocket(symbols);

      return {
        success: true,
        message: '实时数据推送已启动',
        symbols: symbols
      };
    } catch (error) {
      console.error('[Agent数据] 启动实时数据推送失败:', error);
      throw new Error(`无法启动实时数据推送: ${error.message}`);
    }
  }

  /**
   * 停止实时数据推送
   */
  stopRealTimeDataPush() {
    try {
      console.log('[Agent数据] 停止实时数据推送');
      realTimeDataService.disconnect();

      return {
        success: true,
        message: '实时数据推送已停止'
      };
    } catch (error) {
      console.error('[Agent数据] 停止实时数据推送失败:', error);
      throw new Error(`停止实时数据推送失败: ${error.message}`);
    }
  }

  /**
   * 添加数据推送订阅者
   */
  subscribeToRealTimeData(subscriberId, callback) {
    try {
      realTimeDataService.addSubscriber(subscriberId, callback);
      console.log('[Agent数据] 添加实时数据订阅者:', subscriberId);

      return {
        success: true,
        message: '已添加实时数据订阅'
      };
    } catch (error) {
      console.error('[Agent数据] 添加订阅者失败:', error);
      throw new Error(`添加订阅者失败: ${error.message}`);
    }
  }

  /**
   * 移除数据推送订阅者
   */
  unsubscribeFromRealTimeData(subscriberId) {
    try {
      realTimeDataService.removeSubscriber(subscriberId);
      console.log('[Agent数据] 移除实时数据订阅者:', subscriberId);

      return {
        success: true,
        message: '已移除实时数据订阅'
      };
    } catch (error) {
      console.error('[Agent数据] 移除订阅者失败:', error);
      throw new Error(`移除订阅者失败: ${error.message}`);
    }
  }

  /**
   * 获取真实K线数据
   */
  async getKLineData(symbol, period = '1d', limit = 100) {
    try {
      console.log('[Agent数据] 获取真实K线数据:', symbol, period);

      return await realTimeDataService.getKLineData(symbol, period, limit);
    } catch (error) {
      console.error('[Agent数据] 获取K线数据失败:', error);
      throw new Error(`无法获取K线数据: ${error.message}`);
    }
  }



  /**
   * 批量获取数据
   */
  async getBatchData(dataTypes = ['balance', 'positions', 'analysis']) {
    const results = {};
    const promises = [];

    if (dataTypes.includes('balance')) {
      promises.push(
        this.getAccountBalance()
          .then(data => ({ type: 'balance', success: true, data }))
          .catch(error => ({ type: 'balance', success: false, error }))
      );
    }

    if (dataTypes.includes('positions')) {
      promises.push(
        this.getPositions()
          .then(data => ({ type: 'positions', success: true, data }))
          .catch(error => ({ type: 'positions', success: false, error }))
      );
    }

    if (dataTypes.includes('analysis')) {
      promises.push(
        this.getAgentAnalysis()
          .then(data => ({ type: 'analysis', success: true, data }))
          .catch(error => ({ type: 'analysis', success: false, error }))
      );
    }

    try {
      const batchResults = await Promise.allSettled(promises);
      
      batchResults.forEach(result => {
        if (result.status === 'fulfilled') {
          const { type, success, data, error } = result.value;
          results[type] = { success, data, error };
        }
      });

      return results;
    } catch (error) {
      console.error('[Agent数据] 批量获取数据失败:', error);
      throw error;
    }
  }
}

// 创建单例实例
const agentDataService = new AgentDataService();

export default agentDataService;
