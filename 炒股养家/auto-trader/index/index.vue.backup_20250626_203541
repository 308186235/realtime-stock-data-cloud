<template>
	<view class="container">
		<!-- T+0模式提示框 -->
		<view v-if="showT0Toast" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.7); z-index: 999; display: flex; justify-content: center; align-items: center;">
			<view style="background-color: #000; color: #fff; padding: 20rpx 40rpx; border-radius: 10rpx; font-size: 32rpx; font-weight: bold;">
				已开启T+0交易模式
			</view>
		</view>
		
		<!-- 标题及欢迎信息 -->
		<view class="header">
			<text class="main-title">股票交易系统</text>
			<text class="subtitle">AI驱动的智能交易平台</text>
		</view>
		
		<!-- 市场概览 Section -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">市场概览</text>
				<text class="refresh-btn" @click="refreshMarketData">刷新</text>
			</view>
			<scroll-view scroll-x="true" class="market-scroll">
				<view class="market-indices">
					<!-- 硬编码市场指数数据 -->
					<view class="index-card">
						<view class="index-header">
							<text class="index-name">上证指数</text>
							<text class="index-value">3,258.63</text>
							<text class="index-change increase">+0.56%</text>
						</view>
						<view class="strategy-tip" @click="toggleStrategy('shanghai')">
							<text class="tip-icon">ℹ️</text>
							<text class="tip-text">防御策略说明</text>
						</view>
						<view v-if="expandedStrategy === 'shanghai'" class="strategy-detail">
							<text class="strategy-text">• 主力资金3日净流出超5%自动减持\n• 波动率突破布林带上轨触发预警\n• 大宗交易异常同步启动反操纵策略</text>
						</view>
					</view>
					<view class="index-card">
						<text class="index-name">深证成指</text>
						<text class="index-value">10,825.93</text>
						<text class="index-change decrease">-0.23%</text>
					</view>
					<view class="index-card">
						<text class="index-name">创业板指</text>
						<text class="index-value">2,156.78</text>
						<text class="index-change increase">+1.05%</text>
					</view>
					<view class="index-card">
						<text class="index-name">沪深300</text>
						<text class="index-value">3,985.45</text>
						<text class="index-change increase">+0.78%</text>
					</view>
					<view class="index-card">
						<text class="index-name">中证500</text>
						<text class="index-value">6,532.21</text>
						<text class="index-change decrease">-0.12%</text>
					</view>
				</view>
			</scroll-view>
		</view>

		<!-- 主力资金监控 Section -->
		<view class="section fund-flow-section">
			<view class="section-header">
				<text class="section-title">主力资金监控</text>
				<text class="refresh-btn" @click="refreshFundFlow">刷新</text>
			</view>
			<view class="fund-flow-content">
				<view class="fund-flow-chart">
					<!-- 实时资金流向图表 -->
					<canvas canvas-id="fundFlowChart" class="chart-container" id="fundFlowCanvas"></canvas>
				</view>
				<view class="fund-flow-info">
					<view class="abnormal-signal">
						<text class="signal-label">异常信号：</text>
						<text class="signal-value" :class="abnormalSignalClass">{{ abnormalSignalText }}</text>
					</view>
					<view class="fund-flow-stats">
						<view class="stat-item">
							<text class="stat-label">当日净流入</text>
							<text class="stat-value" :class="mainFundData.fundFlow >= 0 ? 'profit' : 'loss'">
								{{ mainFundData.fundFlow >= 0 ? '+' : '' }}{{ mainFundData.fundFlow.toFixed(2) }}%
							</text>
						</view>
						<view class="stat-item">
							<text class="stat-label">更新时间</text>
							<text class="stat-value">{{ mainFundData.lastUpdate }}</text>
						</view>
					</view>
				</view>
			</view>
		</view>

		<view class="section auto-trade-highlight">
			<view class="section-header">
				<text class="section-title">自动交易平台</text>
				<text class="more-btn" @click="navigateTo('/pages/auto-trader/index')">管理</text>
			</view>
			
			<view class="auto-trade-overview">
				<view class="trade-status-box">
					<view class="status-info">
						<text class="status-label">系统状态</text>
						<text v-if="autoTradeEnabled" class="status-value status-active">
							自动交易运行中
						</text>
						<text v-else class="status-value status-inactive">
							自动交易已停止
						</text>
					</view>
					
					<view class="auto-trade-toggle">
						<text class="toggle-label">{{ autoTradeEnabled ? '停止' : '启用' }}</text>
						<switch :checked="autoTradeEnabled" @change="toggleAutoTrading" color="#1989fa"/>
					</view>
				</view>
				
				<view class="trade-mode-selection">
					<text class="mode-title">交易模式</text>
					<view class="mode-options">
						<view class="mode-option" :class="{'active': tradeMode === 'CONSERVATIVE'}"
								@click="setTradeMode('CONSERVATIVE')">
							<text class="mode-icon">🛡️</text>
							<text class="mode-name">保守型</text>
						</view>
						<view class="mode-option" :class="{'active': tradeMode === 'MODERATE'}"
								@click="setTradeMode('MODERATE')">
							<text class="mode-icon">⚖️</text>
							<text class="mode-name">平衡型</text>
						</view>
						<view class="mode-option" :class="{'active': tradeMode === 'AGGRESSIVE'}"
								@click="setTradeMode('AGGRESSIVE')">
							<text class="mode-icon">🚀</text>
							<text class="mode-name">激进型</text>
						</view>
					</view>
				</view>
				
				<view class="trade-metrics">
					<view class="metric-item">
						<text class="metric-label">今日交易</text>
						<text class="metric-value">{{ todayTrades }} 笔</text>
					</view>
					<view class="metric-item">
						<text class="metric-label">自动交易收益</text>
						<text v-if="weeklyProfit >= 0" class="metric-value" style="color: #ff0000; font-weight: bold;">
							+{{ weeklyProfit }}%
						</text>
						<text v-else class="metric-value" style="color: #00cc00; font-weight: bold;">
							{{ weeklyProfit }}%
						</text>
					</view>
				</view>
				
				<view class="quick-actions">
					<button class="action-btn secondary" @click="navigateTo('/pages/trade-settings/index')">交易设置</button>
					<button class="action-btn secondary" @click="navigateTo('/pages/trade-history/index')">交易历史</button>
					<button class="action-btn primary" @click="openAIAnalytics">AI智能分析</button>
				</view>
			</view>
		</view>

		<!-- Portfolio Summary Section -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">持仓概览</text>
				<text class="more-btn" @click="navigateTo('/pages/portfolio/index')">查看详情</text>
			</view>
			<view class="portfolio-summary card">
				<view class="summary-row">
					<text>总资产</text>
					<text class="summary-value">¥{{ totalAssets }}</text>
				</view>
				<view class="summary-row">
					<text>持仓市值</text>
					<text class="summary-value">¥{{ stockValue }}</text>
				</view>
				<view class="summary-row">
					<text>可用资金</text>
					<text class="summary-value">¥{{ availableCash }}</text>
				</view>
				<view class="summary-row">
					<text>可操作金额</text>
					<view class="editable-amount">
						<text class="summary-value">¥{{ operableAmount }}</text>
						<text class="edit-btn" @click="showAmountModal">调整</text>
					</view>
				</view>
				<view class="summary-row">
					<text>今日盈亏</text>
					<text v-if="todayProfit >= 0" class="summary-value" style="color: #ff0000; font-weight: bold;">
						+¥{{ todayProfit }}
					</text>
					<text v-else class="summary-value" style="color: #00cc00; font-weight: bold;">
						-¥{{ Math.abs(todayProfit) }}
					</text>
				</view>
				<view class="summary-row">
					<text>总盈亏</text>
					<text v-if="totalProfit >= 0" class="summary-value" style="color: #ff0000; font-weight: bold;">
						+¥{{ totalProfit }} ({{ totalProfitPercentage }}%)
					</text>
					<text v-else class="summary-value" style="color: #00cc00; font-weight: bold;">
						-¥{{ Math.abs(totalProfit) }} ({{ totalProfitPercentage }}%)
					</text>
				</view>
			</view>
		</view>

		<!-- 高级风控看板 -->
		<view class="section risk-dashboard">
			<view class="section-header">
				<text class="section-title">风控指标</text>
				<text class="refresh-btn" @click="refreshRiskData">刷新</text>
			</view>
			<view class="risk-metrics">
				<view class="metric-card">
					<text class="metric-label">VAR值</text>
					<text class="metric-value" style="color: #ff0000; font-weight: bold;">{{ riskMetrics.var }}%</text>
				</view>
				<view class="metric-card">
					<text class="metric-label">最大回撤</text>
					<text class="metric-value" style="color: #ff0000; font-weight: bold;">{{ riskMetrics.maxDrawdown }}%</text>
				</view>
				<view class="metric-card">
					<text class="metric-label">波动率</text>
					<text class="metric-value">{{ riskMetrics.volatility }}%</text>
				</view>
			</view>
			<view class="risk-chart">
				<canvas canvas-id="riskChart" class="chart-container" :canvas-width="300" :canvas-height="200"></canvas>
			</view>
		</view>

		<!-- 多因子选股结果 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">智能选股推荐</text>
				<text class="more-btn" @click="navigateTo('/pages/stock-picking/results')">查看更多</text>
			</view>
			<view class="stock-picking-results card" style="overflow: hidden; padding: 20rpx; background-color: #f9f9f9; border-radius: 12rpx; margin-bottom: 20rpx;">
				<!-- Strategy and date filters -->
				<view style="display: flex; flex-wrap: wrap; align-items: center; margin-bottom: 16rpx;">
					<view style="margin-right: 20rpx; margin-bottom: 10rpx;">
						<picker @change="changeStrategy" :value="strategyIndex" :range="strategyNames">
							<view style="background-color: #f0f0f0; padding: 10rpx 15rpx; border-radius: 6rpx; font-size: 24rpx;">
								当前策略：{{ strategyNames[strategyIndex] }}
							</view>
						</picker>
					</view>
					
					<view style="display: flex; margin-bottom: 10rpx;">
						<view style="font-size: 24rpx; background-color: #f0f0f0; padding: 10rpx 15rpx; border-radius: 6rpx; margin-right: 10rpx;" :style="{backgroundColor: timeFilter === 'day' ? '#1989fa' : '#f0f0f0', color: timeFilter === 'day' ? '#fff' : '#666'}" @click="timeFilter='day'">当日</view>
						<view style="font-size: 24rpx; background-color: #f0f0f0; padding: 10rpx 15rpx; border-radius: 6rpx;" :style="{backgroundColor: timeFilter === 'week' ? '#1989fa' : '#f0f0f0', color: timeFilter === 'week' ? '#fff' : '#666'}" @click="timeFilter='week'">当周</view>
					</view>
				</view>
    
				<!-- Trading mode and type -->
				<view style="display: flex; flex-wrap: wrap; align-items: center; margin-bottom: 16rpx;">
					<view style="display: flex; align-items: center; margin-right: 20rpx; margin-bottom: 10rpx;">
						<text style="font-size: 24rpx; margin-right: 10rpx;">交易模式:</text>
						<view style="display: flex; overflow: hidden; border-radius: 6rpx;">
							<view style="padding: 10rpx 15rpx; font-size: 24rpx; text-align: center;" :style="{backgroundColor: tradeTimeMode === 'EOD' ? '#1989fa' : '#f0f0f0', color: tradeTimeMode === 'EOD' ? '#fff' : '#666'}" @click="setTradeTimeMode('EOD')">
								尾盘选股
							</view>
							<view style="padding: 10rpx 15rpx; font-size: 24rpx; text-align: center;" :style="{backgroundColor: tradeTimeMode === 'INTRADAY' ? '#1989fa' : '#f0f0f0', color: tradeTimeMode === 'INTRADAY' ? '#fff' : '#666', opacity: t0Enabled ? 0.5 : 1}" @click="setTradeTimeMode('INTRADAY')">
								盘中选股
							</view>
						</view>
					</view>
					
					<view style="display: flex; align-items: center; margin-bottom: 10rpx;">
						<text style="font-size: 24rpx; margin-right: 10rpx;">交易类型:</text>
						<switch :checked="t0Enabled" @change="toggleT0Mode" color="#1989fa" style="transform: scale(0.8);"/>
						<text style="font-size: 24rpx; margin-left: 10rpx; font-weight: bold;">{{ t0Enabled ? 'T+0' : 'T+1' }}</text>
					</view>
				</view>
				
				<!-- Notification -->
				<view v-if="tradeTimeMode === 'EOD'" style="width: 100%; padding: 10rpx; background-color: #f0f0f0; border-radius: 6rpx; margin-bottom: 16rpx; font-size: 24rpx; color: #666;">
					<text>尾盘选股将在每个交易日14:30后更新，以便支持T+0交易</text>
					<view v-if="lastEodUpdateTime">
						<text>最近更新: {{ lastEodUpdateTime }}</text>
						<text style="margin-left: 10rpx; padding: 4rpx 12rpx; border-radius: 16rpx;" :style="{backgroundColor: isEodTime ? '#f6ffed' : '#fff7e6', color: isEodTime ? '#52c41a' : '#d48806'}">{{ isEodTime ? '尾盘时段' : '非尾盘时段' }}</text>
					</view>
				</view>
				
				<!-- Table -->
				<scroll-view scroll-x class="factor-score-table" style="width: 100%; overflow-x: auto; white-space: nowrap;">
					<view style="min-width: 100%; display: table; border-collapse: collapse; width: 100%;">
						<!-- Table header -->
						<view style="display: table-header-group; background-color: #f0f0f0;">
							<view style="display: table-row;">
								<view style="display: table-cell; padding: 16rpx; text-align: center; font-size: 24rpx; font-weight: bold;">代码</view>
								<view style="display: table-cell; padding: 16rpx; text-align: center; font-size: 24rpx; font-weight: bold;">名称</view>
								<view style="display: table-cell; padding: 16rpx; text-align: center; font-size: 24rpx; font-weight: bold;">动量</view>
								<view style="display: table-cell; padding: 16rpx; text-align: center; font-size: 24rpx; font-weight: bold;">估值</view>
								<view style="display: table-cell; padding: 16rpx; text-align: center; font-size: 24rpx; font-weight: bold;">资金</view>
								<view style="display: table-cell; padding: 16rpx; text-align: center; font-size: 24rpx; font-weight: bold;">情绪</view>
								<view style="display: table-cell; padding: 16rpx; text-align: center; font-size: 24rpx; font-weight: bold;">综合</view>
								<view style="display: table-cell; padding: 16rpx; text-align: center; font-size: 24rpx; font-weight: bold;">操作</view>
							</view>
						</view>
						
						<!-- Table body -->
						<view style="display: table-row-group;">
							<view v-for="(item, index) in filteredStocks" :key="index" style="display: table-row; border-bottom: 1px solid #f0f0f0;">
								<view style="display: table-cell; padding: 16rpx; text-align: center; font-size: 24rpx;">{{item.code}}</view>
								<view style="display: table-cell; padding: 16rpx; text-align: center; font-size: 24rpx;">
									{{item.name || ''}}
									<view v-if="t0Enabled && tradeTimeMode === 'EOD' && item.t0Signal" style="display: inline-block; background: #fffbe6; border-radius: 4rpx; padding: 2rpx 6rpx; margin-top: 4rpx; font-size: 20rpx; color: #d48806;">
										⚡ {{item.t0Signal}}
									</view>
								</view>
								<view style="display: table-cell; padding: 16rpx; text-align: center; font-size: 24rpx;">{{(item.momentum*100).toFixed(1)}}%</view>
								<view style="display: table-cell; padding: 16rpx; text-align: center; font-size: 24rpx;">{{(item.valuation*100).toFixed(1)}}%</view>
								<view style="display: table-cell; padding: 16rpx; text-align: center; font-size: 24rpx;">{{(item.liquidity*100).toFixed(1)}}%</view>
								<view style="display: table-cell; padding: 16rpx; text-align: center; font-size: 24rpx;">{{(item.sentiment*100).toFixed(1)}}%</view>
								<view style="display: table-cell; padding: 16rpx; text-align: center; font-size: 24rpx; font-weight: bold; color: #f5222d;">{{(item.composite*100).toFixed(1)}}%</view>
								<view style="display: table-cell; padding: 16rpx; text-align: center; font-size: 24rpx;">
									<button style="width: 100%; font-size: 22rpx; padding: 4rpx 0; text-align: center; border-radius: 4rpx; margin-bottom: 6rpx; background-color: #1989fa; color: white;" @click="showOrderDialog(item, 'buy')">买入</button>
									<button v-if="t0Enabled" style="width: 100%; font-size: 22rpx; padding: 4rpx 0; text-align: center; border-radius: 4rpx; background-color: #ff4d4f; color: white;" @click="showOrderDialog(item, 'sell')">卖出</button>
								</view>
							</view>
						</view>
					</view>
				</scroll-view>
			</view>
		</view>

		<!-- AI Insights Section -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">AI 洞察</text>
				<text class="more-btn" @click="navigateTo('/pages/agent-analysis/diagnosis/index')">查看更多</text>
			</view>
			<view class="ai-insights card">
				<view class="insight-item" v-for="(item, index) in aiInsights" :key="index">
					<text class="insight-title">{{ item.title }}</text>
					<text class="insight-content">{{ item.content }}</text>
					<view class="insight-footer">
						<text class="insight-date">{{ item.date }}</text>
						<text class="insight-tag" :style="{backgroundColor: item.tagColor}">{{ item.tag }}</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 直接嵌入 AI 分析组件 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">AI 分析控制台</text>
				<text class="more-btn" @click="navigateTo('/pages/agent-analysis/index')">全屏查看</text>
			</view>
			<view class="embedded-ai-analytics">
				<view class="loading-indicator">
					<text>AI分析界面已嵌入主页</text>
				</view>
				<AIAnalytics />
			</view>
		</view>

		<!-- 策略效果对比 -->
		<view class="section strategy-comparison">
			<view class="section-header">
				<text class="section-title">策略效果对比</text>
				<text class="more-btn" @click="navigateTo('/pages/strategy-analysis/comparison/index')">更多</text>
			</view>
			<view class="strategy-metrics">
				<view class="metric-card" v-for="(strategy, index) in strategyMetrics" :key="index">
					<text class="metric-label">{{ strategy.name }}</text>
					<text class="metric-value">{{ strategy.return }}%</text>
					<progress class="metric-progress" :value="getProgressValue(strategy.return)" :max="100" :activeColor="getReturnColor(strategy.return)"></progress>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import AIAnalytics from '../../components/AIAnalytics.vue';

