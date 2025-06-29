<template>
  <view class="container">
    <view class="header">
      <view class="back-button" @click="navigateBack">
        <text class="back-icon">&#xe607;</text>
      </view>
      <text class="title">多策略对比分析</text>
    </view>
    
    <!-- 策略选择 -->
    <view class="strategy-selection card">
      <text class="section-title">选择策略进行对比</text>
      <view class="strategy-checkboxes">
        <view v-for="(strategy, index) in availableStrategies" :key="index" class="strategy-checkbox">
          <checkbox :checked="selectedStrategies.includes(strategy.id)" @click="toggleStrategy(strategy.id)" />
          <text class="strategy-name">{{ strategy.name }}</text>
        </view>
      </view>
      <button class="compare-btn" @click="compareStrategies">对比分析</button>
    </view>
    
    <!-- 股票选择 -->
    <view class="stock-selection card">
      <text class="section-title">选择分析标的</text>
      <picker @change="onStockChange" :value="currentStockIndex" :range="stockOptions" range-key="name">
        <view class="picker-value">
          <text>{{ currentStock.code }} {{ currentStock.name }}</text>
          <text class="picker-arrow">▼</text>
        </view>
      </picker>
      
      <view class="date-range">
        <view class="date-picker">
          <text class="date-label">开始日期</text>
          <picker mode="date" :value="startDate" @change="onStartDateChange">
            <view class="date-value">{{ startDate }}</view>
          </picker>
        </view>
        <view class="date-picker">
          <text class="date-label">结束日期</text>
          <picker mode="date" :value="endDate" @change="onEndDateChange">
            <view class="date-value">{{ endDate }}</view>
          </picker>
        </view>
      </view>
    </view>
    
    <!-- 绩效对比 -->
    <view class="performance-comparison card" v-if="isCompared">
      <text class="section-title">绩效对比</text>
      
      <view class="chart-container">
        <text class="chart-title">累计收益曲线</text>
        <view class="chart">
          <!-- 图表区域将由图表库渲染 -->
          <view class="chart-placeholder" v-if="!performanceData.length">
            <text>加载中...</text>
          </view>
        </view>
        
        <view class="chart-legend">
          <view v-for="(strategy, index) in comparedStrategies" :key="index" class="legend-item" :style="{ color: strategyColors[index % strategyColors.length] }">
            <view class="legend-color" :style="{ backgroundColor: strategyColors[index % strategyColors.length] }"></view>
            <text>{{ strategy.name }}</text>
          </view>
        </view>
      </view>
      
      <!-- 绩效指标表格 -->
      <view class="metrics-table">
        <view class="table-header">
          <text class="header-cell strategy-cell">策略</text>
          <text class="header-cell">总收益</text>
          <text class="header-cell">年化收益</text>
          <text class="header-cell">最大回撤</text>
          <text class="header-cell">夏普比率</text>
        </view>
        
        <view v-for="(strategy, index) in comparedStrategies" :key="index" class="table-row">
          <text class="cell strategy-cell">{{ strategy.name }}</text>
          <text class="cell" :class="getCellClass(strategy.totalReturn)">{{ formatPercent(strategy.totalReturn) }}</text>
          <text class="cell" :class="getCellClass(strategy.annualReturn)">{{ formatPercent(strategy.annualReturn) }}</text>
          <text class="cell" :class="getCellClass(-strategy.maxDrawdown)">{{ formatPercent(-strategy.maxDrawdown) }}</text>
          <text class="cell" :class="getCellClass(strategy.sharpeRatio)">{{ strategy.sharpeRatio.toFixed(2) }}</text>
        </view>
      </view>
    </view>
    
    <!-- 交易详情对比 -->
    <view class="trading-details card" v-if="isCompared">
      <text class="section-title">交易详情对比</text>
      
      <view class="metrics-grid">
        <view v-for="(strategy, index) in comparedStrategies" :key="index" class="strategy-metrics">
          <text class="metrics-title" :style="{ color: strategyColors[index % strategyColors.length] }">{{ strategy.name }}</text>
          
          <view class="metrics-row">
            <view class="metric-item">
              <text class="metric-label">胜率</text>
              <text class="metric-value">{{ strategy.winRate }}%</text>
            </view>
            <view class="metric-item">
              <text class="metric-label">盈亏比</text>
              <text class="metric-value">{{ strategy.profitLossRatio.toFixed(2) }}</text>
            </view>
          </view>
          
          <view class="metrics-row">
            <view class="metric-item">
              <text class="metric-label">交易次数</text>
              <text class="metric-value">{{ strategy.tradeCount }}</text>
            </view>
            <view class="metric-item">
              <text class="metric-label">平均持仓</text>
              <text class="metric-value">{{ strategy.avgHoldingDays }}天</text>
            </view>
          </view>
          
          <view class="metrics-row">
            <view class="metric-item">
              <text class="metric-label">最大连续盈利</text>
              <text class="metric-value">{{ strategy.maxConsecutiveWins }}</text>
            </view>
            <view class="metric-item">
              <text class="metric-label">最大连续亏损</text>
              <text class="metric-value">{{ strategy.maxConsecutiveLosses }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 策略建议 -->
    <view class="strategy-recommendation card" v-if="isCompared">
      <text class="section-title">AI策略建议</text>
      
      <view class="recommendation-content">
        <text class="recommendation-text">{{ aiRecommendation.text }}</text>
        
        <view class="best-strategy">
          <text class="best-label">当前市场推荐策略</text>
          <text class="best-value">{{ aiRecommendation.bestStrategy }}</text>
          <text class="best-reason">{{ aiRecommendation.reason }}</text>
        </view>
        
        <view class="market-conditions">
          <text class="conditions-title">市场条件评估</text>
          <view class="conditions-grid">
            <view v-for="(condition, index) in aiRecommendation.marketConditions" :key="index" class="condition-item">
              <text class="condition-name">{{ condition.name }}</text>
              <text class="condition-value" :class="condition.positive ? 'positive' : 'negative'">
                {{ condition.value }}
              </text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      // 可用策略列表
      availableStrategies: [
        { id: 'sixSword', name: '六脉神剑' },
        { id: 'jiuFang', name: '九方智投' },
        { id: 'compass', name: '指南针' },
        { id: 'limitUpDoubleNegative', name: '涨停双阴' },
        { id: 'momentum', name: '动量策略' },
        { id: 'meanReversion', name: '均值回归' }
      ],
      
      // 已选择的策略
      selectedStrategies: ['sixSword', 'jiuFang', 'compass'],
      
      // 股票选项
      stockOptions: [
        { code: 'SH000001', name: '上证指数' },
        { code: 'SH600519', name: '贵州茅台' },
        { code: 'SZ000858', name: '五粮液' },
        { code: 'SZ300750', name: '宁德时代' },
        { code: 'SH601318', name: '中国平安' }
      ],
      currentStockIndex: 0,
      
      // 日期范围
      startDate: '2023-01-01',
      endDate: '2023-06-30',
      
      // 比较状态
      isCompared: false,
      
      // 已比较的策略及其绩效
      comparedStrategies: [],
      
      // 绩效数据
      performanceData: [],
      
      // 策略颜色
      strategyColors: ['#1989fa', '#07c160', '#ff9900', '#ee0a24', '#8f2cd8', '#1677ff'],
      
      // AI策略建议
      aiRecommendation: {
        text: '',
        bestStrategy: '',
        reason: '',
        marketConditions: []
      }
    };
  },
  
  computed: {
    currentStock() {
      return this.stockOptions[this.currentStockIndex];
    }
  },
  
  methods: {
    // 返回上一页
    navigateBack() {
      uni.navigateBack();
    },
    
    // 切换策略选择
    toggleStrategy(strategyId) {
      const index = this.selectedStrategies.indexOf(strategyId);
      if (index === -1) {
        // 最多同时比较4个策略
        if (this.selectedStrategies.length < 4) {
          this.selectedStrategies.push(strategyId);
        } else {
          uni.showToast({
            title: '最多选择4个策略进行对比',
            icon: 'none'
          });
        }
      } else {
        this.selectedStrategies.splice(index, 1);
      }
    },
    
    // 股票变更
    onStockChange(e) {
      this.currentStockIndex = e.detail.value;
    },
    
    // 开始日期变更
    onStartDateChange(e) {
      this.startDate = e.detail.value;
    },
    
    // 结束日期变更
    onEndDateChange(e) {
      this.endDate = e.detail.value;
    },
    
    // 比较策略
    compareStrategies() {
      if (this.selectedStrategies.length < 2) {
        uni.showToast({
          title: '请至少选择两个策略进行对比',
          icon: 'none'
        });
        return;
      }
      
      // 显示加载中
      uni.showLoading({
        title: '分析中...'
      });
      
      // 模拟获取策略对比数据
      setTimeout(() => {
        this.fetchComparisonData();
        uni.hideLoading();
        this.isCompared = true;
      }, 1500);
    },
    
    // 获取策略对比数据
    fetchComparisonData() {
      // 在实际应用中,这里应该调用API获取各策略的历史绩效数据
      
      // 模拟数据
      this.comparedStrategies = this.selectedStrategies.map(id => {
        const strategy = this.availableStrategies.find(s => s.id === id);
        
        return {
          id: id,
          name: strategy.name,
          totalReturn: this.getRandomReturn(10, 30),
          annualReturn: this.getRandomReturn(15, 40),
          maxDrawdown: this.getRandomReturn(5, 15),
          sharpeRatio: 1 + Math.random() * 2,
          winRate: 50 + Math.random() * 30,
          profitLossRatio: 1 + Math.random() * 1.5,
          tradeCount: Math.floor(20 + Math.random() * 80),
          avgHoldingDays: Math.floor(3 + Math.random() * 12),
          maxConsecutiveWins: Math.floor(3 + Math.random() * 5),
          maxConsecutiveLosses: Math.floor(2 + Math.random() * 4)
        };
      });
      
      // 生成AI建议
      this.generateAiRecommendation();
    },
    
    // 生成AI建议
    generateAiRecommendation() {
      // 找出表现最好的策略
      let bestStrategy = this.comparedStrategies.reduce((prev, current) => {
        return (prev.sharpeRatio > current.sharpeRatio) ? prev : current;
      });
      
      this.aiRecommendation = {
        text: `根据历史回测数据分析,在${this.startDate}至${this.endDate}期间,对于${this.currentStock.name}(${this.currentStock.code})的交易,${bestStrategy.name}策略整体表现最佳,夏普比率达到${bestStrategy.sharpeRatio.toFixed(2)},总收益${this.formatPercent(bestStrategy.totalReturn)}。`,
        bestStrategy: bestStrategy.name,
        reason: `该策略在保持较高胜率(${bestStrategy.winRate.toFixed(0)}%)的同时,有效控制了回撤(${bestStrategy.maxDrawdown.toFixed(2)}%),整体风险收益比最佳。`,
        marketConditions: [
          { name: '市场趋势', value: '上升通道', positive: true },
          { name: '波动性', value: '中等', positive: true },
          { name: '成交量', value: '适中', positive: true },
          { name: '大盘情绪', value: '谨慎乐观', positive: true }
        ]
      };
    },
    
    // 获取随机收益率(用于模拟数据)
    getRandomReturn(min, max) {
      return min + Math.random() * (max - min);
    },
    
    // 格式化百分比
    formatPercent(value) {
      const prefix = value >= 0 ? '+' : '';
      return `${prefix}${value.toFixed(2)}%`;
    },
    
    // 获取单元格样式类
    getCellClass(value) {
      if (value > 0) return 'positive';
      if (value < 0) return 'negative';
      return '';
    }
  }
};
</script>

