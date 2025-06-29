<template>
    <view class="container">
        <view class="header">
            <text class="title">自动交易平台</text>
            <text class="subtitle">管理自动交易策略和配置</text>
        </view>
        
        <!-- 系统状态 -->
        <view class="section">
            <view class="section-header">
                <text class="section-title">系统状态</text>
                <view class="status-badge" :class="autoTradeEnabled ? 'active' : 'inactive'">
                    {{ autoTradeEnabled ? '运行中' : '已停止' }}
                </view>
            </view>
            
            <view class="control-panel">
                <view class="status-row">
                    <text class="status-label">自动交易</text>
                    <switch :checked="autoTradeEnabled" @change="toggleAutoTrading" color="#1989fa"/>
                </view>
                
                <view class="status-row">
                    <text class="status-label">交易模式</text>
                    <picker @change="changeTradeMode" :value="tradeModeIndex" :range="tradeModes">
                        <view class="mode-picker">{{ tradeModes[tradeModeIndex] }}</view>
                    </picker>
                </view>
                
                <view class="status-row">
                    <text class="status-label">可用资金</text>
                    <text class="status-value">¥{{ availableCash }}</text>
                </view>
                
                <view class="status-row">
                    <text class="status-label">可操作金额</text>
                    <view class="editable-value">
                        <text class="status-value">¥{{ operableAmount }}</text>
                        <text class="edit-btn" @click="navigateToAmount">调整</text>
                    </view>
                </view>
            </view>
        </view>
        
        <!-- 交易策略配置 -->
        <view class="section">
            <view class="section-header">
                <text class="section-title">交易策略配置</text>
                <text class="edit-btn" @click="openStrategySettings">编辑</text>
            </view>
            
            <view class="strategy-config">
                <view class="config-row">
                    <text class="config-label">最大单笔交易</text>
                    <text class="config-value">¥{{ formatNumber(strategyConfig.maxSingleTradeAmount) }}</text>
                </view>
                
                <view class="config-row">
                    <text class="config-label">每日最大交易次数</text>
                    <text class="config-value">{{ strategyConfig.maxDailyTrades }}次</text>
                </view>
                
                <view class="config-row">
                    <text class="config-label">止损比例</text>
                    <text class="config-value">{{ strategyConfig.stopLossPercent }}%</text>
                </view>
                
                <view class="config-row">
                    <text class="config-label">止盈比例</text>
                    <text class="config-value">{{ strategyConfig.takeProfitPercent }}%</text>
                </view>
                
                <view class="config-row">
                    <text class="config-label">加仓步长</text>
                    <text class="config-value">{{ strategyConfig.increaseStep * 100 }}%</text>
                </view>
                
                <view class="config-row">
                    <text class="config-label">减仓步长</text>
                    <text class="config-value">{{ strategyConfig.reduceStep * 100 }}%</text>
                </view>
            </view>
        </view>
        
        <!-- 交易统计 -->
        <view class="section">
            <view class="section-header">
                <text class="section-title">交易统计</text>
                <view class="ai-badge" @click="showAILearningInfo">
                    <text class="ai-badge-text">AI{{aiOptimized ? '已优化' : '学习中'}}</text>
                </view>
            </view>
            
            <view class="stats-row">
                <view class="stat-item">
                    <text class="stat-label">总收益</text>
                    <text :class="['stat-value', totalProfit >= 0 ? 'profit' : 'loss']">
                        {{ totalProfit >= 0 ? '+' : '' }}{{ totalProfit }}元
                    </text>
                </view>
                <view class="stat-item">
                    <text class="stat-label">胜率</text>
                    <text class="stat-value">{{ winRate }}%</text>
                </view>
                <view class="stat-item">
                    <text class="stat-label">完成交易</text>
                    <text class="stat-value">{{ completedTrades }}</text>
                </view>
                <view class="stat-item">
                    <text class="stat-label">交易中</text>
                    <text class="stat-value">{{ activeTrades }}</text>
                </view>
            </view>
        </view>
        
        <!-- 最近交易 -->
        <view class="section">
            <view class="section-header">
                <text class="section-title">最近交易</text>
                <text class="more-btn" @click="navigateToHistory">查看更多</text>
            </view>
            
            <view class="trades-list">
                <view class="no-data" v-if="recentTrades.length === 0">
                    <text class="no-data-text">暂无交易记录</text>
                </view>
                
                <view class="trade-item" v-for="(trade, index) in recentTrades" :key="index">
                    <view class="trade-info">
                        <text class="trade-time">{{ trade.time }}</text>
                        <text class="trade-stock">{{ trade.stockName }}({{ trade.stockCode }})</text>
                    </view>
                    
                    <view class="trade-details">
                        <view class="trade-type" :class="trade.type">
                            <text class="type-text">{{ trade.type === 'buy' ? '买入' : '卖出' }}</text>
                        </view>
                        <view class="trade-amount">
                            <text class="amount-value">{{ trade.amount }}股</text>
                            <text class="price-value">¥{{ trade.price }}</text>
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
            // 系统状态
            autoTradeEnabled: false,
            tradeModes: ['保守型', '平衡型', '激进型'],
            tradeModeIndex: 1,
            availableCash: '27,230.00',
            operableAmount: '10,000.00',
            
            // 策略配置
            strategyConfig: {
                maxSingleTradeAmount: 5000.00,
                maxDailyTrades: 5,
                stopLossPercent: 8,
                takeProfitPercent: 15,
                increaseStep: 0.1,
                reduceStep: 0.15
            },
            
            // 交易统计
            dateRanges: ['今日', '本周', '本月', '全部'],
            dateRangeIndex: 1,
            tradeStats: {
                totalTrades: 28,
                profitTrades: 18,
                lossTrades: 10,
                winRate: 64,
                totalProfit: 3265.50,
                returnRate: 8.2
            },
            
            // 最近交易
            recentTrades: [
                {
                    time: '2023-06-08 14:32',
                    stockName: '贵州茅台',
                    stockCode: 'SH600519',
                    type: 'buy',
                    amount: 2,
                    price: 1789.50
                },
                {
                    time: '2023-06-08 10:15',
                    stockName: '中国平安',
                    stockCode: 'SH601318',
                    type: 'sell',
                    amount: 200,
                    price: 48.32
                },
                {
                    time: '2023-06-07 15:45',
                    stockName: '五粮液',
                    stockCode: 'SZ000858',
                    type: 'buy',
                    amount: 50,
                    price: 168.75
                }
            ],
            
            // 交易统计数据
            totalProfit: 1258.75,
            winRate: 68,
            completedTrades: 12,
            activeTrades: 3,
            aiOptimized: true
        }
    },
    onLoad() {
        // 加载自动交易数据
        this.loadAutoTradeData();
    },
    methods: {
        // 切换自动交易状态
        toggleAutoTrading(e) {
            this.autoTradeEnabled = e.detail.value;
            uni.showToast({
                title: this.autoTradeEnabled ? '自动交易已启用' : '自动交易已停止',
                icon: 'none'
            });
            
            // 在实际应用中应调用API更新状态
        },
        
        // 改变交易模式
        changeTradeMode(e) {
            this.tradeModeIndex = e.detail.value;
            const modeName = this.tradeModes[this.tradeModeIndex];
            
            uni.showToast({
                title: `已切换为${modeName}模式`,
                icon: 'none'
            });
            
            // 在实际应用中应加载相应的策略配置
            this.loadStrategyConfigByMode();
        },
        
        // 前往金额设置页面
        navigateToAmount() {
            uni.navigateTo({
                url: '/pages/settings/amount'
            });
        },
        
        // 打开策略设置
        openStrategySettings() {
            uni.showToast({
                title: '策略设置功能开发中',
                icon: 'none'
            });
            
            // 实际应跳转到策略设置页面
        },
        
        // 改变日期范围
        changeDateRange(e) {
            this.dateRangeIndex = e.detail.value;
            
            // 在实际应用中应加载相应日期范围的数据
            this.loadTradeStats();
        },
        
        // 前往交易历史页面
        navigateToHistory() {
            uni.navigateTo({
                url: '/pages/trade-history/index'
            });
        },
        
        // 加载自动交易数据
        loadAutoTradeData() {
            // 实际应用中应从API获取数据
            // 这里使用模拟数据
            setTimeout(() => {
                // 模拟加载完成
            }, 500);
        },
        
        // 加载策略配置
        loadStrategyConfigByMode() {
            // 根据当前选择的模式加载相应配置
            const modeConfigs = {
                0: { // 保守型
                    maxSingleTradeAmount: 3000.00,
                    maxDailyTrades: 3,
                    stopLossPercent: 5,
                    takeProfitPercent: 10,
                    increaseStep: 0.05,
                    reduceStep: 0.1
                },
                1: { // 平衡型
                    maxSingleTradeAmount: 5000.00,
                    maxDailyTrades: 5,
                    stopLossPercent: 8,
                    takeProfitPercent: 15,
                    increaseStep: 0.1,
                    reduceStep: 0.15
                },
                2: { // 激进型
                    maxSingleTradeAmount: 10000.00,
                    maxDailyTrades: 8,
                    stopLossPercent: 12,
                    takeProfitPercent: 25,
                    increaseStep: 0.2,
                    reduceStep: 0.25
                }
            };
            
            this.strategyConfig = modeConfigs[this.tradeModeIndex];
        },
        
        // 加载交易统计
        loadTradeStats() {
            // 实际应用中应从API获取数据
            // 这里使用模拟数据
            const statsData = {
                0: { // 今日
                    totalTrades: 8,
                    profitTrades: 5,
                    lossTrades: 3,
                    winRate: 62,
                    totalProfit: 865.50,
                    returnRate: 2.3
                },
                1: { // 本周
                    totalTrades: 28,
                    profitTrades: 18,
                    lossTrades: 10,
                    winRate: 64,
                    totalProfit: 3265.50,
                    returnRate: 8.2
                },
                2: { // 本月
                    totalTrades: 75,
                    profitTrades: 48,
                    lossTrades: 27,
                    winRate: 64,
                    totalProfit: 8765.20,
                    returnRate: 15.4
                },
                3: { // 全部
                    totalTrades: 186,
                    profitTrades: 112,
                    lossTrades: 74,
                    winRate: 60,
                    totalProfit: 22680.50,
                    returnRate: 28.6
                }
            };
            
            this.tradeStats = statsData[this.dateRangeIndex];
        },
        
        // 格式化数字
        formatNumber(num) {
            return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        },
        
        // 导航到AI学习分析页面
        showAILearningInfo() {
            uni.navigateTo({
                url: '/pages/agent-analysis/learning/index'
            });
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
    margin-bottom: 30rpx;
}

.title {
    font-size: 36rpx;
    font-weight: bold;
    color: #333;
}

.subtitle {
    font-size: 28rpx;
    color: #666;
    margin-top: 10rpx;
}

.section {
    margin-bottom: 30rpx;
    background-color: #fff;
    border-radius: 12rpx;
    padding: 20rpx;
    box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
}

.section-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
    padding-bottom: 16rpx;
    border-bottom: 1px solid #f0f0f0;
}

