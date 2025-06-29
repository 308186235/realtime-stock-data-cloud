<template>
    <view class="container" :class="themeClass">
        <view class="header">
            <view class="title">Agent模型训练中心</view>
            <view class="subtitle">管理和监控AI模型的训练进度和性能</view>
        </view>
        
        <!-- 模型训练状态 -->
        <view class="card models-status">
            <view class="card-title">
                <text>模型训练状态</text>
                <text class="refresh-btn" @click="refreshData">刷新</text>
            </view>
            
            <view class="model-list">
                <view v-for="(model, index) in trainingModels" :key="index" class="model-item">
                    <view class="model-info">
                        <view class="model-name">{{model.displayName}}</view>
                        <view class="model-status" :class="getStatusClass(model.status)">{{getStatusText(model.status)}}</view>
                    </view>
                    
                    <view class="progress-container">
                        <view class="progress-bar">
                            <view class="progress" :style="{ width: model.progress + '%', backgroundColor: getProgressColor(model.status) }"></view>
                        </view>
                        <text class="progress-text">{{model.progress}}%</text>
                    </view>
                    
                    <view class="model-details">
                        <view v-if="model.status === 'training'" class="detail-item">
                            <text class="detail-label">当前轮次:</text>
                            <text class="detail-value">{{model.currentEpoch}}/{{model.totalEpochs}}</text>
                        </view>
                        <view v-if="model.status === 'training'" class="detail-item">
                            <text class="detail-label">预计完成:</text>
                            <text class="detail-value">{{formatTimeRemaining(model.estimatedCompletion)}}</text>
                        </view>
                        <view v-if="model.status === 'complete'" class="detail-item">
                            <text class="detail-label">完成时间:</text>
                            <text class="detail-value">{{formatDateTime(model.estimatedCompletion)}}</text>
                        </view>
                        
                        <view class="learning-metrics">
                            <view class="metric-item">
                                <text class="metric-label">准确率:</text>
                                <view class="metric-progress">
                                    <view class="metric-bar" :style="{ width: model.accuracy + '%' }"></view>
                                </view>
                                <text class="metric-value">{{model.accuracy || 0}}%</text>
                            </view>
                            <view class="metric-item">
                                <text class="metric-label">损失值:</text>
                                <view class="metric-progress">
                                    <view class="metric-bar" :style="{ width: (100 - (model.loss || 0) * 100) + '%' }"></view>
                                </view>
                                <text class="metric-value">{{(model.loss || 0).toFixed(4)}}</text>
                            </view>
                        </view>
                        
                        <view class="model-actions">
                            <button class="action-btn view-btn" @click="viewModelDetails(model)">查看详情</button>
                            <button v-if="model.status === 'idle'" class="action-btn start-btn" @click="startTraining(model)">开始训练</button>
                            <button v-if="model.status === 'training'" class="action-btn stop-btn" @click="stopTraining(model)">停止训练</button>
                            <button v-if="model.status === 'complete'" class="action-btn export-btn" @click="exportModel(model)">导出模型</button>
                        </view>
                    </view>
                </view>
            </view>
        </view>
        
        <!-- 性能指标 -->
        <view v-if="selectedModel" class="card performance-metrics">
            <view class="card-title">
                <text>{{selectedModel.displayName}} 性能指标</text>
                <view class="model-selector">
                    <picker @change="onModelChange" :value="modelIndex" :range="modelNames">
                        <view class="picker-value">
                            {{modelNames[modelIndex]}} <text class="down-arrow">▼</text>
                        </view>
                    </picker>
                </view>
            </view>
            
            <view class="metrics-grid">
                <view v-for="(metric, index) in modelPerformance.metrics" :key="index" class="metric-item">
                    <view class="metric-value">{{metric.value}}</view>
                    <view class="metric-name">{{metric.displayName}}</view>
                    <view class="metric-trend" :class="metric.trend === 'down' ? 'trend-good' : 'trend-bad'">
                        {{metric.trend === 'down' ? '↓' : '↑'}} {{metric.changePercent}}%
                    </view>
                </view>
            </view>
            
            <!-- 训练历史图表 -->
            <view class="training-history">
                <view class="chart-title">训练历史</view>
                <view class="chart-container">
                    <!-- H5环境下的图表容器 -->
                    <!-- #ifdef H5 -->
                    <view id="training-history-chart" class="chart-area"></view>
                    <!-- #endif -->
                    
                    <!-- APP或小程序环境下的图表容器 -->
                    <!-- #ifdef APP-PLUS || MP-WEIXIN -->
                    <view class="chart-area">
                        <canvas canvas-id="trainingHistoryChart" id="trainingHistoryChart" class="chart-canvas"></canvas>
                    </view>
                    <!-- #endif -->
                    
                    <!-- 备用显示:当图表无法渲染时显示 -->
                    <view v-if="chartLoading" class="chart-fallback">
                        <view class="fallback-message">训练历史数据图表加载中...</view>
                        <view class="fallback-bars">
                            <view class="fallback-bar" style="height: 60%;"></view>
                            <view class="fallback-bar" style="height: 40%;"></view>
                            <view class="fallback-bar" style="height: 75%;"></view>
                            <view class="fallback-bar" style="height: 50%;"></view>
                            <view class="fallback-bar" style="height: 85%;"></view>
                        </view>
                    </view>
                    
                    <!-- 图表加载失败时显示 -->
                    <view v-else-if="chartError" class="chart-fallback chart-error">
                        <view class="fallback-message">图表加载失败</view>
                        <view class="error-icon">!</view>
                        <button class="retry-btn" @click="retryLoadChart">重试</button>
                    </view>
                    
                    <view class="chart-legend">
                        <view class="legend-item">
                            <view class="legend-color train-color"></view>
                            <text class="legend-text">训练损失</text>
                        </view>
                        <view class="legend-item">
                            <view class="legend-color val-color"></view>
                            <text class="legend-text">验证损失</text>
                        </view>
                        <view class="legend-item">
                            <view class="legend-color train-acc-color"></view>
                            <text class="legend-text">训练准确率</text>
                        </view>
                        <view class="legend-item">
                            <view class="legend-color val-acc-color"></view>
                            <text class="legend-text">验证准确率</text>
                        </view>
                    </view>
                </view>
            </view>
        </view>
        
        <!-- 训练配置 -->
        <view class="card training-config">
            <view class="card-title">
                <text>训练配置</text>
            </view>
            
            <view class="config-form">
                <view class="form-item">
                    <text class="form-label">选择模型</text>
                    <picker @change="onConfigModelChange" :value="configModelIndex" :range="modelNames">
                        <view class="picker-value config-picker">
                            {{modelNames[configModelIndex]}} <text class="down-arrow">▼</text>
                        </view>
                    </picker>
                </view>
                
                <view class="form-item">
                    <text class="form-label">数据源</text>
                    <picker @change="onDataSourceChange" :value="dataSourceIndex" :range="dataSources">
                        <view class="picker-value config-picker">
                            {{dataSources[dataSourceIndex]}} <text class="down-arrow">▼</text>
                        </view>
                    </picker>
                </view>
                
                <view class="form-item">
                    <text class="form-label">轮次数量</text>
                    <slider :value="epochs" :min="10" :max="200" :step="10" show-value @change="onEpochsChange" />
                </view>
                
                <view class="form-item">
                    <text class="form-label">学习率</text>
                    <slider :value="learningRate * 1000" :min="1" :max="100" :step="1" @change="onLearningRateChange" />
                    <text class="slider-value">{{learningRate}}</text>
                </view>
                
                <view class="form-item">
                    <text class="form-label">批次大小</text>
                    <slider :value="batchSize" :min="16" :max="256" :step="16" show-value @change="onBatchSizeChange" />
                </view>
                
                <view class="form-item">
                    <text class="form-label">使用GPU加速</text>
                    <switch :checked="useGPU" @change="onGPUChange" />
                </view>
                
                <view class="form-actions">
                    <button class="config-btn primary" @click="applyConfig">应用配置</button>
                    <button class="config-btn reset" @click="resetConfig">重置</button>
                </view>
            </view>
        </view>
    </view>
