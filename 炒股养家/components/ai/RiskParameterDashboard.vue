<template>
  <view class="risk-dashboard-container">
    <view class="dashboard-header">
      <text class="dashboard-title">风险参数学习面板</text>
      <view class="status-badge" :class="{'active': learningEnabled, 'inactive': !learningEnabled}">
        {{ learningEnabled ? '学习中' : '未启用学习' }}
      </view>
    </view>
    
    <view class="stats-section" v-if="stats">
      <view class="stats-header">
        <text class="section-title">学习统计</text>
        <button class="refresh-btn" size="mini" type="default" @click="fetchStats">刷新</button>
      </view>
      
      <view class="stat-cards">
        <view class="stat-card">
          <text class="stat-value">{{ stats.records_count || 0 }}</text>
          <text class="stat-label">风险记录数</text>
        </view>
        
        <view class="stat-card">
          <text class="stat-value">{{ stats.successful_trades_count || 0 }}</text>
          <text class="stat-label">成功交易数</text>
        </view>
        
        <view class="stat-card">
          <text class="stat-value" :class="getSuccessRateClass(stats.overall_success_rate)">
            {{ formatPercent(stats.overall_success_rate) }}
          </text>
          <text class="stat-label">总成功率</text>
        </view>
        
        <view class="stat-card">
          <text class="stat-value" :class="getRiskClass(stats.current_risk_level)">
            {{ getRiskLevelText(stats.current_risk_level) }}
          </text>
          <text class="stat-label">当前风险级别</text>
        </view>
      </view>
      
      <view class="thresholds-table" v-if="stats.current_thresholds">
        <view class="table-header">
          <text class="table-title">当前阈值参数</text>
          <text class="risk-level-tag" :class="getRiskClass(stats.current_risk_level)">
            {{ getRiskLevelText(stats.current_risk_level) }}风险
          </text>
        </view>
        
        <view class="parameter-list">
          <view class="parameter-item" v-for="(value, key) in stats.current_thresholds" :key="key">
            <text class="param-name">{{ getParameterName(key) }}</text>
            <text class="param-value">{{ formatValue(key, value) }}</text>
            <view class="param-trend" v-if="getParameterTrend(key)">
              <text class="trend-arrow" :class="getParameterTrend(key)">
                {{ getParameterTrend(key) === 'increase' ? '↑' : '↓' }}
              </text>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <view class="learning-history-section" v-if="learningHistory.length > 0">
      <text class="section-title">参数学习历史</text>
      
      <scroll-view class="history-list" scroll-y="true">
        <view 
          v-for="(record, index) in learningHistory" 
          :key="index" 
          class="history-item"
          :class="{'success': record.result === 'success', 'failure': record.result === 'failure'}"
        >
          <view class="history-header">
            <text class="history-date">{{ formatTime(record.timestamp) }}</text>
            <text class="history-result">{{ getResultText(record.result) }}</text>
          </view>
          
          <view class="history-details">
            <text class="detail-item">决策: {{ getActionText(record.action) }}</text>
            <text class="detail-item">置信度: {{ formatPercent(record.confidence) }}</text>
            <text class="detail-item">风险评估: {{ getRiskLevelText(record.risk_level) }}</text>
            <text class="detail-item" v-if="record.profit_loss !== undefined">
              盈亏: <text :class="record.profit_loss > 0 ? 'positive' : record.profit_loss < 0 ? 'negative' : ''">
                {{ formatCurrency(record.profit_loss) }}
              </text>
            </text>
          </view>
        </view>
      </scroll-view>
    </view>
    
    <view class="learning-settings">
      <view class="settings-header">
        <text class="section-title">学习设置</text>
      </view>
      
      <uni-forms :model="learningSettings" label-position="top">
        <view class="form-row">
          <text class="form-label">启用风险参数学习:</text>
          <switch :checked="learningSettings.enable_learning" @change="onLearningChange" color="#007aff" />
        </view>
        
        <uni-forms-item label="风险级别">
          <uni-segmented-control 
            :values="['低风险', '中等风险', '高风险']" 
            :current="getRiskLevelIndex(learningSettings.risk_level)"
            @clickItem="onRiskLevelChange"
            styleType="button"
            activeColor="#007aff"
          />
        </uni-forms-item>
        
        <uni-forms-item label="仓位确定方法">
          <uni-segmented-control 
            :values="['固定', '置信度', 'Kelly', '自适应']" 
            :current="getPositionMethodIndex(learningSettings.position_sizing_method)"
            @clickItem="onPositionMethodChange"
            styleType="button"
            activeColor="#007aff"
          />
        </uni-forms-item>
        
        <uni-forms-item label="单股最大仓位比例">
          <slider 
            :min="5" 
            :max="50" 
            :value="learningSettings.max_position_per_stock * 100" 
            @change="onPositionPercentChange"
            show-value
          />
        </uni-forms-item>
        
        <uni-forms-item label="日亏损限制比例">
          <slider 
            :min="0.5" 
            :max="10" 
            :value="learningSettings.daily_loss_limit * 100" 
            @change="onLossLimitChange"
            show-value
          />
        </uni-forms-item>
      </uni-forms>
      
      <button type="primary" @click="saveSettings" class="save-btn">保存学习设置</button>
    </view>
    
    <view class="optimization-insight" v-if="optimizationInsight">
      <view class="insight-header">
        <text class="insight-title">优化建议</text>
        <text class="insight-time">{{ formatTime(optimizationInsight.timestamp) }}</text>
      </view>
      
      <view class="insight-content">
        <text class="insight-text">{{ optimizationInsight.message }}</text>
        
        <view class="recommendation-list">
          <text class="recommendation-item" v-for="(rec, index) in optimizationInsight.recommendations" :key="index">
            • {{ rec }}
          </text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { formatDate } from '../../utils/dateUtils.js';

