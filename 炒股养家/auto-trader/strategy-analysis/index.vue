<template>
  <view class="container">
    <view class="header">
      <text class="title">策略分析</text>
      <text class="subtitle">AI驱动的多策略分析系统</text>
    </view>
    
    <!-- AI学习状态 -->
    <AILearningStatus
      :optimized="aiLearningOptimized"
      :progress="aiLearningProgress"
      :samples="tradingSamples"
    />
    
    <!-- 股票信息 -->
    <view class="stock-info">
      <view class="stock-header">
        <view class="stock-name-code">
          <text class="stock-name">{{ stockInfo.name }}</text>
          <text class="stock-code">{{ stockInfo.code }}</text>
        </view>
        <view class="stock-price">
          <text class="price" :class="priceChangeClass">¥{{ stockInfo.price }}</text>
          <text class="change" :class="priceChangeClass">
            {{ stockInfo.change > 0 ? '+' : '' }}{{ stockInfo.change }}
            ({{ stockInfo.changePercent > 0 ? '+' : '' }}{{ stockInfo.changePercent }}%)
          </text>
        </view>
      </view>
    </view>
    
    <!-- 交易决策推荐组件 -->
    <TradeRecommendation 
      :decision="analysisResult.decision"
      :strategyResults="strategyResults"
      :weights="analysisResult.weights"
      @execute="executeTradeRecommendation"
      @showDetails="showTradeDetails"
    />
    
    <!-- 策略权重 -->
    <view class="weight-card">
      <text class="card-title">策略权重</text>
      <view class="weight-bars">
        <view class="weight-item">
          <text class="weight-label">六脉神剑</text>
          <view class="weight-bar-container">
            <view class="weight-bar" :style="{ width: `${analysisResult.weights.sixSword * 100}%`, backgroundColor: '#1989fa' }"></view>
          </view>
          <text class="weight-value">{{ Math.round(analysisResult.weights.sixSword * 100) }}%</text>
        </view>
        <view class="weight-item">
          <text class="weight-label">九方智投</text>
          <view class="weight-bar-container">
            <view class="weight-bar" :style="{ width: `${analysisResult.weights.jiuFang * 100}%`, backgroundColor: '#07c160' }"></view>
          </view>
          <text class="weight-value">{{ Math.round(analysisResult.weights.jiuFang * 100) }}%</text>
        </view>
        <view class="weight-item">
          <text class="weight-label">指南针</text>
          <view class="weight-bar-container">
            <view class="weight-bar" :style="{ width: `${analysisResult.weights.compass * 100}%`, backgroundColor: '#ff9900' }"></view>
          </view>
          <text class="weight-value">{{ Math.round(analysisResult.weights.compass * 100) }}%</text>
        </view>
      </view>
    </view>
    
    <!-- 形态识别可视化 -->
    <PatternVisualization 
      v-if="activeTab === 1" 
      :detectedPatterns="jiuFangResult.detectedPatterns"
      :stockData="stockData"
    />
    
    <!-- 策略分析详情 -->
    <view class="strategy-tabs">
      <view 
        v-for="(tab, index) in tabs" 
        :key="index" 
        class="tab-item" 
        :class="{ active: activeTab === index }"
        @click="activeTab = index"
      >
        <text class="tab-text">{{ tab }}</text>
      </view>
    </view>
    
    <view class="strategy-content">
      <!-- 六脉神剑内容 -->
      <view v-if="activeTab === 0" class="strategy-detail">
        <view class="strategy-header">
          <text class="strategy-title">六脉神剑分析</text>
          <view class="score-badge small" :style="{ backgroundColor: getScoreColor(sixSwordResult.overallScore) }">
            <text class="score-text small">{{ Math.round(sixSwordResult.overallScore) }}</text>
          </view>
        </view>
        
        <view class="strategy-summary">
          <text class="summary-text">{{ sixSwordResult.recommendation.description }}</text>
        </view>
        
        <view class="strategy-items">
          <view v-for="(strategy, key) in sixSwordResult.strategies" :key="key" class="strategy-item">
            <view class="item-header">
              <text class="item-title">{{ getSixSwordStrategyName(key) }}</text>
              <text class="item-score" :class="getScoreClass(strategy.score)">{{ strategy.score }}</text>
            </view>
            <text class="item-desc">{{ strategy.interpretation }}</text>
          </view>
        </view>
      </view>
      
      <!-- 九方智投内容 -->
      <view v-if="activeTab === 1" class="strategy-detail">
        <view class="strategy-header">
          <text class="strategy-title">九方智投形态分析</text>
        </view>
        
        <view class="strategy-summary">
          <text class="summary-text">{{ jiuFangResult.summary.description }}</text>
        </view>
        
        <view class="detected-patterns">
          <text class="section-title">检测到的形态</text>
          <view v-for="(pattern, index) in jiuFangResult.detectedPatterns" :key="index" class="pattern-item">
            <view class="pattern-header">
              <text class="pattern-name">{{ pattern.name }}</text>
              <text class="pattern-direction" :class="getDirectionClass(pattern.direction)">
                {{ getDirectionText(pattern.direction) }}
              </text>
            </view>
            <text class="pattern-desc">{{ pattern.description }}</text>
            <view class="confidence-bar">
              <view class="confidence-fill" :style="{ width: `${pattern.confidence * 100}%` }"></view>
            </view>
            <text class="confidence-text">可信度: {{ Math.round(pattern.confidence * 100) }}%</text>
          </view>
        </view>
      </view>
      
      <!-- 指南针内容 -->
      <view v-if="activeTab === 2" class="strategy-detail">
        <view class="strategy-header">
          <text class="strategy-title">指南针策略分析</text>
          <view class="score-badge small" :style="{ backgroundColor: getScoreColor(compassResult.overallScore) }">
            <text class="score-text small">{{ Math.round(compassResult.overallScore) }}</text>
          </view>
        </view>
        
        <view class="strategy-summary">
          <text class="summary-text">{{ compassResult.recommendation.description }}</text>
        </view>
        
        <view class="strategy-items">
          <view v-for="(strategy, key) in compassResult.strategies" :key="key" class="strategy-item">
            <view class="item-header">
              <text class="item-title">{{ getCompassStrategyName(key) }}</text>
              <text class="item-score" :class="getScoreClass(strategy.score)">{{ strategy.score }}</text>
            </view>
            <text class="item-desc">{{ strategy.interpretation }}</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 设置按钮 -->
    <view class="settings-button" @click="openSettings">
      <text class="settings-text">策略设置</text>
    </view>
    
    <!-- 特色策略链接 -->
    <view class="special-strategies">
      <text class="special-title">特色策略</text>
      <view class="strategy-links">
        <view class="strategy-link" @click="navigateToLimitUpDoubleNegative">
          <text class="link-icon">📈</text>
          <text class="link-text">涨停双阴买入法</text>
          <text class="link-arrow">→</text>
        </view>
        <view class="strategy-link" @click="navigateToMultiStrategyComparison">
          <text class="link-icon">📊</text>
          <text class="link-text">多策略对比分析</text>
          <text class="link-arrow">→</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import StrategyManager from '../../utils/strategies/strategyManager.js';
