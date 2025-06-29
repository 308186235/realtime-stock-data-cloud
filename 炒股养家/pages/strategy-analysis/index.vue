<template>
  <view class="container">
    <view class="header">
      <text class="title">{{isEditing ? '编辑策略' : '新建策略'}}</text>
    </view>
    
    <view class="form-container">
      <view class="form-section">
        <text class="section-title">基本信息</text>
        
        <view class="form-item">
          <text class="form-label">策略名称</text>
          <input class="form-input" v-model="strategy.name" placeholder="请输入策略名称" />
        </view>
        
        <view class="form-item">
          <text class="form-label">策略类型</text>
          <picker class="form-picker" mode="selector" :range="strategyTypes" @change="onTypeChange">
            <view class="picker-value">{{strategy.type || '请选择策略类型'}}</view>
          </picker>
        </view>
        
        <view class="form-item">
          <text class="form-label">执行周期</text>
          <picker class="form-picker" mode="selector" :range="intervalOptions" @change="onIntervalChange">
            <view class="picker-value">{{strategy.interval || '请选择执行周期'}}</view>
          </picker>
        </view>
        
        <view class="form-item">
          <text class="form-label">风险等级</text>
          <slider
            class="risk-slider"
            min="1"
            max="5"
            :value="strategy.riskLevel || 1"
            show-value
            activeColor="#4c8dff"
            @change="onRiskLevelChange"
          />
          <text class="risk-level-text" :class="'risk-level-' + strategy.riskLevel">{{getRiskLevelText(strategy.riskLevel)}}</text>
        </view>
      </view>
      
      <view class="form-section">
        <text class="section-title">目标股票</text>
        
        <view class="stock-search">
          <input
            class="search-input"
            v-model="stockSearch"
            placeholder="搜索股票名称或代码"
            @input="searchStocks"
          />
          <button class="add-stock-btn" @click="showStockPicker">选择股票</button>
        </view>
        
        <view class="selected-stocks">
          <view v-for="(stock, index) in strategy.targetStocks" :key="index" class="stock-tag">
            <text class="stock-name">{{stock}}</text>
            <text class="remove-stock" @click="removeStock(index)">×</text>
          </view>
          <text v-if="strategy.targetStocks.length === 0" class="empty-text">请添加目标股票</text>
        </view>
      </view>
      
      <view class="form-section">
        <text class="section-title">交易规则</text>
        
        <view class="rule-item">
          <text class="rule-header">买入条件</text>
          <radio-group @change="onBuyRuleChange">
            <label v-for="(rule, index) in buyRules" :key="index" class="rule-option">
              <radio :value="rule.value" :checked="strategy.buyRule === rule.value" color="#4c8dff" />
              <text>{{rule.label}}</text>
            </label>
          </radio-group>
          
          <view v-if="strategy.buyRule === 'ma_cross'" class="rule-params">
            <view class="param-row">
              <text>短期均线</text>
              <picker class="param-picker" mode="selector" :range="maOptions" @change="onShortMAChange">
                <view class="picker-value">{{strategy.shortMA || '请选择'}}</view>
              </picker>
            </view>
            <view class="param-row">
              <text>长期均线</text>
              <picker class="param-picker" mode="selector" :range="maOptions" @change="onLongMAChange">
                <view class="picker-value">{{strategy.longMA || '请选择'}}</view>
              </picker>
            </view>
          </view>
          
          <view v-if="strategy.buyRule === 'rsi'" class="rule-params">
            <view class="param-row">
              <text>RSI周期</text>
              <picker class="param-picker" mode="selector" :range="rsiPeriods" @change="onRSIPeriodChange">
                <view class="picker-value">{{strategy.rsiPeriod || '请选择'}}</view>
              </picker>
            </view>
            <view class="param-row">
              <text>超卖阈值</text>
              <slider
                class="param-slider"
                min="10"
                max="40"
                :value="strategy.rsiOversold || 30"
                show-value
                activeColor="#4c8dff"
                @change="onRSIOversoldChange"
              />
            </view>
          </view>
        </view>
        
        <view class="rule-item">
          <text class="rule-header">卖出条件</text>
          <radio-group @change="onSellRuleChange">
            <label v-for="(rule, index) in sellRules" :key="index" class="rule-option">
              <radio :value="rule.value" :checked="strategy.sellRule === rule.value" color="#4c8dff" />
              <text>{{rule.label}}</text>
            </label>
          </radio-group>
          
          <view v-if="strategy.sellRule === 'profit_target'" class="rule-params">
            <view class="param-row">
              <text>止盈目标</text>
              <slider
                class="param-slider"
                min="5"
                max="50"
                :value="strategy.profitTarget || 15"
                show-value
                activeColor="#4c8dff"
                @change="onProfitTargetChange"
              />
              <text class="param-unit">%</text>
            </view>
            <view class="param-row">
              <text>止损线</text>
              <slider
                class="param-slider"
                min="2"
                max="20"
                :value="strategy.stopLoss || 8"
                show-value
                activeColor="#4c8dff"
                @change="onStopLossChange"
              />
              <text class="param-unit">%</text>
            </view>
          </view>
          
          <view v-if="strategy.sellRule === 'rsi'" class="rule-params">
            <view class="param-row">
              <text>RSI周期</text>
              <picker class="param-picker" mode="selector" :range="rsiPeriods" @change="onRSIPeriodSellChange">
                <view class="picker-value">{{strategy.rsiPeriodSell || '请选择'}}</view>
              </picker>
            </view>
            <view class="param-row">
              <text>超买阈值</text>
              <slider
                class="param-slider"
                min="60"
                max="90"
                :value="strategy.rsiOverbought || 70"
                show-value
                activeColor="#4c8dff"
                @change="onRSIOverboughtChange"
              />
            </view>
          </view>
        </view>
      </view>
      
      <view class="form-section">
        <text class="section-title">仓位管理</text>
        
        <view class="form-item">
          <text class="form-label">单次买入比例</text>
          <slider
            class="form-slider"
            min="1"
            max="100"
            :value="strategy.positionSize || 10"
            show-value
            activeColor="#4c8dff"
            @change="onPositionSizeChange"
          />
          <text class="param-unit">%</text>
        </view>
        
        <view class="form-item">
          <text class="form-label">最大持仓比例</text>
          <slider
            class="form-slider"
            min="10"
            max="100"
            :value="strategy.maxPosition || 50"
            show-value
            activeColor="#4c8dff"
            @change="onMaxPositionChange"
          />
          <text class="param-unit">%</text>
        </view>
      </view>
    </view>
    
    <view class="button-group">
      <button class="action-btn cancel" @click="goBack">取消</button>
      <button class="action-btn test" @click="testStrategy">回测策略</button>
      <button class="action-btn save" @click="saveStrategy">保存策略</button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      isEditing: false,
      editIndex: -1,
      strategy: {
        name: '',
        type: '',
        interval: '',
        riskLevel: 2,
        targetStocks: [],
        buyRule: 'ma_cross',
        sellRule: 'profit_target',
        shortMA: '5日',
        longMA: '20日',
        rsiPeriod: '14日',
        rsiOversold: 30,
        rsiPeriodSell: '14日',
        rsiOverbought: 70,
        profitTarget: 15,
        stopLoss: 8,
        positionSize: 10,
        maxPosition: 50,
        historicalReturn: 0,
        maxDrawdown: 0,
        winLossRatio: '0:0',
        sharpeRatio: '0'
      },
      stockSearch: '',
      strategyTypes: ['趋势跟踪', '逆势交易', '基本面分析', '量化对冲', '波动率交易'],
      intervalOptions: ['1分钟', '5分钟', '15分钟', '30分钟', '60分钟', '日线', '周线', '月线'],
      buyRules: [
        { label: '均线金叉', value: 'ma_cross' },
        { label: 'RSI超卖', value: 'rsi' },
        { label: '布林带下轨突破', value: 'bollinger_lower' },
        { label: 'MACD金叉', value: 'macd_cross' }
      ],
      sellRules: [
        { label: '止盈/止损', value: 'profit_target' },
        { label: 'RSI超买', value: 'rsi' },
        { label: '布林带上轨突破', value: 'bollinger_upper' },
        { label: 'MACD死叉', value: 'macd_death' }
      ],
      maOptions: ['5日', '10日', '20日', '30日', '60日', '120日', '250日'],
      rsiPeriods: ['6日', '12日', '14日', '21日', '24日']
    };
  },
  onLoad(options) {
    if (options.edit !== undefined) {
      this.isEditing = true;
      this.editIndex = parseInt(options.edit);
      this.loadStrategy(this.editIndex);
    }
  },
  methods: {
    loadStrategy(index) {
      // 实际应用中应该从数据存储中加载策略
      // 这里简单模拟几种策略
      const strategies = [
        {
          name: '均线突破策略',
          type: '趋势跟踪',
          targetStocks: ['贵州茅台', '宁德时代', '中国平安'],
          interval: '5分钟',
          riskLevel: 2,
          buyRule: 'ma_cross',
          sellRule: 'profit_target',
          shortMA: '5日',
          longMA: '20日',
          profitTarget: 15,
          stopLoss: 8,
          positionSize: 10,
          maxPosition: 50,
          historicalReturn: 15.8,
          maxDrawdown: 8.2,
          winLossRatio: '1.5:1',
          sharpeRatio: '1.2'
        },
        {
          name: 'RSI超买超卖策略',
          type: '逆势交易',
          targetStocks: ['阿里巴巴', '腾讯控股'],
          interval: '日线',
          riskLevel: 3,
          buyRule: 'rsi',
          sellRule: 'rsi',
          rsiPeriod: '14日',
          rsiOversold: 30,
          rsiPeriodSell: '14日',
          rsiOverbought: 70,
          positionSize: 20,
          maxPosition: 60,
          historicalReturn: 22.3,
          maxDrawdown: 12.5,
          winLossRatio: '1.3:1',
          sharpeRatio: '0.9'
        },
        {
          name: '价值投资策略',
          type: '基本面分析',
          targetStocks: ['平安银行', '工商银行', '建设银行', '招商银行'],
          interval: '周线',
          riskLevel: 1,
          buyRule: 'bollinger_lower',
          sellRule: 'profit_target',
          profitTarget: 25,
          stopLoss: 10,
          positionSize: 15,
          maxPosition: 40,
          historicalReturn: 8.5,
          maxDrawdown: 5.1,
          winLossRatio: '2.1:1',
          sharpeRatio: '1.5'
        }
      ];
      
      if (index >= 0 && index < strategies.length) {
        this.strategy = {...strategies[index]};
      }
    },
    onTypeChange(e) {
      this.strategy.type = this.strategyTypes[e.detail.value];
    },
    onIntervalChange(e) {
      this.strategy.interval = this.intervalOptions[e.detail.value];
    },
    onRiskLevelChange(e) {
      this.strategy.riskLevel = e.detail.value;
    },
    getRiskLevelText(level) {
      const levels = ['极低', '低', '中', '高', '极高'];
      return levels[level - 1] || '未知';
    },
    searchStocks() {
      // 实际应用中应该调用API搜索股票
    },
    showStockPicker() {
      // 实际应用中应该显示股票选择器
      uni.navigateTo({
        url: '/pages/stock-picking/index?mode=select'
      });
    },
    removeStock(index) {
      this.strategy.targetStocks.splice(index, 1);
    },
    onBuyRuleChange(e) {
      this.strategy.buyRule = e.detail.value;
    },
    onSellRuleChange(e) {
      this.strategy.sellRule = e.detail.value;
    },
    onShortMAChange(e) {
      this.strategy.shortMA = this.maOptions[e.detail.value];
    },
    onLongMAChange(e) {
      this.strategy.longMA = this.maOptions[e.detail.value];
    },
    onRSIPeriodChange(e) {
      this.strategy.rsiPeriod = this.rsiPeriods[e.detail.value];
    },
    onRSIOversoldChange(e) {
      this.strategy.rsiOversold = e.detail.value;
    },
    onRSIPeriodSellChange(e) {
      this.strategy.rsiPeriodSell = this.rsiPeriods[e.detail.value];
    },
    onRSIOverboughtChange(e) {
      this.strategy.rsiOverbought = e.detail.value;
    },
    onProfitTargetChange(e) {
      this.strategy.profitTarget = e.detail.value;
    },
    onStopLossChange(e) {
      this.strategy.stopLoss = e.detail.value;
    },
    onPositionSizeChange(e) {
      this.strategy.positionSize = e.detail.value;
    },
    onMaxPositionChange(e) {
      this.strategy.maxPosition = e.detail.value;
    },
    testStrategy() {
      // 验证表单
      if (!this.validateForm()) {
        return;
      }
      
      // 模拟回测过程
      uni.showLoading({
        title: '策略回测中...'
      });
      
      // 模拟延时,实际应调用API进行回测
      setTimeout(() => {
        uni.hideLoading();
        
        // 模拟回测结果
        this.strategy.historicalReturn = (Math.random() * 30).toFixed(1);
        this.strategy.maxDrawdown = (Math.random() * 20).toFixed(1);
        this.strategy.winLossRatio = (1 + Math.random()).toFixed(1) + ':1';
        this.strategy.sharpeRatio = (Math.random() + 0.5).toFixed(1);
        
        // 展示回测结果
        uni.showModal({
          title: '回测结果',
          content: `历史收益率: ${this.strategy.historicalReturn}%\n最大回撤: ${this.strategy.maxDrawdown}%\n盈亏比: ${this.strategy.winLossRatio}\n夏普比率: ${this.strategy.sharpeRatio}`,
          showCancel: false
        });
      }, 2000);
    },
    saveStrategy() {
      // 验证表单
      if (!this.validateForm()) {
        return;
      }
      
      // 实际应用中应该保存策略到数据存储
      uni.showToast({
        title: '策略保存成功',
        icon: 'success',
        duration: 2000
      });
      
      // 返回上一页
      setTimeout(() => {
        uni.navigateBack();
      }, 2000);
    },
    validateForm() {
      if (!this.strategy.name) {
        uni.showToast({
          title: '请输入策略名称',
          icon: 'none'
        });
        return false;
      }
      
      if (!this.strategy.type) {
        uni.showToast({
          title: '请选择策略类型',
          icon: 'none'
        });
        return false;
      }
      
      if (!this.strategy.interval) {
        uni.showToast({
          title: '请选择执行周期',
          icon: 'none'
        });
        return false;
      }
      
      if (this.strategy.targetStocks.length === 0) {
        uni.showToast({
          title: '请添加目标股票',
          icon: 'none'
        });
        return false;
      }
      
      return true;
    },
    goBack() {
      uni.navigateBack();
    }
  }
};
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

