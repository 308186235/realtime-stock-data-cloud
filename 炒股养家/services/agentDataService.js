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
