<template>
  <view class="container">
    <view class="header">
      <text class="title">数据获取测试</text>
      <text class="subtitle">测试回测功能和真实股票数据获取</text>
    </view>

    <!-- 测试按钮区域 -->
    <view class="test-section">
      <view class="section-title">功能测试</view>
      
      <view class="button-group">
        <button class="test-btn" @click="testStockData" :disabled="loading">
          <text class="btn-text">测试股票数据获取</text>
        </button>
        
        <button class="test-btn" @click="testBacktest" :disabled="loading">
          <text class="btn-text">测试回测功能</text>
        </button>
        
        <button class="test-btn" @click="testAgentConnection" :disabled="loading">
          <text class="btn-text">测试Agent连接</text>
        </button>
        
        <button class="test-btn" @click="clearResults">
          <text class="btn-text">清除结果</text>
        </button>
      </view>
    </view>

    <!-- 加载状态 -->
    <view v-if="loading" class="loading">
      <text class="loading-text">{{ loadingText }}</text>
    </view>

    <!-- 测试结果显示 -->
    <view v-if="results.length > 0" class="results-section">
      <view class="section-title">测试结果</view>
      
      <view v-for="(result, index) in results" :key="index" class="result-item">
        <view class="result-header">
          <text class="result-title">{{ result.title }}</text>
          <text class="result-time">{{ result.timestamp }}</text>
          <text :class="['result-status', result.success ? 'success' : 'error']">
            {{ result.success ? '成功' : '失败' }}
          </text>
        </view>
        
        <view class="result-content">
          <text class="result-text">{{ result.message }}</text>
          
          <!-- 股票数据结果 -->
          <view v-if="result.type === 'stock' && result.data" class="stock-data">
            <view v-for="(stock, symbol) in result.data" :key="symbol" class="stock-item">
              <text class="stock-symbol">{{ symbol }} - {{ stock.name }}</text>
              <text class="stock-price">价格: ¥{{ stock.current_price }}</text>
              <text :class="['stock-change', stock.change >= 0 ? 'positive' : 'negative']">
                涨跌: {{ stock.change >= 0 ? '+' : '' }}{{ stock.change_percent.toFixed(2) }}%
              </text>
            </view>
          </view>
          
          <!-- 回测结果 -->
          <view v-if="result.type === 'backtest' && result.data" class="backtest-data">
            <view class="backtest-summary">
              <text class="backtest-item">策略: {{ result.data.strategy }}</text>
              <text class="backtest-item">初始资金: ¥{{ result.data.initial_capital }}</text>
              <text class="backtest-item">最终价值: ¥{{ result.data.final_value.toFixed(2) }}</text>
              <text :class="['backtest-item', result.data.total_return >= 0 ? 'positive' : 'negative']">
                总收益率: {{ result.data.total_return_pct.toFixed(2) }}%
              </text>
              <text class="backtest-item">最大回撤: {{ (result.data.max_drawdown * 100).toFixed(2) }}%</text>
              <text class="backtest-item">胜率: {{ (result.data.win_rate * 100).toFixed(2) }}%</text>
              <text class="backtest-item">交易次数: {{ result.data.total_trades }}</text>
            </view>
          </view>
          
          <!-- 原始数据 -->
          <view v-if="showRawData" class="raw-data">
            <text class="raw-data-title">原始数据:</text>
            <text class="raw-data-content">{{ JSON.stringify(result.rawData, null, 2) }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 设置区域 -->
    <view class="settings-section">
      <view class="section-title">设置</view>
      
      <view class="setting-item">
        <text class="setting-label">显示原始数据</text>
        <switch :checked="showRawData" @change="toggleRawData" />
      </view>
      
      <view class="setting-item">
        <text class="setting-label">测试股票代码</text>
        <input class="setting-input" v-model="testSymbols" placeholder="000001,600000,600519" />
      </view>
    </view>
  </view>
</template>

<script>
import agentDataService from '@/services/agentDataService.js';

export default {
  data() {
    return {
      loading: false,
      loadingText: '',
      results: [],
      showRawData: false,
      testSymbols: '000001,600000,600519'
    };
  },
  
  methods: {
    async testStockData() {
      this.loading = true;
      this.loadingText = '正在获取股票数据...';
      
      try {
        const symbols = this.testSymbols.split(',').map(s => s.trim());
        const result = await agentDataService.getStockData(symbols);
        
        this.addResult({
          type: 'stock',
          title: '股票数据获取测试',
          success: result.success,
          message: result.success ? 
            `成功获取 ${symbols.length} 只股票的数据${result.source === 'mock' ? ' (模拟数据)' : ' (真实数据)'}` :
            '股票数据获取失败',
          data: result.data,
          rawData: result
        });
      } catch (error) {
        this.addResult({
          type: 'stock',
          title: '股票数据获取测试',
          success: false,
          message: `获取失败: ${error.message}`,
          rawData: { error: error.message }
        });
      } finally {
        this.loading = false;
      }
    },
    
    async testBacktest() {
      this.loading = true;
      this.loadingText = '正在运行回测...';
      
      try {
        const symbols = this.testSymbols.split(',').map(s => s.trim());
        const config = {
          strategy: 'ma_crossover',
          symbols: symbols,
          start_date: '2023-01-01',
          end_date: '2024-01-01',
          initial_capital: 100000
        };
        
        const result = await agentDataService.runBacktest(config);
        
        this.addResult({
          type: 'backtest',
          title: '回测功能测试',
          success: result.success,
          message: result.success ? 
            `回测完成${result.source === 'mock' ? ' (模拟结果)' : ' (真实结果)'}` :
            '回测运行失败',
          data: result.data,
          rawData: result
        });
      } catch (error) {
        this.addResult({
          type: 'backtest',
          title: '回测功能测试',
          success: false,
          message: `回测失败: ${error.message}`,
          rawData: { error: error.message }
        });
      } finally {
        this.loading = false;
      }
    },
    
    async testAgentConnection() {
      this.loading = true;
      this.loadingText = '正在测试Agent连接...';
      
      try {
        const result = await agentDataService.testConnection();
        
        this.addResult({
          type: 'connection',
          title: 'Agent连接测试',
          success: result.success,
          message: result.message,
          rawData: result
        });
      } catch (error) {
        this.addResult({
          type: 'connection',
          title: 'Agent连接测试',
          success: false,
          message: `连接测试失败: ${error.message}`,
          rawData: { error: error.message }
        });
      } finally {
        this.loading = false;
      }
    },
    
    addResult(result) {
      result.timestamp = new Date().toLocaleTimeString();
      this.results.unshift(result);
      
      // 只保留最近10条结果
      if (this.results.length > 10) {
        this.results = this.results.slice(0, 10);
      }
    },
    
    clearResults() {
      this.results = [];
    },
    
    toggleRawData(e) {
      this.showRawData = e.detail.value;
    }
  },
  
  onLoad() {
    console.log('数据测试页面加载');
  }
};
</script>

<style>
.container {
  padding: 30rpx;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 40rpx;
}

.title {
  font-size: 48rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 10rpx;
}

.subtitle {
  font-size: 28rpx;
  color: #666;
  display: block;
}

.test-section, .results-section, .settings-section {
  background: white;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.1);
}

