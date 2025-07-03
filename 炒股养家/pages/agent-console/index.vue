<template>
  <view :class="['container', isDarkMode ? 'dark-theme' : 'light-theme']">
    <view class="header">
      <text class="title">Agent分析控制台</text>
      <view class="status-indicator" :class="systemStatus.is_trading_time ? 'active' : 'inactive'">
        <text class="status-text">{{ systemStatus.is_trading_time ? '交易时间' : '非交易时间' }}</text>
      </view>
    </view>
    
    <!-- 系统状态卡片 -->
    <view class="status-card">
      <view class="card-header">
        <text class="card-title">系统状态</text>
        <view class="refresh-btn" @click="refreshStatus">
          <text class="refresh-icon">🔄</text>
        </view>
      </view>
      <view class="status-grid">
        <view class="status-item">
          <text class="status-label">当前时间</text>
          <text class="status-value">{{ systemStatus.current_time }}</text>
        </view>
        <view class="status-item">
          <text class="status-label">交易时段</text>
          <text class="status-value">{{ systemStatus.trading_window }}</text>
        </view>
        <view class="status-item">
          <text class="status-label">分析间隔</text>
          <text class="status-value">{{ systemStatus.analysis_interval }}秒</text>
        </view>
        <view class="status-item">
          <text class="status-label">配置更新</text>
          <text class="status-value">{{ formatTime(systemStatus.config_updated_at) }}</text>
        </view>
      </view>
    </view>
    
    <!-- 北交所权限控制 -->
    <view class="control-card">
      <view class="card-header">
        <text class="card-title">北交所交易权限</text>
        <view class="beijing-status" :class="beijingConfig.enabled ? 'enabled' : 'disabled'">
          <text class="beijing-status-text">{{ beijingConfig.enabled ? '已开启' : '未开启' }}</text>
        </view>
      </view>
      
      <view class="control-content">
        <view class="control-description">
          <text class="description-text">
            {{ beijingConfig.enabled ? 
              'Agent当前可以分析和推荐北交所股票。如需关闭，请点击下方开关。' : 
              'Agent当前不会分析北交所股票。开启后可获得更多投资机会。' 
            }}
          </text>
        </view>
        
        <view class="control-switch">
          <view class="switch-container">
            <text class="switch-label">启用北交所分析</text>
            <switch 
              :checked="beijingConfig.enabled" 
              @change="toggleBeijingExchange" 
              color="#4c8dff" 
              class="beijing-switch"
            />
          </view>
        </view>
        
        <view class="control-info" v-if="beijingConfig.enabled">
          <view class="info-item">
            <text class="info-icon">⚠️</text>
            <text class="info-text">请确保您的证券账户已开通北交所交易权限</text>
          </view>
          <view class="info-item">
            <text class="info-icon">📊</text>
            <text class="info-text">北交所股票将包含在Agent的分析和推荐中</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- Agent配置 -->
    <view class="config-card">
      <view class="card-header">
        <text class="card-title">Agent配置</text>
      </view>
      
      <view class="config-list">
        <view class="config-item">
          <text class="config-label">分析间隔</text>
          <view class="config-control">
            <text class="config-value">{{ agentConfig.analysis_interval }}秒</text>
            <view class="config-buttons">
              <button class="config-btn" @click="adjustInterval(-5)">-5s</button>
              <button class="config-btn" @click="adjustInterval(5)">+5s</button>
            </view>
          </view>
        </view>
        
        <view class="config-item">
          <text class="config-label">重连间隔</text>
          <view class="config-control">
            <text class="config-value">{{ agentConfig.reconnect_interval }}秒</text>
            <view class="config-buttons">
              <button class="config-btn" @click="adjustReconnectInterval(-5)">-5s</button>
              <button class="config-btn" @click="adjustReconnectInterval(5)">+5s</button>
            </view>
          </view>
        </view>
        
        <view class="config-item">
          <text class="config-label">最大重连次数</text>
          <view class="config-control">
            <text class="config-value">{{ agentConfig.max_reconnect_attempts }}次</text>
            <view class="config-buttons">
              <button class="config-btn" @click="adjustMaxReconnect(-1)">-1</button>
              <button class="config-btn" @click="adjustMaxReconnect(1)">+1</button>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 操作按钮 -->
    <view class="action-buttons">
      <button class="action-btn primary" @click="saveAllConfig">保存配置</button>
      <button class="action-btn secondary" @click="resetConfig">重置默认</button>
      <button class="action-btn info" @click="testConnection">测试连接</button>
    </view>
  </view>