.section-title {
    font-size: 32rpx;
    font-weight: bold;
    color: #333;
}

.status-badge {
    padding: 6rpx 20rpx;
    border-radius: 20rpx;
    font-size: 24rpx;
}

.status-badge.active {
    background-color: #e6f7ff;
    color: #1890ff;
}

.status-badge.inactive {
    background-color: #f5f5f5;
    color: #999;
}

.control-panel, .strategy-config {
    background-color: #f9f9f9;
    border-radius: 8rpx;
    padding: 20rpx;
}

.status-row, .config-row {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 16rpx 0;
    border-bottom: 1px solid #f0f0f0;
}

.status-row:last-child, .config-row:last-child {
    border-bottom: none;
}

.status-label, .config-label {
    font-size: 28rpx;
    color: #666;
}

.status-value, .config-value {
    font-size: 28rpx;
    color: #333;
    font-weight: bold;
}

.editable-value {
    display: flex;
    flex-direction: row;
    align-items: center;
}

.edit-btn, .more-btn {
    font-size: 26rpx;
    color: #1989fa;
}

.edit-btn {
    margin-left: 16rpx;
}

.mode-picker, .date-picker {
    font-size: 28rpx;
    color: #1989fa;
    padding: 6rpx 16rpx;
    background-color: #f0f0f0;
    border-radius: 6rpx;
}

