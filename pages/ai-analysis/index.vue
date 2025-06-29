<template>
    <view class="container" :class="themeClass">
        <view class="header">
            <view class="header-top">
                <view class="title">Agent智能交易</view>
                <view class="theme-switch" @click="toggleTheme">
                    <view class="theme-icon" :class="currentTheme === 'dark' ? 'light-icon' : 'dark-icon'"></view>
                </view>
            </view>
            <view class="subtitle">基于智能Agent的交易决策与学习系统</view>
            
            <view v-if="isLoading" class="loading-indicator">
                <view class="loading-spinner"></view>
                <text class="loading-text">Agent正在分析数据...</text>
            </view>
        </view>
        
        <!-- 功能标签页 -->
        <view class="tab-navigation">
            <view 
                v-for="(tab, index) in tabs" 
                :key="index" 
                class="tab-item" 
                :class="{'active': activeTab === tab.id}"
                @click="switchTab(tab.id)"
            >
                <text class="tab-text">{{ tab.name }}</text>
            </view>
        </view>
        
        <!-- Agent决策交易标签页内容 -->
        <view v-if="activeTab === 'agent-trading'">
            <AgentTradingPanel />
        </view>
        
        <!-- Agent学习中心标签页内容 -->
        <view v-if="activeTab === 'agent-learning'">
            <view class="agent-learning-center card">
                <view class="card-title">
                    <text class="title-text">Agent学习中心</text>
                </view>
                
                <view class="learning-status">
                    <view class="learning-progress">
                        <text class="progress-title">模型训练进度</text>
                        <view class="progress-bar-container">
                            <view class="progress-bar" :style="{ width: `${learningProgress}%` }"></view>
                        </view>
                        <text class="progress-text">{{ learningProgress }}% 完成</text>
                    </view>
                    
                    <view class="learning-metrics">
                        <view class="metric-item">
                            <text class="metric-label">训练样本数</text>
                            <text class="metric-value">{{ learningMetrics.samples }}</text>
                        </view>
                        <view class="metric-item">
                            <text class="metric-label">准确率</text>
                            <text class="metric-value">{{ learningMetrics.accuracy }}%</text>
                        </view>
                        <view class="metric-item">
                            <text class="metric-label">模型迭代次数</text>
                            <text class="metric-value">{{ learningMetrics.iterations }}</text>
                        </view>
                    </view>
                </view>
                
                <!-- 添加训练状态指示器 -->
                <view v-if="isTraining" class="training-status">
                    <view class="training-indicator"></view>
                    <text class="training-text">Agent正在学习中,请稍候...</text>
                </view>
                
                <view class="learning-actions">
                    <button class="learning-btn" @click="startTraining" :disabled="isTraining" 
                        :style="{ backgroundColor: isTraining ? '#888888' : '#4c8dff' }">
                        {{ isTraining ? '⚙️ 训练进行中...' : '▶️ 开始训练' }}
                    </button>
                    <button class="learning-btn" @click="showLearningDetails">详细数据</button>
                </view>
                
                <view class="learning-models">
                    <view class="models-title">
                        <text class="title-text">已训练模型</text>
                    </view>
                    
                    <view class="model-list">
                        <view v-for="(model, index) in trainedModels" :key="index" class="model-item">
                            <text class="model-name">{{ model.name }}</text>
                            <text class="model-date">{{ model.date }}</text>
                            <text class="model-accuracy">准确率: {{ model.accuracy }}%</text>
                            <text class="model-performance" :class="model.performance >= 0 ? 'up' : 'down'">
                                表现: {{ model.performance >= 0 ? '+' : '' }}{{ model.performance }}%
                            </text>
                        </view>
                    </view>
                </view>
                
                <!-- 其他Agent功能链接 -->
                <view class="related-ai-functions">
                    <view class="section-title">
                        <text class="title-text">更多Agent功能</text>
                    </view>
                    
                    <view class="ai-function-cards">
                        <view class="function-card" @click="navigateTo('/pages/agent-training/index')">
                            <view class="function-icon training-icon"></view>
                            <text class="function-name">Agent模型训练</text>
                            <text class="function-desc">专业训练与模型调优</text>
                        </view>
                        
                        <view class="function-card" @click="navigateTo('/pages/agent-research/index')">
                            <view class="function-icon research-icon"></view>
                            <text class="function-name">Agent策略研究</text>
                            <text class="function-desc">高级策略研发与测试</text>
                        </view>
                        
                        <view class="function-card" @click="navigateTo('/pages/agent-prediction/index')">
                            <view class="function-icon prediction-icon"></view>
                            <text class="function-name">Agent智能预测</text>
                            <text class="function-desc">市场趋势与股票预测</text>
                        </view>
                    </view>
                </view>
            </view>
        </view>
    </view>
