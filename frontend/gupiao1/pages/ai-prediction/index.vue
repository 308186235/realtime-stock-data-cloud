<template>
    <view class="container" :class="isDarkMode ? 'dark-theme' : 'light-theme'">
        <view class="header">
            <view class="title">Agent智能预测</view>
            <view class="subtitle">基于深度学习模型的市场行情预测</view>
        </view>
        
        <!-- 股票选择 -->
        <view class="card">
            <view class="stock-selector">
                <view class="search-wrapper">
                    <input type="text" v-model="searchText" placeholder="请输入股票代码或名称" class="search-input" @input="onSearchInput" />
                    <view class="search-icon">
                        <text class="icon-search">🔍</text>
                    </view>
                </view>
                
                <!-- 搜索结果下拉框 -->
                <view class="search-results" v-if="showSearchResults && searchResults.length > 0">
                    <view v-for="(stock, index) in searchResults" :key="index" class="result-item" @click="selectStock(stock)">
                        <view class="stock-code-name">
                            <text class="stock-code">{{stock.code}}</text>
                            <text class="stock-name">{{stock.name}}</text>
                        </view>
                        <text class="stock-price">{{stock.price}}</text>
                    </view>
                </view>
            </view>
            
            <!-- 已选股票信息 -->
            <view class="selected-stock" v-if="selectedStock">
                <view class="stock-info">
                    <view class="stock-name-code">
                        <text class="stock-name-large">{{selectedStock.name}}</text>
                        <text class="stock-code-large">{{selectedStock.code}}</text>
                    </view>
                    <view class="stock-price-change">
                        <text class="stock-price-large" :class="{'price-up': selectedStock.priceChange > 0, 'price-down': selectedStock.priceChange < 0}">
                            {{selectedStock.price}}
                        </text>
                        <view class="price-change" :class="{'price-up': selectedStock.priceChange > 0, 'price-down': selectedStock.priceChange < 0}">
                            <text>{{selectedStock.priceChange > 0 ? '+' : ''}}{{selectedStock.priceChange}}</text>
                            <text>({{selectedStock.priceChangePercent}}%)</text>
                        </view>
                    </view>
                </view>
                
                <view class="time-range-selector">
                    <view v-for="(option, index) in timeRangeOptions" :key="index" 
                        class="time-option" :class="{'active': selectedTimeRange === option.value}"
                        @click="selectTimeRange(option.value)">
                        {{option.label}}
                    </view>
                </view>
            </view>
        </view>
        
        <!-- 价格预测图表 -->
        <view class="card" v-if="selectedStock && pricePrediction">
            <view class="card-title">
                <text>价格预测 ({{timeRangeLabels[selectedTimeRange]}})</text>
                <view class="confidence-level">
                    <text>置信度: {{pricePrediction.confidence}}%</text>
                </view>
            </view>
            
            <view class="chart-container">
                <view class="chart-placeholder">
                    <!-- 实际项目中这里会使用echarts或其他图表库 -->
                    <text class="chart-text">价格预测图表</text>
                </view>
                
                <view class="prediction-summary">
                    <view class="prediction-item" :class="{'prediction-up': predictionTrend > 0, 'prediction-down': predictionTrend < 0}">
                        <text class="prediction-value">{{predictionEndValue}}</text>
                        <text class="prediction-label">{{timeRangeLabels[selectedTimeRange]}}预测价</text>
                    </view>
                    <view class="prediction-item" :class="{'prediction-up': predictionTrend > 0, 'prediction-down': predictionTrend < 0}">
                        <text class="prediction-value">{{predictionTrend > 0 ? '+' : ''}}{{predictionTrend}}%</text>
                        <text class="prediction-label">预期变动</text>
                    </view>
                    <view class="prediction-range">
                        <text class="range-label">预测区间:</text>
                        <text class="range-value">{{pricePrediction.lowerBound}} - {{pricePrediction.upperBound}}</text>
                    </view>
                </view>
            </view>
        </view>
        
        <!-- 关键指标预测 -->
        <view class="card" v-if="selectedStock">
            <view class="card-title">
                <text>关键指标预测</text>
            </view>
            
            <view class="metrics-grid">
                <view v-for="(metric, index) in keyMetrics" :key="index" class="metric-card">
                    <view class="metric-header">
                        <text class="metric-name">{{metric.name}}</text>
                        <view class="metric-trend" :class="{'trend-up': metric.trend > 0, 'trend-down': metric.trend < 0, 'trend-flat': metric.trend === 0}">
                            <text class="trend-icon">{{metric.trend > 0 ? '↑' : metric.trend < 0 ? '↓' : '—'}}</text>
                            <text class="trend-value">{{metric.trend > 0 ? '+' : ''}}{{metric.trend}}%</text>
                        </view>
                    </view>
                    <view class="metric-value">{{metric.value}}</view>
                    <view class="metric-desc">{{metric.description}}</view>
                </view>
            </view>
        </view>
        
        <!-- 行情预判 -->
        <view class="card" v-if="selectedStock">
            <view class="card-title">
                <text>行情预判</text>
                <view class="date-info">
                    <text>数据更新: {{lastUpdateTime}}</text>
                </view>
            </view>
            
            <view class="market-outlook">
                <view class="outlook-section">
                    <view class="outlook-header">
                        <text class="outlook-title">市场情绪</text>
                        <view class="sentiment-indicator" :class="getSentimentClass(marketSentiment)">
                            <text>{{getSentimentText(marketSentiment)}}</text>
                        </view>
                    </view>
                    <view class="outlook-content">{{marketSentimentDesc}}</view>
                </view>
                
                <view class="outlook-section">
                    <view class="outlook-header">
                        <text class="outlook-title">支撑/阻力位</text>
                    </view>
                    <view class="levels-container">
                        <view class="resistance-levels">
                            <view v-for="(level, index) in resistanceLevels" :key="'r'+index" class="level-item resistance">
                                <text class="level-value">{{level.value}}</text>
                                <text class="level-strength">{{level.strength}}</text>
                            </view>
                        </view>
                        <view class="current-price-line">
                            <text class="current-price-marker">{{selectedStock.price}}</text>
                        </view>
                        <view class="support-levels">
                            <view v-for="(level, index) in supportLevels" :key="'s'+index" class="level-item support">
                                <text class="level-value">{{level.value}}</text>
                                <text class="level-strength">{{level.strength}}</text>
                            </view>
                        </view>
                    </view>
                </view>
                
                <view class="outlook-section">
                    <view class="outlook-header">
                        <text class="outlook-title">关键因素</text>
                    </view>
                    <view class="factors-list">
                        <view v-for="(factor, index) in keyFactors" :key="index" class="factor-item">
                            <view class="factor-icon" :class="factor.impact">
                                <text>{{factor.impact === 'positive' ? '↑' : factor.impact === 'negative' ? '↓' : '—'}}</text>
                            </view>
                            <view class="factor-content">
                                <text class="factor-name">{{factor.name}}</text>
                                <text class="factor-desc">{{factor.description}}</text>
                            </view>
                        </view>
                    </view>
                </view>
            </view>
        </view>
        
        <!-- 预测性能评估 -->
        <view class="card" v-if="selectedStock">
            <view class="card-title">
                <text>预测性能</text>
            </view>
            
            <view class="performance-stats">
                <view class="performance-item">
                    <text class="performance-value">{{predictionAccuracy}}%</text>
                    <text class="performance-label">预测准确率</text>
                </view>
                <view class="performance-item">
                    <text class="performance-value">{{predictionMae}}</text>
                    <text class="performance-label">平均绝对误差</text>
                </view>
                <view class="performance-item">
                    <text class="performance-value">{{successfulPredictions}}/{{totalPredictions}}</text>
                    <text class="performance-label">方向预测</text>
                </view>
            </view>
            
            <view class="historical-accuracy">
                <view class="accuracy-header">
                    <text>历史预测表现</text>
                </view>
                <view class="accuracy-chart-placeholder">
                    <!-- 实际项目中这里会使用echarts或其他图表库 -->
                    <text class="chart-text">历史准确率图表</text>
                </view>
            </view>
        </view>
    </view>
