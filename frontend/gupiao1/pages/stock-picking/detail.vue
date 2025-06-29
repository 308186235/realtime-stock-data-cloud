<template>
    <view class="container">
        <view class="header">
            <view class="back-btn" @click="navigateBack">
                <text class="back-icon">←</text>
            </view>
            <view class="stock-info">
                <text class="stock-name">{{stock.name}}</text>
                <text class="stock-code">{{stock.code}}</text>
            </view>
            <view class="stock-price" :class="stock.change >= 0 ? 'up' : 'down'">
                <text class="price">{{stock.price}}</text>
                <text class="change">{{stock.change >= 0 ? '+' : ''}}{{stock.change}}%</text>
            </view>
        </view>
        
        <!-- 操作按钮 -->
        <view class="action-buttons">
            <view class="action-btn" @click="addToWatchlist">
                <view class="btn-icon watch-icon"></view>
                <text class="btn-text">加入自选</text>
            </view>
            <view class="action-btn" @click="showBuyDialog">
                <view class="btn-icon buy-icon"></view>
                <text class="btn-text">买入</text>
            </view>
            <view class="action-btn" @click="showSellDialog">
                <view class="btn-icon sell-icon"></view>
                <text class="btn-text">卖出</text>
            </view>
            <view class="action-btn" @click="showSetReminder">
                <view class="btn-icon reminder-icon"></view>
                <text class="btn-text">提醒</text>
            </view>
        </view>
        
        <!-- 选项卡 -->
        <view class="tab-menu">
            <view class="tab-item" :class="{ active: currentTab === 0 }" @click="changeTab(0)">
                <text class="tab-text">概览</text>
            </view>
            <view class="tab-item" :class="{ active: currentTab === 1 }" @click="changeTab(1)">
                <text class="tab-text">K线图表</text>
            </view>
            <view class="tab-item" :class="{ active: currentTab === 2 }" @click="changeTab(2)">
                <text class="tab-text">技术指标</text>
            </view>
            <view class="tab-item" :class="{ active: currentTab === 3 }" @click="changeTab(3)">
                <text class="tab-text">基本面</text>
            </view>
        </view>
        
        <!-- 概览选项卡 -->
        <view v-if="currentTab === 0" class="tab-content">
            <view class="detail-card">
                <view class="card-title">
                    <text class="title-text">股票概览</text>
                </view>
                <view class="stock-overview">
                    <view class="overview-row">
                        <view class="overview-item">
                            <text class="item-label">最新价</text>
                            <text class="item-value" :class="stock.change >= 0 ? 'up' : 'down'">{{stock.price}}</text>
                        </view>
                        <view class="overview-item">
                            <text class="item-label">涨跌幅</text>
                            <text class="item-value" :class="stock.change >= 0 ? 'up' : 'down'">{{stock.change >= 0 ? '+' : ''}}{{stock.change}}%</text>
                        </view>
                    </view>
                    <view class="overview-row">
                        <view class="overview-item">
                            <text class="item-label">开盘价</text>
                            <text class="item-value">{{stock.open}}</text>
                        </view>
                        <view class="overview-item">
                            <text class="item-label">昨收价</text>
                            <text class="item-value">{{stock.prevClose}}</text>
                        </view>
                    </view>
                    <view class="overview-row">
                        <view class="overview-item">
                            <text class="item-label">最高价</text>
                            <text class="item-value up">{{stock.high}}</text>
                        </view>
                        <view class="overview-item">
                            <text class="item-label">最低价</text>
                            <text class="item-value down">{{stock.low}}</text>
                        </view>
                    </view>
                    <view class="overview-row">
                        <view class="overview-item">
                            <text class="item-label">成交量</text>
                            <text class="item-value">{{stock.volume}}万手</text>
                        </view>
                        <view class="overview-item">
                            <text class="item-label">成交额</text>
                            <text class="item-value">{{stock.turnover}}亿</text>
                        </view>
                    </view>
                    <view class="overview-row">
                        <view class="overview-item">
                            <text class="item-label">市盈率</text>
                            <text class="item-value">{{stock.pe}}</text>
                        </view>
                        <view class="overview-item">
                            <text class="item-label">市净率</text>
                            <text class="item-value">{{stock.pb}}</text>
                        </view>
                    </view>
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
                <view class="chart-controls">
                    <view class="period-selector">
                        <view class="period-btn" :class="{ active: currentPeriod === 'day' }" @click="changePeriod('day')">
                            <text class="period-text">日线</text>
                        </view>
                        <view class="period-btn" :class="{ active: currentPeriod === 'week' }" @click="changePeriod('week')">
                            <text class="period-text">周线</text>
                        </view>
                        <view class="period-btn" :class="{ active: currentPeriod === 'month' }" @click="changePeriod('month')">
                            <text class="period-text">月线</text>
                        </view>
                    </view>
                    <view class="indicator-selector">
                        <view class="indicator-btn" :class="{ active: showVolume }" @click="toggleVolume">
                            <text class="indicator-text">成交量</text>
                        </view>
                        <view class="indicator-btn" :class="{ active: showMA }" @click="toggleMA">
                            <text class="indicator-text">均线</text>
                        </view>
                        <view class="indicator-btn" :class="{ active: showMACD }" @click="toggleMACD">
                            <text class="indicator-text">MACD</text>
                        </view>
                    </view>
                </view>
                
                <!-- 专业K线图表 -->
                <view class="pro-chart-container">
                    <!-- MA指标头部 -->
                    <view class="ma-indicator-bar">
                        <view class="ma-left">
                            <text class="ma-title">MA</text>
                            <text class="ma-item ma5">MA5:<text>1825.30</text><text class="arrow down">↓</text></text>
                            <text class="ma-item ma10">10:<text>1810.75</text><text class="arrow down">↓</text></text>
                            <text class="ma-item ma20">20:<text>1795.62</text><text class="arrow down">↓</text></text>
                            <text class="ma-item ma60">60:<text>1780.03</text><text class="arrow up">↑</text></text>
                        </view>
                        <view class="ma-right">
                            <text class="current-price">{{stock.price}}</text>
                        </view>
                    </view>
                    
                    <!-- 专业K线图表 -->
                    <view class="professional-chart">
                        <!-- 价格轴 -->
                        <view class="price-axis left">
                            <text class="price-label">{{Math.round(stock.price * 1.05)}}</text>
                            <text class="price-label">{{Math.round(stock.price * 1.025)}}</text>
                            <text class="price-label">{{Math.round(stock.price)}}</text>
                            <text class="price-label">{{Math.round(stock.price * 0.975)}}</text>
                            <text class="price-label">{{Math.round(stock.price * 0.95)}}</text>
                        </view>
                        
                        <!-- K线主图区域 -->
                        <view class="chart-main-area">
                            <!-- 网格线 -->
                            <view class="grid-lines">
                                <view class="grid-line"></view>
                                <view class="grid-line"></view>
                                <view class="grid-line"></view>
                                <view class="grid-line"></view>
                                <view class="grid-line"></view>
                                <view class="grid-line"></view>
                            </view>
                            
                            <!-- 蜡烛图 -->
                            <view class="candlestick-chart">
                                <!-- 蜡烛图示例 - 实际项目中应由Canvas API绘制 -->
                                <view class="candlestick red" style="left: 0%; height: 40px; top: 30%;">
                                    <view class="wick" style="height: 60px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 4%; height: 36px; top: 35%;">
                                    <view class="wick" style="height: 55px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 8%; height: 42px; top: 25%;">
                                    <view class="wick" style="height: 65px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 12%; height: 38px; top: 32%;">
                                    <view class="wick" style="height: 58px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 16%; height: 45px; top: 40%;">
                                    <view class="wick" style="height: 70px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 20%; height: 30px; top: 35%;">
                                    <view class="wick" style="height: 50px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 24%; height: 35px; top: 30%;">
                                    <view class="wick" style="height: 55px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 28%; height: 28px; top: 45%;">
                                    <view class="wick" style="height: 48px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 32%; height: 25px; top: 35%;">
                                    <view class="wick" style="height: 45px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 36%; height: 32px; top: 33%;">
                                    <view class="wick" style="height: 52px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 40%; height: 38px; top: 42%;">
                                    <view class="wick" style="height: 58px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 44%; height: 30px; top: 38%;">
                                    <view class="wick" style="height: 50px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 48%; height: 35px; top: 36%;">
                                    <view class="wick" style="height: 55px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 52%; height: 40px; top: 45%;">
                                    <view class="wick" style="height: 60px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 56%; height: 30px; top: 35%;">
                                    <view class="wick" style="height: 50px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 60%; height: 42px; top: 30%;">
                                    <view class="wick" style="height: 62px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 64%; height: 35px; top: 38%;">
                                    <view class="wick" style="height: 55px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 68%; height: 45px; top: 25%;">
                                    <view class="wick" style="height: 65px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 72%; height: 50px; top: 35%;">
                                    <view class="wick" style="height: 70px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 76%; height: 45px; top: 40%;">
                                    <view class="wick" style="height: 65px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 80%; height: 40px; top: 35%;">
                                    <view class="wick" style="height: 60px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 84%; height: 35px; top: 45%;">
                                    <view class="wick" style="height: 55px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 88%; height: 30px; top: 40%;">
                                    <view class="wick" style="height: 50px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 92%; height: 38px; top: 32%;">
                                    <view class="wick" style="height: 58px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 96%; height: 42px; top: 38%;">
                                    <view class="wick" style="height: 62px;"></view>
                                </view>
                            </view>
                            
                            <!-- MA线 -->
                            <view class="ma-lines">
                                <view class="ma-line ma5"></view>
                                <view class="ma-line ma10"></view>
                                <view class="ma-line ma20"></view>
                                <view class="ma-line ma60"></view>
                            </view>
                            
                            <!-- AI买卖点标记 -->
                            <view class="ai-signals">
                                <view class="ai-signal buy" style="left: 28%; top: 50%;">
                                    <text class="signal-label">AI买点 06-15 ¥1788</text>
                                </view>
                                <view class="ai-signal sell" style="left: 62%; top: 25%;">
                                    <text class="signal-label">AI卖点 06-25 ¥1830</text>
                                </view>
                                <view class="ai-signal buy" style="left: 86%; top: 45%;">
                                    <text class="signal-label">AI买点 07-05 ¥1795</text>
                                </view>
                            </view>
                            
                            <!-- 预测区域 -->
                            <view class="forecast-area"></view>
                        </view>
                        
                        <!-- 右侧价格轴 -->
                        <view class="price-axis right">
                            <text class="price-label">{{Math.round(stock.price * 1.05)}}</text>
                            <text class="price-label">{{Math.round(stock.price * 1.025)}}</text>
                            <text class="price-label">{{Math.round(stock.price)}}</text>
                            <text class="price-label">{{Math.round(stock.price * 0.975)}}</text>
                            <text class="price-label">{{Math.round(stock.price * 0.95)}}</text>
                        </view>
                    </view>
                    
                    <!-- 成交量图表 -->
                    <view class="volume-chart">
                        <view class="volume-bars">
                            <view class="volume-bar red" style="height: 40%; left: 0%"></view>
                            <view class="volume-bar green" style="height: 30%; left: 4%"></view>
                            <view class="volume-bar red" style="height: 60%; left: 8%"></view>
                            <view class="volume-bar red" style="height: 35%; left: 12%"></view>
                            <view class="volume-bar green" style="height: 45%; left: 16%"></view>
                            <view class="volume-bar red" style="height: 55%; left: 20%"></view>
                            <view class="volume-bar red" style="height: 40%; left: 24%"></view>
                            <view class="volume-bar green" style="height: 25%; left: 28%"></view>
                            <view class="volume-bar red" style="height: 35%; left: 32%"></view>
                            <view class="volume-bar red" style="height: 30%; left: 36%"></view>
                            <view class="volume-bar green" style="height: 45%; left: 40%"></view>
                            <view class="volume-bar red" style="height: 50%; left: 44%"></view>
                            <view class="volume-bar red" style="height: 35%; left: 48%"></view>
                            <view class="volume-bar green" style="height: 30%; left: 52%"></view>
                            <view class="volume-bar red" style="height: 40%; left: 56%"></view>
                            <view class="volume-bar red" style="height: 60%; left: 60%"></view>
                            <view class="volume-bar green" style="height: 35%; left: 64%"></view>
                            <view class="volume-bar red" style="height: 55%; left: 68%"></view>
                            <view class="volume-bar green" style="height: 70%; left: 72%"></view>
                            <view class="volume-bar green" style="height: 50%; left: 76%"></view>
                            <view class="volume-bar red" style="height: 40%; left: 80%"></view>
                            <view class="volume-bar green" style="height: 30%; left: 84%"></view>
                            <view class="volume-bar red" style="height: 25%; left: 88%"></view>
                            <view class="volume-bar red" style="height: 35%; left: 92%"></view>
                            <view class="volume-bar green" style="height: 45%; left: 96%"></view>
                        </view>
                    </view>
                    
                    <!-- 日期轴 -->
                    <view class="date-axis">
                        <text class="date-label">06-01</text>
                        <text class="date-label">06-08</text>
                        <text class="date-label">06-15</text>
                        <text class="date-label">06-22</text>
                        <text class="date-label">06-29</text>
                        <text class="date-label">今日</text>
                    </view>
                </view>
                
                <!-- OHLC信息 -->
                <view class="ohlc-info">
                    <view class="ohlc-item">
                        <text class="ohlc-label">开盘</text>
                        <text class="ohlc-value">{{stock.open}}</text>
                    </view>
                    <view class="ohlc-item">
                        <text class="ohlc-label">最高</text>
                        <text class="ohlc-value high">{{stock.high}}</text>
                    </view>
                    <view class="ohlc-item">
                        <text class="ohlc-label">最低</text>
                        <text class="ohlc-value low">{{stock.low}}</text>
                    </view>
                    <view class="ohlc-item">
                        <text class="ohlc-label">收盘</text>
                        <text class="ohlc-value close">{{stock.price}}</text>
                    </view>
                    <view class="ohlc-item">
                        <text class="ohlc-label">成交量</text>
                        <text class="ohlc-value">{{stock.volume}}万手</text>
                    </view>
                </view>
            </view>
        </view>
        
        <!-- 技术指标选项卡 -->
        <view v-if="currentTab === 2" class="tab-content">
            <view class="detail-card">
                <view class="card-title">
                    <text class="title-text">技术指标概览</text>
                </view>
                <view class="indicators-grid">
                    <view class="indicator-cell">
                        <text class="indicator-name">MACD</text>
                        <text class="indicator-value up">金叉(偏多)</text>
                    </view>
                    <view class="indicator-cell">
                        <text class="indicator-name">KDJ</text>
                        <text class="indicator-value up">金叉(偏多)</text>
                    </view>
                    <view class="indicator-cell">
                        <text class="indicator-name">RSI</text>
                        <text class="indicator-value">58.3(中性)</text>
                    </view>
                    <view class="indicator-cell">
                        <text class="indicator-name">BOLL</text>
                        <text class="indicator-value up">上轨突破</text>
                    </view>
                    <view class="indicator-cell">
                        <text class="indicator-name">MA</text>
                        <text class="indicator-value up">多头排列</text>
                    </view>
                    <view class="indicator-cell">
                        <text class="indicator-name">VOL</text>
                        <text class="indicator-value up">放量上涨</text>
                    </view>
                </view>
            </view>
            
            <view class="detail-card">
                <view class="card-title">
                    <text class="title-text">形态识别</text>
                </view>
                <view class="patterns-list">
                    <view class="pattern-item">
                        <view class="pattern-icon"></view>
                        <view class="pattern-info">
                            <text class="pattern-name">头肩底形态</text>
                            <text class="pattern-desc">1日K线显示可能形成头肩底形态,属于中长期看涨信号。</text>
                        </view>
                        <text class="pattern-confidence">76%</text>
                    </view>
                    <view class="pattern-item">
                        <view class="pattern-icon"></view>
                        <view class="pattern-info">
                            <text class="pattern-name">双底形态</text>
                            <text class="pattern-desc">近期K线显示可能形成双底形态,为较强的反转信号。</text>
                        </view>
                        <text class="pattern-confidence">68%</text>
                    </view>
                </view>
            </view>
        </view>
        
        <!-- 基本面选项卡 -->
        <view v-if="currentTab === 3" class="tab-content">
            <view class="detail-card">
                <view class="card-title">
                    <text class="title-text">公司概况</text>
                </view>
                <view class="company-info">
                    <text class="company-desc">{{stock.companyDesc}}</text>
                    <view class="company-data">
                        <view class="data-item">
                            <text class="data-label">所属行业</text>
                            <text class="data-value">{{stock.industry}}</text>
                        </view>
                        <view class="data-item">
                            <text class="data-label">总市值</text>
                            <text class="data-value">{{stock.marketCap}}亿</text>
                        </view>
                        <view class="data-item">
                            <text class="data-label">流通市值</text>
                            <text class="data-value">{{stock.floatMarketCap}}亿</text>
                        </view>
                    </view>
                </view>
            </view>
            
            <view class="detail-card">
                <view class="card-title">
                    <text class="title-text">财务指标</text>
                </view>
                <view class="financial-data">
                    <view class="financial-section">
                        <text class="section-title">盈利能力</text>
                        <view class="financial-row">
                            <view class="financial-item">
                                <text class="financial-label">ROE</text>
                                <text class="financial-value">{{stock.financials.roe}}%</text>
                            </view>
                            <view class="financial-item">
                                <text class="financial-label">毛利率</text>
                                <text class="financial-value">{{stock.financials.grossMargin}}%</text>
                            </view>
                        </view>
                        <view class="financial-row">
                            <view class="financial-item">
                                <text class="financial-label">净利率</text>
                                <text class="financial-value">{{stock.financials.netMargin}}%</text>
                            </view>
                            <view class="financial-item">
                                <text class="financial-label">EPS</text>
                                <text class="financial-value">{{stock.financials.eps}}元</text>
                            </view>
                        </view>
                    </view>
                    
                    <view class="financial-section">
                        <text class="section-title">成长能力</text>
                        <view class="financial-row">
                            <view class="financial-item">
                                <text class="financial-label">营收增长</text>
                                <text class="financial-value up">{{stock.financials.revenueGrowth}}%</text>
                            </view>
                            <view class="financial-item">
                                <text class="financial-label">净利润增长</text>
                                <text class="financial-value up">{{stock.financials.profitGrowth}}%</text>
                            </view>
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
            stock: {
                name: '贵州茅台',
                code: '600519',
                price: 1826.50,
                change: 2.34,
                open: 1785.00,
                prevClose: 1785.00,
                high: 1830.20,
                low: 1778.55,
                volume: 24.6,
                turnover: 45.2,
                pe: 28.65,
                pb: 9.82,
                industry: '白酒',
                marketCap: 22954.2,
                floatMarketCap: 22954.2,
                companyDesc: '贵州茅台酒股份有限公司是国内知名白酒生产企业,主要生产销售茅台酒系列产品,是中国白酒行业的龙头企业。',
                financials: {
                    roe: 15.32,
                    grossMargin: 91.4,
                    netMargin: 51.8,
                    eps: 43.65,
                    revenueGrowth: 12.5,
                    profitGrowth: 15.8
                }
            },
            currentTab: 0,
            currentPeriod: 'day',
            showVolume: true,
            showMA: true,
            showMACD: false
        }
    },
    onLoad(options) {
        // 从路由参数获取股票代码和名称
        if (options.code && options.name) {
            // 在实际应用中,这里应该使用股票代码获取完整的股票数据
            this.stock.code = options.code;
            this.stock.name = options.name;
        }
    },
    methods: {
        // 导航回上一页
        navigateBack() {
            uni.navigateBack();
        },
        
        // 更改选项卡
        changeTab(index) {
            this.currentTab = index;
        },
        
        // 更改K线周期
        changePeriod(period) {
            this.currentPeriod = period;
        },
        
        // 切换成交量显示
        toggleVolume() {
            this.showVolume = !this.showVolume;
        },
        
        // 切换均线显示
        toggleMA() {
            this.showMA = !this.showMA;
        },
        
        // 切换MACD显示
        toggleMACD() {
            this.showMACD = !this.showMACD;
        },
        
        // 加入自选
        addToWatchlist() {
            uni.showToast({
                title: '已加入自选',
                icon: 'success'
            });
        },
        
        // 显示买入对话框
        showBuyDialog() {
            uni.showToast({
                title: '买入功能暂未实现',
                icon: 'none'
            });
        },
        
        // 显示卖出对话框
        showSellDialog() {
            uni.showToast({
                title: '卖出功能暂未实现',
                icon: 'none'
            });
        },
        
        // 显示设置提醒
        showSetReminder() {
            uni.showToast({
                title: '提醒功能暂未实现',
                icon: 'none'
            });
        },
        
        // 获取交易策略
        getTradingStrategy() {
            // 根据股票涨跌幅模拟不同的交易策略
            if (this.stock.change > 2) {
                return '短线持有,逢高考虑减仓';
            } else if (this.stock.change > 0) {
                return '逢低吸纳,持续加仓';
            } else if (this.stock.change > -2) {
                return '观望为主,关注支撑位表现';
            } else {
                return '等待企稳信号,暂不介入';
            }
        },
        
        // 获取仓位建议
        getPositionAdvice() {
            // 模拟仓位建议
            if (this.stock.change > 3) {
                return '建议仓位 20%';
            } else if (this.stock.change > 1) {
                return '建议仓位 40%';
            } else if (this.stock.change > -1) {
                return '建议仓位 30%';
            } else {
                return '建议仓位 10%';
            }
        }
    }
}
</script>