export default {
	components: {
		AIAnalytics
	},
	data() {
		return {
			// 多因子选股数据
			strategyNames: ['多因子平衡型', '成长价值型', '动量趋势型'],
			strategyIndex: 0,
			timeFilter: 'day',
			stockPicks: [
				{
					code: 'SH600519',
					name: '贵州茅台',
					momentum: 0.82,
					valuation: 0.75,
					liquidity: 0.68,
					sentiment: 0.91,
					composite: 0.79
				},
				{
					code: 'SZ300750',
					name: '宁德时代',
					momentum: 0.68,
					valuation: 0.88,
					liquidity: 0.92,
					sentiment: 0.76,
					composite: 0.81
				}
			],
			
			// 风控指标数据
			riskMetrics: {
				var: 2.8,
				maxDrawdown: 1.5,
				volatility: 15.2
			},
			// 市场概览数据
			expandedStrategy: '',
			
			// 主力资金数据
			mainFundData: {
				fundFlow: 2.45,
				patternScore: 0.72,
				volatility: 0.15,
				lastUpdate: '14:30',
				history: [] // 添加历史数据数组
			},
			
			// 资金流向历史数据
			capitalFlowHistory: [],
			
			// 预警数据
			alerts: [],
			
			// 异常信号数据
			abnormalSignalText: '未检测到异常',
			abnormalSignalClass: 'normal',
			
			// 自动交易数据
			autoTradeEnabled: false,
			tradeMode: 'MODERATE',
			todayTrades: 8,
			weeklyProfit: 5.2,
			riskRewardRatio: 2.5,
			chartInstance: null,
			
			// 持仓概览数据
			totalAssets: '125,680.00',
			stockValue: '98,450.00',
			availableCash: '27,230.00',
			todayProfit: 1250.80,
			totalProfit: 15680.50,
			totalProfitPercentage: 12.5,
			operableAmount: '10,000.00',
			
			// WebSocket连接管理
			ws: null,
			isConnecting: false,
			reconnectAttempts: 0,
			wsAvailable: true, // 用于标记WebSocket是否可用
			
			// 自动刷新定时器
			refreshTimer: null,
			
			// AI洞察数据
			aiInsights: [
				{
					title: "市场趋势分析",
					content: "根据近期数据分析，市场整体呈现震荡上行趋势，建议关注消费和科技板块。",
					date: "2023-06-05",
					tag: "趋势",
					tagColor: "#1989fa"
				},
				{
					title: "投资组合优化建议",
					content: "当前投资组合风险较高，建议适当增加防御性板块配置，降低组合波动性。",
					date: "2023-06-04",
					tag: "组合",
					tagColor: "#f5222d"
				}
			],
			
			// 策略效果数据
			strategyMetrics: [
				{
					name: "动量策略",
					return: 12.5
				},
				{
					name: "均值回归",
					return: 8.2
				},
				{
					name: "区块链监控",
					return: 15.1
				}
			],
			
			// 指数和成交量数据
			indexData: {
				value: '3,258.63',
				change: '18.25',
				changePercent: '0.56'
			},
			volumeData: {
				value: '1,235.8百万'
			},
			tradeTimeMode: 'EOD',
			t0Enabled: true,
			lastEodUpdateTime: '', // 最后尾盘更新时间
			t0StocksPool: [],      // T+0股票池
			showT0Toast: false,    // T+0模式提示框显示状态
		}
	},
	computed: {
		filteredStocks() {
			// 获取基础股票池
			let stockPool = this.stockPicks.filter(item => {
				const currentScore = item.composite
				return currentScore > 0.7
			}).sort((a, b) => b.composite - a.composite)
			
			// 如果是尾盘选股模式且T+0开启，使用T+0股票池
			if (this.tradeTimeMode === 'EOD' && this.t0Enabled) {
				// 使用T+0股票池，如果有的话
				if (this.t0StocksPool.length > 0) {
					return this.t0StocksPool
				}
			}
			
			return stockPool
		},
		
		// 当前是否可以进行尾盘选股
		isEodTime() {
			const now = new Date()
			const hour = now.getHours()
			const minute = now.getMinutes()
			
			// 判断是否是交易日的14:30以后
			return (hour > 14 || (hour === 14 && minute >= 30)) && hour < 15
		}
	},
	methods: {
		// 多因子选股相关方法
		changeStrategy(e) {
			this.strategyIndex = e.detail.value
		},
		
		showOrderDialog(stock, action) {
			let content = `确认${action === 'buy' ? '买入' : '卖出'} ${stock.code}？`
			
			// 如果是T+0模式且有T+0信号，添加信号提示
			if (this.t0Enabled && stock.t0Signal && this.tradeTimeMode === 'EOD') {
				content += `\n\n尾盘信号: ${stock.t0Signal}\n${stock.t0Reason || ''}`
			}
			
			uni.showModal({
				title: '交易确认',
				content: content,
				success: (res) => {
					if (res.confirm) {
						uni.showToast({
							title: `已${action === 'buy' ? '买入' : '卖出'}`,
							icon: 'success'
						})
					}
				}
			})
		},
		
		// 切换策略显示
		toggleStrategy(strategyKey) {
			if (this.expandedStrategy === strategyKey) {
				this.expandedStrategy = '';
			} else {
				this.expandedStrategy = strategyKey;
			}
		},
		
		// 刷新市场数据
		refreshMarketData() {
			uni.showToast({
				title: '数据已刷新',
				icon: 'success'
			});
		},
		
		// 刷新资金流向
		refreshFundFlow() {
			this.fetchMainFundData();
			this.drawMainFundChart();
			uni.showToast({
				title: '资金流向已刷新',
				icon: 'success'
			});
		},
		
		// 切换自动交易状态
		toggleAutoTrading(e) {
			this.autoTradeEnabled = e.detail.value;
			uni.showToast({
				title: this.autoTradeEnabled ? '自动交易已启用' : '自动交易已停止',
				icon: 'none'
			});
		},
		
		// 设置交易模式
		setTradeMode(mode) {
			this.tradeMode = mode;
			uni.showToast({
				title: '交易模式已设置',
				icon: 'success'
			});
		},
		
		// 页面导航
		navigateTo(url) {
			console.log('Navigating to:', url);
			
			try {
			uni.navigateTo({
					url: url,
					success: (res) => {
						console.log('Navigation success:', url);
					},
					fail: (err) => {
						console.error('Navigation failed:', url, err);
						// 尝试使用重定向作为备选方案
						uni.redirectTo({
							url: url,
							fail: (redirectErr) => {
								console.error('Redirect also failed:', url, redirectErr);
								// 显示错误提示
								uni.showToast({
									title: '页面跳转失败',
									icon: 'none'
								});
							}
						});
					}
				});
			} catch (e) {
				console.error('Navigation error:', e);
			}
		},
		
		// 新增监控方法
		fetchMainFundData() {
			// 模拟数据，实际应调用API
			const newFundFlow = Math.random() * 5 - 2.5;
			
			// 如果没有历史数据，创建初始数据
			if (!this.mainFundData.history || this.mainFundData.history.length === 0) {
				// 生成过去12个时间点的数据
				const history = [];
				const now = new Date();
				for (let i = 11; i >= 0; i--) {
					const time = new Date(now);
					time.setMinutes(now.getMinutes() - (i * 15));
					history.push({
						time: time.toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit'}),
						value: Math.random() * 5 - 2.5
					});
				}
				this.mainFundData.history = history;
			}
			
			// 添加新数据点到历史记录中
			this.mainFundData.history.push({
				time: new Date().toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit'}),
				value: newFundFlow
			});
			
			// 保持最多显示12个数据点，移除最早的
			if (this.mainFundData.history.length > 12) {
				this.mainFundData.history.shift();
			}
			
			this.mainFundData = {
				fundFlow: newFundFlow,
				patternScore: Math.random().toFixed(2),
				volatility: (Math.random() * 0.3).toFixed(2),
				lastUpdate: new Date().toLocaleTimeString('zh-CN'),
				history: this.mainFundData.history
			};
			
			// 更新异常信号
			if (this.mainFundData.fundFlow < -1.5) {
				this.abnormalSignalText = '主力资金大幅流出';
				this.abnormalSignalClass = 'danger';
			} else if (this.mainFundData.fundFlow < -0.5) {
				this.abnormalSignalText = '主力资金轻微流出';
				this.abnormalSignalClass = 'warning';
			} else if (this.mainFundData.fundFlow > 1.5) {
				this.abnormalSignalText = '主力资金大幅流入';
				this.abnormalSignalClass = 'normal';
			} else {
				this.abnormalSignalText = '主力资金流向正常';
				this.abnormalSignalClass = 'normal';
			}
			
			// 绘制主力资金曲线图
			this.drawMainFundChart();
		},
		
		// 绘制主力资金曲线图
		drawMainFundChart() {
			// 使用2D渲染引擎
			const ctx = uni.createCanvasContext('fundFlowChart', this);
			
			// 设置willReadFrequently属性 (解决HTML canvas性能警告)
			// Note: uni-app的canvas上下文可能不支持此属性，但为保险起见仍进行设置
			if (ctx.canvas && typeof ctx.canvas.getContext === 'function') {
				const context2d = ctx.canvas.getContext('2d', { willReadFrequently: true });
				if (context2d) {
					context2d.willReadFrequently = true;
				}
			} else if (ctx) {
				ctx.willReadFrequently = true;
			}
			
			const width = 300;
			const height = 200;
			const padding = 30;
			
			// 清空画布
			ctx.clearRect(0, 0, width, height);
			
			// 获取历史数据
			const historyData = this.mainFundData.history;
			
			// 如果没有数据，显示无数据提示
			if (!historyData || historyData.length === 0) {
				ctx.setFillStyle('#999');
				ctx.setTextAlign('center');
				ctx.setFontSize(14);
				ctx.fillText('暂无数据', width / 2, height / 2);
				ctx.draw();
				return;
			}
			
			// 绘制背景
			ctx.setFillStyle('#f8f8f8');
			ctx.fillRect(0, 0, width, height);
			
			// 获取Y轴的最大和最小值
			let maxValue = -Infinity;
			let minValue = Infinity;
			historyData.forEach(item => {
				maxValue = Math.max(maxValue, item.value);
				minValue = Math.min(minValue, item.value);
			});
			
			// 确保有一定的边距
			const range = Math.max(maxValue - minValue, 2);
			maxValue = maxValue + range * 0.1;
			minValue = minValue - range * 0.1;
			
			// 绘制水平网格线和Y轴标签
			ctx.beginPath();
			ctx.setStrokeStyle('#eeeeee');
			ctx.setLineWidth(1);
			ctx.setFillStyle('#666');
			ctx.setFontSize(10);
			ctx.setTextAlign('right');
			
			const yGridCount = 5;
			for (let i = 0; i <= yGridCount; i++) {
				const y = padding + (height - padding * 2) * (1 - i / yGridCount);
				const value = (minValue + (maxValue - minValue) * (i / yGridCount)).toFixed(1);
				
				// 绘制网格线
				ctx.moveTo(padding, y);
				ctx.lineTo(width - padding, y);
				
				// 绘制Y轴标签
				ctx.fillText(value + '%', padding - 5, y + 3);
			}
			ctx.stroke();
			
			// 绘制X轴标签
			ctx.setTextAlign('center');
			const xStep = (width - padding * 2) / (historyData.length - 1);
			let labelIndex = 0;
			// 仅绘制部分标签以避免拥挤
			const labelStep = Math.ceil(historyData.length / 6);
			
			historyData.forEach((item, index) => {
				if (index % labelStep === 0 || index === historyData.length - 1) {
					const x = padding + index * xStep;
					ctx.fillText(item.time, x, height - padding + 15);
					
					// 绘制垂直网格线
					ctx.beginPath();
					ctx.setStrokeStyle('#eeeeee');
					ctx.moveTo(x, padding);
					ctx.lineTo(x, height - padding);
					ctx.stroke();
					
					labelIndex++;
				}
			});
			
			// 绘制0值的水平线
			if (minValue < 0 && maxValue > 0) {
				const zeroY = padding + (height - padding * 2) * (1 - (0 - minValue) / (maxValue - minValue));
				ctx.beginPath();
				ctx.setStrokeStyle('#dddddd');
				ctx.setLineWidth(1.5);
				ctx.moveTo(padding, zeroY);
				ctx.lineTo(width - padding, zeroY);
				ctx.stroke();
			}
			
			// 绘制主力资金流向曲线
			ctx.beginPath();
			ctx.setStrokeStyle('#1989fa');
			ctx.setLineWidth(2.5);
			
			historyData.forEach((item, index) => {
				const x = padding + index * xStep;
				const y = padding + (height - padding * 2) * (1 - (item.value - minValue) / (maxValue - minValue));
				
				if (index === 0) {
					ctx.moveTo(x, y);
				} else {
					ctx.lineTo(x, y);
				}
			});
			ctx.stroke();
			
			// 绘制曲线下方的渐变填充
			const lastItem = historyData[historyData.length - 1];
			const lastX = padding + (historyData.length - 1) * xStep;
			const lastY = padding + (height - padding * 2) * (1 - (lastItem.value - minValue) / (maxValue - minValue));
			const zeroY = padding + (height - padding * 2) * (1 - (0 - minValue) / (maxValue - minValue));
			const zeroYClamped = Math.min(height - padding, Math.max(padding, zeroY));
			
			// 创建渐变
			const gradient = ctx.createLinearGradient(0, padding, 0, height - padding);
			if (lastItem.value >= 0) {
				gradient.addColorStop(0, 'rgba(25, 137, 250, 0.3)');
				gradient.addColorStop(1, 'rgba(25, 137, 250, 0.05)');
			} else {
				gradient.addColorStop(0, 'rgba(245, 34, 45, 0.05)');
				gradient.addColorStop(1, 'rgba(245, 34, 45, 0.3)');
			}
			
			// 绘制渐变填充
			ctx.beginPath();
			historyData.forEach((item, index) => {
				const x = padding + index * xStep;
				const y = padding + (height - padding * 2) * (1 - (item.value - minValue) / (maxValue - minValue));
				
				if (index === 0) {
					ctx.moveTo(x, y);
				} else {
					ctx.lineTo(x, y);
				}
			});
			ctx.lineTo(lastX, zeroYClamped);
			ctx.lineTo(padding, zeroYClamped);
			ctx.closePath();
			ctx.setFillStyle(gradient);
			ctx.fill();
			
			// 绘制数据点
			historyData.forEach((item, index) => {
				const x = padding + index * xStep;
				const y = padding + (height - padding * 2) * (1 - (item.value - minValue) / (maxValue - minValue));
				
				ctx.beginPath();
				ctx.setFillStyle('#fff');
				ctx.arc(x, y, 3, 0, Math.PI * 2);
				ctx.fill();
				
				ctx.beginPath();
				ctx.setStrokeStyle('#1989fa');
				ctx.setLineWidth(1.5);
				ctx.arc(x, y, 3, 0, Math.PI * 2);
				ctx.stroke();
			});
			
			// 绘制标题
			ctx.setFillStyle('#333');
			ctx.setTextAlign('left');
			ctx.setFontSize(12);
			ctx.fillText('主力资金流向趋势', padding, 15);
			
			// 显示最新值
			ctx.setTextAlign('right');
			ctx.setFontSize(12);
			ctx.fillText('最新: ' + lastItem.value.toFixed(2) + '%', width - padding, 15);
			
			// 提交绘制
			ctx.draw();
		},
		
		initWebSocket() {
			try {
				// 检查WebSocket是否可用
				if (typeof WebSocket === 'undefined') {
					console.log('WebSocket不可用，使用模拟数据');
					// 设置标志位表明WebSocket不可用
					this.wsAvailable = false;
					// 使用模拟数据
					this.startSimulatedDataFeed();
					return;
				}
				
				this.wsAvailable = true;
				this.isConnecting = true;
				
				// 创建WebSocket连接
				try {
					this.ws = new WebSocket('wss://aigupiao.me/ws');
					
					this.ws.onopen = () => {
						console.log('WebSocket连接已建立');
						this.reconnectAttempts = 0;
						this.isConnecting = false;
					};
					
					this.ws.onmessage = (event) => {
						try {
							const data = JSON.parse(event.data);
							// 处理接收到的数据
							this.handleRealTimeData(data);
						} catch (error) {
							console.error('WebSocket数据解析错误:', error);
						}
					};
					
					this.ws.onclose = (e) => {
						console.log('WebSocket连接已关闭, 代码:', e.code);
						this.isConnecting = false;
						
						if (e.code !== 1000) {
							const timeout = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
							console.log(`将在 ${timeout/1000} 秒后尝试重连...`);
							setTimeout(() => {
								this.reconnectAttempts++;
								this.initWebSocket();
							}, timeout);
						}
						
						// 如果重连失败超过一定次数，使用模拟数据
						if (this.reconnectAttempts >= 5) {
							console.log('WebSocket重连失败次数过多，切换到模拟数据');
							this.wsAvailable = false;
							this.startSimulatedDataFeed();
						}
					};
					
					this.ws.onerror = (error) => {
						console.error('WebSocket错误:', error);
						this.isConnecting = false;
						this.ws.close();
					};
				} catch (err) {
					console.error('创建WebSocket连接失败:', err);
					this.wsAvailable = false;
					this.startSimulatedDataFeed();
				}
			} catch (error) {
				console.error('WebSocket初始化错误:', error);
				this.wsAvailable = false;
				this.startSimulatedDataFeed();
			}
		},
		
		// 开始模拟数据流
		startSimulatedDataFeed() {
			console.log('启动模拟数据流');
			// 清除之前的定时器
			if (this.simulatedDataInterval) {
				clearInterval(this.simulatedDataInterval);
			}
			
			// 每5秒生成一次模拟数据
			this.simulatedDataInterval = setInterval(() => {
				const simulatedData = this.generateSimulatedData();
				this.handleRealTimeData(simulatedData);
			}, 5000);
		},
		
		// 生成模拟数据
		generateSimulatedData() {
			// 示例模拟数据结构
			return {
				type: 'marketData',
				timestamp: new Date().getTime(),
				data: {
					stockIndex: {
						value: Math.random() * 100 + 3000,
						change: (Math.random() - 0.5) * 20
					},
					volume: Math.floor(Math.random() * 1000000),
					mainForceFlow: (Math.random() - 0.5) * 10
				}
			};
		},
		
		// 处理实时数据
		handleRealTimeData(data) {
			// 根据数据类型更新相应的UI元素
			if (data.type === 'marketData') {
				// 更新市场数据
				this.updateMarketData(data.data);
			} else if (data.type === 'alertData') {
				// 处理预警数据
				this.handleAlertData(data.data);
			}
		},
		
		// 更新市场数据
		updateMarketData(data) {
			// 更新索引数据
			if (data.stockIndex) {
				this.indexData = {
					...this.indexData,
					value: data.stockIndex.value.toFixed(2),
					change: data.stockIndex.change.toFixed(2),
					changePercent: ((data.stockIndex.change / (data.stockIndex.value - data.stockIndex.change)) * 100).toFixed(2)
				};
			}
			
			// 更新成交量数据
			if (data.volume) {
				const formattedVolume = data.volume > 1000000 
					? (data.volume / 1000000).toFixed(2) + '百万' 
					: (data.volume / 1000).toFixed(0) + '千';
				
				this.volumeData = {
					...this.volumeData,
					value: formattedVolume
				};
			}
			
			// 更新主力资金流向
			if (data.mainForceFlow) {
				// 确保 capitalFlowHistory 已初始化
				if (!this.capitalFlowHistory) {
					this.capitalFlowHistory = [];
				}
				
				// 添加到主力资金流向历史数据
				this.capitalFlowHistory.push({
					time: new Date().toLocaleTimeString(),
					value: data.mainForceFlow
				});
				
				// 保留最近N个数据点
				const maxDataPoints = 20;
				if (this.capitalFlowHistory.length > maxDataPoints) {
					this.capitalFlowHistory = this.capitalFlowHistory.slice(this.capitalFlowHistory.length - maxDataPoints);
				}
				
				// 更新主力资金流向图表
				this.drawCapitalFlow();
			}
		},
		
		// 处理预警数据
		handleAlertData(data) {
			if (!data || !data.alerts) return;
			
			// 确保 alerts 已初始化
			if (!this.alerts) {
				this.alerts = [];
			}
			
			// 添加新预警到预警列表
			data.alerts.forEach(alert => {
				// 防止重复添加相同预警
				const existingAlertIndex = this.alerts.findIndex(a => a.id === alert.id);
				if (existingAlertIndex === -1) {
					this.alerts.push({
						...alert,
						time: new Date().toLocaleTimeString(),
						isNew: true
					});
					
					// 5秒后移除"新"标记
					setTimeout(() => {
						const index = this.alerts.findIndex(a => a.id === alert.id);
						if (index !== -1) {
							this.alerts[index].isNew = false;
							// 强制更新视图
							this.alerts = [...this.alerts];
						}
					}, 5000);
					
					// 如果开启了通知，显示消息提醒
					if (this.userSettings && this.userSettings.enableNotifications) {
						uni.showToast({
							title: alert.title,
							icon: 'none',
							duration: 3000
						});
					}
				}
			});
			
			// 限制预警列表最大长度
			if (this.alerts.length > 20) {
				this.alerts = this.alerts.slice(this.alerts.length - 20);
			}
		},
		
		// 风险指标颜色计算方法
		varColor(value) {
			if (value <= 2) return 'profit';
			if (value <= 4) return 'warn';
			return 'loss';
		},
		
		// 最大回撤颜色计算方法
		drawdownColor(value) {
			if (value <= 1) return 'profit';
			if (value <= 3) return 'warn';
			return 'loss';
		},
		
		// 刷新风险数据
		refreshRiskData() {
			// 模拟数据，实际应调用API
			this.riskMetrics = {
				var: (Math.random() * 5).toFixed(1),
				maxDrawdown: (Math.random() * 4).toFixed(1),
				volatility: (Math.random() * 20 + 5).toFixed(1)
			};
			
			// 更新风险图表
			this.drawRiskChart();
			
			uni.showToast({
				title: '风控指标已刷新',
				icon: 'success'
			});
		},
		
		// 绘制风险图表
		drawRiskChart() {
			// 使用2D渲染引擎
			const ctx = uni.createCanvasContext('riskChart', this);
			
			// 设置willReadFrequently属性 (解决HTML canvas性能警告)
			// Note: uni-app的canvas上下文可能不支持此属性，但为保险起见仍进行设置
			if (ctx.canvas && typeof ctx.canvas.getContext === 'function') {
				const context2d = ctx.canvas.getContext('2d', { willReadFrequently: true });
				if (context2d) {
					context2d.willReadFrequently = true;
				}
			} else if (ctx) {
				ctx.willReadFrequently = true;
			}
			
			const width = 300;
			const height = 200;
			
			// 清空画布
			ctx.clearRect(0, 0, width, height);
			
			// 生成模拟数据 - 风险指标变化
			const varData = [];
			const drawdownData = [];
			const volatilityData = [];
			
			for (let i = 0; i < 10; i++) {
				varData.push(Math.random() * 3 + 1);
				drawdownData.push(Math.random() * 2 + 0.5);
				volatilityData.push(Math.random() * 10 + 10);
			}
			
			// 绘制背景
			ctx.setFillStyle('#f8f8f8');
			ctx.fillRect(0, 0, width, height);
			
			// 绘制网格线
			ctx.beginPath();
			ctx.setStrokeStyle('#eeeeee');
			ctx.setLineWidth(1);
			for (let i = 0; i <= 5; i++) {
				const y = i * (height / 5);
				ctx.moveTo(0, y);
				ctx.lineTo(width, y);
			}
			ctx.stroke();
			
			// 绘制VAR值曲线
			ctx.beginPath();
			ctx.setStrokeStyle('#ff5252');
			ctx.setLineWidth(2);
			ctx.moveTo(0, height - (varData[0] / 5) * height);
			for (let i = 1; i < varData.length; i++) {
				ctx.lineTo(i * (width / (varData.length - 1)), height - (varData[i] / 5) * height);
			}
			ctx.stroke();
			
			// 绘制最大回撤曲线
			ctx.beginPath();
			ctx.setStrokeStyle('#ffd740');
			ctx.setLineWidth(2);
			ctx.moveTo(0, height - (drawdownData[0] / 5) * height);
			for (let i = 1; i < drawdownData.length; i++) {
				ctx.lineTo(i * (width / (drawdownData.length - 1)), height - (drawdownData[i] / 5) * height);
			}
			ctx.stroke();
			
			// 绘制波动率曲线
			ctx.beginPath();
			ctx.setStrokeStyle('#1989fa');
			ctx.setLineWidth(2);
			ctx.moveTo(0, height - (volatilityData[0] / 30) * height);
			for (let i = 1; i < volatilityData.length; i++) {
				ctx.lineTo(i * (width / (volatilityData.length - 1)), height - (volatilityData[i] / 30) * height);
			}
			ctx.stroke();
			
			// 绘制图例
			ctx.setFillStyle('#333');
			ctx.setFontSize(12);
			
			// VAR值图例
			ctx.beginPath();
			ctx.setStrokeStyle('#ff5252');
			ctx.setLineWidth(2);
			ctx.moveTo(10, 20);
			ctx.lineTo(30, 20);
			ctx.stroke();
			ctx.fillText('VAR值', 35, 24);
			
			// 最大回撤图例
			ctx.beginPath();
			ctx.setStrokeStyle('#ffd740');
			ctx.setLineWidth(2);
			ctx.moveTo(80, 20);
			ctx.lineTo(100, 20);
			ctx.stroke();
			ctx.fillText('最大回撤', 105, 24);
			
			// 波动率图例
			ctx.beginPath();
			ctx.setStrokeStyle('#1989fa');
			ctx.setLineWidth(2);
			ctx.moveTo(170, 20);
			ctx.lineTo(190, 20);
			ctx.stroke();
			ctx.fillText('波动率', 195, 24);
			
			// 提交绘制
			ctx.draw();
		},
		
		// 显示可操作金额设置弹窗
		showAmountModal() {
			// 先将当前的可用资金保存到全局数据中
			const app = getApp();
			if (app.globalData) {
				app.globalData.availableCash = this.availableCash;
			}
			
			// 导航到设置页面
			uni.navigateTo({
				url: `/pages/settings/amount?current=${this.operableAmount.replace(/,/g, '')}`
			});
		},
		
		// 获取进度条值
		getProgressValue(returnValue) {
			// 将收益率映射到0-100的范围
			return Math.min(Math.max(returnValue + 10, 0), 100)
		},
		
		// 获取收益率颜色
		getReturnColor(returnValue) {
			if (returnValue >= 10) return '#f5222d'
			if (returnValue >= 5) return '#fa8c16'
			if (returnValue >= 0) return '#52c41a'
			return '#1989fa'
		},
		
		drawCapitalFlow() {
			// 如果没有数据，不绘制
			if (!this.capitalFlowHistory || this.capitalFlowHistory.length === 0) {
				console.log('No capital flow history data available');
				return;
			}
			
			// 使用2D渲染引擎
			const ctx = uni.createCanvasContext('capitalFlowChart', this);
			if (!ctx) {
				console.error('Failed to create canvas context for capitalFlowChart');
				return;
			}
			
			// 添加willReadFrequently属性，解决Canvas警告
			if (ctx.canvas && typeof ctx.canvas.getContext === 'function') {
				try {
					const context2d = ctx.canvas.getContext('2d', { willReadFrequently: true });
					if (context2d) {
						context2d.willReadFrequently = true;
					}
				} catch (error) {
					console.log('Setting willReadFrequently not supported:', error);
				}
			} else if (ctx) {
				ctx.willReadFrequently = true;
			}
			
			const width = 300;
			const height = 200;
			const padding = 30;
			
			// 清空画布
			ctx.clearRect(0, 0, width, height);
			
			// 获取历史数据
			const historyData = this.capitalFlowHistory;
			
			// 如果没有数据，显示无数据提示
			if (!historyData || historyData.length === 0) {
				ctx.setFillStyle('#999');
				ctx.setTextAlign('center');
				ctx.setFontSize(14);
				ctx.fillText('暂无数据', width / 2, height / 2);
				ctx.draw();
				return;
			}
			
			// 绘制背景
			ctx.setFillStyle('#f8f8f8');
			ctx.fillRect(0, 0, width, height);
			
			// 获取Y轴的最大和最小值
			let maxValue = -Infinity;
			let minValue = Infinity;
			historyData.forEach(item => {
				maxValue = Math.max(maxValue, item.value);
				minValue = Math.min(minValue, item.value);
			});
			
			// 确保有一定的边距
			const range = Math.max(maxValue - minValue, 2);
			maxValue = maxValue + range * 0.1;
			minValue = minValue - range * 0.1;
			
			// 绘制水平网格线和Y轴标签
			ctx.beginPath();
			ctx.setStrokeStyle('#eeeeee');
			ctx.setLineWidth(1);
			ctx.setFillStyle('#666');
			ctx.setFontSize(10);
			ctx.setTextAlign('right');
			
			const yGridCount = 5;
			for (let i = 0; i <= yGridCount; i++) {
				const y = padding + (height - padding * 2) * (1 - i / yGridCount);
				const value = (minValue + (maxValue - minValue) * (i / yGridCount)).toFixed(1);
				
				// 绘制网格线
				ctx.moveTo(padding, y);
				ctx.lineTo(width - padding, y);
				
				// 绘制Y轴标签
				ctx.fillText(value + '%', padding - 5, y + 3);
			}
			ctx.stroke();
			
			// 绘制X轴标签
			ctx.setTextAlign('center');
			const xStep = (width - padding * 2) / (historyData.length - 1);
			let labelIndex = 0;
			// 仅绘制部分标签以避免拥挤
			const labelStep = Math.ceil(historyData.length / 6);
			
			historyData.forEach((item, index) => {
				if (index % labelStep === 0 || index === historyData.length - 1) {
					const x = padding + index * xStep;
					ctx.fillText(item.time, x, height - padding + 15);
					
					// 绘制垂直网格线
					ctx.beginPath();
					ctx.setStrokeStyle('#eeeeee');
					ctx.moveTo(x, padding);
					ctx.lineTo(x, height - padding);
					ctx.stroke();
					
					labelIndex++;
				}
			});
			
			// 绘制0值的水平线
			if (minValue < 0 && maxValue > 0) {
				const zeroY = padding + (height - padding * 2) * (1 - (0 - minValue) / (maxValue - minValue));
				ctx.beginPath();
				ctx.setStrokeStyle('#dddddd');
				ctx.setLineWidth(1.5);
				ctx.moveTo(padding, zeroY);
				ctx.lineTo(width - padding, zeroY);
				ctx.stroke();
			}
			
			// 绘制主力资金流向曲线
			ctx.beginPath();
			ctx.setStrokeStyle('#1989fa');
			ctx.setLineWidth(2.5);
			
			historyData.forEach((item, index) => {
				const x = padding + index * xStep;
				const y = padding + (height - padding * 2) * (1 - (item.value - minValue) / (maxValue - minValue));
				
				if (index === 0) {
					ctx.moveTo(x, y);
				} else {
					ctx.lineTo(x, y);
				}
			});
			ctx.stroke();
			
			// 绘制曲线下方的渐变填充
			const lastItem = historyData[historyData.length - 1];
			const lastX = padding + (historyData.length - 1) * xStep;
			const lastY = padding + (height - padding * 2) * (1 - (lastItem.value - minValue) / (maxValue - minValue));
			const zeroY = padding + (height - padding * 2) * (1 - (0 - minValue) / (maxValue - minValue));
			const zeroYClamped = Math.min(height - padding, Math.max(padding, zeroY));
			
			// 创建渐变
			const gradient = ctx.createLinearGradient(0, padding, 0, height - padding);
			if (lastItem.value >= 0) {
				gradient.addColorStop(0, 'rgba(25, 137, 250, 0.3)');
				gradient.addColorStop(1, 'rgba(25, 137, 250, 0.05)');
			} else {
				gradient.addColorStop(0, 'rgba(245, 34, 45, 0.05)');
				gradient.addColorStop(1, 'rgba(245, 34, 45, 0.3)');
			}
			
			// 绘制渐变填充
			ctx.beginPath();
			historyData.forEach((item, index) => {
				const x = padding + index * xStep;
				const y = padding + (height - padding * 2) * (1 - (item.value - minValue) / (maxValue - minValue));
				
				if (index === 0) {
					ctx.moveTo(x, y);
				} else {
					ctx.lineTo(x, y);
				}
			});
			ctx.lineTo(lastX, zeroYClamped);
			ctx.lineTo(padding, zeroYClamped);
			ctx.closePath();
			ctx.setFillStyle(gradient);
			ctx.fill();
			
			// 绘制数据点
			historyData.forEach((item, index) => {
				const x = padding + index * xStep;
				const y = padding + (height - padding * 2) * (1 - (item.value - minValue) / (maxValue - minValue));
				
				ctx.beginPath();
				ctx.setFillStyle('#fff');
				ctx.arc(x, y, 3, 0, Math.PI * 2);
				ctx.fill();
				
				ctx.beginPath();
				ctx.setStrokeStyle('#1989fa');
				ctx.setLineWidth(1.5);
				ctx.arc(x, y, 3, 0, Math.PI * 2);
				ctx.stroke();
			});
			
			// 绘制标题
			ctx.setFillStyle('#333');
			ctx.setTextAlign('left');
			ctx.setFontSize(12);
			ctx.fillText('主力资金流向趋势', padding, 15);
			
			// 显示最新值
			ctx.setTextAlign('right');
			ctx.setFontSize(12);
			ctx.fillText('最新: ' + lastItem.value.toFixed(2) + '%', width - padding, 15);
			
			// 提交绘制
			ctx.draw();
		},
		setTradeTimeMode(mode) {
			// 如果T+0已开启且尝试切换到盘中选股，阻止操作
			if (this.t0Enabled && mode === 'INTRADAY') {
				uni.showToast({
					title: 'T+0模式下只能使用尾盘选股',
					icon: 'none'
				})
				return
			}
			
			this.tradeTimeMode = mode
			
			if (mode === 'EOD') {
				// 如果切换到尾盘选股，检查并加载尾盘选股数据
				this.checkAndLoadEodStocks()
				
				uni.showToast({
					title: '已切换到尾盘选股模式',
					icon: 'none'
				})
			} else {
				uni.showToast({
					title: '已切换到盘中选股模式',
					icon: 'none'
				})
			}
		},
		toggleT0Mode(e) {
			this.t0Enabled = e.detail.value
			
			if (this.t0Enabled) {
				// 如果开启T+0，自动切换到尾盘选股模式
				this.tradeTimeMode = 'EOD'
				
				// 加载T+0股票池
				this.checkAndLoadEodStocks()
				
				// 显示自定义提示框
				this.showT0Toast = true
				setTimeout(() => {
					this.showT0Toast = false
				}, 2000)
			} else {
				uni.showToast({
					title: '已切换为T+1交易模式',
					icon: 'none'
				})
			}
		},
		// 检查并加载尾盘选股数据
		checkAndLoadEodStocks() {
			const now = new Date()
			const today = now.toISOString().split('T')[0] // 当前日期，如 "2023-06-08"
			
			// 获取已保存的尾盘选股数据
			const savedEodData = uni.getStorageSync('eodStocksData')
			
			if (savedEodData && savedEodData.date === today && savedEodData.stocks) {
				// 如果今天已经有尾盘选股数据，直接使用
				this.t0StocksPool = savedEodData.stocks
				this.lastEodUpdateTime = savedEodData.updateTime
				
				console.log('已加载今日尾盘选股数据', this.lastEodUpdateTime)
			} else if (this.isEodTime) {
				// 如果是尾盘时间，获取新的尾盘选股数据
				this.fetchEodStocksData()
			} else {
				// 如果不是尾盘时间，显示提示
				uni.showToast({
					title: '尾盘选股将在14:30后更新',
					icon: 'none'
				})
			}
		},
		
		// 获取尾盘选股数据
		fetchEodStocksData() {
			// 实际应用中，这里应该调用API获取尾盘选股推荐
			// 这里使用模拟数据演示
			
			uni.showLoading({
				title: '获取尾盘数据'
			})
			
			// 模拟API请求延迟
			setTimeout(() => {
				// 生成模拟的尾盘选股数据
				const eodStocks = [
					{
						code: 'SH600519',
						name: '贵州茅台',
						momentum: 0.88,
						valuation: 0.79,
						liquidity: 0.75,
						sentiment: 0.95,
						composite: 0.84,
						t0Signal: '买入',
						t0Reason: '尾盘资金流入强劲，短线有望冲高'
					},
					{
						code: 'SH600036',
						name: '招商银行',
						momentum: 0.79,
						valuation: 0.92,
						liquidity: 0.85,
						sentiment: 0.80,
						composite: 0.83,
						t0Signal: '买入',
						t0Reason: '尾盘突破30日均线，量能配合'
					},
					{
						code: 'SZ000858',
						name: '五粮液',
						momentum: 0.82,
						valuation: 0.84,
						liquidity: 0.78,
						sentiment: 0.86,
						composite: 0.82,
						t0Signal: '买入',
						t0Reason: '尾盘放量上攻，日K形成小阳线'
					}
				]
				
				const now = new Date()
				const today = now.toISOString().split('T')[0]
				const updateTime = now.toLocaleTimeString()
				
				// 保存尾盘选股数据
				this.t0StocksPool = eodStocks
				this.lastEodUpdateTime = updateTime
				
				// 保存到本地存储
				uni.setStorageSync('eodStocksData', {
					date: today,
					updateTime: updateTime,
					stocks: eodStocks
				})
				
				uni.hideLoading()
				uni.showToast({
					title: '尾盘选股数据已更新',
					icon: 'success'
				})
			}, 1500)
		},
		// AI分析界面专用导航方法
		openAIAnalytics() {
			console.log('打开AI智能分析页面');
			
			// 显示加载提示
			uni.showLoading({
				title: '正在打开AI分析'
			});
			
			// 尝试使用多种导航方式
			try {
				// 方法1: 使用navigateTo (普通页面跳转)
				uni.navigateTo({
					url: '/pages/agent-analysis/index',
					success: (res) => {
						console.log('成功打开AI分析页面 (navigateTo)');
						uni.hideLoading();
					},
					fail: (err) => {
						console.error('使用navigateTo打开AI分析失败:', err);
						
						// 方法2: 使用switchTab (如果是tabBar页面)
						uni.switchTab({
							url: '/pages/agent-analysis/index',
							success: (res) => {
								console.log('成功打开AI分析页面 (switchTab)');
								uni.hideLoading();
							},
							fail: (err) => {
								console.error('使用switchTab打开AI分析失败:', err);
								
								// 方法3: 使用redirectTo
								uni.redirectTo({
									url: '/pages/agent-analysis/index',
									success: (res) => {
										console.log('成功打开AI分析页面 (redirectTo)');
										uni.hideLoading();
									},
									fail: (redirectErr) => {
										console.error('使用redirectTo打开AI分析失败:', redirectErr);
										
										// 方法4: 使用reLaunch
										uni.reLaunch({
											url: '/pages/agent-analysis/index',
											success: (res) => {
												console.log('成功打开AI分析页面 (reLaunch)');
												uni.hideLoading();
											},
											fail: (reLaunchErr) => {
												console.error('所有导航方法都失败:', reLaunchErr);
												uni.hideLoading();
												
												// 显示错误提示
												uni.showToast({
													title: 'AI分析界面打开失败',
													icon: 'none',
													duration: 3000
												});
											}
										});
									}
								});
							}
						});
					}
				});
			} catch (e) {
				console.error('导航过程出现异常:', e);
				uni.hideLoading();
				uni.showToast({
					title: '打开AI分析失败',
					icon: 'none'
				});
			}
		}
	},
	onLoad() {
		// 初始化方法
		this.fetchMainFundData();
		this.refreshRiskData();
		
		// 初始化WebSocket连接
		this.initWebSocket();
		
		// 设置自动刷新定时器 (每60秒刷新一次)
		this.refreshTimer = setInterval(() => {
			this.fetchMainFundData();
		}, 60000);
		
		// 初始加载时检查是否需要加载尾盘选股数据
		if (this.tradeTimeMode === 'EOD') {
			this.checkAndLoadEodStocks()
		}
		
		// 设置定时器，定期检查是否需要更新尾盘选股数据
		this.eodCheckTimer = setInterval(() => {
			if (this.tradeTimeMode === 'EOD' && this.isEodTime) {
				// 如果是尾盘选股模式且当前是尾盘时间，自动更新数据
				this.fetchEodStocksData()
			}
		}, 300000) // 每5分钟检查一次
	},
	onShow() {
		// 从全局数据中获取可操作金额
		const app = getApp();
		if (app.globalData && app.globalData.operableAmount) {
			this.operableAmount = app.globalData.operableAmount;
		}
	},
	onUnload() {
		// 页面卸载时清除定时器
		if (this.refreshTimer) {
			clearInterval(this.refreshTimer);
			this.refreshTimer = null;
		}
		
		// 关闭WebSocket连接
		if (this.ws && this.wsAvailable) {
			try {
				this.ws.close(1000);
			} catch (error) {
				console.error('关闭WebSocket时发生错误:', error);
			}
			this.ws = null;
		}
		
		// 清除尾盘选股检查定时器
		if (this.eodCheckTimer) {
			clearInterval(this.eodCheckTimer)
			this.eodCheckTimer = null
		}
	}
}
</script>

