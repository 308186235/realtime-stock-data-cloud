<template>
    <view class="container">
        <view class="header">
            <view class="back-button" @click="navigateBack">
                <text class="back-icon">&#xe607;</text>
            </view>
            <text class="title">形态识别分析</text>
        </view>
        
        <view class="stock-selector">
            <text class="label">选择股票:</text>
            <picker @change="onStockChange" :value="currentStockIndex" :range="stockOptions" range-key="name">
                <view class="picker-value">
                    <text>{{ currentStock.code }} {{ currentStock.name }}</text>
                    <text class="picker-arrow">▼</text>
                </view>
            </picker>
            <button class="analyze-btn" @click="analyzePatterns">分析</button>
        </view>
        
        <!-- 股票K线图和识别形态 -->
        <view class="chart-container card">
            <text class="section-title">K线形态分析</text>
            
            <!-- 使用PatternVisualization组件 -->
            <PatternVisualization 
                v-if="stockData.prices.length > 0 && detectedPatterns.length > 0"
                :detectedPatterns="detectedPatterns"
                :stockData="stockData"
            />
            
            <view v-else class="loading-container">
                <text v-if="isAnalyzing" class="loading-text">正在分析形态...</text>
                <text v-else class="loading-text">请选择股票并点击分析</text>
            </view>
        </view>
        
        <!-- 形态识别结果列表 -->
        <view class="patterns-list card">
            <text class="section-title">识别结果 ({{ detectedPatterns.length }})</text>
            <view class="pattern-filters">
                <text 
                    v-for="(filter, index) in patternFilters" 
                    :key="index"
                    :class="['filter-item', { active: filter.active }]"
                    @click="toggleFilter(index)"
                >
                    {{ filter.name }}
                </text>
            </view>
            
            <scroll-view scroll-y="true" class="patterns-scroll">
                <view 
                    v-for="(pattern, index) in filteredPatterns" 
                    :key="index"
                    class="pattern-item"
                    @click="selectPattern(index)"
                >
                    <view class="pattern-header">
                        <text class="pattern-name">{{ pattern.name }}</text>
                        <text class="pattern-confidence">可信度: {{ Math.round(pattern.confidence * 100) }}%</text>
                    </view>
                    <view class="pattern-info">
                        <text class="pattern-direction" :class="getDirectionClass(pattern.direction)">
                            {{ getDirectionText(pattern.direction) }}
                        </text>
                        <text class="pattern-time">{{ pattern.detectedAt }}</text>
                    </view>
                    <view class="confidence-bar">
                        <view class="confidence-fill" :style="{ width: `${pattern.confidence * 100}%`, backgroundColor: getConfidenceColor(pattern.confidence) }"></view>
                    </view>
                </view>
                
                <view v-if="filteredPatterns.length === 0" class="no-patterns">
                    <text>没有符合条件的形态</text>
                </view>
            </scroll-view>
        </view>
        
        <!-- 交易建议部分 -->
        <view class="trade-advice card" v-if="selectedPattern">
            <text class="section-title">交易建议</text>
            <view class="advice-content">
                <view class="advice-header">
                    <text class="advice-title">根据 {{ selectedPattern.name }} 形态</text>
                    <text class="advice-action" :class="getActionClass(selectedPattern.direction)">
                        {{ getActionText(selectedPattern.direction) }}
                    </text>
                </view>
                
                <view class="advice-detail">
                    <text class="advice-description">{{ getTradeAdvice(selectedPattern) }}</text>
                    
                    <view class="advice-stats">
                        <view class="stat-item">
                            <text class="stat-label">历史成功率</text>
                            <text class="stat-value">{{ getSuccessRate(selectedPattern) }}%</text>
                        </view>
                        <view class="stat-item">
                            <text class="stat-label">平均收益</text>
                            <text class="stat-value" :class="getReturnClass(selectedPattern)">
                                {{ getAverageReturn(selectedPattern) }}%
                            </text>
                        </view>
                        <view class="stat-item">
                            <text class="stat-label">建议持仓</text>
                            <text class="stat-value">{{ getHoldingPeriod(selectedPattern) }}</text>
                        </view>
                    </view>
                </view>
                
                <view class="action-buttons">
                    <button class="action-btn" :class="getBuyButtonClass(selectedPattern)" @click="executeTrade('buy')">买入</button>
                    <button class="action-btn" :class="getSellButtonClass(selectedPattern)" @click="executeTrade('sell')">卖出</button>
                </view>
            </view>
        </view>
    </view>
