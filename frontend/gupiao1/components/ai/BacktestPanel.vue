<template>
  <view class="backtest-panel">
    <view class="panel-header">
      <view class="header-left">
        <text class="panel-title">Agent交易回测系统</text>
        <text class="environment-badge" :class="{ 'live': currentEnvironment === 'live', 'backtest': currentEnvironment === 'backtest' }">
          {{ currentEnvironment === 'live' ? '实盘环境' : '回测环境' }}
        </text>
      </view>
      <view class="header-right">
        <switch :checked="currentEnvironment === 'backtest'" @change="toggleEnvironment" color="#007aff" />
        <text class="switch-label">回测模式</text>
      </view>
    </view>
    
    <!-- 回测配置表单 -->
    <view class="backtest-form" v-if="currentEnvironment === 'backtest'">
      <uni-forms :model="backtestConfig" label-position="top">
        <uni-forms-item label="股票代码" required>
          <uni-easyinput v-model="backtestConfig.stock_code" placeholder="请输入股票代码" />
        </uni-forms-item>
        
        <view class="form-row">
          <uni-forms-item label="开始日期" required class="date-item">
            <uni-datetime-picker 
              v-model="backtestConfig.start_date" 
              type="date" 
              :end="backtestConfig.end_date || new Date()" 
            />
          </uni-forms-item>
          
          <uni-forms-item label="结束日期" required class="date-item">
            <uni-datetime-picker 
              v-model="backtestConfig.end_date" 
              type="date" 
              :start="backtestConfig.start_date" 
              :end="new Date()"
            />
          </uni-forms-item>
        </view>
        
        <uni-forms-item label="初始资金">
          <uni-number-box 
            :min="10000" 
            :max="10000000" 
            :step="10000" 
            v-model="backtestConfig.initial_capital" 
          />
        </uni-forms-item>
        
        <view class="strategy-params">
          <text class="param-title">策略参数</text>
          
          <view class="param-row">
            <text class="param-label">风险等级:</text>
            <uni-segmented-control 
              :values="['低风险', '中等风险', '高风险']" 
              :current="getRiskLevelIndex()"
              @clickItem="onSelectRiskLevel"
              styleType="button"
              activeColor="#007aff"
            />
          </view>
          
          <view class="param-row">
            <text class="param-label">最大持仓比例:</text>
            <slider 
              :min="10" 
              :max="100" 
              :value="backtestConfig.strategy_params.max_position_percent * 100" 
              @change="onPositionPercentChange"
              show-value
            />
          </view>
          
          <view class="param-row">
            <text class="param-label">交易方向:</text>
            <uni-segmented-control 
              :values="['仅多头', '仅空头', '双向交易']" 
              :current="getTradeDirectionIndex()"
              @clickItem="onSelectTradeDirection"
              styleType="button"
              activeColor="#007aff"
            />
          </view>
          
          <view class="param-row">
            <text class="param-label">自动执行:</text>
            <switch 
              :checked="backtestConfig.strategy_params.auto_execute" 
              @change="onAutoExecuteChange" 
              color="#007aff"
            />
          </view>
        </view>
        
        <view class="action-buttons">
          <button 
            class="load-data-btn" 
            type="primary" 
            size="mini" 
            :disabled="!backtestConfig.stock_code"
            @click="loadBacktestData"
          >
            加载数据
          </button>
          
          <button 
            class="run-backtest-btn" 
            type="success" 
            size="mini" 
            :disabled="!hasBacktestData || isRunning"
            @click="runBacktest"
          >
            {{ isRunning ? '运行中...' : '开始回测' }}
          </button>
        </view>
      </uni-forms>
    </view>
    
    <!-- 回测结果 -->
    <view class="backtest-results" v-if="backtestResults && currentEnvironment === 'backtest'">
      <view class="results-header">
        <text class="results-title">回测结果</text>
        <button type="default" size="mini" @click="exportResults">导出结果</button>
      </view>
      
      <!-- 性能指标卡片 -->
      <view class="metrics-card">
        <view class="metric-item">
          <text class="metric-value" :class="getReturnClass(backtestResults.metrics.total_return)">
            {{ formatPercent(backtestResults.metrics.total_return) }}
          </text>
          <text class="metric-label">总收益率</text>
        </view>
        
        <view class="metric-item">
          <text class="metric-value" :class="getReturnClass(backtestResults.metrics.annual_return)">
            {{ formatPercent(backtestResults.metrics.annual_return) }}
          </text>
          <text class="metric-label">年化收益</text>
        </view>
        
        <view class="metric-item">
          <text class="metric-value">
            {{ formatPercent(backtestResults.metrics.win_rate) }}
          </text>
          <text class="metric-label">胜率</text>
        </view>
        
        <view class="metric-item">
          <text class="metric-value negative">
            {{ formatPercent(backtestResults.metrics.max_drawdown) }}
          </text>
          <text class="metric-label">最大回撤</text>
        </view>
        
        <view class="metric-item">
          <text class="metric-value" :class="getSharpeRatioClass(backtestResults.metrics.sharpe_ratio)">
            {{ backtestResults.metrics.sharpe_ratio.toFixed(2) }}
          </text>
          <text class="metric-label">夏普比率</text>
        </view>
      </view>
      
      <!-- 交易记录表格 -->
      <view class="trades-table">
        <view class="table-header">
          <text class="header-cell date-cell">日期</text>
          <text class="header-cell type-cell">类型</text>
          <text class="header-cell price-cell">价格</text>
          <text class="header-cell quantity-cell">数量</text>
          <text class="header-cell profit-cell">盈亏</text>
        </view>
        
        <scroll-view class="table-body" scroll-y="true">
          <view 
            v-for="(trade, index) in backtestResults.trades" 
            :key="index" 
            class="table-row"
          >
            <text class="row-cell date-cell">{{ formatDate(trade.date) }}</text>
            <text class="row-cell type-cell" :class="{ 'buy': trade.action === 'buy', 'sell': trade.action === 'sell' }">
              {{ trade.action === 'buy' ? '买入' : '卖出' }}
            </text>
            <text class="row-cell price-cell">{{ trade.price.toFixed(2) }}</text>
            <text class="row-cell quantity-cell">{{ trade.quantity }}</text>
            <text class="row-cell profit-cell" :class="{ 'positive': trade.profit > 0, 'negative': trade.profit < 0 }" v-if="trade.profit != null">
              {{ trade.profit.toFixed(2) }}
            </text>
            <text class="row-cell profit-cell" v-else>-</text>
          </view>
        </scroll-view>
      </view>
    </view>
    
    <!-- 实盘风险控制配置 -->
    <view class="risk-control-panel" v-if="currentEnvironment === 'live'">
      <view class="panel-title">实盘交易风险控制</view>
      
      <uni-forms :model="riskControlConfig" label-position="top">
        <view class="form-row">
          <uni-forms-item label="风险级别" class="half-width">
            <uni-segmented-control 
              :values="['低风险', '中等风险', '高风险']" 
              :current="getRiskControlLevelIndex()"
              @clickItem="onSelectRiskControlLevel"
              styleType="button"
              activeColor="#007aff"
            />
          </uni-forms-item>
          
          <uni-forms-item label="仓位确定方法" class="half-width">
            <uni-segmented-control 
              :values="['固定', '置信度', 'Kelly公式']" 
              :current="getPositionSizingMethodIndex()"
              @clickItem="onSelectPositionSizingMethod"
              styleType="button"
              activeColor="#007aff"
            />
          </uni-forms-item>
        </view>
        
        <uni-forms-item label="单只股票最大仓位比例">
          <slider 
            :min="5" 
            :max="50" 
            :value="riskControlConfig.max_position_per_stock * 100" 
            @change="onMaxPositionChange"
            show-value
          />
        </uni-forms-item>
        
        <uni-forms-item label="日亏损限制比例">
          <slider 
            :min="0.5" 
            :max="10" 
            :value="riskControlConfig.daily_loss_limit * 100" 
            @change="onDailyLossLimitChange"
            show-value
          />
        </uni-forms-item>
        
        <button 
          type="primary" 
          @click="saveRiskControlSettings"
          class="save-settings-btn"
        >
          保存风险控制设置
        </button>
      </uni-forms>
      
      <view class="live-trading-tips">
        <view class="tips-title">实盘交易建议</view>
        <view class="tip-item">
          <text class="tip-icon">📈</text>
          <text class="tip-text">相比回测环境,实盘环境加强了风险控制,使用更保守的交易策略</text>
        </view>
        <view class="tip-item">
          <text class="tip-icon">⚠️</text>
          <text class="tip-text">低风险设置下,系统将提高交易置信度阈值,减少交易频率</text>
        </view>
        <view class="tip-item">
          <text class="tip-icon">💰</text>
          <text class="tip-text">建议从小仓位开始,持续监控系统表现,逐步调整参数</text>
        </view>
        <view class="tip-item">
          <text class="tip-icon">🔄</text>
          <text class="tip-text">系统会根据市场状况自动调整交易策略,但定期检查和优化风控设置非常重要</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import agentTradingService from '../../services/agentTradingService.js';

