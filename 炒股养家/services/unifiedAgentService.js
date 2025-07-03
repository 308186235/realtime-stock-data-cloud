/**
 * 统一Agent服务
 * 集成云端API、本地API、WebSocket连接和状态管理
 */

class UnifiedAgentService {
  constructor() {
    // API配置
    this.cloudApiUrl = 'https://api.aigupiao.me';
    this.localApiUrl = 'https://api.aigupiao.me';
    this.websocketUrl = 'wss://api.aigupiao.me/ws';
    
    // 连接状态
    this.cloudConnected = false;
    this.localConnected = false;
    this.websocketConnected = false;
    
    // WebSocket连接
    this.websocket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectInterval = 5000;
    
    // 事件监听器
    this.eventListeners = {};
    
    // 初始化
    this.init();
  }
  
  /**
   * 初始化服务
   */
  async init() {
    console.log('🚀 初始化统一Agent服务');
    
    // 检查连接状态
    await this.checkConnections();
    
    // 建立WebSocket连接
    this.connectWebSocket();
    
    // 定期检查连接状态
    setInterval(() => {
      this.checkConnections();
    }, 30000); // 30秒检查一次
  }
  
  /**
   * 检查所有连接状态
   */
  async checkConnections() {
    try {
      // 检查云端连接
      const cloudStatus = await this.request('GET', '/health', {}, 'cloud');
      this.cloudConnected = cloudStatus.success;
      
      // 检查本地连接
      const localStatus = await this.request('GET', '/status', {}, 'local');
      this.localConnected = localStatus.success;
      
      console.log(`📊 连接状态 - 云端: ${this.cloudConnected ? '✅' : '❌'}, 本地: ${this.localConnected ? '✅' : '❌'}, WebSocket: ${this.websocketConnected ? '✅' : '❌'}`);
      
      // 触发状态更新事件
      this.emit('connectionStatusChanged', {
        cloud: this.cloudConnected,
        local: this.localConnected,
        websocket: this.websocketConnected
      });
      
    } catch (error) {
      console.error('❌ 检查连接状态失败:', error);
    }
  }
  
  /**
   * 建立WebSocket连接
   */
  connectWebSocket() {
    try {
      console.log('🔗 尝试建立WebSocket连接');

      // 暂时禁用WebSocket连接，避免错误
      console.log('⚠️ WebSocket功能暂时禁用，使用HTTP轮询替代');
      this.websocketConnected = false;

      // 使用HTTP轮询替代WebSocket
      this.startHttpPolling();
      return;
      
      this.websocket.onMessage((message) => {
        try {
          const data = JSON.parse(message.data);
          this.handleWebSocketMessage(data);
        } catch (error) {
          console.error('❌ 解析WebSocket消息失败:', error);
        }
      });
      
      this.websocket.onClose(() => {
        console.log('🔌 WebSocket连接关闭');
        this.websocketConnected = false;
        this.emit('websocketDisconnected');
        
        // 自动重连
        this.reconnectWebSocket();
      });
      
      this.websocket.onError((error) => {
        console.error('❌ WebSocket连接错误:', error);
        this.websocketConnected = false;
      });
      
    } catch (error) {
      console.error('❌ 建立WebSocket连接失败:', error);
    }
  }

  /**
   * 启动HTTP轮询替代WebSocket
   */
  startHttpPolling() {
    console.log('🔄 启动HTTP轮询');

    // 每30秒轮询一次状态
    this.pollingInterval = setInterval(async () => {
      try {
        const response = await uni.request({
          url: `${this.cloudApiUrl}/api/agent/status`,
          method: 'GET',
          timeout: 10000
        });

        if (response.statusCode === 200) {
          console.log('📡 HTTP轮询状态正常');
        }
      } catch (error) {
        console.log('⚠️ HTTP轮询失败:', error.message);
      }
    }, 30000);
  }
  
