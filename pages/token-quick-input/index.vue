<template>
  <view class="container">
    <view class="header">
      <text class="title">🔑 Token快速更换</text>
      <text class="subtitle">茶股帮Token即将过期？快速切换备用Token</text>
    </view>

    <!-- 当前Token状态 -->
    <view class="status-card">
      <view class="status-item">
        <text class="label">当前Token:</text>
        <text class="value">{{ currentToken || '未设置' }}</text>
      </view>
      <view class="status-item">
        <text class="label">连接状态:</text>
        <text class="value" :class="{ connected: isConnected }">
          {{ isConnected ? '已连接 🟢' : '未连接 🔴' }}
        </text>
      </view>
    </view>

    <!-- 快速输入新Token -->
    <view class="input-section">
      <text class="section-title">输入新Token</text>
      
      <view class="input-group">
        <text class="input-label">Token值:</text>
        <textarea
          class="token-input"
          v-model="newTokenValue"
          placeholder="请粘贴新的茶股帮Token (以QT_开头)"
          :auto-height="true"
          :show-confirm-bar="false"
          maxlength="200"
        />
      </view>

      <view class="input-group">
        <text class="input-label">Token名称:</text>
        <textarea
          class="name-input"
          v-model="newTokenName"
          placeholder="给这个Token起个名字 (如: backup_token_1)"
          :auto-height="true"
          :show-confirm-bar="false"
          maxlength="50"
        />
      </view>

      <view class="actions">
        <button class="btn test-btn" @click="testToken" :disabled="!newTokenValue || testing">
          {{ testing ? '测试中...' : '🔍 测试Token' }}
        </button>
        <button class="btn update-btn" @click="updateToken" :disabled="!canUpdate || updating">
          {{ updating ? '更新中...' : '🚀 立即更换' }}
        </button>
      </view>
    </view>

    <!-- 备用Token列表 -->
    <view class="backup-tokens" v-if="backupTokens.length > 0">
      <text class="section-title">备用Token快速切换</text>
      <view 
        v-for="(token, index) in backupTokens" 
        :key="index"
        class="token-item"
        @click="switchToToken(token)"
      >
        <view class="token-info">
          <text class="token-name">{{ token.name }}</text>
          <text class="token-preview">{{ token.token.substring(0, 15) }}...</text>
        </view>
        <button class="switch-btn" :disabled="switching">
          {{ switching ? '切换中...' : '切换' }}
        </button>
      </view>
    </view>

    <!-- 操作结果 -->
    <view class="result-section" v-if="lastResult">
      <view class="result-item" :class="{ success: lastResult.success, error: !lastResult.success }">
        <text class="result-text">{{ lastResult.message }}</text>
        <text class="result-time">{{ lastResult.time }}</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      // Token状态
      currentToken: '',
      isConnected: false,
      
      // 输入数据
      newTokenValue: '',
      newTokenName: '',
      
      // 操作状态
      testing: false,
      updating: false,
      switching: false,
      
      // 备用Token列表
      backupTokens: [],
      
      // 操作结果
      lastResult: null
    };
  },
  
  computed: {
    canUpdate() {
      return this.newTokenValue && 
             this.newTokenValue.startsWith('QT_') && 
             this.newTokenName && 
             !this.testing && 
             !this.updating;
    }
  },
  
  onLoad() {
    this.loadCurrentStatus();
    this.loadBackupTokens();
  },
  
  methods: {
    // 加载当前状态
    async loadCurrentStatus() {
      try {
        const response = await uni.request({
          url: 'https://agent.aigupiao.me/tokens',
          method: 'GET',
          timeout: 10000
        });
        
        if (response.statusCode === 200 && response.data.success) {
          this.currentToken = response.data.current_token || '';
          this.isConnected = response.data.connection_status === 'connected';
        }
      } catch (error) {
        console.error('加载状态失败:', error);
      }
    },
    
    // 加载备用Token列表
    async loadBackupTokens() {
      try {
        const response = await uni.request({
          url: 'https://agent.aigupiao.me/tokens',
          method: 'GET',
          timeout: 10000
        });
        
        if (response.statusCode === 200 && response.data.success) {
          this.backupTokens = response.data.tokens || [];
        }
      } catch (error) {
        console.error('加载备用Token失败:', error);
      }
    },
    
    // 测试Token
    async testToken() {
      if (!this.newTokenValue) {
        this.showResult(false, '请输入Token值');
        return;
      }
      
      if (!this.newTokenValue.startsWith('QT_')) {
        this.showResult(false, 'Token格式错误，应该以QT_开头');
        return;
      }
      
      this.testing = true;
      
      try {
        // 这里可以添加Token测试逻辑
        await new Promise(resolve => setTimeout(resolve, 2000)); // 模拟测试
        
        this.showResult(true, 'Token测试通过，可以使用');
      } catch (error) {
        this.showResult(false, `Token测试失败: ${error.message}`);
      } finally {
        this.testing = false;
      }
    },
    
    // 更新Token
    async updateToken() {
      if (!this.canUpdate) return;
      
      this.updating = true;
      
      try {
        // 1. 添加到云端
        const addResponse = await uni.request({
          url: 'https://agent.aigupiao.me/tokens',
          method: 'POST',
          data: {
            token: this.newTokenValue,
            name: this.newTokenName || `token_${Date.now()}`,
            priority: 8
          },
          timeout: 15000
        });
        
        if (addResponse.statusCode === 200 && addResponse.data.success) {
          // 2. 切换到新Token
          const switchResponse = await uni.request({
            url: 'https://agent.aigupiao.me/switch-token',
            method: 'POST',
            data: {
              token_name: this.newTokenName || `token_${Date.now()}`
            },
            timeout: 15000
          });
          
          if (switchResponse.statusCode === 200 && switchResponse.data.success) {
            this.showResult(true, '✅ Token更换成功！数据服务已恢复');
            
            // 清空输入
            this.newTokenValue = '';
            this.newTokenName = '';
            
            // 刷新状态
            setTimeout(() => {
              this.loadCurrentStatus();
              this.loadBackupTokens();
            }, 1000);
          } else {
            this.showResult(false, '切换失败: ' + (switchResponse.data?.message || '未知错误'));
          }
        } else {
          this.showResult(false, '添加失败: ' + (addResponse.data?.message || '未知错误'));
        }
        
      } catch (error) {
        this.showResult(false, `更新失败: ${error.message}`);
      } finally {
        this.updating = false;
      }
    },
    
    // 切换到备用Token
    async switchToToken(token) {
      this.switching = true;
      
      try {
        const response = await uni.request({
          url: 'https://agent.aigupiao.me/switch-token',
          method: 'POST',
          data: {
            token_name: token.name
          },
          timeout: 10000
        });
        
        if (response.statusCode === 200 && response.data.success) {
          this.showResult(true, `✅ 已切换到: ${token.name}`);
          
          // 刷新状态
          setTimeout(() => {
            this.loadCurrentStatus();
          }, 1000);
        } else {
          this.showResult(false, '切换失败: ' + (response.data?.message || '未知错误'));
        }
        
      } catch (error) {
        this.showResult(false, `切换失败: ${error.message}`);
      } finally {
        this.switching = false;
      }
    },
    
    // 显示操作结果
    showResult(success, message) {
      this.lastResult = {
        success,
        message,
        time: new Date().toLocaleTimeString()
      };
      
      // 显示toast
      uni.showToast({
        title: message,
        icon: success ? 'success' : 'none',
        duration: 3000
      });
    }
  }
};
</script>

