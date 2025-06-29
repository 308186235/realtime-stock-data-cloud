<template>
    <view :class="['container', isDarkMode ? 'dark-theme' : 'light-theme']">
        <view class="header">
            <view class="title">Agent智能交易系统</view>
            <view class="subtitle">智能选股 · 量化交易 · 数据分析</view>
        </view>

        <!-- 后端连接状态 -->
        <BackendConnectionStatus />
        
        <!-- 高级功能卡片 -->
        <view class="premium-features">
            <view class="feature-card ai-feature" @click="navigateTo('/pages/ai-analysis/index')">
                <view class="feature-icon ai-icon"></view>
                <view class="feature-content">
                    <text class="feature-title">Agent分析控制台</text>
                    <text class="feature-desc">基于AI的智能决策交易系统</text>
                </view>
                <view class="arrow-right"></view>
            </view>
            
            <view class="feature-card trade-feature" @click="navigateTo('/pages/trade/index')">
                <view class="feature-icon trade-icon"></view>
                <view class="feature-content">
                    <text class="feature-title">交易中心</text>
                    <text class="feature-desc">东吴证券同花顺交易通道</text>
                </view>
                <view class="arrow-right"></view>
            </view>
            
            <view class="feature-card t0-feature" @click="navigateTo('/pages/auto-trader/index')">
                <view class="feature-icon t0-icon"></view>
                <view class="feature-content">
                    <text class="feature-title">T+0交易</text>
                    <text class="feature-desc">当日买卖,自动交易系统</text>
                </view>
                <view class="arrow-right"></view>
            </view>

            <view class="feature-card test-feature" @click="goToTestPage">
                <view class="feature-icon test-icon"></view>
                <view class="feature-content">
                    <text class="feature-title">🧪 数据测试</text>
                    <text class="feature-desc">测试回测功能和股票数据获取</text>
                </view>
                <view class="arrow-right"></view>
            </view>
        </view>
        
        <!-- 市场概览 -->
        <view class="market-overview">
            <view class="card-title">
                <text class="title-text">市场概览</text>
                <view class="update-info" v-if="lastUpdateTime">
                    <text class="update-time">{{ lastUpdateTime }}</text>
                    <view class="loading-indicator" v-if="loading"></view>
                </view>
            </view>
            <view class="indices">
                <view
                    v-for="(index, i) in marketIndices"
                    :key="i"
                    class="index-card"
                    :class="index.trend"
                >
                    <text class="index-name">{{ index.name }}</text>
                    <text class="index-value">{{ index.value }}</text>
                    <text class="index-change">{{ index.change }}</text>
                </view>
            </view>
        </view>
        
        <!-- Agent智能选股 -->
        <view class="stock-recommendation">
            <view class="card-title">
                <text class="title-text">智能选股推荐</text>
                <text class="refresh-btn" @click="refreshData" :class="{ loading: loading }">
                    {{ loading ? '刷新中...' : '刷新' }}
                </text>
            </view>
            <view class="stock-list">
                <view
                    v-for="(stock, i) in recommendedStocks"
                    :key="i"
                    class="stock-item"
                    @click="navigateTo('/pages/stock-picking/detail')"
                >
                    <view class="stock-info">
                        <text class="stock-name">{{ stock.name }}</text>
                        <text class="stock-code">{{ stock.code }}</text>
                    </view>
                    <view class="stock-price">
                        <text class="price" :class="stock.trend">{{ stock.price }}</text>
                        <text class="change" :class="stock.trend">{{ stock.change }}</text>
                    </view>
                </view>
            </view>
        </view>
        
        <!-- 功能快捷方式 -->
        <view class="feature-shortcuts">
            <view class="shortcut-row">
                <view class="shortcut-item" @click="navigateTo('/pages/ai-analysis/index')">
                    <view class="shortcut-icon ai-icon"></view>
                    <text class="shortcut-text">Agent智能交易</text>
                </view>
                <view class="shortcut-item" @click="navigateTo('/pages/portfolio/index')">
                    <view class="shortcut-icon portfolio-icon"></view>
                    <text class="shortcut-text">我的持仓</text>
                </view>
            </view>
            <view class="shortcut-row">
                <view class="shortcut-item" @click="navigateTo('/pages/device-test/index')">
                    <view class="shortcut-icon test-icon"></view>
                    <text class="shortcut-text">设备测试</text>
                </view>
            </view>
            <view class="shortcut-row">
                <view class="shortcut-item" @click="navigateTo('/pages/trade/index')">
                    <view class="shortcut-icon trade-icon"></view>
                    <text class="shortcut-text">Agent交易中心</text>
                </view>
                <view class="shortcut-item" @click="navigateTo('/pages/indicators/index')">
                    <view class="shortcut-icon indicator-icon"></view>
                    <text class="shortcut-text">技术指标</text>
                </view>
                <view class="shortcut-item" @click="navigateTo('/pages/auto-trader/index')">
                    <view class="shortcut-icon auto-icon"></view>
                    <text class="shortcut-text">Agent T+0交易</text>
                </view>
            </view>
        </view>
        
        <!-- 热门股票K线图 -->
        <view class="stock-charts-section">
            <view class="card-title">
                <text class="title-text">热门股票行情</text>
                <text class="view-more" @click="navigateTo('/pages/stock-picking/index')">查看更多</text>
            </view>
            
            <!-- 贵州茅台K线图 -->
            <view class="stock-chart-card" @click="navigateTo('/pages/stock-picking/detail?code=600519&name=贵州茅台')">
                <!-- 股票标题信息 -->
                <view class="chart-header">
                    <view class="stock-basic-info">
                        <text class="stock-name">贵州茅台</text>
                        <text class="stock-code">600519</text>
                    </view>
                    <view class="stock-price-info">
                        <text class="price up">1826.50</text>
                        <text class="change up">+2.34% (+42.50)</text>
                    </view>
                </view>
                
                <!-- 专业K线图 -->
                <view class="pro-chart-container">
                    <!-- MA指标头部 -->
                    <view class="ma-indicator-bar">
                        <view class="ma-left">
                            <text class="ma-title">MA</text>
                            <text class="ma-item ma5">MA5:1825.30<text class="arrow down">↓</text></text>
                            <text class="ma-item ma10">10:1810.75<text class="arrow down">↓</text></text>
                            <text class="ma-item ma20">20:1795.62<text class="arrow down">↓</text></text>
                            <text class="ma-item ma60">60:1780.03<text class="arrow up">↑</text></text>
                        </view>
                        <view class="ma-right">
                            <text class="current-price">1826.50</text>
                        </view>
                    </view>
                    
                    <!-- K线图表主体 -->
                    <view class="professional-chart">
                        <!-- 左侧价格轴 -->
                        <view class="price-axis left">
                            <text class="price-label">1918</text>
                            <text class="price-label">1872</text>
                            <text class="price-label">1826</text>
                            <text class="price-label">1781</text>
                            <text class="price-label">1735</text>
                        </view>
                        
                        <!-- 主图区域 -->
                        <view class="chart-main-area">
                            <!-- 网格线 -->
                            <view class="grid-lines">
                                <view class="grid-line"></view>
                                <view class="grid-line"></view>
                                <view class="grid-line"></view>
                                <view class="grid-line"></view>
                                <view class="grid-line"></view>
                            </view>
                            
                            <!-- 蜡烛图 -->
                            <view class="candlestick-chart">
                                <view class="candlestick red" style="left: 5%; height: 20px; top: 30%;">
                                    <view class="wick" style="height: 40px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 10%; height: 15px; top: 35%;">
                                    <view class="wick" style="height: 30px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 15%; height: 25px; top: 28%;">
                                    <view class="wick" style="height: 45px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 20%; height: 18px; top: 33%;">
                                    <view class="wick" style="height: 35px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 25%; height: 22px; top: 40%;">
                                    <view class="wick" style="height: 38px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 30%; height: 28px; top: 30%;">
                                    <view class="wick" style="height: 48px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 35%; height: 15px; top: 32%;">
                                    <view class="wick" style="height: 30px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 40%; height: 20px; top: 38%;">
                                    <view class="wick" style="height: 40px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 45%; height: 25px; top: 42%;">
                                    <view class="wick" style="height: 45px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 50%; height: 30px; top: 30%;">
                                    <view class="wick" style="height: 50px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 55%; height: 25px; top: 28%;">
                                    <view class="wick" style="height: 45px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 60%; height: 22px; top: 36%;">
                                    <view class="wick" style="height: 42px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 65%; height: 18px; top: 40%;">
                                    <view class="wick" style="height: 35px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 70%; height: 15px; top: 35%;">
                                    <view class="wick" style="height: 30px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 75%; height: 20px; top: 38%;">
                                    <view class="wick" style="height: 40px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 80%; height: 28px; top: 42%;">
                                    <view class="wick" style="height: 48px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 85%; height: 25px; top: 45%;">
                                    <view class="wick" style="height: 45px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 90%; height: 22px; top: 48%;">
                                    <view class="wick" style="height: 42px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 95%; height: 20px; top: 35%;">
                                    <view class="wick" style="height: 40px;"></view>
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
                                <view class="ai-signal buy" style="left: 40%; top: 45%;">
                                    <text class="signal-label">AI买点</text>
                                </view>
                                <view class="ai-signal sell" style="left: 70%; top: 32%;">
                                    <text class="signal-label">AI卖点</text>
                                </view>
                            </view>
                        </view>
                        
                        <!-- 右侧价格轴 -->
                        <view class="price-axis right">
                            <text class="price-label">1918</text>
                            <text class="price-label">1872</text>
                            <text class="price-label">1826</text>
                            <text class="price-label">1781</text>
                            <text class="price-label">1735</text>
                        </view>
                    </view>
                    
                    <!-- 成交量 -->
                    <view class="volume-chart">
                        <view class="volume-bars">
                            <view class="volume-bar red" style="height: 40%; left: 5%"></view>
                            <view class="volume-bar green" style="height: 30%; left: 10%"></view>
                            <view class="volume-bar red" style="height: 50%; left: 15%"></view>
                            <view class="volume-bar green" style="height: 35%; left: 20%"></view>
                            <view class="volume-bar green" style="height: 40%; left: 25%"></view>
                            <view class="volume-bar red" style="height: 60%; left: 30%"></view>
                            <view class="volume-bar red" style="height: 25%; left: 35%"></view>
                            <view class="volume-bar green" style="height: 35%; left: 40%"></view>
                            <view class="volume-bar green" style="height: 45%; left: 45%"></view>
                            <view class="volume-bar red" style="height: 55%; left: 50%"></view>
                            <view class="volume-bar red" style="height: 40%; left: 55%"></view>
                            <view class="volume-bar green" style="height: 35%; left: 60%"></view>
                            <view class="volume-bar green" style="height: 30%; left: 65%"></view>
                            <view class="volume-bar red" style="height: 25%; left: 70%"></view>
                            <view class="volume-bar green" style="height: 35%; left: 75%"></view>
                            <view class="volume-bar green" style="height: 50%; left: 80%"></view>
                            <view class="volume-bar green" style="height: 40%; left: 85%"></view>
                            <view class="volume-bar green" style="height: 35%; left: 90%"></view>
                            <view class="volume-bar red" style="height: 45%; left: 95%"></view>
                        </view>
                    </view>
                    
                    <!-- 日期轴 -->
                    <view class="date-axis">
                        <text class="date-label">06-01</text>
                        <text class="date-label">06-15</text>
                        <text class="date-label">07-01</text>
                        <text class="date-label">07-15</text>
                        <text class="date-label">今日</text>
                    </view>
                </view>
                
                <!-- 交易按钮 -->
                <view class="chart-actions">
                    <view class="action-button buy">买入</view>
                    <view class="action-button sell">卖出</view>
                    <view class="action-button analyze">分析</view>
                </view>
            </view>
            
            <!-- 腾讯控股K线图 -->
            <view class="stock-chart-card" @click="navigateTo('/pages/stock-picking/detail?code=00700&name=腾讯控股')">
                <!-- 股票标题信息 -->
                <view class="chart-header">
                    <view class="stock-basic-info">
                        <text class="stock-name">腾讯控股</text>
                        <text class="stock-code">00700</text>
                    </view>
                    <view class="stock-price-info">
                        <text class="price down">365.80</text>
                        <text class="change down">-1.25% (-4.60)</text>
                    </view>
                </view>
                
                <!-- 专业K线图 -->
                <view class="pro-chart-container">
                    <!-- MA指标头部 -->
                    <view class="ma-indicator-bar">
                        <view class="ma-left">
                            <text class="ma-title">MA</text>
                            <text class="ma-item ma5">MA5:368.20<text class="arrow down">↓</text></text>
                            <text class="ma-item ma10">10:370.15<text class="arrow down">↓</text></text>
                            <text class="ma-item ma20">20:372.40<text class="arrow up">↑</text></text>
                            <text class="ma-item ma60">60:375.80<text class="arrow up">↑</text></text>
                        </view>
                        <view class="ma-right">
                            <text class="current-price">365.80</text>
                        </view>
                    </view>
                    
                    <!-- K线图表主体 -->
                    <view class="professional-chart">
                        <!-- 左侧价格轴 -->
                        <view class="price-axis left">
                            <text class="price-label">384</text>
                            <text class="price-label">375</text>
                            <text class="price-label">366</text>
                            <text class="price-label">357</text>
                            <text class="price-label">348</text>
                        </view>
                        
                        <!-- 主图区域 -->
                        <view class="chart-main-area">
                            <!-- 网格线 -->
                            <view class="grid-lines">
                                <view class="grid-line"></view>
                                <view class="grid-line"></view>
                                <view class="grid-line"></view>
                                <view class="grid-line"></view>
                                <view class="grid-line"></view>
                            </view>
                            
                            <!-- 蜡烛图 -->
                            <view class="candlestick-chart">
                                <view class="candlestick green" style="left: 5%; height: 20px; top: 40%;">
                                    <view class="wick" style="height: 40px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 10%; height: 15px; top: 42%;">
                                    <view class="wick" style="height: 30px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 15%; height: 25px; top: 45%;">
                                    <view class="wick" style="height: 45px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 20%; height: 18px; top: 35%;">
                                    <view class="wick" style="height: 35px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 25%; height: 22px; top: 30%;">
                                    <view class="wick" style="height: 38px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 30%; height: 28px; top: 25%;">
                                    <view class="wick" style="height: 48px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 35%; height: 15px; top: 32%;">
                                    <view class="wick" style="height: 30px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 40%; height: 20px; top: 38%;">
                                    <view class="wick" style="height: 40px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 45%; height: 25px; top: 30%;">
                                    <view class="wick" style="height: 45px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 50%; height: 30px; top: 25%;">
                                    <view class="wick" style="height: 50px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 55%; height: 25px; top: 35%;">
                                    <view class="wick" style="height: 45px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 60%; height: 22px; top: 40%;">
                                    <view class="wick" style="height: 42px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 65%; height: 18px; top: 35%;">
                                    <view class="wick" style="height: 35px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 70%; height: 15px; top: 30%;">
                                    <view class="wick" style="height: 30px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 75%; height: 20px; top: 25%;">
                                    <view class="wick" style="height: 40px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 80%; height: 28px; top: 20%;">
                                    <view class="wick" style="height: 48px;"></view>
                                </view>
                                <view class="candlestick green" style="left: 85%; height: 25px; top: 30%;">
                                    <view class="wick" style="height: 45px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 90%; height: 22px; top: 25%;">
                                    <view class="wick" style="height: 42px;"></view>
                                </view>
                                <view class="candlestick red" style="left: 95%; height: 20px; top: 22%;">
                                    <view class="wick" style="height: 40px;"></view>
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
                                <view class="ai-signal buy" style="left: 55%; top: 45%;">
                                    <text class="signal-label">AI买点</text>
                                </view>
                                <view class="ai-signal sell" style="left: 80%; top: 15%;">
                                    <text class="signal-label">AI卖点</text>
                                </view>
                            </view>
                        </view>
                        
                        <!-- 右侧价格轴 -->
                        <view class="price-axis right">
                            <text class="price-label">384</text>
                            <text class="price-label">375</text>
                            <text class="price-label">366</text>
                            <text class="price-label">357</text>
                            <text class="price-label">348</text>
                        </view>
                    </view>
                    
                    <!-- 成交量 -->
                    <view class="volume-chart">
                        <view class="volume-bars">
                            <view class="volume-bar green" style="height: 40%; left: 5%"></view>
                            <view class="volume-bar green" style="height: 30%; left: 10%"></view>
                            <view class="volume-bar green" style="height: 50%; left: 15%"></view>
                            <view class="volume-bar red" style="height: 35%; left: 20%"></view>
                            <view class="volume-bar red" style="height: 40%; left: 25%"></view>
                            <view class="volume-bar red" style="height: 60%; left: 30%"></view>
                            <view class="volume-bar green" style="height: 25%; left: 35%"></view>
                            <view class="volume-bar green" style="height: 35%; left: 40%"></view>
                            <view class="volume-bar red" style="height: 45%; left: 45%"></view>
                            <view class="volume-bar red" style="height: 55%; left: 50%"></view>
                            <view class="volume-bar green" style="height: 40%; left: 55%"></view>
                            <view class="volume-bar green" style="height: 35%; left: 60%"></view>
                            <view class="volume-bar red" style="height: 30%; left: 65%"></view>
                            <view class="volume-bar red" style="height: 25%; left: 70%"></view>
                            <view class="volume-bar red" style="height: 35%; left: 75%"></view>
                            <view class="volume-bar red" style="height: 80%; left: 80%"></view>
                            <view class="volume-bar green" style="height: 60%; left: 85%"></view>
                            <view class="volume-bar red" style="height: 35%; left: 90%"></view>
                            <view class="volume-bar red" style="height: 45%; left: 95%"></view>
                        </view>
                    </view>
                    
                    <!-- 日期轴 -->
                    <view class="date-axis">
                        <text class="date-label">06-01</text>
                        <text class="date-label">06-15</text>
                        <text class="date-label">07-01</text>
                        <text class="date-label">07-15</text>
                        <text class="date-label">今日</text>
                    </view>
                </view>
                
                <!-- 交易按钮 -->
                <view class="chart-actions">
                    <view class="action-button buy">买入</view>
                    <view class="action-button sell">卖出</view>
                    <view class="action-button analyze">分析</view>
                    <view class="action-button test" @click="goToTestPage">数据测试</view>
                </view>
            </view>
        </view>

        <!-- 浮动测试按钮 -->
        <view class="floating-test-btn" @click="goToTestPage">
            <text class="floating-btn-text">🧪 测试</text>
        </view>

        <!-- 真实数据错误提示 -->
        <RealDataErrorAlert
            :visible="showDataError"
            :errorMessage="dataErrorMessage"
            @close="hideDataError"
            @retry="retryDataConnection" />
    </view>