export default {
  name: "RiskParameterDashboard",
  data() {
    return {
      learningEnabled: false,
      stats: null,
      learningHistory: [],
      parameterTrends: {},
      optimizationInsight: null,
      
      learningSettings: {
        enable_learning: true,
        risk_level: 'medium',
        position_sizing_method: 'confidence',
        max_position_per_stock: 0.2,
        daily_loss_limit: 0.02
      },
      
      // 参数名称映射
      parameterNameMap: {
        'confidence_threshold': '置信度阈值',
        'volatility_limit': '波动率限制',
        'position_factor': '仓位系数',
        'profit_target_multiplier': '止盈目标倍数',
        'stop_loss_multiplier': '止损距离倍数',
        'volume_requirement': '成交量要求',
        'max_trades_per_day': '每日最大交易数',
        'price_reversal_threshold': '价格反转阈值'
      }
    }
  },
  
  mounted() {
    this.fetchStats();
    this.fetchLearningHistory();
    
    // 模拟优化建议 (实际项目中应从后端获取)
    this.simulateOptimizationInsight();
  },
  
  methods: {
    // 获取风险参数统计
    async fetchStats() {
      try {
        // 实际项目应调用后端API
        const response = {
          learning_enabled: true,
          records_count: 156,
          successful_trades_count: 87,
          overall_success_rate: 0.56,
          current_risk_level: 'medium',
          current_thresholds: {
            confidence_threshold: 0.67,
            volatility_limit: 0.05,
            position_factor: 0.75,
            profit_target_multiplier: 1.2,
            stop_loss_multiplier: 0.8,
            volume_requirement: 1.0,
            max_trades_per_day: 5,
            price_reversal_threshold: 0.015
          },
          historical_thresholds: [
            // 最近5条历史记录
            { confidence_threshold: 0.65 },
            { confidence_threshold: 0.66 },
            { confidence_threshold: 0.66 },
            { confidence_threshold: 0.67 },
            { confidence_threshold: 0.67 }
          ],
          position_sizing_method: 'confidence',
          last_optimization_time: new Date().toISOString()
        };
        
        this.stats = response;
        this.learningEnabled = response.learning_enabled;
        
        // 计算参数趋势
        this.calculateParameterTrends();
        
        // 更新学习设置表单
        this.learningSettings.enable_learning = response.learning_enabled;
        this.learningSettings.risk_level = response.current_risk_level;
        this.learningSettings.position_sizing_method = response.position_sizing_method;
      } catch (e) {
        console.error('获取风险参数统计失败:', e);
        uni.showToast({
          title: '获取统计数据失败',
          icon: 'none'
        });
      }
    },
    
    // 获取学习历史记录
    async fetchLearningHistory() {
      try {
        // 实际项目应调用后端API
        const history = [
          {
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            action: 'buy',
            confidence: 0.78,
            risk_level: 'medium',
            result: 'success',
            profit_loss: 380.50
          },
          {
            timestamp: new Date(Date.now() - 7200000).toISOString(),
            action: 'sell',
            confidence: 0.62,
            risk_level: 'medium',
            result: 'failure',
            profit_loss: -120.30
          },
          {
            timestamp: new Date(Date.now() - 14400000).toISOString(),
            action: 'buy',
            confidence: 0.81,
            risk_level: 'low',
            result: 'success',
            profit_loss: 550.75
          },
          {
            timestamp: new Date(Date.now() - 28800000).toISOString(),
            action: 'sell',
            confidence: 0.74,
            risk_level: 'medium',
            result: 'success',
            profit_loss: 280.20
          },
          {
            timestamp: new Date(Date.now() - 86400000).toISOString(),
            action: 'buy',
            confidence: 0.59,
            risk_level: 'high',
            result: 'failure',
            profit_loss: -210.45
          }
        ];
        
        this.learningHistory = history;
      } catch (e) {
        console.error('获取学习历史记录失败:', e);
      }
    },
    
    // 计算参数趋势
    calculateParameterTrends() {
      if (!this.stats || !this.stats.historical_thresholds || this.stats.historical_thresholds.length < 2) {
        return;
      }
      
      const lastThresholds = this.stats.historical_thresholds[this.stats.historical_thresholds.length - 1];
      const prevThresholds = this.stats.historical_thresholds[this.stats.historical_thresholds.length - 2];
      
      // 比较关键参数的变化
      for (const key in lastThresholds) {
        if (prevThresholds[key] !== undefined) {
          if (lastThresholds[key] > prevThresholds[key]) {
            this.parameterTrends[key] = 'increase';
          } else if (lastThresholds[key] < prevThresholds[key]) {
            this.parameterTrends[key] = 'decrease';
          } else {
            this.parameterTrends[key] = null; // 无变化
          }
        }
      }
    },
    
    // 生成优化建议(实际项目中应从后端获取)
    simulateOptimizationInsight() {
      this.optimizationInsight = {
        timestamp: new Date().toISOString(),
        message: "系统分析了最近的87次交易结果,发现在以下条件下交易成功率显著提高:",
        recommendations: [
          "置信度阈值可以适当调低至0.63,发现更多交易机会",
          "成交量要求参数过高,可以降低至0.9",
          "Kelly公式在连续获利时表现更好,建议切换到Kelly仓位策略",
          "低波动率环境下,当前风险参数设置表现良好",
          "止损距离倍数可以适当提高,避免过早触发止损"
        ]
      };
    },
    
    // 保存学习设置
    async saveSettings() {
      try {
        // 实际项目应调用后端API
        uni.showLoading({
          title: '保存中...'
        });
        
        // 模拟API调用延迟
        setTimeout(() => {
          uni.hideLoading();
          uni.showToast({
            title: '设置已保存',
            icon: 'success'
          });
          
          // 刷新数据
          this.fetchStats();
        }, 800);
      } catch (e) {
        uni.hideLoading();
        console.error('保存学习设置失败:', e);
        uni.showToast({
          title: '保存设置失败',
          icon: 'none'
        });
      }
    },
    
    // 表单事件处理
    onLearningChange(e) {
      this.learningSettings.enable_learning = e.target.value;
    },
    
    onRiskLevelChange(e) {
      const riskLevels = ['low', 'medium', 'high'];
      this.learningSettings.risk_level = riskLevels[e.currentIndex];
    },
    
    onPositionMethodChange(e) {
      const methods = ['fixed', 'confidence', 'kelly', 'adaptive'];
      this.learningSettings.position_sizing_method = methods[e.currentIndex];
    },
    
    onPositionPercentChange(e) {
      this.learningSettings.max_position_per_stock = e.detail.value / 100;
    },
    
    onLossLimitChange(e) {
      this.learningSettings.daily_loss_limit = e.detail.value / 100;
    },
    
    // 辅助方法 - 格式化
    formatPercent(value) {
      if (value === undefined || value === null) return '-';
      return (value * 100).toFixed(1) + '%';
    },
    
    formatTime(timestamp) {
      if (!timestamp) return '-';
      return new Date(timestamp).toLocaleString();
    },
    
    formatCurrency(value) {
      if (value === undefined || value === null) return '-';
      return '¥' + value.toFixed(2);
    },
    
    formatValue(key, value) {
      if (key.includes('threshold') || key.includes('limit') || key.includes('factor') || key.includes('multiplier')) {
        return value.toFixed(2);
      } else if (key === 'max_trades_per_day') {
        return Math.round(value) + '次';
      } else if (key === 'volume_requirement') {
        return value.toFixed(1) + 'x';
      }
      return value;
    },
    
    // 辅助方法 - 获取样式类
    getSuccessRateClass(rate) {
      if (rate === undefined || rate === null) return '';
      if (rate >= 0.6) return 'positive';
      if (rate >= 0.5) return 'neutral';
      return 'negative';
    },
    
    getRiskClass(level) {
      if (level === 'low') return 'low-risk';
      if (level === 'high') return 'high-risk';
      return 'medium-risk';
    },
    
    // 辅助方法 - 获取显示文本
    getRiskLevelText(level) {
      if (level === 'low') return '低';
      if (level === 'high') return '高';
      return '中';
    },
    
    getActionText(action) {
      if (action === 'buy') return '买入';
      if (action === 'sell') return '卖出';
      return '持有';
    },
    
    getResultText(result) {
      if (result === 'success') return '成功';
      if (result === 'failure') return '失败';
      return '中性';
    },
    
    getParameterName(key) {
      return this.parameterNameMap[key] || key;
    },
    
    getParameterTrend(key) {
      return this.parameterTrends[key];
    },
    
    // 辅助方法 - 获取索引
    getRiskLevelIndex(level) {
      const levels = ['low', 'medium', 'high'];
      return levels.indexOf(level);
    },
    
    getPositionMethodIndex(method) {
      const methods = ['fixed', 'confidence', 'kelly', 'adaptive'];
      return methods.indexOf(method);
    }
  }
}
</script>

