<template>
  <view class="container">
    <view class="header">
      <text class="title">设备测试页面</text>
      <text class="subtitle">真机运行状态检测</text>
    </view>
    
    <view class="test-section">
      <view class="test-item">
        <text class="label">设备信息:</text>
        <text class="value">{{ deviceInfo.model }}</text>
      </view>
      
      <view class="test-item">
        <text class="label">系统版本:</text>
        <text class="value">{{ deviceInfo.system }}</text>
      </view>
      
      <view class="test-item">
        <text class="label">平台:</text>
        <text class="value">{{ deviceInfo.platform }}</text>
      </view>
      
      <view class="test-item">
        <text class="label">网络状态:</text>
        <text class="value" :class="networkClass">{{ networkStatus }}</text>
      </view>
      
      <view class="test-item">
        <text class="label">当前时间:</text>
        <text class="value">{{ currentTime }}</text>
      </view>
    </view>
    
    <view class="button-section">
      <button class="test-btn" @click="testVibrate">测试震动</button>
      <button class="test-btn" @click="testToast">测试提示</button>
      <button class="test-btn" @click="testNetwork">测试网络</button>
      <button class="test-btn" @click="goHome">返回首页</button>
    </view>
    
    <view class="log-section">
      <text class="log-title">测试日志:</text>
      <scroll-view class="log-content" scroll-y="true">
        <view v-for="(log, index) in logs" :key="index" class="log-item">
          <text class="log-text">{{ log }}</text>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      deviceInfo: {},
      networkStatus: '检测中...',
      networkClass: 'checking',
      currentTime: '',
      logs: []
    };
  },
  
  onLoad() {
    this.addLog('页面加载完成');
    this.getDeviceInfo();
    this.checkNetwork();
    this.updateTime();
    
    // 每秒更新时间
    setInterval(() => {
      this.updateTime();
    }, 1000);
  },
  
  methods: {
    addLog(message) {
      const timestamp = new Date().toLocaleTimeString();
      this.logs.unshift(`[${timestamp}] ${message}`);
      
      // 限制日志数量
      if (this.logs.length > 20) {
        this.logs = this.logs.slice(0, 20);
      }
    },
    
    getDeviceInfo() {
      uni.getSystemInfo({
        success: (res) => {
          this.deviceInfo = {
            model: res.model || '未知',
            system: `${res.platform} ${res.system}` || '未知',
            platform: res.platform || '未知'
          };
          this.addLog(`设备信息获取成功: ${this.deviceInfo.model}`);
        },
        fail: (err) => {
          this.addLog(`设备信息获取失败: ${err.errMsg}`);
        }
      });
    },
    
    checkNetwork() {
      uni.getNetworkType({
        success: (res) => {
          this.networkStatus = res.networkType;
          this.networkClass = res.networkType === 'none' ? 'offline' : 'online';
          this.addLog(`网络状态: ${res.networkType}`);
        },
        fail: (err) => {
          this.networkStatus = '检测失败';
          this.networkClass = 'error';
          this.addLog(`网络检测失败: ${err.errMsg}`);
        }
      });
    },
    
    updateTime() {
      this.currentTime = new Date().toLocaleString();
    },
    
    testVibrate() {
      uni.vibrateLong({
        success: () => {
          this.addLog('震动测试成功');
        },
        fail: (err) => {
          this.addLog(`震动测试失败: ${err.errMsg}`);
        }
      });
    },
    
    testToast() {
      uni.showToast({
        title: '真机运行正常!',
        icon: 'success',
        duration: 2000
      });
      this.addLog('提示测试成功');
    },
    
    testNetwork() {
      this.addLog('开始网络测试...');
      
      uni.request({
        url: 'https://api.aigupiao.me/health',
        method: 'GET',
        timeout: 10000,
        success: (res) => {
          if (res.statusCode === 200) {
            this.addLog('网络连接测试成功');
          } else {
            this.addLog(`网络测试失败: HTTP ${res.statusCode}`);
          }
        },
        fail: (err) => {
          this.addLog(`网络测试失败: ${err.errMsg}`);
        }
      });
    },
    
    goHome() {
      uni.navigateTo({
        url: '/pages/index/index'
      });
    }
  }
};
</script>

<style scoped>
.container {
  padding: 40rpx;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 60rpx;
}

.title {
  font-size: 48rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
}

.subtitle {
  font-size: 28rpx;
  color: #666;
  display: block;
}

.test-section {
  background: white;
  border-radius: 16rpx;
  padding: 40rpx;
  margin-bottom: 40rpx;
}

.test-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1px solid #eee;
}

.test-item:last-child {
  border-bottom: none;
}

.label {
  font-size: 32rpx;
  color: #333;
  font-weight: bold;
}

.value {
  font-size: 28rpx;
  color: #666;
}

.value.online {
  color: #4CAF50;
}

.value.offline {
  color: #f44336;
}

.value.error {
  color: #ff9800;
}

.value.checking {
  color: #2196F3;
}

.button-section {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
  margin-bottom: 40rpx;
}

.test-btn {
  flex: 1;
  min-width: 200rpx;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 8rpx;
  padding: 24rpx;
  font-size: 28rpx;
}

.test-btn:active {
  background-color: #0056b3;
}

.log-section {
  background: white;
  border-radius: 16rpx;
  padding: 40rpx;
}

.log-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.log-content {
  height: 400rpx;
  border: 1px solid #eee;
  border-radius: 8rpx;
  padding: 20rpx;
}

.log-item {
  margin-bottom: 10rpx;
}

.log-text {
  font-size: 24rpx;
  color: #666;
  font-family: monospace;
}
</style>
