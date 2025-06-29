/**
 * 增强版WebSocket客户端
 * 支持自动重连,心跳检测,订阅管理和错误处理
 */

// WebSocket事件类型
export const EVENTS = {
  OPEN: 'open',
  CLOSE: 'close',
  ERROR: 'error',
  MESSAGE: 'message',
  RECONNECT: 'reconnect',
  RECONNECT_ATTEMPT: 'reconnect_attempt',
  SUBSCRIBE: 'subscribe',
  UNSUBSCRIBE: 'unsubscribe'
};

// WebSocket消息类型
export const MSG_TYPES = {
  PING: 'ping',
  PONG: 'pong',
  SUBSCRIBE: 'subscribe',
  UNSUBSCRIBE: 'unsubscribe',
  DATA: 'data',
  ERROR: 'error'
};

// 默认配置
const DEFAULT_CONFIG = {
  url: 'ws://localhost:8000/ws', // 使用新的根路径WebSocket端点
  reconnectInterval: 5000,       // 重连间隔(毫秒)
  reconnectAttempts: 10,         // 最大重连次数
  heartbeatInterval: 30000,      // 心跳间隔(毫秒)
  debug: false                   // 调试模式
};

export default class WebSocketClient {
  /**
   * WebSocket客户端
   * @param {Object} config 配置选项
   */
  constructor(config = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.socket = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.subscriptions = new Map(); // 管理订阅
    this.eventListeners = {};      // 事件监听器
    this.heartbeatTimer = null;
    this.reconnectTimer = null;
    
    // 绑定方法
    this._onOpen = this._onOpen.bind(this);
    this._onClose = this._onClose.bind(this);
    this._onError = this._onError.bind(this);
    this._onMessage = this._onMessage.bind(this);
    
    this._log('WebSocket客户端已初始化');
  }
  
  /**
   * 连接WebSocket服务器
   * @returns {Promise} 连接Promise
   */
  connect() {
    if (this.socket && this.isConnected) {
      this._log('WebSocket已连接');
      return Promise.resolve();
    }
    
    return new Promise((resolve, reject) => {
      try {
        this._log(`连接到WebSocket: ${this.config.url}`);
        this.socket = new WebSocket(this.config.url);
        
        this.socket.onopen = (event) => {
          this._onOpen(event);
          resolve(event);
        };
        
        this.socket.onclose = this._onClose;
        this.socket.onerror = (error) => {
          this._onError(error);
          reject(error);
        };
        this.socket.onmessage = this._onMessage;
      } catch (error) {
        this._log(`连接错误: ${error.message}`, 'error');
        reject(error);
      }
    });
  }
  
  /**
   * 断开WebSocket连接
   */
  disconnect() {
    this._log('断开WebSocket连接');
    
    // 清除定时器
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    // 重置重连计数
    this.reconnectAttempts = 0;
    
    // 如果已连接,关闭连接
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    
    this.isConnected = false;
  }
  
  /**
   * 订阅频道
   * @param {string} channel 频道名称
   * @param {Object} params 订阅参数
   */
  subscribe(channel, params = {}) {
    if (!this.isConnected) {
      this._log(`未连接,无法订阅: ${channel}`, 'error');
      return;
    }
    
    this._log(`订阅频道: ${channel}, 参数: ${JSON.stringify(params)}`);
    
    // 保存订阅
    this.subscriptions.set(channel, params);
    
    // 发送订阅消息
    const message = {
      type: MSG_TYPES.SUBSCRIBE,
      channel,
      params
    };
    
    this.send(message);
    this.emit(EVENTS.SUBSCRIBE, { channel, params });
  }
  
  /**
   * 取消订阅
   * @param {string} channel 频道名称
   */
  unsubscribe(channel) {
    if (!this.isConnected) {
      this._log(`未连接,无法取消订阅: ${channel}`, 'error');
      return;
    }
    
    this._log(`取消订阅频道: ${channel}`);
    
    // 移除订阅
    this.subscriptions.delete(channel);
    
    // 发送取消订阅消息
    const message = {
      type: MSG_TYPES.UNSUBSCRIBE,
      channel
    };
    
    this.send(message);
    this.emit(EVENTS.UNSUBSCRIBE, { channel });
  }
  
  /**
   * 发送消息到服务器
   * @param {Object|string} data 要发送的数据
   */
  send(data) {
    if (!this.isConnected) {
      this._log('未连接,无法发送消息', 'error');
      return;
    }
    
    const message = typeof data === 'string' ? data : JSON.stringify(data);
    this.socket.send(message);
  }
  
  /**
   * 发送心跳消息
   */
  sendHeartbeat() {
    this.send({
      type: MSG_TYPES.PING,
      timestamp: Date.now()
    });
  }
  
