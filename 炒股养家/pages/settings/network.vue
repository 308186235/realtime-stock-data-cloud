<template>
  <view class="network-settings">
    <view class="header">
      <text class="title">网络设置</text>
      <text class="subtitle">配置后端服务器连接</text>
    </view>
    
    <!-- 服务器地址配置 -->
    <view class="section">
      <view class="section-title">服务器地址</view>
      
      <view class="input-group">
        <text class="input-label">API基础地址</text>
        <input 
          class="input-field" 
          v-model="apiBaseUrl" 
          placeholder="https://api.aigupiao.me"
          @blur="validateUrl"
        />
      </view>
      
      <view class="preset-buttons">
        <button 
          class="preset-btn" 
          :class="{ active: apiBaseUrl === preset.url }"
          v-for="preset in presetUrls" 
          :key="preset.name"
          @click="selectPreset(preset)"
        >
          {{ preset.name }}
        </button>
      </view>
    </view>
    
    <!-- 连接测试 -->
    <view class="section">
      <view class="section-title">连接测试</view>
      
      <view class="test-result" v-if="testResult">
        <view class="result-item">
          <text class="result-label">状态:</text>
          <text class="result-value" :class="testResult.status">
            {{ testResult.status === 'success' ? '✅ 连接成功' : '❌ 连接失败' }}
          </text>
        </view>
        
        <view class="result-item" v-if="testResult.responseTime">
          <text class="result-label">响应时间:</text>
          <text class="result-value">{{ testResult.responseTime }}ms</text>
        </view>
        
        <view class="result-item" v-if="testResult.error">
          <text class="result-label">错误信息:</text>
          <text class="result-value error">{{ testResult.error }}</text>
        </view>
      </view>
      
      <button class="test-btn" @click="testConnection" :disabled="isTesting">
        {{ isTesting ? '测试中...' : '测试连接' }}
      </button>
    </view>
    
    <!-- 高级设置 -->
    <view class="section">
      <view class="section-title">高级设置</view>
      
      <view class="setting-item">
        <text class="setting-label">连接超时 (秒)</text>
        <input 
          class="setting-input" 
          type="number" 
          v-model.number="timeout" 
          min="5" 
          max="60"
        />
      </view>
      
      <view class="setting-item">
        <text class="setting-label">自动重连</text>
        <switch :checked="autoReconnect" @change="toggleAutoReconnect" />
      </view>
      
      <view class="setting-item">
        <text class="setting-label">检测间隔 (秒)</text>
        <input 
          class="setting-input" 
          type="number" 
          v-model.number="checkInterval" 
          min="10" 
          max="300"
        />
      </view>
    </view>
    
    <!-- 保存按钮 -->
    <view class="actions">
      <button class="save-btn" @click="saveSettings">保存设置</button>
      <button class="reset-btn" @click="resetSettings">重置默认</button>
    </view>
  </view>
</template>

