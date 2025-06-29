<template>
  <view class="agent-trading-panel">
    <!-- AI头像和状态 -->
    <view class="ai-header">
      <view class="ai-avatar">
        <image src="/static/images/ai-avatar.png" mode="aspectFit" />
        <view class="ai-status-indicator" :class="{ active: isRunning }"></view>
      </view>
      <view class="ai-info">
        <text class="ai-name">智能交易助手</text>
        <text class="ai-status">{{ isRunning ? '正在为您执行交易决策' : '交易系统待命中' }}</text>
      </view>
      <view class="ai-controls">
        <button class="ai-toggle-btn" :class="{ active: isRunning }" @click="toggleAISystem">
          {{ isRunning ? '停止AI' : '启动AI' }}
        </button>
      </view>
    </view>
    
    <view class="panel-header">
      <view class="header-top">
        <view class="title-section">
          <text class="panel-title">Agent分析控制台</text>
          <text class="panel-subtitle">基于人工智能的交易决策学习系统</text>
        </view>
        <view class="header-actions">
          <button class="refresh-btn" @click="refreshData" :disabled="isLoading">
            {{ isLoading ? '刷新中...' : '刷新数据' }}
          </button>
        </view>
      </view>
      
      <!-- 数据源延迟显示 -->
      <view class="data-source-delay">
        <view class="delay-item">
          <text class="delay-label">股票实时接口:</text>
          <text class="delay-value" :class="{'normal': stockApiDelay < 500, 'warning': stockApiDelay >= 500 && stockApiDelay < 1000, 'critical': stockApiDelay >= 1000}">
            {{ stockApiDelay }}ms
          </text>
        </view>
        <view class="delay-item">
          <text class="delay-label">网络延迟:</text>
          <text class="delay-value" :class="{'normal': networkDelay < 500, 'warning': networkDelay >= 500 && networkDelay < 1000, 'critical': networkDelay >= 1000}">
            {{ networkDelay }}ms
          </text>
        </view>
      </view>
    </view>
    
    <!-- 状态卡片 -->
    <view class="status-card" :class="isRunning ? 'status-running' : 'status-stopped'">
      <view class="status-header">
        <text class="status-title">系统状态</text>
        <text class="status-indicator">{{ isRunning ? '运行中' : '已停止' }}</text>
      </view>
      
      <!-- 市场追踪数据状态 - 显示后端市场追踪服务仍在工作 -->
      <view class="market-tracking-status">
        <text class="tracking-label">市场追踪数据:</text>
        <text class="tracking-value" :class="{'connected': marketDataConnected}">
          {{ marketDataConnected ? '数据流正常' : '数据连接断开' }}
        </text>
        <text class="tracking-updated">最后更新: {{ lastMarketDataUpdate }}</text>
      </view>
      
      <view class="status-details">
        <view class="status-item">
          <text class="status-label">当前策略</text>
          <text class="status-value">{{ currentStrategies.join('、') || '未选择' }}</text>
        </view>
        <view class="status-item">
          <text class="status-label">运行时间</text>
          <text class="status-value">{{ runningTime }}</text>
        </view>
        <view class="status-item">
          <text class="status-label">交易次数</text>
          <text class="status-value">{{ tradeCount }}</text>
        </view>
        <view class="status-item">
          <text class="status-label">当日盈亏</text>
          <text class="status-value" :class="dailyProfit >= 0 ? 'profit' : 'loss'">
            {{ dailyProfit >= 0 ? '+' : '' }}¥{{ Math.abs(dailyProfit).toFixed(2) }}
          </text>
        </view>
      </view>
      
      <!-- AI可操作资金设置 -->
      <view class="ai-fund-control">
        <view class="fund-control-header">
          <text class="fund-control-title">AI可操作资金</text>
        </view>
        <view class="fund-control-input">
          <input 
            type="number" 
            class="fund-input" 
            :value="aiControlFunds" 
            @input="updateAIFunds"
            placeholder="请输入金额"
          />
          <text class="fund-unit">元</text>
        </view>
        <view class="fund-control-slider">
          <slider 
            :value="fundPercentage" 
            @change="updateFundPercentage" 
            min="0" 
            max="100" 
            show-value
            :disabled="!isConnected"
          />
          <text class="fund-percentage">账户资金的 {{ fundPercentage }}%</text>
        </view>
        
        <!-- 资金使用进度 -->
        <view class="fund-usage">
          <text class="fund-usage-label">资金使用情况:</text>
          <view class="fund-progress-container">
            <view 
              class="fund-progress-bar" 
              :style="{ width: `${calculateFundUsagePercentage()}%` }"
              :class="{'warning': calculateFundUsagePercentage() > 70, 'danger': calculateFundUsagePercentage() > 90}"
            ></view>
          </view>
          <text class="fund-usage-text">{{ calculateUsedFunds().toFixed(2) }}/{{ aiControlFunds }}元 ({{ calculateFundUsagePercentage() }}%)</text>
        </view>
        
        <view class="fund-description">
          <text>设置Agent交易系统可操作的最大资金额度，用于控制风险</text>
        </view>
        
        <!-- 通知设置 -->
        <view class="notification-settings">
          <text class="notification-label">通知栏推送提醒:</text>
          <switch :checked="enableNotifications" @change="toggleNotifications" color="#1989fa" style="transform: scale(0.8);"/>
          <text class="notification-status">{{ enableNotifications ? '已开启' : '已关闭' }}</text>
        </view>
      </view>
      
      <view class="connection-status">
        <text class="connection-label">交易账户:</text>
        <text class="connection-value" :class="{'connected': isConnected}">
          {{ isConnected ? `${brokerName} (已连接)` : '未连接' }}
        </text>
        <button v-if="!isConnected" class="connect-btn" @click="showConnectionDialog">连接账户</button>
      </view>
      
      <!-- T+0 交易控制 -->
      <view class="t0-trading-controls">
        <view class="t0-header">
          <text class="t0-title">T+0交易设置</text>
        </view>
        
        <view class="t0-options">
          <view class="t0-mode-selection">
            <text class="t0-label">交易模式:</text>
            <view class="mode-buttons">
              <view class="mode-button" :class="{ active: tradeTimeMode === 'EOD' }" @click="setTradeTimeMode('EOD')">
                尾盘选股
              </view>
              <view class="mode-button" :class="{ active: tradeTimeMode === 'INTRADAY', disabled: t0Enabled }" @click="setTradeTimeMode('INTRADAY')">
                盘中选股
              </view>
            </view>
          </view>
          
          <view class="t0-toggle">
            <text class="t0-label">交易类型:</text>
            <switch :checked="t0Enabled" @change="toggleT0Mode" color="#1989fa" style="transform: scale(0.8);"/>
            <text class="t0-status">{{ t0Enabled ? 'T+0' : 'T+1' }}</text>
          </view>
        </view>
        
        <view class="t0-info" v-if="tradeTimeMode === 'EOD'">
          <text class="t0-info-text">T+0策略核心是尾盘买入异动或热点股，次日开盘高抛，控制单股仓位在20-30%内</text>
          <view v-if="lastEodUpdateTime" class="last-update">
            <text>最近更新: {{ lastEodUpdateTime }}</text>
            <text class="update-status" :class="isEodTime ? 'eod-time' : 'not-eod-time'">
              {{ isEodTime ? '尾盘时段' : '非尾盘时段' }}
            </text>
          </view>
        </view>
      </view>
      
      <view class="control-buttons">
        <button class="control-btn" :class="isRunning ? 'btn-stop' : 'btn-start'"
                @click="toggleSystem" :disabled="!isConnected">
          {{ isRunning ? '停止系统' : '启动系统' }}
        </button>
        <button class="control-btn btn-settings" @click="showSettings">
          系统设置
        </button>
      </view>
    </view>

    <!-- T+0股票池 -->
    <view class="t0-stocks-pool" v-if="t0Enabled && t0StocksPool.length > 0">
      <view class="card-header">
        <text class="card-title">T+0交易股票池</text>
        <text class="refresh-btn" @click="refreshT0StocksPool">刷新</text>
      </view>

      <view class="pool-description">
        <text>以下股票适合实施T+0策略(尾盘买入，次日早盘卖出，快速获利)</text>
      </view>

      <scroll-view scroll-x class="t0-stocks-table">
        <view class="stocks-table">
          <!-- Table header -->
          <view class="table-header">
            <view class="table-cell">代码</view>
            <view class="table-cell">名称</view>
            <view class="table-cell">现价</view>
            <view class="table-cell">涨跌幅</view>
            <view class="table-cell">量比</view>
            <view class="table-cell">成交模式</view>
            <view class="table-cell">T+0信号</view>
            <view class="table-cell">操作</view>
          </view>

          <!-- Table body -->
          <view class="table-body">
            <view class="table-row" v-for="(stock, index) in t0StocksPool" :key="index">
              <view class="table-cell">{{ stock.symbol }}</view>
              <view class="table-cell">{{ stock.name }}</view>
              <view class="table-cell">{{ stock.price }}</view>
              <view class="table-cell" :class="stock.changePercent >= 0 ? 'positive' : 'negative'">
                {{ stock.changePercent >= 0 ? '+' : '' }}{{ stock.changePercent }}%
              </view>
              <view class="table-cell" :class="getVolumeRatioClass(stock)">
                {{ stock.volumeAnalysis ? stock.volumeAnalysis.volumeRatio.toFixed(2) : '1.00' }}
              </view>
              <view class="table-cell volume-pattern">
                <text class="volume-pattern-tag" :class="getVolumePatternClass(stock)">
                  {{ stock.volumeAnalysis && stock.volumeAnalysis.pattern ? stock.volumeAnalysis.pattern.name : '正常' }}
                </text>
              </view>
              <view class="table-cell">
                <text class="t0-signal">{{ stock.t0Signal || '波动交易' }}</text>
              </view>
              <view class="table-cell actions">
                <button class="action-btn buy" @click="quickTrade(stock, 'BUY')">买入</button>
                <button class="action-btn details" @click="showVolumeDetail(stock)">详情</button>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>

      <view class="pool-note">
        <text>注: T+0股票筛选基于市场热点、技术指标和成交量变化，每日尾盘更新推荐</text>
      </view>
    </view>

    <!-- T+0模式提示框 -->
    <view v-if="showT0Toast" class="t0-toast">
      <view class="t0-toast-content">
        已开启T+0交易模式
      </view>
    </view>

    <!-- AI决策历史 -->
    <view class="decisions-card" v-if="isConnected">
      <view class="card-header">
        <text class="card-title">最近AI决策</text>
        <text class="refresh-btn" @click="refreshDecisions">刷新</text>
      </view>

      <view class="decision-list" v-if="decisions.length > 0">
        <view class="decision-item" v-for="(decision, index) in decisions" :key="index">
          <view class="decision-header">
            <view class="decision-stock">
              <text class="decision-symbol">{{ decision.symbol }}</text>
              <text class="decision-name">{{ decision.name }}</text>
            </view>
            <view class="decision-action" :class="decision.action === 'BUY' || decision.action === 'buy' ? 'buy-action' : 'sell-action'">
              {{ decision.action === 'BUY' || decision.action === 'buy' ? '买入' : decision.action === 'SELL' || decision.action === 'sell' ? '卖出' : '持有' }}
            </view>
          </view>
          <view class="decision-details">
            <view class="decision-detail-item">
              <text class="detail-label">价格</text>
              <text class="detail-value">{{ decision.price }}</text>
            </view>
            <view class="decision-detail-item">
              <text class="detail-label">数量</text>
              <text class="detail-value">{{ decision.volume || decision.suggested_quantity }}股</text>
            </view>
            <view class="decision-detail-item">
              <text class="detail-label">置信度</text>
              <text class="detail-value confidence">{{ ((decision.confidence || 0.5) * 100).toFixed(0) }}%</text>
            </view>
            <view class="decision-detail-item">
              <text class="detail-label">决策源</text>
              <text class="detail-value">{{ decision.source || decision.strategy_id || "AI综合分析" }}</text>
            </view>
          </view>
          <view class="decision-reason">
            <text class="reason-title">决策理由:</text>
            <text class="reason-content">{{ decision.reason || decision.detailedReasons || (decision.reasons ? decision.reasons.join(', ') : '') }}</text>
          </view>
          <view class="decision-actions" v-if="!decision.executed && decision.action !== 'hold'">
            <button class="action-btn execute-btn" @click="executeDecision(decision)">
              执行交易
            </button>
            <button class="action-btn ignore-btn" @click="ignoreDecision(decision)">
              忽略
            </button>
          </view>
          <view class="decision-status" v-else-if="decision.executed">
            <text class="status-text" :class="decision.executionResult?.success ? 'status-success' : 'status-failed'">
              {{ decision.executionResult?.success ? '交易成功' : '交易失败' }}
            </text>
            <text class="status-message" v-if="decision.executionResult?.message">
              {{ decision.executionResult.message }}
            </text>
          </view>
          <view class="decision-status" v-else-if="decision.action === 'hold'">
            <text class="status-text status-hold">建议持有观望</text>
          </view>
        </view>
      </view>

      <view class="empty-decisions" v-else>
        <text class="empty-text">暂无AI决策记录</text>
      </view>
    </view>

    <!-- AI学习进度 -->
    <view class="learning-card">
      <view class="card-header">
        <text class="card-title">AI学习进度</text>
      </view>

      <view class="learning-progress">
        <view class="progress-bar-container">
          <view class="progress-bar" :style="{ width: `${learningProgress}%` }"></view>
        </view>
        <text class="progress-text">已完成 {{ learningProgress }}%</text>
      </view>

      <view class="learning-stats">
        <view class="stat-item">
          <text class="stat-label">训练样本数</text>
          <text class="stat-value">{{ trainingSamples }}</text>
        </view>
        <view class="stat-item">
          <text class="stat-label">学习次数</text>
          <text class="stat-value">{{ learningIterations }}</text>
        </view>
        <view class="stat-item">
          <text class="stat-label">准确率</text>
          <text class="stat-value">{{ (accuracy * 100).toFixed(2) }}%</text>
        </view>
      </view>

      <view class="learning-metrics">
        <view class="metric-item">
          <text class="metric-label">策略回测收益率</text>
          <text class="metric-value" :class="strategyReturns >= 0 ? 'profit' : 'loss'">
            {{ strategyReturns >= 0 ? '+' : '' }}{{ strategyReturns }}%
          </text>
        </view>
        <view class="metric-item">
          <text class="metric-label">胜率</text>
          <text class="metric-value">{{ winRate }}%</text>
        </view>
        <view class="metric-item">
          <text class="metric-label">最大回撤</text>
          <text class="metric-value loss">-{{ maxDrawdown }}%</text>
        </view>
      </view>

      <view class="learning-actions">
        <button class="learning-btn" @click="startManualLearning">
          开始训练
        </button>
        <button class="learning-btn" @click="viewLearningDetails">
          查看详情
        </button>
      </view>
    </view>

    <!-- 回测功能 -->
    <view class="backtest-card">
      <view class="card-header">
        <text class="card-title">策略回测</text>
        <text class="refresh-btn" @click="refreshBacktestResults">刷新</text>
      </view>

      <view class="backtest-config">
        <view class="config-row">
          <text class="config-label">回测周期:</text>
          <picker @change="onBacktestPeriodChange" :value="backtestPeriodIndex" :range="backtestPeriods">
            <view class="picker-value">{{ backtestPeriods[backtestPeriodIndex] }}</view>
          </picker>
        </view>
        <view class="config-row">
          <text class="config-label">初始资金:</text>
          <input type="number" class="config-input" v-model="backtestInitialFunds" placeholder="100000" />
          <text class="config-unit">元</text>
        </view>
      </view>

      <view class="backtest-actions">
        <button class="backtest-btn" @click="runBacktest" :disabled="backtestRunning">
          {{ backtestRunning ? '回测中...' : '开始回测' }}
        </button>
        <button class="backtest-btn secondary" @click="loadBacktestData">
          加载历史数据
        </button>
      </view>

      <view class="backtest-results" v-if="backtestResults">
        <view class="result-item">
          <text class="result-label">总收益率</text>
          <text class="result-value" :class="backtestResults.totalReturn >= 0 ? 'profit' : 'loss'">
            {{ backtestResults.totalReturn >= 0 ? '+' : '' }}{{ backtestResults.totalReturn }}%
          </text>
        </view>
        <view class="result-item">
          <text class="result-label">年化收益率</text>
          <text class="result-value" :class="backtestResults.annualReturn >= 0 ? 'profit' : 'loss'">
            {{ backtestResults.annualReturn >= 0 ? '+' : '' }}{{ backtestResults.annualReturn }}%
          </text>
        </view>
        <view class="result-item">
          <text class="result-label">最大回撤</text>
          <text class="result-value loss">-{{ backtestResults.maxDrawdown }}%</text>
        </view>
        <view class="result-item">
          <text class="result-label">夏普比率</text>
          <text class="result-value">{{ backtestResults.sharpeRatio }}</text>
        </view>
        <view class="result-item">
          <text class="result-label">胜率</text>
          <text class="result-value">{{ backtestResults.winRate }}%</text>
        </view>
        <view class="result-item">
          <text class="result-label">交易次数</text>
          <text class="result-value">{{ backtestResults.tradeCount }}</text>
        </view>
      </view>
    </view>

    <!-- 风险控制 -->
    <view class="risk-control-card">
      <view class="card-header">
        <text class="card-title">风险控制设置</text>
        <text class="refresh-btn" @click="saveRiskConfig">保存</text>
      </view>

      <view class="risk-config">
        <view class="risk-item">
          <text class="risk-label">单笔最大损失:</text>
          <input type="number" class="risk-input" v-model="riskConfig.maxLossPerTrade" placeholder="5" />
          <text class="risk-unit">%</text>
        </view>
        <view class="risk-item">
          <text class="risk-label">日最大损失:</text>
          <input type="number" class="risk-input" v-model="riskConfig.maxDailyLoss" placeholder="10" />
          <text class="risk-unit">%</text>
        </view>
        <view class="risk-item">
          <text class="risk-label">最大持仓比例:</text>
          <input type="number" class="risk-input" v-model="riskConfig.maxPositionRatio" placeholder="30" />
          <text class="risk-unit">%</text>
        </view>
        <view class="risk-item">
          <text class="risk-label">止损价格:</text>
          <input type="number" class="risk-input" v-model="riskConfig.stopLossRatio" placeholder="8" />
          <text class="risk-unit">%</text>
        </view>
        <view class="risk-item">
          <text class="risk-label">止盈价格:</text>
          <input type="number" class="risk-input" v-model="riskConfig.takeProfitRatio" placeholder="15" />
          <text class="risk-unit">%</text>
        </view>
      </view>

      <view class="risk-switches">
        <view class="switch-item">
          <text class="switch-label">启用风险控制:</text>
          <switch :checked="riskConfig.enabled" @change="toggleRiskControl" color="#1989fa" style="transform: scale(0.8);"/>
        </view>
        <view class="switch-item">
          <text class="switch-label">自动止损:</text>
          <switch :checked="riskConfig.autoStopLoss" @change="toggleAutoStopLoss" color="#1989fa" style="transform: scale(0.8);"/>
        </view>
        <view class="switch-item">
          <text class="switch-label">自动止盈:</text>
          <switch :checked="riskConfig.autoTakeProfit" @change="toggleAutoTakeProfit" color="#1989fa" style="transform: scale(0.8);"/>
        </view>
      </view>
    </view>

    <!-- 性能统计 -->
    <view class="performance-card">
      <view class="card-header">
        <text class="card-title">Agent性能统计</text>
        <picker @change="onPerformancePeriodChange" :value="performancePeriodIndex" :range="performancePeriods">
          <view class="picker-value">{{ performancePeriods[performancePeriodIndex] }}</view>
        </picker>
      </view>

      <view class="performance-stats" v-if="performanceStats">
        <view class="stat-row">
          <view class="stat-item">
            <text class="stat-label">决策准确率</text>
            <text class="stat-value">{{ performanceStats.decisionAccuracy }}%</text>
          </view>
          <view class="stat-item">
            <text class="stat-label">执行成功率</text>
            <text class="stat-value">{{ performanceStats.executionSuccess }}%</text>
          </view>
        </view>
        <view class="stat-row">
          <view class="stat-item">
            <text class="stat-label">平均响应时间</text>
            <text class="stat-value">{{ performanceStats.avgResponseTime }}ms</text>
          </view>
          <view class="stat-item">
            <text class="stat-label">系统稳定性</text>
            <text class="stat-value">{{ performanceStats.systemStability }}%</text>
          </view>
        </view>
        <view class="stat-row">
          <view class="stat-item">
            <text class="stat-label">盈利交易比例</text>
            <text class="stat-value profit">{{ performanceStats.profitableTradeRatio }}%</text>
          </view>
          <view class="stat-item">
            <text class="stat-label">平均持仓时间</text>
            <text class="stat-value">{{ performanceStats.avgHoldingTime }}h</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 环境管理 -->
    <view class="environment-card">
      <view class="card-header">
        <text class="card-title">交易环境</text>
        <text class="refresh-btn" @click="refreshEnvironment">刷新</text>
      </view>

      <view class="environment-selector">
        <text class="env-label">当前环境:</text>
        <picker @change="onEnvironmentChange" :value="currentEnvironmentIndex" :range="environments">
          <view class="picker-value" :class="currentEnvironment === 'production' ? 'env-prod' : 'env-test'">
            {{ environments[currentEnvironmentIndex] }}
          </view>
        </picker>
      </view>

      <view class="environment-info">
        <view class="info-item">
          <text class="info-label">API端点:</text>
          <text class="info-value">{{ environmentInfo.apiEndpoint }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">数据源:</text>
          <text class="info-value">{{ environmentInfo.dataSource }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">风险级别:</text>
          <text class="info-value" :class="environmentInfo.riskLevel === 'high' ? 'risk-high' : 'risk-low'">
            {{ environmentInfo.riskLevel === 'high' ? '高风险' : '低风险' }}
          </text>
        </view>
      </view>

      <view class="environment-warning" v-if="currentEnvironment === 'production'">
        <text class="warning-text">⚠️ 生产环境：所有交易将使用真实资金</text>
      </view>
    </view>

    <!-- T+0自动更新配置 -->
    <view class="t0-auto-update-card" v-if="t0Enabled">
      <view class="card-header">
        <text class="card-title">T+0股票池自动更新</text>
        <text class="refresh-btn" @click="saveT0UpdateConfig">保存</text>
      </view>

      <view class="t0-update-config">
        <view class="config-item">
          <text class="config-label">更新频率:</text>
          <picker @change="onT0UpdateFrequencyChange" :value="t0UpdateFrequencyIndex" :range="t0UpdateFrequencies">
            <view class="picker-value">{{ t0UpdateFrequencies[t0UpdateFrequencyIndex] }}</view>
          </picker>
        </view>
        <view class="config-item">
          <text class="config-label">更新时间:</text>
          <picker mode="time" @change="onT0UpdateTimeChange" :value="t0UpdateTime">
            <view class="picker-value">{{ t0UpdateTime }}</view>
          </picker>
        </view>
        <view class="config-item">
          <text class="config-label">最大股票数:</text>
          <input type="number" class="config-input" v-model="t0UpdateConfig.maxStocks" placeholder="20" />
        </view>
      </view>

      <view class="t0-update-controls">
        <view class="switch-item">
          <text class="switch-label">启用自动更新:</text>
          <switch :checked="t0UpdateConfig.autoUpdate" @change="toggleT0AutoUpdate" color="#1989fa" style="transform: scale(0.8);"/>
        </view>
        <button class="t0-update-btn" @click="manualUpdateT0Pool">
          立即更新股票池
        </button>
      </view>

      <view class="t0-update-status" v-if="t0UpdateStatus">
        <text class="status-label">上次更新:</text>
        <text class="status-value">{{ t0UpdateStatus.lastUpdate }}</text>
        <text class="status-label">下次更新:</text>
        <text class="status-value">{{ t0UpdateStatus.nextUpdate }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import agentTradingService from '@/services/agentTradingService.js';
import dataService from '@/services/dataService.js';
import notificationService from '@/services/notificationService.js';
import mobileService from '@/services/mobileService.js';
import pushService from '@/services/pushService.js';
import gestureService from '@/services/gestureService.js';

export default {
  name: 'AgentTradingPanel',
  data() {
    return {
      // 系统状态
      isRunning: false,
      isConnected: false,
      isLoading: false,
      brokerName: '',
      runningTime: '00:00:00',
      tradeCount: 0,
      dailyProfit: 0,
      currentStrategies: [],
      
      // 数据源延迟
      stockApiDelay: 0,     // 股票实时接口延迟(毫秒)
      networkDelay: 0,      // 网络延迟(毫秒)
      delayTimer: null,     // 延迟更新定时器
      
      // AI可操作资金设置
      aiControlFunds: 100000,
      fundPercentage: 50,
      
      // 持仓数据
      currentHoldings: [],
      tradeHistory: [],
      
      // AI决策
      decisions: [],
      
      // AI学习数据
      learningProgress: 68,
      trainingSamples: 2580,
      learningIterations: 42,
      accuracy: 0.857,
      strategyReturns: 12.6,
      winRate: 65,
      maxDrawdown: 8.2,
      
      // 定时器
      timer: null,
      startTime: null,
      
      // WebSocket连接
      wsConnection: null,
      
      // 市场追踪数据状态
      marketDataConnected: true,
      lastMarketDataUpdate: 'N/A',
      
      // T+0 相关属性
      t0Enabled: false,
      tradeTimeMode: 'EOD',
      showT0Toast: false,
      lastEodUpdateTime: null,
      t0StocksPool: [],
      isEodTime: false,
      
      // 通知设置
      enableNotifications: true,
      
      // 成交量详情相关
      currentDetailStock: null,

      // 回测功能
      backtestPeriods: ['1个月', '3个月', '6个月', '1年', '2年'],
      backtestPeriodIndex: 2,
      backtestInitialFunds: 100000,
      backtestRunning: false,
      backtestResults: null,

      // 风险控制
      riskConfig: {
        enabled: true,
        maxLossPerTrade: 5,
        maxDailyLoss: 10,
        maxPositionRatio: 30,
        stopLossRatio: 8,
        takeProfitRatio: 15,
        autoStopLoss: true,
        autoTakeProfit: true
      },

      // 性能统计
      performancePeriods: ['今日', '本周', '本月', '本季度', '本年'],
      performancePeriodIndex: 0,
      performanceStats: {
        decisionAccuracy: 85.6,
        executionSuccess: 98.2,
        avgResponseTime: 245,
        systemStability: 99.1,
        profitableTradeRatio: 67.8,
        avgHoldingTime: 4.2
      },

      // 环境管理
      environments: ['测试环境', '生产环境'],
      currentEnvironmentIndex: 0,
      currentEnvironment: 'test',
      environmentInfo: {
        apiEndpoint: 'http://localhost:8000/api',
        dataSource: '模拟数据源',
        riskLevel: 'low'
      },

      // T+0自动更新
      t0UpdateFrequencies: ['每小时', '每2小时', '每4小时', '每日'],
      t0UpdateFrequencyIndex: 3,
      t0UpdateTime: '14:30',
      t0UpdateConfig: {
        autoUpdate: false,
        maxStocks: 20,
        frequency: 'daily',
        updateTime: '14:30'
      },
      t0UpdateStatus: {
        lastUpdate: '2024-01-15 14:30:00',
        nextUpdate: '2024-01-16 14:30:00'
      },
    };
  },
  created() {
    // 初始化数据
    this.initData();

    // 开始轮询更新
    this.startPolling();

    // 获取市场追踪数据状态
    this.checkMarketDataStatus();

    // 初始化数据源延迟数据并开始更新
    this.simulateDataSourceDelays();
    this.startDelayUpdates();
  },
  beforeDestroy() {
    if (this.timer) {
      clearInterval(this.timer);
    }

    // 关闭WebSocket连接
    if (this.wsConnection) {
      this.wsConnection.close();
    }

    // 清除定时器
    this.stopPolling();

    // 清除延迟更新定时器
    if (this.delayTimer) {
      clearInterval(this.delayTimer);
      this.delayTimer = null;
    }
  },
  onLoad() {
    // 从本地存储加载AI资金设置
    this.loadAIFundsSettings();

    // 从本地存储加载通知设置
    this.loadNotificationSettings();

    // 检查交易系统连接状态
    this.checkConnectionStatus();

    // 初始化其他数据
    this.initTradeData();

    // 加载实时数据
    this.loadRealTimeData();

    // 初始化移动端特性
    this.initMobileFeatures();

    // 检查资金使用情况
    this.$nextTick(() => {
      this.checkFundUsageWarning();
    });
  },

  onShow() {
    // 页面显示时刷新数据
    this.refreshData();
  },
  methods: {
    // 加载实时数据
    async loadRealTimeData(forceRefresh = false) {
      if (this.isLoading) return;

      this.isLoading = true;
      try {
        // 使用数据服务批量获取数据
        const results = await dataService.getBatchData([
          'agent-analysis',
          'account-balance',
          'account-positions'
        ], forceRefresh);

        // 处理结果
        results.forEach(result => {
          if (result.success) {
            switch (result.endpoint) {
              case 'agent-analysis':
                this.processAgentAnalysisData(result.data);
                break;
              case 'account-balance':
                this.processAccountBalanceData(result.data);
                break;
              case 'account-positions':
                this.processAccountPositionsData(result.data);
                break;
            }
          } else {
            console.error(`加载${result.endpoint}数据失败:`, result.error);
          }
        });

        this.updateLastDataTime();

        if (forceRefresh) {
          notificationService.success('数据更新成功');
        }
      } catch (error) {
        console.error('加载实时数据失败:', error);
        notificationService.handleApiError(error, '数据加载');
      } finally {
        this.isLoading = false;
      }
    },

    // 刷新数据
    async refreshData() {
      await this.loadRealTimeData(true); // 强制刷新
    },

    // 处理Agent分析数据
    processAgentAnalysisData(response) {
      if (!response) return;

      // 更新学习进度数据
      if (response.learning_progress) {
        this.accuracy = response.learning_progress.accuracy || this.accuracy;
        this.winRate = response.learning_progress.win_rate * 100 || this.winRate;
        this.maxDrawdown = response.learning_progress.max_drawdown * 100 || this.maxDrawdown;
      }

      // 更新推荐决策
      if (response.recommendations) {
        this.decisions = response.recommendations.slice(0, 5).map(rec => ({
          time: new Date().toLocaleTimeString(),
          action: rec.action,
          stock: rec.name,
          code: rec.symbol,
          confidence: Math.round(rec.confidence * 100),
          reason: rec.reason
        }));
      }
    },

    // 处理账户余额数据
    processAccountBalanceData(response) {
      if (!response || !response.balance_info) return;

      // 更新资金相关数据
      this.aiControlFunds = response.balance_info.available_balance || this.aiControlFunds;
      this.dailyProfit = response.balance_info.daily_profit || this.dailyProfit;
    },

    // 处理持仓数据
    processAccountPositionsData(response) {
      if (!response || !response.positions) return;

      this.currentHoldings = response.positions.slice(0, 10).map(pos => ({
        stock: pos.stock_name,
        code: pos.stock_code,
        quantity: pos.quantity,
        cost: pos.cost_price,
        current: pos.current_price,
        profit: pos.profit_loss,
        profitRate: pos.profit_loss_ratio
      }));
    },

    // 更新最后数据时间
    updateLastDataTime() {
      this.lastMarketDataUpdate = new Date().toLocaleTimeString();
      this.marketDataConnected = true;
    },

    // 初始化移动端特性
    initMobileFeatures() {
      // 设置手势操作
      this.setupGestures();

      // 设置推送通知
      this.setupPushNotifications();

      // 设置屏幕常亮（交易时段）
      if (this.isInTradingHours()) {
        mobileService.keepScreenOn(true);
      }
    },

    // 设置手势操作
    setupGestures() {
      try {
        // 双击刷新数据
        gestureService.on('doubleTap', () => {
          this.refreshData();
          mobileService.vibrate('short'); // 震动反馈
        });

        // 长按显示操作菜单
        gestureService.on('longPress', () => {
          this.showActionMenu();
        });

        // 下滑刷新
        gestureService.on('swipeDown', (data) => {
          if (data.deltaY > 100) {
            this.refreshData();
          }
        });
      } catch (error) {
        console.error('设置手势操作失败:', error);
      }
    },

    // 设置推送通知
    setupPushNotifications() {
      // 检查推送权限
      const pushStatus = pushService.getStatus();
      if (!pushStatus.permissionGranted) {
        // 提示用户开启推送权限
        setTimeout(() => {
          uni.showModal({
            title: '开启推送通知',
            content: '开启推送通知以接收重要的交易提醒和AI决策通知',
            confirmText: '开启',
            success: (res) => {
              if (res.confirm) {
                pushService.requestPermission();
              }
            }
          });
        }, 2000);
      }
    },

    // 显示操作菜单
    async showActionMenu() {
      const result = await notificationService.showActionSheet({
        itemList: ['刷新数据', '复制链接', '分享页面', '设置提醒', '查看帮助']
      });

      if (result.success) {
        switch (result.tapIndex) {
          case 0: // 刷新数据
            this.refreshData();
            break;
          case 1: // 复制链接
            mobileService.copyToClipboard('https://aigupiao.me/pages/ai-analysis/index');
            break;
          case 2: // 分享页面
            this.sharePage();
            break;
          case 3: // 设置提醒
            this.setupAlerts();
            break;
          case 4: // 查看帮助
            this.showHelp();
            break;
        }
      }
    },

    // 分享页面
    sharePage() {
      mobileService.share({
        title: 'Agent智能交易分析',
        summary: '查看我的AI交易分析结果',
        href: 'https://aigupiao.me/pages/ai-analysis/index',
        imageUrl: '/static/app-logo.png'
      });
    },

    // 设置提醒
    setupAlerts() {
      uni.navigateTo({
        url: '/pages/settings/notification'
      });
    },

    // 显示帮助
    showHelp() {
      uni.showModal({
        title: '操作帮助',
        content: '双击屏幕：刷新数据\n长按屏幕：显示操作菜单\n下滑屏幕：刷新数据',
        showCancel: false
      });
    },

    // 检查是否在交易时间
    isInTradingHours() {
      const now = new Date();
      const hour = now.getHours();
      const minute = now.getMinutes();
      const currentTime = hour * 100 + minute;

      // A股交易时间：9:30-11:30, 13:00-15:00
      return (currentTime >= 930 && currentTime <= 1130) ||
             (currentTime >= 1300 && currentTime <= 1500);
    },

    // 初始化数据
    async initData() {
      try {
        // 获取系统状态
        const statusResponse = await agentTradingService.getSystemStatus();
        if (statusResponse && statusResponse.success) {
          const statusData = statusResponse.data;
          this.isRunning = statusData.isRunning;
          this.isConnected = statusData.isConnected;
          this.brokerName = statusData.brokerName || '';
          this.runningTime = statusData.runningTime || '00:00:00';
          this.tradeCount = statusData.tradeCount || 0;
          this.dailyProfit = statusData.dailyProfit || 0;
          this.currentStrategies = statusData.currentStrategies || [];

          // 设置 T+0 相关属性
          this.t0Enabled = statusData.t0Enabled || false;
          this.tradeTimeMode = statusData.tradeTimeMode || 'EOD';
          this.lastEodUpdateTime = statusData.lastEodUpdateTime || null;
          this.t0StocksPool = statusData.t0StocksPool || [];
        }

        // 获取AI决策
        await this.refreshDecisions();

        // 检查是否是尾盘时间
        this.checkEodTime();

        // 设置定时检查尾盘时间
        this.eodCheckTimer = setInterval(() => {
          this.checkEodTime();
        }, 60000); // 每分钟检查一次

        // 加载高级功能配置
        await this.loadAdvancedConfigs();

      } catch (error) {
        console.error('初始化Agent交易面板数据失败:', error);
        uni.showToast({
          title: '加载数据失败',
          icon: 'none'
        });
      }
    },

    // 加载高级功能配置
    async loadAdvancedConfigs() {
      try {
        // 并行加载各种配置
        await Promise.all([
          this.refreshBacktestResults(),
          this.refreshPerformanceStats(),
          this.refreshEnvironment(),
          this.loadT0UpdateConfig()
        ]);
      } catch (error) {
        console.error('加载高级功能配置失败:', error);
      }
    },

    // 开始轮询更新数据
    startPolling() {
      this.pollingTimer = setInterval(() => {
        this.refreshData();
      }, 30000); // 每30秒更新一次
    },

    // 停止轮询
    stopPolling() {
      if (this.pollingTimer) {
        clearInterval(this.pollingTimer);
        this.pollingTimer = null;
      }

      if (this.eodCheckTimer) {
        clearInterval(this.eodCheckTimer);
        this.eodCheckTimer = null;
      }
    },

    // 刷新数据
    async refreshData() {
      try {
        // 获取系统状态
        const statusResponse = await agentTradingService.getSystemStatus();
        if (statusResponse && statusResponse.success) {
          const statusData = statusResponse.data;
          this.isRunning = statusData.isRunning;
          this.isConnected = statusData.isConnected;
          this.runningTime = statusData.runningTime || '00:00:00';
          this.tradeCount = statusData.tradeCount || 0;
          this.dailyProfit = statusData.dailyProfit || 0;

          // 设置 T+0 相关属性
          this.t0Enabled = statusData.t0Enabled || false;
          this.tradeTimeMode = statusData.tradeTimeMode || 'EOD';
          this.lastEodUpdateTime = statusData.lastEodUpdateTime || null;
          this.t0StocksPool = statusData.t0StocksPool || [];
        }

        // 获取最新设置
        const settingsResponse = await agentTradingService.getSettings();
        if (settingsResponse && settingsResponse.success && settingsResponse.data) {
          const settings = settingsResponse.data;
          // 更新当前策略
          this.currentStrategies = [this.getStrategyName(settings.strategy_id)];
        }

        // 检查市场追踪数据状态
        this.checkMarketDataStatus();

        // 检查是否是尾盘时间
        this.checkEodTime();

      } catch (error) {
        console.error('刷新Agent交易数据失败:', error);
      }
    },

    // 检查市场追踪数据状态 - 添加重试机制
    async checkMarketDataStatus() {
      // 最大重试次数
      const maxRetries = 2;
      let retryCount = 0;
      let success = false;

      while (!success && retryCount <= maxRetries) {
        try {
          // 尝试获取数据，增加retry_count参数供后端记录
          const response = await agentTradingService.checkMarketDataStatus(retryCount);

          if (response && response.success) {
            this.marketDataConnected = response.data.connected;
            this.lastMarketDataUpdate = response.data.lastUpdate || new Date().toLocaleTimeString();

            // 检查并存储是否使用模拟数据
            this.isUsingSimulatedData = response.data.isSimulated;

            // 如果返回了数据源延迟信息，更新延迟值
            if (response.data.dataSourceDelays) {
              this.updateDataSourceDelays(response.data.dataSourceDelays);
              success = true;
            } else {
              // 如果API不返回延迟信息，使用模拟值
              this.simulateDataSourceDelays();
              success = true;
            }
          } else {
            // 增加重试次数
            retryCount++;
            // 简单的退避策略：每次重试等待时间增加
            if (retryCount <= maxRetries) {
              await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
            } else {
              this.marketDataConnected = false;
              this.simulateDataSourceDelays();
            }
          }
        } catch (error) {
          console.error(`检查市场追踪数据状态失败(尝试${retryCount}): ${error}`);
          retryCount++;

          // 简单的退避策略：每次重试等待时间增加
          if (retryCount <= maxRetries) {
            await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
          } else {
            this.marketDataConnected = false;
            // 出错时使用模拟值
            this.simulateDataSourceDelays();
          }
        }
      }
    },

    // 生成模拟的数据源延迟
    simulateDataSourceDelays() {
      // 生成随机延迟值
      this.stockApiDelay = Math.floor(Math.random() * 800) + 100; // 100-900ms
      this.networkDelay = Math.floor(Math.random() * 600) + 200; // 200-800ms
    },

    // 更新数据源延迟
    updateDataSourceDelays(delays) {
      if (delays) {
        // 更新股票实时接口延迟
        if (delays.stockApi !== undefined) {
          this.stockApiDelay = delays.stockApi;
        }

        // 更新网络延迟
        if (delays.network !== undefined) {
          this.networkDelay = delays.network;
        }
      }
    },

    // 启动延迟更新
    startDelayUpdates() {
      // 清除现有定时器
      if (this.delayTimer) {
        clearInterval(this.delayTimer);
      }

      // 设置更合理的轮询间隔：15秒而不是5秒
      // 可以减轻服务器负载并保持UI响应性
      this.delayTimer = setInterval(() => {
        // 调用API获取最新延迟
        this.checkMarketDataStatus();
      }, 15000);
    },

    toggleAISystem() {
      this.isRunning = !this.isRunning;
      uni.showToast({
        title: this.isRunning ? 'AI系统已启动' : 'AI系统已停止',
        icon: 'success'
      });
    },
    updateAIFunds(e) {
      this.aiControlFunds = parseInt(e.detail.value) || 0;
    },
    updateFundPercentage(e) {
      this.fundPercentage = e.detail.value;
    },
    calculateFundUsagePercentage() {
      return Math.min(100, (this.calculateUsedFunds() / this.aiControlFunds) * 100);
    },
    calculateUsedFunds() {
      return this.currentHoldings.reduce((total, holding) => total + (holding.price * holding.volume), 0);
    },
    toggleNotifications(e) {
      this.enableNotifications = e.detail.value;
    },
    showConnectionDialog() {
      uni.navigateTo({
        url: '/pages/trade/index'
      });
    },
    setTradeTimeMode(mode) {
      this.tradeTimeMode = mode;
    },
    toggleT0Mode(e) {
      this.t0Enabled = e.detail.value;
    },
    toggleSystem() {
      this.toggleAISystem();
    },
    showSettings() {
      uni.showToast({
        title: '设置功能开发中',
        icon: 'none'
      });
    },

    // 获取策略名称
    getStrategyName(strategyId) {
      const strategyNames = {
        'momentum': '动量策略',
        'mean_reversion': '均值回归',
        'trend_following': '趋势跟踪',
        'pattern_recognition': '形态识别',
        'dual_thrust': '双重突破',
        'volatility_breakout': '波动率突破'
      };

      return strategyNames[strategyId] || strategyId;
    },

    // 检查是否是尾盘时间
    checkEodTime() {
      const now = new Date();
      const hour = now.getHours();
      const minute = now.getMinutes();

      // 判断是否是交易日的14:30以后
      this.isEodTime = (hour > 14 || (hour === 14 && minute >= 30)) && hour < 15;
    },

    // 刷新AI决策列表
    async refreshDecisions() {
      try {
        uni.showLoading({
          title: '正在刷新...'
        });

        // 获取交易历史
        const result = await agentTradingService.getTradeHistory();

        if (result.success && result.data && result.data.trades) {
          // 将交易历史转换为决策列表
          const decisions = result.data.trades.map(trade => ({
            symbol: trade.symbol,
            name: trade.name || this.getStockName(trade.symbol),
            action: trade.action,
            price: trade.price,
            volume: trade.volume,
            reason: trade.reason || '未提供决策理由',
            confidence: trade.confidence || 0.75,
            strategy_id: trade.strategy_id,
            timestamp: trade.timestamp,
            executed: true,
            executionResult: trade.execution_result
          }));

          this.decisions = decisions;

          // 获取最新的实时AI统一决策，如果有活跃的股票
          await this.getLatestUnifiedDecision();

          uni.hideLoading();
          uni.showToast({
            title: '决策已更新',
            icon: 'success'
          });
        } else {
          uni.hideLoading();
          // 如果没有交易历史，仍尝试获取最新的统一决策
          await this.getLatestUnifiedDecision();

          if (this.decisions.length > 0) {
            uni.showToast({
              title: '已获取最新AI决策',
              icon: 'success'
            });
          } else {
            uni.showToast({
              title: '没有新的交易决策',
              icon: 'none'
            });
          }
        }
      } catch (error) {
        uni.hideLoading();
        console.error('刷新决策列表失败:', error);
        uni.showToast({
          title: '刷新失败，请重试',
          icon: 'none'
        });
      }
    },

    // 获取最新的统一AI决策
    async getLatestUnifiedDecision() {
      try {
        // 检查是否有活跃的股票信息
        const activeStock = uni.getStorageSync('active_stock');
        if (!activeStock) return;

        const stockInfo = JSON.parse(activeStock);
        if (!stockInfo || !stockInfo.code) return;

        // 获取历史数据（实际项目中应从缓存或API获取）
        const historicalData = null; // 如果有历史数据可以传入

        // 获取统一AI决策
        const result = await agentTradingService.getUnifiedAIDecision(stockInfo, historicalData);

        if (result && result.success && result.data) {
          const aiDecision = result.data;

          // 创建新的决策对象
          const newDecision = {
            symbol: stockInfo.code,
            name: stockInfo.name,
            action: aiDecision.action,
            price: aiDecision.price || stockInfo.currentPrice,
            suggested_quantity: aiDecision.suggested_quantity || 0,
            reasons: aiDecision.reasons || [],
            confidence: aiDecision.confidence || 0.5,
            source: 'unified_ai_model',
            timestamp: new Date().toISOString(),
            executed: false,
            risk_reward: aiDecision.risk_reward
          };

          // 添加到决策列表顶部
          if (aiDecision.action !== 'hold' || this.isRunning) {
            this.decisions.unshift(newDecision);

            // 如果决策列表太长，删除较旧的项
            if (this.decisions.length > 10) {
              this.decisions = this.decisions.slice(0, 10);
            }
          }
        }
      } catch (error) {
        console.error('获取统一AI决策失败:', error);
      }
    },

    // 执行交易决策
    async executeDecision(decision) {
      if (!this.isConnected) {
        uni.showToast({
          title: '请先连接交易账户',
          icon: 'none'
        });
        return;
      }

      // 显示确认对话框
      uni.showModal({
        title: 'Agent交易建议',
        content: `AI建议${decision.action === 'BUY' ? '买入' : '卖出'} ${decision.name}${decision.volume}股，价格${decision.price}元。确认执行此交易吗？`,
        confirmText: '执行交易',
        confirmColor: '#007aff',
        success: async (res) => {
          if (res.confirm) {
            try {
              uni.showLoading({
                title: '执行交易中...'
              });

              const result = await agentTradingService.executeTradeDecision(decision, true);

              uni.hideLoading();

              if (result.success) {
                // 更新决策状态
                const index = this.decisions.findIndex(d =>
                  d.symbol === decision.symbol &&
                  d.timestamp === decision.timestamp
                );

                if (index >= 0) {
                  this.decisions[index].executed = true;
                  this.decisions[index].executionResult = {
                    success: true,
                    message: result.message || '委托已提交'
                  };

                  // 更新交易计数
                  this.tradeCount++;

                  uni.showToast({
                    title: 'Agent交易已执行',
                    icon: 'success'
                  });
                }
              } else {
                uni.showToast({
                  title: result.message || '执行失败',
                  icon: 'none'
                });
              }
            } catch (error) {
              uni.hideLoading();
              console.error('执行交易决策失败:', error);
              uni.showToast({
                title: '执行失败，请重试',
                icon: 'none'
              });
            }
          }
        }
      });
    },

    // 忽略交易决策
    ignoreDecision(decision) {
      const index = this.decisions.findIndex(d =>
        d.symbol === decision.symbol &&
        d.timestamp === decision.timestamp
      );

      if (index >= 0) {
        this.decisions.splice(index, 1);
      }

      uni.showToast({
        title: '已忽略该决策',
        icon: 'success'
      });
    },

    // 刷新T+0股票池
    async refreshT0StocksPool() {
      try {
        uni.showLoading({
          title: '正在刷新T+0股票池...'
        });

        // 改用增强版T+0股票池API，包含成交量分析
        const result = await agentTradingService.getEnhancedT0StocksPool();

        uni.hideLoading();

        if (result.success && result.data && result.data.stocks) {
          this.t0StocksPool = result.data.stocks;
          uni.showToast({
            title: 'T+0股票池已更新',
            icon: 'success'
          });
        } else {
          uni.showToast({
            title: '没有新的T+0股票池',
            icon: 'none'
          });
        }
      } catch (error) {
        uni.hideLoading();
        console.error('刷新T+0股票池失败:', error);
        uni.showToast({
          title: '刷新失败，请重试',
          icon: 'none'
        });
      }
    },

    // 快速交易
    async quickTrade(stock, action) {
      if (!this.isConnected) {
        uni.showToast({
          title: '请先连接交易账户',
          icon: 'none'
        });
        return;
      }

      try {
        uni.showLoading({
          title: '执行快速交易...'
        });

        const result = await agentTradingService.executeQuickTrade(stock, action);

        uni.hideLoading();

        if (result.success) {
          uni.showToast({
            title: '交易已执行',
            icon: 'success'
          });
        } else {
          uni.showToast({
            title: result.message || '交易失败',
            icon: 'none'
          });
        }
      } catch (error) {
        uni.hideLoading();
        console.error('快速交易失败:', error);
        uni.showToast({
          title: '交易失败，请重试',
          icon: 'none'
        });
      }
    },

    // 显示成交量详情
    showVolumeDetail(stock) {
      this.currentDetailStock = stock;
      // 这里可以显示详情弹窗或跳转到详情页面
      uni.showToast({
        title: '成交量详情功能开发中',
        icon: 'none'
      });
    },

    // 开始手动学习
    async startManualLearning() {
      try {
        uni.showLoading({
          title: '开始AI训练...'
        });

        const result = await agentTradingService.startModelTraining();

        uni.hideLoading();

        if (result.success) {
          // 模拟训练进度增加
          this.learningProgress = Math.min(100, this.learningProgress + 5);
          this.learningIterations += 1;
          this.accuracy = Math.min(0.95, this.accuracy + 0.01);

          uni.showToast({
            title: result.message || 'AI训练已启动',
            icon: 'success'
          });
        } else {
          uni.showToast({
            title: result.message || '训练启动失败',
            icon: 'none'
          });
        }
      } catch (error) {
        uni.hideLoading();
        console.error('启动AI训练失败:', error);
        uni.showToast({
          title: '训练启动失败，请重试',
          icon: 'none'
        });
      }
    },

    // 查看学习详情
    viewLearningDetails() {
      // 将学习数据存储到全局状态，避免URL过长
      const learningData = {
        progress: this.learningProgress,
        samples: this.trainingSamples,
        iterations: this.learningIterations,
        accuracy: this.accuracy,
        returns: this.strategyReturns,
        winRate: this.winRate,
        drawdown: this.maxDrawdown
      };

      // 存储到全局状态
      getApp().globalData.learningData = learningData;

      // 简化URL参数
      uni.navigateTo({
        url: `/pages/ai-training/index?from=analysis`,
        success: () => {
          console.log('跳转到AI学习详情页面成功');
        },
        fail: (err) => {
          console.error('跳转到AI学习详情页面失败:', err);
          uni.showToast({
            title: '跳转失败，请重试',
            icon: 'none'
          });
        }
      });
    },

    // 获取成交量比率样式类
    getVolumeRatioClass(stock) {
      if (!stock.volumeAnalysis) return '';
      const ratio = stock.volumeAnalysis.volumeRatio;
      if (ratio > 2) return 'high-volume';
      if (ratio > 1.5) return 'medium-volume';
      return 'normal-volume';
    },

    // 获取成交量模式样式类
    getVolumePatternClass(stock) {
      if (!stock.volumeAnalysis || !stock.volumeAnalysis.pattern) return '';
      const pattern = stock.volumeAnalysis.pattern.type;
      if (pattern === 'bullish') return 'bullish-pattern';
      if (pattern === 'bearish') return 'bearish-pattern';
      return 'neutral-pattern';
    },

    // 获取股票名称
    getStockName(symbol) {
      const stockNames = {
        '600519': '贵州茅台',
        '000858': '五粮液',
        '601318': '中国平安',
        '600036': '招商银行'
      };

      return stockNames[symbol] || '未知股票';
    },

    // ========== 回测功能 ==========

    // 回测周期变化
    onBacktestPeriodChange(e) {
      this.backtestPeriodIndex = e.detail.value;
    },

    // 运行回测
    async runBacktest() {
      if (this.backtestRunning) return;

      try {
        this.backtestRunning = true;
        uni.showLoading({
          title: '正在运行回测...'
        });

        const period = this.backtestPeriods[this.backtestPeriodIndex];
        const result = await agentTradingService.runBacktest({
          period: period,
          initialFunds: this.backtestInitialFunds,
          strategies: this.currentStrategies
        });

        if (result.success && result.data) {
          this.backtestResults = result.data;
          uni.showToast({
            title: '回测完成',
            icon: 'success'
          });
        } else {
          uni.showToast({
            title: '回测失败',
            icon: 'none'
          });
        }
      } catch (error) {
        console.error('运行回测失败:', error);
        uni.showToast({
          title: '回测失败，请重试',
          icon: 'none'
        });
      } finally {
        this.backtestRunning = false;
        uni.hideLoading();
      }
    },

    // 加载回测数据
    async loadBacktestData() {
      try {
        uni.showLoading({
          title: '加载历史数据...'
        });

        const result = await agentTradingService.loadBacktestData({
          period: this.backtestPeriods[this.backtestPeriodIndex]
        });

        uni.hideLoading();

        if (result.success) {
          uni.showToast({
            title: '历史数据加载完成',
            icon: 'success'
          });
        } else {
          uni.showToast({
            title: '数据加载失败',
            icon: 'none'
          });
        }
      } catch (error) {
        uni.hideLoading();
        console.error('加载回测数据失败:', error);
        uni.showToast({
          title: '数据加载失败',
          icon: 'none'
        });
      }
    },

    // 刷新回测结果
    async refreshBacktestResults() {
      try {
        const result = await agentTradingService.getBacktestResults();
        if (result.success && result.data) {
          this.backtestResults = result.data;
        }
      } catch (error) {
        console.error('刷新回测结果失败:', error);
      }
    },

    // ========== 风险控制 ==========

    // 切换风险控制
    toggleRiskControl(e) {
      this.riskConfig.enabled = e.detail.value;
    },

    // 切换自动止损
    toggleAutoStopLoss(e) {
      this.riskConfig.autoStopLoss = e.detail.value;
    },

    // 切换自动止盈
    toggleAutoTakeProfit(e) {
      this.riskConfig.autoTakeProfit = e.detail.value;
    },

    // 保存风险配置
    async saveRiskConfig() {
      try {
        uni.showLoading({
          title: '保存配置中...'
        });

        const result = await agentTradingService.configureRiskControl(this.riskConfig);

        uni.hideLoading();

        if (result.success) {
          uni.showToast({
            title: '风险配置已保存',
            icon: 'success'
          });
        } else {
          uni.showToast({
            title: '保存失败',
            icon: 'none'
          });
        }
      } catch (error) {
        uni.hideLoading();
        console.error('保存风险配置失败:', error);
        uni.showToast({
          title: '保存失败，请重试',
          icon: 'none'
        });
      }
    },

    // ========== 性能统计 ==========

    // 性能统计周期变化
    onPerformancePeriodChange(e) {
      this.performancePeriodIndex = e.detail.value;
      this.refreshPerformanceStats();
    },

    // 刷新性能统计
    async refreshPerformanceStats() {
      try {
        const timeRange = ['1d', '1w', '1m', '3m', '1y'][this.performancePeriodIndex];
        const result = await agentTradingService.getPerformanceStats(timeRange);

        if (result.success && result.data) {
          this.performanceStats = result.data;
        }
      } catch (error) {
        console.error('刷新性能统计失败:', error);
      }
    },

    // ========== 环境管理 ==========

    // 环境变化
    async onEnvironmentChange(e) {
      const newIndex = e.detail.value;
      const newEnvironment = newIndex === 0 ? 'test' : 'production';

      // 显示确认对话框
      if (newEnvironment === 'production') {
        uni.showModal({
          title: '切换到生产环境',
          content: '切换到生产环境将使用真实资金进行交易，确认继续吗？',
          confirmText: '确认切换',
          confirmColor: '#ff4757',
          success: async (res) => {
            if (res.confirm) {
              await this.switchEnvironment(newIndex, newEnvironment);
            }
          }
        });
      } else {
        await this.switchEnvironment(newIndex, newEnvironment);
      }
    },

    // 切换环境
    async switchEnvironment(index, environment) {
      try {
        uni.showLoading({
          title: '切换环境中...'
        });

        const result = await agentTradingService.setTradingEnvironment(environment);

        if (result.success) {
          this.currentEnvironmentIndex = index;
          this.currentEnvironment = environment;

          // 更新环境信息
          if (environment === 'production') {
            this.environmentInfo = {
              apiEndpoint: 'https://aigupiao.me/api',
              dataSource: '实时股票数据源',
              riskLevel: 'high'
            };
          } else {
            this.environmentInfo = {
              apiEndpoint: 'http://localhost:8000/api',
              dataSource: '模拟数据源',
              riskLevel: 'low'
            };
          }

          uni.showToast({
            title: `已切换到${environment === 'production' ? '生产' : '测试'}环境`,
            icon: 'success'
          });
        } else {
          uni.showToast({
            title: '环境切换失败',
            icon: 'none'
          });
        }
      } catch (error) {
        console.error('切换环境失败:', error);
        uni.showToast({
          title: '环境切换失败',
          icon: 'none'
        });
      } finally {
        uni.hideLoading();
      }
    },

    // 刷新环境信息
    async refreshEnvironment() {
      try {
        const result = await agentTradingService.getCurrentEnvironment();
        if (result.success && result.data) {
          this.currentEnvironment = result.data.environment;
          this.currentEnvironmentIndex = result.data.environment === 'production' ? 1 : 0;
          this.environmentInfo = result.data.info;
        }
      } catch (error) {
        console.error('刷新环境信息失败:', error);
      }
    },

    // ========== T+0自动更新 ==========

    // T+0更新频率变化
    onT0UpdateFrequencyChange(e) {
      this.t0UpdateFrequencyIndex = e.detail.value;
      const frequencies = ['hourly', '2hourly', '4hourly', 'daily'];
      this.t0UpdateConfig.frequency = frequencies[e.detail.value];
    },

    // T+0更新时间变化
    onT0UpdateTimeChange(e) {
      this.t0UpdateTime = e.detail.value;
      this.t0UpdateConfig.updateTime = e.detail.value;
    },

    // 切换T+0自动更新
    async toggleT0AutoUpdate(e) {
      this.t0UpdateConfig.autoUpdate = e.detail.value;

      try {
        if (e.detail.value) {
          // 启动自动更新
          const result = await agentTradingService.startT0PoolAutoUpdate(this.t0UpdateConfig);
          if (result.success) {
            uni.showToast({
              title: 'T+0自动更新已启动',
              icon: 'success'
            });
          } else {
            this.t0UpdateConfig.autoUpdate = false;
            uni.showToast({
              title: '启动失败',
              icon: 'none'
            });
          }
        } else {
          // 停止自动更新
          const result = await agentTradingService.stopT0PoolAutoUpdate();
          if (result.success) {
            uni.showToast({
              title: 'T+0自动更新已停止',
              icon: 'success'
            });
          } else {
            this.t0UpdateConfig.autoUpdate = true;
            uni.showToast({
              title: '停止失败',
              icon: 'none'
            });
          }
        }
      } catch (error) {
        console.error('切换T+0自动更新失败:', error);
        this.t0UpdateConfig.autoUpdate = !e.detail.value;
        uni.showToast({
          title: '操作失败',
          icon: 'none'
        });
      }
    },

    // 保存T+0更新配置
    async saveT0UpdateConfig() {
      try {
        uni.showLoading({
          title: '保存配置中...'
        });

        const result = await agentTradingService.configureT0PoolUpdate(this.t0UpdateConfig);

        uni.hideLoading();

        if (result.success) {
          uni.showToast({
            title: 'T+0配置已保存',
            icon: 'success'
          });
        } else {
          uni.showToast({
            title: '保存失败',
            icon: 'none'
          });
        }
      } catch (error) {
        uni.hideLoading();
        console.error('保存T+0配置失败:', error);
        uni.showToast({
          title: '保存失败，请重试',
          icon: 'none'
        });
      }
    },

    // 手动更新T+0股票池
    async manualUpdateT0Pool() {
      try {
        uni.showLoading({
          title: '更新股票池中...'
        });

        const result = await agentTradingService.updateT0StocksPool();

        uni.hideLoading();

        if (result.success) {
          // 更新股票池数据
          if (result.data && result.data.stocks) {
            this.t0StocksPool = result.data.stocks;
          }

          // 更新状态信息
          this.t0UpdateStatus.lastUpdate = new Date().toLocaleString();

          uni.showToast({
            title: 'T+0股票池已更新',
            icon: 'success'
          });
        } else {
          uni.showToast({
            title: '更新失败',
            icon: 'none'
          });
        }
      } catch (error) {
        uni.hideLoading();
        console.error('手动更新T+0股票池失败:', error);
        uni.showToast({
          title: '更新失败，请重试',
          icon: 'none'
        });
      }
    },

    // 获取T+0更新配置
    async loadT0UpdateConfig() {
      try {
        const result = await agentTradingService.getT0PoolUpdateConfig();
        if (result.success && result.data) {
          this.t0UpdateConfig = result.data.config;
          this.t0UpdateStatus = result.data.status;

          // 更新UI状态
          const frequencies = ['hourly', '2hourly', '4hourly', 'daily'];
          this.t0UpdateFrequencyIndex = frequencies.indexOf(this.t0UpdateConfig.frequency);
          this.t0UpdateTime = this.t0UpdateConfig.updateTime;
        }
      } catch (error) {
        console.error('加载T+0更新配置失败:', error);
      }
    },

    // ========== 高级决策功能 ==========

    // 请求AI决策
    async requestDecision(context = {}) {
      try {
        const result = await agentTradingService.requestDecision(context);
        if (result.success && result.data) {
          return result.data;
        }
        return null;
      } catch (error) {
        console.error('请求AI决策失败:', error);
        return null;
      }
    },

    // 提供反馈
    async provideFeedback(decisionId, feedback) {
      try {
        const result = await agentTradingService.provideFeedback(decisionId, feedback);
        if (result.success) {
          uni.showToast({
            title: '反馈已提交',
            icon: 'success'
          });
        }
      } catch (error) {
        console.error('提供反馈失败:', error);
        uni.showToast({
          title: '反馈提交失败',
          icon: 'none'
        });
      }
    },

    // 加载AI资金设置
    loadAIFundsSettings() {
      const savedFunds = uni.getStorageSync('ai_control_funds');
      if (savedFunds) {
        this.aiControlFunds = parseInt(savedFunds);
      }
    },

    // 加载通知设置
    loadNotificationSettings() {
      const savedNotifications = uni.getStorageSync('enable_notifications');
      if (savedNotifications !== null) {
        this.enableNotifications = savedNotifications;
      }
    },

    // 检查连接状态
    checkConnectionStatus() {
      // 模拟连接状态
      this.isConnected = true;
      this.brokerName = '模拟交易';
    },

    // 初始化交易数据
    initTradeData() {
      // 模拟初始化
      this.tradeCount = 12;
      this.dailyProfit = 307.00;
      this.currentStrategies = ['趋势跟踪', '量价分析'];
      this.runningTime = '03:45:21';
      this.lastMarketDataUpdate = '16:56:15 GMT+0800 (CST)';
    },

    // 检查资金使用警告
    checkFundUsageWarning() {
      // 模拟检查
    }
  }
}
</script>

<style scoped>
.agent-trading-panel {
  background-color: #141414;
  min-height: 100vh;
  padding: 20rpx;
}

/* AI头像和状态 */
.ai-header {
  display: flex;
  align-items: center;
  padding: 30rpx;
  background: linear-gradient(135deg, #1e3a5f, #2c5aa0);
  border-radius: 16rpx;
  margin-bottom: 30rpx;
}

.ai-avatar {
  position: relative;
  width: 80rpx;
  height: 80rpx;
  margin-right: 20rpx;
}

.ai-avatar image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.ai-status-indicator {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 20rpx;
  height: 20rpx;
  background-color: #666;
  border-radius: 50%;
  border: 3rpx solid #fff;
}

.ai-status-indicator.active {
  background-color: #4caf50;
}

.ai-info {
  flex: 1;
}

.ai-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #ffffff;
  display: block;
  margin-bottom: 8rpx;
}

.ai-status {
  font-size: 26rpx;
  color: #cccccc;
}

.ai-controls {
  margin-left: 20rpx;
}

.ai-toggle-btn {
  background-color: #4c8dff;
  color: #ffffff;
  border: none;
  border-radius: 24rpx;
  padding: 16rpx 32rpx;
  font-size: 26rpx;
}

.ai-toggle-btn.active {
  background-color: #ff4757;
}

/* 面板头部 */
.panel-header {
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30rpx;
}

.title-section {
  flex: 1;
  text-align: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.refresh-btn {
  background-color: #1989fa;
  color: white;
  border: none;
  border-radius: 20rpx;
  padding: 12rpx 24rpx;
  font-size: 24rpx;
  min-width: 120rpx;
}

.refresh-btn:disabled {
  background-color: #cccccc;
  color: #666666;
}

.panel-title {
  font-size: 40rpx;
  font-weight: bold;
  color: #ffffff;
  display: block;
  margin-bottom: 12rpx;
}

.panel-subtitle {
  font-size: 26rpx;
  color: #999999;
  display: block;
  margin-bottom: 30rpx;
}

/* 数据源延迟 */
.data-source-delay {
  display: flex;
  justify-content: center;
  gap: 40rpx;
}

.delay-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.delay-label {
  font-size: 24rpx;
  color: #cccccc;
}

.delay-value {
  font-size: 24rpx;
  font-weight: bold;
}

.delay-value.normal {
  color: #4caf50;
}

.delay-value.warning {
  color: #ff9800;
}

.delay-value.critical {
  color: #f44336;
}

/* 状态卡片 */
.status-card {
  background: linear-gradient(135deg, #1e3a5f, #2c5aa0);
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.status-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #ffffff;
}

.status-indicator {
  background-color: #4caf50;
  color: #ffffff;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
}

/* 市场追踪状态 */
.market-tracking-status {
  margin-bottom: 30rpx;
}

.tracking-label {
  font-size: 26rpx;
  color: #cccccc;
  margin-right: 16rpx;
}

.tracking-value {
  font-size: 26rpx;
  color: #ffffff;
}

.tracking-value.connected {
  color: #4caf50;
}

.tracking-updated {
  font-size: 22rpx;
  color: #999999;
  display: block;
  margin-top: 8rpx;
}

/* 状态详情 */
.status-details {
  margin-bottom: 30rpx;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid rgba(255, 255, 255, 0.1);
}

.status-item:last-child {
  border-bottom: none;
}

.status-label {
  font-size: 26rpx;
  color: #cccccc;
}

.status-value {
  font-size: 26rpx;
  color: #ffffff;
}

.status-value.profit {
  color: #4caf50;
  font-weight: bold;
}

.status-value.loss {
  color: #f44336;
  font-weight: bold;
}

/* AI可操作资金 */
.ai-fund-control {
  margin-bottom: 30rpx;
}

.fund-control-header {
  margin-bottom: 20rpx;
}

.fund-control-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #ffffff;
}

.fund-control-input {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.fund-input {
  flex: 1;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1rpx solid rgba(255, 255, 255, 0.2);
  border-radius: 8rpx;
  padding: 16rpx;
  color: #ffffff;
  font-size: 32rpx;
}

.fund-unit {
  font-size: 26rpx;
  color: #ffffff;
  margin-left: 16rpx;
}

.fund-control-slider {
  margin-bottom: 20rpx;
}

.fund-percentage {
  font-size: 24rpx;
  color: #cccccc;
  margin-top: 12rpx;
}

/* 资金使用进度 */
.fund-usage {
  margin-bottom: 20rpx;
}

.fund-usage-label {
  font-size: 24rpx;
  color: #cccccc;
  margin-bottom: 12rpx;
}

.fund-progress-container {
  height: 8rpx;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 4rpx;
  overflow: hidden;
  margin-bottom: 8rpx;
}

.fund-progress-bar {
  height: 100%;
  background-color: #4caf50;
  transition: width 0.3s ease;
}

.fund-progress-bar.warning {
  background-color: #ff9800;
}

.fund-progress-bar.danger {
  background-color: #f44336;
}

.fund-usage-text {
  font-size: 22rpx;
  color: #999999;
}

.fund-description {
  margin-bottom: 20rpx;
}

.fund-description text {
  font-size: 22rpx;
  color: #999999;
  line-height: 1.5;
}

/* 通知设置 */
.notification-settings {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.notification-label {
  font-size: 26rpx;
  color: #cccccc;
  margin-right: 20rpx;
}

.notification-status {
  font-size: 26rpx;
  color: #4caf50;
  margin-left: 16rpx;
}

/* 连接状态 */
.connection-status {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
}

.connection-label {
  font-size: 26rpx;
  color: #cccccc;
  margin-right: 20rpx;
}

.connection-value {
  font-size: 26rpx;
  color: #ffffff;
  flex: 1;
}

.connection-value.connected {
  color: #4caf50;
}

.connect-btn {
  background-color: #4c8dff;
  color: #ffffff;
  border: none;
  border-radius: 20rpx;
  padding: 12rpx 24rpx;
  font-size: 24rpx;
}

/* T+0 交易控制 */
.t0-trading-controls {
  margin-bottom: 30rpx;
}

.t0-header {
  margin-bottom: 20rpx;
}

.t0-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #ffffff;
}

.t0-options {
  margin-bottom: 20rpx;
}

.t0-mode-selection {
  margin-bottom: 20rpx;
}

.t0-label {
  font-size: 26rpx;
  color: #cccccc;
  margin-bottom: 12rpx;
  display: block;
}

.mode-buttons {
  display: flex;
  gap: 16rpx;
}

.mode-button {
  flex: 1;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1rpx solid rgba(255, 255, 255, 0.2);
  border-radius: 8rpx;
  padding: 16rpx;
  text-align: center;
  font-size: 24rpx;
  color: #cccccc;
}

.mode-button.active {
  background-color: #4c8dff;
  color: #ffffff;
  border-color: #4c8dff;
}

.mode-button.disabled {
  opacity: 0.5;
}

.t0-toggle {
  display: flex;
  align-items: center;
}

.t0-status {
  font-size: 26rpx;
  color: #4caf50;
  margin-left: 16rpx;
}

.t0-info {
  margin-top: 20rpx;
}

.t0-info-text {
  font-size: 22rpx;
  color: #999999;
  line-height: 1.5;
  margin-bottom: 12rpx;
}

.last-update {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.last-update text {
  font-size: 20rpx;
  color: #999999;
}

.update-status.eod-time {
  color: #4caf50;
}

.update-status.not-eod-time {
  color: #ff9800;
}

/* 控制按钮 */
.control-buttons {
  display: flex;
  gap: 20rpx;
}

.control-btn {
  flex: 1;
  border: none;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 28rpx;
  font-weight: bold;
}

.btn-start {
  background-color: #4caf50;
  color: #ffffff;
}

.btn-stop {
  background-color: #f44336;
  color: #ffffff;
}

.btn-settings {
  background-color: #666666;
  color: #ffffff;
}

.control-btn:disabled {
  opacity: 0.5;
}

/* T+0股票池 */
.t0-stocks-pool {
  background: linear-gradient(135deg, #1e3a5f, #2c5aa0);
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.card-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #ffffff;
}

.refresh-btn {
  font-size: 24rpx;
  color: #4c8dff;
  padding: 8rpx 16rpx;
  border: 1rpx solid #4c8dff;
  border-radius: 20rpx;
}

.pool-description {
  margin-bottom: 20rpx;
}

.pool-description text {
  font-size: 22rpx;
  color: #cccccc;
  line-height: 1.5;
}

.t0-stocks-table {
  margin-bottom: 20rpx;
}

.stocks-table {
  min-width: 1200rpx;
}

.table-header, .table-row {
  display: flex;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid rgba(255, 255, 255, 0.1);
}

.table-header {
  background-color: rgba(255, 255, 255, 0.05);
}

.table-cell {
  flex: 1;
  text-align: center;
  font-size: 24rpx;
  color: #ffffff;
  padding: 0 8rpx;
}

.table-header .table-cell {
  font-weight: bold;
  color: #cccccc;
}

.positive {
  color: #4caf50;
}

.negative {
  color: #f44336;
}

.high-volume {
  color: #ff4757;
  font-weight: bold;
}

.medium-volume {
  color: #ff9800;
}

.normal-volume {
  color: #ffffff;
}

.volume-pattern-tag {
  padding: 4rpx 8rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
}

.bullish-pattern {
  background-color: #4caf50;
  color: #ffffff;
}

.bearish-pattern {
  background-color: #f44336;
  color: #ffffff;
}

.neutral-pattern {
  background-color: #666666;
  color: #ffffff;
}

.t0-signal {
  font-size: 22rpx;
  color: #4c8dff;
}

.actions {
  display: flex;
  gap: 8rpx;
}

.action-btn {
  padding: 8rpx 16rpx;
  border-radius: 16rpx;
  font-size: 20rpx;
  border: none;
}

.action-btn.buy {
  background-color: #4caf50;
  color: #ffffff;
}

.action-btn.details {
  background-color: #666666;
  color: #ffffff;
}

.pool-note {
  margin-top: 20rpx;
}

.pool-note text {
  font-size: 20rpx;
  color: #999999;
  line-height: 1.5;
}

/* T+0提示框 */
.t0-toast {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 9999;
}

.t0-toast-content {
  background-color: #4caf50;
  color: #ffffff;
  padding: 20rpx 40rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
}

/* AI决策历史 */
.decisions-card {
  background: linear-gradient(135deg, #1e3a5f, #2c5aa0);
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.decision-list {
  margin-top: 20rpx;
}

.decision-item {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 12rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
}

.decision-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.decision-stock {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.decision-symbol {
  font-size: 26rpx;
  font-weight: bold;
  color: #ffffff;
}

.decision-name {
  font-size: 24rpx;
  color: #cccccc;
}

.decision-action {
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  font-weight: bold;
}

.buy-action {
  background-color: #4caf50;
  color: #ffffff;
}

.sell-action {
  background-color: #f44336;
  color: #ffffff;
}

.decision-details {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
  margin-bottom: 16rpx;
}

.decision-detail-item {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.detail-label {
  font-size: 20rpx;
  color: #999999;
}

.detail-value {
  font-size: 24rpx;
  color: #ffffff;
}

.detail-value.confidence {
  color: #4c8dff;
  font-weight: bold;
}

.decision-reason {
  margin-bottom: 16rpx;
}

.reason-title {
  font-size: 22rpx;
  color: #cccccc;
  margin-bottom: 8rpx;
}

.reason-content {
  font-size: 24rpx;
  color: #ffffff;
  line-height: 1.5;
}

.decision-actions {
  display: flex;
  gap: 16rpx;
}

.execute-btn {
  background-color: #4caf50;
  color: #ffffff;
}

.ignore-btn {
  background-color: #666666;
  color: #ffffff;
}

.decision-status {
  text-align: center;
}

.status-text {
  font-size: 24rpx;
  font-weight: bold;
}

.status-success {
  color: #4caf50;
}

.status-failed {
  color: #f44336;
}

.status-hold {
  color: #ff9800;
}

.status-message {
  font-size: 20rpx;
  color: #cccccc;
  margin-top: 8rpx;
}

.empty-decisions {
  text-align: center;
  padding: 40rpx;
}

.empty-text {
  font-size: 24rpx;
  color: #999999;
}

/* AI学习进度 */
.learning-card {
  background: linear-gradient(135deg, #1e3a5f, #2c5aa0);
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.learning-progress {
  margin-bottom: 30rpx;
}

.progress-bar-container {
  height: 12rpx;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 6rpx;
  overflow: hidden;
  margin-bottom: 12rpx;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4c8dff, #00d4ff);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 24rpx;
  color: #cccccc;
  text-align: center;
}

.learning-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 30rpx;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 22rpx;
  color: #cccccc;
  margin-bottom: 8rpx;
}

.stat-value {
  font-size: 28rpx;
  font-weight: bold;
  color: #ffffff;
}

.learning-metrics {
  margin-bottom: 30rpx;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12rpx 0;
  border-bottom: 1rpx solid rgba(255, 255, 255, 0.1);
}

.metric-item:last-child {
  border-bottom: none;
}

.metric-label {
  font-size: 24rpx;
  color: #cccccc;
}

.metric-value {
  font-size: 24rpx;
  font-weight: bold;
  color: #ffffff;
}

.metric-value.profit {
  color: #4caf50;
}

.metric-value.loss {
  color: #f44336;
}

.learning-actions {
  display: flex;
  gap: 20rpx;
}

.learning-btn {
  flex: 1;
  background-color: #4c8dff;
  color: #ffffff;
  border: none;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 26rpx;
  font-weight: bold;
}

/* 回测功能 */
.backtest-card {
  background: linear-gradient(135deg, #1e3a5f, #2c5aa0);
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.backtest-config {
  margin-bottom: 30rpx;
}

.config-row {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.config-label {
  font-size: 26rpx;
  color: #cccccc;
  width: 160rpx;
}

.picker-value {
  background-color: rgba(255, 255, 255, 0.1);
  border: 1rpx solid rgba(255, 255, 255, 0.2);
  border-radius: 8rpx;
  padding: 12rpx 16rpx;
  color: #ffffff;
  font-size: 24rpx;
  min-width: 120rpx;
  text-align: center;
}

.config-input {
  flex: 1;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1rpx solid rgba(255, 255, 255, 0.2);
  border-radius: 8rpx;
  padding: 12rpx 16rpx;
  color: #ffffff;
  font-size: 24rpx;
  margin: 0 16rpx;
}

.config-unit {
  font-size: 24rpx;
  color: #cccccc;
}

.backtest-actions {
  display: flex;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.backtest-btn {
  flex: 1;
  background-color: #4c8dff;
  color: #ffffff;
  border: none;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 26rpx;
  font-weight: bold;
}

.backtest-btn.secondary {
  background-color: #666666;
}

.backtest-btn:disabled {
  opacity: 0.5;
}

.backtest-results {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.result-item {
  flex: 1;
  min-width: 200rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16rpx;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8rpx;
}

.result-label {
  font-size: 22rpx;
  color: #cccccc;
  margin-bottom: 8rpx;
}

.result-value {
  font-size: 28rpx;
  font-weight: bold;
  color: #ffffff;
}

/* 风险控制 */
.risk-control-card {
  background: linear-gradient(135deg, #1e3a5f, #2c5aa0);
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.risk-config {
  margin-bottom: 30rpx;
}

.risk-item {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.risk-label {
  font-size: 26rpx;
  color: #cccccc;
  width: 200rpx;
}

.risk-input {
  flex: 1;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1rpx solid rgba(255, 255, 255, 0.2);
  border-radius: 8rpx;
  padding: 12rpx 16rpx;
  color: #ffffff;
  font-size: 24rpx;
  margin-right: 16rpx;
}

.risk-unit {
  font-size: 24rpx;
  color: #cccccc;
  width: 40rpx;
}

.risk-switches {
  margin-bottom: 20rpx;
}

.switch-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.switch-label {
  font-size: 26rpx;
  color: #cccccc;
}

/* 性能统计 */
.performance-card {
  background: linear-gradient(135deg, #1e3a5f, #2c5aa0);
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.performance-stats {
  margin-top: 20rpx;
}

.stat-row {
  display: flex;
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.stat-row:last-child {
  margin-bottom: 0;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16rpx;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8rpx;
}

.stat-label {
  font-size: 22rpx;
  color: #cccccc;
  margin-bottom: 8rpx;
  text-align: center;
}

.stat-value {
  font-size: 28rpx;
  font-weight: bold;
  color: #ffffff;
}

/* 环境管理 */
.environment-card {
  background: linear-gradient(135deg, #1e3a5f, #2c5aa0);
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.environment-selector {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
}

.env-label {
  font-size: 26rpx;
  color: #cccccc;
  margin-right: 20rpx;
}

.env-prod {
  color: #ff4757 !important;
  font-weight: bold;
}

.env-test {
  color: #4c8dff !important;
}

.environment-info {
  margin-bottom: 20rpx;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12rpx 0;
  border-bottom: 1rpx solid rgba(255, 255, 255, 0.1);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 24rpx;
  color: #cccccc;
}

.info-value {
  font-size: 24rpx;
  color: #ffffff;
}

.risk-high {
  color: #ff4757;
  font-weight: bold;
}

.risk-low {
  color: #4caf50;
}

.environment-warning {
  background-color: rgba(255, 71, 87, 0.1);
  border: 1rpx solid #ff4757;
  border-radius: 8rpx;
  padding: 16rpx;
  margin-top: 20rpx;
}

.warning-text {
  font-size: 24rpx;
  color: #ff4757;
  text-align: center;
}

/* T+0自动更新 */
.t0-auto-update-card {
  background: linear-gradient(135deg, #1e3a5f, #2c5aa0);
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.t0-update-config {
  margin-bottom: 30rpx;
}

.config-item {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.t0-update-controls {
  margin-bottom: 20rpx;
}

.t0-update-btn {
  width: 100%;
  background-color: #4c8dff;
  color: #ffffff;
  border: none;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 26rpx;
  font-weight: bold;
  margin-top: 20rpx;
}

.t0-update-status {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
  padding: 16rpx;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8rpx;
}

.status-label {
  font-size: 22rpx;
  color: #cccccc;
  margin-right: 12rpx;
}

.status-value {
  font-size: 22rpx;
  color: #ffffff;
}
</style>
