<template>
  <view class="container">
    <view class="header">
      <text class="title">技术指标分析</text>
    </view>
    
    <view class="search-bar">
      <input 
        class="search-input" 
        type="text" 
        v-model="searchQuery" 
        placeholder="搜索股票代码或名称"
        @input="searchStocks"
      />
      <button class="search-button" @click="searchStocks">搜索</button>
    </view>
    
    <view class="indicator-panel">
      <view class="indicator-selection">
        <text class="section-title">选择技术指标</text>
        <checkbox-group @change="onIndicatorChange">
          <label v-for="(indicator, index) in availableIndicators" :key="index" class="indicator-checkbox">
            <checkbox :value="indicator.value" :checked="indicator.checked" color="#4c8dff" />
            <text>{{indicator.label}}</text>
          </label>
        </checkbox-group>
      </view>
      
      <view class="time-range">
        <text class="section-title">时间范围</text>
        <radio-group @change="onTimeRangeChange">
          <label v-for="(range, index) in timeRanges" :key="index" class="time-radio">
            <radio :value="range.value" :checked="range.value === selectedTimeRange" color="#4c8dff" />
            <text>{{range.label}}</text>
          </label>
        </radio-group>
      </view>
    </view>
    
    <view v-if="currentStock" class="chart-container">
      <view class="stock-info">
        <text class="stock-name">{{currentStock.name}}</text>
        <text class="stock-code">{{currentStock.code}}</text>
        <text class="stock-price">{{currentStock.price}}</text>
        <text class="stock-change" :class="currentStock.change >= 0 ? 'price-up' : 'price-down'">
          {{currentStock.change >= 0 ? '+' : ''}}{{currentStock.change}}%
        </text>
      </view>
      
      <view class="candlestick-chart">
        <!-- 蜡烛图表将在这里渲染 -->
        <text class="placeholder">K线图</text>
      </view>
      
      <view v-for="(indicator, index) in selectedIndicators" :key="index" class="indicator-chart">
        <text class="indicator-title">{{indicator.label}}</text>
        <!-- 指标图表将在这里渲染 -->
        <text class="placeholder">{{indicator.label}}图表</text>
      </view>
    </view>
    
    <view v-else class="empty-state">
      <text class="empty-text">请搜索并选择股票以查看技术指标</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      searchQuery: '',
      currentStock: null,
      availableIndicators: [
        { label: 'MACD', value: 'macd', checked: true },
        { label: 'RSI', value: 'rsi', checked: false },
        { label: 'KDJ', value: 'kdj', checked: false },
        { label: '布林带', value: 'bollinger', checked: false },
        { label: '移动平均线', value: 'ma', checked: true },
        { label: '成交量', value: 'volume', checked: true }
      ],
      selectedIndicators: [],
      timeRanges: [
        { label: '日线', value: 'daily' },
        { label: '周线', value: 'weekly' },
        { label: '月线', value: 'monthly' },
        { label: '60分钟', value: '60min' },
        { label: '30分钟', value: '30min' },
        { label: '15分钟', value: '15min' }
      ],
      selectedTimeRange: 'daily',
      stockSuggestions: []
    }
  },
  created() {
    // 初始化选中的指标
    this.selectedIndicators = this.availableIndicators.filter(item => item.checked);
  },
  methods: {
    searchStocks() {
      // 模拟股票搜索
      if (this.searchQuery.length > 0) {
        // 这里应该调用API获取股票数据
        setTimeout(() => {
          this.currentStock = {
            code: '600000',
            name: '浦发银行',
            price: '10.25',
            change: 2.15
          };
        }, 500);
      }
    },
    onIndicatorChange(e) {
      const values = e.detail.value;
      this.selectedIndicators = this.availableIndicators.filter(item => 
        values.includes(item.value)
      ).map(item => ({
        label: item.label,
        value: item.value
      }));
      
      // 更新指标选中状态
      this.availableIndicators.forEach(item => {
        item.checked = values.includes(item.value);
      });
      
      this.updateCharts();
    },
    onTimeRangeChange(e) {
      this.selectedTimeRange = e.detail.value;
      this.updateCharts();
    },
    updateCharts() {
      // 此处应该根据所选指标和时间范围更新图表
      console.log('Updating charts with:', {
        indicators: this.selectedIndicators,
        timeRange: this.selectedTimeRange
      });
    }
  }
}
</script>

<style>
.container {
  background-color: #141414;
  color: #eee;
  min-height: 100vh;
  padding: 20rpx;
}

.header {
  padding: 20rpx 0;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
}

.search-bar {
  display: flex;
  margin: 20rpx 0;
}

.search-input {
  flex: 1;
  background-color: #222;
  color: #eee;
  padding: 10rpx 20rpx;
  border-radius: 8rpx;
  margin-right: 20rpx;
  border: 1px solid #333;
}

.search-button {
  background-color: #4c8dff;
  color: white;
  border: none;
  border-radius: 8rpx;
  padding: 0 30rpx;
}

.indicator-panel {
  background-color: #222;
  border-radius: 10rpx;
  padding: 20rpx;
  margin: 20rpx 0;
}

.section-title {
  font-size: 30rpx;
  margin-bottom: 20rpx;
  display: block;
}

.indicator-checkbox, .time-radio {
  margin-right: 30rpx;
  display: inline-block;
  margin-bottom: 20rpx;
}

.time-range {
  margin-top: 30rpx;
}

.chart-container {
  background-color: #222;
  border-radius: 10rpx;
  padding: 20rpx;
  margin: 20rpx 0;
}

.stock-info {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
}

.stock-name {
  font-size: 32rpx;
  font-weight: bold;
  margin-right: 20rpx;
}

.stock-code {
  color: #999;
  margin-right: 40rpx;
}

.stock-price {
  font-size: 32rpx;
  font-weight: bold;
  margin-right: 20rpx;
}

.stock-change {
  font-size: 28rpx;
}

.price-up {
  color: #ff5252;
}

.price-down {
  color: #4caf50;
}

.candlestick-chart, .indicator-chart {
  height: 400rpx;
  background-color: #1a1a1a;
  border-radius: 8rpx;
  margin-bottom: 30rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}

.indicator-title {
  font-size: 28rpx;
  margin-bottom: 10rpx;
  display: block;
}

.placeholder {
  color: #666;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400rpx;
  background-color: #222;
  border-radius: 10rpx;
  margin: 20rpx 0;
}

.empty-text {
  color: #666;
  font-size: 28rpx;
}
</style> 