</template>

<script>
import BackendConnectionStatus from '@/components/BackendConnectionStatus.vue'
import RealDataErrorAlert from '@/components/RealDataErrorAlert.vue'
import dataService from '@/services/dataService.js'

export default {
    components: {
        BackendConnectionStatus,
        RealDataErrorAlert
    },
    data() {
        return {
            isDarkMode: false,
            // 市场数据
            marketIndices: [
                { name: '上证指数', value: '3,458.23', change: '+1.35%', trend: 'up' },
                { name: '深证成指', value: '14,256.89', change: '+1.62%', trend: 'up' },
                { name: '创业板指', value: '2,876.45', change: '-0.32%', trend: 'down' }
            ],
            // 推荐股票
            recommendedStocks: [
                { name: '贵州茅台', code: '600519', price: '1826.50', change: '+2.34%', trend: 'up' },
                { name: '比亚迪', code: '002594', price: '241.85', change: '+1.58%', trend: 'up' },
                { name: '宁德时代', code: '300750', price: '187.36', change: '-0.75%', trend: 'down' }
            ],
            // 加载状态
            loading: false,
            lastUpdateTime: null,
            // 真实数据错误提示
            showDataError: false,
            dataErrorMessage: ''
        }
    },
    onLoad() {
        // 获取当前主题设置
        const app = getApp();
        this.isDarkMode = app.globalData.isDarkMode;

        // 加载数据
        this.loadData();

        // 测试数据获取功能
        this.testDataFunctions();
    },
    onShow() {
        // 每次显示页面时检查当前主题
        const app = getApp();
        this.isDarkMode = app.globalData.isDarkMode;

        // 刷新数据
        this.refreshData();
    },
    onPullDownRefresh() {
        // 下拉刷新
        this.refreshData().finally(() => {
            uni.stopPullDownRefresh();
        });
    },
    methods: {
        // 页面导航
        navigateTo(url) {
            uni.navigateTo({
                url: url
            });
        },

        // 跳转到数据测试页面
        goToTestPage() {
            uni.navigateTo({
                url: '/pages/test-data/index'
            });
        },

        // 测试真实数据获取功能
        async testDataFunctions() {
            try {
                console.log('🧪 开始测试真实数据获取功能...');

                // 动态导入agentDataService
                const agentDataService = (await import('@/services/agentDataService.js')).default;

                // 测试真实股票数据获取
                console.log('📊 测试真实股票数据获取...');
                const stockResult = await agentDataService.getStockData(['000001', '600000']);
                console.log('📊 真实股票数据测试结果:', stockResult);

                // 测试真实数据回测功能
                console.log('🔄 测试真实数据回测功能...');
                const backtestResult = await agentDataService.runBacktest({
                    strategy: 'ma_crossover',
                    symbols: ['000001'],
                    initial_capital: 100000,
                    start_date: '2023-01-01',
                    end_date: '2024-01-01'
                });
                console.log('🔄 真实数据回测测试结果:', backtestResult);

                // 显示测试完成提示
                uni.showToast({
                    title: '真实数据测试完成，请查看控制台',
                    icon: 'success',
                    duration: 3000
                });

            } catch (error) {
                console.error('❌ 真实数据测试失败:', error);
                console.error('💡 请确保Agent后端服务正在运行并连接到真实数据源');

                // 显示详细的错误提示
                this.showDataErrorAlert(error.message);
            }
        },

        // 显示数据错误提示
        showDataErrorAlert(message) {
            this.dataErrorMessage = message;
            this.showDataError = true;
        },

        // 隐藏数据错误提示
        hideDataError() {
            this.showDataError = false;
        },

        // 重试数据连接
        async retryDataConnection() {
            console.log('🔄 重试真实数据连接...');
            await this.testDataFunctions();
        },

        // 加载数据
        async loadData() {
            this.loading = true;
            try {
                await Promise.all([
                    this.loadAgentAnalysis(),
                    this.loadAccountBalance()
                ]);
                this.lastUpdateTime = new Date().toLocaleTimeString();
            } catch (error) {
                console.error('加载数据失败:', error);
                uni.showToast({
                    title: '数据加载失败',
                    icon: 'none'
                });
            } finally {
                this.loading = false;
            }
        },

        // 刷新数据
        async refreshData() {
            if (this.loading) return;
            await this.loadData();
        },

        // 加载Agent分析数据
        async loadAgentAnalysis() {
            try {
                const response = await dataService.getAgentAnalysis();

                if (response && response.recommendations) {
                    // 更新推荐股票数据
                    this.recommendedStocks = response.recommendations.slice(0, 3).map(stock => ({
                        name: stock.name,
                        code: stock.symbol,
                        price: stock.target_price ? stock.target_price.toFixed(2) : '0.00',
                        change: '+0.00%', // 这里可以根据实际数据计算
                        trend: stock.action === '买入' ? 'up' : stock.action === '卖出' ? 'down' : 'neutral'
                    }));
                }
            } catch (error) {
                console.error('加载Agent分析数据失败:', error);

                // 检查是否为模拟数据错误
                if (error.message && error.message.includes('模拟')) {
                    this.showDataErrorAlert(error.message);
                } else {
                    console.error('💡 Agent分析服务连接失败，请检查后端服务');
                }
            }
        },

        // 加载账户余额数据
        async loadAccountBalance() {
            try {
                const response = await dataService.getAccountBalance();

                if (response && response.balance_info) {
                    // 这里可以根据需要更新相关数据
                    console.log('账户余额数据:', response.balance_info);
                }
            } catch (error) {
                console.error('加载账户余额数据失败:', error);
                // 使用默认数据，避免影响页面显示
            }
        }
    }
}
</script>

