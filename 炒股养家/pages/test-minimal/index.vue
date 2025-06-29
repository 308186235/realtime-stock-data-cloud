<template>
  <view class="container">
    <view class="header">
      <text class="title">最小化测试页面</text>
    </view>
    
    <view class="content">
      <text class="message">这是一个最小化的测试页面</text>
      <text class="info">如果您能看到这个页面，说明uni-app基础功能正常</text>
      
      <view class="test-section">
        <text class="section-title">基础信息:</text>
        <text class="info-item">当前时间: {{ currentTime }}</text>
        <text class="info-item">页面状态: 正常</text>
        <text class="info-item">计数器: {{ counter }}</text>
      </view>
      
      <view class="button-section">
        <button class="test-button" @click="increment">点击计数 +1</button>
        <button class="test-button" @click="showToast">显示提示</button>
        <button class="test-button" @click="goHome">返回首页</button>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      currentTime: '',
      counter: 0
    };
  },
  
  onLoad() {
    console.log('最小化测试页面加载');
    this.updateTime();
    
    // 每秒更新时间
    setInterval(() => {
      this.updateTime();
    }, 1000);
  },
  
  methods: {
    updateTime() {
      const now = new Date();
      this.currentTime = now.toLocaleTimeString();
    },
    
    increment() {
      this.counter++;
      console.log('计数器增加:', this.counter);
    },
    
    showToast() {
      uni.showToast({
        title: '测试成功!',
        icon: 'success',
        duration: 2000
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
}

.content {
  background: white;
  border-radius: 16rpx;
  padding: 40rpx;
}

.message {
  font-size: 32rpx;
  color: #333;
  text-align: center;
  margin-bottom: 20rpx;
  display: block;
}

.info {
  font-size: 28rpx;
  color: #666;
  text-align: center;
  margin-bottom: 40rpx;
  display: block;
}

.test-section {
  margin: 40rpx 0;
  padding: 30rpx;
  background-color: #f8f9fa;
  border-radius: 12rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.info-item {
  font-size: 28rpx;
  color: #666;
  margin-bottom: 16rpx;
  display: block;
}

.button-section {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.test-button {
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 8rpx;
  padding: 24rpx;
  font-size: 32rpx;
}

.test-button:active {
  background-color: #0056b3;
}
</style>
