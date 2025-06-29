<template>
    <view class="container">
        <view class="header">
            <view class="stock-basic-info">
                <view class="name-code">
                    <text class="stock-name">{{stock.name}}</text>
                    <text class="stock-code">{{stock.code}}</text>
                </view>
                <view class="price-info">
                    <text class="price">￥{{stock.price}}</text>
                    <text :class="['change', stock.change >= 0 ? 'increase' : 'decrease']">
                        {{stock.change >= 0 ? '+' : ''}}{{stock.change}}%
                    </text>
                </view>
            </view>
        </view>
        
        <view class="tab-nav">
            <view 
                v-for="(tab, index) in tabs" 
                :key="index" 
                :class="['tab-item', { active: currentTab === index }]"
                @click="switchTab(index)"
            >
                <text class="tab-text">{{tab}}</text>
            </view>
        </view>
        
        <!-- 概览选项卡 -->
        <view v-if="currentTab === 0" class="tab-content">
            <view class="detail-card">
                <view class="card-title">
                    <text class="title-text">推荐分析</text>
                </view>
                <view class="recommendation-details">
                    <view class="score-box">
                        <text class="score-title">综合评分</text>
                        <view class="score-circle" :class="getScoreClass(stock.score)">
                            <text class="score-value">{{stock.score}}</text>
                        </view>
                    </view>
                    <view class="action-box">
                        <text class="action-title">操作建议</text>
                        <text :class="['action-tag', getActionClass(stock.action)]">
                            {{getActionText(stock.action)}}
                        </text>
                    </view>
                </view>
                
                <view class="factor-analysis">
                    <view class="factor-title">
                        <text>因子分析</text>
                    </view>
                    <view class="factor-list">
                        <view v-for="(factor, index) in stock.factors" :key="index" class="factor-item">
                            <text class="factor-name">{{factor.name}}</text>
                            <view class="factor-details">
                                <text :class="['factor-value', factor.isPositive ? 'positive' : 'negative']">{{factor.value}}</text>
                                <text :class="['factor-impact', factor.isPositive ? 'positive' : 'negative']">
                                    {{factor.isPositive ? '利好' : '利空'}}
                                </text>
                            </view>
                        </view>
                    </view>
                </view>
                
                <view class="ai-summary">
                    <view class="summary-title">
                        <text>AI分析摘要</text>
                    </view>
                    <text class="summary-content">
                        通过对{{stock.name}}进行多维度分析,该股估值处于行业低位,动量指标显示近期有上涨趋势。威廉指标(Williams %R)当前值为{{getWilliamsRValue()}},处于{{getWilliamsRZone()}},{{getWilliamsRAnalysis()}}
                    </text>
                </view>
            </view>
            
            <view class="detail-card">
                <view class="card-title">
                    <text class="title-text">交易建议</text>
                </view>
                <view class="trading-advice">
                    <view class="advice-item">
                        <text class="advice-type">操作策略</text>
                        <text class="advice-content">{{getTradingStrategy()}}</text>
                    </view>
                    <view class="advice-item">
                        <text class="advice-type">建议仓位</text>
                        <text class="advice-content">{{getPositionAdvice()}}</text>
                    </view>
                    <view class="advice-item">
                        <text class="advice-type">止盈参考</text>
                        <text class="advice-content">{{stock.price * 1.1}}元 (+10%)</text>
                    </view>
                    <view class="advice-item">
                        <text class="advice-type">止损参考</text>
                        <text class="advice-content">{{stock.price * 0.95}}元 (-5%)</text>
                    </view>
                </view>
            </view>
        </view>
        
        <!-- K线图表选项卡 -->
        <view v-if="currentTab === 1" class="tab-content">
            <view class="detail-card">
                <view class="card-title">
                    <text class="title-text">K线图表</text>
                </view>
                <StockChart :code="stock.code" :title="stock.name" :showCompare="true"></StockChart>
            </view>
        </view>
        
        <!-- 威廉指标选项卡 -->
        <view v-if="currentTab === 2" class="tab-content">
            <view class="detail-card">
                <view class="card-title">
                    <text class="title-text">威廉指标分析</text>
                </view>
                
                <view class="williams-analysis">
                    <view class="williams-current">
                        <text class="analysis-subtitle">当前威廉指标值</text>
                        <view class="williams-value-box">
                            <text :class="['williams-value', getWilliamsClass()]">{{getWilliamsRValue()}}</text>
                            <text class="williams-zone">({{getWilliamsRZone()}})</text>
                        </view>
                    </view>
                    
                    <view class="williams-chart">
                        <text class="analysis-subtitle">威廉指标趋势图</text>
                        <view class="chart-placeholder">
                            <text class="placeholder-text">指标走势图</text>
                            <!-- 实际应用中这里应该是真正的图表组件 -->
                        </view>
                    </view>
                    
                    <view class="williams-interpretation">
                        <text class="analysis-subtitle">指标解读</text>
                        <text class="interpretation-text">
                            {{getWilliamsRDetailedAnalysis()}}
                        </text>
                    </view>
                    
                    <view class="williams-signals">
                        <text class="analysis-subtitle">信号历史</text>
                        <view class="signals-list">
                            <view class="signal-item">
                                <text class="signal-date">2023-05-02</text>
                                <text class="signal-type buy">从超卖区上穿</text>
                                <text class="signal-result positive">+8.5%</text>
                            </view>
                            <view class="signal-item">
                                <text class="signal-date">2023-03-15</text>
                                <text class="signal-type sell">从超买区下穿</text>
                                <text class="signal-result positive">+3.2%</text>
                            </view>
                            <view class="signal-item">
                                <text class="signal-date">2023-02-10</text>
                                <text class="signal-type buy">从超卖区上穿</text>
                                <text class="signal-result negative">-2.1%</text>
                            </view>
                        </view>
                    </view>
                </view>
            </view>
        </view>
        
        <!-- 基本面选项卡 -->
        <view v-if="currentTab === 3" class="tab-content">
            <view class="detail-card">
                <view class="card-title">
                    <text class="title-text">基本面数据</text>
                </view>
                <view class="fundamental-data">
                    <view class="data-row">
                        <text class="data-label">市盈率(P/E)</text>
                        <text class="data-value">{{getFundamentalValue('pe')}}</text>
                    </view>
                    <view class="data-row">
                        <text class="data-label">市净率(P/B)</text>
                        <text class="data-value">{{getFundamentalValue('pb')}}</text>
                    </view>
                    <view class="data-row">
                        <text class="data-label">市值</text>
                        <text class="data-value">{{getFundamentalValue('marketCap')}}</text>
                    </view>
                    <view class="data-row">
                        <text class="data-label">净资产收益率(ROE)</text>
                        <text class="data-value">{{getFundamentalValue('roe')}}</text>
                    </view>
                    <view class="data-row">
                        <text class="data-label">股息率</text>
                        <text class="data-value">{{getFundamentalValue('dividendYield')}}</text>
                    </view>
                    <view class="data-row">
                        <text class="data-label">总收入(最新季度)</text>
                        <text class="data-value">{{getFundamentalValue('revenue')}}</text>
                    </view>
                    <view class="data-row">
                        <text class="data-label">净利润(最新季度)</text>
                        <text class="data-value">{{getFundamentalValue('netIncome')}}</text>
                    </view>
                    <view class="data-row">
                        <text class="data-label">收入增长率(YoY)</text>
                        <text class="data-value">{{getFundamentalValue('revenueGrowth')}}</text>
                    </view>
                </view>
            </view>
        </view>
        
        <view class="action-buttons">
            <button class="action-btn primary" @click="addToWatchlist">加入自选</button>
            <button class="action-btn secondary" @click="simulateTrade">模拟交易</button>
        </view>
    </view>
