<template>
  <view class="container">
    <view class="header">
      <text class="title">快速设置</text>
      <text class="subtitle">简单几步配置自动交易</text>
    </view>

    <!-- 步骤导航 -->
    <view class="step-nav">
      <view 
        v-for="(step, index) in steps" 
        :key="index"
        class="step-item"
        :class="{ 'active': currentStep === index, 'completed': index < currentStep }"
        @tap="goToStep(index)"
      >
        <text class="step-number">{{ index + 1 }}</text>
        <text class="step-name">{{ step.name }}</text>
      </view>
    </view>

    <!-- 手机连接步骤 -->
    <view class="step-content" v-if="currentStep === 0">
      <view class="section">
        <view class="section-header">
          <text class="section-title">连接您的手机</text>
        </view>

        <view class="qrcode-section">
          <view class="qrcode-container">
            <image class="qrcode" src="/static/qrcode.png"></image>
          </view>
          <view class="qrcode-instructions">
            <text class="instruction-title">扫描上方二维码</text>
            <text class="instruction-text">1. 用手机扫描二维码</text>
            <text class="instruction-text">2. 下载并安装助手APP</text>
            <text class="instruction-text">3. 打开APP并点击"连接电脑"</text>
          </view>
        </view>

        <view class="connection-status" :class="isConnected ? 'connected' : ''">
          <text class="status-text">{{ isConnected ? '已连接' : '等待连接...' }}</text>
          <text class="device-info" v-if="isConnected">{{ deviceInfo.name }}</text>
        </view>

        <view class="manual-connection">
          <text class="manual-title">手动连接</text>
          <text class="manual-text">您也可以通过输入配对码连接</text>
          <view class="pairing-code">
            <text class="code-text">123456</text>
            <text class="code-refresh" @tap="refreshCode">刷新</text>
          </view>
        </view>
      </view>

      <view class="step-actions">
        <button class="btn-next" @tap="nextStep" :disabled="!isConnected">下一步</button>
      </view>
    </view>

    <!-- 交易软件选择步骤 -->
    <view class="step-content" v-if="currentStep === 1">
      <view class="section">
        <view class="section-header">
          <text class="section-title">选择交易软件</text>
        </view>

        <view class="app-grid">
          <view 
            v-for="(app, index) in tradingApps" 
            :key="index"
            class="app-item"
            :class="{ 'selected': selectedAppIndex === index }"
            @tap="selectApp(index)"
          >
            <view class="app-icon">{{ app.icon }}</view>
            <text class="app-name">{{ app.name }}</text>
          </view>
        </view>

        <view class="app-version" v-if="selectedAppIndex !== null">
          <text class="version-label">软件版本</text>
          <picker @change="handleVersionChange" :value="versionIndex" :range="appVersions">
            <view class="version-picker">
              {{ appVersions[versionIndex] }}
              <text class="picker-arrow">▼</text>
            </view>
          </picker>
        </view>
      </view>

      <view class="step-actions">
        <button class="btn-prev" @tap="prevStep">上一步</button>
        <button class="btn-next" @tap="nextStep" :disabled="selectedAppIndex === null">下一步</button>
      </view>
    </view>

    <!-- 自动交易设置步骤 -->
    <view class="step-content" v-if="currentStep === 2">
      <view class="section">
        <view class="section-header">
          <text class="section-title">交易设置</text>
        </view>

        <view class="settings-group">
          <view class="setting-item">
            <text class="setting-label">交易确认</text>
            <switch :checked="tradeSettings.confirmTrade" @change="toggleSetting('confirmTrade')" color="#0066cc" />
          </view>
          <text class="setting-desc">执行买入或卖出前进行确认</text>

          <view class="setting-item">
            <text class="setting-label">单笔最大金额</text>
            <input 
              type="digit" 
              v-model="tradeSettings.maxAmount" 
              class="setting-input"
              placeholder="输入金额"
            />
            <text class="input-unit">元</text>
          </view>
          <text class="setting-desc">单次交易的最大金额限制</text>

          <view class="setting-item">
            <text class="setting-label">交易间隔</text>
            <slider 
              :value="tradeSettings.interval" 
              @change="setTradeInterval" 
              min="1" 
              max="10" 
              show-value
              class="setting-slider"
            />
          </view>
          <text class="setting-desc">两次交易之间的最小间隔时间(分钟)</text>

          <view class="setting-item">
            <text class="setting-label">交易时段</text>
            <picker 
              mode="time" 
              :value="tradeSettings.startTime" 
              @change="setStartTime"
              class="time-picker"
            >
              <view class="time-value">{{ tradeSettings.startTime }}</view>
            </picker>
            <text class="time-separator">至</text>
            <picker 
              mode="time" 
              :value="tradeSettings.endTime" 
              @change="setEndTime"
              class="time-picker"
            >
              <view class="time-value">{{ tradeSettings.endTime }}</view>
            </picker>
          </view>
          <text class="setting-desc">只在指定时间段内进行交易</text>
        </view>
      </view>

      <view class="step-actions">
        <button class="btn-prev" @tap="prevStep">上一步</button>
        <button class="btn-next" @tap="nextStep">下一步</button>
      </view>
    </view>

    <!-- 完成设置步骤 -->
    <view class="step-content" v-if="currentStep === 3">
      <view class="section">
        <view class="section-header">
          <text class="section-title">设置完成</text>
        </view>

        <view class="setup-summary">
          <text class="summary-title">自动交易设置已完成</text>
          <view class="summary-item">
            <text class="summary-label">连接设备:</text>
            <text class="summary-value">{{ deviceInfo.name }}</text>
          </view>
          <view class="summary-item">
            <text class="summary-label">交易软件:</text>
            <text class="summary-value">{{ selectedAppIndex !== null ? tradingApps[selectedAppIndex].name : '未选择' }}</text>
          </view>
          <view class="summary-item">
            <text class="summary-label">软件版本:</text>
            <text class="summary-value">{{ appVersions[versionIndex] }}</text>
          </view>
          <view class="summary-item">
            <text class="summary-label">交易确认:</text>
            <text class="summary-value">{{ tradeSettings.confirmTrade ? '开启' : '关闭' }}</text>
          </view>
          <view class="summary-item">
            <text class="summary-label">单笔限额:</text>
            <text class="summary-value">{{ tradeSettings.maxAmount }}元</text>
          </view>
          <view class="summary-item">
            <text class="summary-label">交易间隔:</text>
            <text class="summary-value">{{ tradeSettings.interval }}分钟</text>
          </view>
          <view class="summary-item">
            <text class="summary-label">交易时段:</text>
            <text class="summary-value">{{ tradeSettings.startTime }} - {{ tradeSettings.endTime }}</text>
          </view>
        </view>

        <view class="activation-toggle">
          <text class="toggle-label">自动交易</text>
          <switch :checked="isActivated" @change="toggleActivation" color="#0066cc" />
          <text class="toggle-status">{{ isActivated ? '已启用' : '未启用' }}</text>
        </view>

        <view class="notice-box">
          <text class="notice-title">注意事项</text>
          <text class="notice-text">1. 请保持手机与电脑的连接</text>
          <text class="notice-text">2. 确保交易软件处于前台状态</text>
          <text class="notice-text">3. 为保证交易安全,建议设置单笔交易限额</text>
        </view>
      </view>

      <view class="step-actions">
        <button class="btn-prev" @tap="prevStep">上一步</button>
        <button class="btn-complete" @tap="completeSetup">完成设置</button>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      steps: [
        { name: '连接手机' },
        { name: '选择软件' },
        { name: '交易设置' },
        { name: '完成' }
      ],
      currentStep: 0,
      isConnected: false,
      deviceInfo: {
        name: '小米12 Pro',
        model: 'M2001J1C',
        osVersion: 'Android 12'
      },
      tradingApps: [
        { name: '东方财富', icon: '东' },
        { name: '华泰证券', icon: '华' },
        { name: '国泰君安', icon: '泰' },
        { name: '招商证券', icon: '招' },
        { name: '中信证券', icon: '中' }
      ],
      selectedAppIndex: null,
      appVersions: ['最新版本', 'v5.6.2', 'v5.5.0', 'v5.4.8', '其他版本'],
      versionIndex: 0,
      tradeSettings: {
        confirmTrade: true,
        maxAmount: '5000',
        interval: 5,
        startTime: '09:30',
        endTime: '14:30'
      },
      isActivated: false
    }
  },
  mounted() {
    // 模拟自动连接设备
    setTimeout(() => {
      this.isConnected = true;
    }, 3000);
  },
  methods: {
    goToStep(index) {
      // 只允许跳转到已完成步骤或下一步
      if (index <= this.currentStep) {
        this.currentStep = index;
      }
    },
    nextStep() {
      if (this.currentStep < this.steps.length - 1) {
        this.currentStep++;
      }
    },
    prevStep() {
      if (this.currentStep > 0) {
        this.currentStep--;
      }
    },
    refreshCode() {
      uni.showToast({
        title: '配对码已更新',
        icon: 'success'
      });
    },
    selectApp(index) {
      this.selectedAppIndex = index;
    },
    handleVersionChange(e) {
      this.versionIndex = e.detail.value;
    },
    toggleSetting(setting) {
      this.tradeSettings[setting] = !this.tradeSettings[setting];
    },
    setTradeInterval(e) {
      this.tradeSettings.interval = e.detail.value;
    },
    setStartTime(e) {
      this.tradeSettings.startTime = e.detail.value;
    },
    setEndTime(e) {
      this.tradeSettings.endTime = e.detail.value;
    },
    toggleActivation(e) {
      this.isActivated = e.detail.value;
    },
    completeSetup() {
      uni.showLoading({
        title: '保存设置中'
      });
      
      // 模拟保存设置过程
      setTimeout(() => {
        uni.hideLoading();
        
        uni.showModal({
          title: '设置完成',
          content: '自动交易设置已保存,您可以随时在设置中修改这些选项。',
          showCancel: false,
          success: (res) => {
            if (res.confirm) {
              uni.navigateBack();
            }
          }
        });
      }, 1500);
    }
  }
}
</script>