</template>

<script>
import aiService from '../../services/aiService.js';

export default {
    data() {
        return {
            searchText: '',
            selectedStock: null,
            showSearchResults: false,
            searchResults: [],
            isDarkMode: false, // 使用与设置页面相同的方式
            timeRangeOptions: [
                { label: '1天', value: 'day' },
                { label: '1周', value: 'week' },
                { label: '1月', value: 'month' },
                { label: '3月', value: 'quarter' }
            ],
            timeRangeLabels: {
                'day': '1天后',
                'week': '1周后',
                'month': '1月后',
                'quarter': '3月后'
            },
            selectedTimeRange: 'week',
            pricePrediction: null,
            keyMetrics: [],
            marketSentiment: 0, // -100 到 100
            marketSentimentDesc: '',
            resistanceLevels: [],
            supportLevels: [],
            keyFactors: [],
            predictionAccuracy: 0,
            predictionMae: 0,
            successfulPredictions: 0,
            totalPredictions: 0,
            lastUpdateTime: '',
            loading: false
        };
    },
    
    computed: {
        // 计算预测价格趋势百分比
        predictionTrend() {
            if (!this.selectedStock || !this.pricePrediction) return 0;
            
            const currentPrice = parseFloat(this.selectedStock.price);
            const predictedPrice = parseFloat(this.pricePrediction.endValue);
            
            return parseFloat(((predictedPrice - currentPrice) / currentPrice * 100).toFixed(2));
        },
        
        // 获取预测最终价格
        predictionEndValue() {
            if (!this.pricePrediction) return '';
            return this.pricePrediction.endValue;
        }
    },
    
    onLoad() {
        // 使用全局主题设置
        const app = getApp();
        if (app.globalData) {
            this.isDarkMode = app.globalData.isDarkMode;
        }
        
        // 监听主题变化事件
        uni.$on('theme-changed', this.updateThemeFromGlobal);
        
        // 查询上次选择的股票
        this.getLastSelectedStock();
        // 获取预测性能
        this.fetchPredictionPerformance();
    },
    
    onUnload() {
        // 移除主题变化监听
        uni.$off('theme-changed', this.updateThemeFromGlobal);
    },
    
    onShow() {
        // 每次显示页面时同步全局主题设置
        this.updateThemeFromGlobal();
    },
    
    methods: {
        // 更新主题来自全局设置
        updateThemeFromGlobal() {
            const app = getApp();
            if (app.globalData) {
                this.isDarkMode = app.globalData.isDarkMode;
            }
        },
        
        // 处理搜索输入
        onSearchInput() {
            if (this.searchText.trim() === '') {
                this.showSearchResults = false;
                this.searchResults = [];
                return;
            }
            
            // 这里应该调用实际的股票搜索API
            // 为了演示,使用模拟数据
            this.mockSearchResults();
        },
        
        // 模拟搜索结果
        mockSearchResults() {
            this.searchResults = [
                { code: '600519', name: '贵州茅台', price: '1832.00', priceChange: 24.5, priceChangePercent: 1.35 },
                { code: '601318', name: '中国平安', price: '41.23', priceChange: -0.52, priceChangePercent: -1.24 },
                { code: '000858', name: '五粮液', price: '168.75', priceChange: 3.25, priceChangePercent: 1.96 },
                { code: '600036', name: '招商银行', price: '35.87', priceChange: 0.15, priceChangePercent: 0.42 }
            ];
            this.showSearchResults = true;
        },
        
        // 选择股票
        selectStock(stock) {
            this.selectedStock = stock;
            this.showSearchResults = false;
            this.searchText = `${stock.code} ${stock.name}`;
            
            // 获取预测数据
            this.fetchPredictionData();
        },
        
        // 选择时间范围
        selectTimeRange(range) {
            this.selectedTimeRange = range;
            
            // 重新获取预测数据
            this.fetchPredictionData();
        },
        
        // 获取价格预测和相关数据
        async fetchPredictionData() {
            try {
                this.loading = true;
                uni.showLoading({
                    title: '获取预测数据...'
                });
                
                // 转换时间范围为天数
                const timeStepsMap = {
                    'day': 1,
                    'week': 5,
                    'month': 20,
                    'quarter': 60
                };
                
                // 获取价格预测
                const priceData = await aiService.getPricePrediction(
                    this.selectedStock.code,
                    timeStepsMap[this.selectedTimeRange]
                );
                
                // 处理价格预测数据
                this.processPricePrediction(priceData);
                
                // 获取市场情绪和支撑阻力位
                this.fetchMarketOutlook();
                
                // 获取关键指标预测
                this.fetchKeyMetrics();
                
                // 获取预测性能指标
                this.fetchPredictionPerformance();
                
                uni.hideLoading();
            } catch (err) {
                uni.hideLoading();
                console.error('获取预测数据失败:', err);
                uni.showToast({
                    title: '获取预测数据失败',
                    icon: 'none'
                });
            } finally {
                this.loading = false;
            }
        },
        
        // 处理价格预测数据
        processPricePrediction(data) {
            // 在实际项目中,这里会处理后端返回的价格预测数据
            // 这里直接用模拟数据
            
            // 计算最终预测价格
            const predictions = data.predictions || [];
            const lastPrediction = predictions[predictions.length - 1] || {};
            
            this.pricePrediction = {
                startValue: this.selectedStock.price,
                endValue: lastPrediction.predicted_price ? lastPrediction.predicted_price.toFixed(2) : (parseFloat(this.selectedStock.price) * 1.05).toFixed(2),
                trend: this.predictionTrend,
                lowerBound: lastPrediction.lower_bound ? lastPrediction.lower_bound.toFixed(2) : (parseFloat(this.selectedStock.price) * 0.98).toFixed(2),
                upperBound: lastPrediction.upper_bound ? lastPrediction.upper_bound.toFixed(2) : (parseFloat(this.selectedStock.price) * 1.12).toFixed(2),
                confidence: lastPrediction.confidence ? Math.round(lastPrediction.confidence * 100) : 95,
                data: predictions
            };
        },
        
        // 获取市场前景和支撑阻力位
        async fetchMarketOutlook() {
            try {
                // 这里应该调用实际的API
                // 为了演示,使用模拟数据
                
                // 模拟市场情绪 (-100 到 100)
                this.marketSentiment = Math.floor(Math.random() * 140) - 70;
                
                // 市场情绪描述
                if (this.marketSentiment >= 50) {
                    this.marketSentimentDesc = '市场情绪高涨,投资者普遍看好该股短期表现。各大机构近期持续增持,散户跟风明显。';
                } else if (this.marketSentiment >= 0) {
                    this.marketSentimentDesc = '市场情绪中性偏乐观,投资者对该股看法分歧不大。主力资金态度观望,散户跟风情绪不高。';
                } else if (this.marketSentiment >= -50) {
                    this.marketSentimentDesc = '市场情绪中性偏谨慎,投资者对该股未来走势存有疑虑。主力资金有小幅流出,散户持币观望。';
                } else {
                    this.marketSentimentDesc = '市场情绪低迷,投资者对该股前景普遍悲观。主力资金持续流出,散户恐慌情绪加剧。';
                }
                
                // 模拟阻力位数据
                const basePrice = parseFloat(this.selectedStock.price);
                this.resistanceLevels = [
                    { value: (basePrice * 1.03).toFixed(2), strength: '弱' },
                    { value: (basePrice * 1.05).toFixed(2), strength: '中' },
                    { value: (basePrice * 1.08).toFixed(2), strength: '强' }
                ];
                
                // 模拟支撑位数据
                this.supportLevels = [
                    { value: (basePrice * 0.97).toFixed(2), strength: '弱' },
                    { value: (basePrice * 0.95).toFixed(2), strength: '中' },
                    { value: (basePrice * 0.92).toFixed(2), strength: '强' }
                ];
                
                // 模拟关键因素
                this.keyFactors = [
                    {
                        name: '季报业绩超预期',
                        description: '公司第三季度净利润同比增长22.5%,超出市场预期的18.3%',
                        impact: 'positive'
                    },
                    {
                        name: '外资持续流入',
                        description: '近20个交易日外资净流入3.2亿元,持仓比例上升0.4%',
                        impact: 'positive'
                    },
                    {
                        name: '行业政策调控',
                        description: '最新行业监管政策或将限制公司部分高利润业务的扩张',
                        impact: 'negative'
                    },
                    {
                        name: '市场波动加剧',
                        description: '大盘波动率近期显著提高,增加系统性风险',
                        impact: 'neutral'
                    }
                ];
                
                // 更新时间
                const now = new Date();
                this.lastUpdateTime = `${now.getMonth()+1}月${now.getDate()}日 ${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`;
                
            } catch (err) {
                console.error('获取市场前景数据失败:', err);
            }
        },
        
        // 获取关键指标预测
        async fetchKeyMetrics() {
            try {
                // 这里应该调用实际的API
                // 为了演示,使用模拟数据
                this.keyMetrics = [
                    {
                        name: '市盈率(P/E)',
                        value: '18.6',
                        trend: 2.5,
                        description: '估值水平相比行业平均低10%,具有一定安全边际'
                    },
                    {
                        name: '收入增长',
                        value: '15.8%',
                        trend: 3.2,
                        description: '营收增速持续高于行业水平,市场份额稳步提升'
                    },
                    {
                        name: '净利润率',
                        value: '12.4%',
                        trend: -1.8,
                        description: '原材料成本上升导致利润率小幅下滑,但仍处于健康水平'
                    },
                    {
                        name: '资产负债率',
                        value: '42.5%',
                        trend: 0,
                        description: '财务结构稳健,长期债务比例下降,流动性充足'
                    }
                ];
            } catch (err) {
                console.error('获取关键指标预测失败:', err);
            }
        },
        
        // 获取预测性能指标
        async fetchPredictionPerformance() {
            try {
                // 这里应该调用实际的API
                // 为了演示,使用模拟数据
                this.predictionAccuracy = 87.6;
                this.predictionMae = 0.62;
                this.successfulPredictions = 17;
                this.totalPredictions = 20;
            } catch (err) {
                console.error('获取预测性能指标失败:', err);
            }
        },
        
        // 获取市场情绪等级样式
        getSentimentClass(value) {
            if (value >= 50) return 'sentiment-bullish';
            if (value >= 0) return 'sentiment-slightly-bullish';
            if (value >= -50) return 'sentiment-slightly-bearish';
            return 'sentiment-bearish';
        },
        
        // 获取市场情绪文本
        getSentimentText(value) {
            if (value >= 50) return '强烈看多';
            if (value >= 0) return '谨慎看多';
            if (value >= -50) return '谨慎看空';
            return '强烈看空';
        },
        
        // 获取上一次选择的股票
        getLastSelectedStock() {
            try {
                // 尝试从本地存储获取上次选择的股票
                const lastStock = uni.getStorageSync('last_selected_stock');
                if (lastStock) {
                    this.selectedStock = JSON.parse(lastStock);
                    this.searchText = `${this.selectedStock.code} ${this.selectedStock.name}`;
                    
                    // 获取预测数据
                    this.fetchPredictionData();
                } else {
                    // 没有找到上次选择的股票,使用默认股票
                    this.selectedStock = {
                        code: '600519',
                        name: '贵州茅台',
                        price: '1832.00',
                        priceChange: 24.5,
                        priceChangePercent: 1.35
                    };
                    this.searchText = `${this.selectedStock.code} ${this.selectedStock.name}`;
                    
                    // 获取预测数据
                    this.fetchPredictionData();
                    
                    // 显示提示
                    uni.showToast({
                        title: '已加载默认股票数据',
                        icon: 'none',
                        duration: 2000
                    });
                }
            } catch (error) {
                console.error('获取上次选择的股票失败:', error);
                
                // 出错时使用默认股票
                this.selectedStock = {
                    code: '600519',
                    name: '贵州茅台',
                    price: '1832.00',
                    priceChange: 24.5,
                    priceChangePercent: 1.35
                };
                this.searchText = `${this.selectedStock.code} ${this.selectedStock.name}`;
                
                // 获取预测数据
                this.fetchPredictionData();
            }
        }
    }
};
</script>