</template>

<script>
import AgentTradingPanel from '@/components/ai/AgentTradingPanel.vue';
import agentTradingService from '@/services/agentTradingService';

export default {
    components: {
        AgentTradingPanel
    },
    data() {
        return {
            // Tab导航
            activeTab: 'agent-trading',
            tabs: [
                { id: 'agent-trading', name: 'Agent决策交易' },
                { id: 'agent-learning', name: '学习中心' }
            ],
            
            // Agent学习中心数据
            learningProgress: 78,
            learningMetrics: {
                samples: 24680,
                accuracy: 85.6,
                iterations: 42
            },
            isTraining: false,
            trainingTimer: null,
            trainedModels: [
                { 
                    name: '趋势跟踪模型 v3.2', 
                    date: '2023-06-15', 
                    accuracy: 87.5, 
                    performance: 15.2 
                },
                { 
                    name: '形态识别模型 v2.8', 
                    date: '2023-05-28', 
                    accuracy: 82.1, 
                    performance: 9.6 
                },
                { 
                    name: '量价关系模型 v1.5', 
                    date: '2023-04-10', 
                    accuracy: 76.8, 
                    performance: -2.3 
                }
            ],
            
            // 原有数据
            searchText: '',
            selectedStock: null,
            isLoading: false,
            currentTheme: 'dark',
            themeClass: 'dark-theme',
            stockList: [
                { name: '贵州茅台', code: '600519', price: 1680.28, change: 0.75, industry: '白酒', avgVolume: 230.45, marketCap: 21080.32, peRatio: 35.2, pbRatio: 9.8, dividendYield: 1.1 },
                { name: '中国平安', code: '601318', price: 46.35, change: -0.28, industry: '金融保险', avgVolume: 320.80, marketCap: 8456.32, peRatio: 9.8, pbRatio: 1.2, dividendYield: 4.2 },
                { name: '阿里巴巴', code: '09988', price: 78.55, change: 1.20, industry: '互联网服务', avgVolume: 180.30, marketCap: 16885.25, peRatio: 18.6, pbRatio: 3.2, dividendYield: 0.8 },
                { name: '宁德时代', code: '300750', price: 242.36, change: 2.85, industry: '新能源', avgVolume: 165.20, marketCap: 5652.35, peRatio: 52.3, pbRatio: 8.5, dividendYield: 0.3 },
                { name: '招商银行', code: '600036', price: 34.58, change: -0.15, industry: '银行', avgVolume: 98.65, marketCap: 8720.50, peRatio: 7.2, pbRatio: 1.1, dividendYield: 4.8 }
            ],
            marketData: {
                indices: [
                    { name: '上证指数', code: '000001', price: 3458.23, change: 1.35 },
                    { name: '深证成指', code: '399001', price: 14256.89, change: 1.62 },
                    { name: '创业板指', code: '399006', price: 2876.45, change: -0.32 },
                    { name: '沪深300', code: '000300', price: 4652.78, change: 1.18 }
                ],
                sectors: [
                    { name: '食品饮料', change: 2.15, strength: 8 },
                    { name: '银行', change: 0.87, strength: 6 },
                    { name: '医药生物', change: -0.35, strength: 4 },
                    { name: '新能源', change: -1.25, strength: 3 },
                    { name: '电子科技', change: 1.48, strength: 7 }
                ],
                riskLevel: 'medium' // 市场整体风险水平: low, medium, high
            },
            analysisData: null,
            searchResults: [],
            showSearchResults: false
        }
    },
    onLoad() {
        // 从全局获取主题设置
        const app = getApp();
        if (app.globalData && app.globalData.theme) {
            this.currentTheme = app.globalData.theme;
            this.themeClass = this.currentTheme === 'dark' ? 'dark-theme' : 'light-theme';
        }
        
        // 检查是否有训练正在进行
        const trainingStatus = uni.getStorageSync('ai_training_status');
        if (trainingStatus && trainingStatus.isTraining) {
            this.isTraining = true;
            this.learningProgress = trainingStatus.progress;
            this.learningMetrics.iterations = trainingStatus.iterations;
            this.learningMetrics.accuracy = trainingStatus.accuracy;
            
            // 继续模拟训练进度
            this.trainingTimer = setInterval(() => {
                console.log('更新训练进度');
                this.learningProgress = Math.min(100, this.learningProgress + 2);
                this.learningMetrics.iterations += 1;
                this.learningMetrics.accuracy = Math.min(95, this.learningMetrics.accuracy + 0.5);
                
                // 更新本地存储
                uni.setStorageSync('ai_training_status', {
                    isTraining: true,
                    startTime: Date.now(),
                    progress: this.learningProgress,
                    iterations: this.learningMetrics.iterations,
                    accuracy: this.learningMetrics.accuracy
                });
                
                // 如果训练完成,清除定时器
                if (this.learningProgress >= 100) {
                    clearInterval(this.trainingTimer);
                    this.isTraining = false;
                    console.log('训练完成,状态已重置');
                    uni.setStorageSync('ai_training_status', {
                        isTraining: false,
                        startTime: Date.now(),
                        progress: 100,
                        iterations: this.learningMetrics.iterations,
                        accuracy: this.learningMetrics.accuracy
                    });
                    
                    // 显示完成提示
                    uni.showToast({
                        title: '训练已完成',
                        icon: 'success',
                        duration: 2000
                    });
                }
            }, 5000);
        }
    },
    onUnload() {
        // 清理定时器
        if (this.trainingTimer) {
            clearInterval(this.trainingTimer);
            this.trainingTimer = null;
        }
    },
    methods: {
        // 切换标签页
        switchTab(tabId) {
            this.activeTab = tabId;
        },
        
        // 导航到其他页面
        navigateTo(url) {
            uni.navigateTo({
                url: url
            });
        },
        
        // 切换主题
        toggleTheme() {
            this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
            this.themeClass = this.currentTheme === 'dark' ? 'dark-theme' : 'light-theme';
            
            // 更新全局主题设置
            const app = getApp();
            if (app.globalData) {
                app.globalData.theme = this.currentTheme;
            }
        },
        
        // Agent学习中心方法
        async startTraining() {
            if (this.isTraining) return; // 如果已经在训练,直接返回
            
            try {
                // 添加提示框
                uni.showModal({
                    title: '开始训练',
                    content: '即将开始Agent模型训练,这可能需要一些时间。',
                    success: async (res) => {
                        if (res.confirm) {
                            uni.showLoading({
                                title: '启动训练中...'
                            });
                            
                            console.log('准备调用agentTradingService.startModelTraining()');
                            // 显示调试信息
                            uni.showToast({
                                title: '正在启动训练...',
                                icon: 'none',
                                duration: 2000
                            });
                            
                            // 调用服务启动训练
                            try {
                                const result = await agentTradingService.startModelTraining();
                                console.log('训练启动结果:', result);
                                
                                uni.hideLoading();
                                
                                if (result && result.success) {
                                    // 设置训练状态
                                    this.isTraining = true;
                                    console.log('训练状态已设置为true');
                                    
                                    // 显示调试信息
                                    uni.showToast({
                                        title: '训练已启动成功',
                                        icon: 'success',
                                        duration: 2000
                                    });
                                    
                                    // 更新UI
                                    this.learningProgress = Math.min(100, this.learningProgress + 5);
                                    this.learningMetrics.iterations += 1;
                                    this.learningMetrics.accuracy = Math.min(95, this.learningMetrics.accuracy + 1.2);
                                    
                                    // 保存训练状态到本地存储
                                    uni.setStorageSync('ai_training_status', {
                                        isTraining: true,
                                        startTime: Date.now(),
                                        progress: this.learningProgress,
                                        iterations: this.learningMetrics.iterations,
                                        accuracy: this.learningMetrics.accuracy
                                    });
                                    
                                    // 添加定时器模拟训练进度
                                    this.trainingTimer = setInterval(() => {
                                        console.log('更新训练进度');
                                        this.learningProgress = Math.min(100, this.learningProgress + 2);
                                        this.learningMetrics.iterations += 1;
                                        this.learningMetrics.accuracy = Math.min(95, this.learningMetrics.accuracy + 0.5);
                                        
                                        // 更新本地存储
                                        uni.setStorageSync('ai_training_status', {
                                            isTraining: true,
                                            startTime: Date.now(),
                                            progress: this.learningProgress,
                                            iterations: this.learningMetrics.iterations,
                                            accuracy: this.learningMetrics.accuracy
                                        });
                                        
                                        // 如果训练完成,清除定时器并更新状态
                                        if (this.learningProgress >= 100) {
                                            clearInterval(this.trainingTimer);
                                            this.isTraining = false;
                                            console.log('训练完成,状态已重置');
                                            uni.setStorageSync('ai_training_status', {
                                                isTraining: false,
                                                startTime: Date.now(),
                                                progress: 100,
                                                iterations: this.learningMetrics.iterations,
                                                accuracy: this.learningMetrics.accuracy
                                            });
                                            
                                            // 显示完成提示
                                            uni.showToast({
                                                title: '训练已完成',
                                                icon: 'success',
                                                duration: 2000
                                            });
                                        }
                                    }, 5000); // 每5秒更新一次
                                } else {
                                    uni.showToast({
                                        title: '启动训练失败',
                                        icon: 'none'
                                    });
                                }
                            } catch (error) {
                                console.error('调用训练API错误:', error);
                                uni.hideLoading();
                                uni.showToast({
                                    title: '训练API调用错误',
                                    icon: 'none'
                                });
                            }
                        }
                    }
                });
            } catch (error) {
                uni.hideLoading();
                console.error('启动训练失败:', error);
                uni.showToast({
                    title: '启动训练失败,请重试',
                    icon: 'none'
                });
            }
        },
        
        showLearningDetails() {
            this.navigateTo('/pages/agent-analysis/learning/index');
        }
    }
}
</script>