<style>
/* 深色主题样式 */
.dark-theme {
    padding: 30rpx;
    background-color: #141414;
}

.dark-theme .header {
    margin-bottom: 30rpx;
}

.dark-theme .title {
    font-size: 40rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 10rpx;
}

.dark-theme .subtitle {
    font-size: 26rpx;
    color: #999999;
}

/* 高级功能卡片 - 深色主题 */
.dark-theme .premium-features {
    margin-bottom: 30rpx;
}

.dark-theme .feature-card {
    display: flex;
    align-items: center;
    background-color: #222222;
    border-radius: 12rpx;
    padding: 20rpx;
    margin-bottom: 15rpx;
}

.dark-theme .feature-icon {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    margin-right: 20rpx;
    display: flex;
    justify-content: center;
    align-items: center;
}

.dark-theme .ai-icon {
    background: linear-gradient(135deg, #4c8dff, #9c27b0);
}

.dark-theme .trade-icon {
    background: linear-gradient(135deg, #00c853, #009688);
}

.dark-theme .t0-icon {
    background: linear-gradient(135deg, #ff5252, #ff9800);
}

.dark-theme .test-icon {
    background: linear-gradient(135deg, #2196f3, #03a9f4);
}

.dark-theme .feature-content {
    flex: 1;
}

.dark-theme .feature-title {
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 5rpx;
}

.dark-theme .feature-desc {
    font-size: 24rpx;
    color: #999999;
}

.dark-theme .arrow-right {
    width: 30rpx;
    height: 30rpx;
    border-top: 3rpx solid #666;
    border-right: 3rpx solid #666;
    transform: rotate(45deg);
}

/* 市场概览 - 深色主题 */
.dark-theme .market-overview {
    background-color: #222222;
    border-radius: 12rpx;
    padding: 20rpx;
    margin-bottom: 30rpx;
}

.dark-theme .card-title {
    margin-bottom: 20rpx;
}

.dark-theme .title-text {
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
}

.dark-theme .indices {
    display: flex;
    justify-content: space-between;
}

.dark-theme .index-card {
    background-color: #333333;
    border-radius: 8rpx;
    padding: 15rpx;
    width: 31%;
    display: flex;
    flex-direction: column;
}

.dark-theme .index-name {
    font-size: 24rpx;
    color: #cccccc;
    margin-bottom: 10rpx;
}

.dark-theme .index-value {
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 5rpx;
}

.dark-theme .index-change {
    font-size: 24rpx;
}

/* Agent智能选股 - 深色主题 */
.dark-theme .stock-recommendation {
    background-color: #222222;
    border-radius: 12rpx;
    padding: 20rpx;
    margin-bottom: 30rpx;
}

.dark-theme .stock-list {
    display: flex;
    flex-direction: column;
}

.dark-theme .stock-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx 0;
    border-bottom: 1px solid #333333;
}

.dark-theme .stock-item:last-child {
    border-bottom: none;
}

.dark-theme .stock-info {
    display: flex;
    flex-direction: column;
}

.dark-theme .stock-name {
    font-size: 28rpx;
    color: #ffffff;
    margin-bottom: 5rpx;
}

.dark-theme .stock-code {
    font-size: 24rpx;
    color: #999999;
}

.dark-theme .stock-price {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}

.dark-theme .price {
    font-size: 30rpx;
    font-weight: bold;
    margin-bottom: 5rpx;
}

.dark-theme .change {
    font-size: 24rpx;
}

/* 功能快捷方式 - 深色主题 */
.dark-theme .feature-shortcuts {
    background-color: #222222;
    border-radius: 12rpx;
    padding: 20rpx;
}

.dark-theme .shortcut-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 30rpx;
}

.dark-theme .shortcut-row:last-child {
    margin-bottom: 0;
}

.dark-theme .shortcut-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 30%;
}

.dark-theme .shortcut-icon {
    width: 100rpx;
    height: 100rpx;
    border-radius: 50%;
    background-color: #333333;
    margin-bottom: 15rpx;
}

.dark-theme .shortcut-text {
    font-size: 24rpx;
    color: #cccccc;
}

/* 热门股票K线图 - 深色主题 */
.dark-theme .stock-charts-section {
    background-color: #222222;
    border-radius: 12rpx;
    padding: 20rpx;
    margin-bottom: 30rpx;
}

.dark-theme .view-more {
    font-size: 24rpx;
    color: #999999;
}

.dark-theme .stock-chart-card {
    background-color: #333333;
    border-radius: 8rpx;
    padding: 15rpx;
    margin-bottom: 20rpx;
}

.dark-theme .chart-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10rpx;
}

