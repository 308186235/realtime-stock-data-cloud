/**
 * 茶股帮实时数据服务
 * 提供茶股帮实时股票数据的前端接口
 */

import { API_BASE_URL, API_ENDPOINTS } from './config.js';

class ChaguBangService {
  constructor() {
    this.baseUrl = API_BASE_URL;
    this.endpoints = API_ENDPOINTS.chagubang;
    this.cache = new Map();
    this.cacheTimeout = 5000; // 5秒缓存
    this.subscribers = new Map();
    this.websocket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  /**
   * 通用请求方法
   */
  async request(endpoint, options = {}) {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`茶股帮API请求失败 ${endpoint}:`, error);
      throw error;
    }
  }

  /**
   * 检查服务健康状态
   */
  async checkHealth() {
    try {
      const response = await this.request(this.endpoints.health);
      return response;
    } catch (error) {
      console.error('茶股帮健康检查失败:', error);
      return { status: 'unhealthy', error: error.message };
    }
  }

  /**
   * 获取单只股票数据
   */
  async getStockData(stockCode) {
    try {
      // 检查缓存
      const cacheKey = `stock_${stockCode}`;
      if (this.cache.has(cacheKey)) {
        const cached = this.cache.get(cacheKey);
        if (Date.now() - cached.timestamp < this.cacheTimeout) {
          return cached.data;
        }
      }

      const response = await this.request(`${this.endpoints.stock}/${stockCode}`);
      
      // 缓存数据
      this.cache.set(cacheKey, {
        data: response,
        timestamp: Date.now()
      });

      return response;
    } catch (error) {
      console.error(`获取股票数据失败 ${stockCode}:`, error);
      throw error;
    }
  }

  /**
   * 获取所有股票数据
   */
  async getAllStocks(options = {}) {
    try {
      const params = new URLSearchParams();
      
      if (options.limit) params.append('limit', options.limit);
      if (options.sortBy) params.append('sort_by', options.sortBy);
      if (options.order) params.append('order', options.order);

      const endpoint = `${this.endpoints.stocks}${params.toString() ? '?' + params.toString() : ''}`;
      const response = await this.request(endpoint);
      
      return response;
    } catch (error) {
      console.error('获取所有股票数据失败:', error);
      throw error;
    }
  }

  /**
   * 获取市场概览
   */
  async getMarketOverview() {
    try {
      // 检查缓存
      const cacheKey = 'market_overview';
      if (this.cache.has(cacheKey)) {
        const cached = this.cache.get(cacheKey);
        if (Date.now() - cached.timestamp < this.cacheTimeout) {
          return cached.data;
        }
      }

      const response = await this.request(this.endpoints.market);
      
      // 缓存数据
      this.cache.set(cacheKey, {
        data: response,
        timestamp: Date.now()
      });

      return response;
    } catch (error) {
      console.error('获取市场概览失败:', error);
      throw error;
    }
  }

  /**
   * 获取热门股票
   */
  async getHotStocks(limit = 10, type = 'change') {
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        type: type
      });

      const endpoint = `${this.endpoints.hot}?${params.toString()}`;
      const response = await this.request(endpoint);
      
      return response;
    } catch (error) {
      console.error('获取热门股票失败:', error);
      throw error;
    }
  }

  /**
   * 搜索股票
   */
  async searchStocks(query, limit = 10) {
    try {
      const params = new URLSearchParams({
        q: query,
        limit: limit.toString()
      });

      const endpoint = `${this.endpoints.search}?${params.toString()}`;
      const response = await this.request(endpoint);
      
      return response;
    } catch (error) {
      console.error('搜索股票失败:', error);
      throw error;
    }
  }

  /**
   * 获取服务统计
   */
  async getServiceStats() {
    try {
      const response = await this.request(this.endpoints.stats);
      return response;
    } catch (error) {
      console.error('获取服务统计失败:', error);
      throw error;
    }
  }

  /**
   * 订阅数据更新
   */
  subscribe(eventType, callback) {
    if (!this.subscribers.has(eventType)) {
      this.subscribers.set(eventType, new Set());
    }
    this.subscribers.get(eventType).add(callback);

    // 如果是第一次订阅，启动WebSocket连接
    if (this.subscribers.size === 1) {
      this.connectWebSocket();
    }

    // 返回取消订阅函数
    return () => {
      this.unsubscribe(eventType, callback);
    };
  }

  /**
   * 取消订阅
   */
  unsubscribe(eventType, callback) {
    if (this.subscribers.has(eventType)) {
      this.subscribers.get(eventType).delete(callback);
      
      // 如果没有回调了，删除事件类型
      if (this.subscribers.get(eventType).size === 0) {
        this.subscribers.delete(eventType);
      }
    }

    // 如果没有订阅者了，关闭WebSocket
    if (this.subscribers.size === 0) {
      this.disconnectWebSocket();
    }
  }

  /**
   * 连接WebSocket
   */
  connectWebSocket() {
    try {
      const wsUrl = `${this.baseUrl.replace('http', 'ws')}${this.endpoints.ws}`;
      this.websocket = new WebSocket(wsUrl);

      this.websocket.onopen = () => {
        console.log('茶股帮WebSocket连接成功');
        this.reconnectAttempts = 0;
      };

      this.websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleWebSocketMessage(data);
        } catch (error) {
          console.error('解析WebSocket消息失败:', error);
        }
      };

      this.websocket.onclose = () => {
        console.log('茶股帮WebSocket连接关闭');
        this.attemptReconnect();
      };

      this.websocket.onerror = (error) => {
        console.error('茶股帮WebSocket错误:', error);
      };

    } catch (error) {
      console.error('创建WebSocket连接失败:', error);
    }
  }

  /**
   * 断开WebSocket
   */
  disconnectWebSocket() {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
  }

  /**
   * 尝试重连WebSocket
   */
  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.subscribers.size > 0) {
      this.reconnectAttempts++;
      const delay = Math.pow(2, this.reconnectAttempts) * 1000; // 指数退避
      
      console.log(`${delay/1000}秒后尝试重连WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connectWebSocket();
      }, delay);
    }
  }

  /**
   * 处理WebSocket消息
   */
  handleWebSocketMessage(data) {
    const { type } = data;
    
    if (this.subscribers.has(type)) {
      this.subscribers.get(type).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('WebSocket回调执行失败:', error);
        }
      });
    }

    // 更新缓存
    if (type === 'market_overview') {
      this.cache.set('market_overview', {
        data: { success: true, data: data.data },
        timestamp: Date.now()
      });
    }
  }

  /**
   * 清除缓存
   */
  clearCache() {
    this.cache.clear();
  }

  /**
   * 获取缓存统计
   */
  getCacheStats() {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys())
    };
  }
}

// 创建全局实例
const chaguBangService = new ChaguBangService();

// 导出服务实例和类
export default chaguBangService;
export { ChaguBangService };