import PatternVisualization from '../../components/PatternVisualization.vue';
import TradeRecommendation from '../../components/TradeRecommendation.vue';
import AILearningStatus from '../../components/AILearningStatus.vue';

export default {
  components: {
    PatternVisualization,
    TradeRecommendation,
    AILearningStatus
  },
  
  data() {
    return {
      stockInfo: {
        name: '示例股票',
        code: 'SH000001',
        price: 3258.63,
        change: 18.25,
        changePercent: 0.56
      },
      stockData: {
        prices: [],
        volumes: [],
        highs: [],
        lows: [],
        opens: [],
        closes: [],
        dates: []
      },
      analysisResult: {
        overallScore: 65,
        decision: {
          action: 'buy',
          confidence: 'medium',
          allocation: 0.6,
          description: '大部分指标显示积极信号,市场走势向好。'
        },
        weights: {
          sixSword: 0.35,
          jiuFang: 0.35,
          compass: 0.30
        }
      },
      strategyResults: {
        sixSword: null,
        jiuFang: null,
        compass: null
      },
      sixSwordResult: {
        overallScore: 70,
        recommendation: {
          action: '建议买入',
          confidence: '中高',
          description: '大部分指标显示积极信号,市场走势向好。'
        },
        strategies: {
          tian: { score: 60, interpretation: '有一定突破迹象,但需确认,可小仓位试探' },
          di: { score: 40, interpretation: '股价在支撑位有效反弹,可能开始上涨' },
          ren: { score: 35, interpretation: '量价配合良好,放量上涨,看多信号明确' },
          he: { score: 65, interpretation: '股价调整后明显企稳回升,可能是买入机会' },
          shun: { score: 70, interpretation: '大趋势向上,建议顺势操作,持股或买入' },
          ling: { score: 55, interpretation: '部分高级指标显示积极,谨慎看多' }
        }
      },
      jiuFangResult: {
        summary: {
          trend: '温和上涨',
          strength: '中',
          recommendation: '谨慎买入',
          description: '出现一些看涨信号,市场可能呈现温和上涨趋势。最显著的形态是MACD金叉,表明短期动量超过长期动量,可能预示着上涨趋势的开始。'
        },
        detectedPatterns: [
          {
            name: 'MACD金叉',
            detected: true,
            confidence: 0.85,
            direction: 'bullish',
            description: 'MACD金叉是一个看涨信号,表明短期动量超过长期动量,可能预示着上涨趋势的开始。'
          },
          {
            name: '双底形态',
            detected: true,
            confidence: 0.70,
            direction: 'bullish',
            description: '双底是一种底部反转形态,表明下跌趋势即将结束,转为上涨趋势。'
          },
          {
            name: '均线多头排列',
            detected: true,
            confidence: 0.65,
            direction: 'bullish',
            description: '均线多头排列表示市场处于上升趋势,短期均线在上,长期均线在下。'
          }
        ]
      },
      compassResult: {
        overallScore: 60,
        recommendation: {
          action: '建议买入',
          confidence: '中高',
          description: '大部分指标显示积极信号,市场走势向好。'
        },
        strategies: {
          mainForce: { score: 55, interpretation: '有一定主力控盘迹象,主力正在吸筹,可小仓位试探性跟随。' },
          trendFollowing: { score: 65, interpretation: '市场可能处于上升趋势初期或中期,趋势强度适中,可小仓位跟随趋势。' },
          breakthroughSystem: { score: 40, interpretation: '出现一些突破信号,但尚未得到充分确认。' },
          momentumSystem: { score: 70, interpretation: '动量指标显示积极信号,市场力量向上。' },
          volumePrice: { score: 60, interpretation: '量价配合良好,成交量逐渐放大。' },
          supportResistance: { score: 50, interpretation: '价格运行在支撑位与阻力位之间,暂无明确方向。' },
          marketMood: { score: 55, interpretation: '市场情绪逐渐改善,但尚未达到极度乐观。' },
          multiTimeframe: { score: 65, interpretation: '多个时间周期趋势向好,中长期走势看涨。' }
        }
      },
      tabs: ['六脉神剑', '九方智投', '指南针'],
      activeTab: 0,
      strategyManager: null,
      aiLearningOptimized: false,
      aiLearningProgress: 65,
      tradingSamples: 28
    };
  },
  computed: {
    priceChangeClass() {
      return this.stockInfo.change > 0 ? 'increase' : this.stockInfo.change < 0 ? 'decrease' : '';
    }
  },
  onLoad() {
    // 初始化策略管理器
    this.strategyManager = new StrategyManager();
    
    // 获取股票数据
    this.getStockData();
  },
  methods: {
    // 获取股票数据
    getStockData() {
      // 实际应用中,这里会调用API获取股票数据
      // 为了演示,这里使用模拟数据
      const mockStockData = this.generateMockStockData();
      
      // 保存原始数据用于可视化
      this.stockData = mockStockData;
      
      // 分析股票数据
      this.analyzeStockData(mockStockData);
      
      // 检查AI学习状态
      this.checkAILearningStatus();
    },
    
    // 检查AI学习状态
    checkAILearningStatus() {
      // 在实际应用中,这里会从策略管理器获取学习状态
      const strategyAI = this.strategyManager.getStrategyAI();
      
      if (strategyAI) {
        const learningEngine = strategyAI.getLearningEngine();
        
        if (learningEngine) {
          this.tradingSamples = learningEngine.tradingHistory.length;
          this.aiLearningOptimized = strategyAI.learningOptimized;
          
          // 如果满足条件,尝试自动优化
          if (strategyAI.shouldOptimize()) {
            this.autoOptimizeStrategies(strategyAI);
          }
        }
      }
    },
    
    // 自动优化策略
    autoOptimizeStrategies(strategyAI) {
      const result = strategyAI.autoOptimize();
      
      if (result.success) {
        this.aiLearningOptimized = true;
        
        // 提示用户策略已优化
        uni.showToast({
          title: 'AI已自动优化策略',
          icon: 'success',
          duration: 2000
        });
        
        // 更新分析结果中的权重
        this.analysisResult.weights = result.weights;
      }
    },
    
    // 导航到涨停双阴买入法页面
    navigateToLimitUpDoubleNegative() {
      uni.navigateTo({
        url: '/pages/strategy-analysis/limit-up-double-negative'
      });
    },
    
    // 导航到多策略对比分析页面
    navigateToMultiStrategyComparison() {
      uni.navigateTo({
        url: '/pages/strategy-analysis/multi-strategy-comparison'
      });
    },
    
    // 生成模拟股票数据
    generateMockStockData() {
      const prices = [];
      const volumes = [];
      const highs = [];
      const lows = [];
      const opens = [];
      const closes = [];
      const dates = [];
      
      // 生成60天的模拟数据
      let price = 100;
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 60);
      
      for (let i = 0; i < 60; i++) {
        const change = (Math.random() - 0.5) * 2;
        price = Math.max(50, price + change);
        prices.push(price);
        
        const high = price + Math.random() * 1;
        const low = price - Math.random() * 1;
        highs.push(high);
        lows.push(low);
        
        opens.push(price - change / 2);
        closes.push(price);
        
        volumes.push(Math.random() * 1000000 + 500000);
        
        const currentDate = new Date(startDate);
        currentDate.setDate(startDate.getDate() + i);
        dates.push(currentDate.toISOString().split('T')[0]);
      }
      
      return {
        prices,
        volumes,
        highs,
        lows,
        opens,
        closes,
        dates
      };
    },
    
    // 分析股票数据
    analyzeStockData(stockData) {
      // 使用策略管理器分析数据
      const result = this.strategyManager.analyzeStock(stockData);
      
      // 更新分析结果
      this.analysisResult = {
        overallScore: result.overallScore,
        decision: result.decision,
        weights: result.weights
      };
      
      // 更新各个策略的结果
      this.sixSwordResult = result.strategyResults.sixSword;
      this.jiuFangResult = result.strategyResults.jiuFang;
      this.compassResult = result.strategyResults.compass;
      
      // 更新策略结果对象(用于交易推荐组件)
      this.strategyResults = {
        sixSword: this.sixSwordResult,
        jiuFang: this.jiuFangResult,
        compass: this.compassResult
      };
    },
    
    // 执行交易推荐
    executeTradeRecommendation(recommendation) {
      uni.showModal({
        title: '执行交易',
        content: `确认要${recommendation.action === 'buy' || recommendation.action === 'strong_buy' ? 
                  '买入' : recommendation.action === 'sell' || recommendation.action === 'strong_sell' ? 
                  '卖出' : '持有'}该股票,仓位比例${Math.round(recommendation.allocation * 100)}%?`,
        success: (res) => {
          if (res.confirm) {
            uni.showToast({
              title: '交易指令已发送',
              icon: 'success'
            });
          }
        }
      });
    },
    
    // 显示交易详情
    showTradeDetails() {
      uni.navigateTo({
        url: '/pages/trade-details/index'
      });
    },
    
    // 获取评分颜色
    getScoreColor(score) {
      if (score >= 80) return '#07c160'; // 绿色
      if (score >= 60) return '#1989fa'; // 蓝色
      if (score >= 40) return '#ff9900'; // 橙色
      return '#ee0a24'; // 红色
    },
    
    // 获取评分样式类
    getScoreClass(score) {
      if (score >= 60) return 'score-high';
      if (score >= 30) return 'score-medium';
      return 'score-low';
    },
    
    // 获取方向样式类
    getDirectionClass(direction) {
      if (direction === 'bullish') return 'direction-bullish';
      if (direction === 'bearish') return 'direction-bearish';
      return 'direction-neutral';
    },
    
    // 获取方向文本
    getDirectionText(direction) {
      if (direction === 'bullish') return '看涨';
      if (direction === 'bearish') return '看跌';
      return '中性';
    },
    
    // 获取操作样式类
    getActionClass(action) {
      if (action === 'strong_buy' || action === 'buy') return 'action-buy';
      if (action === 'strong_sell' || action === 'sell') return 'action-sell';
      return 'action-hold';
    },
    
    // 获取操作文本
    getActionText(action) {
      const actionTexts = {
        'strong_buy': '强烈买入',
        'buy': '买入',
        'hold': '持有',
        'sell': '卖出',
        'strong_sell': '强烈卖出'
      };
      
      return actionTexts[action] || '未知';
    },
    
    // 获取信心水平文本
    getConfidenceText(confidence) {
      const confidenceTexts = {
        'high': '高',
        'medium': '中',
        'low': '低'
      };
      
      return confidenceTexts[confidence] || '未知';
    },
    
    // 获取推荐标题
    getRecommendationTitle(action) {
      if (action === 'strong_buy') return '强烈看好';
      if (action === 'buy') return '看好';
      if (action === 'hold') return '中性';
      if (action === 'sell') return '看空';
      if (action === 'strong_sell') return '强烈看空';
      return '未知';
    },
    
    // 获取六脉神剑策略名称
    getSixSwordStrategyName(key) {
      const names = {
        tian: '天字诀',
        di: '地字诀',
        ren: '人字诀',
        he: '和字诀',
        shun: '顺字诀',
        ling: '凌字诀'
      };
      
      return names[key] || key;
    },
    
    // 获取指南针策略名称
    getCompassStrategyName(key) {
      const names = {
        mainForce: '主力控盘',
        trendFollowing: '趋势跟踪',
        breakthroughSystem: '突破系统',
        momentumSystem: '动量系统',
        volumePrice: '量价关系',
        supportResistance: '支撑阻力',
        marketMood: '市场情绪',
        multiTimeframe: '多时间周期'
      };
      
      return names[key] || key;
    },
    
    // 打开设置
    openSettings() {
      uni.navigateTo({
        url: '/pages/strategy-settings/index'
      });
    }
  }
};
</script>