export default {
  name: "BacktestPanel",
  data() {
    return {
      currentEnvironment: 'live', // 默认为实盘环境
      isLoading: false,
      hasBacktestData: false,
      isRunning: false,
      
      // 回测配置
      backtestConfig: {
        stock_code: '',
        start_date: this.getDateString(-180), // 默认6个月前
        end_date: this.getDateString(0),      // 今天
        initial_capital: 100000,
        strategy_params: {
          risk_level: 'medium',
          max_position_percent: 0.5,
          trade_direction: 'both',
          auto_execute: true
        }
      },
      
      // 回测结果
      backtestResults: null,
      
      // 实盘风险控制配置
      riskControlConfig: {
        risk_level: 'medium',
        max_position_per_stock: 0.2,
        daily_loss_limit: 0.02,
        position_sizing_method: 'confidence'
      }
    }
  },
  
  async created() {
    try {
      // 获取当前环境
      const result = await agentTradingService.getCurrentEnvironment();
      if (result.success) {
        this.currentEnvironment = result.environment;
        
        // 获取实盘风险控制设置
        if (this.currentEnvironment === 'live') {
          // 这里应该从后端获取当前风险控制设置
          // 简化处理,使用默认设置
        }
      }
    } catch (e) {
      console.error('获取环境信息失败:', e);
      uni.showToast({
        title: '获取环境信息失败',
        icon: 'none'
      });
    }
  },
  
  methods: {
    // 切换交易环境
    async toggleEnvironment(e) {
      const newEnvironment = e.target.value ? 'backtest' : 'live';
      
      try {
        this.isLoading = true;
        const result = await agentTradingService.setTradingEnvironment(newEnvironment);
        
        if (result.success) {
          this.currentEnvironment = newEnvironment;
          
          uni.showToast({
            title: `已切换至${newEnvironment === 'live' ? '实盘' : '回测'}环境`,
            icon: 'success'
          });
          
          // 切换到回测环境时,重置回测结果
          if (newEnvironment === 'backtest') {
            this.backtestResults = null;
            this.hasBacktestData = false;
          }
        } else {
          uni.showToast({
            title: result.message || '切换环境失败',
            icon: 'none'
          });
        }
      } catch (e) {
        console.error('切换环境失败:', e);
        uni.showToast({
          title: '切换环境失败',
          icon: 'none'
        });
      } finally {
        this.isLoading = false;
      }
    },
    
    // 加载回测数据
    async loadBacktestData() {
      if (!this.backtestConfig.stock_code) {
        uni.showToast({
          title: '请输入股票代码',
          icon: 'none'
        });
        return;
      }
      
      try {
        this.isLoading = true;
        
        const result = await agentTradingService.loadBacktestData(this.backtestConfig.stock_code);
        
        if (result.success) {
          this.hasBacktestData = true;
          
          uni.showToast({
            title: result.message || '数据加载成功',
            icon: 'success'
          });
        } else {
          uni.showToast({
            title: result.message || '数据加载失败',
            icon: 'none'
          });
        }
      } catch (e) {
        console.error('加载回测数据失败:', e);
        uni.showToast({
          title: '加载回测数据失败',
          icon: 'none'
        });
      } finally {
        this.isLoading = false;
      }
    },
    
    // 运行回测
    async runBacktest() {
      if (!this.hasBacktestData) {
        uni.showToast({
          title: '请先加载回测数据',
          icon: 'none'
        });
        return;
      }
      
      try {
        this.isRunning = true;
        
        const result = await agentTradingService.runBacktest(this.backtestConfig);
        
        if (result.success) {
          this.backtestResults = result.result;
          
          uni.showToast({
            title: '回测完成',
            icon: 'success'
          });
        } else {
          uni.showToast({
            title: result.message || '回测失败',
            icon: 'none'
          });
        }
      } catch (e) {
        console.error('运行回测失败:', e);
        uni.showToast({
          title: '运行回测失败',
          icon: 'none'
        });
      } finally {
        this.isRunning = false;
      }
    },
    
    // 导出回测结果
    async exportResults() {
      if (!this.backtestResults) {
        uni.showToast({
          title: '没有回测结果可导出',
          icon: 'none'
        });
        return;
      }
      
      try {
        const result = await agentTradingService.getBacktestResults('csv');
        
        if (result.success) {
          uni.showToast({
            title: '结果已导出',
            icon: 'success'
          });
          
          // 在实际应用中,这里应该处理文件下载或保存
          console.log('导出结果:', result.data);
        } else {
          uni.showToast({
            title: result.message || '导出失败',
            icon: 'none'
          });
        }
      } catch (e) {
        console.error('导出结果失败:', e);
        uni.showToast({
          title: '导出结果失败',
          icon: 'none'
        });
      }
    },
    
    // 保存风险控制设置
    async saveRiskControlSettings() {
      try {
        const result = await agentTradingService.configureRiskControl(this.riskControlConfig);
        
        if (result.success) {
          uni.showToast({
            title: '风险控制设置已保存',
            icon: 'success'
          });
        } else {
          uni.showToast({
            title: result.message || '保存设置失败',
            icon: 'none'
          });
        }
      } catch (e) {
        console.error('保存风险控制设置失败:', e);
        uni.showToast({
          title: '保存设置失败',
          icon: 'none'
        });
      }
    },
    
    // 辅助方法:获取日期字符串
    getDateString(daysOffset) {
      const date = new Date();
      date.setDate(date.getDate() + daysOffset);
      return date.toISOString().split('T')[0];
    },
    
    // 辅助方法:格式化百分比
    formatPercent(value) {
      if (value == null) return '-';
      return (value * 100).toFixed(2) + '%';
    },
    
    // 辅助方法:格式化日期
    formatDate(dateString) {
      if (!dateString) return '-';
      
      // 如果日期格式已经是YYYY-MM-DD,直接返回
      if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
        return dateString;
      }
      
      try {
        const date = new Date(dateString);
        return date.toISOString().split('T')[0];
      } catch (e) {
        return dateString;
      }
    },
    
    // 辅助方法:获取收益类名
    getReturnClass(value) {
      if (value == null) return '';
      return value > 0 ? 'positive' : value < 0 ? 'negative' : '';
    },
    
    // 辅助方法:获取夏普比率类名
    getSharpeRatioClass(value) {
      if (value == null) return '';
      return value > 1 ? 'positive' : value < 0 ? 'negative' : '';
    },
    
    // 辅助方法:获取风险等级索引
    getRiskLevelIndex() {
      const level = this.backtestConfig.strategy_params.risk_level;
      return level === 'low' ? 0 : level === 'medium' ? 1 : 2;
    },
    
    // 辅助方法:获取交易方向索引
    getTradeDirectionIndex() {
      const direction = this.backtestConfig.strategy_params.trade_direction;
      return direction === 'long_only' ? 0 : direction === 'short_only' ? 1 : 2;
    },
    
    // 辅助方法:获取风险控制级别索引
    getRiskControlLevelIndex() {
      const level = this.riskControlConfig.risk_level;
      return level === 'low' ? 0 : level === 'medium' ? 1 : 2;
    },
    
    // 辅助方法:获取仓位确定方法索引
    getPositionSizingMethodIndex() {
      const method = this.riskControlConfig.position_sizing_method;
      return method === 'fixed' ? 0 : method === 'confidence' ? 1 : 2;
    },
    
    // 事件处理:选择风险等级
    onSelectRiskLevel(e) {
      const index = e.currentIndex;
      this.backtestConfig.strategy_params.risk_level = index === 0 ? 'low' : index === 1 ? 'medium' : 'high';
    },
    
    // 事件处理:选择交易方向
    onSelectTradeDirection(e) {
      const index = e.currentIndex;
      this.backtestConfig.strategy_params.trade_direction = index === 0 ? 'long_only' : index === 1 ? 'short_only' : 'both';
    },
    
    // 事件处理:选择风险控制级别
    onSelectRiskControlLevel(e) {
      const index = e.currentIndex;
      this.riskControlConfig.risk_level = index === 0 ? 'low' : index === 1 ? 'medium' : 'high';
    },
    
    // 事件处理:选择仓位确定方法
    onSelectPositionSizingMethod(e) {
      const index = e.currentIndex;
      this.riskControlConfig.position_sizing_method = index === 0 ? 'fixed' : index === 1 ? 'confidence' : 'kelly';
    },
    
    // 事件处理:持仓比例变化
    onPositionPercentChange(e) {
      this.backtestConfig.strategy_params.max_position_percent = e.detail.value / 100;
    },
    
    // 事件处理:自动执行变化
    onAutoExecuteChange(e) {
      this.backtestConfig.strategy_params.auto_execute = e.target.value;
    },
    
    // 事件处理:最大仓位变化
    onMaxPositionChange(e) {
      this.riskControlConfig.max_position_per_stock = e.detail.value / 100;
    },
    
    // 事件处理:日亏损限制变化
    onDailyLossLimitChange(e) {
      this.riskControlConfig.daily_loss_limit = e.detail.value / 100;
    }
  }
}
</script>