<style>
.container {
  padding: 20px;
  background-color: #f5f5f5;
}

.header {
  margin-bottom: 20px;
}

.title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.subtitle {
  font-size: 14px;
  color: #666;
}

.section {
  background-color: #ffffff;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.section-header {
  margin-bottom: 15px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

/* 步骤导航样式 */
.step-nav {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  background-color: #fff;
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;
}

.step-item:not(:last-child):after {
  content: '';
  position: absolute;
  top: 12px;
  right: -50%;
  width: 100%;
  height: 2px;
  background-color: #ddd;
  z-index: 1;
}

.step-item.active:not(:last-child):after,
.step-item.completed:not(:last-child):after {
  background-color: #0066cc;
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 12px;
  background-color: #ddd;
  color: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 14px;
  margin-bottom: 5px;
  position: relative;
  z-index: 2;
}

.step-item.active .step-number,
.step-item.completed .step-number {
  background-color: #0066cc;
}

.step-name {
  font-size: 12px;
  color: #666;
}

.step-item.active .step-name {
  color: #0066cc;
  font-weight: bold;
}

/* 步骤内容样式 */
.step-content {
  margin-bottom: 20px;
}

/* 手机连接步骤样式 */
.qrcode-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.qrcode-container {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #fff;
  border: 1px solid #eee;
  border-radius: 4px;
}

.qrcode {
  width: 200px;
  height: 200px;
  background-color: #f0f0f0;
}

.qrcode-instructions {
  text-align: center;
}

.instruction-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
  display: block;
}