<style>
.container {
    padding: 30rpx;
    min-height: 100vh;
}

/* 主题样式 */
.dark-theme {
    background-color: #141414;
    color: #e0e0e0;
}

.light-theme {
    background-color: #f5f5f5;
    color: #333333;
}

.dark-theme .card {
    background-color: #222222;
    border-radius: 12rpx;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.3);
    margin-bottom: 20rpx;
}

.light-theme .card {
    background-color: #ffffff;
    border-radius: 12rpx;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
    margin-bottom: 20rpx;
}

/* 头部样式 */
.header {
    margin-bottom: 20rpx;
}

.title {
    font-size: 40rpx;
    font-weight: bold;
    margin-bottom: 10rpx;
}

.subtitle {
    font-size: 26rpx;
    color: #999;
}

/* 卡片样式 */
.card {
    padding: 20rpx;
    margin-bottom: 20rpx;
}

.card-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
    font-size: 32rpx;
    font-weight: bold;
}

/* 股票选择样式 */
.stock-selector {
    position: relative;
    margin-bottom: 20rpx;
}

.search-wrapper {
    position: relative;
    margin-bottom: 10rpx;
}

.search-input {
    height: 80rpx;
    border-radius: 8rpx;
    padding: 0 70rpx 0 20rpx;
    font-size: 28rpx;
    width: 100%;
    box-sizing: border-box;
}