  /**
   * WebSocket重连
   */
  reconnectWebSocket() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ 达到最大重连次数，停止重连');
      return;
    }
    
    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectInterval * this.reconnectAttempts, 30000);
    
    console.log(`⏳ ${delay/1000}秒后重连WebSocket (第${this.reconnectAttempts}次)`);
    
    setTimeout(() => {
      this.connectWebSocket();
    }, delay);
  }
  
  /**
   * 发送WebSocket消息
   */
  sendWebSocketMessage(message) {
    if (this.websocket && this.websocketConnected) {
      this.websocket.send({
        data: JSON.stringify(message)
      });
    } else {
      console.warn('⚠️ WebSocket未连接，无法发送消息');
    }
  }
  
  /**
   * 处理WebSocket消息
   */
  handleWebSocketMessage(data) {
    console.log('📨 收到WebSocket消息:', data);
    
    const messageType = data.type;
    
    switch (messageType) {
      case 'agent_decision':
        this.emit('agentDecision', data);
        break;
      case 'trade_result':
        this.emit('tradeResult', data);
        break;
      case 'system_status':
        this.emit('systemStatus', data);
        break;
      case 'real_time_data':
        this.emit('realTimeData', data);
        break;
      default:
        console.log('📋 未处理的消息类型:', messageType);
    }
  }
  
  /**
   * 统一请求方法
   */
  async request(method, endpoint, data = {}, target = 'cloud') {
    const baseUrl = target === 'cloud' ? this.cloudApiUrl : this.localApiUrl;
    const url = `${baseUrl}${endpoint}`;
    
    try {
      const options = {
        url,
        method: method.toUpperCase(),
        header: {
          'Content-Type': 'application/json'
        }
      };
      
      if (method.toUpperCase() !== 'GET' && Object.keys(data).length > 0) {
        options.data = data;
      }
      
      const response = await uni.request(options);
      
      if (response.statusCode === 200) {
        return {
          success: true,
          data: response.data
        };
      } else {
        throw new Error(`HTTP ${response.statusCode}: ${response.data?.message || '请求失败'}`);
      }
      
    } catch (error) {
      console.error(`❌ ${target}请求失败:`, error);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * 获取系统完整状态
   */
  async getSystemStatus() {
    try {
      const cloudStatus = await this.request('GET', '/config/status', {}, 'cloud');
      const localStatus = await this.request('GET', '/status', {}, 'local');
      
      return {
        success: true,
        cloud: cloudStatus.data,
        local: localStatus.data,
        connections: {
          cloud: this.cloudConnected,
          local: this.localConnected,
          websocket: this.websocketConnected
        },
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('❌ 获取系统状态失败:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * 发送交易命令
   */
  async sendTradeCommand(command) {
    try {
      console.log('💰 发送交易命令:', command);
      
      // 优先通过云端API发送到本地
      const result = await this.request('POST', '/cloud-local/trade', command, 'cloud');
      
      if (!result.success) {
        // 如果云端失败，尝试直接发送到本地
        console.log('⚠️ 云端发送失败，尝试直接发送到本地');
        return await this.request('POST', '/trade', command, 'local');
      }
      
      return result;
    } catch (error) {
      console.error('❌ 发送交易命令失败:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * 获取投资组合
   */
  async getPortfolio() {
    try {
      // 优先从云端获取
      const cloudResult = await this.request('GET', '/cloud-local/portfolio', {}, 'cloud');
      
      if (!cloudResult.success) {
        // 如果云端失败，直接从本地获取
        return await this.request('GET', '/portfolio', {}, 'local');
      }
      
      return cloudResult;
    } catch (error) {
      console.error('❌ 获取投资组合失败:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * 导出数据
   */
  async exportData(dataType = 'all') {
    try {
      const command = { data_type: dataType };
      
      // 优先通过云端导出
      const result = await this.request('POST', '/cloud-local/export', command, 'cloud');
      
      if (!result.success) {
        // 如果云端失败，直接从本地导出
        return await this.request('POST', '/export', command, 'local');
      }
      
      return result;
    } catch (error) {
      console.error('❌ 导出数据失败:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * 配置管理
   */
  async updateConfig(config) {
    return await this.request('POST', '/config', config, 'cloud');
  }
  
  async getConfig() {
    return await this.request('GET', '/config', {}, 'cloud');
  }
  
  async toggleBeijingExchange(enabled) {
    return await this.request('POST', '/config/beijing-exchange', { enabled }, 'cloud');
  }
  
  /**
   * 事件监听
   */
  on(event, callback) {
    if (!this.eventListeners[event]) {
      this.eventListeners[event] = [];
    }
    this.eventListeners[event].push(callback);
  }
  
  off(event, callback) {
    if (this.eventListeners[event]) {
      const index = this.eventListeners[event].indexOf(callback);
      if (index > -1) {
        this.eventListeners[event].splice(index, 1);
      }
    }
  }
  
  emit(event, data) {
    if (this.eventListeners[event]) {
      this.eventListeners[event].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`❌ 事件回调执行失败 (${event}):`, error);
        }
      });
    }
  }
  
  /**
   * 销毁服务
   */
  destroy() {
    console.log('🛑 销毁统一Agent服务');
    
    if (this.websocket) {
      this.websocket.close();
    }
    
    this.eventListeners = {};
  }
}

// 创建全局实例
const unifiedAgentService = new UnifiedAgentService();

// 导出
export default unifiedAgentService;
