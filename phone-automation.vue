<template>
  <view class="container">
    <view class="header">
      <text class="title">手机自动操作设置</text>
      <text class="subtitle">通过模拟手势操作实现自动交易</text>
    </view>

    <!-- 连接状态 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">设备连接状态</text>
      </view>
      <view class="status-card" :class="isConnected ? 'connected' : 'disconnected'">
        <view class="status-icon">
          <text class="iconfont">{{ isConnected ? '✓' : '!' }}</text>
        </view>
        <view class="status-info">
          <text class="status-title">{{ isConnected ? '设备已连接' : '设备未连接' }}</text>
          <text class="status-desc">{{ isConnected ? `已连接到 ${deviceInfo.name}` : '请连接您的手机设备' }}</text>
        </view>
      </view>
    </view>

    <!-- 连接设置 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">连接方式</text>
      </view>
      
      <view class="connection-methods">
        <view class="method-item" :class="connectionMethod === 'usb' ? 'active' : ''" @tap="setConnectionMethod('usb')">
          <view class="method-icon">
            <text class="iconfont">📱</text>
          </view>
          <view class="method-info">
            <text class="method-title">USB连接</text>
            <text class="method-desc">通过USB数据线连接您的手机</text>
          </view>
        </view>
        
        <view class="method-item" :class="connectionMethod === 'wifi' ? 'active' : ''" @tap="setConnectionMethod('wifi')">
          <view class="method-icon">
            <text class="iconfont">📶</text>
          </view>
          <view class="method-info">
            <text class="method-title">WIFI连接</text>
            <text class="method-desc">通过无线网络连接您的手机</text>
          </view>
        </view>
      </view>
      
      <view class="connection-action">
        <button class="connect-btn" @tap="connectDevice" v-if="!isConnected">连接设备</button>
        <button class="disconnect-btn" @tap="disconnectDevice" v-else>断开连接</button>
      </view>
      
      <view class="connection-guide">
        <view class="guide-title">
          <text class="guide-title-text">连接指南</text>
        </view>
        <view class="guide-steps">
          <view class="guide-step">
            <text class="step-number">1</text>
            <text class="step-desc">在手机上开启USB调试或WIFI调试功能</text>
          </view>
          <view class="guide-step">
            <text class="step-number">2</text>
            <text class="step-desc">允许电脑连接到您的手机设备</text>
          </view>
          <view class="guide-step">
            <text class="step-number">3</text>
            <text class="step-desc">确保手机已安装相应的股票交易软件</text>
          </view>
          <view class="guide-step">
            <text class="step-number">4</text>
            <text class="step-desc">点击"连接设备"按钮完成配对</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 交易软件设置 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">交易软件设置</text>
      </view>
      
      <view class="app-selection">
        <text class="form-label">选择交易软件</text>
        <picker @change="handleAppChange" :value="appIndex" :range="tradingApps">
          <view class="picker-view">
            {{ tradingApps[appIndex] }}
            <text class="iconfont">▼</text>
          </view>
        </picker>
      </view>
      
      <view class="app-config">
        <text class="form-label">界面布局设置</text>
        <view class="layout-options">
          <text class="layout-tip">请确保您的交易软件使用默认布局,以保证自动操作的准确性</text>
          <view class="sample-layout">
            <image class="sample-image" src="/static/sample-layout.png" mode="aspectFit"></image>
            <text class="sample-desc">示例界面布局</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 操作配置 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">操作配置</text>
      </view>
      
      <view class="operation-settings">
        <view class="form-item">
          <text class="form-label">交易延迟设置 (秒)</text>
          <slider 
            :value="operationDelay" 
            @change="setOperationDelay" 
            min="1" 
            max="10" 
            show-value
          />
          <text class="setting-tip">较长的延迟可以提高操作的稳定性,但会降低交易速度</text>
        </view>
        
        <view class="form-item">
          <text class="form-label">操作安全性</text>
          <view class="safety-options">
            <view class="checkbox-item">
              <checkbox :checked="safetySettings.confirmBeforeTrade" @tap="toggleSafety('confirmBeforeTrade')" />
              <text class="checkbox-label">交易前确认</text>
            </view>
            <view class="checkbox-item">
              <checkbox :checked="safetySettings.limitTradeFrequency" @tap="toggleSafety('limitTradeFrequency')" />
              <text class="checkbox-label">限制交易频率</text>
            </view>
            <view class="checkbox-item">
              <checkbox :checked="safetySettings.emergencyStop" @tap="toggleSafety('emergencyStop')" />
              <text class="checkbox-label">启用紧急停止功能</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 测试与验证 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">测试与验证</text>
      </view>
      
      <view class="test-area">
        <text class="test-desc">在应用自动操作前,您可以测试各项功能是否正常工作</text>
        
        <view class="test-buttons">
          <button class="test-btn" @tap="testOperation('refresh')" :disabled="!isConnected">测试刷新</button>
          <button class="test-btn" @tap="testOperation('navigate')" :disabled="!isConnected">测试导航</button>
          <button class="test-btn warning" @tap="testOperation('mockBuy')" :disabled="!isConnected">模拟买入</button>
          <button class="test-btn warning" @tap="testOperation('mockSell')" :disabled="!isConnected">模拟卖出</button>
        </view>
        
        <view class="test-result" v-if="testResult">
          <text class="result-title">测试结果</text>
          <text class="result-content" :class="testSuccess ? 'success' : 'error'">
            {{ testResultMessage }}
          </text>
        </view>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-buttons">
      <button class="btn-cancel" @tap="navigateBack">取消</button>
      <button class="btn-submit" @tap="saveSettings" :disabled="!isConnected">保存设置</button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      isConnected: false,
      deviceInfo: {
        name: "",
        model: "",
        osVersion: ""
      },
      connectionMethod: 'usb',
      tradingApps: ['东方财富证券', '华泰证券', '招商证券', '国泰君安', '中信证券', '其他'],
      appIndex: 0,
      operationDelay: 3,
      safetySettings: {
        confirmBeforeTrade: true,
        limitTradeFrequency: true,
        emergencyStop: true
      },
      testResult: false,
      testSuccess: false,
      testResultMessage: ""
    }
  },
  methods: {
    setConnectionMethod(method) {
      this.connectionMethod = method;
    },
    connectDevice() {
      uni.showLoading({
        title: '连接中...'
      });
      
      // 模拟连接过程
      setTimeout(() => {
        uni.hideLoading();
        
        // 根据连接方式,显示不同的连接提示
        if (this.connectionMethod === 'usb') {
          uni.showModal({
            title: '连接设备',
            content: '请确保USB调试已开启,并允许本应用访问您的设备',
            success: (res) => {
              if (res.confirm) {
                // 模拟连接成功
                this.mockSuccessfulConnection();
              }
            }
          });
        } else {
          uni.showModal({
            title: 'WIFI连接',
            content: '请在手机上打开WIFI调试,并输入配对码:123456',
            success: (res) => {
              if (res.confirm) {
                // 模拟连接成功
                this.mockSuccessfulConnection();
              }
            }
          });
        }
      }, 1500);
    },
    mockSuccessfulConnection() {
      // 模拟成功连接手机
      setTimeout(() => {
        this.isConnected = true;
        this.deviceInfo = {
          name: "您的手机",
          model: "高端手机型号",
          osVersion: "Android 12.0"
        };
        
        uni.showToast({
          title: '设备连接成功',
          icon: 'success'
        });
      }, 1000);
    },
    disconnectDevice() {
      uni.showLoading({
        title: '断开连接中...'
      });
      
      // 模拟断开连接
      setTimeout(() => {
        uni.hideLoading();
        this.isConnected = false;
        this.deviceInfo = {
          name: "",
          model: "",
          osVersion: ""
        };
        
        uni.showToast({
          title: '已断开连接',
          icon: 'success'
        });
      }, 800);
    },
    handleAppChange(e) {
      this.appIndex = e.detail.value;
    },
    setOperationDelay(e) {
      this.operationDelay = e.detail.value;
    },
    toggleSafety(setting) {
      this.safetySettings[setting] = !this.safetySettings[setting];
    },
    testOperation(operation) {
      if (!this.isConnected) {
        uni.showToast({
          title: '请先连接设备',
          icon: 'none'
        });
        return;
      }
      
      uni.showLoading({
        title: '测试中...'
      });
      
      // 模拟测试过程
      setTimeout(() => {
        uni.hideLoading();
        this.testResult = true;
        
        // 根据操作类型返回不同的测试结果
        switch(operation) {
          case 'refresh':
            this.testSuccess = true;
            this.testResultMessage = "刷新操作测试成功!";
            break;
          case 'navigate':
            this.testSuccess = true;
            this.testResultMessage = "导航操作测试成功!";
            break;
          case 'mockBuy':
            this.testSuccess = true;
            this.testResultMessage = "模拟买入操作测试成功!系统能够正确定位并点击买入按钮。";
            break;
          case 'mockSell':
            this.testSuccess = true;
            this.testResultMessage = "模拟卖出操作测试成功!系统能够正确定位并点击卖出按钮。";
            break;
        }
      }, 2000);
    },
    saveSettings() {
      if (!this.isConnected) {
        uni.showToast({
          title: '请先连接设备',
          icon: 'none'
        });
        return;
      }
      
      uni.showLoading({
        title: '保存设置中'
      });
      
      // 模拟保存设置
      setTimeout(() => {
        uni.hideLoading();
        
        uni.showModal({
          title: '设置保存成功',
          content: '手机自动操作设置已保存成功,自动交易功能已准备就绪',
          showCancel: false,
          success: (res) => {
            if (res.confirm) {
              this.navigateBack();
            }
          }
        });
      }, 1500);
    },
    navigateBack() {
      uni.navigateBack();
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

/* 状态卡片样式 */
.status-card {
  display: flex;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
}

.connected {
  background-color: #e8f5e9;
}

.disconnected {
  background-color: #ffebee;
}

.status-icon {
  width: 40px;
  height: 40px;
  border-radius: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 15px;
}

.connected .status-icon {
  background-color: #4caf50;
}

.disconnected .status-icon {
  background-color: #f44336;
}

.iconfont {
  font-size: 24px;
  color: white;
}

.status-info {
  flex: 1;
}

.status-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
}

.connected .status-title {
  color: #2e7d32;
}

.disconnected .status-title {
  color: #c62828;
}

.status-desc {
  font-size: 14px;
  color: #666;
}

/* 连接方式样式 */
.connection-methods {
  display: flex;
  margin-bottom: 20px;
}

.method-item {
  flex: 1;
  display: flex;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-right: 10px;
}

.method-item:last-child {
  margin-right: 0;
}

.method-item.active {
  border-color: #0066cc;
  background-color: #e3f2fd;
}

.method-icon {
  margin-right: 10px;
}

.method-info {
  flex: 1;
}

.method-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
  color: #333;
}

