/**
 * 真实股票数据服务
 * 通过Agent后端获取真实股票数据和推送
 */

import { baseUrl } from './config.js';

class RealTimeDataService {
  constructor() {
    this.apiBaseUrl = baseUrl;
    this.websocket = null;
    this.subscribers = new Map(); // 订阅者管理
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 5000;
    this.isConnected = false;
  }

  /**
   * 获取真实股票实时数据
   */
  async getRealTimeQuotes(symbols) {
    try {
      console.log('[真实数据] 获取实时行情:', symbols);
      
      const response = await uni.request({
        url: `${this.apiBaseUrl}/api/stock/realtime`,
        method: 'GET',
        data: { 
          symbols: Array.isArray(symbols) ? symbols.join(',') : symbols,
          source: 'agent' // 指定使用Agent数据源
        },
        timeout: 10000,
        header: {
          'Content-Type': 'application/json'
        }
      });

      if (response.statusCode === 200 && response.data) {
        console.log('[真实数据] 成功获取实时行情:', response.data);
        
        return {
          success: true,
          data: this._formatQuoteData(response.data),
          timestamp: new Date().toISOString(),
          source: 'real'
        };
      } else {
        throw new Error(`API响应错误: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('[真实数据] 获取实时行情失败:', error);
      throw new Error(`无法获取真实股票数据: ${error.message}`);
    }
  }

  /**
   * 获取真实K线数据
   */
  async getKLineData(symbol, period = '1d', limit = 100) {
    try {
      console.log('[真实数据] 获取K线数据:', symbol, period);
      
      const response = await uni.request({
        url: `${this.apiBaseUrl}/api/stock/kline`,
        method: 'GET',
        data: { 
          symbol: symbol,
          period: period,
          limit: limit,
          source: 'agent'
        },
        timeout: 15000,
        header: {
          'Content-Type': 'application/json'
        }
      });

      if (response.statusCode === 200 && response.data) {
        console.log('[真实数据] 成功获取K线数据:', response.data);
        
        return {
          success: true,
          data: this._formatKLineData(response.data),
          symbol: symbol,
          period: period,
          timestamp: new Date().toISOString(),
          source: 'real'
        };
      } else {
        throw new Error(`API响应错误: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('[真实数据] 获取K线数据失败:', error);
      throw new Error(`无法获取K线数据: ${error.message}`);
    }
  }

  /**
   * 建立WebSocket连接接收实时推送
   */
  connectWebSocket(symbols = []) {
    try {
      console.log('[真实数据] 建立WebSocket连接:', symbols);
      
      const wsUrl = `${this.apiBaseUrl.replace('http', 'ws')}/ws/stock-data`;
      this.websocket = uni.connectSocket({
        url: wsUrl,
        protocols: ['stock-data']
      });

      this.websocket.onOpen(() => {
        console.log('[真实数据] WebSocket连接成功');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        
        // 订阅股票数据
        if (symbols.length > 0) {
          this.subscribeSymbols(symbols);
        }
      });

      this.websocket.onMessage((message) => {
        try {
          const data = JSON.parse(message.data);
          console.log('[真实数据] 收到推送数据:', data);
          
          // 分发数据给订阅者
          this._distributeData(data);
        } catch (error) {
          console.error('[真实数据] 解析推送数据失败:', error);
        }
      });

      this.websocket.onError((error) => {
        console.error('[真实数据] WebSocket连接错误:', error);
        this.isConnected = false;
        this._attemptReconnect(symbols);
      });

      this.websocket.onClose(() => {
        console.log('[真实数据] WebSocket连接关闭');
        this.isConnected = false;
        this._attemptReconnect(symbols);
      });

    } catch (error) {
      console.error('[真实数据] WebSocket连接失败:', error);
      throw new Error(`无法建立实时数据连接: ${error.message}`);
    }
  }

  /**
   * 订阅股票数据推送
   */
  subscribeSymbols(symbols) {
    if (!this.isConnected || !this.websocket) {
      throw new Error('WebSocket未连接，无法订阅数据');
    }

    const subscribeMessage = {
      action: 'subscribe',
      symbols: Array.isArray(symbols) ? symbols : [symbols],
      timestamp: new Date().toISOString()
    };

    console.log('[真实数据] 订阅股票数据:', subscribeMessage);
    this.websocket.send({
      data: JSON.stringify(subscribeMessage)
    });
  }

  /**
   * 添加数据订阅者
   */
  addSubscriber(id, callback) {
    this.subscribers.set(id, callback);
    console.log('[真实数据] 添加订阅者:', id);
  }

  /**
   * 移除数据订阅者
   */
  removeSubscriber(id) {
    this.subscribers.delete(id);
    console.log('[真实数据] 移除订阅者:', id);
  }

  /**
   * 分发数据给订阅者
   */
  _distributeData(data) {
    this.subscribers.forEach((callback, id) => {
      try {
        callback(data);
      } catch (error) {
        console.error(`[真实数据] 分发数据给订阅者${id}失败:`, error);
      }
    });
  }

  /**
   * 尝试重连
   */
  _attemptReconnect(symbols) {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[真实数据] 达到最大重连次数，停止重连');
      return;
    }

    this.reconnectAttempts++;
    console.log(`[真实数据] 尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      this.connectWebSocket(symbols);
    }, this.reconnectInterval);
  }

  /**
   * 格式化行情数据
   */
  _formatQuoteData(rawData) {
    if (!rawData || !rawData.quotes) {
      return {};
    }

    const formatted = {};
    rawData.quotes.forEach(quote => {
      formatted[quote.symbol] = {
        symbol: quote.symbol,
        name: quote.name,
        current_price: parseFloat(quote.current_price || quote.price),
        change: parseFloat(quote.change || 0),
        change_percent: parseFloat(quote.change_percent || 0),
        volume: parseInt(quote.volume || 0),
        turnover: parseFloat(quote.turnover || 0),
        high: parseFloat(quote.high || 0),
        low: parseFloat(quote.low || 0),
        open: parseFloat(quote.open || 0),
        prev_close: parseFloat(quote.prev_close || 0),
        timestamp: quote.timestamp || new Date().toISOString()
      };
    });

    return formatted;
  }

  /**
   * 格式化K线数据
   */
  _formatKLineData(rawData) {
    if (!rawData || !rawData.klines) {
      return [];
    }

    return rawData.klines.map(kline => ({
      timestamp: kline.timestamp,
      open: parseFloat(kline.open),
      high: parseFloat(kline.high),
      low: parseFloat(kline.low),
      close: parseFloat(kline.close),
      volume: parseInt(kline.volume),
      turnover: parseFloat(kline.turnover || 0)
    }));
  }

  /**
   * 关闭连接
   */
  disconnect() {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    this.isConnected = false;
    this.subscribers.clear();
    console.log('[真实数据] 已断开连接');
  }

  /**
   * 获取连接状态
   */
  getConnectionStatus() {
    return {
      connected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      subscriberCount: this.subscribers.size
    };
  }
}

// 创建单例实例
const realTimeDataService = new RealTimeDataService();

export default realTimeDataService;
