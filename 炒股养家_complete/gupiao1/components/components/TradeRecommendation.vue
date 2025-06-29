<template>
  <view class="trade-recommendation">
    <view class="recommendation-header">
      <text class="title">交易决策</text>
      <view class="score-badge" :style="{ backgroundColor: getScoreColor(decision.score) }">
        <text class="score-text">{{ Math.round(decision.score) }}</text>
      </view>
    </view>
    
    <!-- 主要建议 -->
    <view class="main-recommendation">
      <view class="action-badge" :class="getActionClass(decision.action)">
        <text class="action-text">{{ getActionText(decision.action) }}</text>
      </view>
      <text class="recommendation-title">{{ getRecommendationTitle(decision.action) }}</text>
      <text class="confidence-level">信心水平: {{ getConfidenceText(decision.confidence) }}</text>
    </view>
    
    <!-- 建议详情 -->
    <view class="recommendation-details">
      <text class="details-text">{{ decision.description }}</text>
    </view>
    
    <!-- 决策依据 -->
    <view class="decision-rationale" v-if="decision.detailedReasons">
      <text class="rationale-title">决策依据</text>
      <text class="rationale-text">{{ decision.detailedReasons }}</text>
      
      <!-- 关键信号指标 -->
      <view class="signal-indicators" v-if="decision.signalDetails && hasSignals">
        <text class="signals-title">关键信号指标</text>
        
        <!-- 技术指标 -->
        <view class="signal-group" v-if="decision.signalDetails.technical && decision.signalDetails.technical.length > 0">
          <text class="signal-group-title">技术指标</text>
          <view class="signal-tags">
            <view 
              v-for="(signal, index) in decision.signalDetails.technical" 
              :key="'tech-'+index" 
              class="signal-tag"
              :class="signal.type === 'bullish' ? 'bullish-tag' : 'bearish-tag'"
            >
              <text class="signal-tag-text">{{ signal.name }}</text>
            </view>
          </view>
        </view>
        
        <!-- 形态信号 -->
        <view class="signal-group" v-if="decision.signalDetails.pattern && decision.signalDetails.pattern.length > 0">
          <text class="signal-group-title">形态识别</text>
          <view class="signal-tags">
            <view 
              v-for="(signal, index) in decision.signalDetails.pattern" 
              :key="'pattern-'+index" 
              class="signal-tag"
              :class="signal.type === 'bullish' ? 'bullish-tag' : 'bearish-tag'"
            >
              <text class="signal-tag-text">{{ signal.name }}</text>
            </view>
          </view>
        </view>
        
        <!-- 量价信号 -->
        <view class="signal-group" v-if="decision.signalDetails.volume && decision.signalDetails.volume.length > 0">
          <text class="signal-group-title">量价关系</text>
          <view class="signal-tags">
            <view 
              v-for="(signal, index) in decision.signalDetails.volume" 
              :key="'volume-'+index" 
              class="signal-tag"
              :class="signal.type === 'bullish' ? 'bullish-tag' : 'bearish-tag'"
            >
              <text class="signal-tag-text">{{ signal.name }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 仓位建议 -->
    <view class="position-recommendation">
      <text class="position-title">建议仓位</text>
      <view class="position-bar-container">
        <view class="position-bar" :style="{ width: `${decision.allocation * 100}%`, backgroundColor: getPositionColor(decision.action) }"></view>
      </view>
      <text class="position-value">{{ Math.round(decision.allocation * 100) }}%</text>
    </view>
    
    <!-- 策略贡献 -->
    <view class="strategy-contributions">
      <text class="contributions-title">策略贡献</text>
      <view class="contribution-item" v-for="(contribution, key) in strategyContributions" :key="key">
        <text class="contribution-name">{{ getStrategyName(key) }}</text>
        <view class="contribution-bar-container">
          <view class="contribution-bar" :style="{ width: `${contribution.percentage}%`, backgroundColor: contribution.color }"></view>
        </view>
        <text class="contribution-value">{{ contribution.percentage }}%</text>
      </view>
    </view>
    
    <!-- 风险提示 -->
    <view class="risk-warning">
      <text class="warning-icon">⚠️</text>
      <text class="warning-text">{{ getRiskWarning(decision) }}</text>
    </view>
    
    <!-- 操作按钮 -->
    <view class="action-buttons">
      <view class="action-button primary" @click="executeAction">
        <text class="button-text">执行建议</text>
      </view>
      <view class="action-button secondary" @click="showDetails">
        <text class="button-text">查看详情</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  props: {
    decision: {
      type: Object,
      default: () => ({
        action: 'hold',
        confidence: 'medium',
        allocation: 0.5,
        description: '市场信号中性,建议持有现有仓位或观望。',
        score: 50
      })
    },
    strategyResults: {
      type: Object,
      default: () => ({
        sixSword: { overallScore: 50 },
        jiuFang: { summary: { recommendation: '观望' } },
        compass: { overallScore: 50 }
      })
    },
    weights: {
      type: Object,
      default: () => ({
        sixSword: 0.35,
        jiuFang: 0.35,
        compass: 0.30
      })
    }
  },
  
  computed: {
    strategyContributions() {
      // 计算各个策略的贡献
      const contributions = {};
      
      // 六脉神剑贡献
      contributions.sixSword = {
        score: this.strategyResults.sixSword.overallScore * this.weights.sixSword,
        percentage: Math.round(this.weights.sixSword * 100),
        color: '#1989fa'
      };
      
      // 九方智投贡献
      contributions.jiuFang = {
        score: this.getJiuFangScore() * this.weights.jiuFang,
        percentage: Math.round(this.weights.jiuFang * 100),
        color: '#07c160'
      };
      
      // 指南针贡献
      contributions.compass = {
        score: this.strategyResults.compass.overallScore * this.weights.compass,
        percentage: Math.round(this.weights.compass * 100),
        color: '#ff9900'
      };
      
      return contributions;
    },
    
    hasSignals() {
      if (!this.decision.signalDetails) return false;
      
      const { technical, pattern, volume, trend } = this.decision.signalDetails;
      
      return (
        (technical && technical.length > 0) || 
        (pattern && pattern.length > 0) || 
        (volume && volume.length > 0) || 
        (trend && trend.length > 0)
      );
    }
  },
  
  methods: {
    getJiuFangScore() {
      // 根据九方智投的推荐转换为分数
      const recommendation = this.strategyResults.jiuFang.summary.recommendation;
      
      switch (recommendation) {
        case '买入': return 75;
        case '谨慎买入': return 65;
        case '观望': return 50;
        case '谨慎卖出': return 35;
        case '卖出': return 25;
        default: return 50;
      }
    },
    
    getScoreColor(score) {
      if (score >= 80) return '#ee0a24'; // 红色
      if (score >= 60) return '#1989fa'; // 蓝色
      if (score >= 40) return '#ff9900'; // 橙色
      return '#07c160'; // 绿色
    },
    
    getActionClass(action) {
      if (action === 'strong_buy' || action === 'buy') return 'action-buy';
      if (action === 'strong_sell' || action === 'sell') return 'action-sell';
      return 'action-hold';
    },
    
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
    
    getConfidenceText(confidence) {
      const confidenceTexts = {
        'high': '高',
        'medium': '中',
        'low': '低'
      };
      
      return confidenceTexts[confidence] || '未知';
    },
    
    getRecommendationTitle(action) {
      if (action === 'strong_buy') return '强烈看好该股票';
      if (action === 'buy') return '看好该股票';
      if (action === 'hold') return '中性观望';
      if (action === 'sell') return '看空该股票';
      if (action === 'strong_sell') return '强烈看空该股票';
      return '未知';
    },
    
    getPositionColor(action) {
      if (action === 'strong_buy' || action === 'buy') return '#ee0a24';
      if (action === 'hold') return '#1989fa';
      return '#07c160';
    },
    
    getStrategyName(key) {
      const names = {
        sixSword: '六脉神剑',
        jiuFang: '九方智投',
        compass: '指南针'
      };
      
      return names[key] || key;
    },
    
    getRiskWarning(decision) {
      // 根据决策生成风险提示
      if (decision.action === 'strong_buy' || decision.action === 'buy') {
        return '投资有风险,入市需谨慎。即使AI分析看好,也请结合自身风险承受能力和市场环境做出判断。';
      } else if (decision.action === 'strong_sell' || decision.action === 'sell') {
        return '卖出决策可能导致错过后续上涨行情,请结合自身投资目标和持仓成本综合考虑。';
      } else {
        return '市场存在不确定性,建议密切关注市场变化,及时调整策略。';
      }
    },
    
    executeAction() {
      // 执行建议的操作
      this.$emit('execute', {
        action: this.decision.action,
        allocation: this.decision.allocation
      });
    },
    
    showDetails() {
      // 显示详细分析
      this.$emit('showDetails');
    }
  }
};
</script>