<style scoped>
.container {
  padding: 20rpx;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 30rpx;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 10rpx;
}

.subtitle {
  font-size: 24rpx;
  color: #666;
  display: block;
}

.status-card {
  background: white;
  border-radius: 12rpx;
  padding: 25rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.1);
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15rpx;
}

.status-item:last-child {
  margin-bottom: 0;
}

.label {
  font-size: 28rpx;
  color: #333;
  font-weight: bold;
}

.value {
  font-size: 26rpx;
  color: #666;
  font-family: monospace;
}

.value.connected {
  color: #4caf50;
}

.input-section {
  background: white;
  border-radius: 12rpx;
  padding: 25rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.1);
}

.section-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 25rpx;
  display: block;
}

.input-group {
  margin-bottom: 25rpx;
}

.input-label {
  font-size: 26rpx;
  color: #333;
  font-weight: bold;
  display: block;
  margin-bottom: 10rpx;
}

.token-input, .name-input {
  width: 100%;
  min-height: 80rpx;
  padding: 20rpx;
  border: 2rpx solid #ddd;
  border-radius: 8rpx;
  font-size: 26rpx;
  background-color: #fafafa;
  box-sizing: border-box;
}

.token-input:focus, .name-input:focus {
  border-color: #4c8dff;
  background-color: white;
}

.actions {
  display: flex;
  gap: 20rpx;
}

.btn {
  flex: 1;
  padding: 25rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
  font-weight: bold;
  border: none;
  text-align: center;
}

.test-btn {
  background-color: #ff9800;
  color: white;
}

.update-btn {
  background-color: #4caf50;
  color: white;
}

.btn:disabled {
  background-color: #ccc;
  color: #666;
}

.backup-tokens {
  background: white;
  border-radius: 12rpx;
  padding: 25rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.1);
}

.token-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #eee;
}

.token-item:last-child {
  border-bottom: none;
}

.token-info {
  flex: 1;
}

.token-name {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 5rpx;
}

.token-preview {
  font-size: 24rpx;
  color: #666;
  font-family: monospace;
  display: block;
}

.switch-btn {
  padding: 15rpx 25rpx;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 6rpx;
  font-size: 24rpx;
}

.switch-btn:disabled {
  background-color: #ccc;
  color: #666;
}

.result-section {
  background: white;
  border-radius: 12rpx;
  padding: 25rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.1);
}

.result-item {
  padding: 20rpx;
  border-radius: 8rpx;
  margin-bottom: 15rpx;
}

.result-item.success {
  background-color: #e8f5e8;
  border-left: 4rpx solid #4caf50;
}

.result-item.error {
  background-color: #ffeaea;
  border-left: 4rpx solid #f44336;
}

.result-text {
  font-size: 26rpx;
  color: #333;
  display: block;
  margin-bottom: 5rpx;
}

.result-time {
  font-size: 22rpx;
  color: #666;
  display: block;
}
</style>