.dark-theme .search-input {
    background-color: #333;
    color: #fff;
    border: 1px solid #444;
}

.light-theme .search-input {
    background-color: #f5f5f5;
    color: #333;
    border: 1px solid #ddd;
}

.search-icon {
    position: absolute;
    right: 20rpx;
    top: 20rpx;
    font-size: 32rpx;
    color: #999;
}

.search-results {
    position: absolute;
    left: 0;
    right: 0;
    top: 90rpx;
    border-radius: 8rpx;
    z-index: 100;
    max-height: 400rpx;
    overflow-y: auto;
}

.dark-theme .search-results {
    background-color: #333;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.3);
}

.light-theme .search-results {
    background-color: #fff;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.result-item {
    display: flex;
    justify-content: space-between;
    padding: 20rpx;
    border-bottom: 1px solid #444;
    cursor: pointer;
}

.dark-theme .result-item {
    border-bottom: 1px solid #444;
}

.light-theme .result-item {
    border-bottom: 1px solid #eee;
}

.result-item:last-child {
    border-bottom: none;
}

.dark-theme .result-item:active {
    background-color: #444;
}

.light-theme .result-item:active {
    background-color: #f0f0f0;
}

.stock-code-name {
    display: flex;
    flex-direction: column;
}

.stock-code {
    font-size: 26rpx;
    font-weight: bold;
    margin-bottom: 5rpx;
}

