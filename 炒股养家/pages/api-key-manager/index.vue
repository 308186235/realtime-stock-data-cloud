<template>
  <view class="container">
    <view class="header">
      <text class="title">API Key 管理</text>
      <text class="subtitle">管理股票数据API Key，支持快速切换</text>
    </view>

    <!-- 统计信息 -->
    <view class="stats-section">
      <view class="stat-card">
        <text class="stat-number">{{ statistics.total }}</text>
        <text class="stat-label">总数</text>
      </view>
      <view class="stat-card active">
        <text class="stat-number">{{ statistics.active }}</text>
        <text class="stat-label">活跃</text>
      </view>
      <view class="stat-card error">
        <text class="stat-number">{{ statistics.error }}</text>
        <text class="stat-label">错误</text>
      </view>
      <view class="stat-card disabled">
        <text class="stat-number">{{ statistics.disabled }}</text>
        <text class="stat-label">禁用</text>
      </view>
    </view>

    <!-- 当前使用的API Key -->
    <view class="current-key-section">
      <view class="section-title">当前API Key</view>
      <view class="current-key-card">
        <view class="key-info">
          <text class="key-name">{{ currentKey?.name || '未选择' }}</text>
          <text class="key-value">{{ currentKey?.key || 'N/A' }}</text>
        </view>
        <view class="key-actions">
          <button class="action-btn switch" @click="quickSwitch">快速切换</button>
          <button class="action-btn test" @click="testCurrentKey">测试</button>
        </view>
      </view>
    </view>

    <!-- API Key列表 -->
    <view class="keys-section">
      <view class="section-header">
        <text class="section-title">API Key 列表</text>
        <button class="add-btn" @click="showAddDialog">+ 添加</button>
      </view>
      
      <view v-for="(key, index) in apiKeys" :key="key.id" class="key-item">
        <view class="key-header">
          <view class="key-basic-info">
            <text class="key-name">{{ key.name }}</text>
            <text :class="['key-status', key.status]">{{ getStatusText(key.status) }}</text>
          </view>
          <view class="key-actions">
            <button v-if="key.status !== 'active'" class="action-btn activate" @click="activateKey(key.id)">
              激活
            </button>
            <button class="action-btn test" @click="testKey(key.id)">测试</button>
            <button class="action-btn delete" @click="deleteKey(key.id)">删除</button>
          </view>
        </view>
        
        <view class="key-details">
          <text class="key-value">{{ key.key }}</text>
          <view class="key-stats">
            <text class="stat-item">错误: {{ key.errorCount }}/{{ key.maxErrors }}</text>
            <text class="stat-item">最后使用: {{ formatTime(key.lastUsed) }}</text>
          </view>
        </view>
        
        <view v-if="key.lastError" class="key-error">
          <text class="error-text">{{ key.lastError.message }}</text>
          <text class="error-time">{{ formatTime(key.lastError.timestamp) }}</text>
        </view>
      </view>
    </view>

    <!-- 批量操作 -->
    <view class="batch-section">
      <view class="section-title">批量操作</view>
      <view class="batch-actions">
        <button class="batch-btn" @click="testAllKeys">测试所有</button>
        <button class="batch-btn" @click="resetAllStatus">重置状态</button>
        <button class="batch-btn" @click="exportConfig">导出配置</button>
        <button class="batch-btn" @click="showImportDialog">导入配置</button>
      </view>
    </view>

    <!-- 添加API Key对话框 -->
    <view v-if="showAdd" class="dialog-overlay" @click="hideAddDialog">
      <view class="dialog" @click.stop>
        <view class="dialog-header">
          <text class="dialog-title">添加API Key</text>
          <text class="close-btn" @click="hideAddDialog">×</text>
        </view>
        <view class="dialog-content">
          <view class="input-group">
            <text class="input-label">名称</text>
            <input class="input" v-model="newKey.name" placeholder="API Key名称" />
          </view>
          <view class="input-group">
            <text class="input-label">API Key</text>
            <input class="input" v-model="newKey.key" placeholder="输入API Key" />
          </view>
          <view class="input-group">
            <text class="input-label">描述</text>
            <input class="input" v-model="newKey.description" placeholder="可选描述" />
          </view>
          <view class="input-group">
            <text class="input-label">最大错误次数</text>
            <input class="input" v-model="newKey.maxErrors" placeholder="5" type="number" />
          </view>
        </view>
        <view class="dialog-actions">
          <button class="dialog-btn cancel" @click="hideAddDialog">取消</button>
          <button class="dialog-btn confirm" @click="addKey">添加</button>
        </view>
      </view>
    </view>

    <!-- 测试结果显示 -->
    <view v-if="testResults.length > 0" class="test-results">
      <view class="section-title">测试结果</view>
      <view v-for="(result, index) in testResults" :key="index" class="test-result-item">
        <view class="result-header">
          <text class="result-key">{{ result.keyName }}</text>
          <text :class="['result-status', result.success ? 'success' : 'error']">
            {{ result.success ? '成功' : '失败' }}
          </text>
        </view>
        <view class="result-details">
          <text v-if="result.success" class="result-time">响应时间: {{ result.responseTime }}ms</text>
          <text v-else class="result-error">{{ result.error }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import apiKeyManager from '@/services/apiKeyManager.js';

export default {
  data() {
    return {
      apiKeys: [],
      currentKey: null,
      statistics: {
        total: 0,
        active: 0,
        error: 0,
        disabled: 0
      },
      showAdd: false,
      newKey: {
        name: '',
        key: '',
        description: '',
        maxErrors: 5
      },
      testResults: []
    };
  },
  
  onLoad() {
    this.loadData();
  },
  
  methods: {
    loadData() {
      this.apiKeys = apiKeyManager.getAllKeys();
      this.currentKey = apiKeyManager.getCurrentApiKey();
      this.statistics = apiKeyManager.getStatistics();
    },
    
    quickSwitch() {
      const switched = apiKeyManager.switchToNextKey();
      if (switched) {
        this.loadData();
        uni.showToast({
          title: `已切换到: ${switched.name}`,
          icon: 'success'
        });
      } else {
        uni.showToast({
          title: '没有可用的API Key',
          icon: 'error'
        });
      }
    },
    
    activateKey(keyId) {
      const activated = apiKeyManager.switchToKey(keyId);
      if (activated) {
        this.loadData();
        uni.showToast({
          title: `已激活: ${activated.name}`,
          icon: 'success'
        });
      }
    },
    
    async testKey(keyId) {
      const result = await apiKeyManager.testApiKey(keyId);
      const key = this.apiKeys.find(k => k.id === keyId);
      
      this.testResults.unshift({
        keyName: key?.name || keyId,
        success: result.success,
        responseTime: result.responseTime,
        error: result.error,
        timestamp: new Date().toLocaleTimeString()
      });
      
      // 只保留最近10条结果
      if (this.testResults.length > 10) {
        this.testResults = this.testResults.slice(0, 10);
      }
      
      this.loadData();
    },
    
    async testCurrentKey() {
      if (this.currentKey) {
        await this.testKey(this.currentKey.id);
      }
    },
    
    async testAllKeys() {
      uni.showLoading({ title: '测试中...' });
      
      const results = await apiKeyManager.testAllKeys();
      
      this.testResults = [];
      Object.entries(results).forEach(([keyId, result]) => {
        const key = this.apiKeys.find(k => k.id === keyId);
        this.testResults.push({
          keyName: key?.name || keyId,
          success: result.success,
          responseTime: result.responseTime,
          error: result.error,
          timestamp: new Date().toLocaleTimeString()
        });
      });
      
      uni.hideLoading();
      this.loadData();
    },
    
    deleteKey(keyId) {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这个API Key吗？',
        success: (res) => {
          if (res.confirm) {
            apiKeyManager.removeApiKey(keyId);
            this.loadData();
            uni.showToast({
              title: '删除成功',
              icon: 'success'
            });
          }
        }
      });
    },
    
    showAddDialog() {
      this.showAdd = true;
      this.newKey = {
        name: '',
        key: '',
        description: '',
        maxErrors: 5
      };
    },
    
    hideAddDialog() {
      this.showAdd = false;
    },
    
    addKey() {
      if (!this.newKey.name || !this.newKey.key) {
        uni.showToast({
          title: '请填写名称和API Key',
          icon: 'error'
        });
        return;
      }
      
      apiKeyManager.addApiKey(this.newKey);
      this.hideAddDialog();
      this.loadData();
      
      uni.showToast({
        title: '添加成功',
        icon: 'success'
      });
    },
    
    resetAllStatus() {
      this.apiKeys.forEach(key => {
        apiKeyManager.resetKeyStatus(key.id);
      });
      this.loadData();
      
      uni.showToast({
        title: '状态已重置',
        icon: 'success'
      });
    },
    
    exportConfig() {
      const config = apiKeyManager.exportConfig();
      
      // 这里可以实现导出功能，比如复制到剪贴板
      console.log('导出配置:', config);
      
      uni.showToast({
        title: '配置已导出到控制台',
        icon: 'success'
      });
    },
    
    showImportDialog() {
      // 这里可以实现导入功能
      uni.showToast({
        title: '导入功能开发中',
        icon: 'none'
      });
    },
    
    getStatusText(status) {
      const statusMap = {
        'active': '活跃',
        'inactive': '未激活',
        'error': '错误',
        'disabled': '禁用'
      };
      return statusMap[status] || status;
    },
    
    formatTime(timestamp) {
      if (!timestamp) return '从未';
      return new Date(timestamp).toLocaleString();
    }
  }
};
</script>