.form-container {
  margin-bottom: 100rpx;
}

.form-section {
  background-color: #222;
  border-radius: 10rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
  padding-bottom: 15rpx;
  border-bottom: 1px solid #333;
}

.form-item {
  margin-bottom: 20rpx;
}

.form-label {
  font-size: 28rpx;
  color: #bbb;
  margin-bottom: 10rpx;
  display: block;
}

.form-input {
  background-color: #333;
  color: #eee;
  padding: 15rpx;
  border-radius: 6rpx;
  width: 100%;
  box-sizing: border-box;
}

.form-picker {
  background-color: #333;
  padding: 15rpx;
  border-radius: 6rpx;
}

.picker-value {
  color: #eee;
  font-size: 28rpx;
}

.risk-slider {
  margin: 0 15rpx;
}

.risk-level-text {
  font-size: 28rpx;
  margin-top: 10rpx;
  display: block;
  text-align: center;
}

.risk-level-1 {
  color: #4caf50;
}

.risk-level-2 {
  color: #8bc34a;
}

.risk-level-3 {
  color: #ff9800;
}

.risk-level-4 {
  color: #ff5722;
}

.risk-level-5 {
  color: #f44336;
}

.stock-search {
  display: flex;
  margin-bottom: 20rpx;
}

.search-input {
  flex: 1;
  background-color: #333;
  color: #eee;
  padding: 15rpx;
  border-radius: 6rpx;
  margin-right: 15rpx;
}