.dark-theme .stock-basic-info {
    display: flex;
    flex-direction: column;
}

.dark-theme .stock-name {
    font-size: 28rpx;
    color: #ffffff;
    font-weight: bold;
}

.dark-theme .stock-code {
    font-size: 22rpx;
    color: #999999;
}

.dark-theme .stock-price-info {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}

.dark-theme .price {
    font-size: 30rpx;
    font-weight: bold;
}

.dark-theme .change {
    font-size: 22rpx;
}

.dark-theme .pro-chart-container {
    position: relative;
    height: 300rpx;
    background-color: #222222;
    border-radius: 6rpx;
    overflow: hidden;
    margin: 12rpx 0;
}

.dark-theme .ma-indicator-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #1a1a1a;
    padding: 4rpx 10rpx;
    height: 40rpx;
}

.dark-theme .ma-left {
    display: flex;
    align-items: center;
}

.dark-theme .ma-title {
    font-size: 22rpx;
    color: #999;
    margin-right: 8rpx;
}

.dark-theme .ma-item {
    font-size: 22rpx;
    margin-right: 12rpx;
    display: flex;
    align-items: center;
}

.dark-theme .ma5 {
    color: #fff;
}

.dark-theme .ma10 {
    color: #ffb74d;
}

.dark-theme .ma20 {
    color: #ce93d8;
}