<style>
/* 通用容器样式 */
.container {
    padding: 30rpx;
}

/* 暗色主题 */
.dark-theme {
    background-color: #141414;
    color: #fff;
}

/* 亮色主题 */
.light-theme {
    background-color: #f5f5f5;
    color: #333;
}

/* 头部样式 */
.header {
    margin-bottom: 30rpx;
}

.header-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10rpx;
}

.title {
    font-size: 40rpx;
    font-weight: bold;
}

.subtitle {
    font-size: 26rpx;
    color: #999;
    margin-bottom: 20rpx;
}

.theme-switch {
    width: 50rpx;
    height: 50rpx;
    display: flex;
    justify-content: center;
    align-items: center;
}

.theme-icon {
    width: 40rpx;
    height: 40rpx;
    border-radius: 50%;
}

.dark-icon {
    background-color: #333;
    border: 2rpx solid #666;
}

.light-icon {
    background-color: #f0f0f0;
    border: 2rpx solid #ccc;
}

/* 加载指示器 */
.loading-indicator {
    display: flex;
    align-items: center;
    margin-top: 20rpx;
}

.loading-spinner {
    width: 30rpx;
    height: 30rpx;
    border: 3rpx solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: #fff;
    animation: spin 1s linear infinite;
    margin-right: 10rpx;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading-text {
    font-size: 24rpx;
    color: #999;
}

/* 标签页导航 */
.tab-navigation {
    display: flex;
    border-bottom: 1rpx solid #333;
    margin-bottom: 20rpx;
}

.tab-item {
    padding: 20rpx 30rpx;
    font-size: 28rpx;
    border-bottom: 4rpx solid transparent;
    margin-right: 20rpx;
}

.dark-theme .tab-item {
    color: #999;
}

.light-theme .tab-item {
    color: #666;
}

.tab-item.active {
    border-bottom-color: #4c8dff;
}

.dark-theme .tab-item.active {
    color: #fff;
}

.light-theme .tab-item.active {
    color: #333;
}

/* Agent学习中心样式 */
.card {
    background-color: #222;
    border-radius: 12rpx;
    padding: 30rpx;
    margin-bottom: 30rpx;
}

.light-theme .card {
    background-color: #fff;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
}

.card-title {
    margin-bottom: 20rpx;
}

.title-text {
    font-size: 32rpx;
    font-weight: bold;
}

.learning-status {
    margin-bottom: 30rpx;
}

.learning-progress {
    margin-bottom: 20rpx;
}

.progress-title {
    font-size: 28rpx;
    margin-bottom: 10rpx;
}

.progress-bar-container {
    height: 16rpx;
    background-color: #333;
    border-radius: 8rpx;
    overflow: hidden;
    margin-bottom: 10rpx;
}

.light-theme .progress-bar-container {
    background-color: #eee;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #4c8dff, #0cce6b);
    border-radius: 8rpx;
}

.progress-text {
    font-size: 24rpx;
    color: #999;
    text-align: right;
}

.learning-metrics {
    display: flex;
    justify-content: space-between;
}

.metric-item {
    text-align: center;
    flex: 1;
}

.metric-label {
    font-size: 24rpx;
    color: #999;
    margin-bottom: 8rpx;
}

.metric-value {
    font-size: 30rpx;
    font-weight: bold;
}

/* 训练状态指示器样式 */
.training-status {
    display: flex;
    align-items: center;
    background-color: rgba(25, 137, 250, 0.1);
    padding: 15rpx;
    border-radius: 8rpx;
    margin-bottom: 20rpx;
}

.training-indicator {
    width: 20rpx;
    height: 20rpx;
    border-radius: 50%;
    background-color: #4c8dff;
    margin-right: 10rpx;
    animation: pulse 1s infinite ease-in-out;
}

.training-text {
    font-size: 24rpx;
    color: #4c8dff;
}

@keyframes pulse {
    0% { opacity: 0.3; }
    50% { opacity: 1; }
    100% { opacity: 0.3; }
}

.learning-actions {
    display: flex;
    justify-content: space-between;
    margin-bottom: 30rpx;
}

.learning-btn {
    width: 48%;
    padding: 20rpx 0;
    font-size: 28rpx;
    border: none;
    border-radius: 8rpx;
    color: #fff;
    background-color: #4c8dff;
}

.learning-models {
    margin-bottom: 30rpx;
}

.models-title {
    margin-bottom: 20rpx;
}

.model-list {
    display: flex;
    flex-direction: column;
}

.model-item {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 8rpx;
    padding: 20rpx;
    margin-bottom: 15rpx;
}

.light-theme .model-item {
    background-color: rgba(0, 0, 0, 0.02);
    border: 1rpx solid #eee;
}

.model-name {
    font-size: 28rpx;
    font-weight: bold;
    margin-bottom: 10rpx;
}

.model-date {
    font-size: 24rpx;
    color: #999;
    margin-bottom: 10rpx;
}

.model-accuracy {
    font-size: 24rpx;
    color: #4c8dff;
    margin-bottom: 10rpx;
}

.model-performance {
    font-size: 24rpx;
}

.model-performance.up {
    color: #0cce6b;
}

.model-performance.down {
    color: #ff4d4f;
}

/* 其他Agent功能链接 */
.section-title {
    margin-bottom: 20rpx;
}

.ai-function-cards {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
}

.function-card {
    width: 30%;
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 12rpx;
    padding: 20rpx;
    text-align: center;
}

.light-theme .function-card {
    background-color: rgba(0, 0, 0, 0.02);
    border: 1rpx solid #eee;
}

.function-icon {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    margin: 0 auto 15rpx;
}

.training-icon {
    background-color: #1989fa;
}

.research-icon {
    background-color: #ff4d4f;
}

.prediction-icon {
    background-color: #0cce6b;
}

.function-name {
    font-size: 26rpx;
    font-weight: bold;
    margin-bottom: 8rpx;
}

.function-desc {
    font-size: 22rpx;
    color: #999;
}
</style> 