.add-stock-btn {
  background-color: #4c8dff;
  color: white;
  font-size: 28rpx;
  padding: 0 20rpx;
  border-radius: 6rpx;
}

.selected-stocks {
  min-height: 100rpx;
  padding: 15rpx;
  background-color: #333;
  border-radius: 6rpx;
  display: flex;
  flex-wrap: wrap;
}

.stock-tag {
  background-color: #4c8dff;
  border-radius: 30rpx;
  padding: 8rpx 20rpx;
  margin-right: 15rpx;
  margin-bottom: 15rpx;
  display: flex;
  align-items: center;
}

.stock-name {
  font-size: 26rpx;
  color: white;
  margin-right: 10rpx;
}

.remove-stock {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
  width: 30rpx;
  height: 30rpx;
  text-align: center;
  line-height: 30rpx;
}

.empty-text {
  color: #666;
  font-size: 28rpx;
  text-align: center;
  width: 100%;
  padding: 20rpx 0;
}

.rule-item {
  background-color: #333;
  border-radius: 8rpx;
  padding: 15rpx;
  margin-bottom: 20rpx;
}

.rule-header {
  font-size: 28rpx;
  font-weight: bold;
  margin-bottom: 15rpx;
}

.rule-option {
  display: flex;
  align-items: center;
  margin-bottom: 15rpx;
  margin-right: 20rpx;
  font-size: 26rpx;
}

.rule-params {
  background-color: #3a3a3a;
  border-radius: 6rpx;
  padding: 15rpx;
  margin-top: 15rpx;
}

.param-row {
  display: flex;
  align-items: center;
  margin-bottom: 15rpx;
}

.param-row text {
  font-size: 26rpx;
  width: 150rpx;
}

.param-picker {
  flex: 1;
  background-color: #444;
  padding: 10rpx;
  border-radius: 4rpx;
  margin-left: 15rpx;
}

.param-slider {
  flex: 1;
  margin: 0 15rpx;
}

.param-unit {
  font-size: 26rpx;
  color: #999;
  margin-left: 10rpx;
}

.form-slider {
  margin: 0 15rpx;
}

.button-group {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  padding: 20rpx;
  background-color: #1a1a1a;
  border-top: 1px solid #333;
}

.action-btn {
  flex: 1;
  height: 80rpx;
  line-height: 80rpx;
  text-align: center;
  border-radius: 8rpx;
  margin: 0 10rpx;
  font-size: 28rpx;
}

.cancel {
  background-color: #444;
  color: white;
}

.test {
  background-color: #ff9800;
  color: white;
}

.save {
  background-color: #4c8dff;
  color: white;
}
</style> 
