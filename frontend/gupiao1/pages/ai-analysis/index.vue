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
                
                <!-- 添加训练状态显示器用于调试 -->
                <view class="debug-status" v-if="isTraining">
                    <text>训练状态: {{isTraining ? '进行中' : '未开始'}}</text>
                    <text>进度: {{learningProgress}}%</text>
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
                    <!-- 训练开始按钮 -->
                    <button v-show="!isTraining" class="learning-btn start-btn" @click="startTraining">
                        <view class="button-content">
                            <view class="button-icon">▶️</view>
                            <text>开始训练</text>
                        </view>
                    </button>
                    
                    <!-- 训练中按钮 -->
                    <button v-show="isTraining" class="learning-btn training-btn">
                        <view class="button-content">
                            <view class="button-icon rotating">⚙️</view>
                            <text>训练进行中...</text>
                        </view>
                    </button>
                    
                    <button class="learning-btn" @click="showLearningDetails">详细数据</button>
                </view>
                
                <view class="learning-models">
                    <view class="models-title">
                        <text class="title-text">已训练模型</text>
                    </view>
                    
                    <view class="model-list">
                        <view v-for="(model, index) in trainedModels" :key="index" class="model-item">
                            <view class="model-header">
                                <text class="model-name">{{ model.name }}</text>
                                <text class="model-date">{{ model.date }}</text>
                            </view>
                            <view class="model-body">
                                <view class="model-metric">
                                    <text class="model-metric-label">准确率:</text>
                                    <text class="model-accuracy">{{ model.accuracy }}%</text>
                                </view>
                                <view class="model-metric">
                                    <text class="model-metric-label">表现:</text>
                                    <text class="model-performance" :class="model.performance >= 0 ? 'up' : 'down'">
                                        {{ model.performance >= 0 ? '+' : '' }}{{ model.performance }}%
                                    </text>
                                </view>
                            </view>
                        </view>
                    </view>
                </view>
                
                <!-- 其他Agent功能链接 -->
                <view class="related-agent-functions">
                    <view class="section-title">
                        <text class="title-text">更多Agent功能</text>
                    </view>
                    
                    <view class="agent-function-cards">
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
            activeTab: 'agent-learning',
            tabs: [
                { id: 'agent-trading', name: 'Agent决策交易' },
                { id: 'agent-learning', name: '学习中心' }
            ],
            
            // Agent学习中心数据
            learningProgress: 55,
            learningMetrics: {
                samples: 24680,
                accuracy: 78.5,
                iterations: 32
            },
            isTraining: false,
            initComplete: false,
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
                },
                {
                    name: '均线策略模型 v2.0',
                    date: '2023-07-20',
                    accuracy: 81.3,
                    performance: 8.7
                },
                {
                    name: '波浪理论模型 v1.2',
                    date: '2023-03-05',
                    accuracy: 72.4,
                    performance: 5.1
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
                { name: '招商银行', code: '600036', price: 34.58, change: -0.15, industry: '银行', avgVolume: 98.65, marketCap: 8720.50, peRatio: 7.2, pbRatio: 1.1, dividendYield: 4.8 },
                { name: '腾讯控股', code: '00700', price: 338.80, change: 1.45, industry: '互联网服务', avgVolume: 145.50, marketCap: 32520.60, peRatio: 24.3, pbRatio: 4.8, dividendYield: 0.6 },
                { name: '格力电器', code: '000651', price: 36.25, change: -0.62, industry: '家电', avgVolume: 52.30, marketCap: 2176.65, peRatio: 10.5, pbRatio: 2.1, dividendYield: 3.5 },
                { name: '恒瑞医药', code: '600276', price: 32.86, change: 2.12, industry: '医药生物', avgVolume: 63.21, marketCap: 1905.32, peRatio: 42.8, pbRatio: 7.2, dividendYield: 0.7 },
                { name: '海康威视', code: '002415', price: 27.64, change: 0.84, industry: '电子科技', avgVolume: 75.42, marketCap: 2578.36, peRatio: 22.1, pbRatio: 5.3, dividendYield: 1.8 },
                { name: '中国石油', code: '601857', price: 5.78, change: -0.34, industry: '能源', avgVolume: 28.50, marketCap: 10586.32, peRatio: 8.7, pbRatio: 0.9, dividendYield: 5.6 }
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
    watch: {
        isTraining(newVal, oldVal) {
            console.log(`isTraining changed from ${oldVal} to ${newVal}`);
        }
    },
    onLoad() {
        // 从全局获取主题设置
        const app = getApp();
        if (app.globalData && app.globalData.theme) {
            this.currentTheme = app.globalData.theme;
            this.themeClass = this.currentTheme === 'dark' ? 'dark-theme' : 'light-theme';
        }
        
        // 强制初始化数据
        this.initAgentTrainingData();
    },
    onShow() {
        // 每次页面显示时检查训练状态
        console.log('Page shown, checking training status');
        this.checkTrainingStatus();
        
        // 添加调试信息
        console.log('Current training state:', this.isTraining);
    },
    onUnload() {
        // 清理定时器
        if (this.trainingTimer) {
            clearInterval(this.trainingTimer);
            this.trainingTimer = null;
        }
    },
    methods: {
        // 初始化Agent训练数据
        initAgentTrainingData() {
            console.log('初始化Agent训练数据');
            // 检查是否有训练正在进行
            this.checkTrainingStatus();
            
            // 标记初始化完成
            this.initComplete = true;
        },
        
        // 更新训练状态的辅助方法
        updateTrainingState(isTraining, progress, iterations, accuracy) {
            // 更新组件状态
            this.isTraining = isTraining;
            
            // 设置其他状态变量
            if (progress !== undefined) this.learningProgress = progress;
            if (iterations !== undefined) this.learningMetrics.iterations = iterations;
            if (accuracy !== undefined) this.learningMetrics.accuracy = accuracy;
            
            // 更新本地存储
            uni.setStorageSync('agent_training_status', {
                isTraining: isTraining,
                startTime: Date.now(),
                progress: this.learningProgress,
                iterations: this.learningMetrics.iterations,
                accuracy: this.learningMetrics.accuracy
            });
            
            console.log('训练状态已更新:', isTraining ? '训练中' : '未训练');
        },
        
        // 检查训练状态
        checkTrainingStatus() {
            // 获取本地存储中的训练状态
            try {
                const trainingStatus = uni.getStorageSync('agent_training_status');
                console.log('获取到训练状态:', trainingStatus);
                
                if (trainingStatus && trainingStatus.isTraining) {
                    // 更新训练状态
                    this.updateTrainingState(true, trainingStatus.progress, trainingStatus.iterations, trainingStatus.accuracy);
                    
                    // 如果有定时器,先清除
                    if (this.trainingTimer) {
                        clearInterval(this.trainingTimer);
                    }
                    
                    // 继续模拟训练进度
                    this.trainingTimer = setInterval(() => {
                        console.log('更新训练进度');
                        const newProgress = Math.min(100, this.learningProgress + 2);
                        const newIterations = this.learningMetrics.iterations + 1;
                        const newAccuracy = Math.min(95, this.learningMetrics.accuracy + 0.5);
                        
                        // 使用辅助方法更新状态
                        this.updateTrainingState(true, newProgress, newIterations, newAccuracy);
                        
                        // 如果训练完成,清除定时器
                        if (this.learningProgress >= 100) {
                            clearInterval(this.trainingTimer);
                            
                            // 更新为已完成状态
                            this.updateTrainingState(false, 100, this.learningMetrics.iterations, this.learningMetrics.accuracy);
                            
                            console.log('训练完成,状态已重置');
                            
                            // 显示完成提示
                            uni.showToast({
                                title: '训练已完成',
                                icon: 'success',
                                duration: 2000
                            });
                        }
                    }, 5000);
                } else {
                    // 确保状态为false
                    this.updateTrainingState(false, this.learningProgress, this.learningMetrics.iterations, this.learningMetrics.accuracy);
                    
                    // 清除定时器
                    if (this.trainingTimer) {
                        clearInterval(this.trainingTimer);
                        this.trainingTimer = null;
                    }
                }
            } catch (e) {
                console.error('获取训练状态失败:', e);
                // 在错误情况下重置状态
                this.updateTrainingState(false, this.learningProgress, this.learningMetrics.iterations, this.learningMetrics.accuracy);
            }
        },
        
        // 切换标签页
        switchTab(tabId) {
            this.activeTab = tabId;
        },
        
        // 导航到其他页面
        navigateTo(url) {
            console.log('导航到:', url);
            
            // 特殊处理Agent预测页面的导航,提供友好提示
            if (url === '/pages/agent-prediction/index') {
                uni.showToast({
                    title: '正在加载Agent预测,将使用默认股票(贵州茅台)',
                    icon: 'none',
                    duration: 2000
                });
            }
            
            uni.navigateTo({
                url: url,
                fail: (err) => {
                    console.error('导航失败:', err);
                    uni.showToast({
                        title: '页面跳转失败',
                        icon: 'none'
                    });
                }
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
            console.log('Start training clicked, current state:', this.isTraining);
            
            if (this.isTraining) {
                console.log('Already training, ignoring click');
                return;
            }
            
            // 立即设置状态,不使用async/await或复杂逻辑
            this.isTraining = true;
            console.log('State changed to:', this.isTraining);
            
            // 直接更新存储
            uni.setStorageSync('agent_training_status', {
                isTraining: true,
                startTime: Date.now(),
                progress: this.learningProgress,
                iterations: this.learningMetrics.iterations,
                accuracy: this.learningMetrics.accuracy
            });
            
            // 显示Toast提示
            uni.showToast({
                title: '训练已开始',
                icon: 'success',
                duration: 1500
            });
            
            // 开始训练进度模拟
            this.startProgressSimulation();
        },
        
        // 分离进度模拟为独立函数
        startProgressSimulation() {
            // 清除现有定时器
            if (this.trainingTimer) {
                clearInterval(this.trainingTimer);
            }
            
            // 设置新定时器
            this.trainingTimer = setInterval(() => {
                console.log('Updating training progress');
                this.learningProgress = Math.min(100, this.learningProgress + 2);
                this.learningMetrics.iterations += 1;
                this.learningMetrics.accuracy = Math.min(95, this.learningMetrics.accuracy + 0.5);
                
                // 更新本地存储
                uni.setStorageSync('agent_training_status', {
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
                    console.log('Training completed, reset state');
                    
                    uni.setStorageSync('agent_training_status', {
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
            }, 3000); // 每3秒更新一次
        },
        
        showLearningDetails() {
            this.navigateTo('/pages/agent-training/index');
        }
    }
}
</script>

<style>
/* 通用容器样式 */
.container {
    padding: 30rpx;
    padding-bottom: 110rpx;
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
    margin-bottom: 15rpx;
    background-color: rgba(76, 141, 255, 0.05);
    border-radius: 8rpx;
    padding: 15rpx;
}

.metric-item {
    text-align: center;
    flex: 1;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
    padding: 0 10rpx;
}

.metric-item:last-child {
    border-right: none;
}

.metric-label {
    font-size: 24rpx;
    color: #999;
    margin-bottom: 8rpx;
    display: block;
}

.metric-value {
    font-size: 30rpx;
    font-weight: bold;
    color: #4c8dff;
    display: block;
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
}

.start-btn {
    background-color: #4c8dff;
}

.training-btn {
    background-color: #888888;
    border: 2px solid #aaaaaa;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.button-content {
    display: flex;
    align-items: center;
    justify-content: center;
}

.button-icon {
    margin-right: 10rpx;
    font-size: 24rpx;
}

.rotating {
    display: inline-block;
    animation: rotate 2s linear infinite;
}

.learning-models {
    margin-bottom: 30rpx;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding-top: 20rpx;
}

.models-title {
    margin-bottom: 20rpx;
    display: flex;
    align-items: center;
}

.models-title .title-text {
    font-size: 32rpx;
    font-weight: bold;
    position: relative;
}

.models-title .title-text:after {
    content: '';
    position: absolute;
    bottom: -8rpx;
    left: 0;
    width: 60rpx;
    height: 4rpx;
    background-color: #4c8dff;
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
    border-left: 4rpx solid #4c8dff;
}

.light-theme .model-item {
    background-color: rgba(0, 0, 0, 0.02);
    border: 1rpx solid #eee;
    border-left: 4rpx solid #4c8dff;
}

.model-header {
    margin-bottom: 15rpx;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.model-name {
    font-size: 28rpx;
    font-weight: bold;
}

.model-date {
    font-size: 24rpx;
    color: #999;
}

.model-body {
    display: flex;
    justify-content: space-between;
}

.model-metric {
    display: flex;
    align-items: center;
}

.model-metric-label {
    font-size: 24rpx;
    color: #999;
    margin-right: 5rpx;
}

.model-accuracy {
    font-size: 26rpx;
    color: #4c8dff;
    font-weight: bold;
}

.model-performance {
    font-size: 26rpx;
    font-weight: bold;
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

.agent-function-cards {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    margin-bottom: 30rpx;
}

.function-card {
    width: 30%;
    background-color: rgba(76, 141, 255, 0.1);
    border-radius: 12rpx;
    padding: 20rpx;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 20rpx;
    transition: all 0.3s ease;
}

.function-card:hover {
    transform: translateY(-5rpx);
    box-shadow: 0 8rpx 20rpx rgba(0, 0, 0, 0.1);
}

.light-theme .function-card {
    background-color: #ffffff;
    border: 1rpx solid #eaeaea;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.function-icon {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    margin-bottom: 15rpx;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 36rpx;
}

.training-icon {
    background: linear-gradient(135deg, #4c8dff, #006eff);
    color: #ffffff;
}

.training-icon:before {
    content: "🧠";
}

.research-icon {
    background: linear-gradient(135deg, #ff6b6b, #ee0979);
    color: #ffffff;
}

.research-icon:before {
    content: "🔍";
}

.prediction-icon {
    background: linear-gradient(135deg, #56ab2f, #a8e063);
    color: #ffffff;
}

.prediction-icon:before {
    content: "📊";
}

.function-name {
    font-size: 28rpx;
    font-weight: bold;
    margin-bottom: 10rpx;
    text-align: center;
}

.function-desc {
    font-size: 24rpx;
    color: #999999;
    text-align: center;
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

/* 亮色主题相关调整 */
.light-theme .card {
    background-color: #fff;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
}

.light-theme .learning-metrics {
    background-color: rgba(76, 141, 255, 0.05);
}

.light-theme .metric-item {
    border-right: 1px solid rgba(0, 0, 0, 0.05);
}

.light-theme .learning-models {
    border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.light-theme .training-status {
    background-color: rgba(25, 137, 250, 0.1);
}

/* 添加调试状态显示样式 */
.debug-status {
    background-color: rgba(0, 0, 0, 0.7);
    color: #fff;
    padding: 10rpx;
    border-radius: 8rpx;
    font-size: 24rpx;
    margin-bottom: 10rpx;
    display: flex;
    flex-direction: column;
}
</style> 