</template>

<script>
import unifiedAgentService from '@/services/unifiedAgentService.js'

export default {
  data() {
    return {
      isDarkMode: false,
      systemStatus: {
        current_time: '',
        is_trading_time: false,
        trading_window: '',
        analysis_interval: 40,
        config_updated_at: '',
        beijing_exchange_enabled: false
      },
      beijingConfig: {
        enabled: false,
        message: ''
      },
      agentConfig: {
        analysis_interval: 40,
        reconnect_interval: 30,
        max_reconnect_attempts: 10
      },
      connectionStatus: {
        cloud: false,
        local: false,
        websocket: false
      },
      realTimeData: null,
      agentDecisions: [],
      tradeHistory: []
    }
  },
  onLoad() {
    // 获取主题设置
    const app = getApp();
    this.isDarkMode = app.globalData.isDarkMode;

    // 设置事件监听
    this.setupEventListeners();

    // 加载配置
    this.loadSystemStatus();
    this.loadBeijingConfig();
    this.loadAgentConfig();
  },

  onUnload() {
    // 清理事件监听
    this.cleanupEventListeners();
  },
  methods: {
    setupEventListeners() {
      // 监听连接状态变化
      unifiedAgentService.on('connectionStatusChanged', this.onConnectionStatusChanged);

      // 监听实时数据
      unifiedAgentService.on('realTimeData', this.onRealTimeData);

      // 监听Agent决策
      unifiedAgentService.on('agentDecision', this.onAgentDecision);

      // 监听交易结果
      unifiedAgentService.on('tradeResult', this.onTradeResult);

      // 监听系统状态
      unifiedAgentService.on('systemStatus', this.onSystemStatus);
    },

    cleanupEventListeners() {
      unifiedAgentService.off('connectionStatusChanged', this.onConnectionStatusChanged);
      unifiedAgentService.off('realTimeData', this.onRealTimeData);
      unifiedAgentService.off('agentDecision', this.onAgentDecision);
      unifiedAgentService.off('tradeResult', this.onTradeResult);
      unifiedAgentService.off('systemStatus', this.onSystemStatus);
    },

    onConnectionStatusChanged(status) {
      this.connectionStatus = status;
      console.log('连接状态更新:', status);
    },

    onRealTimeData(data) {
      this.realTimeData = data;
      console.log('实时数据:', data);
    },

    onAgentDecision(decision) {
      this.agentDecisions.unshift(decision);
      if (this.agentDecisions.length > 50) {
        this.agentDecisions = this.agentDecisions.slice(0, 50);
      }
      console.log('Agent决策:', decision);
    },

    onTradeResult(result) {
      this.tradeHistory.unshift(result);
      if (this.tradeHistory.length > 100) {
        this.tradeHistory = this.tradeHistory.slice(0, 100);
      }
      console.log('交易结果:', result);
    },

    onSystemStatus(status) {
      this.systemStatus = { ...this.systemStatus, ...status };
      console.log('系统状态更新:', status);
    },

    async loadSystemStatus() {
      try {
        const result = await unifiedAgentService.getSystemStatus();
        if (result.success) {
          this.systemStatus = result.cloud || {};
          this.connectionStatus = result.connections || {};
        }
      } catch (e) {
        console.error('加载系统状态失败:', e);
      }
    },
    
    async loadBeijingConfig() {
      try {
        const result = await unifiedAgentService.getConfig();
        if (result.success && result.data.config) {
          this.beijingConfig.enabled = result.data.config.enable_beijing_exchange || false;
        }
      } catch (e) {
        console.error('加载北交所配置失败:', e);
      }
    },

    async loadAgentConfig() {
      try {
        const result = await unifiedAgentService.getConfig();
        if (result.success && result.data.config) {
          const config = result.data.config;
          this.agentConfig = {
            analysis_interval: config.analysis_interval || 40,
            reconnect_interval: config.reconnect_interval || 30,
            max_reconnect_attempts: config.max_reconnect_attempts || 10
          };
        }
      } catch (e) {
        console.error('加载Agent配置失败:', e);
      }
    },
    
    async toggleBeijingExchange(e) {
      const enabled = e.detail.value;

      try {
        const result = await unifiedAgentService.toggleBeijingExchange(enabled);

        if (result.success) {
          this.beijingConfig.enabled = enabled;
          uni.showToast({
            title: result.data.message || (enabled ? '北交所权限已开启' : '北交所权限已关闭'),
            icon: 'success'
          });
        } else {
          throw new Error(result.error || '切换失败');
        }
      } catch (e) {
        console.error('切换北交所权限失败:', e);
        uni.showToast({
          title: '切换失败',
          icon: 'none'
        });
        // 恢复开关状态
        this.beijingConfig.enabled = !enabled;
      }
    },
    
    adjustInterval(delta) {
      const newValue = Math.max(10, Math.min(300, this.agentConfig.analysis_interval + delta));
      this.agentConfig.analysis_interval = newValue;
    },
    
    adjustReconnectInterval(delta) {
      const newValue = Math.max(5, Math.min(120, this.agentConfig.reconnect_interval + delta));
      this.agentConfig.reconnect_interval = newValue;
    },
    
    adjustMaxReconnect(delta) {
      const newValue = Math.max(1, Math.min(50, this.agentConfig.max_reconnect_attempts + delta));
      this.agentConfig.max_reconnect_attempts = newValue;
    },
    
    async saveAllConfig() {
      try {
        uni.showLoading({ title: '保存中...' });

        const result = await unifiedAgentService.updateConfig(this.agentConfig);

        if (result.success) {
          uni.showToast({
            title: '配置保存成功',
            icon: 'success'
          });
          this.refreshStatus();
        } else {
          throw new Error(result.error || '保存失败');
        }
      } catch (e) {
        console.error('保存配置失败:', e);
        uni.showToast({
          title: '保存失败',
          icon: 'none'
        });
      } finally {
        uni.hideLoading();
      }
    },
    
    async resetConfig() {
      uni.showModal({
        title: '重置配置',
        content: '确定要重置所有配置为默认值吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              const apiBaseUrl = uni.getStorageSync('apiBaseUrl') || 'https://app.aigupiao.me';
              await uni.request({
                url: `${apiBaseUrl}/api/config/reset`,
                method: 'POST'
              });
              
              uni.showToast({
                title: '配置已重置',
                icon: 'success'
              });
              
              // 重新加载配置
              this.loadSystemStatus();
              this.loadBeijingConfig();
              this.loadAgentConfig();
            } catch (e) {
              uni.showToast({
                title: '重置失败',
                icon: 'none'
              });
            }
          }
        }
      });
    },
    
    async testConnection() {
      try {
        uni.showLoading({ title: '测试中...' });

        // 检查连接状态
        await unifiedAgentService.checkConnections();

        const status = unifiedAgentService.connectionStatus;

        let content = '连接状态:\n';
        content += `云端: ${status.cloud ? '✅ 正常' : '❌ 失败'}\n`;
        content += `本地: ${status.local ? '✅ 正常' : '❌ 失败'}\n`;
        content += `WebSocket: ${status.websocket ? '✅ 正常' : '❌ 失败'}`;

        uni.showModal({
          title: '连接测试',
          content: content,
          showCancel: false
        });

      } catch (e) {
        uni.showModal({
          title: '连接测试',
          content: '连接测试失败，请检查网络设置',
          showCancel: false
        });
      } finally {
        uni.hideLoading();
      }
    },
    
    async refreshStatus() {
      await this.loadSystemStatus();
      uni.showToast({
        title: '状态已刷新',
        icon: 'none'
      });
    },
    
    formatTime(timeStr) {
      if (!timeStr || timeStr === '未知') return '未知';
      try {
        const date = new Date(timeStr);
        return date.toLocaleString('zh-CN');
      } catch (e) {
        return '未知';
      }
    }
  }
}
</script>