.stock-name {
    font-size: 24rpx;
    color: #999;
}

.stock-price {
    font-size: 28rpx;
    font-weight: bold;
}

/* 已选股票样式 */
.selected-stock {
    margin-top: 20rpx;
}

.stock-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
}

.stock-name-code {
    display: flex;
    flex-direction: column;
}

.stock-name-large {
    font-size: 32rpx;
    font-weight: bold;
    margin-bottom: 5rpx;
}

.stock-code-large {
    font-size: 26rpx;
    color: #999;
}

.stock-price-change {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}

.stock-price-large {
    font-size: 36rpx;
    font-weight: bold;
    margin-bottom: 5rpx;
}

.price-change {
    display: flex;
    font-size: 24rpx;
}

.price-up {
    color: #f5222d;
}

.price-down {
    color: #52c41a;
}

/* 时间范围选择器 */
.time-range-selector {
    display: flex;
    justify-content: space-between;
    margin-top: 20rpx;
}

.time-option {
    flex: 1;
    text-align: center;
    padding: 15rpx 0;
    font-size: 28rpx;
    border-radius: 6rpx;
    margin: 0 5rpx;
    cursor: pointer;
}

.dark-theme .time-option {
    background-color: #333;
}

.light-theme .time-option {
    background-color: #f0f0f0;
}