<style>
.container {
  padding: 20rpx;
}

.header {
  padding: 20rpx 0;
  align-items: center;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  margin-bottom: 10rpx;
}

.subtitle {
  font-size: 24rpx;
  color: #666;
}

/* 股票信息样式 */
.stock-info {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
}

.stock-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

.stock-name {
  font-size: 32rpx;
  font-weight: bold;
  margin-right: 10rpx;
}

.stock-code {
  font-size: 24rpx;
  color: #666;
}

.price {
  font-size: 36rpx;
  font-weight: bold;
}

.change {
  font-size: 24rpx;
  margin-top: 5rpx;
}

.increase {
  color: #f5222d;
}

.decrease {
  color: #52c41a;
}

/* 分析卡片样式 */
.analysis-card, .weight-card {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
}

.card-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.card-title {
  font-size: 28rpx;
  font-weight: bold;
}

.score-badge {
  width: 60rpx;
  height: 60rpx;
  border-radius: 30rpx;
  justify-content: center;
  align-items: center;
}

.score-badge.small {
  width: 50rpx;
  height: 50rpx;
  border-radius: 25rpx;
}

.score-text {
  color: #fff;
  font-size: 28rpx;
  font-weight: bold;
}

.score-text.small {
  font-size: 24rpx;
}