<style>
.container {
    padding: 0;
    background-color: #141414;
    min-height: 100vh;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx 30rpx;
    background-color: #222222;
    border-bottom: 1px solid #333333;
}

.back-btn {
    width: 60rpx;
    height: 60rpx;
    display: flex;
    justify-content: center;
    align-items: center;
}

.back-icon {
    font-size: 40rpx;
    color: #ffffff;
}

.stock-info {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stock-name {
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 5rpx;
}

.stock-code {
    font-size: 24rpx;
    color: #999999;
}

.stock-price {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}

.price {
    font-size: 32rpx;
    font-weight: bold;
    margin-bottom: 5rpx;
}

.change {
    font-size: 24rpx;
}

.up {
    color: #ff5252;
}

.down {
    color: #4caf50;
}

/* 操作按钮 */
.action-buttons {
    display: flex;
    justify-content: space-between;
    padding: 20rpx 30rpx;
    background-color: #222222;
    margin-bottom: 20rpx;
}

.action-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.btn-icon {
    width: 60rpx;
    height: 60rpx;
    border-radius: 30rpx;
    margin-bottom: 10rpx;
}

.watch-icon {
    background-color: #64b5f6;
}

.buy-icon {
    background-color: #ff5252;
}

.sell-icon {
    background-color: #4caf50;
}

.reminder-icon {
    background-color: #ffc107;
}

.btn-text {
    font-size: 24rpx;
    color: #cccccc;
}

/* 选项卡 */
.tab-menu {
    display: flex;
    background-color: #222222;
    margin-bottom: 20rpx;
}

.tab-item {
    flex: 1;
    text-align: center;
    padding: 20rpx 0;
    border-bottom: 3rpx solid transparent;
}

.tab-item.active {
    border-bottom-color: #4c8dff;
}

.tab-text {
    font-size: 28rpx;
    color: #cccccc;
}

.active .tab-text {
    color: #4c8dff;
    font-weight: bold;
}

/* 选项卡内容 */
.tab-content {
    padding: 0 30rpx 30rpx;
}

.detail-card {
    background-color: #222222;
    border-radius: 12rpx;
    padding: 20rpx;
    margin-bottom: 20rpx;
}

.card-title {
    margin-bottom: 20rpx;
}

.title-text {
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
}

/* 股票概览 */
.stock-overview {
    display: flex;
    flex-direction: column;
}

.overview-row {
    display: flex;
    margin-bottom: 15rpx;
}

.overview-row:last-child {
    margin-bottom: 0;
}

.overview-item {
    flex: 1;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.item-label {
    font-size: 26rpx;
    color: #999999;
}

.item-value {
    font-size: 26rpx;
    color: #ffffff;
    font-weight: bold;
}

/* 交易建议 */
.trading-advice {
    display: flex;
    flex-direction: column;
}

.advice-item {
    display: flex;
    justify-content: space-between;
    padding: 12rpx 0;
    border-bottom: 1px solid #333333;
}

.advice-item:last-child {
    border-bottom: none;
}

.advice-type {
    font-size: 26rpx;
    color: #999999;
}

.advice-content {
    font-size: 26rpx;
    color: #ffffff;
    font-weight: bold;
}

/* K线图表 */
.chart-controls {
    display: flex;
    flex-direction: column;
}

.period-selector {
    display: flex;
    margin-bottom: 15rpx;
}

.period-btn {
    flex: 1;
    text-align: center;
    padding: 10rpx 0;
    background-color: #333333;
    margin-right: 10rpx;
    border-radius: 6rpx;
}

.period-btn:last-child {
    margin-right: 0;
}

.period-btn.active {
    background-color: #4c8dff;
}

.period-text {
    font-size: 24rpx;
    color: #cccccc;
}

.active .period-text {
    color: #ffffff;
}

.indicator-selector {
    display: flex;
}

.indicator-btn {
    flex: 1;
    text-align: center;
    padding: 10rpx 0;
    background-color: #333333;
    margin-right: 10rpx;
    border-radius: 6rpx;
}

.indicator-btn:last-child {
    margin-right: 0;
}

.indicator-btn.active {
    background-color: #4c8dff;
}

.indicator-text {
    font-size: 24rpx;
    color: #cccccc;
}

.active .indicator-text {
    color: #ffffff;
}

/* 技术指标 */
.indicators-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-gap: 20rpx;
}

.indicator-cell {
    background-color: #333333;
    border-radius: 8rpx;
    padding: 15rpx;
    display: flex;
    flex-direction: column;
}

.indicator-name {
    font-size: 26rpx;
    color: #999999;
    margin-bottom: 10rpx;
}

.indicator-value {
    font-size: 28rpx;
    color: #ffffff;
    font-weight: bold;
}

/* 形态识别 */
.patterns-list {
    display: flex;
    flex-direction: column;
}

.pattern-item {
    display: flex;
    align-items: center;
    padding: 15rpx 0;
    border-bottom: 1px solid #333333;
}

.pattern-item:last-child {
    border-bottom: none;
}

.pattern-icon {
    width: 60rpx;
    height: 60rpx;
    background-color: #7986cb;
    border-radius: 30rpx;
    margin-right: 15rpx;
}

.pattern-info {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.pattern-name {
    font-size: 28rpx;
    color: #ffffff;
    margin-bottom: 5rpx;
}

.pattern-desc {
    font-size: 24rpx;
    color: #999999;
}

.pattern-confidence {
    font-size: 28rpx;
    color: #4c8dff;
    font-weight: bold;
}

/* 公司信息 */
.company-info {
    display: flex;
    flex-direction: column;
}

.company-desc {
    font-size: 26rpx;
    color: #ffffff;
    line-height: 1.5;
    margin-bottom: 20rpx;
}

.company-data {
    display: flex;
    flex-direction: column;
}

.data-item {
    display: flex;
    justify-content: space-between;
    padding: 10rpx 0;
    border-bottom: 1px solid #333333;
}

.data-item:last-child {
    border-bottom: none;
}

.data-label {
    font-size: 26rpx;
    color: #999999;
}

.data-value {
    font-size: 26rpx;
    color: #ffffff;
    font-weight: bold;
}

/* 财务指标 */
.financial-data {
    display: flex;
    flex-direction: column;
}

.financial-section {
    margin-bottom: 20rpx;
}

.financial-section:last-child {
    margin-bottom: 0;
}

.section-title {
    font-size: 28rpx;
    color: #ffffff;
    margin-bottom: 15rpx;
}

.financial-row {
    display: flex;
    margin-bottom: 10rpx;
}

.financial-row:last-child {
    margin-bottom: 0;
}

.financial-item {
    flex: 1;
    display: flex;
    justify-content: space-between;
    background-color: #333333;
    border-radius: 6rpx;
    padding: 10rpx 15rpx;
    margin-right: 10rpx;
}

.financial-item:last-child {
    margin-right: 0;
}

.financial-label {
    font-size: 24rpx;
    color: #999999;
}

.financial-value {
    font-size: 24rpx;
    color: #ffffff;
    font-weight: bold;
}

/* 专业K线图表 */
.pro-chart-container {
    position: relative;
    height: 400rpx;
    background-color: #333333;
    border-radius: 8rpx;
    margin-bottom: 20rpx;
}

.ma-indicator-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10rpx;
}

.ma-left {
    display: flex;
    flex-direction: column;
}

.ma-title {
    font-size: 28rpx;
    color: #ffffff;
    margin-bottom: 10rpx;
}

.ma-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5rpx;
}