<script>
export default {
  name: 'NetworkSettings',
  data() {
    return {
      // 配置项
      apiBaseUrl: 'https://api.aigupiao.me',
      timeout: 10,
      autoReconnect: true,
      checkInterval: 30,
      
      // 预设地址
      presetUrls: [
        { name: '生产环境', url: 'https://api.aigupiao.me' },
        { name: '本地测试', url: 'http://localhost:8000' },
        { name: '局域网', url: 'http://192.168.1.100:8000' }
      ],
      
      // 测试状态
      isTesting: false,
      testResult: null
    }
  },
  
  mounted() {
    this.loadSettings();
  },
  
  methods: {
    // 加载设置
    loadSettings() {
      try {
        const settings = uni.getStorageSync('network_settings');
        if (settings) {
          const config = JSON.parse(settings);
          this.apiBaseUrl = config.apiBaseUrl || 'https://api.aigupiao.me';
          this.timeout = config.timeout || 10;
          this.autoReconnect = config.autoReconnect !== false;
          this.checkInterval = config.checkInterval || 30;
        }
      } catch (e) {
        console.error('加载网络设置失败:', e);
      }
    },
    
    // 保存设置
    saveSettings() {
      try {
        const settings = {
          apiBaseUrl: this.apiBaseUrl,
          timeout: this.timeout,
          autoReconnect: this.autoReconnect,
          checkInterval: this.checkInterval,
          updatedAt: new Date().toISOString()
        };
        
        uni.setStorageSync('network_settings', JSON.stringify(settings));
        uni.setStorageSync('app_config', { apiBaseUrl: this.apiBaseUrl });
        
        uni.showToast({
          title: '设置已保存',
          icon: 'success'
        });
        
        // 通知其他页面更新
        uni.$emit('networkSettingsChanged', settings);
        
      } catch (e) {
        console.error('保存网络设置失败:', e);
        uni.showToast({
          title: '保存失败',
          icon: 'error'
        });
      }
    },
    
    // 重置设置
    resetSettings() {
      uni.showModal({
        title: '确认重置',
        content: '确定要重置为默认设置吗？',
        success: (res) => {
          if (res.confirm) {
            this.apiBaseUrl = 'https://api.aigupiao.me';
            this.timeout = 10;
            this.autoReconnect = true;
            this.checkInterval = 30;
            this.testResult = null;
            
            uni.showToast({
              title: '已重置',
              icon: 'success'
            });
          }
        }
      });
    },
    
    // 选择预设地址
    selectPreset(preset) {
      this.apiBaseUrl = preset.url;
      this.testResult = null;
    },
    
    // 验证URL
    validateUrl() {
      if (!this.apiBaseUrl) {
        uni.showToast({
          title: '请输入服务器地址',
          icon: 'none'
        });
        return false;
      }
      
      if (!this.apiBaseUrl.startsWith('http://') && !this.apiBaseUrl.startsWith('https://')) {
        uni.showToast({
          title: '地址格式错误',
          icon: 'none'
        });
        return false;
      }
      
      return true;
    },
    
    // 测试连接
    async testConnection() {
      if (!this.validateUrl()) return;
      
      this.isTesting = true;
      this.testResult = null;
      
      try {
        const startTime = Date.now();
        
        const response = await uni.request({
          url: `${this.apiBaseUrl}/health`,
          method: 'GET',
          timeout: this.timeout * 1000,
          header: {
            'Content-Type': 'application/json'
          }
        });
        
        const responseTime = Date.now() - startTime;
        
        if (response.statusCode === 200) {
          this.testResult = {
            status: 'success',
            responseTime,
            data: response.data
          };
        } else {
          this.testResult = {
            status: 'error',
            error: `HTTP ${response.statusCode}`
          };
        }
        
      } catch (error) {
        this.testResult = {
          status: 'error',
          error: error.errMsg || error.message || '连接超时'
        };
      } finally {
        this.isTesting = false;
      }
    },
    
    // 切换自动重连
    toggleAutoReconnect(e) {
      this.autoReconnect = e.detail.value;
    }
  }
}
</script>

<style scoped>
.network-settings {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 14px;
  color: #666;
}

.section {
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 16px;
}

.input-group {
  margin-bottom: 16px;
}

.input-label {
  font-size: 14px;
  color: #666;
  display: block;
  margin-bottom: 8px;
}

.input-field {
  width: 100%;
  padding: 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.preset-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.preset-btn {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: white;
  font-size: 12px;
  color: #666;
}

.preset-btn.active {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}

.test-result {
  background: #f9f9f9;
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 16px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.result-label {
  font-size: 12px;
  color: #666;
}

.result-value {
  font-size: 12px;
  color: #333;
}

.result-value.success {
  color: #52c41a;
}

.result-value.error {
  color: #ff4d4f;
}

.test-btn {
  width: 100%;
  padding: 12px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
}

.test-btn:disabled {
  background: #d9d9d9;
  color: #999;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.setting-label {
  font-size: 14px;
  color: #333;
}

.setting-input {
  width: 80px;
  padding: 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  text-align: center;
}

.actions {
  display: flex;
  gap: 16px;
}

.save-btn, .reset-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
}

.save-btn {
  background: #52c41a;
  color: white;
}

.reset-btn {
  background: #f5f5f5;
  color: #333;
}
</style>