<style>
.trade-recommendation {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
}

.recommendation-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.title {
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

.score-text {
  color: #fff;
  font-size: 28rpx;
  font-weight: bold;
}

.main-recommendation {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30rpx;
}

.action-badge {
  padding: 10rpx 30rpx;
  border-radius: 30rpx;
  margin-bottom: 15rpx;
}

.action-buy {
  background-color: rgba(238, 10, 36, 0.1);
  border: 1rpx solid #ee0a24;
}

.action-sell {
  background-color: rgba(7, 193, 96, 0.1);
  border: 1rpx solid #07c160;
}

.action-hold {
  background-color: rgba(25, 137, 250, 0.1);
  border: 1rpx solid #1989fa;
}

.action-text {
  font-size: 32rpx;
  font-weight: bold;
}

.action-buy .action-text {
  color: #ee0a24;
}

.action-sell .action-text {
  color: #07c160;
}

.action-hold .action-text {
  color: #1989fa;
}

.recommendation-title {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 10rpx;
}

.confidence-level {
  font-size: 24rpx;
  color: #666;
}

.recommendation-details {
  padding: 15rpx;
  background-color: #f9f9f9;
  border-radius: 8rpx;
  margin-bottom: 20rpx;
}

.details-text {
  font-size: 26rpx;
  color: #333;
  line-height: 1.5;
}

.position-recommendation {
  margin-bottom: 20rpx;
}

.position-title {
  font-size: 26rpx;
  font-weight: bold;
  margin-bottom: 10rpx;
}

.position-bar-container {
  height: 20rpx;
  background-color: #f5f5f5;
  border-radius: 10rpx;
  overflow: hidden;
  margin-bottom: 5rpx;
}

.position-bar {
  height: 100%;
  border-radius: 10rpx;
}

.position-value {
  font-size: 24rpx;
  color: #666;
  text-align: right;
}

.strategy-contributions {
  margin-bottom: 20rpx;
}

.contributions-title {
  font-size: 26rpx;
  font-weight: bold;
  margin-bottom: 10rpx;
}

.contribution-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 10rpx;
}