.ma-left .ma-item {
    font-size: 24rpx;
    color: #999999;
}

.ma-right {
    font-size: 28rpx;
    color: #ffffff;
    font-weight: bold;
}

.current-price {
    font-size: 28rpx;
    color: #ffffff;
    font-weight: bold;
}

.professional-chart {
    position: absolute;
    top: 40rpx;
    left: 10rpx;
    right: 10rpx;
    bottom: 10rpx;
}

.price-axis {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}

.price-axis.left {
    left: 10rpx;
}

.price-axis.right {
    right: 10rpx;
}

.price-label {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 24rpx;
    color: #999999;
}

.chart-main-area {
    position: relative;
}

.grid-lines {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}

.grid-line {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background-color: #333333;
}

.candlestick-chart {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}

.candlestick {
    position: absolute;
}

.candlestick.red {
    background-color: #ff5252;
}

.candlestick.green {
    background-color: #4caf50;
}

.wick {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 100%;
    background-color: #ffffff;
}

.ma-lines {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}

.ma-line {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background-color: #ffffff;
}

.ai-signals {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}

.ai-signal {
    position: absolute;
    width: 10rpx;
    height: 10rpx;
    border-radius: 50%;
}

.ai-signal.buy {
    background-color: #4caf50;
    border: 2rpx solid #ffffff;
}

