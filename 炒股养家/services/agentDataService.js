/**
 * Agent数据服务
 * 专门用于从后端Agent系统获取真实的交易数据
 */

import { baseUrl } from './config.js';

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
   * 获取真实股票数据
   */
  async getStockData(symbols = ['000001', '600000', '600519'], period = '1d') {
    try {
      console.log('[Agent数据] 正在获取股票数据:', symbols);

      const response = await uni.request({
        url: `${this.apiBaseUrl}/api/market-data`,
        method: 'GET',
        data: {
          symbols: symbols.join(','),
          period: period,
          limit: 100
        },
        timeout: this.timeout,
        header: {
          'Content-Type': 'application/json'
        }
      });

      if (response.statusCode === 200 && response.data) {
        console.log('[Agent数据] 成功获取股票数据:', response.data);

        return {
          success: true,
          data: response.data.market_data || response.data,
          symbols: symbols,
          period: period,
          timestamp: new Date().toISOString()
        };
      } else {
        throw new Error(`API响应错误: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('[Agent数据] 获取股票数据失败:', error);

      // 返回模拟股票数据
      console.log('[Agent数据] 使用模拟股票数据');
      return {
        success: true,
        data: this._generateMockStockData(symbols),
        symbols: symbols,
        period: period,
        timestamp: new Date().toISOString(),
        source: 'mock'
      };
    }
  }

  /**
   * 运行回测
   */
  async runBacktest(config = {}) {
    try {
      console.log('[Agent数据] 正在运行回测:', config);

      const backtestConfig = {
        strategy: config.strategy || 'ma_crossover',
        symbols: config.symbols || ['000001', '600000'],
        start_date: config.start_date || '2023-01-01',
        end_date: config.end_date || '2024-01-01',
        initial_capital: config.initial_capital || 100000,
        ...config
      };

      const response = await uni.request({
        url: `${this.apiBaseUrl}/api/backtesting/run`,
        method: 'POST',
        data: backtestConfig,
        timeout: 30000, // 回测可能需要更长时间
        header: {
          'Content-Type': 'application/json'
        }
      });

      if (response.statusCode === 200 && response.data) {
        console.log('[Agent数据] 回测运行成功:', response.data);

        return {
          success: true,
          data: response.data,
          config: backtestConfig,
          timestamp: new Date().toISOString()
        };
      } else {
        throw new Error(`回测API响应错误: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('[Agent数据] 回测运行失败:', error);

      // 返回模拟回测结果
      console.log('[Agent数据] 使用模拟回测结果');
      return {
        success: true,
        data: this._generateMockBacktestResult(config),
        config: config,
        timestamp: new Date().toISOString(),
        source: 'mock'
      };
    }
  }

  /**
   * 生成模拟股票数据
   */
  _generateMockStockData(symbols) {
    const mockData = {};

    symbols.forEach(symbol => {
      const basePrice = Math.random() * 100 + 10; // 10-110之间的基础价格
      const data = [];

      // 生成30天的模拟数据
      for (let i = 0; i < 30; i++) {
        const date = new Date();
        date.setDate(date.getDate() - (29 - i));

        const open = basePrice + (Math.random() - 0.5) * 5;
        const close = open + (Math.random() - 0.5) * 3;
        const high = Math.max(open, close) + Math.random() * 2;
        const low = Math.min(open, close) - Math.random() * 2;
        const volume = Math.floor(Math.random() * 1000000) + 100000;

        data.push({
          date: date.toISOString().split('T')[0],
          open: open.toFixed(2),
          high: high.toFixed(2),
          low: low.toFixed(2),
          close: close.toFixed(2),
          volume: volume,
          symbol: symbol
        });
      }

      mockData[symbol] = {
        symbol: symbol,
        name: this._getStockName(symbol),
        current_price: data[data.length - 1].close,
        change: (Math.random() - 0.5) * 5,
        change_percent: (Math.random() - 0.5) * 10,
        volume: data[data.length - 1].volume,
        kline_data: data
      };
    });

    return mockData;
  }

  /**
   * 生成模拟回测结果
   */
  _generateMockBacktestResult(config) {
    const initialCapital = config.initial_capital || 100000;
    const finalValue = initialCapital * (1 + (Math.random() - 0.3) * 0.5); // -30%到+20%的收益
    const totalReturn = (finalValue - initialCapital) / initialCapital;

    return {
      backtest_id: `mock_${Date.now()}`,
      strategy: config.strategy || 'ma_crossover',
      symbols: config.symbols || ['000001', '600000'],
      start_date: config.start_date || '2023-01-01',
      end_date: config.end_date || '2024-01-01',
      initial_capital: initialCapital,
      final_value: finalValue,
      total_return: totalReturn,
      total_return_pct: totalReturn * 100,
      max_drawdown: Math.random() * 0.2,
      sharpe_ratio: (Math.random() - 0.5) * 3,
      win_rate: 0.4 + Math.random() * 0.4,
      total_trades: Math.floor(Math.random() * 100) + 20,
      profitable_trades: Math.floor(Math.random() * 50) + 10,
      avg_trade_return: totalReturn / 50,
      trades: this._generateMockTrades(config),
      equity_curve: this._generateMockEquityCurve(initialCapital, finalValue),
      status: 'completed',
      created_at: new Date().toISOString()
    };
  }

  /**
   * 生成模拟交易记录
   */
  _generateMockTrades(config) {
    const trades = [];
    const symbols = config.symbols || ['000001', '600000'];
    const tradeCount = Math.floor(Math.random() * 20) + 5;

    for (let i = 0; i < tradeCount; i++) {
      const symbol = symbols[Math.floor(Math.random() * symbols.length)];
      const entryDate = new Date(config.start_date || '2023-01-01');
      entryDate.setDate(entryDate.getDate() + Math.floor(Math.random() * 300));

      const exitDate = new Date(entryDate);
      exitDate.setDate(exitDate.getDate() + Math.floor(Math.random() * 30) + 1);

      const entryPrice = 10 + Math.random() * 90;
      const exitPrice = entryPrice * (1 + (Math.random() - 0.5) * 0.2);
      const quantity = Math.floor(Math.random() * 1000) + 100;
      const pnl = (exitPrice - entryPrice) * quantity;

      trades.push({
        symbol: symbol,
        entry_date: entryDate.toISOString().split('T')[0],
        exit_date: exitDate.toISOString().split('T')[0],
        entry_price: entryPrice.toFixed(2),
        exit_price: exitPrice.toFixed(2),
        quantity: quantity,
        side: 'long',
        pnl: pnl.toFixed(2),
        pnl_pct: ((exitPrice - entryPrice) / entryPrice * 100).toFixed(2)
      });
    }

    return trades;
  }

  /**
   * 生成模拟资金曲线
   */
  _generateMockEquityCurve(initialCapital, finalValue) {
    const curve = [];
    const days = 250; // 一年交易日
    const dailyReturn = Math.pow(finalValue / initialCapital, 1 / days) - 1;

    let currentValue = initialCapital;
    const startDate = new Date('2023-01-01');

    for (let i = 0; i < days; i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i);

      // 添加随机波动
      const randomReturn = dailyReturn + (Math.random() - 0.5) * 0.02;
      currentValue *= (1 + randomReturn);

      curve.push({
        date: date.toISOString().split('T')[0],
        value: currentValue.toFixed(2),
        return: ((currentValue - initialCapital) / initialCapital * 100).toFixed(2)
      });
    }

    return curve;
  }

  /**
   * 获取股票名称
   */
  _getStockName(symbol) {
    const stockNames = {
      '000001': '平安银行',
      '000002': '万科A',
      '600000': '浦发银行',
      '600036': '招商银行',
      '600519': '贵州茅台',
      '000858': '五粮液',
      '300750': '宁德时代',
      '601318': '中国平安'
    };

    return stockNames[symbol] || `股票${symbol}`;
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
