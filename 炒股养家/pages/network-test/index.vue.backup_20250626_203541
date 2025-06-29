<template>
  <view class="container">
    <view class="header">
      <text class="title">网络连接测试</text>
      <text class="subtitle">检测移动前端与后端的连接状态</text>
    </view>
    
    <!-- 环境信息 -->
    <view class="env-info">
      <view class="info-item">
        <text class="label">当前环境:</text>
        <text class="value" :class="envClass">{{ currentEnv }}</text>
      </view>
      <view class="info-item">
        <text class="label">API地址:</text>
        <text class="value">{{ apiUrl }}</text>
      </view>
      <view class="info-item">
        <text class="label">WebSocket地址:</text>
        <text class="value">{{ wsUrl }}</text>
      </view>
    </view>
    
    <!-- 测试按钮 -->
    <view class="test-buttons">
      <button class="test-btn" @click="testApiConnection" :disabled="testing">
        {{ testing ? '测试中...' : '测试API连接' }}
      </button>
      <button class="test-btn" @click="testWebSocketConnection" :disabled="wsConnecting">
        {{ wsConnecting ? '连接中...' : '测试WebSocket连接' }}
      </button>
      <button class="test-btn" @click="testAgentService" :disabled="agentTesting">
        {{ agentTesting ? '测试中...' : '测试Agent服务' }}
      </button>
    </view>
    
    <!-- 测试结果 -->
    <view class="test-results">
      <view class="result-section">
        <text class="section-title">API连接测试</text>
        <view class="result-item" :class="apiResult.status">
          <text class="result-status">{{ apiResult.status || '未测试' }}</text>
          <text class="result-message">{{ apiResult.message }}</text>
          <text class="result-time" v-if="apiResult.responseTime">响应时间: {{ apiResult.responseTime }}ms</text>
        </view>
      </view>
      
      <view class="result-section">
        <text class="section-title">WebSocket连接测试</text>
        <view class="result-item" :class="wsResult.status">
          <text class="result-status">{{ wsResult.status || '未测试' }}</text>
          <text class="result-message">{{ wsResult.message }}</text>
        </view>
      </view>
      
      <view class="result-section">
        <text class="section-title">Agent服务测试</text>
        <view class="result-item" :class="agentResult.status">
          <text class="result-status">{{ agentResult.status || '未测试' }}</text>
          <text class="result-message">{{ agentResult.message }}</text>
        </view>
      </view>
    </view>
    
    <!-- 详细日志 -->
    <view class="logs-section" v-if="logs.length > 0">
      <text class="section-title">详细日志</text>
      <scroll-view class="logs-container" scroll-y>
        <view class="log-item" v-for="(log, index) in logs" :key="index" :class="log.type">
          <text class="log-time">{{ log.time }}</text>
          <text class="log-message">{{ log.message }}</text>
        </view>
      </scroll-view>
    </view>
    
    <!-- 清除日志按钮 -->
    <view class="actions" v-if="logs.length > 0">
      <button class="clear-btn" @click="clearLogs">清除日志</button>
    </view>
  </view>
</template>

<script>
import env from '@/env';
import agentTradingService from '@/services/agentTradingService';