<style scoped>
.risk-dashboard-container {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 16px;
  margin: 10px 0;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dashboard-title {
  font-size: 18px;
  font-weight: bold;
}

.status-badge {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
  color: #ffffff;
}

.active {
  background-color: #19be6b;
}

.inactive {
  background-color: #909399;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  display: block;
}

.stats-section {
  margin-bottom: 20px;
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.refresh-btn {
  padding: 0 10px;
  height: 28px;
  line-height: 28px;
  font-size: 12px;
}

.stat-cards {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -5px;
}

.stat-card {
  flex: 1;
  min-width: calc(50% - 10px);
  background-color: #f8f8f8;
  border-radius: 6px;
  padding: 10px;
  margin: 5px;
  text-align: center;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  display: block;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #606266;
}

.positive {
  color: #f56c6c;
}

.negative {
  color: #19be6b;
}

.neutral {
  color: #e6a23c;
}

.low-risk {
  color: #19be6b;
}

.medium-risk {
  color: #e6a23c;
}

.high-risk {
  color: #f56c6c;
}

.thresholds-table {
  background-color: #f8f8f8;
  border-radius: 6px;
  padding: 12px;
  margin-top: 15px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.table-title {
  font-size: 14px;
  font-weight: bold;
}

.risk-level-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  border: 1px solid currentColor;
}

.parameter-list {
  display: flex;
  flex-wrap: wrap;
}

.parameter-item {
  width: 50%;
  padding: 5px 0;
  display: flex;
  align-items: center;
}

.param-name {
  width: 60%;
  font-size: 12px;
  color: #606266;
}

.param-value {
  width: 30%;
  font-size: 14px;
  font-weight: 500;
}

.param-trend {
  width: 10%;
}

.trend-arrow {
  font-size: 16px;
}

.increase {
  color: #f56c6c;
}

.decrease {
  color: #19be6b;
}

.learning-history-section {
  margin-bottom: 20px;
}

.history-list {
  max-height: 250px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
}

.history-item {
  padding: 10px;
  border-bottom: 1px solid #ebeef5;
}

.history-item:last-child {
  border-bottom: none;
}

.history-item.success {
  border-left: 3px solid #19be6b;
}

.history-item.failure {
  border-left: 3px solid #f56c6c;
}

.history-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.history-date {
  font-size: 12px;
  color: #909399;
}

.history-result {
  font-size: 12px;
  font-weight: bold;
}

.history-details {
  font-size: 13px;
}

.detail-item {
  display: block;
  margin-bottom: 2px;
}

.learning-settings {
  margin-bottom: 20px;
}

.settings-header {
  margin-bottom: 10px;
}

.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.form-label {
  flex: 1;
  font-size: 14px;
}

.save-btn {
  width: 100%;
}

.optimization-insight {
  background-color: #ecf5ff;
  border: 1px solid #d9ecff;
  border-radius: 6px;
  padding: 12px;
}

.insight-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.insight-title {
  font-size: 16px;
  font-weight: bold;
  color: #409eff;
}

.insight-time {
  font-size: 12px;
  color: #909399;
}

.insight-text {
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 10px;
  display: block;
}

.recommendation-list {
  margin-top: 10px;
}

.recommendation-item {
  font-size: 13px;
  line-height: 1.6;
  display: block;
  margin-bottom: 5px;
}
</style> 