<style>
.container {
	padding: 30rpx;
	background-color: #f5f5f5;
}

.header {
	margin-bottom: 40rpx;
	padding: 20rpx;
	background: linear-gradient(135deg, #1989fa, #0056b3);
	border-radius: 16rpx;
	color: #fff;
	box-shadow: 0 4rpx 12rpx rgba(25, 137, 250, 0.3);
}

.main-title {
	font-size: 40rpx;
	font-weight: bold;
	margin-bottom: 10rpx;
	display: block;
}

.subtitle {
	font-size: 24rpx;
	opacity: 0.9;
	display: block;
}

.section {
	margin-bottom: 30rpx;
	background-color: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
}

.section-header {
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
	border-bottom: 1px solid #f0f0f0;
	padding-bottom: 16rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.refresh-btn, .more-btn {
	font-size: 24rpx;
	color: #1989fa;
	background-color: rgba(25, 137, 250, 0.1);
	padding: 6rpx 16rpx;
	border-radius: 30rpx;
}

/* 市场指数样式 */
.market-indices {
	display: flex;
	flex-direction: row;
	flex-wrap: wrap;
	justify-content: space-between;
}

.index-card {
	width: 48%;
	background-color: #f9f9f9;
	border-radius: 12rpx;
	padding: 20rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.03);
}

.index-header {
	margin-bottom: 10rpx;
}

.index-name {
	font-size: 28rpx;
	color: #666;
	margin-bottom: 6rpx;
	display: block;
}

.index-value {
	font-size: 36rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 6rpx;
	display: block;
}

.index-change {
	font-size: 28rpx;
	font-weight: bold;
	display: block;
}

.increase {
	color: #f5222d;
}

.decrease {
	color: #52c41a;
}

/* 主力资金监控 */
.fund-flow-section {
	background: linear-gradient(to bottom, #fff, #f8f8ff);
}

.fund-flow-content {
	display: flex;
	flex-direction: column;
}

.fund-flow-chart {
	height: 300rpx;
	width: 100%;
	margin-bottom: 20rpx;
}

.chart-container {
	width: 100%;
	height: 100%;
}

.fund-flow-info {
	width: 100%;
}

@media screen and (min-width: 768px) {
	.fund-flow-content {
		flex-direction: row;
	}
	
	.fund-flow-chart {
		height: 400rpx;
		width: 70%;
		margin-right: 20rpx;
		margin-bottom: 0;
	}
	
	.fund-flow-info {
		width: 30%;
	}
}

.abnormal-signal {
	display: flex;
	flex-direction: row;
	align-items: center;
	background-color: rgba(0,0,0,0.03);
	padding: 16rpx;
	border-radius: 8rpx;
	margin-bottom: 20rpx;
}

.signal-label {
	font-size: 28rpx;
	color: #666;
	margin-right: 10rpx;
}

.signal-value {
	font-size: 28rpx;
	font-weight: bold;
}

.signal-value.normal {
	color: #52c41a;
}

.signal-value.warning {
	color: #faad14;
}

.signal-value.danger {
	color: #f5222d;
}

.fund-flow-stats {
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	align-items: center;
}

.stat-item {
	flex: 1;
	text-align: center;
}

.stat-label {
	font-size: 24rpx;
	color: #666;
	margin-bottom: 6rpx;
	display: block;
}

.stat-value {
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
	display: block;
}

/* 自动交易平台 */
.auto-trade-highlight {
	background: linear-gradient(to bottom, #fff, #f0f8ff);
	border-left: 6rpx solid #1989fa;
}

.auto-trade-overview {
	padding: 10rpx;
}

.trade-status-box {
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	align-items: center;
	background-color: #f9f9f9;
	padding: 20rpx;
	border-radius: 12rpx;
	margin-bottom: 20rpx;
}

.status-info {
	display: flex;
	flex-direction: column;
}

.status-label {
	font-size: 26rpx;
	color: #666;
	margin-bottom: 6rpx;
}

.status-value {
	font-size: 32rpx;
	font-weight: bold;
}

.status-active {
	color: #52c41a;
}

.status-inactive {
	color: #999;
}

.auto-trade-toggle {
	display: flex;
	flex-direction: column;
	align-items: center;
}

.toggle-label {
	font-size: 24rpx;
	color: #666;
	margin-bottom: 6rpx;
}

.trade-mode-selection {
	margin-bottom: 20rpx;
}

.mode-title {
	font-size: 28rpx;
	color: #333;
	margin-bottom: 16rpx;
	display: block;
}

.mode-options {
	display: flex;
	flex-direction: row;
	justify-content: space-between;
}

.mode-option {
	flex: 1;
	background-color: #f9f9f9;
	padding: 16rpx;
	text-align: center;
	margin: 0 10rpx;
	border-radius: 8rpx;
}

.mode-option:first-child {
	margin-left: 0;
}

.mode-option:last-child {
	margin-right: 0;
}

.mode-option.active {
	background-color: #e6f7ff;
	border: 1px solid #91d5ff;
}

.mode-icon {
	font-size: 36rpx;
	margin-bottom: 6rpx;
	display: block;
}

.mode-name {
	font-size: 24rpx;
	color: #333;
}

.trade-metrics {
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	margin-bottom: 20rpx;
	background-color: #f9f9f9;
	padding: 16rpx;
	border-radius: 8rpx;
}

.metric-item {
	flex: 1;
	text-align: center;
}

.metric-label {
	font-size: 24rpx;
	color: #666;
	margin-bottom: 6rpx;
	display: block;
}

.metric-value {
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
	display: block;
}

.profit {
	color: #ff0000 !important;
	font-weight: bold;
}

.loss {
	color: #00cc00 !important;
	font-weight: bold;
}

.quick-actions {
	display: flex;
	flex-direction: row;
	flex-wrap: wrap;
}

.action-btn {
	flex: 1;
	margin: 0 10rpx;
	background-color: #1989fa;
	color: #fff;
	font-size: 28rpx;
	padding: 16rpx 0;
	text-align: center;
	border-radius: 8rpx;
	min-width: 180rpx;
}

.action-btn.secondary {
	background-color: #f0f0f0;
	color: #666;
}

/* 持仓概览 */
.portfolio-summary {
	background-color: #f9f9f9;
	border-radius: 12rpx;
	padding: 20rpx;
}

.summary-row {
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	align-items: center;
	padding: 16rpx 0;
	border-bottom: 1px solid #f0f0f0;
}

.summary-row:last-child {
	border-bottom: none;
}

.summary-value {
	font-weight: bold;
	color: #333;
}

.editable-amount {
	display: flex;
	flex-direction: row;
	align-items: center;
}

.edit-btn {
	margin-left: 10rpx;
	color: #1989fa;
	font-size: 24rpx;
}

/* 风控指标 */
.risk-dashboard {
	background: linear-gradient(to bottom, #fff, #fff9f9);
}

.risk-metrics {
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	margin-bottom: 20rpx;
}

.metric-card {
	flex: 1;
	background-color: #f9f9f9;
	padding: 16rpx;
	margin: 0 10rpx;
	border-radius: 8rpx;
	text-align: center;
}

.metric-card:first-child {
	margin-left: 0;
}

.metric-card:last-child {
	margin-right: 0;
}

.risk-chart {
	height: 200px;
}

/* 智能选股推荐 */
.stock-picking-results {
	background-color: #f9f9f9;
	border-radius: 12rpx;
	padding: 20rpx;
    overflow: hidden;
    width: 100%;
    box-sizing: border-box;
}

.filter-controls {
	display: flex;
	flex-direction: column;
	align-items: flex-start;
}

.insight-date {
	font-size: 24rpx;
	color: #999;
}

.insight-tag {
	font-size: 24rpx;
	color: #fff;
	padding: 4rpx 12rpx;
	border-radius: 4rpx;
}

/* 策略效果对比 */
.strategy-comparison {
	background: linear-gradient(to bottom, #fff, #f0f8ff);
}

.strategy-metrics {
	display: flex;
	flex-direction: column;
}

.metric-progress {
	margin-top: 10rpx;
}

/* 修复T+0模式通知样式 */
.t0-notification {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 20rpx;
    text-align: center;
    border-radius: 10rpx 10rpx 0 0;
    z-index: 999;
    font-size: 28rpx;
    font-weight: bold;
}

/* 添加T+0交易模式弹窗样式 */
.t0-mode-notification {
    background-color: #333;
    color: #fff;
    padding: 10rpx 20rpx;
    border-radius: 8rpx;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 999;
    font-size: 28rpx;
    text-align: center;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.3);
}

.t0-active-toast {
    background-color: #000000;
    color: white;
    border-radius: 10rpx;
    padding: 20rpx 40rpx;
    text-align: center;
    font-size: 32rpx;
    font-weight: bold;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.5);
}

.t0-toast-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 999;
}

/* 修改当前策略过滤器样式 */
.picker {
    background-color: #f0f0f0;
    padding: 12rpx 20rpx;
    border-radius: 8rpx;
    font-size: 26rpx;
    color: #333;
    max-width: 300rpx;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.factor-score-table {
    width: 100%;
    overflow-x: auto;
    white-space: nowrap;
}

.eod-notification {
    width: 100%;
    box-sizing: border-box;
    padding: 10rpx;
    background-color: #f9f9f9;
    border-radius: 8rpx;
    margin-bottom: 10rpx;
    font-size: 24rpx;
}

.eod-status {
    font-size: 24rpx;
    color: #666;
}

.eod-status.active {
    color: #52c41a;
}

.eod-status.inactive {
    color: #999;
}

/* 嵌入式AI分析组件样式 */
.embedded-ai-analytics {
    background-color: #f9f9f9;
    border-radius: 12rpx;
    padding: 20rpx;
    margin-bottom: 20rpx;
    max-height: 800rpx;
    overflow-y: auto;
}

.loading-indicator {
    background-color: #e6f7ff;
    border: 1px solid #1890ff;
    border-radius: 8rpx;
    padding: 16rpx;
    margin-bottom: 20rpx;
    text-align: center;
    font-weight: bold;
    color: #1890ff;
}
</style>