</template>

<script>
import aiService from '../../services/aiService.js';
// 适配uni-app环境的方式导入echarts
// #ifdef H5
let echarts;
try {
    echarts = require('echarts');
} catch (error) {
    console.error('加载echarts库失败:', error);
}
// #endif

export default {
    data() {
        return {
            trainingModels: [],
            selectedModel: null,
            modelPerformance: { metrics: [], history: {} },
            modelIndex: 0,
            configModelIndex: 0,
            modelNames: [],
            dataSourceIndex: 0,
            dataSources: ['历史市场数据', '实时交易数据', '混合数据'],
            epochs: 50,
            learningRate: 0.001,
            batchSize: 32,
            useGPU: true,
            loading: false,
            themeClass: 'dark-theme', // 默认深色主题
            isDataLoaded: false,
            // 修改图表相关属性
            chartInstance: null,
            chartInitialized: false,
            // 兼容不同平台的图表渲染器
            canvasId: 'trainingHistoryChart',
            chartLoading: true,
            chartError: false,
            resizeListener: null
        };
    },
    
    onLoad(options) {
        // 检查URL参数并使用它们初始化页面
        if (options) {
            // 解析从AgentTradingPanel传过来的参数
            const progress = parseFloat(options.progress);
            const samples = parseInt(options.samples);
            const iterations = parseInt(options.iterations);
            const accuracy = parseFloat(options.accuracy);
            const returns = parseFloat(options.returns);
            const winRate = parseFloat(options.winRate);
            const drawdown = parseFloat(options.drawdown);
            
            // 创建初始模型数据
            if (!isNaN(progress) && !isNaN(accuracy)) {
                // 使用URL参数创建初始模型,同时确保显示三个模型
                this.trainingModels = [
                    {
                        name: 'price_prediction',
                        displayName: '价格预测模型',
                        status: 'training',
                        progress: progress,
                        startTime: Date.now() - 3600000,
                        estimatedCompletion: Date.now() + 1800000,
                        currentEpoch: iterations || 32,
                        totalEpochs: 50,
                        accuracy: (accuracy * 100).toFixed(2),
                        loss: 0.0256
                    },
                    {
                        name: 'strategy_optimizer',
                        displayName: '策略优化模型',
                        status: 'complete',
                        progress: 100,
                        startTime: Date.now() - 7200000,
                        estimatedCompletion: Date.now() - 3600000,
                        currentEpoch: 50,
                        totalEpochs: 50,
                        accuracy: '92.5',
                        loss: 0.0157
                    },
                    {
                        name: 'risk_assessment',
                        displayName: '风险评估模型',
                        status: 'idle',
                        progress: 0,
                        startTime: null,
                        estimatedCompletion: null,
                        currentEpoch: 0,
                        totalEpochs: 40,
                        accuracy: '0',
                        loss: 0.5000
                    }
                ];
                
                // 设置模型选择器数据
                this.modelNames = this.trainingModels.map(model => model.displayName);
                
                // 选中第一个模型
                this.selectedModel = this.trainingModels[0];
                
                // 设置模型性能数据
                this.modelPerformance = {
                    metrics: [
                        { name: 'mse', displayName: '均方误差', value: '0.0324', trend: 'down', changePercent: '5.2' },
                        { name: 'mae', displayName: '平均绝对误差', value: '0.1253', trend: 'down', changePercent: '3.7' },
                        { name: 'accuracy', displayName: '准确率', value: `${(accuracy * 100).toFixed(1)}%`, trend: 'up', changePercent: '2.1' },
                        { name: 'annual_return', displayName: '年化收益率', value: `${returns}%`, trend: 'up', changePercent: '3.5' },
                        { name: 'win_rate', displayName: '胜率', value: `${winRate}%`, trend: 'up', changePercent: '1.8' },
                        { name: 'max_drawdown', displayName: '最大回撤', value: `${drawdown}%`, trend: 'down', changePercent: '2.0' }
                    ],
                    history: {
                        epochs: Array.from({ length: iterations || 42 }, (_, i) => i + 1),
                        train_loss: Array.from({ length: iterations || 42 }, (_, i) => Math.max(0.01, 0.5 - i * 0.01)).sort((a, b) => a - b),
                        val_loss: Array.from({ length: iterations || 42 }, (_, i) => Math.max(0.02, 0.6 - i * 0.01)).sort((a, b) => a - b),
                        train_accuracy: Array.from({ length: iterations || 42 }, (_, i) => Math.min(accuracy * 1.05, 0.5 + i * 0.01)),
                        val_accuracy: Array.from({ length: iterations || 42 }, (_, i) => Math.min(accuracy, 0.45 + i * 0.01))
                    }
                };
                
                this.isDataLoaded = true;
            }
        }
        
        // 加载系统主题设置
        this.detectSystemTheme();
        
        // 如果没有从URL参数获取到数据,则从API获取训练模型数据
        if (!this.isDataLoaded) {
            this.fetchTrainingData();
        }
    },
    
    onReady() {
        // 页面加载完成后,如果已选中模型,就渲染图表
        if (this.selectedModel) {
            setTimeout(() => {
                this.renderTrainingHistoryChart();
            }, 800); // 延长延迟时间,确保DOM已完全加载
        }
    },
    
    // 页面显示时检查是否需要更新图表
    onShow() {
        if (this.selectedModel && !this.chartInitialized) {
            setTimeout(() => {
                this.renderTrainingHistoryChart();
            }, 800); // 延长延迟时间
        }
    },
    
    // 主题改变时更新图表
    watch: {
        themeClass() {
            this.onThemeChange();
        }
    },
    
    // 当窗口尺寸改变时,重新渲染图表
    onResize() {
        if (this.chartInstance) {
            // #ifdef H5
            this.chartInstance.resize();
            // #endif
        }
    },
    
    // 组件销毁前清理图表实例
    onUnload() {
        if (this.chartInstance) {
            // #ifdef H5
            this.chartInstance.dispose();
            // #endif
            this.chartInstance = null;
        }
        
        // #ifdef H5
        // 移除事件监听器
        if (this.resizeListener) {
            window.removeEventListener('resize', this.resizeListener);
        }
        // #endif
    },
    
    methods: {
        // 检测系统主题
        detectSystemTheme() {
            // 先从本地存储获取用户之前的主题设置
            try {
                const savedTheme = uni.getStorageSync('appTheme');
                if (savedTheme) {
                    this.themeClass = savedTheme === 'dark' ? 'dark-theme' : 'light-theme';
                    return;
                }
            } catch (e) {
                console.log('获取存储的主题失败', e);
            }
            
            // 检测系统主题
            uni.getSystemInfo({
                success: (res) => {
                    // 根据系统明暗主题设置主题
                    if (res.theme) {
                        this.themeClass = res.theme === 'dark' ? 'dark-theme' : 'light-theme';
                    } else if (res.osTheme) {
                        this.themeClass = res.osTheme === 'dark' ? 'dark-theme' : 'light-theme';
                    } else {
                        // 默认设置为深色主题
                        this.themeClass = 'dark-theme';
                    }
                },
                fail: () => {
                    // 默认为深色主题
                    this.themeClass = 'dark-theme';
                }
            });
        },
        
        // 获取训练数据
        async fetchTrainingData() {
            try {
                this.loading = true;
                // 获取训练进度数据
                const models = await aiService.getTrainingProgress();
                
                // 检查是否成功获取三个模型的数据
                if (models && Array.isArray(models) && models.length === 3) {
                    this.trainingModels = models;
                } else {
                    // 如果返回的不是三个模型,则使用默认的三个模型数据
                    console.warn('API未返回三个模型数据,使用默认模型数据');
                    this.trainingModels = this.getDefaultModels();
                }
                
                // 设置模型选择器数据
                this.modelNames = this.trainingModels.map(model => model.displayName);
                
                // 默认选中第一个模型
                if (this.trainingModels.length > 0) {
                    this.selectedModel = this.trainingModels[0];
                    // 获取第一个模型的性能数据
                    this.fetchModelPerformance(this.trainingModels[0].name);
                }
                
                this.isDataLoaded = true;
            } catch (err) {
                console.error('获取AI训练数据失败:', err);
                // 使用默认模型数据
                this.trainingModels = this.getDefaultModels();
                this.modelNames = this.trainingModels.map(model => model.displayName);
                
                if (this.trainingModels.length > 0) {
                    this.selectedModel = this.trainingModels[0];
                }
                
                this.isDataLoaded = true;
                
                uni.showToast({
                    title: '获取训练数据失败,使用默认数据',
                    icon: 'none'
                });
            } finally {
                this.loading = false;
            }
        },
        
        // 获取默认模型数据
        getDefaultModels() {
            return [
                {
                    name: 'price_prediction',
                    displayName: '价格预测模型',
                    status: 'training',
                    progress: 65,
                    startTime: Date.now() - 3600000,
                    estimatedCompletion: Date.now() + 1800000,
                    currentEpoch: 32,
                    totalEpochs: 50,
                    accuracy: '75.0',
                    loss: 0.025
                },
                {
                    name: 'strategy_optimizer',
                    displayName: '策略优化模型',
                    status: 'complete',
                    progress: 100,
                    startTime: Date.now() - 7200000,
                    estimatedCompletion: Date.now() - 3600000,
                    currentEpoch: 50,
                    totalEpochs: 50,
                    accuracy: '92.5',
                    loss: 0.015
                },
                {
                    name: 'risk_assessment',
                    displayName: '风险评估模型',
                    status: 'idle',
                    progress: 0,
                    startTime: null,
                    estimatedCompletion: null,
                    currentEpoch: 0,
                    totalEpochs: 40,
                    accuracy: '0',
                    loss: 0.5
                }
            ];
        },
        
        // 获取模型性能数据
        async fetchModelPerformance(modelType) {
            try {
                const performance = await aiService.getModelPerformance(modelType);
                
                // 验证返回的数据是否完整
                if (performance && performance.metrics && performance.metrics.length > 0) {
                    this.modelPerformance = performance;
                } else {
                    // 如果返回数据不完整,使用默认性能数据
                    console.warn('API返回的性能数据不完整,使用默认性能数据');
                    this.modelPerformance = this.getDefaultPerformance(modelType);
                }
                
                // 如果界面上有图表,这里会更新图表数据
                // this.updateCharts(performance.history);
            } catch (err) {
                console.error('获取模型性能数据失败:', err);
                // 使用默认性能数据
                this.modelPerformance = this.getDefaultPerformance(modelType);
                
                uni.showToast({
                    title: '获取性能数据失败,使用默认数据',
                    icon: 'none'
                });
            }
        },
        
        // 获取默认性能数据
        getDefaultPerformance(modelType) {
            // 根据模型类型返回不同的默认性能数据
            switch(modelType) {
                case 'price_prediction':
                    return {
                        metrics: [
                            { name: 'mse', displayName: '均方误差', value: '0.0324', trend: 'down', changePercent: '5.2' },
                            { name: 'mae', displayName: '平均绝对误差', value: '0.1253', trend: 'down', changePercent: '3.7' },
                            { name: 'accuracy', displayName: '准确率', value: '85.6%', trend: 'up', changePercent: '2.1' },
                            { name: 'annual_return', displayName: '年化收益率', value: '12.5%', trend: 'up', changePercent: '3.5' },
                            { name: 'win_rate', displayName: '胜率', value: '65%', trend: 'up', changePercent: '1.8' },
                            { name: 'max_drawdown', displayName: '最大回撤', value: '8.2%', trend: 'down', changePercent: '2.0' }
                        ],
                        history: this.generateDefaultHistory(0.85)
                    };
                case 'strategy_optimizer':
                    return {
                        metrics: [
                            { name: 'sharpe', displayName: '夏普比率', value: '1.85', trend: 'up', changePercent: '4.2' },
                            { name: 'sortino', displayName: '索提诺比率', value: '2.32', trend: 'up', changePercent: '5.1' },
                            { name: 'accuracy', displayName: '准确率', value: '92.5%', trend: 'up', changePercent: '1.5' },
                            { name: 'annual_return', displayName: '年化收益率', value: '18.7%', trend: 'up', changePercent: '2.8' },
                            { name: 'win_rate', displayName: '胜率', value: '72%', trend: 'up', changePercent: '3.2' },
                            { name: 'max_drawdown', displayName: '最大回撤', value: '6.4%', trend: 'down', changePercent: '4.5' }
                        ],
                        history: this.generateDefaultHistory(0.925)
                    };
                case 'risk_assessment':
                    return {
                        metrics: [
                            { name: 'var', displayName: '风险价值', value: '2.45%', trend: 'down', changePercent: '3.1' },
                            { name: 'cvar', displayName: '条件风险价值', value: '3.62%', trend: 'down', changePercent: '2.8' },
                            { name: 'accuracy', displayName: '准确率', value: '0%', trend: 'up', changePercent: '0.0' },
                            { name: 'risk_score', displayName: '风险评分', value: '中等', trend: 'neutral', changePercent: '0.0' },
                            { name: 'coverage', displayName: '覆盖率', value: '95%', trend: 'up', changePercent: '0.0' },
                            { name: 'confidence', displayName: '置信度', value: '0%', trend: 'neutral', changePercent: '0.0' }
                        ],
                        history: this.generateDefaultHistory(0)
                    };
                default:
                    // 默认性能数据
                    return {
                        metrics: [
                            { name: 'mse', displayName: '均方误差', value: '0.0324', trend: 'down', changePercent: '5.2' },
                            { name: 'mae', displayName: '平均绝对误差', value: '0.1253', trend: 'down', changePercent: '3.7' },
                            { name: 'accuracy', displayName: '准确率', value: '87.6%', trend: 'up', changePercent: '2.1' },
                            { name: 'recall', displayName: '召回率', value: '0.825', trend: 'up', changePercent: '1.8' }
                        ],
                        history: this.generateDefaultHistory(0.85)
                    };
            }
        },
        
        // 生成默认历史数据
        generateDefaultHistory(targetAccuracy) {
            const epochs = 50;
            return {
                epochs: Array.from({ length: epochs }, (_, i) => i + 1),
                train_loss: Array.from({ length: epochs }, (_, i) => Math.max(0.01, 0.5 - i * 0.01)).sort((a, b) => a - b),
                val_loss: Array.from({ length: epochs }, (_, i) => Math.max(0.02, 0.6 - i * 0.01)).sort((a, b) => a - b),
                train_accuracy: Array.from({ length: epochs }, (_, i) => Math.min(targetAccuracy * 1.05, 0.5 + i * 0.01)),
                val_accuracy: Array.from({ length: epochs }, (_, i) => Math.min(targetAccuracy, 0.45 + i * 0.01))
            };
        },
        
        // 刷新数据
        refreshData() {
            this.fetchTrainingData();
            uni.showToast({
                title: '数据已刷新',
                icon: 'none'
            });
            
            // 如果当前选中模型,刷新图表
            if (this.selectedModel) {
                this.fetchModelPerformance(this.selectedModel.name);
            }
        },
        
        // 获取状态样式类
        getStatusClass(status) {
            switch (status) {
                case 'training': return 'status-training';
                case 'complete': return 'status-complete';
                case 'idle': return 'status-idle';
                default: return '';
            }
        },
        
        // 获取状态显示文本
        getStatusText(status) {
            switch (status) {
                case 'training': return '训练中';
                case 'complete': return '已完成';
                case 'idle': return '未开始';
                default: return status;
            }
        },
        
        // 获取进度条颜色
        getProgressColor(status) {
            switch (status) {
                case 'training': return '#4c8dff';
                case 'complete': return '#52c41a';
                default: return '#999';
            }
        },
        
        // 格式化剩余时间
        formatTimeRemaining(timestamp) {
            const now = Date.now();
            const diff = timestamp - now;
            
            if (diff <= 0) return '即将完成';
            
            const minutes = Math.floor(diff / 60000);
            const hours = Math.floor(minutes / 60);
            
            if (hours > 0) {
                return `约${hours}小时${minutes % 60}分钟`;
            } else {
                return `约${minutes}分钟`;
            }
        },
        
        // 格式化日期时间
        formatDateTime(timestamp) {
            const date = new Date(timestamp);
            return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
        },
        
        // 查看模型详情
        viewModelDetails(model) {
            this.selectedModel = model;
            this.modelIndex = this.trainingModels.findIndex(m => m.name === model.name);
            this.fetchModelPerformance(model.name);
            
            // 获取数据后渲染图表
            setTimeout(() => {
                this.renderTrainingHistoryChart();
            }, 300);
        },
        
        // 渲染训练历史图表
        renderTrainingHistoryChart() {
            // 重置状态
            this.chartLoading = true;
            this.chartError = false;
            
            // 确保有历史数据
            if (!this.modelPerformance.history || !this.modelPerformance.history.epochs) {
                console.warn('没有图表历史数据');
                this.chartError = true;
                this.chartLoading = false;
                return;
            }
            
            // 延迟一点时间,确保DOM已经渲染完成
            setTimeout(() => {
                const history = this.modelPerformance.history;
                
                // 准备图表配置
                const option = {
                    color: ['#4c8dff', '#ff4d4f', '#52c41a', '#faad14'],
                    animation: true,
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross'
                        }
                    },
                    legend: {
                        data: ['训练损失', '验证损失', '训练准确率', '验证准确率'],
                        textStyle: {
                            color: this.themeClass === 'dark-theme' ? '#ccc' : '#333'
                        }
                    },
                    grid: {
                        left: '3%',
                        right: '4%',
                        bottom: '3%',
                        containLabel: true
                    },
                    xAxis: {
                        type: 'category',
                        boundaryGap: false,
                        data: history.epochs,
                        axisLabel: {
                            color: this.themeClass === 'dark-theme' ? '#ccc' : '#333'
                        }
                    },
                    yAxis: [
                        {
                            type: 'value',
                            name: '损失',
                            position: 'left',
                            axisLabel: {
                                formatter: '{value}',
                                color: this.themeClass === 'dark-theme' ? '#ccc' : '#333'
                            },
                            splitLine: {
                                lineStyle: {
                                    color: this.themeClass === 'dark-theme' ? '#333' : '#eee'
                                }
                            }
                        },
                        {
                            type: 'value',
                            name: '准确率',
                            min: 0,
                            max: 1,
                            position: 'right',
                            axisLabel: {
                                formatter: '{value * 100}%',
                                color: this.themeClass === 'dark-theme' ? '#ccc' : '#333'
                            },
                            splitLine: {
                                show: false
                            }
                        }
                    ],
                    series: [
                        {
                            name: '训练损失',
                            type: 'line',
                            yAxisIndex: 0,
                            data: history.train_loss || [],
                            smooth: true,
                            lineStyle: {
                                width: 2
                            },
                            symbol: 'circle',
                            symbolSize: 5
                        },
                        {
                            name: '验证损失',
                            type: 'line',
                            yAxisIndex: 0,
                            data: history.val_loss || [],
                            smooth: true,
                            lineStyle: {
                                width: 2
                            },
                            symbol: 'circle',
                            symbolSize: 5
                        },
                        {
                            name: '训练准确率',
                            type: 'line',
                            yAxisIndex: 1,
                            data: history.train_accuracy || [],
                            smooth: true,
                            lineStyle: {
                                width: 2
                            },
                            symbol: 'circle',
                            symbolSize: 5
                        },
                        {
                            name: '验证准确率',
                            type: 'line',
                            yAxisIndex: 1,
                            data: history.val_accuracy || [],
                            smooth: true,
                            lineStyle: {
                                width: 2
                            },
                            symbol: 'circle',
                            symbolSize: 5
                        }
                    ]
                };
                
                // 使用uni-app环境特有的方式渲染图表
                // #ifdef H5
                this.initEChartsForH5(option);
                // #endif
                
                // #ifdef APP-PLUS || MP-WEIXIN
                this.initEChartsForMobile(option);
                // #endif
            }, 300); // 增加延迟时间
        },
        
        // 在H5环境中初始化echarts
        initEChartsForH5(option) {
            try {
                // 检查echarts是否正确加载
                if (typeof echarts === 'undefined') {
                    console.error('echarts库未加载');
                    this.chartError = true;
                    uni.showToast({
                        title: '图表库加载失败',
                        icon: 'none'
                    });
                    return;
                }

                const chartDom = document.getElementById('training-history-chart');
                if (!chartDom) {
                    console.error('图表DOM元素不存在');
                    this.chartError = true;
                    return;
                }
                
                // 确保容器有足够的高度和宽度
                chartDom.style.height = '350px';
                chartDom.style.width = '100%';
                
                // 清除之前的实例
                if (this.chartInstance) {
                    this.chartInstance.dispose();
                }
                
                // 初始化图表
                this.chartInstance = echarts.init(chartDom);
                this.chartInitialized = true;
                this.chartLoading = false;
                console.log('echarts已初始化');
                
                // 设置图表
                this.chartInstance.setOption(option);
                console.log('echarts已设置数据');
                
                // 确保图表会随窗口调整大小
                if (this.resizeListener) {
                    window.removeEventListener('resize', this.resizeListener);
                }
                
                this.resizeListener = () => {
                    if (this.chartInstance) {
                        this.chartInstance.resize();
                    }
                };
                
                window.addEventListener('resize', this.resizeListener);
            } catch (error) {
                console.error('初始化图表失败:', error);
                this.chartError = true;
                this.chartLoading = false;
                uni.showToast({
                    title: '图表初始化失败',
                    icon: 'none'
                });
            }
        },
        
        // 在移动端环境中初始化echarts
        initEChartsForMobile(option) {
            // 注意:在APP或小程序中可能需要使用组件方式
            // 这里使用uni-app提供的canvas组件
            this.chartInitialized = true;
            
            // 在APP和小程序中,可以用uni.createCanvasContext创建上下文
            // 这需要结合第三方的echarts适配库,如mpvue-echarts或uCharts
            // 由于这里是示例,仅作为参考
            uni.showToast({
                title: '当前环境不支持图表',
                icon: 'none'
            });
        },
        
        // 主题变化时更新图表
        onThemeChange() {
            // 清理现有图表
            if (this.chartInstance) {
                // #ifdef H5
                this.chartInstance.dispose();
                // #endif
                this.chartInstance = null;
                this.chartInitialized = false;
            }
            
            // 重新渲染图表
            setTimeout(() => {
                this.renderTrainingHistoryChart();
            }, 300);
        },
        
        // 开始训练模型
        async startTraining(model) {
            if (model.status === 'training') {
                uni.showToast({
                    title: '模型已在训练中',
                    icon: 'none'
                });
                return;
            }
            
            try {
                uni.showLoading({
                    title: '启动训练...',
                    mask: true
                });
                
                // 构建训练参数
                const trainingParams = {
                    epochs: this.epochs,
                    learning_rate: this.learningRate,
                    batch_size: this.batchSize,
                    data_source: this.dataSources[this.dataSourceIndex],
                    use_gpu: this.useGPU
                };
                
                // 调用AI服务启动训练,传递GPU使用选项
                const response = await aiService.startModelTraining(
                    model.name,
                    trainingParams,
                    this.useGPU
                );
                
                if (response && response.status === 'success') {
                    // 更新模型状态为训练中
                    model.status = 'training';
                    model.progress = 0;
                    model.currentEpoch = 0;
                    
                    // 显示开始训练的提示,包含GPU状态
                    uni.showToast({
                        title: `训练已开始${this.useGPU ? ' (GPU加速)' : ''}`,
                        icon: 'success'
                    });
                    
                    // 如果返回了预估完成时间
                    if (response.estimated_time) {
                        const now = new Date();
                        const estimatedDate = new Date(now.getTime() + 90 * 60 * 1000); // 假设90分钟
                        model.estimatedCompletion = estimatedDate.toISOString();
                    }
                    
                    // 开始模拟训练进度更新
                    this.startProgressSimulation(model);
                } else {
                    throw new Error(response?.message || '启动训练失败');
                }
            } catch (error) {
                console.error('启动训练失败:', error);
                uni.showToast({
                    title: `启动训练失败: ${error.message || '未知错误'}`,
                    icon: 'none'
                });
            } finally {
                uni.hideLoading();
            }
        },
        
        // 停止训练模型
        async stopTraining(model) {
            try {
                uni.showLoading({
                    title: '停止训练中'
                });
                
                // 这里应该调用实际的API
                // const result = await aiService.stopModelTraining(model.name);
                
                // 模拟训练停止
                setTimeout(() => {
                    uni.hideLoading();
                    
                    // 更新模型状态
                    const index = this.trainingModels.findIndex(m => m.name === model.name);
                    if (index >= 0) {
                        this.trainingModels[index].status = 'idle';
                        this.trainingModels[index].progress = 0;
                    }
                    
                    uni.showToast({
                        title: '训练已停止',
                        icon: 'success'
                    });
                }, 1500);
                
            } catch (err) {
                uni.hideLoading();
                console.error('停止训练失败:', err);
                uni.showToast({
                    title: '停止训练失败',
                    icon: 'none'
                });
            }
        },
        
        // 导出模型
        exportModel(model) {
            uni.showToast({
                title: '模型导出功能暂未实现',
                icon: 'none'
            });
        },
        
        // 模型选择变化
        onModelChange(e) {
            const index = e.detail.value;
            this.modelIndex = index;
            this.selectedModel = this.trainingModels[index];
            this.fetchModelPerformance(this.selectedModel.name);
        },
        
        // 配置中的模型选择变化
        onConfigModelChange(e) {
            this.configModelIndex = e.detail.value;
        },
        
        // 数据源变化
        onDataSourceChange(e) {
            this.dataSourceIndex = e.detail.value;
        },
        
        // 轮次数量变化
        onEpochsChange(e) {
            this.epochs = e.detail.value;
        },
        
        // 学习率变化
        onLearningRateChange(e) {
            this.learningRate = e.detail.value / 1000;
        },
        
        // 批次大小变化
        onBatchSizeChange(e) {
            this.batchSize = e.detail.value;
        },
        
        // GPU使用变化
        onGPUChange(e) {
            this.useGPU = e.detail.value;
        },
        
        // 应用配置
        applyConfig() {
            const selectedModel = this.trainingModels[this.configModelIndex];
            if (!selectedModel) return;
            
            uni.showToast({
                title: `配置已应用到${selectedModel.displayName}`,
                icon: 'none'
            });
        },
        
        // 重置配置
        resetConfig() {
            this.epochs = 50;
            this.learningRate = 0.001;
            this.batchSize = 32;
            this.useGPU = true;
            this.dataSourceIndex = 0;
            
            uni.showToast({
                title: '配置已重置',
                icon: 'none'
            });
        },
        
        // 重试加载图表
        retryLoadChart() {
            this.chartError = false;
            this.chartLoading = true;
            this.chartInitialized = false;
            
            // 重新初始化图表
            setTimeout(() => {
                this.renderTrainingHistoryChart();
            }, 500);
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

.refresh-btn {
    font-size: 24rpx;
    color: #4c8dff;
    padding: 6rpx 12rpx;
    border-radius: 6rpx;
    background-color: rgba(76, 141, 255, 0.1);
    cursor: pointer;
}

.dark-theme .refresh-btn:active,
.dark-theme .refresh-btn:hover {
    background-color: rgba(76, 141, 255, 0.2);
}

.light-theme .refresh-btn:active,
.light-theme .refresh-btn:hover {
    background-color: rgba(76, 141, 255, 0.15);
}

/* 模型列表样式 */
.model-list {
    display: flex;
    flex-direction: column;
}

.model-item {
    padding: 20rpx;
    margin-bottom: 20rpx;
    border-radius: 8rpx;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.dark-theme .model-item {
    background-color: #2d2d2d;
    border: 1px solid #3a3a3a;
}

.light-theme .model-item {
    background-color: #ffffff;
    border: 1px solid #eeeeee;
}

.model-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10rpx;
}

.model-name {
    font-size: 28rpx;
    font-weight: bold;
}

.model-status {
    font-size: 24rpx;
    padding: 4rpx 10rpx;
    border-radius: 20rpx;
}

.status-training {
    background-color: rgba(76, 141, 255, 0.2);
    color: #4c8dff;
}

.status-complete {
    background-color: rgba(82, 196, 26, 0.2);
    color: #52c41a;
}

.status-idle {
    background-color: rgba(153, 153, 153, 0.2);
    color: #999999;
}

.progress-container {
    margin: 10px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.progress-bar {
    flex: 1;
    height: 8px;
    background: #333;
    border-radius: 4px;
    overflow: hidden;
}

.progress {
    height: 100%;
    transition: width 0.3s ease;
    border-radius: 4px;
}

.dark-theme .progress-bar {
    background: #2a2a2a;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
}

.light-theme .progress-bar {
    background: #eeeeee;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.progress-text {
    font-size: 14px;
    font-weight: bold;
    color: #ffffff;
    text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
    min-width: 40px;
    text-align: right;
}

.light-theme .progress-text {
    color: #333333;
    text-shadow: none;
}

/* 学习指标样式 */
.learning-metrics {
    margin: 15rpx 0;
    padding: 15rpx;
    background-color: rgba(76, 175, 80, 0.1);
    border-radius: 10rpx;
}

.learning-metrics .metric-item {
    margin-bottom: 15rpx;
    display: flex;
    align-items: center;
}

.learning-metrics .metric-item:last-child {
    margin-bottom: 0;
}

.learning-metrics .metric-label {
    font-size: 26rpx;
    color: rgba(255, 255, 255, 0.7);
    display: inline-block;
    width: 120rpx;
}

.learning-metrics .metric-progress {
    flex: 1;
    height: 10rpx;
    background-color: rgba(200, 200, 200, 0.2);
    border-radius: 5rpx;
    margin: 0 10rpx;
    overflow: hidden;
    position: relative;
}

.learning-metrics .metric-bar {
    height: 100%;
    background: linear-gradient(90deg, #4caf50, #8bc34a);
    border-radius: 5rpx;
    transition: width 0.5s ease-out;
}

.learning-metrics .metric-value {
    font-size: 28rpx;
    font-weight: bold;
    color: #fff;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    display: inline-block;
    width: 80rpx;
    text-align: right;
}

/* 性能指标网格样式 */
.metrics-grid .metric-value {
    width: auto;
    font-size: 36rpx;
    font-weight: bold;
    margin-bottom: 8rpx;
    color: #ffffff;
    text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
}

.light-theme .metrics-grid .metric-value {
    color: #333333;
    text-shadow: none;
}

.model-details {
    margin-top: 15rpx;
}

.detail-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8rpx;
}

.detail-label {
    font-size: 24rpx;
    color: #999;
}

.detail-value {
    font-size: 24rpx;
}

.model-actions {
    display: flex;
    gap: 10px;
    margin-top: 15px;
}

.action-btn {
    flex: 1;
    padding: 8px 0;
    border-radius: 4px;
    font-size: 14px;
    text-align: center;
    border: none;
    cursor: pointer;
    transition: opacity 0.3s;
}

.action-btn:active {
    opacity: 0.8;
}

.view-btn {
    background: #2196F3;
    color: white;
}

.start-btn {
    background: #4CAF50;
    color: white;
}

.stop-btn {
    background: #f44336;
    color: white;
}

.export-btn {
    background: #FF9800;
    color: white;
}

/* 性能指标样式 */
.model-selector {
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

.metrics-grid {
    display: flex;
    flex-wrap: wrap;
    margin-bottom: 20rpx;
    gap: 10px;
}

.metrics-grid .metric-item {
    width: calc(50% - 5px);
    padding: 20rpx;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    border-radius: 8px;
}

.dark-theme .metrics-grid .metric-item {
    background-color: #2d2d2d;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.light-theme .metrics-grid .metric-item {
    background-color: #f9f9f9;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.metrics-grid .metric-name {
    font-size: 24rpx;
    color: #bbbbbb;
    margin-bottom: 12rpx;
}

.light-theme .metrics-grid .metric-name {
    color: #666666;
}

.metrics-grid .metric-trend {
    font-size: 22rpx;
    font-weight: bold;
    padding: 4rpx 12rpx;
    border-radius: 20rpx;
}

.dark-theme .metrics-grid .trend-good {
    color: #52c41a;
    background-color: rgba(82, 196, 26, 0.15);
}

.dark-theme .metrics-grid .trend-bad {
    color: #ff4d4f;
    background-color: rgba(255, 77, 79, 0.15);
}

.light-theme .metrics-grid .trend-good {
    color: #52c41a;
    background-color: rgba(82, 196, 26, 0.1);
}

.light-theme .metrics-grid .trend-bad {
    color: #ff4d4f;
    background-color: rgba(255, 77, 79, 0.1);
}

/* 训练历史样式 */
.training-history {
    margin-top: 30rpx;
}

.chart-title {
    font-size: 28rpx;
    font-weight: bold;
    margin-bottom: 15rpx;
}

.chart-container {
    height: 400rpx;
    margin-bottom: 20rpx;
    position: relative;
}

.chart-area {
    height: 350rpx;
    width: 100%;
    border-radius: 8rpx;
    background-color: rgba(255, 255, 255, 0.05);
}

.dark-theme .chart-area {
    background-color: #2d2d2d;
}

.light-theme .chart-area {
    background-color: #f5f5f5;
}

.chart-canvas {
    width: 100%;
    height: 100%;
}

.chart-legend {
    display: flex;
    justify-content: center;
    margin-top: 15rpx;
}

.legend-item {
    display: flex;
    align-items: center;
    margin: 0 10rpx;
}

.legend-color {
    width: 20rpx;
    height: 10rpx;
    margin-right: 6rpx;
}

.train-color {
    background-color: #4c8dff;
}

.val-color {
    background-color: #ff4d4f;
}

.train-acc-color {
    background-color: #52c41a;
}

.val-acc-color {
    background-color: #faad14;
}

.legend-text {
    font-size: 22rpx;
    color: #999;
}

/* 训练配置样式 */
.config-form {
    padding: 10rpx;
}

.form-item {
    margin-bottom: 20rpx;
}

.form-label {
    display: block;
    font-size: 26rpx;
    margin-bottom: 10rpx;
}

.config-picker {
    height: 70rpx;
    line-height: 70rpx;
}

.slider-value {
    margin-left: 10rpx;
    font-size: 24rpx;
}

.form-actions {
    display: flex;
    margin-top: 30rpx;
}

.config-btn {
    flex: 1;
    height: 80rpx;
    border-radius: 8rpx;
    font-size: 28rpx;
    line-height: 80rpx;
    text-align: center;
    margin: 0 10rpx;
}

.primary {
    background-color: #4c8dff;
    color: #fff;
}

.reset {
    background-color: transparent;
}

.dark-theme .reset {
    border: 1px solid #555;
    color: #ddd;
}

.light-theme .reset {
    border: 1px solid #ddd;
    color: #666;
}

/* 添加备用图表的CSS样式 */
.chart-fallback {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 350rpx;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 8rpx;
}

.fallback-message {
    font-size: 24rpx;
    color: #999;
    margin-bottom: 20rpx;
}

.fallback-bars {
    display: flex;
    width: 80%;
    height: 180rpx;
    justify-content: space-between;
    align-items: flex-end;
}

.fallback-bar {
    width: 30rpx;
    background: linear-gradient(to top, #4c8dff, #52c41a);
    border-radius: 4rpx;
    animation: pulse 1.5s infinite alternate;
}

@keyframes pulse {
    0% { opacity: 0.6; }
    100% { opacity: 1; }
}

/* 图表错误状态样式 */
.chart-error {
    background-color: rgba(255, 77, 79, 0.05);
}

.error-icon {
    width: 60rpx;
    height: 60rpx;
    line-height: 60rpx;
    text-align: center;
    background-color: #ff4d4f;
    color: white;
    border-radius: 50%;
    font-size: 40rpx;
    font-weight: bold;
    margin: 20rpx 0;
}

.retry-btn {
    background-color: #4c8dff;
    color: white;
    font-size: 24rpx;
    padding: 10rpx 30rpx;
    border-radius: 30rpx;
    margin-top: 20rpx;
    border: none;
}
</style> 
