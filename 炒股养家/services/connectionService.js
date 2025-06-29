/**
 * 后端连接服务
 * 负责管理与后端服务器的连接状态检测
 */

import env from '@/env.js';

class ConnectionService {
  constructor() {
    this.isConnected = false;
    this.lastCheckTime = null;
    this.responseTime = null;
    this.statusListeners = [];
    this.autoCheckTimer = null;
    this.checkInterval = 30000; // 30秒检测一次
    
    // 启动自动检测
    this.startAutoCheck();
  }
  
  /**
   * 获取服务器URL
   */
  getServerUrl() {
    return env.current.apiBaseUrl;
  }
  
  /**
   * 测试连接
   */
  async testConnection() {
    const startTime = Date.now();
    
    try {
      const response = await uni.request({
        url: `${this.getServerUrl()}/api/test`,
        method: 'GET',
        timeout: 10000,
        header: {
          'Content-Type': 'application/json'
        }
      });
      
      const endTime = Date.now();
      this.responseTime = endTime - startTime;
      this.lastCheckTime = new Date();
      
      if (response.statusCode === 200) {
        this.isConnected = true;
        this.notifyStatusChange('connected');
        
        return {
          success: true,
          data: response.data,
          responseTime: this.responseTime
        };
      } else {
        this.isConnected = false;
        this.notifyStatusChange('disconnected');
        
        return {
          success: false,
          error: `HTTP ${response.statusCode}: ${response.data?.message || '连接失败'}`
        };
      }
      
    } catch (error) {
      console.error('连接测试失败:', error);
      
      this.isConnected = false;
      this.responseTime = null;
      this.lastCheckTime = new Date();
      this.notifyStatusChange('error');
      
      return {
        success: false,
        error: this.getErrorMessage(error)
      };
    }
  }
  
  /**
   * 获取错误信息
   */
  getErrorMessage(error) {
    if (error.errMsg) {
      if (error.errMsg.includes('timeout')) {
        return '连接超时';
      } else if (error.errMsg.includes('fail')) {
        return '网络连接失败';
      } else if (error.errMsg.includes('abort')) {
        return '请求被中断';
      }
      return error.errMsg;
    }
    
    return error.message || '未知错误';
  }
  
  /**
   * 获取连接状态
   */
  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      lastCheckTime: this.lastCheckTime,
      responseTime: this.responseTime,
      serverUrl: this.getServerUrl()
    };
  }
  
  /**
   * 监听状态变化
   */
  onStatusChange(callback) {
    if (typeof callback === 'function') {
      this.statusListeners.push(callback);
    }
  }
  
  /**
   * 移除状态监听
   */
  offStatusChange(callback) {
    const index = this.statusListeners.indexOf(callback);
    if (index > -1) {
      this.statusListeners.splice(index, 1);
    }
  }
  
  /**
   * 通知状态变化
   */
  notifyStatusChange(status) {
    this.statusListeners.forEach(callback => {
      try {
        callback(status);
      } catch (error) {
        console.error('状态监听回调执行失败:', error);
      }
    });
  }
  
  /**
   * 启动自动检测
   */
  startAutoCheck() {
    if (this.autoCheckTimer) {
      clearInterval(this.autoCheckTimer);
    }
    
    // 立即执行一次检测
    this.testConnection();
    
    // 设置定时检测
    this.autoCheckTimer = setInterval(() => {
      this.testConnection();
    }, this.checkInterval);
  }
  
  /**
   * 停止自动检测
   */
  stopAutoCheck() {
    if (this.autoCheckTimer) {
      clearInterval(this.autoCheckTimer);
      this.autoCheckTimer = null;
    }
  }
  
  /**
   * 设置检测间隔
   */
  setCheckInterval(interval) {
    this.checkInterval = interval;
    if (this.autoCheckTimer) {
      this.startAutoCheck(); // 重新启动以应用新间隔
    }
  }
  
  /**
   * 手动刷新连接状态
   */
  async refresh() {
    return await this.testConnection();
  }
  
  /**
   * 销毁服务
   */
  destroy() {
    this.stopAutoCheck();
    this.statusListeners = [];
  }
}

// 创建单例实例
const connectionService = new ConnectionService();

export { connectionService };
export default connectionService;
