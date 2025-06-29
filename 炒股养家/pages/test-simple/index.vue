<template>
  <view class="container">
    <view class="header">
      <text class="title">简单测试页面</text>
    </view>
    
    <view class="content">
      <text class="message">如果您能看到这个页面，说明基础路由正常工作</text>
      
      <view class="test-info">
        <text class="info-item">当前时间: {{ currentTime }}</text>
        <text class="info-item">页面状态: 正常加载</text>
        <text class="info-item">Vue版本: {{ vueVersion }}</text>
      </view>
      
      <view class="button-group">
        <button class="test-btn" @click="testFunction">测试按钮</button>
        <button class="test-btn" @click="goBack">返回首页</button>
      </view>
      
      <view class="log-section">
        <text class="log-title">测试日志:</text>
        <view class="log-content">
          <text v-for="(log, index) in logs" :key="index" class="log-item">
            {{ log }}
          </text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      currentTime: '',
      vueVersion: '3.x',
      logs: []
    };
  },
  
  onLoad() {
    this.addLog('页面加载完成');
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
    
    addLog(message) {
      const timestamp = new Date().toLocaleTimeString();
      this.logs.unshift(`[${timestamp}] ${message}`);
      
      // 限制日志数量
      if (this.logs.length > 10) {
        this.logs = this.logs.slice(0, 10);
      }
    },
    
    testFunction() {
      this.addLog('测试按钮被点击');
      uni.showToast({
        title: '测试成功',
        icon: 'success'
      });
    },
    
    goBack() {
      this.addLog('返回首页');
      uni.navigateTo({
        url: '/pages/index/index'
      });
    }
  }
};
</script>

<style scoped>
.container {
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
}

.content {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.message {
  font-size: 16px;
  color: #666;
  text-align: center;
  margin-bottom: 20px;
  display: block;
}

.test-info {
  margin: 20px 0;
}

.info-item {
  display: block;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
  color: #333;
}

.button-group {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.test-btn {
  flex: 1;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 12px;
  font-size: 16px;
}

.log-section {
  margin-top: 20px;
}

.log-title {
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
  display: block;
}

.log-content {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 10px;
  max-height: 200px;
  overflow-y: auto;
}

.log-item {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
  font-family: monospace;
}
</style>