<style scoped>
.backtest-panel {
  background-color: #f8f8f8;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.header-left {
  display: flex;
  align-items: center;
}

.panel-title {
  font-size: 18px;
  font-weight: bold;
  margin-right: 10px;
}

.environment-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  color: white;
}

.environment-badge.live {
  background-color: #19be6b;
}

.environment-badge.backtest {
  background-color: #ff9900;
}

.header-right {
  display: flex;
  align-items: center;
}

.switch-label {
  font-size: 14px;
  margin-left: 5px;
}

.backtest-form {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
}

.form-row {
  display: flex;
  justify-content: space-between;
}

.date-item {
  width: 48%;
}

.strategy-params {
  margin-top: 15px;
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.param-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  display: block;
}

.param-row {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.param-label {
  width: 120px;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.load-data-btn, .run-backtest-btn {
  width: 48%;
}

.backtest-results {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  margin-top: 15px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.results-title {
  font-size: 16px;
  font-weight: bold;
}

.metrics-card {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  padding: 15px;
  background-color: #f8f8f8;
  border-radius: 8px;
  margin-bottom: 15px;
}

.metric-item {
  width: 33%;
  text-align: center;
  margin-bottom: 10px;
}

.metric-value {
  font-size: 18px;
  font-weight: bold;
  display: block;
}

.metric-label {
  font-size: 12px;
  color: #666;
  display: block;
}

.positive {
  color: #f56c6c;
}

.negative {
  color: #19be6b;
}

.trades-table {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  display: flex;
  background-color: #f8f8f8;
  font-weight: bold;
  padding: 10px 0;
}

.header-cell {
  flex: 1;
  text-align: center;
  font-size: 14px;
}

.table-body {
  max-height: 300px;
}

.table-row {
  display: flex;
  border-top: 1px solid #eee;
  padding: 10px 0;
}

.row-cell {
  flex: 1;
  text-align: center;
  font-size: 14px;
}

.date-cell {
  flex: 1.5;
}

.type-cell {
  flex: 0.8;
}

.buy {
  color: #f56c6c;
}

.sell {
  color: #19be6b;
}

.risk-control-panel {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  margin-top: 15px;
}

.half-width {
  width: 48%;
}

.save-settings-btn {
  margin-top: 15px;
}

.live-trading-tips {
  margin-top: 20px;
  background-color: #f8f8f8;
  border-radius: 8px;
  padding: 15px;
}

.tips-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
}

.tip-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.tip-icon {
  margin-right: 10px;
  font-size: 18px;
}

.tip-text {
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}
</style> 