</template>

<script>
import StockChart from '../../components/StockChart.vue';

export default {
    components: {
        StockChart
    },
    data() {
        return {
            stock: {
                name: '',
                code: '',
                price: '',
                change: 0,
                score: 0,
                action: '',
                factors: []
            },
            tabs: ['综合概览', 'K线图表', '威廉指标', '基本面数据'],
            currentTab: 0,
            fundamentalData: {
                pe: '12.5',
                pb: '1.8',
                marketCap: '2350亿元',
                roe: '15.2%',
                dividendYield: '2.3%',
                revenue: '458亿元',
                netIncome: '62亿元',
                revenueGrowth: '+12.5%'
            }
        };
    },
    onLoad(option) {
        // 获取传递过来的股票代码
        const code = option.code;
        
        // 从本地存储获取股票信息
        try {
            const stockData = uni.getStorageSync('selectedStock');
            if (stockData) {
                this.stock = JSON.parse(stockData);
            } else {
                // 如果没有找到数据,可以根据code从服务器获取
                this.fetchStockData(code);
            }
        } catch (e) {
            console.error('获取股票数据失败', e);
            // 在实际应用中,这里应该处理错误并从服务器获取数据
            this.fetchStockData(code);
        }
    },
    methods: {
        switchTab(index) {
            this.currentTab = index;
        },
        fetchStockData(code) {
            // 模拟API请求
            console.log('正在获取股票数据,代码:', code);
            // 实际应用中,这里应该是从服务器获取数据
            
            // 模拟数据
            setTimeout(() => {
                this.stock = {
                    name: '示例股票',
                    code: code || '000000',
                    price: '50.00',
                    change: 1.5,
                    score: 75,
                    action: 'BUY',
                    factors: [
                        { name: '估值', value: 'P/E: 12.5', isPositive: true },
                        { name: '动量', value: '中性', isPositive: true },
                        { name: '威廉指标', value: '-78.3', isPositive: true }
                    ]
                };
            }, 500);
        },
        getScoreClass(score) {
            if (score >= 80) return 'high-score';
            if (score >= 60) return 'medium-score';
            return 'low-score';
        },
        getActionClass(action) {
            if (action === 'STRONG_BUY') return 'strong-buy';
            if (action === 'BUY') return 'buy';
            if (action === 'HOLD') return 'hold';
            if (action === 'SELL') return 'sell';
            return '';
        },
        getActionText(action) {
            if (action === 'STRONG_BUY') return '强烈推荐';
            if (action === 'BUY') return '建议买入';
            if (action === 'HOLD') return '持有';
            if (action === 'SELL') return '建议卖出';
            return '';
        },
        addToWatchlist() {
            uni.showToast({
                title: this.stock.name + '已加入自选',
                icon: 'success'
            });
        },
        simulateTrade() {
            uni.showToast({
                title: '已添加到模拟交易',
                icon: 'success'
            });
        },
        getWilliamsRValue() {
            // 从因子中获取威廉指标值
            const williamsRFactor = this.stock.factors.find(f => f.name === '威廉指标');
            return williamsRFactor ? williamsRFactor.value.replace('Williams %R: ', '') : '-78.3';
        },
        getWilliamsRZone() {
            const value = parseFloat(this.getWilliamsRValue());
            if (value >= -20) return '超买区';
            if (value <= -80) return '超卖区';
            return '中性区域';
        },
        getWilliamsClass() {
            const zone = this.getWilliamsRZone();
            if (zone === '超买区') return 'overbought';
            if (zone === '超卖区') return 'oversold';
            return 'neutral';
        },
        getWilliamsRAnalysis() {
            const zone = this.getWilliamsRZone();
            if (zone === '超买区') return '表明市场可能超买,存在回调风险。建议谨慎追高,考虑逢高减仓。';
            if (zone === '超卖区') return '表明市场可能超卖,存在反弹机会。可考虑逢低布局,但需结合其他指标确认。';
            return '表明市场处于中性状态,建议观察其他指标辅助决策。';
        },
        getWilliamsRDetailedAnalysis() {
            const value = parseFloat(this.getWilliamsRValue());
            const zone = this.getWilliamsRZone();
            
            let analysis = `威廉指标(Williams %R)是一种动量振荡器,用于识别超买和超卖水平。当前${this.stock.name}的威廉指标值为${this.getWilliamsRValue()},处于${zone}。`;
            
            if (zone === '超卖区') {
                analysis += `\n\n从历史数据看,当威廉指标低于-80并开始回升时,往往是较好的买入机会。当前指标已进入超卖区域,若后续伴随成交量放大并出现指标回升,可能形成较强的买入信号。`;
                analysis += `\n\n建议结合RSI指标和MACD指标进行确认。当威廉指标,RSI和MACD三者同时显示底部反转信号时,成功率更高。`;
            } else if (zone === '超买区') {
                analysis += `\n\n从历史数据看,当威廉指标高于-20并开始回落时,往往是较好的卖出机会。当前指标已进入超买区域,表明短期内上涨动能可能已接近尾声,存在回调风险。`;
                analysis += `\n\n建议密切关注指标是否开始回落,若出现回落并伴随成交量萎缩,可能是较好的获利了结时机。`;
            } else {
                analysis += `\n\n目前指标处于中性区域,既没有明显的超买也没有明显的超卖信号。建议观察指标未来走势变化,并结合其他技术指标和基本面因素做出决策。`;
            }
            
            return analysis;
        },
        getTradingStrategy() {
            const action = this.stock.action;
            
            if (action === 'STRONG_BUY') {
                return '建议积极买入,可分批建仓,第一批位置25%仓位';
            } else if (action === 'BUY') {
                return '建议逢低买入,可小仓位试探性建仓10-15%';
            } else if (action === 'HOLD') {
                return '持有已有仓位,暂不加仓也不减仓';
            } else if (action === 'SELL') {
                return '建议减持,可分批出售现有仓位';
            }
            
            return '观望为主,等待更明确的信号';
        },
        getPositionAdvice() {
            const score = this.stock.score;
            
            if (score >= 90) return '30-40% 仓位';
            if (score >= 80) return '20-30% 仓位';
            if (score >= 70) return '10-20% 仓位';
            if (score >= 60) return '5-10% 仓位';
            
            return '不建议开仓';
        },
        getFundamentalValue(key) {
            return this.fundamentalData[key] || '--';
        }
    }
};
</script>