.instruction-text {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  display: block;
}

.connection-status {
  background-color: #f0f0f0;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 20px;
}

.connection-status.connected {
  background-color: #e8f5e9;
}

.status-text {
  font-size: 16px;
  font-weight: bold;
  color: #666;
  margin-bottom: 5px;
  display: block;
}

.connected .status-text {
  color: #4caf50;
}

.device-info {
  font-size: 14px;
  color: #666;
}

.manual-connection {
  text-align: center;
}

.manual-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
  display: block;
}

.manual-text {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
  display: block;
}

.pairing-code {
  display: flex;
  justify-content: center;
  align-items: center;
}

.code-text {
  font-size: 24px;
  font-weight: bold;
  color: #0066cc;
  letter-spacing: 5px;
  margin-right: 10px;
}

.code-refresh {
  font-size: 14px;
  color: #0066cc;
  text-decoration: underline;
}

/* 交易软件选择步骤样式 */
.app-grid {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -10px 20px;
}

.app-item {
  width: 33.33%;
  padding: 10px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.app-icon {
  width: 60px;
  height: 60px;
  border-radius: 30px;
  background-color: #f0f0f0;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 8px;
  font-size: 24px;
  color: #666;
  font-weight: bold;
}

.app-item.selected .app-icon {
  background-color: #0066cc;
  color: white;
}

.app-name {
  font-size: 14px;
  color: #666;
  text-align: center;
}

.app-item.selected .app-name {
  color: #0066cc;
  font-weight: bold;
}

.app-version {
  margin-top: 20px;
}

.version-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
  display: block;
}