</template>

<script>
import PatternVisualization from '../../components/PatternVisualization.vue';

export default {
    components: {
        PatternVisualization
    },
    data() {
        return {
            // 股票选项
            stockOptions: [
                { code: 'SH000001', name: '上证指数' },
                { code: 'SH600519', name: '贵州茅台' },
                { code: 'SZ000858', name: '五粮液' },
                { code: 'SZ300750', name: '宁德时代' },
                { code: 'SH601318', name: '中国平安' }
            ],
            currentStockIndex: 0,
            
            // 股票数据
            stockData: {
                prices: [],
                volumes: [],
                highs: [],
                lows: [],
                opens: [],
                closes: [],
                dates: []
            },
            
            // 分析状态
            isAnalyzing: false,
            
            // 检测到的形态
            detectedPatterns: [],
            selectedPattern: null,
            
            // 形态过滤器
            patternFilters: [
                { name: '全部', type: 'all', active: true },
                { name: '看涨', type: 'bullish', active: false },
                { name: '看跌', type: 'bearish', active: false },
                { name: '反转', type: 'reversal', active: false },
                { name: '持续', type: 'continuation', active: false }
            ]
        }
    },
    computed: {
        currentStock() {
            return this.stockOptions[this.currentStockIndex];
        },
        filteredPatterns() {
            // 获取激活的过滤器
            const activeFilter = this.patternFilters.find(filter => filter.active);
            
            if (activeFilter.type === 'all') {
                return this.detectedPatterns;
            }
            
            // 根据过滤条件筛选形态
            return this.detectedPatterns.filter(pattern => {
                if (activeFilter.type === 'bullish') {
                    return pattern.direction === 'bullish';
                } else if (activeFilter.type === 'bearish') {
                    return pattern.direction === 'bearish';
                } else if (activeFilter.type === 'reversal') {
                    return pattern.patternType === 'reversal';
                } else if (activeFilter.type === 'continuation') {
                    return pattern.patternType === 'continuation';
                }
                return true;
            });
        }
    },
    methods: {
        // 导航回上一页
        navigateBack() {
            uni.navigateBack();
        },
        
        // 更改股票选择
        onStockChange(e) {
            this.currentStockIndex = e.detail.value;
        },
        
        // 分析形态
        analyzePatterns() {
            this.isAnalyzing = true;
            this.detectedPatterns = [];
            this.selectedPattern = null;
            
            // 获取股票数据
            this.fetchStockData(this.currentStock.code)
                .then(() => {
                    // 分析形态
                    this.detectPatterns();
                    this.isAnalyzing = false;
                })
                .catch(error => {
                    console.error('获取股票数据失败', error);
                    this.isAnalyzing = false;
                    uni.showToast({
                        title: '获取数据失败',
                        icon: 'none'
                    });
                });
        },
        
        // 获取股票数据
        fetchStockData(stockCode) {
            // 模拟获取数据
            return new Promise((resolve) => {
                setTimeout(() => {
                    // 生成模拟股票数据
                    const data = this.generateMockStockData();
                    this.stockData = data;
                    resolve(data);
                }, 1000);
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
                
                const high = price + Math.random() * 1;
                const low = price - Math.random() * 1;
                
                highs.push(high);
                lows.push(low);
                
                opens.push(price - change / 2);
                closes.push(price);
                prices.push(price);
                
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
        
        // 检测形态
        detectPatterns() {
            // 模拟形态检测
            const mockPatterns = [
                {
                    name: 'MACD金叉',
                    detected: true,
                    confidence: 0.85,
                    direction: 'bullish',
                    patternType: 'reversal',
                    description: 'MACD金叉是一个看涨信号,表明短期动量超过长期动量,可能预示着上涨趋势的开始。',
                    detectedAt: '2023-06-12'
                },
                {
                    name: '双底形态',
                    detected: true,
                    confidence: 0.70,
                    direction: 'bullish',
                    patternType: 'reversal',
                    description: '双底是一种底部反转形态,表明下跌趋势即将结束,转为上涨趋势。',
                    detectedAt: '2023-06-10'
                },
                {
                    name: '头肩顶形态',
                    detected: true,
                    confidence: 0.65,
                    direction: 'bearish',
                    patternType: 'reversal',
                    description: '头肩顶是一种顶部反转形态,表明上涨趋势即将结束,转为下跌趋势。',
                    detectedAt: '2023-06-05'
                },
                {
                    name: '三重底形态',
                    detected: true,
                    confidence: 0.62,
                    direction: 'bullish',
                    patternType: 'reversal',
                    description: '三重底是一种底部反转形态,显示价格三次测试同一水平的支撑位后开始上涨。',
                    detectedAt: '2023-06-08'
                },
                {
                    name: '上升三角形',
                    detected: true,
                    confidence: 0.78,
                    direction: 'bullish',
                    patternType: 'continuation',
                    description: '上升三角形是一种持续性形态,通常在上升趋势中出现,预示着趋势将继续。',
                    detectedAt: '2023-06-15'
                },
                {
                    name: '看跌旗形',
                    detected: true,
                    confidence: 0.73,
                    direction: 'bearish',
                    patternType: 'continuation',
                    description: '看跌旗形是一种短期整理形态,预示着下跌趋势将继续。',
                    detectedAt: '2023-06-02'
                }
            ];
            
            this.detectedPatterns = mockPatterns;
            
            if (mockPatterns.length > 0) {
                this.selectedPattern = mockPatterns[0];
            }
        },
        
        // 切换过滤器
        toggleFilter(index) {
            this.patternFilters.forEach((filter, i) => {
                filter.active = i === index;
            });
        },
        
        // 选择形态
        selectPattern(index) {
            this.selectedPattern = this.filteredPatterns[index];
        },
        
        // 根据形态方向获取样式类
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
        
        // 获取操作类型文本
        getActionText(direction) {
            if (direction === 'bullish') return '建议买入';
            if (direction === 'bearish') return '建议卖出';
            return '观望';
        },
        
        // 获取操作类型样式
        getActionClass(direction) {
            if (direction === 'bullish') return 'action-buy';
            if (direction === 'bearish') return 'action-sell';
            return 'action-hold';
        },
        
        // 获取可信度颜色
        getConfidenceColor(confidence) {
            if (confidence >= 0.8) return '#07c160';
            if (confidence >= 0.6) return '#1989fa';
            if (confidence >= 0.4) return '#ffa300';
            return '#ff3b30';
        },
        
        // 获取交易建议
        getTradeAdvice(pattern) {
            if (pattern.direction === 'bullish') {
                return `根据${pattern.name}形态分析,该股票可能呈现上涨趋势。该形态在历史上有较高的成功率,建议考虑买入并持有1-2周,密切关注突破关键阻力位情况。`;
            } else if (pattern.direction === 'bearish') {
                return `根据${pattern.name}形态分析,该股票可能呈现下跌趋势。建议考虑减持或做空,设置适当止损,关注支撑位反弹情况。`;
            }
            return '当前形态分析结果不明确,建议观望,等待更多信号确认。';
        },
        
        // 获取历史成功率
        getSuccessRate(pattern) {
            // 模拟数据
            const successRates = {
                'MACD金叉': 78,
                '双底形态': 65,
                '头肩顶形态': 72,
                '三重底形态': 68,
                '上升三角形': 75,
                '看跌旗形': 70
            };
            
            return successRates[pattern.name] || 60;
        },
        
        // 获取平均收益
        getAverageReturn(pattern) {
            // 模拟数据
            const averageReturns = {
                'MACD金叉': 5.8,
                '双底形态': 7.2,
                '头肩顶形态': -6.5,
                '三重底形态': 8.3,
                '上升三角形': 6.2,
                '看跌旗形': -5.4
            };
            
            return averageReturns[pattern.name] || 0;
        },
        
        // 获取收益样式
        getReturnClass(pattern) {
            const returnValue = this.getAverageReturn(pattern);
            if (returnValue > 0) return 'positive-return';
            if (returnValue < 0) return 'negative-return';
            return '';
        },
        
        // 获取建议持仓时间
        getHoldingPeriod(pattern) {
            // 模拟数据
            const holdingPeriods = {
                'MACD金叉': '1-2周',
                '双底形态': '2-4周',
                '头肩顶形态': '2-3周',
                '三重底形态': '3-4周',
                '上升三角形': '2-3周',
                '看跌旗形': '1-2周'
            };
            
            return holdingPeriods[pattern.name] || '2周';
        },
        
        // 获取买入按钮样式
        getBuyButtonClass(pattern) {
            return pattern.direction === 'bullish' ? 'primary' : 'secondary';
        },
        
        // 获取卖出按钮样式
        getSellButtonClass(pattern) {
            return pattern.direction === 'bearish' ? 'primary' : 'secondary';
        },
        
        // 执行交易
        executeTrade(action) {
            if (!this.selectedPattern) return;
            
            uni.showModal({
                title: '交易确认',
                content: `确认要${action === 'buy' ? '买入' : '卖出'} ${this.currentStock.code} ${this.currentStock.name}?`,
                success: (res) => {
                    if (res.confirm) {
                        uni.showToast({
                            title: `已${action === 'buy' ? '买入' : '卖出'}`,
                            icon: 'success'
                        });
                    }
                }
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

.stock-selector {
    display: flex;
    flex-direction: row;
    align-items: center;
    margin-bottom: 30rpx;
    background-color: #fff;
    border-radius: 16rpx;
    padding: 20rpx;
    box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
}

.label {
    font-size: 28rpx;
    color: #666;
    margin-right: 20rpx;
}

.picker-value {
    flex: 1;
    font-size: 28rpx;
    color: #333;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
}

.picker-arrow {
    font-size: 24rpx;
    color: #999;
    margin-left: 10rpx;
}

.analyze-btn {
    width: 160rpx;
    height: 70rpx;
    line-height: 70rpx;
    background-color: #1989fa;
    color: #fff;
    font-size: 28rpx;
    text-align: center;
    border-radius: 35rpx;
    margin-left: 20rpx;
}

.chart-container {
    height: 600rpx;
    overflow: hidden;
}

.loading-container {
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.loading-text {
    font-size: 28rpx;
    color: #999;
}

.patterns-list {
    max-height: 600rpx;
    overflow: hidden;
}

.pattern-filters {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    margin-bottom: 20rpx;
}

.filter-item {
    font-size: 26rpx;
    color: #666;
    background-color: #f0f0f0;
    padding: 8rpx 20rpx;
    border-radius: 30rpx;
    margin-right: 15rpx;
    margin-bottom: 15rpx;
}

.filter-item.active {
    color: #fff;
    background-color: #1989fa;
}

.patterns-scroll {
    max-height: 400rpx;
}

.pattern-item {
    padding: 20rpx;
    border-bottom: 1px solid #f0f0f0;
}

.pattern-item:last-child {
    border-bottom: none;
}

.pattern-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10rpx;
}

.pattern-name {
    font-size: 28rpx;
    font-weight: bold;
    color: #333;
}

.pattern-confidence {
    font-size: 24rpx;
    color: #666;
}

.pattern-info {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10rpx;
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

.pattern-time {
    font-size: 24rpx;
    color: #999;
}

.confidence-bar {
    height: 8rpx;
    background-color: #f0f0f0;
    border-radius: 4rpx;
    overflow: hidden;
    margin-top: 10rpx;
}

.confidence-fill {
    height: 100%;
    border-radius: 4rpx;
}

.no-patterns {
    padding: 30rpx 0;
    text-align: center;
}

.no-patterns text {
    font-size: 28rpx;
    color: #999;
}

.trade-advice {
    margin-bottom: 100rpx;
}

.advice-content {
    padding: 20rpx;
    background-color: #f9f9f9;
    border-radius: 12rpx;
}

.advice-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
}

.advice-title {
    font-size: 28rpx;
    font-weight: bold;
    color: #333;
}

.advice-action {
    font-size: 28rpx;
    font-weight: bold;
    padding: 6rpx 16rpx;
    border-radius: 6rpx;
}

.action-buy {
    color: #07c160;
    background-color: rgba(7, 193, 96, 0.1);
}

.action-sell {
    color: #ee0a24;
    background-color: rgba(238, 10, 36, 0.1);
}

.action-hold {
    color: #1989fa;
    background-color: rgba(25, 137, 250, 0.1);
}

.advice-detail {
    margin-bottom: 30rpx;
}

.advice-description {
    font-size: 26rpx;
    color: #666;
    line-height: 1.6;
    margin-bottom: 20rpx;
    display: block;
}

.advice-stats {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    background-color: #fff;
    border-radius: 8rpx;
    padding: 16rpx;
    margin-top: 20rpx;
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
}

.positive-return {
    color: #07c160;
}

.negative-return {
    color: #ee0a24;
}

.action-buttons {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
}

.action-btn {
    flex: 1;
    height: 80rpx;
    line-height: 80rpx;
    text-align: center;
    font-size: 28rpx;
    border-radius: 40rpx;
    margin: 0 15rpx;
}

.action-btn.primary {
    background-color: #1989fa;
    color: #fff;
}

.action-btn.secondary {
    background-color: #f0f0f0;
    color: #666;
}
</style> 