.ai-signal.sell {
    background-color: #ff5252;
    border: 2rpx solid #ffffff;
}

.signal-label {
    position: absolute;
    top: -30rpx;
    left: -40rpx;
    text-align: center;
    font-size: 16rpx;
    color: #ffffff;
    background-color: rgba(0, 0, 0, 0.7);
    padding: 4rpx 8rpx;
    border-radius: 4rpx;
    white-space: nowrap;
    z-index: 10;
}

.forecast-area {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 8rpx;
}

.volume-chart {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}

.volume-bars {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}

.volume-bar {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 100%;
    background-color: #ffffff;
}

.volume-bar.red {
    background-color: #ff5252;
}

.volume-bar.green {
    background-color: #4caf50;
}

.date-axis {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10rpx;
}

.date-label {
    font-size: 24rpx;
    color: #999999;
}

.ohlc-info {
    display: flex;
    justify-content: space-between;
    padding: 10rpx;
    background-color: #333333;
    border-radius: 6rpx;
    margin-top: 20rpx;
}

.ohlc-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.ohlc-label {
    font-size: 24rpx;
    color: #999999;
    margin-bottom: 5rpx;
}

.ohlc-value {
    font-size: 24rpx;
    color: #ffffff;
    font-weight: bold;
}

.ohlc-value.high {
    color: #ff5252;
}

.ohlc-value.low {
    color: #4caf50;
}

.ohlc-value.close {
    color: #ffffff;
}
</style> 
