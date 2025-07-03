/**
 * 前端API客户端
 * 统一管理与后端和本地API的通信
 */

import config from './frontend-config-production.js';

// HTTP客户端基类
class HTTPClient {
  constructor(baseURL, options = {}) {
    this.baseURL = baseURL;
    this.timeout = options.timeout || 30000;
    this.headers = options.headers || {};
    this.retryAttempts = options.retryAttempts || 3;
    this.retryDelay = options.retryDelay || 1000;
  }
  
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const requestOptions = {
      method: options.method || 'GET',
      headers: { ...this.headers, ...options.headers },
      ...options
    };
    
    if (options.data) {
      requestOptions.body = JSON.stringify(options.data);
    }
    
    let lastError;
    
    for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
      try {
        console.log(`🔄 API请求 (尝试 ${attempt}/${this.retryAttempts}): ${options.method || 'GET'} ${url}`);
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        
        const response = await fetch(url, {
          ...requestOptions,
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log(`✅ API请求成功: ${url}`);
        return data;
        
      } catch (error) {
        lastError = error;
        console.error(`❌ API请求失败 (尝试 ${attempt}/${this.retryAttempts}): ${error.message}`);
        
        if (attempt < this.retryAttempts) {
          console.log(`⏳ ${this.retryDelay}ms后重试...`);
          await new Promise(resolve => setTimeout(resolve, this.retryDelay));
        }
      }
    }
    
    throw lastError;
  }
  
  async get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }
  
  async post(endpoint, data, options = {}) {
    return this.request(endpoint, { ...options, method: 'POST', data });
  }
  
  async put(endpoint, data, options = {}) {
    return this.request(endpoint, { ...options, method: 'PUT', data });
  }
  
  async delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }
}

// 云端API客户端
class CloudAPIClient extends HTTPClient {
  constructor() {
    super(config.cloud.url, {
      timeout: config.cloud.timeout,
      headers: config.client.headers,
      retryAttempts: config.client.retry.attempts,
      retryDelay: config.client.retry.delay
    });
  }
  
  // 健康检查
  async healthCheck() {
    return this.get(config.cloud.endpoints.health);
  }
  
  // AI分析
  async requestAnalysis(data) {
    return this.post(config.cloud.endpoints.analysis, data);
  }
  
  // AI决策
  async requestDecision(data) {
    return this.post(config.cloud.endpoints.decision, data);
  }
  
  // 执行交易
  async executeTrading(data) {
    return this.post(config.cloud.endpoints.execute, data);
  }
  
  // 本地API代理
  async proxyToLocal(endpoint, method = 'GET', data = null) {
    const proxyEndpoint = `${config.cloud.endpoints.localProxy}${endpoint}`;
    if (method === 'GET') {
      return this.get(proxyEndpoint);
    } else {
      return this.post(proxyEndpoint, data);
    }
  }
}

// 本地API客户端
class LocalAPIClient extends HTTPClient {
  constructor() {
    super(config.local.url, {
      timeout: config.local.timeout,
      headers: config.client.headers,
      retryAttempts: config.client.retry.attempts,
      retryDelay: config.client.retry.delay
    });
  }
  
  // 健康检查
  async healthCheck() {
    return this.get(config.local.endpoints.health);
  }
  
  // 获取余额
  async getBalance() {
    return this.get(config.local.endpoints.balance);
  }
  
  // 导出数据
  async exportData(type = 'all') {
    return this.post(config.local.endpoints.export, { type });
  }
  
  // 执行交易
  async executeTrade(action, code, quantity, price = '市价') {
    return this.post(config.local.endpoints.trade, {
      action,
      code,
      quantity,
      price
    });
  }
  
  // 连接云端
  async connectToCloud(cloudUrl) {
    return this.post(config.local.endpoints.connectCloud, { cloud_url: cloudUrl });
  }
  
  // 获取云端连接状态
  async getCloudStatus() {
    return this.get(config.local.endpoints.cloudStatus);
  }
}

// WebSocket管理器
class WebSocketManager {
  constructor() {
    this.ws = null;
    this.url = config.websocket.url;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = config.websocket.reconnect.maxAttempts;
    this.reconnectDelay = config.websocket.reconnect.delay;
    this.isConnected = false;
    this.messageHandlers = new Map();
    this.heartbeatInterval = null;
  }
  