.method-desc {
  font-size: 12px;
  color: #666;
}

.connection-action {
  margin-bottom: 20px;
}

.connect-btn, .disconnect-btn {
  width: 100%;
  height: 44px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.connect-btn {
  background-color: #0066cc;
  color: white;
}

.disconnect-btn {
  background-color: #f44336;
  color: white;
}

.connection-guide {
  background-color: #f0f0f0;
  border-radius: 8px;
  padding: 15px;
}

.guide-title {
  margin-bottom: 10px;
}

.guide-title-text {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.guide-steps {
  display: flex;
  flex-direction: column;
}

.guide-step {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.guide-step:last-child {
  margin-bottom: 0;
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 12px;
  background-color: #0066cc;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 14px;
  margin-right: 10px;
}

.step-desc {
  font-size: 14px;
  color: #333;
}

/* 交易软件设置样式 */
.app-selection {
  margin-bottom: 20px;
}

.form-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
  display: block;
}

.picker-view {
  width: 100%;
  height: 44px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0 12px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
}

.layout-options {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.layout-tip {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
  display: block;
}

.sample-layout {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.sample-image {
  width: 200px;
  height: 150px;
  background-color: #eee;
  border: 1px solid #ddd;
  margin-bottom: 5px;
  border-radius: 4px;
}

.sample-desc {
  font-size: 12px;
  color: #999;
}

/* 操作配置样式 */
.form-item {
  margin-bottom: 20px;
}

.form-item:last-child {
  margin-bottom: 0;
}

.setting-tip {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
  display: block;
}

.safety-options {
  margin-top: 10px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.checkbox-item:last-child {
  margin-bottom: 0;
}

.checkbox-label {
  font-size: 14px;
  color: #333;
  margin-left: 8px;
}

/* 测试区域样式 */
.test-area {
  display: flex;
  flex-direction: column;
}

.test-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
}

.test-buttons {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -5px;
  margin-bottom: 15px;
}

.test-btn {
  flex: 1 0 40%;
  margin: 0 5px 10px;
  height: 40px;
  font-size: 14px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #0066cc;
  color: white;
}

.test-btn.warning {
  background-color: #ff9800;
}

.test-btn:disabled {
  background-color: #cccccc;
  color: #666;
}

.test-result {
  background-color: #f0f0f0;
  padding: 15px;
  border-radius: 8px;
}

.result-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 5px;
  color: #333;
}

.result-content {
  font-size: 14px;
}

.result-content.success {
  color: #2e7d32;
}

.result-content.error {
  color: #c62828;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.btn-cancel, .btn-submit {
  width: 48%;
  height: 44px;
  border-radius: 4px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-cancel {
  background-color: #f0f0f0;
  color: #666;
}

.btn-submit {
  background-color: #0066cc;
  color: white;
}

.btn-submit:disabled {
  background-color: #cccccc;
  color: #999;
}
</style> 