.version-picker {
  height: 44px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
}

.picker-arrow {
  font-size: 12px;
  color: #999;
}

/* 自动交易设置步骤样式 */
.settings-group {
  margin-bottom: 20px;
}

.setting-item {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.setting-label {
  font-size: 16px;
  color: #333;
  flex: 1;
}

.setting-desc {
  font-size: 12px;
  color: #999;
  margin-bottom: 15px;
  display: block;
}

.setting-input {
  width: 120px;
  height: 40px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0 12px;
  font-size: 16px;
  text-align: right;
}

.input-unit {
  margin-left: 8px;
  font-size: 14px;
  color: #666;
}

.setting-slider {
  width: 200px;
}

.time-picker {
  width: 100px;
}

.time-value {
  height: 40px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.time-separator {
  margin: 0 8px;
  color: #666;
}

/* 完成设置步骤样式 */
.setup-summary {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.summary-title {
  font-size: 16px;
  font-weight: bold;
  color: #0066cc;
  margin-bottom: 15px;
  display: block;
  text-align: center;
}

.summary-item {
  display: flex;
  margin-bottom: 10px;
}

.summary-label {
  width: 100px;
  font-size: 14px;
  color: #666;
}

.summary-value {
  flex: 1;
  font-size: 14px;
  color: #333;
  font-weight: bold;
}

.activation-toggle {
  display: flex;
  align-items: center;
  padding: 15px;
  background-color: #f0f0f0;
  border-radius: 8px;
  margin-bottom: 20px;
}

.toggle-label {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  flex: 1;
}

.toggle-status {
  font-size: 14px;
  margin-left: 10px;
  color: #666;
}

.notice-box {
  background-color: #fff8e1;
  padding: 15px;
  border-radius: 8px;
}

.notice-title {
  font-size: 16px;
  font-weight: bold;
  color: #ff8f00;
  margin-bottom: 10px;
}

.notice-text {
  font-size: 14px;
  color: #333;
  line-height: 1.5;
  margin-bottom: 5px;
  display: block;
}

/* 步骤操作按钮 */
.step-actions {
  display: flex;
  justify-content: space-between;
}

.btn-prev, .btn-next, .btn-complete {
  height: 44px;
  border-radius: 4px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-prev {
  width: 48%;
  background-color: #f0f0f0;
  color: #666;
}

.btn-next {
  width: 48%;
  background-color: #0066cc;
  color: white;
}

.btn-next:disabled {
  background-color: #cccccc;
  color: #999;
}

.btn-complete {
  width: 48%;
  background-color: #4caf50;
  color: white;
}
</style> 