.recommendation {
  margin-bottom: 20rpx;
}

.recommendation-title {
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 10rpx;
}

.recommendation-desc {
  font-size: 26rpx;
  color: #666;
  line-height: 1.5;
}

.action-details {
  margin-top: 20rpx;
  border-top: 1rpx solid #eee;
  padding-top: 20rpx;
}

.detail-item {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  margin-bottom: 15rpx;
}

.detail-label {
  font-size: 26rpx;
  color: #666;
}

.detail-value {
  font-size: 26rpx;
  font-weight: bold;
}

.action-buy {
  color: #07c160;
}

.action-sell {
  color: #ee0a24;
}

.action-hold {
  color: #1989fa;
}

/* 权重条样式 */
.weight-bars {
  margin-top: 20rpx;
}

.weight-item {
  margin-bottom: 15rpx;
}

.weight-label {
  font-size: 26rpx;
  margin-bottom: 8rpx;
}

.weight-bar-container {
  height: 20rpx;
  background-color: #f5f5f5;
  border-radius: 10rpx;
  overflow: hidden;
}

.weight-bar {
  height: 100%;
  border-radius: 10rpx;
}

.weight-value {
  font-size: 24rpx;
  color: #666;
  margin-top: 5rpx;
  text-align: right;
}

/* 策略标签页样式 */
.strategy-tabs {
  display: flex;
  flex-direction: row;
  background-color: #fff;
  border-radius: 12rpx 12rpx 0 0;
  margin-bottom: 0;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
}