<style>
.container {
  padding: 30rpx;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 40rpx;
}

.title {
  font-size: 48rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 10rpx;
}

.subtitle {
  font-size: 28rpx;
  color: #666;
  display: block;
}

.stats-section {
  display: flex;
  justify-content: space-between;
  margin-bottom: 30rpx;
}

.stat-card {
  background: white;
  border-radius: 15rpx;
  padding: 20rpx;
  text-align: center;
  flex: 1;
  margin: 0 10rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.1);
}

.stat-card.active {
  background: linear-gradient(135deg, #4caf50, #45a049);
  color: white;
}

.stat-card.error {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  color: white;
}

.stat-card.disabled {
  background: linear-gradient(135deg, #9e9e9e, #757575);
  color: white;
}

.stat-number {
  font-size: 36rpx;
  font-weight: bold;
  display: block;
}

.stat-label {
  font-size: 24rpx;
  opacity: 0.8;
}

.current-key-section, .keys-section, .batch-section, .test-results {
  background: white;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.1);
}

.section-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.add-btn {
  background: linear-gradient(135deg, #2196f3, #1976d2);
  color: white;
  border: none;
  border-radius: 10rpx;
  padding: 15rpx 25rpx;
  font-size: 28rpx;
}

.current-key-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  background: #f8f9fa;
  border-radius: 15rpx;
}

.key-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  display: block;
}

