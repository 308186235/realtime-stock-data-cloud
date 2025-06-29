<template>
  <view class="test-page">
    <view class="header">
      <text class="title">后端连接测试</text>
      <text class="subtitle">测试手机软件与后端的连接状态</text>
    </view>
    
    <!-- 连接状态组件 -->
    <BackendConnectionStatus />
    
    <!-- 测试信息 -->
    <view class="test-info">
      <view class="info-card">
        <text class="info-title">测试说明</text>
        <text class="info-text">• 绿色圆点表示后端连接正常</text>
        <text class="info-text">• 红色圆点表示后端连接失败</text>
        <text class="info-text">• 蓝色闪烁表示正在检测中</text>
        <text class="info-text">• 点击状态栏可查看详细信息</text>
        <text class="info-text">• 每30秒自动检测一次连接状态</text>
      </view>
      
      <view class="info-card">
        <text class="info-title">功能特性</text>
        <text class="info-text">✅ 实时连接状态显示</text>
        <text class="info-text">✅ 自动定期检测</text>
        <text class="info-text">✅ 响应时间监测</text>
        <text class="info-text">✅ 错误信息提示</text>
        <text class="info-text">✅ 手动重新检测</text>
        <text class="info-text">✅ 网络设置入口</text>
      </view>
    </view>
    
    <!-- 操作按钮 -->
    <view class="actions">
      <button class="action-btn" @click="goToNetworkSettings">网络设置</button>
      <button class="action-btn" @click="goToMainPage">返回首页</button>
    </view>
  </view>
</template>

<script>
import BackendConnectionStatus from '@/components/BackendConnectionStatus.vue'

export default {
  name: 'ConnectionTest',
  components: {
    BackendConnectionStatus
  },
  
  methods: {
    goToNetworkSettings() {
      uni.navigateTo({
        url: '/pages/settings/network'
      });
    },
    
    goToMainPage() {
      uni.switchTab({
        url: '/pages/index/index'
      });
    }
  }
}
</script>

<style scoped>
.test-page {
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

.test-info {
  margin: 30px 0;
}

.info-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.info-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 12px;
}

.info-text {
  font-size: 14px;
  color: #666;
  display: block;
  margin-bottom: 8px;
  line-height: 1.5;
}

.actions {
  display: flex;
  gap: 16px;
  margin-top: 30px;
}

.action-btn {
  flex: 1;
  padding: 12px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
}
</style>