.tab-item {
  flex: 1;
  padding: 20rpx 0;
  align-items: center;
  border-bottom: 4rpx solid transparent;
}

.tab-item.active {
  border-bottom-color: #1989fa;
}

.tab-text {
  font-size: 28rpx;
  color: #333;
}

.tab-item.active .tab-text {
  color: #1989fa;
  font-weight: bold;
}

/* 策略内容样式 */
.strategy-content {
  background-color: #fff;
  border-radius: 0 0 12rpx 12rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
}

.strategy-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.strategy-title {
  font-size: 28rpx;
  font-weight: bold;
}

.strategy-summary {
  padding: 15rpx;
  background-color: #f9f9f9;
  border-radius: 8rpx;
  margin-bottom: 20rpx;
}

.summary-text {
  font-size: 26rpx;
  color: #666;
  line-height: 1.5;
}

.strategy-items, .detected-patterns {
  margin-top: 20rpx;
}

.strategy-item, .pattern-item {
  margin-bottom: 20rpx;
  padding: 15rpx;
  background-color: #f9f9f9;
  border-radius: 8rpx;
}

.item-header, .pattern-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  margin-bottom: 10rpx;
}

.item-title, .pattern-name {
  font-size: 26rpx;
  font-weight: bold;
}

.item-score {
  font-size: 26rpx;
  font-weight: bold;
}