.dark-theme .ma60 {
    color: #81d4fa;
}

.dark-theme .arrow {
    font-size: 18rpx;
    margin-left: 4rpx;
}

.dark-theme .arrow.up {
    color: #ff5252;
}

.dark-theme .arrow.down {
    color: #4caf50;
}

.dark-theme .current-price {
    font-size: 22rpx;
    color: #fff;
    font-weight: bold;
}

.dark-theme .professional-chart {
    display: flex;
    height: 200rpx;
    position: relative;
}

.dark-theme .price-axis {
    width: 45rpx;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background-color: #1a1a1a;
    padding: 5rpx 0;
}

.dark-theme .price-axis.left {
    border-right: 1px solid #333;
}

.dark-theme .price-axis.right {
    border-left: 1px solid #333;
}

.dark-theme .price-label {
    font-size: 18rpx;
    color: #999;
    text-align: center;
}

.dark-theme .chart-main-area {
    flex: 1;
    position: relative;
    background-color: #1a1a1a;
}

.dark-theme .grid-lines {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: 1;
}

.dark-theme .grid-line {
    position: absolute;
    left: 0;
    width: 100%;
    height: 1px;
    background-color: rgba(255, 255, 255, 0.05);
}

.dark-theme .grid-line:nth-child(1) {
    top: 0%;
}

