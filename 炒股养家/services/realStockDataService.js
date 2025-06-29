/**
 * 真实股票数据服务
 * 连接专业股票数据推送API
 * 支持多API Key管理和自动切换
 */

import apiKeyManager from './apiKeyManager.js';

class RealStockDataService {
  constructor() {
    this.currentApiKey = null;
    this.host = ''; // 需要配置真实服务器地址
    this.port = 0;  // 需要配置真实服务器端口
    this.socket = null;
    this.isConnected = false;
    this.subscribers = new Map();
    this.dataQueue = [];
    this.maxQueueSize = 10000; // 最大队列大小
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 5000;
    this.connectionErrors = 0;
    this.maxConnectionErrors = 3;
  }

  /**
   * 连接到真实股票数据服务器
   */
  async connect(host, port) {
    try {
      console.log('[真实股票数据] 连接到数据服务器:', host, port);
      
      this.host = host;
      this.port = port;
      
      // 在uni-app中使用WebSocket连接
      const wsUrl = `ws://${host}:${port}`;
      
      this.socket = uni.connectSocket({
        url: wsUrl,
        protocols: ['stock-data']
      });

      this.socket.onOpen(() => {
        console.log('[真实股票数据] WebSocket连接成功');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        
        // 发送认证token
        this.authenticate();
      });

      this.socket.onMessage((message) => {
        this.handleMessage(message.data);
      });

      this.socket.onError((error) => {
        console.error('[真实股票数据] 连接错误:', error);
        this.isConnected = false;
        this.connectionErrors++;

        // 报告API Key错误
        const currentKey = this.getCurrentApiKey();
        if (currentKey) {
          apiKeyManager.reportError(currentKey.id, error);
        }

        this.attemptReconnect();
      });

      this.socket.onClose(() => {
        console.log('[真实股票数据] 连接关闭');
        this.isConnected = false;
        this.connectionErrors++;
        this.attemptReconnect();
      });

    } catch (error) {
      console.error('[真实股票数据] 连接失败:', error);
      throw new Error(`连接真实股票数据服务失败: ${error.message}`);
    }
  }

  /**
   * 获取当前API Key
   */
  getCurrentApiKey() {
    if (!this.currentApiKey) {
      this.currentApiKey = apiKeyManager.getCurrentApiKey();
    }
    return this.currentApiKey;
  }

  /**
   * 切换API Key
   */
  switchApiKey() {
    const oldKey = this.currentApiKey;
    this.currentApiKey = apiKeyManager.switchToNextKey();

    if (this.currentApiKey) {
      console.log(`[真实股票数据] API Key切换: ${oldKey?.name} -> ${this.currentApiKey.name}`);
      return true;
    } else {
      console.error('[真实股票数据] 没有可用的API Key');
      return false;
    }
  }

  /**
   * 发送认证token
   */
  authenticate() {
    const apiKey = this.getCurrentApiKey();
    if (this.socket && this.isConnected && apiKey) {
      console.log('[真实股票数据] 发送认证token:', apiKey.name);
      this.socket.send({
        data: apiKey.key
      });
    } else {
      console.error('[真实股票数据] 无法认证: 缺少API Key或连接');
    }
  }

  /**
   * 处理接收到的消息
   */
  handleMessage(data) {
    try {
      // 快速处理数据，避免堆积
      this.processDataQuickly(data);
    } catch (error) {
      console.error('[真实股票数据] 处理消息失败:', error);
    }
  }

  /**
   * 快速处理数据
   */
  processDataQuickly(rawData) {
    try {
      // 检查队列大小，防止内存溢出
      if (this.dataQueue.length > this.maxQueueSize) {
        console.warn('[真实股票数据] 队列已满，清理旧数据');
        this.dataQueue = this.dataQueue.slice(-this.maxQueueSize / 2);
      }

      // 解析数据
      let stockData;
      
      if (typeof rawData === 'string') {
        // 沪深数据格式解析
        stockData = this.parseHuShenData(rawData);
      } else {
        // 北交所JSON格式解析
        stockData = this.parseBeiJiaoSuoData(rawData);
      }

      if (stockData) {
        // 添加到队列
        this.dataQueue.push({
          ...stockData,
          timestamp: Date.now(),
          source: 'real'
        });

        // 立即分发给订阅者
        this.distributeData(stockData);
      }

    } catch (error) {
      console.error('[真实股票数据] 快速处理数据失败:', error);
    }
  }

