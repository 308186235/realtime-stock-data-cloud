<template>
  <view class="connection-status-container">
    <!-- 连接状态指示器 -->
    <view class="status-indicator" :class="connectionStatusClass" @click="toggleDetails">
      <view class="status-dot" :class="connectionStatusClass"></view>
      <text class="status-text">{{ connectionStatusText }}</text>
      <text class="status-icon">{{ showDetails ? '▼' : '▶' }}</text>
    </view>
    
    <!-- 详细信息面板 -->
    <view v-if="showDetails" class="details-panel">
      <view class="detail-item">
        <text class="detail-label">后端地址:</text>
        <text class="detail-value">{{ apiBaseUrl }}</text>
      </view>
      
      <view class="detail-item">
        <text class="detail-label">连接状态:</text>
        <text class="detail-value" :class="connectionStatusClass">{{ connectionStatusText }}</text>
      </view>
      
      <view class="detail-item" v-if="lastCheckTime">
        <text class="detail-label">最后检测:</text>
        <text class="detail-value">{{ formatTime(lastCheckTime) }}</text>
      </view>
      
      <view class="detail-item" v-if="responseTime">
        <text class="detail-label">响应时间:</text>
        <text class="detail-value">{{ responseTime }}ms</text>
      </view>
      
      <view class="detail-item" v-if="errorMessage">
        <text class="detail-label">错误信息:</text>
        <text class="detail-value error">{{ errorMessage }}</text>
      </view>
      
      <!-- 操作按钮 -->
      <view class="action-buttons">
        <button class="test-btn" @click="testConnection" :disabled="isTesting">
          {{ isTesting ? '检测中...' : '重新检测' }}
        </button>
        <button class="settings-btn" @click="openSettings">设置</button>
      </view>
    </view>
  </view>
</template>

<script>
import env from '@/env.js'

export default {
  name: 'BackendConnectionStatus',
  data() {
    return {
      // 连接状态
      isConnected: false,
      isTesting: false,
      showDetails: false,
      
      // 连接信息
      apiBaseUrl: '',
      lastCheckTime: null,
      responseTime: null,
      errorMessage: '',
      
      // 自动检测定时器
      checkInterval: null,
      checkIntervalTime: 30000, // 30秒检测一次
    }
  },
  
  computed: {
    connectionStatusClass() {
      if (this.isTesting) return 'testing';
      return this.isConnected ? 'connected' : 'disconnected';
    },
    
    connectionStatusText() {
      if (this.isTesting) return '检测中...';
      return this.isConnected ? '后端已连接' : '后端未连接';
    }
  },
  
  mounted() {
    this.initConnection();
    this.startAutoCheck();
  },
  
  beforeDestroy() {
    this.stopAutoCheck();
  },
  
  methods: {
    // 初始化连接
    async initConnection() {
      // 从配置中获取API地址
      this.apiBaseUrl = this.getApiBaseUrl();
      await this.testConnection();
    },
    
    // 获取API基础地址
    getApiBaseUrl() {
      // 从本地存储获取用户自定义配置
      try {
        const config = uni.getStorageSync('app_config');
        if (config && config.apiBaseUrl) {
          return config.apiBaseUrl;
        }
      } catch (e) {
        console.error('获取配置失败:', e);
      }

      // 使用环境配置的默认地址
      return env.apiBaseUrl || 'https://trading-system-api.netlify.app';
    },
    
    // 测试连接
    async testConnection() {
      this.isTesting = true;
      this.errorMessage = '';
      
      try {
        const startTime = Date.now();
        
        // 测试健康检查接口
        const response = await uni.request({
          url: `${this.apiBaseUrl}/api/health`,
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
          this.showConnectionToast('后端连接成功', 'success');
        } else {
          this.isConnected = false;
          this.errorMessage = `HTTP ${response.statusCode}`;
          this.showConnectionToast('后端连接失败', 'error');
        }
        
      } catch (error) {
        this.isConnected = false;
        this.responseTime = null;
        this.lastCheckTime = new Date();
        this.errorMessage = error.errMsg || error.message || '连接超时';
        this.showConnectionToast('后端连接失败', 'error');
      } finally {
        this.isTesting = false;
      }
    },
    
    // 显示连接状态提示
    showConnectionToast(message, type) {
      uni.showToast({
        title: message,
        icon: type === 'success' ? 'success' : 'none',
        duration: 2000
      });
    },
    
    // 开始自动检测
    startAutoCheck() {
      this.checkInterval = setInterval(() => {
        this.testConnection();
      }, this.checkIntervalTime);
    },
    
    // 停止自动检测
    stopAutoCheck() {
      if (this.checkInterval) {
        clearInterval(this.checkInterval);
        this.checkInterval = null;
      }
    },
    
    // 切换详情显示
    toggleDetails() {
      this.showDetails = !this.showDetails;
    },
    
    // 格式化时间
    formatTime(date) {
      if (!date) return '';
      return date.toLocaleTimeString();
    },
    
    // 打开设置
    openSettings() {
      uni.navigateTo({
        url: '/pages/settings/network'
      });
    }
  }
}
</script>

<style scoped>
.connection-status-container {
  margin: 10px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.status-indicator {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
}

.status-dot.connected {
  background-color: #52c41a;
  box-shadow: 0 0 8px rgba(82, 196, 26, 0.5);
}

.status-dot.disconnected {
  background-color: #ff4d4f;
  box-shadow: 0 0 8px rgba(255, 77, 79, 0.5);
}

.status-dot.testing {
  background-color: #1890ff;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.status-text {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
}

.status-text.connected {
  color: #52c41a;
}

.status-text.disconnected {
  color: #ff4d4f;
}

.status-text.testing {
  color: #1890ff;
}

.status-icon {
  font-size: 12px;
  color: #999;
}

.details-panel {
  border-top: 1px solid #f0f0f0;
  padding: 16px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.detail-label {
  font-size: 12px;
  color: #666;
}

.detail-value {
  font-size: 12px;
  color: #333;
}

.detail-value.connected {
  color: #52c41a;
}

.detail-value.disconnected {
  color: #ff4d4f;
}

.detail-value.error {
  color: #ff4d4f;
}

.action-buttons {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.test-btn, .settings-btn {
  flex: 1;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 12px;
  border: none;
}

.test-btn {
  background-color: #1890ff;
  color: white;
}

.test-btn:disabled {
  background-color: #d9d9d9;
  color: #999;
}

.settings-btn {
  background-color: #f5f5f5;
  color: #333;
}
</style>