  // 连接WebSocket
  connect() {
    return new Promise((resolve, reject) => {
      try {
        console.log(`🔌 连接WebSocket: ${this.url}`);
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
          console.log('✅ WebSocket连接成功');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          this.handleMessage(event.data);
        };
        
        this.ws.onclose = () => {
          console.log('❌ WebSocket连接关闭');
          this.isConnected = false;
          this.stopHeartbeat();
          this.handleReconnect();
        };
        
        this.ws.onerror = (error) => {
          console.error('❌ WebSocket错误:', error);
          reject(error);
        };
        
      } catch (error) {
        console.error('❌ WebSocket连接失败:', error);
        reject(error);
      }
    });
  }
  
  // 发送消息
  send(message) {
    if (this.isConnected && this.ws) {
      const data = JSON.stringify(message);
      this.ws.send(data);
      console.log('📤 WebSocket发送消息:', message.type);
    } else {
      console.error('❌ WebSocket未连接，无法发送消息');
    }
  }
  
  // 处理消息
  handleMessage(data) {
    try {
      const message = JSON.parse(data);
      console.log('📨 WebSocket收到消息:', message.type);
      
      const handler = this.messageHandlers.get(message.type);
      if (handler) {
        handler(message);
      } else {
        console.log('⚠️ 未找到消息处理器:', message.type);
      }
    } catch (error) {
      console.error('❌ WebSocket消息解析失败:', error);
    }
  }
  
  // 注册消息处理器
  onMessage(type, handler) {
    this.messageHandlers.set(type, handler);
  }
  
  // 处理重连
  handleReconnect() {
    if (config.websocket.reconnect.enabled && 
        this.reconnectAttempts < this.maxReconnectAttempts) {
      
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(config.websocket.reconnect.backoff, this.reconnectAttempts - 1);
      
      console.log(`🔄 ${delay}ms后尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect().catch(error => {
          console.error('❌ WebSocket重连失败:', error);
        });
      }, delay);
    } else {
      console.error('❌ WebSocket重连次数已达上限');
    }
  }
  
  // 开始心跳
  startHeartbeat() {
    if (config.websocket.heartbeat.enabled) {
      this.heartbeatInterval = setInterval(() => {
        this.send({
          type: 'heartbeat',
          timestamp: new Date().toISOString()
        });
      }, config.websocket.heartbeat.interval);
    }
  }
  
  // 停止心跳
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
  
  // 断开连接
  disconnect() {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
  }
}

// 统一API管理器
class APIManager {
  constructor() {
    this.cloud = new CloudAPIClient();
    this.local = new LocalAPIClient();
    this.websocket = new WebSocketManager();
    this.connectionStatus = {
      cloud: false,
      local: false,
      websocket: false
    };
  }
  
  // 检查所有连接
  async checkAllConnections() {
    console.log('🔍 检查所有连接状态...');
    
    // 检查云端连接
    try {
      await this.cloud.healthCheck();
      this.connectionStatus.cloud = true;
      console.log('✅ 云端API连接正常');
    } catch (error) {
      this.connectionStatus.cloud = false;
      console.error('❌ 云端API连接失败:', error.message);
    }
    
    // 检查本地连接
    try {
      await this.local.healthCheck();
      this.connectionStatus.local = true;
      console.log('✅ 本地API连接正常');
    } catch (error) {
      this.connectionStatus.local = false;
      console.error('❌ 本地API连接失败:', error.message);
    }
    
    // 检查WebSocket连接
    if (!this.websocket.isConnected) {
      try {
        await this.websocket.connect();
        this.connectionStatus.websocket = true;
      } catch (error) {
        this.connectionStatus.websocket = false;
        console.error('❌ WebSocket连接失败:', error.message);
      }
    } else {
      this.connectionStatus.websocket = true;
    }
    
    return this.connectionStatus;
  }
  
  // 获取连接状态
  getConnectionStatus() {
    return this.connectionStatus;
  }
}

// 创建全局API管理器实例
const apiManager = new APIManager();

// 导出
export {
  CloudAPIClient,
  LocalAPIClient,
  WebSocketManager,
  APIManager,
  apiManager
};

export default apiManager;