<style>
.container {
  padding: 30rpx;
  background-color: #f5f5f5;
}

.header {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 30rpx;
}

.back-button {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 20rpx;
}

.back-icon {
  font-family: "iconfont";
  font-size: 40rpx;
  color: #333;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

.card {
  background-color: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

/* 策略选择 */
.strategy-selection {
  margin-bottom: 30rpx;
}

.strategy-checkboxes {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin-bottom: 20rpx;
}

.strategy-checkbox {
  width: 33.33%;
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 20rpx;
}

.strategy-name {
  font-size: 28rpx;
  color: #333;
  margin-left: 10rpx;
}

.compare-btn {
  width: 100%;
  height: 80rpx;
  line-height: 80rpx;
  background-color: #1989fa;
  color: #fff;
  font-size: 28rpx;
  text-align: center;
  border-radius: 40rpx;
  margin-top: 10rpx;
}

/* 股票选择 */
.stock-selection {
  margin-bottom: 30rpx;
}

.picker-value {
  padding: 20rpx;
  background-color: #f9f9f9;
  border-radius: 8rpx;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.picker-arrow {
  color: #999;
}

.date-range {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.date-picker {
  width: 48%;
}

.date-label {
  font-size: 24rpx;
  color: #666;
  margin-bottom: 10rpx;
  display: block;
}

.date-value {
  padding: 16rpx;
  background-color: #f9f9f9;
  border-radius: 8rpx;
  font-size: 26rpx;
  color: #333;
  text-align: center;
}

/* 绩效对比 */
.performance-comparison {
  margin-bottom: 30rpx;
}

.chart-container {
  margin-bottom: 30rpx;
}

.chart-title {
  font-size: 28rpx;
  color: #666;
  margin-bottom: 10rpx;
  display: block;
}

.chart {
  height: 400rpx;
  background-color: #f9f9f9;
  border-radius: 8rpx;
  margin-bottom: 10rpx;
}

.chart-placeholder {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.chart-legend {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin-top: 10rpx;
}

.legend-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-right: 20rpx;
  margin-bottom: 10rpx;
}

.legend-color {
  width: 24rpx;
  height: 10rpx;
  margin-right: 8rpx;
  border-radius: 2rpx;
}

/* 绩效指标表格 */
.metrics-table {
  width: 100%;
  border-radius: 8rpx;
  overflow: hidden;
  font-size: 24rpx;
}

.table-header {
  display: flex;
  flex-direction: row;
  background-color: #f0f0f0;
}

.header-cell {
  flex: 1;
  padding: 16rpx 10rpx;
  text-align: center;
  color: #333;
  font-weight: bold;
}

.table-row {
  display: flex;
  flex-direction: row;
  border-bottom: 1px solid #f0f0f0;
}

.table-row:last-child {
  border-bottom: none;
}

.cell {
  flex: 1;
  padding: 16rpx 10rpx;
  text-align: center;
  color: #333;
}

.strategy-cell {
  text-align: left;
  font-weight: bold;
}

.positive {
  color: #f5222d;
}

.negative {
  color: #52c41a;
}

/* 交易详情对比 */
.trading-details {
  margin-bottom: 30rpx;
}

.metrics-grid {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin: 0 -10rpx;
}

.strategy-metrics {
  width: 50%;
  padding: 10rpx;
  box-sizing: border-box;
  margin-bottom: 20rpx;
}

.metrics-title {
  font-size: 28rpx;
  font-weight: bold;
  margin-bottom: 16rpx;
  display: block;
}

.metrics-row {
  display: flex;
  flex-direction: row;
  margin-bottom: 16rpx;
}

.metric-item {
  flex: 1;
}

.metric-label {
  font-size: 24rpx;
  color: #666;
  margin-bottom: 6rpx;
  display: block;
}

.metric-value {
  font-size: 26rpx;
  color: #333;
  font-weight: bold;
}

/* 策略建议 */
.strategy-recommendation {
  margin-bottom: 100rpx;
}

.recommendation-content {
  background-color: #f9f9f9;
  padding: 20rpx;
  border-radius: 8rpx;
}

.recommendation-text {
  font-size: 26rpx;
  color: #333;
  line-height: 1.5;
  margin-bottom: 20rpx;
  display: block;
}

.best-strategy {
  background-color: rgba(25, 137, 250, 0.1);
  padding: 16rpx;
  border-radius: 8rpx;
  margin-bottom: 20rpx;
}

.best-label {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 10rpx;
  display: block;
}

.best-value {
  font-size: 30rpx;
  color: #1989fa;
  font-weight: bold;
  margin-bottom: 10rpx;
  display: block;
}

.best-reason {
  font-size: 24rpx;
  color: #666;
  line-height: 1.5;
}

.market-conditions {
  margin-top: 20rpx;
}

.conditions-title {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 10rpx;
  display: block;
}

.conditions-grid {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}

.condition-item {
  width: 50%;
  padding: 10rpx;
  box-sizing: border-box;
}

.condition-name {
  font-size: 24rpx;
  color: #666;
  margin-bottom: 6rpx;
  display: block;
}

.condition-value {
  font-size: 26rpx;
  font-weight: bold;
}

.condition-value.positive {
  color: #07c160;
}

.condition-value.negative {
  color: #ee0a24;
}
</style> 