.trade-stats {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    margin-bottom: 20rpx;
}

.stat-card {
    width: 25%;
    text-align: center;
    margin-bottom: 16rpx;
}

.stat-value {
    font-size: 36rpx;
    font-weight: bold;
    color: #333;
    display: block;
    margin-bottom: 6rpx;
}

.stat-label {
    font-size: 24rpx;
    color: #666;
}

.profit {
    color: #f5222d;
}

.loss {
    color: #52c41a;
}

.profit-summary {
    background-color: #f9f9f9;
    border-radius: 8rpx;
    padding: 16rpx;
}

.summary-row {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 12rpx 0;
}

.summary-label {
    font-size: 28rpx;
    color: #666;
}

.summary-value {
    font-size: 28rpx;
    font-weight: bold;
}

.trades-list {
    margin-top: 10rpx;
}

.no-data {
    padding: 30rpx 0;
    text-align: center;
}

.no-data-text {
    font-size: 28rpx;
    color: #999;
}

.trade-item {
    padding: 20rpx 0;
    border-bottom: 1px solid #f0f0f0;
}

.trade-item:last-child {
    border-bottom: none;
}

.trade-info {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    margin-bottom: 12rpx;
}

.trade-time {
    font-size: 24rpx;
    color: #999;
}

.trade-stock {
    font-size: 28rpx;
    color: #333;
    font-weight: bold;
}

.trade-details {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
}

.trade-type {
    padding: 4rpx 16rpx;
    border-radius: 4rpx;
    font-size: 24rpx;
}

.trade-type.buy {
    background-color: #f0f5ff;
    color: #1890ff;
}

.trade-type.sell {
    background-color: #fff7e6;
    color: #fa8c16;
}

.trade-amount {
    text-align: right;
}

.amount-value {
    font-size: 28rpx;
    color: #333;
    font-weight: bold;
    display: block;
}

.price-value {
    font-size: 24rpx;
    color: #666;
    margin-top: 4rpx;
}

.ai-badge {
    padding: 4rpx 12rpx;
    background-color: #f0f7ff;
    border-radius: 30rpx;
    border: 1px solid #1989fa;
}

.ai-badge-text {
    font-size: 22rpx;
    color: #1989fa;
}
</style> 