export default {
  data() {
    return {
      currentEnv: env.isProd ? '生产环境' : '开发环境',
      apiUrl: env.current.apiBaseUrl,
      wsUrl: env.current.wsUrl,
      
      testing: false,
      wsConnecting: false,
      agentTesting: false,
      
      apiResult: {},
      wsResult: {},
      agentResult: {},
      
      logs: [],
      ws: null
    };
  },
  computed: {
    envClass() {
      return env.isProd ? 'env-prod' : 'env-dev';
    }
  },
  methods: {
    // 添加日志
    addLog(message, type = 'info') {
      const now = new Date();
      const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
      
      this.logs.unshift({
        time,
        message,
        type
      });
      
      // 限制日志数量
      if (this.logs.length > 50) {
        this.logs = this.logs.slice(0, 50);
      }
    },
    
    // 测试API连接
    async testApiConnection() {
      this.testing = true;
      this.apiResult = {};
      
      try {
        this.addLog('开始测试API连接...', 'info');
        const startTime = Date.now();
        
        // 测试基础健康检查
        const response = await uni.request({
          url: `${this.apiUrl}/api/health`,
          method: 'GET',
          timeout: 10000
        });
        
        const responseTime = Date.now() - startTime;
        
        if (response.statusCode === 200) {
          this.apiResult = {
            status: 'success',
            message: 'API连接成功',
            responseTime
          };
          this.addLog(`API连接成功，响应时间: ${responseTime}ms`, 'success');
        } else {
          this.apiResult = {
            status: 'error',
            message: `API返回错误状态码: ${response.statusCode}`,
            responseTime
          };
          this.addLog(`API连接失败，状态码: ${response.statusCode}`, 'error');
        }
      } catch (error) {
        this.apiResult = {
          status: 'error',
          message: `连接失败: ${error.message || error.errMsg || '未知错误'}`
        };
        this.addLog(`API连接失败: ${error.message || error.errMsg}`, 'error');
      } finally {
        this.testing = false;
      }
    },
    
    // 测试WebSocket连接
    async testWebSocketConnection() {
      this.wsConnecting = true;
      this.wsResult = {};
      
      try {
        this.addLog('开始测试WebSocket连接...', 'info');
        
        // 关闭现有连接
        if (this.ws) {
          this.ws.close();
          this.ws = null;
        }
        
        // 创建新的WebSocket连接
        this.ws = new WebSocket(this.wsUrl);
        
        // 设置超时
        const timeout = setTimeout(() => {
          if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
            this.ws.close();
            this.wsResult = {
              status: 'error',
              message: 'WebSocket连接超时'
            };
            this.addLog('WebSocket连接超时', 'error');
            this.wsConnecting = false;
          }
        }, 10000);
        
        this.ws.onopen = () => {
          clearTimeout(timeout);
          this.wsResult = {
            status: 'success',
            message: 'WebSocket连接成功'
          };
          this.addLog('WebSocket连接成功', 'success');
          this.wsConnecting = false;
          
          // 发送测试消息
          this.ws.send(JSON.stringify({
            type: 'ping',
            timestamp: Date.now()
          }));
        };
        
        this.ws.onmessage = (event) => {
          this.addLog(`收到WebSocket消息: ${event.data}`, 'info');
        };
        
        this.ws.onerror = (error) => {
          clearTimeout(timeout);
          this.wsResult = {
            status: 'error',
            message: 'WebSocket连接错误'
          };
          this.addLog(`WebSocket连接错误: ${JSON.stringify(error)}`, 'error');
          this.wsConnecting = false;
        };
        
        this.ws.onclose = (event) => {
          if (event.code !== 1000) {
            this.addLog(`WebSocket连接关闭: ${event.code} - ${event.reason}`, 'warning');
          }
        };
        
      } catch (error) {
        this.wsResult = {
          status: 'error',
          message: `WebSocket连接失败: ${error.message}`
        };
        this.addLog(`WebSocket连接失败: ${error.message}`, 'error');
        this.wsConnecting = false;
      }
    },
    
    // 测试Agent服务
    async testAgentService() {
      this.agentTesting = true;
      this.agentResult = {};
      
      try {
        this.addLog('开始测试Agent服务...', 'info');
        
        // 测试Agent系统状态
        const result = await agentTradingService.getSystemStatus();
        
        if (result && result.success) {
          this.agentResult = {
            status: 'success',
            message: 'Agent服务连接成功'
          };
          this.addLog('Agent服务连接成功', 'success');
          this.addLog(`Agent状态: ${JSON.stringify(result.data)}`, 'info');
        } else {
          this.agentResult = {
            status: 'warning',
            message: 'Agent服务响应异常'
          };
          this.addLog('Agent服务响应异常', 'warning');
        }
      } catch (error) {
        this.agentResult = {
          status: 'error',
          message: `Agent服务连接失败: ${error.message}`
        };
        this.addLog(`Agent服务连接失败: ${error.message}`, 'error');
      } finally {
        this.agentTesting = false;
      }
    },
    
    // 清除日志
    clearLogs() {
      this.logs = [];
    }
  },
  
  onUnload() {
    // 页面卸载时关闭WebSocket连接
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
</script>

<style scoped>
.container {
  padding: 30rpx;
  background-color: #141414;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 40rpx;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  color: #ffffff;
  display: block;
  margin-bottom: 10rpx;
}

.subtitle {
  font-size: 24rpx;
  color: #999999;
}

/* 环境信息 */
.env-info {
  background-color: #222222;
  border-radius: 12rpx;
  padding: 20rpx;
  margin-bottom: 30rpx;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #333333;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  font-size: 26rpx;
  color: #cccccc;
}

.value {
  font-size: 24rpx;
  color: #ffffff;
  max-width: 60%;
  text-align: right;
  word-break: break-all;
}

.env-prod {
  color: #ff4757;
  font-weight: bold;
}

.env-dev {
  color: #4c8dff;
}

/* 测试按钮 */
.test-buttons {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-bottom: 40rpx;
}

.test-btn {
  background-color: #4c8dff;
  color: #ffffff;
  border: none;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 28rpx;
  font-weight: bold;
}

.test-btn:disabled {
  opacity: 0.5;
}

/* 测试结果 */
.test-results {
  margin-bottom: 40rpx;
}

.result-section {
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #ffffff;
  display: block;
  margin-bottom: 15rpx;
}

.result-item {
  background-color: #222222;
  border-radius: 8rpx;
  padding: 20rpx;
  border-left: 4rpx solid #666666;
}

.result-item.success {
  border-left-color: #4caf50;
}

.result-item.error {
  border-left-color: #f44336;
}

.result-item.warning {
  border-left-color: #ff9800;
}

.result-status {
  font-size: 24rpx;
  font-weight: bold;
  color: #ffffff;
  display: block;
  margin-bottom: 8rpx;
}

.result-message {
  font-size: 24rpx;
  color: #cccccc;
  display: block;
  margin-bottom: 8rpx;
}

.result-time {
  font-size: 22rpx;
  color: #999999;
}

/* 日志 */
.logs-section {
  margin-bottom: 30rpx;
}

.logs-container {
  height: 400rpx;
  background-color: #000000;
  border-radius: 8rpx;
  padding: 15rpx;
}

.log-item {
  margin-bottom: 10rpx;
  padding: 8rpx;
  border-radius: 4rpx;
}

.log-item.info {
  background-color: rgba(76, 141, 255, 0.1);
}

.log-item.success {
  background-color: rgba(76, 175, 80, 0.1);
}

.log-item.error {
  background-color: rgba(244, 67, 54, 0.1);
}

.log-item.warning {
  background-color: rgba(255, 152, 0, 0.1);
}

.log-time {
  font-size: 20rpx;
  color: #999999;
  margin-right: 15rpx;
}

.log-message {
  font-size: 22rpx;
  color: #ffffff;
}

/* 操作按钮 */
.actions {
  text-align: center;
}

.clear-btn {
  background-color: #666666;
  color: #ffffff;
  border: none;
  border-radius: 8rpx;
  padding: 15rpx 30rpx;
  font-size: 24rpx;
}
</style>