<style scoped>
.container {
    padding: 20px;
    background-color: #f5f5f5;
}

.header {
    margin-bottom: 20px;
}

.stock-basic-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.stock-name {
    font-size: 24px;
    font-weight: bold;
    color: #333;
}

.stock-code {
    font-size: 14px;
    color: #666;
    margin-left: 10px;
}

.price {
    font-size: 24px;
    font-weight: bold;
    color: #333;
}

.change {
    font-size: 18px;
    margin-left: 10px;
}

.increase {
    color: #f56c6c;
}

.decrease {
    color: #4caf50;
}

.tab-nav {
    display: flex;
    background-color: #fff;
    border-radius: 8px;
    margin-bottom: 20px;
    overflow: hidden;
}

.tab-item {
    flex: 1;
    text-align: center;
    padding: 15px 0;
    position: relative;
}

.tab-item.active {
    color: #1989fa;
}

.tab-item.active::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 25%;
    width: 50%;
    height: 3px;
    background-color: #1989fa;
    border-radius: 3px;
}

.tab-text {
    font-size: 16px;
}

.detail-card {
    background-color: #fff;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.card-title {
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.title-text {
    font-size: 18px;
    font-weight: bold;
    color: #333;
}

.recommendation-details {
    display: flex;
    margin-bottom: 20px;
}

.score-box, .action-box {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.score-title, .action-title {
    font-size: 14px;
    color: #666;
    margin-bottom: 10px;
}

.score-circle {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 24px;
    font-weight: bold;
    color: #fff;
}

.high-score {
    background-color: #67c23a;
}

.medium-score {
    background-color: #e6a23c;
}

.low-score {
    background-color: #f56c6c;
}

.action-tag {
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 16px;
    font-weight: bold;
}

.strong-buy {
    background-color: #f56c6c;
    color: #fff;
}

.buy {
    background-color: #e6a23c;
    color: #fff;
}

.hold {
    background-color: #909399;
    color: #fff;
}

.sell {
    background-color: #4caf50;
    color: #fff;
}

.factor-analysis {
    margin-bottom: 20px;
}

.factor-title {
    font-size: 16px;
    color: #333;
    margin-bottom: 10px;
}

.factor-list {
    background-color: #f9f9f9;
    border-radius: 6px;
    padding: 15px;
}

.factor-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
}

.factor-item:last-child {
    margin-bottom: 0;
}

.factor-name {
    font-size: 14px;
    color: #333;
}

.factor-details {
    display: flex;
}

.factor-value {
    font-size: 14px;
    margin-right: 10px;
}

.factor-impact {
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 4px;
}

.positive {
    color: #f56c6c;
}

.negative {
    color: #4caf50;
}

.ai-summary {
    margin-bottom: 20px;
}

.summary-title {
    font-size: 16px;
    color: #333;
    margin-bottom: 10px;
}

.summary-content {
    font-size: 14px;
    color: #666;
    line-height: 1.6;
}

.trading-advice {
    background-color: #f9f9f9;
    border-radius: 6px;
    padding: 15px;
}

.advice-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
}