.time-option.active {
    background-color: #4c8dff;
    color: #fff;
}

/* 置信度 */
.confidence-level {
    font-size: 24rpx;
    color: #999;
    background-color: rgba(76, 141, 255, 0.1);
    padding: 5rpx 15rpx;
    border-radius: 20rpx;
}

/* 预测图表 */
.chart-container {
    margin-top: 20rpx;
}

.chart-placeholder {
    height: 350rpx;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 8rpx;
    margin-bottom: 20rpx;
}

.dark-theme .chart-placeholder {
    background-color: #333;
}

.light-theme .chart-placeholder {
    background-color: #f0f0f0;
}

.chart-text {
    font-size: 28rpx;
    color: #999;
}

.prediction-summary {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
}

.prediction-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 15rpx;
    width: 40%;
}

.prediction-value {
    font-size: 36rpx;
    font-weight: bold;
    margin-bottom: 5rpx;
}

.prediction-label {
    font-size: 24rpx;
    color: #999;
}

.prediction-up .prediction-value {
    color: #f5222d;
}

.prediction-down .prediction-value {
    color: #52c41a;
}

.prediction-range {
    width: 100%;
    text-align: center;
    margin-top: 10rpx;
    font-size: 24rpx;
}

.range-label {
    color: #999;
    margin-right: 10rpx;
}