  /**
   * 重新连接
   */
  reconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    
    this.reconnectAttempts += 1;
    
    if (this.reconnectAttempts > this.config.reconnectAttempts) {
      this._log('超过最大重连次数,停止重连', 'error');
      this.emit(EVENTS.ERROR, new Error('重连失败: 超过最大重连次数'));
      return;
    }
    
    this._log(`尝试重连 (${this.reconnectAttempts}/${this.config.reconnectAttempts})...`);
    this.emit(EVENTS.RECONNECT_ATTEMPT, this.reconnectAttempts);
    
    this.reconnectTimer = setTimeout(() => {
      this.connect()
        .then(() => {
          this._log('重连成功');
          this.emit(EVENTS.RECONNECT, this.reconnectAttempts);
          this.reconnectAttempts = 0;
          
          // 重新订阅所有频道
          this.subscriptions.forEach((params, channel) => {
            this.subscribe(channel, params);
          });
        })
        .catch(error => {
          this._log(`重连失败: ${error.message}`, 'error');
          this.reconnect();
        });
    }, this.config.reconnectInterval);
  }
  
  /**
   * 添加事件监听器
   * @param {string} event 事件名称
   * @param {Function} callback 回调函数
   * @returns {WebSocketClient} this
   */
  on(event, callback) {
    if (!this.eventListeners[event]) {
      this.eventListeners[event] = [];
    }
    
    this.eventListeners[event].push(callback);
    return this;
  }
  
  /**
   * 移除事件监听器
   * @param {string} event 事件名称
   * @param {Function} callback 回调函数
   * @returns {WebSocketClient} this
   */
  off(event, callback) {
    if (!this.eventListeners[event]) {
      return this;
    }
    
    if (callback) {
      this.eventListeners[event] = this.eventListeners[event].filter(cb => cb !== callback);
    } else {
      delete this.eventListeners[event];
    }
    
    return this;
  }
  
  /**
   * 触发事件
   * @param {string} event 事件名称
   * @param {*} data 事件数据
   */
  emit(event, data) {
    if (!this.eventListeners[event]) {
      return;
    }
    
    this.eventListeners[event].forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        this._log(`事件处理器错误: ${error.message}`, 'error');
      }
    });
  }
  
  /**
   * WebSocket打开事件处理
   * @private
   */
  _onOpen(event) {
    this._log('WebSocket连接已建立');
    this.isConnected = true;
    this.reconnectAttempts = 0;
    
    // 启动心跳
    this._startHeartbeat();
    
    this.emit(EVENTS.OPEN, event);
  }
  
  /**
   * WebSocket关闭事件处理
   * @private
   */
  _onClose(event) {
    this._log(`WebSocket连接已关闭: ${event.code} ${event.reason}`);
    this.isConnected = false;
    
    // 停止心跳
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
    
    this.emit(EVENTS.CLOSE, event);
    
    // 非正常关闭时自动重连
    if (event.code !== 1000) {
      this.reconnect();
    }
  }
  
  /**
   * WebSocket错误事件处理
   * @private
   */
  _onError(error) {
    this._log(`WebSocket错误: ${error.message || '未知错误'}`, 'error');
    this.emit(EVENTS.ERROR, error);
  }
  
  /**
   * WebSocket消息事件处理
   * @private
   */
  _onMessage(event) {
    try {
      const message = JSON.parse(event.data);
      this._handleMessage(message);
    } catch (error) {
      this._log(`解析消息错误: ${error.message}`, 'error');
      this.emit(EVENTS.ERROR, new Error(`解析消息错误: ${error.message}`));
    }
  }
  
  /**
   * 处理收到的消息
   * @param {Object} message 收到的消息
   * @private
   */
  _handleMessage(message) {
    // 处理特定类型的消息
    if (message.type === MSG_TYPES.PONG) {
      // 心跳响应,不需特殊处理
      return;
    }
    
    // 发送收到的消息给监听器
    this.emit(EVENTS.MESSAGE, message);
  }
  
  /**
   * 启动心跳
   * @private
   */
  _startHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
    }
    
    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected) {
        this.sendHeartbeat();
      }
    }, this.config.heartbeatInterval);
  }
  
  /**
   * 记录日志
   * @param {string} message 日志消息
   * @param {string} level 日志级别
   * @private
   */
  _log(message, level = 'info') {
    if (!this.config.debug) {
      return;
    }
    
    const timestamp = new Date().toISOString();
    
    switch (level) {
      case 'error':
        console.error(`[WebSocketClient ${timestamp}] ${message}`);
        break;
      case 'warn':
        console.warn(`[WebSocketClient ${timestamp}] ${message}`);
        break;
      default:
        console.log(`[WebSocketClient ${timestamp}] ${message}`);
    }
  }
} 
 