.advice-item:last-child {
    margin-bottom: 0;
}

.advice-type {
    font-size: 14px;
    color: #333;
}

.advice-content {
    font-size: 14px;
    color: #666;
}

.williams-analysis {
    margin-bottom: 20px;
}

.analysis-subtitle {
    font-size: 16px;
    color: #333;
    margin-bottom: 10px;
    display: block;
}

.williams-current {
    margin-bottom: 20px;
}

.williams-value-box {
    display: flex;
    align-items: center;
}

.williams-value {
    font-size: 24px;
    font-weight: bold;
    margin-right: 10px;
}

.overbought {
    color: #f56c6c;
}

.oversold {
    color: #4caf50;
}

.neutral {
    color: #e6a23c;
}

.williams-zone {
    font-size: 16px;
    color: #666;
}

.williams-chart {
    margin-bottom: 20px;
}

.chart-placeholder {
    height: 200px;
    background-color: #f1f1f1;
    border-radius: 6px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.placeholder-text {
    font-size: 14px;
    color: #999;
}

.williams-interpretation {
    margin-bottom: 20px;
}

.interpretation-text {
    font-size: 14px;
    color: #666;
    line-height: 1.6;
}

.signals-list {
    background-color: #f9f9f9;
    border-radius: 6px;
    padding: 15px;
}

.signal-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.signal-item:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
}

.signal-date {
    font-size: 14px;
    color: #333;
}

.signal-type {
    font-size: 14px;
    padding: 2px 8px;
    border-radius: 4px;
}

.signal-type.buy {
    background-color: #f56c6c;
    color: #fff;
}

.signal-type.sell {
    background-color: #4caf50;
    color: #fff;
}

.signal-result {
    font-size: 14px;
    font-weight: bold;
}

.signal-result.positive {
    color: #f56c6c;
}

.signal-result.negative {
    color: #4caf50;
}

.fundamental-data {
    background-color: #f9f9f9;
    border-radius: 6px;
    padding: 15px;
}

.data-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.data-row:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
}

.data-label {
    font-size: 14px;
    color: #333;
}

.data-value {
    font-size: 14px;
    color: #666;
}

.action-buttons {
    display: flex;
    justify-content: space-between;
}

.action-btn {
    flex: 1;
    height: 45px;
    line-height: 45px;
    text-align: center;
    border-radius: 8px;
    font-size: 16px;
    margin: 0 5px;
}

.action-btn.primary {
    background-color: #1989fa;
    color: #fff;
}

.action-btn.secondary {
    background-color: #f5f5f5;
    color: #333;
    border: 1px solid #ddd;
}
</style> 