/* 关键指标样式 */
.metrics-grid {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -10rpx;
}

.metric-card {
    width: 50%;
    padding: 10rpx;
    box-sizing: border-box;
    margin-bottom: 20rpx;
}

.metric-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10rpx;
}

.metric-name {
    font-size: 26rpx;
    font-weight: bold;
}

.metric-trend {
    display: flex;
    align-items: center;
    font-size: 22rpx;
}

.trend-icon {
    margin-right: 5rpx;
}

.trend-up {
    color: #f5222d;
}

.trend-down {
    color: #52c41a;
}

.trend-flat {
    color: #999;
}

.metric-value {
    font-size: 32rpx;
    font-weight: bold;
    margin-bottom: 5rpx;
}

.metric-desc {
    font-size: 22rpx;
    line-height: 1.3;
}

.dark-theme .metric-desc {
    color: #999;
}

.light-theme .metric-desc {
    color: #666;
}

/* 行情预判样式 */
.date-info {
    font-size: 22rpx;
    color: #999;
}

.market-outlook {
    margin-top: 10rpx;
}

.outlook-section {
    margin-bottom: 30rpx;
}

.outlook-header {
    display: flex;
    align-items: center;
    margin-bottom: 15rpx;
}

.outlook-title {
    font-size: 28rpx;
    font-weight: bold;
    margin-right: 15rpx;
}

.sentiment-indicator {
    font-size: 24rpx;
    padding: 5rpx 15rpx;
    border-radius: 20rpx;
}

