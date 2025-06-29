<template>
    <view class="container" :class="isDarkMode ? 'dark-theme' : 'light-theme'">
        <view class="header">
            <view class="title">Agent策略研究</view>
            <view class="subtitle">发现与分析优秀的交易策略</view>
        </view>
        
        <!-- 策略搜索 -->
        <view class="card">
            <view class="card-title">
                <text>策略搜索</text>
            </view>
            
            <view class="search-area">
                <view class="search-form">
                    <view class="search-input-wrapper">
                        <input type="text" v-model="searchQuery" placeholder="输入策略关键词,特征或问题" class="search-input" />
                    </view>
                    <view class="search-language">
                        <picker @change="onLanguageChange" :value="languageIndex" :range="languages">
                            <view class="language-selector">
                                <text>{{languages[languageIndex]}}</text>
                                <text class="arrow-down">▼</text>
                            </view>
                        </picker>
                    </view>
                    <button class="search-btn" @click="searchStrategies">搜索</button>
                </view>
                
                <view class="filter-options">
                    <view class="filter-item">
                        <text class="filter-label">结果数量:</text>
                        <slider :value="maxResults" :min="1" :max="20" :step="1" @change="onMaxResultsChange" show-value />
                    </view>
                    
                    <view class="filter-tags">
                        <view class="filter-tag" :class="{'active': activeFilters.includes('trending')}" @click="toggleFilter('trending')">热门</view>
                        <view class="filter-tag" :class="{'active': activeFilters.includes('high_profit')}" @click="toggleFilter('high_profit')">高收益</view>
                        <view class="filter-tag" :class="{'active': activeFilters.includes('low_risk')}" @click="toggleFilter('low_risk')">低风险</view>
                        <view class="filter-tag" :class="{'active': activeFilters.includes('easy')}" @click="toggleFilter('easy')">易实现</view>
                    </view>
                </view>
            </view>
        </view>
        
        <!-- 搜索结果 -->
        <view class="card" v-if="searchResults.length > 0">
            <view class="card-title">
                <text>搜索结果</text>
                <text class="result-count">共 {{searchResults.length}} 条</text>
            </view>
            
            <view class="strategy-list">
                <view v-for="(strategy, index) in searchResults" :key="index" class="strategy-item" @click="viewStrategyDetail(strategy)">
                    <view class="strategy-header">
                        <view class="strategy-name">{{strategy.name}}</view>
                        <view class="strategy-score" :class="getScoreClass(strategy.score)">{{strategy.score}}</view>
                    </view>
                    
                    <view class="strategy-desc">{{strategy.description}}</view>
                    
                    <view class="strategy-metrics">
                        <view class="metric">
                            <text class="metric-label">收益率:</text>
                            <text class="metric-value" :class="getReturnClass(strategy.annual_return)">{{strategy.annual_return}}%</text>
                        </view>
                        <view class="metric">
                            <text class="metric-label">夏普比率:</text>
                            <text class="metric-value">{{strategy.sharpe_ratio}}</text>
                        </view>
                        <view class="metric">
                            <text class="metric-label">最大回撤:</text>
                            <text class="metric-value" :class="getDrawdownClass(strategy.max_drawdown)">{{strategy.max_drawdown}}%</text>
                        </view>
                    </view>
                    
                    <view class="strategy-tags">
                        <view class="tag" v-for="(tag, tagIndex) in strategy.tags" :key="tagIndex">{{tag}}</view>
                    </view>
                    
                    <view class="strategy-author">
                        <text class="author-label">来源:</text>
                        <text class="author-value">{{strategy.source}}</text>
                    </view>
                </view>
            </view>
        </view>
        
        <!-- 顶级交易者 -->
        <view class="card">
            <view class="card-title">
                <text>顶级交易者策略</text>
                <view class="market-selector">
                    <picker @change="onMarketChange" :value="marketIndex" :range="markets">
                        <view class="picker-value">
                            {{markets[marketIndex]}} <text class="down-arrow">▼</text>
                        </view>
                    </picker>
                </view>
            </view>
            
            <view class="traders-list">
                <view v-for="(trader, index) in topTraders" :key="index" class="trader-item">
                    <view class="trader-rank">{{index + 1}}</view>
                    <view class="trader-info">
                        <view class="trader-name">{{trader.name}}</view>
                        <view class="trader-desc">{{trader.description}}</view>
                        
                        <view class="trader-metrics">
                            <view class="trader-metric">
                                <text class="trader-metric-label">年化收益:</text>
                                <text class="trader-metric-value return">{{trader.annual_return}}%</text>
                            </view>
                            <view class="trader-metric">
                                <text class="trader-metric-label">连续盈利:</text>
                                <text class="trader-metric-value">{{trader.consecutive_wins}}个月</text>
                            </view>
                            <view class="trader-metric">
                                <text class="trader-metric-label">交易数量:</text>
                                <text class="trader-metric-value">{{trader.trades_count}}</text>
                            </view>
                        </view>
                        
                        <view class="trader-actions">
                            <button class="trader-btn view-btn" @click="viewTraderDetail(trader)">查看策略</button>
                            <button class="trader-btn follow-btn" @click="followTrader(trader)">关注</button>
                        </view>
                    </view>
                </view>
            </view>
        </view>
        
        <!-- 自动研究计划 -->
        <view class="card">
            <view class="card-title">
                <text>自动研究计划</text>
                <view class="schedule-toggle">
                    <switch :checked="autoResearchEnabled" @change="toggleAutoResearch" color="#4c8dff" />
                </view>
            </view>
            
            <view class="auto-research-config" v-if="autoResearchEnabled">
                <view class="config-item">
                    <text class="config-label">研究频率:</text>
                    <picker @change="onFrequencyChange" :value="frequencyIndex" :range="frequencies">
                        <view class="frequency-picker">
                            {{frequencies[frequencyIndex]}} <text class="arrow-down">▼</text>
                        </view>
                    </picker>
                </view>
                
                <view class="config-item">
                    <text class="config-label">关注主题:</text>
                    <view class="theme-tags">
                        <view v-for="(theme, themeIndex) in researchThemes" :key="themeIndex" 
                              class="theme-tag" :class="{'selected': selectedThemes.includes(theme.id)}" 
                              @click="toggleTheme(theme.id)">
                            {{theme.name}}
                        </view>
                    </view>
                </view>
                
                <view class="config-item">
                    <text class="config-label">接收通知:</text>
                    <switch :checked="notificationsEnabled" @change="toggleNotifications" color="#4c8dff" />
                </view>
                
                <view class="scheduler-actions">
                    <button class="scheduler-btn apply-btn" @click="applyScheduleSettings">应用设置</button>
                    <button class="scheduler-btn reset-btn" @click="resetScheduleSettings">重置</button>
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
            isDarkMode: false, // 使用与设置页面相同的方式
            searchQuery: '',
            searchResults: [],
            languages: ['中文', '英文'],
            languageIndex: 0,
            maxResults: 5,
            activeFilters: [],
            topTraders: [],
            markets: ['全球', '中国', '美国', '欧洲', '亚太'],
            marketIndex: 0,
            autoResearchEnabled: false,
            frequencies: ['每天', '每周', '每两周', '每月'],
            frequencyIndex: 1,
            researchThemes: [
                { id: 'trend', name: '趋势交易' },
                { id: 'value', name: '价值投资' },
                { id: 'quant', name: '量化策略' },
                { id: 'swing', name: '短线波段' },
                { id: 'sector', name: '行业轮动' },
                { id: 'macro', name: '宏观策略' }
            ],
            selectedThemes: ['trend', 'quant'],
            notificationsEnabled: true,
            loading: false
        };
    },
    
    onLoad() {
        // 使用全局主题设置
        const app = getApp();
        if (app.globalData) {
            this.isDarkMode = app.globalData.isDarkMode;
        }
        
        // 监听主题变化事件
        uni.$on('theme-changed', this.updateThemeFromGlobal);
        
        // 获取顶级交易者数据
        this.fetchTopTraders();
        // 获取自动研究计划状态
        this.fetchResearchStatus();
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
        
        // 语言选择变化
        onLanguageChange(e) {
            this.languageIndex = e.detail.value;
        },
        
        // 最大结果数变化
        onMaxResultsChange(e) {
            this.maxResults = e.detail.value;
        },
        
        // 切换过滤器
        toggleFilter(filter) {
            const index = this.activeFilters.indexOf(filter);
            if (index > -1) {
                this.activeFilters.splice(index, 1);
            } else {
                this.activeFilters.push(filter);
            }
        },
        
        // 搜索策略
        async searchStrategies() {
            if (!this.searchQuery.trim()) {
                uni.showToast({
                    title: '请输入搜索关键词',
                    icon: 'none'
                });
                return;
            }
            
            try {
                this.loading = true;
                uni.showLoading({
                    title: '搜索中...'
                });
                
                // 定义语言代码
                const language = this.languageIndex === 0 ? 'zh' : 'en';
                
                // 调用AI服务的研究策略方法
                const results = await aiService.researchExternalStrategies(
                    this.searchQuery, 
                    language, 
                    this.maxResults,
                    this.activeFilters
                );
                
                this.searchResults = results.strategies || [];
                
                uni.hideLoading();
                
                if (this.searchResults.length === 0) {
                    uni.showToast({
                        title: '未找到匹配的策略',
                        icon: 'none'
                    });
                }
            } catch (err) {
                uni.hideLoading();
                console.error('搜索策略失败:', err);
                uni.showToast({
                    title: '搜索失败,请重试',
                    icon: 'none'
                });
            } finally {
                this.loading = false;
            }
        },
        
        // 查看策略详情
        viewStrategyDetail(strategy) {
            // 可以在这里使用uni.navigateTo导航到策略详情页
            // 也可以在这里创建一个弹出层显示策略详情
            uni.showToast({
                title: `查看${strategy.name}策略`,
                icon: 'none'
            });
        },
        
        // 获取评分样式类
        getScoreClass(score) {
            if (score >= 8) return 'score-high';
            if (score >= 6) return 'score-medium';
            return 'score-low';
        },
        
        // 获取收益率样式类
        getReturnClass(annualReturn) {
            if (annualReturn >= 20) return 'return-high';
            if (annualReturn >= 10) return 'return-medium';
            if (annualReturn > 0) return 'return-low';
            return 'return-negative';
        },
        
        // 获取最大回撤样式类
        getDrawdownClass(maxDrawdown) {
            if (maxDrawdown <= 10) return 'drawdown-low';
            if (maxDrawdown <= 20) return 'drawdown-medium';
            return 'drawdown-high';
        },
        
        // 市场选择变化
        onMarketChange(e) {
            this.marketIndex = e.detail.value;
            this.fetchTopTraders();
        },
        
        // 获取顶级交易者数据
        async fetchTopTraders() {
            try {
                this.loading = true;
                
                // 获取市场代码
                const marketCode = ['global', 'cn', 'us', 'eu', 'asia'][this.marketIndex];
                
                // 调用AI服务获取顶级交易者
                const result = await aiService.getTopTraderStrategies(marketCode, 5);
                
                this.topTraders = result.traders || [];
            } catch (err) {
                console.error('获取顶级交易者失败:', err);
                uni.showToast({
                    title: '获取交易者数据失败',
                    icon: 'none'
                });
            } finally {
                this.loading = false;
            }
        },
        
        // 查看交易者详情
        viewTraderDetail(trader) {
            uni.showToast({
                title: `查看${trader.name}策略`,
                icon: 'none'
            });
        },
        
        // 关注交易者
        followTrader(trader) {
            uni.showToast({
                title: `已关注${trader.name}`,
                icon: 'success'
            });
        },
        
        // 切换自动研究
        toggleAutoResearch(e) {
            this.autoResearchEnabled = e.detail.value;
        },
        
        // 频率选择变化
        onFrequencyChange(e) {
            this.frequencyIndex = e.detail.value;
        },
        
        // 切换主题选择
        toggleTheme(themeId) {
            // 检查参数是否是主题ID (字符串),如果是则处理研究主题的切换
            if (typeof themeId === 'string') {
            const index = this.selectedThemes.indexOf(themeId);
            if (index > -1) {
                this.selectedThemes.splice(index, 1);
            } else {
                this.selectedThemes.push(themeId);
                }
                return;
            }
            
            // 否则是切换全局主题设置
            this.isDarkMode = !this.isDarkMode;
            
            // 更新全局主题设置
            const app = getApp();
            if (app.globalData) {
                app.globalData.isDarkMode = this.isDarkMode;
                app.globalData.theme = this.isDarkMode ? 'dark' : 'light';
                
                // 应用主题到全局UI
                if (typeof app.applyTheme === 'function') {
                    app.applyTheme();
                }
                
                // 发布主题变化事件
                uni.$emit('theme-changed');
            }
        },
        
        // 切换通知
        toggleNotifications(e) {
            this.notificationsEnabled = e.detail.value;
        },
        
        // 应用计划设置
        async applyScheduleSettings() {
            try {
                uni.showLoading({
                    title: '保存设置...'
                });
                
                // 计算间隔小时数
                const hoursInterval = [24, 168, 336, 720][this.frequencyIndex];
                
                // 调用AI服务设置自动研究计划
                await aiService.scheduleAutomaticResearch(
                    this.autoResearchEnabled,
                    hoursInterval,
                    this.selectedThemes,
                    this.notificationsEnabled
                );
                
                uni.hideLoading();
                uni.showToast({
                    title: '设置已保存',
                    icon: 'success'
                });
            } catch (err) {
                uni.hideLoading();
                console.error('保存设置失败:', err);
                uni.showToast({
                    title: '保存设置失败',
                    icon: 'none'
                });
            }
        },
        
        // 重置计划设置
        resetScheduleSettings() {
            this.autoResearchEnabled = false;
            this.frequencyIndex = 1;
            this.selectedThemes = ['trend', 'quant'];
            this.notificationsEnabled = true;
            
            uni.showToast({
                title: '设置已重置',
                icon: 'none'
            });
        },
        
        // 获取自动研究状态
        async fetchResearchStatus() {
            try {
                const status = await aiService.getExternalLearningStatus();
                
                if (status) {
                    this.autoResearchEnabled = status.enabled || false;
                    
                    // 设置频率索引
                    const hourMap = {24: 0, 168: 1, 336: 2, 720: 3};
                    this.frequencyIndex = hourMap[status.interval_hours] || 1;
                    
                    // 设置主题
                    if (status.themes && Array.isArray(status.themes)) {
                        this.selectedThemes = status.themes;
                    }
                    
                    // 设置通知
                    this.notificationsEnabled = status.notifications_enabled || true;
                }
            } catch (err) {
                console.error('获取研究状态失败:', err);
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

.result-count {
    font-size: 24rpx;
    color: #999;
    font-weight: normal;
}

/* 搜索区域样式 */
.search-area {
    padding: 10rpx;
}

.search-form {
    display: flex;
    margin-bottom: 20rpx;
}

.search-input-wrapper {
    flex: 1;
    margin-right: 10rpx;
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

.search-input {
    height: 80rpx;
    border-radius: 8rpx;
    padding: 0 20rpx;
    font-size: 28rpx;
    width: 100%;
    box-sizing: border-box;
}

.search-language {
    width: 150rpx;
    margin-right: 10rpx;
}

.language-selector {
    height: 80rpx;
    border-radius: 8rpx;
    padding: 0 20rpx;
    font-size: 28rpx;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.dark-theme .language-selector {
    background-color: #333;
    border: 1px solid #444;
}

.light-theme .language-selector {
    background-color: #f5f5f5;
    border: 1px solid #ddd;
}

.arrow-down {
    font-size: 20rpx;
    margin-left: 5rpx;
}

.search-btn {
    width: 150rpx;
    height: 80rpx;
    border-radius: 8rpx;
    background-color: #4c8dff;
    color: #fff;
    font-size: 28rpx;
    line-height: 80rpx;
    text-align: center;
    padding: 0;
}

.search-btn:active {
    background-color: #3a7be0;
}

.filter-options {
    margin: 10rpx 0;
}

.filter-item {
    margin-bottom: 20rpx;
    display: flex;
    align-items: center;
}

.filter-label {
    font-size: 26rpx;
    width: 150rpx;
}

.filter-tags {
    display: flex;
    flex-wrap: wrap;
}

.filter-tag {
    padding: 8rpx 20rpx;
    border-radius: 30rpx;
    margin-right: 15rpx;
    margin-bottom: 15rpx;
    font-size: 24rpx;
    cursor: pointer;
}

.dark-theme .filter-tag {
    background-color: #333;
    color: #ddd;
}

.light-theme .filter-tag {
    background-color: #f0f0f0;
    color: #666;
}

.filter-tag.active {
    background-color: #4c8dff;
    color: #fff;
}

/* 策略列表样式 */
.strategy-list {
    margin-top: 15rpx;
}

.strategy-item {
    padding: 20rpx;
    margin-bottom: 20rpx;
    border-radius: 8rpx;
    cursor: pointer;
}

.dark-theme .strategy-item {
    background-color: #333;
}

.light-theme .strategy-item {
    background-color: #f5f5f5;
}

.dark-theme .strategy-item:active {
    background-color: #444;
}

.light-theme .strategy-item:active {
    background-color: #e8e8e8;
}

.strategy-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10rpx;
}

.strategy-name {
    font-size: 30rpx;
    font-weight: bold;
}

.strategy-score {
    font-size: 26rpx;
    font-weight: bold;
    padding: 4rpx 10rpx;
    border-radius: 6rpx;
}

.score-high {
    background-color: rgba(82, 196, 26, 0.2);
    color: #52c41a;
}

.score-medium {
    background-color: rgba(250, 173, 20, 0.2);
    color: #faad14;
}

.score-low {
    background-color: rgba(255, 77, 79, 0.2);
    color: #ff4d4f;
}

.strategy-desc {
    font-size: 26rpx;
    margin-bottom: 15rpx;
    line-height: 1.4;
}

.dark-theme .strategy-desc {
    color: #bbb;
}

.light-theme .strategy-desc {
    color: #666;
}

.strategy-metrics {
    display: flex;
    margin-bottom: 15rpx;
}

.metric {
    margin-right: 30rpx;
    font-size: 24rpx;
}

.metric-label {
    color: #999;
    margin-right: 5rpx;
}

.return-high {
    color: #52c41a;
}

.return-medium {
    color: #1890ff;
}

.return-low {
    color: #722ed1;
}

.return-negative {
    color: #ff4d4f;
}

.drawdown-low {
    color: #52c41a;
}

.drawdown-medium {
    color: #faad14;
}

.drawdown-high {
    color: #ff4d4f;
}

.strategy-tags {
    display: flex;
    flex-wrap: wrap;
    margin-bottom: 10rpx;
}

.tag {
    font-size: 22rpx;
    padding: 4rpx 10rpx;
    border-radius: 4rpx;
    margin-right: 10rpx;
    margin-bottom: 10rpx;
}

.dark-theme .tag {
    background-color: #444;
    color: #bbb;
}

.light-theme .tag {
    background-color: #f0f0f0;
    color: #666;
}

.strategy-author {
    font-size: 24rpx;
}

.author-label {
    color: #999;
    margin-right: 10rpx;
}

/* 顶级交易者样式 */
.market-selector {
    font-size: 24rpx;
}

.picker-value {
    display: flex;
    align-items: center;
    background-color: rgba(76, 141, 255, 0.1);
    padding: 6rpx 16rpx;
    border-radius: 6rpx;
    font-size: 24rpx;
    color: #4c8dff;
}

.down-arrow {
    margin-left: 8rpx;
    font-size: 20rpx;
}

.traders-list {
    margin-top: 15rpx;
}

.trader-item {
    display: flex;
    padding: 20rpx;
    margin-bottom: 20rpx;
    border-radius: 8rpx;
}

.dark-theme .trader-item {
    background-color: #333;
}

.light-theme .trader-item {
    background-color: #f5f5f5;
}

.trader-rank {
    width: 60rpx;
    height: 60rpx;
    border-radius: 30rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28rpx;
    font-weight: bold;
    margin-right: 20rpx;
}

.dark-theme .trader-rank {
    background-color: #444;
    color: #fff;
}

.light-theme .trader-rank {
    background-color: #e0e0e0;
    color: #333;
}

.trader-info {
    flex: 1;
}

.trader-name {
    font-size: 28rpx;
    font-weight: bold;
    margin-bottom: 5rpx;
}

.trader-desc {
    font-size: 24rpx;
    margin-bottom: 15rpx;
    line-height: 1.4;
}

.dark-theme .trader-desc {
    color: #bbb;
}

.light-theme .trader-desc {
    color: #666;
}

.trader-metrics {
    display: flex;
    margin-bottom: 20rpx;
}

.trader-metric {
    margin-right: 30rpx;
    font-size: 24rpx;
}

.trader-metric-label {
    color: #999;
    margin-right: 5rpx;
}

.trader-metric-value.return {
    color: #52c41a;
}

.trader-actions {
    display: flex;
}

.trader-btn {
    font-size: 24rpx;
    padding: 8rpx 20rpx;
    border-radius: 6rpx;
    margin-right: 15rpx;
    background-color: transparent;
}

.dark-theme .trader-btn {
    border: 1px solid #444;
}

.light-theme .trader-btn {
    border: 1px solid #ddd;
}

.view-btn {
    color: #4c8dff;
    border-color: #4c8dff;
}

.follow-btn {
    color: #52c41a;
    border-color: #52c41a;
}

/* 自动研究计划样式 */
.schedule-toggle {
    font-size: 24rpx;
}

.auto-research-config {
    padding: 10rpx;
}

.config-item {
    margin-bottom: 20rpx;
}

.config-label {
    display: block;
    font-size: 26rpx;
    margin-bottom: 10rpx;
}

.frequency-picker {
    height: 70rpx;
    line-height: 70rpx;
    background-color: rgba(76, 141, 255, 0.1);
    padding: 0 20rpx;
    border-radius: 8rpx;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: #4c8dff;
    font-size: 26rpx;
}

.theme-tags {
    display: flex;
    flex-wrap: wrap;
}

.theme-tag {
    padding: 8rpx 20rpx;
    border-radius: 6rpx;
    margin-right: 15rpx;
    margin-bottom: 15rpx;
    font-size: 24rpx;
    cursor: pointer;
}

.dark-theme .theme-tag {
    background-color: #333;
    color: #bbb;
    border: 1px solid #444;
}

.light-theme .theme-tag {
    background-color: #f5f5f5;
    color: #666;
    border: 1px solid #ddd;
}

.theme-tag.selected {
    background-color: #4c8dff;
    color: #fff;
    border-color: #4c8dff;
}

.scheduler-actions {
    display: flex;
    margin-top: 30rpx;
}

.scheduler-btn {
    flex: 1;
    height: 80rpx;
    border-radius: 8rpx;
    font-size: 28rpx;
    line-height: 80rpx;
    text-align: center;
    margin: 0 10rpx;
}

.apply-btn {
    background-color: #4c8dff;
    color: #fff;
}

.reset-btn {
    background-color: transparent;
}

.dark-theme .reset-btn {
    border: 1px solid #444;
    color: #ddd;
}

.light-theme .reset-btn {
    border: 1px solid #ddd;
    color: #666;
}
</style> 