.dark-theme .grid-line:nth-child(2) {
    top: 25%;
}

.dark-theme .grid-line:nth-child(3) {
    top: 50%;
}

.dark-theme .grid-line:nth-child(4) {
    top: 75%;
}

.dark-theme .grid-line:nth-child(5) {
    top: 100%;
}

.dark-theme .candlestick-chart {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: 2;
}

.dark-theme .candlestick {
    position: absolute;
    width: 6rpx;
    transform: translateX(-50%);
}

.dark-theme .candlestick .wick {
    position: absolute;
    width: 1px;
    left: 50%;
    transform: translateX(-50%);
}

.dark-theme .candlestick.red {
    background-color: #ff5252;
}

.dark-theme .candlestick.green {
    background-color: #4caf50;
}

.dark-theme .ma-lines {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: 3;
}

.dark-theme .ma-line {
    position: absolute;
    width: 100%;
    height: 1px;
}

.dark-theme .ma-line.ma5 {
    top: 30%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5) 10%, rgba(255, 255, 255, 0.5) 90%, transparent);
}

.dark-theme .ma-line.ma10 {
    top: 40%;
    background: linear-gradient(90deg, transparent, rgba(255, 183, 77, 0.5) 10%, rgba(255, 183, 77, 0.5) 90%, transparent);
}

.dark-theme .ma-line.ma20 {
    top: 50%;
    background: linear-gradient(90deg, transparent, rgba(206, 147, 216, 0.5) 10%, rgba(206, 147, 216, 0.5) 90%, transparent);
}

.dark-theme .ma-line.ma60 {
    top: 60%;
    background: linear-gradient(90deg, transparent, rgba(129, 212, 250, 0.5) 10%, rgba(129, 212, 250, 0.5) 90%, transparent);
}

.dark-theme .ai-signals {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: 4;
}

.dark-theme .ai-signal {
    position: absolute;
    transform: translate(-50%, -50%);
}

.dark-theme .ai-signal.buy::before {
    content: '';
    display: block;
    width: 0;
    height: 0;
    border-left: 6rpx solid transparent;
    border-right: 6rpx solid transparent;
    border-bottom: 12rpx solid #ff5252;
    margin: 0 auto 4rpx;
}

.dark-theme .ai-signal.sell::before {
    content: '';
    display: block;
    width: 0;
    height: 0;
    border-left: 6rpx solid transparent;
    border-right: 6rpx solid transparent;
    border-top: 12rpx solid #4caf50;
    margin: 0 auto 4rpx;
}

.dark-theme .signal-label {
    font-size: 16rpx;
    background-color: rgba(0, 0, 0, 0.5);
    padding: 2rpx 6rpx;
    border-radius: 4rpx;
    white-space: nowrap;
}

.dark-theme .ai-signal.buy .signal-label {
    color: #ff5252;
    border: 1px solid rgba(255, 82, 82, 0.3);
}

.dark-theme .ai-signal.sell .signal-label {
    color: #4caf50;
    border: 1px solid rgba(76, 175, 80, 0.3);
}

.dark-theme .volume-chart {
    height: 40rpx;
    position: relative;
    background-color: #1a1a1a;
    margin-top: 2rpx;
}

.dark-theme .volume-bars {
    position: relative;
    height: 100%;
    width: 100%;
    padding: 0 45rpx;
}

.dark-theme .volume-bar {
    position: absolute;
    width: 6rpx;
    bottom: 0;
    transform: translateX(-50%);
}

.dark-theme .volume-bar.red {
    background-color: rgba(255, 82, 82, 0.6);
}

.dark-theme .volume-bar.green {
    background-color: rgba(76, 175, 80, 0.6);
}

.dark-theme .date-axis {
    display: flex;
    justify-content: space-between;
    padding: 0 45rpx;
    margin-top: 2rpx;
}

.dark-theme .date-label {
    font-size: 18rpx;
    color: #999;
}

.dark-theme .chart-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 12rpx;
}

.dark-theme .action-button {
    width: 23%;
    height: 60rpx;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 6rpx;
    font-size: 24rpx;
    font-weight: bold;
}

.dark-theme .action-button.buy {
    background-color: #ff5252;
    color: #fff;
}

.dark-theme .action-button.sell {
    background-color: #4caf50;
    color: #fff;
}

.dark-theme .action-button.analyze {
    background-color: #1989fa;
    color: #fff;
}

.dark-theme .action-button.test {
    background-color: #ff9800;
    color: #fff;
}

/* 浅色主题样式 */
.light-theme {
    padding: 30rpx;
    background-color: #f5f5f5;
}

.light-theme .header {
    margin-bottom: 30rpx;
}

.light-theme .title {
    font-size: 40rpx;
    font-weight: bold;
    color: #333333;
    margin-bottom: 10rpx;
}

.light-theme .subtitle {
    font-size: 26rpx;
    color: #666666;
}

/* 高级功能卡片 - 浅色主题 */
.light-theme .premium-features {
    margin-bottom: 30rpx;
}

