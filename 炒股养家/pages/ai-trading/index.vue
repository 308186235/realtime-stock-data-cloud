  <!-- AI决策流程可视化 -->
  <view class="ai-decision-process" v-if="showDecisionProcess && currentDecision">
    <view class="process-card">
      <view class="process-header">
        <text class="process-title">AI决策流程分析</text>
        <text class="close-btn" @click="showDecisionProcess = false">×</text>
      </view>
      
      <view class="process-body">
        <view class="target-stock">
          <text class="stock-symbol">{{ currentDecision.symbol }}</text>
          <text class="stock-name">{{ currentDecision.name }}</text>
          <text class="price">
            {{ formatNumber(currentDecision.price, 2) }}
            <text class="price-change" :class="{'positive': priceChange > 0, 'negative': priceChange < 0}">
              {{ priceChange > 0 ? '+' : '' }}{{ formatNumber(priceChange, 2) }}%
            </text>
          </text>
        </view>
        
        <view class="final-decision">
          <view class="decision-badge" :class="getActionClass(currentDecision.action)">
            {{ getActionText(currentDecision.action) }}
          </view>
          <text class="confidence-text">置信度: {{ formatNumber(currentDecision.confidence * 100, 0) }}%</text>
        </view>
        
        <view class="decision-factors">
          <view class="factor-header">
            <text class="factor-title">决策因素分析</text>
          </view>
          
          <!-- 技术分析因子 -->
          <view class="factor-group">
            <view class="factor-name">
              <text class="factor-label">技术分析</text>
              <text class="factor-weight">40%</text>
            </view>
            <view class="factor-items">
              <view class="factor-item" v-if="decisionFactors.technical?.technical_indicators">
                <text class="item-name">技术指标</text>
                <text class="item-value" :class="getSignalClass(decisionFactors.technical.technical_indicators.signal)">
                  {{ getSignalText(decisionFactors.technical.technical_indicators.signal) }}
                  ({{ decisionFactors.technical.technical_indicators.bullish_count || 0 }}/{{ decisionFactors.technical.technical_indicators.bearish_count || 0 }})
                </text>
              </view>
              <view class="factor-item" v-if="decisionFactors.technical?.price_trend">
                <text class="item-name">价格趋势</text>
                <text class="item-value" :class="getDirectionClass(decisionFactors.technical.price_trend.direction)">
                  {{ getDirectionText(decisionFactors.technical.price_trend.direction) }}
                </text>
              </view>
              <view class="factor-item" v-if="decisionFactors.technical?.t_trading">
                <text class="item-name">T交易信号</text>
                <text class="item-value" :class="decisionFactors.technical.t_trading.has_opportunity ? 'positive' : 'neutral'">
                  {{ decisionFactors.technical.t_trading.has_opportunity ? (decisionFactors.technical.t_trading.mode === 'positive' ? '正T机会' : '反T机会') : '无机会' }}
                </text>
              </view>
            </view>
          </view>
          
          <!-- 量价分析因子 -->
          <view class="factor-group">
            <view class="factor-name">
              <text class="factor-label">量价分析</text>
              <text class="factor-weight">30%</text>
            </view>
            <view class="factor-items">
              <view class="factor-item" v-if="decisionFactors.volume_price">
                <text class="item-name">成交量比</text>
                <text class="item-value">{{ formatNumber(decisionFactors.volume_price.volume_ratio, 2) }}x</text>
              </view>
              <view class="factor-item" v-if="decisionFactors.volume_price">
                <text class="item-name">量价模式</text>
                <text class="item-value" :class="getSignalClass(decisionFactors.volume_price.signal)">
                  {{ decisionFactors.volume_price.pattern }}
                </text>
              </view>
            </view>
          </view>
          
          <!-- 市场情绪因子 -->
          <view class="factor-group">
            <view class="factor-name">
              <text class="factor-label">市场情绪</text>
              <text class="factor-weight">15%</text>
            </view>
            <view class="factor-items">
              <view class="factor-item" v-if="decisionFactors.market_sentiment">
                <text class="item-name">情绪指数</text>
                <text class="item-value">{{ decisionFactors.market_sentiment.score }}分</text>
              </view>
              <view class="factor-item" v-if="decisionFactors.market_sentiment">
                <text class="item-name">情绪偏向</text>
                <text class="item-value" :class="getSignalClass(decisionFactors.market_sentiment.signal)">
                  {{ decisionFactors.market_sentiment.sentiment }}
                </text>
              </view>
            </view>
          </view>
          
          <!-- 历史绩效因子 -->
          <view class="factor-group">
            <view class="factor-name">
              <text class="factor-label">历史绩效</text>
              <text class="factor-weight">15%</text>
            </view>
            <view class="factor-items">
              <view class="factor-item" v-if="decisionFactors.historical_performance">
                <text class="item-name">相似案例</text>
                <text class="item-value">{{ decisionFactors.historical_performance.similar_cases }}个</text>
              </view>
              <view class="factor-item" v-if="decisionFactors.historical_performance">
                <text class="item-name">成功率</text>
                <text class="item-value" :class="getSuccessRateClass(decisionFactors.historical_performance.success_rate)">
                  {{ formatNumber(decisionFactors.historical_performance.success_rate * 100, 0) }}%
                </text>
              </view>
            </view>
          </view>
        </view>
        
        <!-- 决策理由 -->
        <view class="decision-reasons">
          <text class="reasons-title">决策理由:</text>
          <view class="reason-list">
            <text 
              v-for="(reason, index) in currentDecision.reasons" 
              :key="index" 
              class="reason-item"
            >
              {{ index + 1 }}. {{ reason }}
            </text>
          </view>
        </view>
        
        <!-- 风险收益分析 -->
        <view class="risk-reward-analysis" v-if="currentDecision.risk_reward">
          <text class="analysis-title">风险收益分析:</text>
          
          <view class="analysis-content">
            <view class="analysis-row">
              <view class="analysis-item">
                <text class="item-label">目标价格</text>
                <text class="item-value">{{ formatNumber(currentDecision.risk_reward.target_price, 2) }}</text>
              </view>
              <view class="analysis-item">
                <text class="item-label">止损价格</text>
                <text class="item-value">{{ formatNumber(currentDecision.risk_reward.stop_loss, 2) }}</text>
              </view>
            </view>
            
            <view class="analysis-row">
              <view class="analysis-item">
                <text class="item-label">预期收益</text>
                <text class="item-value positive">¥{{ formatNumber(currentDecision.risk_reward.potential_gain, 2) }}</text>
              </view>
              <view class="analysis-item">
                <text class="item-label">预期风险</text>
                <text class="item-value negative">¥{{ formatNumber(currentDecision.risk_reward.potential_loss, 2) }}</text>
              </view>
            </view>
            
            <view class="risk-reward-ratio">
              <text class="ratio-label">风险收益比:</text>
              <text class="ratio-value">1:{{ formatNumber(currentDecision.risk_reward.risk_reward_ratio, 2) }}</text>
            </view>
          </view>
        </view>
        
        <view class="decision-actions">
          <button 
            class="action-btn" 
            :class="getActionButtonClass(currentDecision.action)"
            @click="executeAIDecision"
            v-if="currentDecision.action !== 'hold'"
          >
            执行{{ getActionText(currentDecision.action) }}
          </button>
          <button class="action-btn cancel" @click="showDecisionProcess = false">
            关闭
          </button>
        </view>
      </view>
    </view>
  </view>

  <!-- 添加回测/实盘切换入口 -->
  <view class="environment-selector">
    <text class="environment-label">当前环境:</text>
    <text class="environment-value" :class="{'env-live': currentEnvironment === 'live', 'env-backtest': currentEnvironment === 'backtest'}">
      {{ currentEnvironment === 'live' ? '实盘交易' : '回测模式' }}
    </text>
    <button class="switch-env-btn" size="mini" @click="toggleEnvironmentView">
      切换到{{ currentEnvironment === 'live' ? '回测' : '实盘' }}
    </button>
  </view>
  
  <!-- 回测面板 -->
  <backtest-panel v-if="showBacktestPanel" />

  <script>
  import BacktestPanel from '../../components/ai/BacktestPanel.vue';
  import agentTradingService from '../../services/agentTradingService.js';
  
  export default {
    components: {
      BacktestPanel
    },
    data() {
      return {
        // 添加决策流程相关数据
        showDecisionProcess: false,
        currentDecision: null,
        decisionFactors: {},
        priceChange: 0.0,
        
        // 环境相关数据
        currentEnvironment: 'live',
        showBacktestPanel: false
      };
    },
    
    async created() {
      // 获取当前环境
      try {
        const result = await agentTradingService.getCurrentEnvironment();
        if (result.success) {
          this.currentEnvironment = result.environment;
          this.showBacktestPanel = this.currentEnvironment === 'backtest';
        }
      } catch (e) {
        console.error('获取当前环境失败:', e);
      }
    },
    
    methods: {
      // 添加环境切换方法
      async toggleEnvironmentView() {
        const newEnvironment = this.currentEnvironment === 'live' ? 'backtest' : 'live';
        
        try {
          const result = await agentTradingService.setTradingEnvironment(newEnvironment);
          
          if (result.success) {
            this.currentEnvironment = newEnvironment;
            this.showBacktestPanel = newEnvironment === 'backtest';
            
            uni.showToast({
              title: `已切换到${newEnvironment === 'live' ? '实盘' : '回测'}环境`,
              icon: 'success'
            });
          } else {
            uni.showToast({
              title: result.message || '环境切换失败',
              icon: 'none'
            });
          }
        } catch (e) {
          console.error('环境切换失败:', e);
          uni.showToast({
            title: '环境切换失败',
            icon: 'none'
          });
        }
      },
      
      // 显示AI决策流程
      showAIDecisionProcess(decision) {
        this.currentDecision = decision;
        this.decisionFactors = decision.factors || {};
        this.priceChange = 0.75; // 模拟价格变动,实际应该从股票数据中获取
        this.showDecisionProcess = true;
      },
      
      // 格式化数字
      formatNumber(num, digits = 0) {
        return Number(num).toFixed(digits);
      },
      
      // 获取操作类名
      getActionClass(action) {
        switch(action.toLowerCase()) {
          case 'buy':
            return 'buy-action';
          case 'sell':
            return 'sell-action';
          default:
            return 'hold-action';
        }
      },
      
      // 获取操作文本
      getActionText(action) {
        switch(action.toLowerCase()) {
          case 'buy':
            return '买入';
          case 'sell':
            return '卖出';
          default:
            return '持有';
        }
      },
      
      // 获取信号类名
      getSignalClass(signal) {
        switch(signal) {
          case 'bullish':
            return 'positive';
          case 'bearish':
            return 'negative';
          default:
            return 'neutral';
        }
      },
      
      // 获取信号文本
      getSignalText(signal) {
        switch(signal) {
          case 'bullish':
            return '看涨';
          case 'bearish':
            return '看跌';
          default:
            return '中性';
        }
      },
      
      // 获取方向类名
      getDirectionClass(direction) {
        switch(direction) {
          case 'up':
            return 'positive';
          case 'down':
            return 'negative';
          default:
            return 'neutral';
        }
      },
      
      // 获取方向文本
      getDirectionText(direction) {
        switch(direction) {
          case 'up':
            return '上涨';
          case 'down':
            return '下跌';
          case 'sideways':
            return '震荡';
          default:
            return '未知';
        }
      },
      
      // 获取成功率类名
      getSuccessRateClass(rate) {
        if (rate > 0.7) return 'positive';
        if (rate > 0.5) return 'neutral';
        return 'negative';
      },
      
      // 获取操作按钮类名
      getActionButtonClass(action) {
        switch(action.toLowerCase()) {
          case 'buy':
            return 'buy-btn';
          case 'sell':
            return 'sell-btn';
          default:
            return 'hold-btn';
        }
      },
      
      // 执行AI决策
      executeAIDecision() {
        if (!this.currentDecision) return;
        
        // 实际项目中应调用交易API
        uni.showLoading({
          title: '执行交易中...'
        });
        
        setTimeout(() => {
          uni.hideLoading();
          uni.showToast({
            title: '交易已执行',
            icon: 'success'
          });
          this.showDecisionProcess = false;
        }, 1500);
      }
    }
  }
  </script>

  <style>
  .ai-decision-process {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
  }
  
  .process-card {
    width: 90%;
    max-width: 650px;
    max-height: 80vh;
    background-color: #fff;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
    display: flex;
    flex-direction: column;
  }
  
  .process-header {
    padding: 15px;
    background-color: #f8f8f8;
    display: flex;
    justify-content: space-between;
    border-bottom: 1px solid #eee;
  }
  
  .process-title {
    font-size: 18px;
    font-weight: bold;
  }
  
  .close-btn {
    font-size: 22px;
    color: #999;
    cursor: pointer;
  }
  
  .process-body {
    padding: 15px;
    overflow-y: auto;
  }
  
  .target-stock {
    display: flex;
    align-items: baseline;
    margin-bottom: 15px;
  }
  
  .stock-symbol {
    font-size: 18px;
    font-weight: bold;
    margin-right: 8px;
  }
  
  .stock-name {
    font-size: 16px;
    color: #666;
    margin-right: 15px;
  }
  
  .price {
    font-size: 18px;
    font-weight: bold;
  }
  
  .price-change {
    font-size: 14px;
    margin-left: 5px;
  }
  
  .positive {
    color: #f56c6c;
  }
  
  .negative {
    color: #07c160;
  }
  
  .neutral {
    color: #909399;
  }
  
  .final-decision {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
  }
  
  .decision-badge {
    padding: 5px 15px;
    border-radius: 5px;
    font-weight: bold;
    color: #fff;
    margin-right: 15px;
  }
  
  .buy-action {
    background-color: #f56c6c;
  }
  
  .sell-action {
    background-color: #07c160;
  }
  
  .hold-action {
    background-color: #909399;
  }
  
  .confidence-text {
    font-size: 16px;
    color: #666;
  }
  
  .decision-factors {
    border: 1px solid #eee;
    border-radius: 5px;
    margin-bottom: 20px;
  }
  
  .factor-header {
    padding: 10px 15px;
    background-color: #f8f8f8;
    border-bottom: 1px solid #eee;
  }
  
  .factor-title {
    font-size: 16px;
    font-weight: bold;
  }
  
  .factor-group {
    padding: 10px 15px;
    border-bottom: 1px solid #eee;
  }
  
  .factor-group:last-child {
    border-bottom: none;
  }
  
  .factor-name {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
  }
  
  .factor-label {
    font-size: 16px;
    font-weight: bold;
  }
  
  .factor-weight {
    font-size: 14px;
    color: #999;
  }
  
  .factor-items {
    display: flex;
    flex-wrap: wrap;
  }
  
  .factor-item {
    width: 50%;
    margin-bottom: 8px;
  }
  
  .item-name {
    font-size: 14px;
    color: #666;
    display: block;
  }
  
  .item-value {
    font-size: 16px;
    font-weight: bold;
  }
  
  .decision-reasons {
    margin-bottom: 20px;
  }
  
  .reasons-title {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 10px;
    display: block;
  }
  
  .reason-item {
    display: block;
    margin-bottom: 5px;
    padding-left: 10px;
    position: relative;
    line-height: 1.4;
  }
  
  .risk-reward-analysis {
    margin-bottom: 20px;
    border: 1px solid #eee;
    border-radius: 5px;
    padding: 15px;
    background-color: #fafafa;
  }
  
  .analysis-title {
    font-size: 16px;
    font-weight: bold;
    display: block;
    margin-bottom: 15px;
  }
  
  .analysis-content {
    display: flex;
    flex-direction: column;
  }
  
  .analysis-row {
    display: flex;
    margin-bottom: 15px;
  }
  
  .analysis-item {
    width: 50%;
  }
  
  .item-label {
    font-size: 14px;
    color: #666;
    display: block;
    margin-bottom: 5px;
  }
  
  .item-value {
    font-size: 16px;
    font-weight: bold;
  }
  
  .risk-reward-ratio {
    padding-top: 10px;
    border-top: 1px dotted #eee;
    display: flex;
    align-items: center;
  }
  
  .ratio-label {
    font-size: 14px;
    margin-right: 10px;
  }
  
  .ratio-value {
    font-size: 16px;
    font-weight: bold;
  }
  
  .decision-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
  
  .action-btn {
    padding: 8px 20px;
    border: none;
    border-radius: 5px;
    color: #fff;
    font-weight: bold;
    margin-left: 10px;
  }
  
  .buy-btn {
    background-color: #f56c6c;
  }
  
  .sell-btn {
    background-color: #07c160;
  }
  
  .cancel {
    background-color: #909399;
  }
  
  /* 环境选择器样式 */
  .environment-selector {
    display: flex;
    align-items: center;
    background-color: #f8f8f8;
    padding: 10px 15px;
    border-radius: 8px;
    margin-bottom: 15px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  }
  
  .environment-label {
    font-size: 14px;
    color: #666;
    margin-right: 10px;
  }
  
  .environment-value {
    font-size: 16px;
    font-weight: bold;
    margin-right: 20px;
  }
  
  .env-live {
    color: #19be6b;
  }
  
  .env-backtest {
    color: #ff9900;
  }
  
  .switch-env-btn {
    background-color: #007aff;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 4px 12px;
    font-size: 12px;
    margin-left: auto;
  }
  </style> 