  /**
   * 解析沪深数据格式
   */
  parseHuShenData(dataString) {
    try {
      const fields = dataString.split('$');
      
      if (fields.length < 33) {
        return null;
      }

      return {
        symbol: fields[0],           // 股票代码
        name: fields[1],             // 股票名称
        timestamp: parseInt(fields[2]) * 1000, // 时间戳
        open: parseFloat(fields[3]),  // 开盘价
        high: parseFloat(fields[4]),  // 最高价
        low: parseFloat(fields[5]),   // 最低价
        current_price: parseFloat(fields[6]), // 最新价
        volume: parseInt(fields[7]),  // 成交量(手)
        turnover: parseFloat(fields[8]), // 成交额
        
        // 五档行情
        ask_prices: [
          parseFloat(fields[9]),   // 卖一价
          parseFloat(fields[10]),  // 卖二价
          parseFloat(fields[11]),  // 卖三价
          parseFloat(fields[12]),  // 卖四价
          parseFloat(fields[13])   // 卖五价
        ],
        ask_volumes: [
          parseInt(fields[14]),    // 卖一量
          parseInt(fields[15]),    // 卖二量
          parseInt(fields[16]),    // 卖三量
          parseInt(fields[17]),    // 卖四量
          parseInt(fields[18])     // 卖五量
        ],
        bid_prices: [
          parseFloat(fields[19]),  // 买一价
          parseFloat(fields[20]),  // 买二价
          parseFloat(fields[21]),  // 买三价
          parseFloat(fields[22]),  // 买四价
          parseFloat(fields[23])   // 买五价
        ],
        bid_volumes: [
          parseInt(fields[24]),    // 买一量
          parseInt(fields[25]),    // 买二量
          parseInt(fields[26]),    // 买三量
          parseInt(fields[27]),    // 买四量
          parseInt(fields[28])     // 买五量
        ],
        
        turnover_rate: parseFloat(fields[29]), // 换手率
        prev_close: parseFloat(fields[30]),    // 昨收盘价
        limit_up: parseFloat(fields[31]),      // 涨停价
        limit_down: parseFloat(fields[32]),    // 跌停价
        
        // 计算涨跌
        change: parseFloat(fields[6]) - parseFloat(fields[30]),
        change_percent: ((parseFloat(fields[6]) - parseFloat(fields[30])) / parseFloat(fields[30]) * 100).toFixed(2),
        
        market: this.getMarketFromSymbol(fields[0])
      };
    } catch (error) {
      console.error('[真实股票数据] 解析沪深数据失败:', error);
      return null;
    }
  }

  /**
   * 解析北交所数据格式
   */
  parseBeiJiaoSuoData(jsonData) {
    try {
      const data = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData;
      
      return {
        symbol: data.stock_code,
        name: this.getStockName(data.stock_code),
        timestamp: data.time,
        open: data.open,
        high: data.high,
        low: data.low,
        current_price: data.lastPrice,
        volume: data.volume,
        turnover: data.amount,
        
        // 五档行情
        ask_prices: data.askPrice,
        ask_volumes: data.askVol,
        bid_prices: data.bidPrice,
        bid_volumes: data.bidVol,
        
        prev_close: data.lastClose,
        pe_ratio: data.pe,
        
        // 计算涨跌
        change: data.lastPrice - data.lastClose,
        change_percent: ((data.lastPrice - data.lastClose) / data.lastClose * 100).toFixed(2),
        
        market: 'BJ' // 北交所
      };
    } catch (error) {
      console.error('[真实股票数据] 解析北交所数据失败:', error);
      return null;
    }
  }