.key-value {
  font-size: 24rpx;
  color: #666;
  font-family: monospace;
  display: block;
  margin-top: 5rpx;
}

.key-actions {
  display: flex;
  gap: 10rpx;
}

.action-btn {
  padding: 10rpx 20rpx;
  border-radius: 8rpx;
  font-size: 24rpx;
  border: none;
}

.action-btn.switch {
  background: #ff9800;
  color: white;
}

.action-btn.test {
  background: #2196f3;
  color: white;
}

.action-btn.activate {
  background: #4caf50;
  color: white;
}

.action-btn.delete {
  background: #f44336;
  color: white;
}

.key-item {
  border: 2rpx solid #eee;
  border-radius: 15rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
}

.key-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  background: #f8f9fa;
}

.key-status {
  padding: 5rpx 15rpx;
  border-radius: 15rpx;
  font-size: 22rpx;
  color: white;
  margin-left: 10rpx;
}

.key-status.active {
  background: #4caf50;
}

.key-status.inactive {
  background: #9e9e9e;
}

.key-status.error {
  background: #f44336;
}

.key-status.disabled {
  background: #757575;
}

.key-details {
  padding: 20rpx;
}

.key-stats {
  display: flex;
  gap: 20rpx;
  margin-top: 10rpx;
}

.stat-item {
  font-size: 24rpx;
  color: #666;
}

.key-error {
  padding: 15rpx 20rpx;
  background: #ffebee;
  border-top: 1rpx solid #ffcdd2;
}

.error-text {
  font-size: 26rpx;
  color: #d32f2f;
  display: block;
}

.error-time {
  font-size: 22rpx;
  color: #999;
  display: block;
  margin-top: 5rpx;
}

.batch-actions {
  display: flex;
  gap: 15rpx;
  flex-wrap: wrap;
}

.batch-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 10rpx;
  padding: 20rpx 30rpx;
  font-size: 28rpx;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.dialog {
  background: white;
  border-radius: 20rpx;
  padding: 40rpx;
  margin: 40rpx;
  max-width: 600rpx;
  width: 100%;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.dialog-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

.close-btn {
  font-size: 48rpx;
  color: #999;
  cursor: pointer;
}

.input-group {
  margin-bottom: 25rpx;
}

.input-label {
  font-size: 28rpx;
  color: #333;
  display: block;
  margin-bottom: 10rpx;
}

.input {
  width: 100%;
  padding: 20rpx;
  border: 2rpx solid #ddd;
  border-radius: 10rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15rpx;
  margin-top: 30rpx;
}

.dialog-btn {
  padding: 20rpx 40rpx;
  border-radius: 10rpx;
  font-size: 28rpx;
  border: none;
}

.dialog-btn.cancel {
  background: #f5f5f5;
  color: #666;
}

.dialog-btn.confirm {
  background: linear-gradient(135deg, #4caf50, #45a049);
  color: white;
}

.test-result-item {
  border: 2rpx solid #eee;
  border-radius: 10rpx;
  padding: 20rpx;
  margin-bottom: 15rpx;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10rpx;
}

.result-key {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
}

.result-status.success {
  color: #4caf50;
  font-weight: bold;
}

.result-status.error {
  color: #f44336;
  font-weight: bold;
}

.result-details {
  font-size: 24rpx;
  color: #666;
}
</style>
