<template>
  <view v-if="showAlert" class="error-alert-overlay" @click="closeAlert">
    <view class="error-alert-container" @click.stop>
      <view class="error-header">
        <text class="error-icon">⚠️</text>
        <text class="error-title">交易软件要求真实数据</text>
      </view>
      
      <view class="error-content">
        <text class="error-message">{{ errorMessage }}</text>
        
        <view class="error-details">
          <text class="detail-title">检测到的问题:</text>
          <text class="detail-item">• 后端返回了模拟/测试数据</text>
          <text class="detail-item">• 交易软件拒绝使用模拟数据</text>
          <text class="detail-item">• 需要连接真实股票数据源</text>
        </view>
        
        <view class="solution-section">
          <text class="solution-title">解决方案:</text>
          <text class="solution-item">1. 确保Agent后端连接真实数据源</text>
          <text class="solution-item">2. 配置真实股票API (如同花顺、通达信)</text>
          <text class="solution-item">3. 移除所有模拟数据配置</text>
          <text class="solution-item">4. 重启Agent服务并重新连接</text>
        </view>
      </view>
      
      <view class="error-actions">
        <button class="retry-btn" @click="retryConnection">重试连接</button>
        <button class="close-btn" @click="closeAlert">关闭</button>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'RealDataErrorAlert',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    errorMessage: {
      type: String,
      default: '检测到模拟数据，交易软件要求真实数据'
    }
  },
  
  data() {
    return {
      showAlert: false
    };
  },
  
  watch: {
    visible(newVal) {
      this.showAlert = newVal;
    }
  },
  
  methods: {
    closeAlert() {
      this.showAlert = false;
      this.$emit('close');
    },
    
    retryConnection() {
      this.$emit('retry');
      this.closeAlert();
    }
  }
};
</script>

<style scoped>
.error-alert-overlay {
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

.error-alert-container {
  background: white;
  border-radius: 20rpx;
  padding: 40rpx;
  margin: 40rpx;
  max-width: 600rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.3);
}

.error-header {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
  padding-bottom: 20rpx;
  border-bottom: 2rpx solid #ffeb3b;
}

.error-icon {
  font-size: 48rpx;
  margin-right: 20rpx;
}

.error-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #f44336;
}

.error-content {
  margin-bottom: 40rpx;
}

.error-message {
  font-size: 32rpx;
  color: #333;
  line-height: 1.5;
  display: block;
  margin-bottom: 30rpx;
  padding: 20rpx;
  background: #fff3cd;
  border-radius: 10rpx;
  border-left: 6rpx solid #ffc107;
}

.error-details {
  margin-bottom: 30rpx;
}

.detail-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #d32f2f;
  display: block;
  margin-bottom: 15rpx;
}

.detail-item {
  font-size: 28rpx;
  color: #666;
  display: block;
  margin-bottom: 10rpx;
  padding-left: 20rpx;
}

.solution-section {
  background: #e8f5e8;
  padding: 20rpx;
  border-radius: 10rpx;
  border-left: 6rpx solid #4caf50;
}

.solution-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #2e7d32;
  display: block;
  margin-bottom: 15rpx;
}

.solution-item {
  font-size: 28rpx;
  color: #4caf50;
  display: block;
  margin-bottom: 8rpx;
  padding-left: 20rpx;
}

.error-actions {
  display: flex;
  justify-content: space-between;
  gap: 20rpx;
}

.retry-btn, .close-btn {
  flex: 1;
  height: 80rpx;
  border-radius: 15rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
}

.retry-btn {
  background: linear-gradient(135deg, #4caf50, #45a049);
  color: white;
}

.close-btn {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  color: white;
}

.retry-btn:active {
  background: linear-gradient(135deg, #45a049, #3d8b40);
}

.close-btn:active {
  background: linear-gradient(135deg, #d32f2f, #b71c1c);
}
</style>