.sentiment-bullish {
    background-color: rgba(245, 34, 45, 0.2);
    color: #f5222d;
}

.sentiment-slightly-bullish {
    background-color: rgba(245, 34, 45, 0.1);
    color: #f5222d;
}

.sentiment-slightly-bearish {
    background-color: rgba(82, 196, 26, 0.1);
    color: #52c41a;
}

.sentiment-bearish {
    background-color: rgba(82, 196, 26, 0.2);
    color: #52c41a;
}

.outlook-content {
    font-size: 26rpx;
    line-height: 1.5;
}

.dark-theme .outlook-content {
    color: #bbb;
}

.light-theme .outlook-content {
    color: #666;
}

/* 支撑阻力位样式 */
.levels-container {
    position: relative;
    padding: 20rpx 0;
}

.resistance-levels, .support-levels {
    display: flex;
    flex-direction: column;
}

.level-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10rpx 20rpx;
    margin: 5rpx 0;
    border-radius: 6rpx;
    font-size: 24rpx;
}

.resistance {
    color: #f5222d;
}

.dark-theme .resistance {
    background-color: rgba(245, 34, 45, 0.1);
}

.light-theme .resistance {
    background-color: rgba(245, 34, 45, 0.05);
}

.support {
    color: #52c41a;
}

.dark-theme .support {
    background-color: rgba(82, 196, 26, 0.1);
}

.light-theme .support {
    background-color: rgba(82, 196, 26, 0.05);
}

.level-strength {
    font-size: 22rpx;
    opacity: 0.8;
}

.current-price-line {
    position: relative;
    height: 40rpx;
    margin: 15rpx 0;
    border-left: 3rpx dashed #999;
    display: flex;
    align-items: center;
}

.current-price-marker {
    font-size: 26rpx;
    font-weight: bold;
    background-color: #4c8dff;
    color: #fff;
    padding: 5rpx 10rpx;
    border-radius: 4rpx;
    margin-left: 10rpx;
}

/* 关键因素样式 */
.factors-list {
    margin-top: 10rpx;
}

.factor-item {
    display: flex;
    margin-bottom: 15rpx;
    padding: 10rpx;
    border-radius: 6rpx;
}

.dark-theme .factor-item {
    background-color: #333;
}

.light-theme .factor-item {
    background-color: #f5f5f5;
}

.factor-icon {
    width: 50rpx;
    height: 50rpx;
    border-radius: 25rpx;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 28rpx;
    margin-right: 15rpx;
}

.factor-icon.positive {
    background-color: rgba(82, 196, 26, 0.2);
    color: #52c41a;
}

.factor-icon.negative {
    background-color: rgba(245, 34, 45, 0.2);
    color: #f5222d;
}

.factor-icon.neutral {
    background-color: rgba(250, 173, 20, 0.2);
    color: #faad14;
}

.factor-content {
    flex: 1;
}

.factor-name {
    font-size: 26rpx;
    font-weight: bold;
    margin-bottom: 5rpx;
}

.factor-desc {
    font-size: 24rpx;
}

.dark-theme .factor-desc {
    color: #999;
}

.light-theme .factor-desc {
    color: #666;
}

/* 预测性能样式 */
.performance-stats {
    display: flex;
    justify-content: space-around;
    margin-bottom: 30rpx;
}

.performance-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.performance-value {
    font-size: 32rpx;
    font-weight: bold;
    margin-bottom: 5rpx;
}

.performance-label {
    font-size: 24rpx;
    color: #999;
}

.historical-accuracy {
    margin-top: 20rpx;
}

.accuracy-header {
    font-size: 28rpx;
    font-weight: bold;
    margin-bottom: 15rpx;
}

.accuracy-chart-placeholder {
    height: 200rpx;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 8rpx;
}

.dark-theme .accuracy-chart-placeholder {
    background-color: #333;
}

.light-theme .accuracy-chart-placeholder {
    background-color: #f0f0f0;
}
</style> 