  /**
   * 根据股票代码判断市场
   */
  getMarketFromSymbol(symbol) {
    if (symbol.startsWith('SZ')) return 'SZ'; // 深圳
    if (symbol.startsWith('SH')) return 'SH'; // 上海
    if (symbol.endsWith('.BJ')) return 'BJ';  // 北交所
    
    // 根据代码前缀判断
    const code = symbol.replace(/[A-Z]/g, '');
    if (code.startsWith('000') || code.startsWith('002') || code.startsWith('300')) {
      return 'SZ';
    } else if (code.startsWith('600') || code.startsWith('601') || code.startsWith('603')) {
      return 'SH';
    }
    
    return 'UNKNOWN';
  }

  /**
   * 获取股票名称
   */
  getStockName(symbol) {
    // 这里可以维护一个股票代码到名称的映射
    // 或者从其他API获取
    return symbol;
  }

  /**
   * 分发数据给订阅者
   */
  distributeData(stockData) {
    this.subscribers.forEach((callback, subscriberId) => {
      try {
        callback(stockData);
      } catch (error) {
        console.error(`[真实股票数据] 分发数据给订阅者${subscriberId}失败:`, error);
      }
    });
  }

  /**
   * 添加数据订阅者
   */
  subscribe(subscriberId, callback) {
    this.subscribers.set(subscriberId, callback);
    console.log('[真实股票数据] 添加订阅者:', subscriberId);
    
    return () => {
      this.unsubscribe(subscriberId);
    };
  }

  /**
   * 移除订阅者
   */
  unsubscribe(subscriberId) {
    this.subscribers.delete(subscriberId);
    console.log('[真实股票数据] 移除订阅者:', subscriberId);
  }

  /**
   * 获取最新数据
   */
  getLatestData(symbol) {
    // 从队列中查找最新的指定股票数据
    for (let i = this.dataQueue.length - 1; i >= 0; i--) {
      const data = this.dataQueue[i];
      if (data.symbol === symbol || data.symbol.includes(symbol)) {
        return data;
      }
    }
    return null;
  }

  /**
   * 获取多只股票的最新数据
   */
  getLatestDataBatch(symbols) {
    const result = {};
    
    symbols.forEach(symbol => {
      const data = this.getLatestData(symbol);
      if (data) {
        result[symbol] = data;
      }
    });
    
    return result;
  }

  /**
   * 尝试重连
   */
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[真实股票数据] 达到最大重连次数');

      // 如果连接错误过多，尝试切换API Key
      if (this.connectionErrors >= this.maxConnectionErrors) {
        console.log('[真实股票数据] 连接错误过多，尝试切换API Key');
        if (this.switchApiKey()) {
          this.reconnectAttempts = 0; // 重置重连次数
          this.connectionErrors = 0;  // 重置错误次数
        } else {
          console.error('[真实股票数据] 没有可用的API Key，停止重连');
          return;
        }
      } else {
        return;
      }
    }

    this.reconnectAttempts++;
    console.log(`[真实股票数据] 尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      if (this.host && this.port) {
        this.connect(this.host, this.port);
      }
    }, this.reconnectInterval);
  }

  /**
   * 尝试重连
   */
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[真实股票数据] 达到最大重连次数，停止重连');
      return;
    }

    this.reconnectAttempts++;
    console.log(`[真实股票数据] 尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      if (this.host && this.port) {
        this.connect(this.host, this.port);
      }
    }, this.reconnectInterval);
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.isConnected = false;
    this.subscribers.clear();
    this.dataQueue = [];
    console.log('[真实股票数据] 已断开连接');
  }

  /**
   * 获取连接状态
   */
  getStatus() {
    return {
      connected: this.isConnected,
      queueSize: this.dataQueue.length,
      subscriberCount: this.subscribers.size,
      reconnectAttempts: this.reconnectAttempts,
      apiKey: this.apiKey.substring(0, 8) + '...' // 部分显示API Key
    };
  }
}

// 创建单例实例
const realStockDataService = new RealStockDataService();

export default realStockDataService;