<style>
.container {
  padding: 40rpx;
  min-height: 100vh;
}

.light-theme {
  background-color: #f8f9fa;
  color: #333;
}

.dark-theme {
  background-color: #1a1a1a;
  color: #fff;
}

/* 头部 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40rpx;
}

.title {
  font-size: 48rpx;
  font-weight: bold;
}

.status-indicator {
  padding: 12rpx 24rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
}

.status-indicator.active {
  background-color: #e8f5e8;
  color: #2e7d32;
  border: 1px solid #4caf50;
}

.status-indicator.inactive {
  background-color: #ffeaa7;
  color: #e17055;
  border: 1px solid #fdcb6e;
}

.dark-theme .status-indicator.active {
  background-color: rgba(76, 175, 80, 0.2);
  color: #81c784;
}

.dark-theme .status-indicator.inactive {
  background-color: rgba(253, 203, 110, 0.2);
  color: #ffb74d;
}

/* 卡片通用样式 */
.status-card, .control-card, .config-card {
  background-color: #fff;
  border-radius: 20rpx;
  padding: 40rpx;
  margin-bottom: 40rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
}

.dark-theme .status-card,
.dark-theme .control-card,
.dark-theme .config-card {
  background-color: #2d2d2d;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.3);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.card-title {
  font-size: 36rpx;
  font-weight: bold;
}