.light-theme .feature-card {
    display: flex;
    align-items: center;
    background-color: #ffffff;
    border-radius: 12rpx;
    padding: 20rpx;
    margin-bottom: 15rpx;
    box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.light-theme .feature-icon {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    margin-right: 20rpx;
    display: flex;
    justify-content: center;
    align-items: center;
}

.light-theme .ai-icon {
    background: linear-gradient(135deg, #4c8dff, #9c27b0);
}

.light-theme .trade-icon {
    background: linear-gradient(135deg, #00c853, #009688);
}

.light-theme .t0-icon {
    background: linear-gradient(135deg, #ff5252, #ff9800);
}

.light-theme .test-icon {
    background: linear-gradient(135deg, #2196f3, #03a9f4);
}

.light-theme .feature-content {
    flex: 1;
}

.light-theme .feature-title {
    font-size: 32rpx;
    font-weight: bold;
    color: #333333;
    margin-bottom: 5rpx;
}

.light-theme .feature-desc {
    font-size: 24rpx;
    color: #666666;
}

.light-theme .arrow-right {
    width: 30rpx;
    height: 30rpx;
    border-top: 3rpx solid #999;
    border-right: 3rpx solid #999;
    transform: rotate(45deg);
}

/* 市场概览 - 浅色主题 */
.light-theme .market-overview {
    background-color: #ffffff;
    border-radius: 12rpx;
    padding: 20rpx;
    margin-bottom: 30rpx;
    box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.light-theme .card-title {
    margin-bottom: 20rpx;
}

.light-theme .title-text {
    font-size: 32rpx;
    font-weight: bold;
    color: #333333;
}

.light-theme .indices {
    display: flex;
    justify-content: space-between;
}

.light-theme .index-card {
    background-color: #f5f5f5;
    border-radius: 8rpx;
    padding: 15rpx;
    width: 31%;
    display: flex;
    flex-direction: column;
}

.light-theme .index-name {
    font-size: 24rpx;
    color: #666666;
    margin-bottom: 10rpx;
}

.light-theme .index-value {
    font-size: 32rpx;
    font-weight: bold;
    color: #333333;
    margin-bottom: 5rpx;
}

.light-theme .index-change {
    font-size: 24rpx;
}

/* Agent智能选股 - 浅色主题 */
.light-theme .stock-recommendation {
    background-color: #ffffff;
    border-radius: 12rpx;
    padding: 20rpx;
    margin-bottom: 30rpx;
    box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.light-theme .stock-list {
    display: flex;
    flex-direction: column;
}

.light-theme .stock-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx 0;
    border-bottom: 1px solid #eeeeee;
}

.light-theme .stock-item:last-child {
    border-bottom: none;
}

.light-theme .stock-info {
    display: flex;
    flex-direction: column;
}

.light-theme .stock-name {
    font-size: 28rpx;
    color: #333333;
    margin-bottom: 5rpx;
}

.light-theme .stock-code {
    font-size: 24rpx;
    color: #999999;
}

.light-theme .stock-price {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}

.light-theme .price {
    font-size: 30rpx;
    font-weight: bold;
    margin-bottom: 5rpx;
}

.light-theme .change {
    font-size: 24rpx;
}

/* 功能快捷方式 - 浅色主题 */
.light-theme .feature-shortcuts {
    background-color: #ffffff;
    border-radius: 12rpx;
    padding: 20rpx;
    box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.light-theme .shortcut-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 30rpx;
}

.light-theme .shortcut-row:last-child {
    margin-bottom: 0;
}

.light-theme .shortcut-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 30%;
}

.light-theme .shortcut-icon {
    width: 100rpx;
    height: 100rpx;
    border-radius: 50%;
    background-color: #f0f0f0;
    margin-bottom: 15rpx;
}

.light-theme .shortcut-text {
    font-size: 24rpx;
    color: #666666;
}

/* 热门股票K线图 - 浅色主题 */
.light-theme .stock-charts-section {
    background-color: #ffffff;
    border-radius: 12rpx;
    padding: 20rpx;
    margin-bottom: 30rpx;
    box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.light-theme .view-more {
    font-size: 24rpx;
    color: #666666;
}

.light-theme .stock-chart-card {
    background-color: #f5f5f5;
    border-radius: 8rpx;
    padding: 15rpx;
    margin-bottom: 20rpx;
}

.light-theme .chart-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10rpx;
}

.light-theme .stock-basic-info {
    display: flex;
    flex-direction: column;
}

.light-theme .stock-name {
    font-size: 28rpx;
    color: #333333;
    font-weight: bold;
}

.light-theme .stock-code {
    font-size: 22rpx;
    color: #999999;
}

.light-theme .stock-price-info {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}

.light-theme .price {
    font-size: 30rpx;
    font-weight: bold;
}

.light-theme .change {
    font-size: 22rpx;
}

.light-theme .pro-chart-container {
    position: relative;
    height: 300rpx;
    background-color: #ffffff;
    border-radius: 6rpx;
    overflow: hidden;
    margin: 12rpx 0;
    box-shadow: 0 1rpx 5rpx rgba(0, 0, 0, 0.05);
}

.light-theme .ma-indicator-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #f5f5f5;
    padding: 4rpx 10rpx;
    height: 40rpx;
}

.light-theme .ma-left {
    display: flex;
    align-items: center;
}

.light-theme .ma-title {
    font-size: 22rpx;
    color: #666;
    margin-right: 8rpx;
}

.light-theme .ma-item {
    font-size: 22rpx;
    margin-right: 12rpx;
    display: flex;
    align-items: center;
}

.light-theme .ma5 {
    color: #333;
}

.light-theme .ma10 {
    color: #f57c00;
}

.light-theme .ma20 {
    color: #7b1fa2;
}

.light-theme .ma60 {
    color: #0288d1;
}

.light-theme .arrow {
    font-size: 18rpx;
    margin-left: 4rpx;
}

.light-theme .arrow.up {
    color: #ff5252;
}

.light-theme .arrow.down {
    color: #4caf50;
}

.light-theme .current-price {
    font-size: 22rpx;
    color: #333;
    font-weight: bold;
}

.light-theme .professional-chart {
    display: flex;
    height: 200rpx;
    position: relative;
}

.light-theme .price-axis {
    width: 45rpx;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background-color: #f5f5f5;
    padding: 5rpx 0;
}

.light-theme .price-axis.left {
    border-right: 1px solid #e0e0e0;
}

.light-theme .price-axis.right {
    border-left: 1px solid #e0e0e0;
}

.light-theme .price-label {
    font-size: 18rpx;
    color: #666;
    text-align: center;
}

.light-theme .chart-main-area {
    flex: 1;
    position: relative;
    background-color: #ffffff;
}

.light-theme .grid-lines {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: 1;
}

.light-theme .grid-line {
    position: absolute;
    left: 0;
    width: 100%;
    height: 1px;
    background-color: rgba(0, 0, 0, 0.05);
}

.light-theme .grid-line:nth-child(1) {
    top: 0%;
}

.light-theme .grid-line:nth-child(2) {
    top: 25%;
}

.light-theme .grid-line:nth-child(3) {
    top: 50%;
}

.light-theme .grid-line:nth-child(4) {
    top: 75%;
}

.light-theme .grid-line:nth-child(5) {
    top: 100%;
}

.light-theme .candlestick-chart {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: 2;
}

.light-theme .candlestick {
    position: absolute;
    width: 6rpx;
    transform: translateX(-50%);
}

.light-theme .candlestick .wick {
    position: absolute;
    width: 1px;
    left: 50%;
    transform: translateX(-50%);
}

.light-theme .candlestick.red {
    background-color: #ff5252;
}

.light-theme .candlestick.green {
    background-color: #4caf50;
}

.light-theme .ma-lines {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: 3;
}

.light-theme .ma-line {
    position: absolute;
    width: 100%;
    height: 1px;
}

.light-theme .ma-line.ma5 {
    top: 30%;
    background: linear-gradient(90deg, transparent, rgba(0, 0, 0, 0.5) 10%, rgba(0, 0, 0, 0.5) 90%, transparent);
}

.light-theme .ma-line.ma10 {
    top: 40%;
    background: linear-gradient(90deg, transparent, rgba(245, 124, 0, 0.5) 10%, rgba(245, 124, 0, 0.5) 90%, transparent);
}

.light-theme .ma-line.ma20 {
    top: 50%;
    background: linear-gradient(90deg, transparent, rgba(123, 31, 162, 0.5) 10%, rgba(123, 31, 162, 0.5) 90%, transparent);
}

.light-theme .ma-line.ma60 {
    top: 60%;
    background: linear-gradient(90deg, transparent, rgba(2, 136, 209, 0.5) 10%, rgba(2, 136, 209, 0.5) 90%, transparent);
}

.light-theme .ai-signals {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: 4;
}

.light-theme .ai-signal {
    position: absolute;
    transform: translate(-50%, -50%);
}

.light-theme .ai-signal.buy::before {
    content: '';
    display: block;
    width: 0;
    height: 0;
    border-left: 6rpx solid transparent;
    border-right: 6rpx solid transparent;
    border-bottom: 12rpx solid #ff5252;
    margin: 0 auto 4rpx;
}

.light-theme .ai-signal.sell::before {
    content: '';
    display: block;
    width: 0;
    height: 0;
    border-left: 6rpx solid transparent;
    border-right: 6rpx solid transparent;
    border-top: 12rpx solid #4caf50;
    margin: 0 auto 4rpx;
}

.light-theme .signal-label {
    font-size: 16rpx;
    background-color: rgba(255, 255, 255, 0.8);
    padding: 2rpx 6rpx;
    border-radius: 4rpx;
    white-space: nowrap;
}

.light-theme .ai-signal.buy .signal-label {
    color: #ff5252;
    border: 1px solid rgba(255, 82, 82, 0.3);
}

.light-theme .ai-signal.sell .signal-label {
    color: #4caf50;
    border: 1px solid rgba(76, 175, 80, 0.3);
}

.light-theme .volume-chart {
    height: 40rpx;
    position: relative;
    background-color: #f5f5f5;
    margin-top: 2rpx;
}

.light-theme .volume-bars {
    position: relative;
    height: 100%;
    width: 100%;
    padding: 0 45rpx;
}

.light-theme .volume-bar {
    position: absolute;
    width: 6rpx;
    bottom: 0;
    transform: translateX(-50%);
}

.light-theme .volume-bar.red {
    background-color: rgba(255, 82, 82, 0.6);
}

.light-theme .volume-bar.green {
    background-color: rgba(76, 175, 80, 0.6);
}

.light-theme .date-axis {
    display: flex;
    justify-content: space-between;
    padding: 0 45rpx;
    margin-top: 2rpx;
}

.light-theme .date-label {
    font-size: 18rpx;
    color: #666;
}

.light-theme .chart-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 12rpx;
}

.light-theme .action-button {
    width: 23%;
    height: 60rpx;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 6rpx;
    font-size: 24rpx;
    font-weight: bold;
}

.light-theme .action-button.buy {
    background-color: #ff5252;
    color: #fff;
}

.light-theme .action-button.sell {
    background-color: #4caf50;
    color: #fff;
}

.light-theme .action-button.analyze {
    background-color: #1989fa;
    color: #fff;
}

.light-theme .action-button.test {
    background-color: #ff9800;
    color: #fff;
}

/* 浮动测试按钮 */
.floating-test-btn {
    position: fixed;
    bottom: 100rpx;
    right: 30rpx;
    width: 120rpx;
    height: 120rpx;
    background: linear-gradient(135deg, #ff9800, #f57c00);
    border-radius: 60rpx;
    display: flex;
    justify-content: center;
    align-items: center;
    box-shadow: 0 8rpx 20rpx rgba(255, 152, 0, 0.4);
    z-index: 1000;
}

.floating-btn-text {
    color: white;
    font-size: 24rpx;
    font-weight: bold;
    text-align: center;
}

/* 通用样式 */
.card-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15rpx;
}

.update-info {
    display: flex;
    align-items: center;
    gap: 10rpx;
}

.update-time {
    font-size: 22rpx;
    color: #888888;
}

.loading-indicator {
    width: 20rpx;
    height: 20rpx;
    border: 2rpx solid #333333;
    border-top: 2rpx solid #1989fa;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

.refresh-btn {
    font-size: 24rpx;
    color: #1989fa;
    padding: 8rpx 16rpx;
    border-radius: 16rpx;
    background-color: rgba(25, 137, 250, 0.1);
    cursor: pointer;
}

.refresh-btn.loading {
    color: #888888;
    background-color: rgba(136, 136, 136, 0.1);
    cursor: not-allowed;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.up {
    color: #ff5252;
}

.down {
    color: #4caf50;
}
</style> 