.section-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 30rpx;
  display: block;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.test-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 15rpx;
  padding: 25rpx;
  font-size: 32rpx;
}

.test-btn[disabled] {
  background: #ccc;
}

.btn-text {
  color: white;
  font-size: 32rpx;
}

.loading {
  text-align: center;
  padding: 40rpx;
}

.loading-text {
  font-size: 32rpx;
  color: #666;
}

.result-item {
  border: 2rpx solid #eee;
  border-radius: 15rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
}

.result-header {
  background: #f8f9fa;
  padding: 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.result-time {
  font-size: 24rpx;
  color: #999;
}

.result-status {
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
  font-size: 24rpx;
  color: white;
}

.result-status.success {
  background: #28a745;
}

.result-status.error {
  background: #dc3545;
}

.result-content {
  padding: 20rpx;
}

.result-text {
  font-size: 28rpx;
  color: #666;
  display: block;
  margin-bottom: 20rpx;
}

.stock-data, .backtest-data {
  margin-top: 20rpx;
}

.stock-item, .backtest-item {
  display: block;
  padding: 10rpx 0;
  font-size: 26rpx;
  border-bottom: 1rpx solid #eee;
}

.stock-symbol {
  font-weight: bold;
  color: #333;
}

.positive {
  color: #28a745;
}

.negative {
  color: #dc3545;
}

.raw-data {
  margin-top: 20rpx;
  padding: 20rpx;
  background: #f8f9fa;
  border-radius: 10rpx;
}

.raw-data-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 10rpx;
}

.raw-data-content {
  font-size: 24rpx;
  color: #666;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #eee;
}

.setting-label {
  font-size: 30rpx;
  color: #333;
}

.setting-input {
  border: 2rpx solid #ddd;
  border-radius: 10rpx;
  padding: 15rpx;
  font-size: 28rpx;
  width: 300rpx;
}
</style>