.refresh-btn {
  padding: 10rpx;
  cursor: pointer;
}

.refresh-icon {
  font-size: 32rpx;
}

/* 状态网格 */
.status-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30rpx;
}

.status-item {
  text-align: center;
}

.status-label {
  display: block;
  font-size: 24rpx;
  color: #666;
  margin-bottom: 10rpx;
}

.dark-theme .status-label {
  color: #999;
}

.status-value {
  display: block;
  font-size: 28rpx;
  font-weight: bold;
}

/* 北交所状态 */
.beijing-status {
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
}

.beijing-status.enabled {
  background-color: #e8f5e8;
  color: #2e7d32;
  border: 1px solid #4caf50;
}

.beijing-status.disabled {
  background-color: #ffeaa7;
  color: #e17055;
  border: 1px solid #fdcb6e;
}

.dark-theme .beijing-status.enabled {
  background-color: rgba(76, 175, 80, 0.2);
  color: #81c784;
}

.dark-theme .beijing-status.disabled {
  background-color: rgba(253, 203, 110, 0.2);
  color: #ffb74d;
}

/* 控制内容 */
.control-content {
  margin-top: 30rpx;
}

.control-description {
  margin-bottom: 30rpx;
}

.description-text {
  font-size: 28rpx;
  line-height: 1.6;
  color: #666;
}

.dark-theme .description-text {
  color: #ccc;
}

.control-switch {
  margin-bottom: 30rpx;
}

.switch-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  background-color: #f5f5f5;
  border-radius: 15rpx;
}

.dark-theme .switch-container {
  background-color: #3d3d3d;
}

.switch-label {
  font-size: 32rpx;
  font-weight: 500;
}

.beijing-switch {
  transform: scale(1.2);
}

/* 信息提示 */
.control-info {
  background-color: #f0f8ff;
  border-radius: 15rpx;
  padding: 20rpx;
}

.dark-theme .control-info {
  background-color: rgba(70, 130, 180, 0.1);
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 15rpx;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-icon {
  margin-right: 15rpx;
  font-size: 28rpx;
}

.info-text {
  font-size: 26rpx;
  color: #4682b4;
}

.dark-theme .info-text {
  color: #87ceeb;
}

/* 配置列表 */
.config-list {
  margin-top: 30rpx;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25rpx 0;
  border-bottom: 1px solid #eee;
}

.dark-theme .config-item {
  border-bottom-color: #444;
}

.config-item:last-child {
  border-bottom: none;
}

.config-label {
  font-size: 30rpx;
  font-weight: 500;
}

.config-control {
  display: flex;
  align-items: center;
}

.config-value {
  font-size: 28rpx;
  margin-right: 20rpx;
  min-width: 80rpx;
  text-align: center;
}

.config-buttons {
  display: flex;
  gap: 10rpx;
}

.config-btn {
  padding: 8rpx 16rpx;
  font-size: 24rpx;
  border: 1px solid #ddd;
  border-radius: 8rpx;
  background-color: #fff;
  color: #333;
}

.dark-theme .config-btn {
  background-color: #444;
  color: #fff;
  border-color: #666;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 20rpx;
  margin-top: 40rpx;
}

.action-btn {
  flex: 1;
  padding: 25rpx;
  border-radius: 15rpx;
  font-size: 30rpx;
  font-weight: bold;
  border: none;
}

.action-btn.primary {
  background-color: #4c8dff;
  color: #fff;
}

.action-btn.secondary {
  background-color: #6c757d;
  color: #fff;
}

.action-btn.info {
  background-color: #17a2b8;
  color: #fff;
}

.dark-theme .action-btn.primary {
  background-color: #5a9cff;
}

.dark-theme .action-btn.secondary {
  background-color: #7a8288;
}

.dark-theme .action-btn.info {
  background-color: #20c997;
}
</style>