.contribution-name {
  font-size: 24rpx;
  color: #333;
  width: 150rpx;
}

.contribution-bar-container {
  flex: 1;
  height: 16rpx;
  background-color: #f5f5f5;
  border-radius: 8rpx;
  overflow: hidden;
  margin: 0 15rpx;
}

.contribution-bar {
  height: 100%;
  border-radius: 8rpx;
}

.contribution-value {
  font-size: 24rpx;
  color: #666;
  width: 60rpx;
  text-align: right;
}

.risk-warning {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  padding: 15rpx;
  background-color: rgba(255, 153, 0, 0.1);
  border-radius: 8rpx;
  margin-bottom: 20rpx;
}

.warning-icon {
  font-size: 28rpx;
  margin-right: 10rpx;
}

.warning-text {
  font-size: 24rpx;
  color: #ff9900;
  line-height: 1.4;
  flex: 1;
}

.action-buttons {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.action-button {
  flex: 1;
  height: 80rpx;
  border-radius: 40rpx;
  justify-content: center;
  align-items: center;
  margin: 0 10rpx;
}

.action-button.primary {
  background-color: #1989fa;
}

.action-button.secondary {
  background-color: #f5f5f5;
}

.button-text {
  font-size: 28rpx;
}

.primary .button-text {
  color: #fff;
}

.secondary .button-text {
  color: #333;
}

/* 决策依据样式 */
.decision-rationale {
  margin-top: 15rpx;
  padding: 15rpx;
  background-color: #f9f9f9;
  border-radius: 8rpx;
  margin-bottom: 20rpx;
}

.rationale-title {
  font-size: 26rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 8rpx;
}

.rationale-text {
  font-size: 24rpx;
  line-height: 1.5;
  color: #666;
  margin-bottom: 12rpx;
}

.signals-title {
  font-size: 24rpx;
  font-weight: bold;
  color: #333;
  margin: 12rpx 0 8rpx;
}

.signal-group {
  margin-bottom: 10rpx;
}

.signal-group-title {
  font-size: 22rpx;
  color: #666;
  margin-bottom: 8rpx;
}

.signal-tags {
  display: flex;
  flex-wrap: wrap;
}

.signal-tag {
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
  margin-right: 8rpx;
  margin-bottom: 8rpx;
}

.bullish-tag {
  background-color: rgba(238, 10, 36, 0.1);
}

.bearish-tag {
  background-color: rgba(7, 193, 96, 0.1);
}

.signal-tag-text {
  font-size: 22rpx;
}

.bullish-tag .signal-tag-text {
  color: #ee0a24;
}

.bearish-tag .signal-tag-text {
  color: #07c160;
}

.profit {
  color: #ee0a24;
}

.loss {
  color: #07c160;
}
</style> 