.score-high {
  color: #07c160;
}

.score-medium {
  color: #1989fa;
}

.score-low {
  color: #ee0a24;
}

.item-desc, .pattern-desc {
  font-size: 24rpx;
  color: #666;
  line-height: 1.5;
}

.pattern-direction {
  font-size: 24rpx;
  padding: 4rpx 12rpx;
  border-radius: 4rpx;
}

.direction-bullish {
  background-color: rgba(7, 193, 96, 0.1);
  color: #07c160;
}

.direction-bearish {
  background-color: rgba(238, 10, 36, 0.1);
  color: #ee0a24;
}

.direction-neutral {
  background-color: rgba(25, 137, 250, 0.1);
  color: #1989fa;
}

.section-title {
  font-size: 28rpx;
  font-weight: bold;
  margin-bottom: 15rpx;
}

.confidence-bar {
  height: 10rpx;
  background-color: #eee;
  border-radius: 5rpx;
  margin: 10rpx 0;
}

.confidence-fill {
  height: 100%;
  background-color: #1989fa;
  border-radius: 5rpx;
}

.confidence-text {
  font-size: 24rpx;
  color: #666;
}

/* 设置按钮 */
.settings-button {
  position: fixed;
  bottom: 40rpx;
  right: 40rpx;
  background-color: #1989fa;
  width: 180rpx;
  height: 80rpx;
  border-radius: 40rpx;
  justify-content: center;
  align-items: center;
  box-shadow: 0 4rpx 16rpx rgba(25, 137, 250, 0.3);
}

.settings-text {
  color: #fff;
  font-size: 28rpx;
}

/* 特色策略链接样式 */
.special-strategies {
  margin-top: 20rpx;
  padding: 20rpx;
  background-color: #fff;
  border-radius: 12rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
}

.special-title {
  font-size: 28rpx;
  font-weight: bold;
  margin-bottom: 15rpx;
}

.strategy-links {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

.strategy-link {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 10rpx 20rpx;
  background-color: #f9f9f9;
  border-radius: 8rpx;
}

.link-icon {
  font-size: 28rpx;
  margin-right: 10rpx;
}

.link-text {
  font-size: 26rpx;
}

.link-arrow {
  font-size: 24rpx;
  margin-left: 10rpx;
}
</style> 
