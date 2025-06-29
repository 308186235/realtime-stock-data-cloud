/**
 * 数据服务
 * 统一管理前后端数据交互，提供缓存、错误处理、重试机制
 */

import { request } from '@/utils/request.js';

class DataService {
  constructor() {
    // 数据缓存
    this.cache = new Map();
    
    // 缓存过期时间配置（毫秒）
    this.cacheExpiry = {
      'agent-analysis': 5 * 60 * 1000,    // 5分钟
      'account-balance': 2 * 60 * 1000,   // 2分钟
      'account-positions': 3 * 60 * 1000, // 3分钟
      'health': 1 * 60 * 1000             // 1分钟
    };
    
    // 请求状态管理
    this.requestStatus = new Map();
    
    // 重试配置
    this.retryConfig = {
      maxRetries: 3,
      retryDelay: 1000, // 1秒
      retryMultiplier: 2
    };
  }
  
  /**
   * 获取缓存键
   */
  getCacheKey(endpoint, params = {}) {
    const paramStr = Object.keys(params).length > 0 ? JSON.stringify(params) : '';
    return `${endpoint}${paramStr}`;
  }
  
  /**
   * 检查缓存是否有效
   */
  isCacheValid(cacheKey) {
    const cached = this.cache.get(cacheKey);
    if (!cached) return false;
    
    const now = Date.now();
    const endpoint = cacheKey.split('{')[0]; // 提取端点名称
    const expiry = this.cacheExpiry[endpoint] || 5 * 60 * 1000; // 默认5分钟
    
    return (now - cached.timestamp) < expiry;
  }
  
  /**
   * 设置缓存
   */
  setCache(cacheKey, data) {
    this.cache.set(cacheKey, {
      data: data,
      timestamp: Date.now()
    });
  }
  
  /**
   * 获取缓存数据
   */
  getCache(cacheKey) {
    const cached = this.cache.get(cacheKey);
    return cached ? cached.data : null;
  }
  
  /**
   * 清除缓存
   */
  clearCache(pattern = null) {
    if (pattern) {
      // 清除匹配模式的缓存
      for (const key of this.cache.keys()) {
        if (key.includes(pattern)) {
          this.cache.delete(key);
        }
      }
    } else {
      // 清除所有缓存
      this.cache.clear();
    }
  }
  
  /**
   * 带重试的请求方法
   */
  async requestWithRetry(options, retryCount = 0) {
    try {
      const response = await request(options);
      return response;
    } catch (error) {
      if (retryCount < this.retryConfig.maxRetries) {
        const delay = this.retryConfig.retryDelay * Math.pow(this.retryConfig.retryMultiplier, retryCount);
        
        console.log(`请求失败，${delay}ms后重试 (${retryCount + 1}/${this.retryConfig.maxRetries}):`, options.url);
        
        await new Promise(resolve => setTimeout(resolve, delay));
        return this.requestWithRetry(options, retryCount + 1);
      } else {
        throw error;
      }
    }
  }
  
  /**
   * 通用数据获取方法
   */
  async getData(endpoint, params = {}, options = {}) {
    const cacheKey = this.getCacheKey(endpoint, params);
    
    // 检查是否正在请求中
    if (this.requestStatus.has(cacheKey)) {
      return this.requestStatus.get(cacheKey);
    }
    
    // 检查缓存
    if (!options.forceRefresh && this.isCacheValid(cacheKey)) {
      return Promise.resolve(this.getCache(cacheKey));
    }
    
    // 创建请求Promise
    const requestPromise = this.requestWithRetry({
      url: `/api/${endpoint}`,
      method: options.method || 'GET',
      data: params
    }).then(data => {
      // 缓存数据
      this.setCache(cacheKey, data);
      // 清除请求状态
      this.requestStatus.delete(cacheKey);
      return data;
    }).catch(error => {
      // 清除请求状态
      this.requestStatus.delete(cacheKey);
      throw error;
    });
    
    // 记录请求状态
    this.requestStatus.set(cacheKey, requestPromise);
    
    return requestPromise;
  }
  
  /**
   * 获取Agent分析数据
   */
  async getAgentAnalysis(forceRefresh = false) {
    return this.getData('agent-analysis', {}, { forceRefresh });
  }
  
  /**
   * 获取账户余额数据
   */
  async getAccountBalance(forceRefresh = false) {
    return this.getData('account-balance', {}, { forceRefresh });
  }
  
  /**
   * 获取持仓数据
   */
  async getAccountPositions(forceRefresh = false) {
    return this.getData('account-positions', {}, { forceRefresh });
  }
  
  /**
   * 获取健康检查数据
   */
  async getHealth(forceRefresh = false) {
    return this.getData('health', {}, { forceRefresh });
  }
  
  /**
   * 批量获取数据
   */
  async getBatchData(endpoints, forceRefresh = false) {
    const promises = endpoints.map(endpoint => {
      if (typeof endpoint === 'string') {
        return this.getData(endpoint, {}, { forceRefresh });
      } else {
        return this.getData(endpoint.name, endpoint.params || {}, { 
          forceRefresh: endpoint.forceRefresh || forceRefresh,
          method: endpoint.method 
        });
      }
    });
    
    try {
      const results = await Promise.allSettled(promises);
      return results.map((result, index) => ({
        endpoint: typeof endpoints[index] === 'string' ? endpoints[index] : endpoints[index].name,
        success: result.status === 'fulfilled',
        data: result.status === 'fulfilled' ? result.value : null,
        error: result.status === 'rejected' ? result.reason : null
      }));
    } catch (error) {
      console.error('批量获取数据失败:', error);
      throw error;
    }
  }
  
  /**
   * 提交交易订单
   */
  async submitTradeOrder(orderData) {
    return this.requestWithRetry({
      url: '/api/trade-order',
      method: 'POST',
      data: orderData
    });
  }
  
  /**
   * 获取缓存统计信息
   */
  getCacheStats() {
    const stats = {
      totalEntries: this.cache.size,
      entries: []
    };
    
    for (const [key, value] of this.cache.entries()) {
      const age = Date.now() - value.timestamp;
      const endpoint = key.split('{')[0];
      const expiry = this.cacheExpiry[endpoint] || 5 * 60 * 1000;
      const isValid = age < expiry;
      
      stats.entries.push({
        key,
        age: Math.round(age / 1000), // 秒
        isValid,
        expiresIn: isValid ? Math.round((expiry - age) / 1000) : 0
      });
    }
    
    return stats;
  }
  
  /**
   * 预加载数据
   */
  async preloadData() {
    const endpoints = ['agent-analysis', 'account-balance', 'account-positions'];
    
    try {
      await this.getBatchData(endpoints);
      console.log('数据预加载完成');
    } catch (error) {
      console.error('数据预加载失败:', error);
    }
  }
  
  /**
   * 设置自动刷新
   */
  startAutoRefresh(interval = 30000) { // 默认30秒
    if (this.autoRefreshTimer) {
      clearInterval(this.autoRefreshTimer);
    }
    
    this.autoRefreshTimer = setInterval(async () => {
      try {
        await this.getBatchData(['agent-analysis', 'account-balance'], true);
        console.log('自动刷新数据完成');
      } catch (error) {
        console.error('自动刷新数据失败:', error);
      }
    }, interval);
  }
  
  /**
   * 停止自动刷新
   */
  stopAutoRefresh() {
    if (this.autoRefreshTimer) {
      clearInterval(this.autoRefreshTimer);
      this.autoRefreshTimer = null;
    }
  }
}

// 创建单例实例
const dataService = new DataService();

export default dataService;
