<template>
  <div class="ai-analytics-dashboard">
    <div class="dashboard-header">
      <h2>AI智能分析控制台</h2>
      <div class="actions">
        <button @click="refreshData" class="refresh-btn">
          <i class="icon-refresh"></i> 刷新数据
        </button>
      </div>
    </div>

    <!-- AI训练进度部分 -->
    <section class="dashboard-section training-progress">
      <h3>Agent模型训练进度</h3>
      <div class="training-cards">
        <div v-for="model in trainingProgress" :key="model.name" class="training-card" :class="{ 'active': model.status === 'training' }">
          <div class="card-header">
            <h4>{{ model.displayName }}</h4>
            <span class="status-badge" :class="model.status">{{ statusText[model.status] }}</span>
          </div>
          <div class="progress-container">
            <div class="progress-bar" :style="{ width: model.progress + '%' }"></div>
            <span class="progress-text">{{ model.progress }}%</span>
          </div>
          <div class="card-details">
            <div class="detail-item">
              <span class="label">开始时间:</span>
              <span>{{ formatDate(model.startTime) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">预计完成:</span>
              <span>{{ model.estimatedCompletion ? formatDate(model.estimatedCompletion) : '计算中...' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">当前批次:</span>
              <span>{{ model.currentEpoch }}/{{ model.totalEpochs }}</span>
            </div>
          </div>
          <div class="card-actions">
            <button @click="triggerTraining(model.name)" :disabled="model.status === 'training'" class="action-btn">
              {{ model.status === 'training' ? '训练中' : '开始训练' }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- 模型性能展示部分 -->
    <section class="dashboard-section model-performance">
      <h3>模型性能指标</h3>
      <div class="model-selector">
        <button v-for="modelType in modelTypes" 
                :key="modelType.id" 
                @click="selectModelType(modelType.id)"
                :class="{ 'active': selectedModelType === modelType.id }" 
                class="model-type-btn">
          {{ modelType.name }}
        </button>
      </div>
      
      <div class="performance-metrics">
        <div class="metrics-charts">
          <div class="chart-container">
            <h4>损失函数趋势</h4>
            <div id="loss-chart" class="chart"></div>
          </div>
          <div class="chart-container">
            <h4>准确率趋势</h4>
            <div id="accuracy-chart" class="chart"></div>
          </div>
        </div>
        
        <div class="metrics-cards">
          <div class="metric-card" v-for="metric in performanceMetrics" :key="metric.name">
            <div class="metric-value">{{ metric.value }}</div>
            <div class="metric-name">{{ metric.displayName }}</div>
            <div class="trend-indicator" :class="metric.trend">
              <i :class="'icon-' + metric.trend"></i>
              <span>{{ metric.changePercent }}%</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- AI预测结果可视化部分 -->
    <section class="dashboard-section prediction-results">
      <h3>AI预测结果可视化</h3>
      <div class="prediction-controls">
        <div class="control-group">
          <label>股票代码</label>
          <input v-model="predictionParams.stockCode" type="text" placeholder="输入股票代码" />
        </div>
        <div class="control-group">
          <label>预测时间步数</label>
          <select v-model="predictionParams.timeSteps">
            <option v-for="n in [5, 10, 15, 20, 30]" :key="n" :value="n">{{ n }} 天</option>
          </select>
        </div>
        <button @click="getPrediction" class="action-btn">生成预测</button>
      </div>
      
      <div v-if="predictionData" class="prediction-visualization">
        <div class="prediction-chart-container">
          <div id="prediction-chart" class="prediction-chart"></div>
        </div>
        <div class="prediction-details">
          <h4>预测详情</h4>
          <table class="prediction-table">
            <thead>
              <tr>
                <th>时间</th>
                <th>预测价格</th>
                <th>置信区间</th>
                <th>涨跌幅</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in predictionData.predictions" :key="index">
                <td>{{ formatPredictionDate(index) }}</td>
                <td>{{ item.predicted_price.toFixed(2) }}</td>
                <td>{{ item.lower_bound.toFixed(2) }} - {{ item.upper_bound.toFixed(2) }}</td>
                <td :class="getChangeClass(index)">
                  {{ getChangePercent(index) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import * as echarts from 'echarts';
import aiService from '../../services/aiService';

// 状态变量
const trainingProgress = ref([]);
const performanceMetrics = ref([]);
const predictionData = ref(null);
const selectedModelType = ref('price_prediction');
const isLoading = ref(false);
const predictionParams = ref({
  stockCode: '000001',
  timeSteps: 10
});

// 图表实例
let lossChart = null;
let accuracyChart = null;
let predictionChart = null;

// 状态文本映射
const statusText = {
  idle: '已就绪',
  training: '训练中',
  complete: '已完成',
  failed: '失败'
};

// 模型类型选项
const modelTypes = [
  { id: 'price_prediction', name: '价格预测模型' },
  { id: 'strategy_optimizer', name: '策略优化模型' },
  { id: 'risk_assessment', name: '风险评估模型' }
];

// 数据刷新方法
async function refreshData() {
  isLoading.value = true;
  try {
    await Promise.all([
      fetchTrainingProgress(),
      fetchModelPerformance(),
    ]);
  } catch (error) {
    console.error('数据刷新失败:', error);
  } finally {
    isLoading.value = false;
  }
}

// 获取训练进度数据
async function fetchTrainingProgress() {
  const data = await aiService.getTrainingProgress();
  if (data && !data.status) {
    trainingProgress.value = data;
  }
}

// 获取模型性能数据
async function fetchModelPerformance() {
  const data = await aiService.getModelPerformance(selectedModelType.value);
  if (data && !data.status) {
    performanceMetrics.value = data.metrics;
    updatePerformanceCharts(data.history);
  }
}

// 选择模型类型
function selectModelType(modelType) {
  selectedModelType.value = modelType;
  fetchModelPerformance();
}

// 触发模型训练
async function triggerTraining(modelType) {
  try {
    await aiService.triggerTraining(modelType);
    fetchTrainingProgress();
  } catch (error) {
    console.error('触发训练失败:', error);
  }
}

// 获取预测数据
async function getPrediction() {
  try {
    const { stockCode, timeSteps } = predictionParams.value;
    const data = await aiService.getPricePrediction(stockCode, timeSteps);
    if (data && !data.error) {
      predictionData.value = data;
      updatePredictionChart();
    }
  } catch (error) {
    console.error('获取预测数据失败:', error);
  }
}

// 更新性能指标图表
function updatePerformanceCharts(history) {
  if (!history || !lossChart || !accuracyChart) return;
  
  const epochs = history.epochs || [];
  const trainLoss = history.train_loss || [];
  const valLoss = history.val_loss || [];
  const trainAcc = history.train_accuracy || [];
  const valAcc = history.val_accuracy || [];
  
  lossChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['训练损失', '验证损失'] },
    xAxis: { type: 'category', data: epochs },
    yAxis: { type: 'value', name: '损失值' },
    series: [
      { name: '训练损失', type: 'line', data: trainLoss, smooth: true },
      { name: '验证损失', type: 'line', data: valLoss, smooth: true }
    ]
  });
  
  accuracyChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['训练准确率', '验证准确率'] },
    xAxis: { type: 'category', data: epochs },
    yAxis: { type: 'value', name: '准确率', min: 0, max: 1 },
    series: [
      { name: '训练准确率', type: 'line', data: trainAcc, smooth: true },
      { name: '验证准确率', type: 'line', data: valAcc, smooth: true }
    ]
  });
}

// 更新预测图表
function updatePredictionChart() {
  if (!predictionData.value || !predictionChart) return;
  
  const data = predictionData.value;
  const dates = Array.from({ length: data.predictions.length }, (_, i) => formatPredictionDate(i));
  
  const prices = data.predictions.map(p => p.predicted_price);
  const lowerBounds = data.predictions.map(p => p.lower_bound);
  const upperBounds = data.predictions.map(p => p.upper_bound);
  
  // 添加当前价格作为起点
  dates.unshift('当前');
  prices.unshift(data.current_price);
  lowerBounds.unshift(data.current_price);
  upperBounds.unshift(data.current_price);
  
  predictionChart.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const price = params[0].value;
        const lower = params[1].value;
        const upper = params[2].value;
        return `${params[0].name}<br/>
                预测价格: ${price.toFixed(2)}<br/>
                置信区间: ${lower.toFixed(2)} - ${upper.toFixed(2)}`;
      }
    },
    legend: {
      data: ['预测价格', '置信区间']
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value',
      name: '价格'
    },
    series: [
      {
        name: '预测价格',
        type: 'line',
        smooth: true,
        data: prices,
        symbolSize: 6,
        itemStyle: {
          color: '#1890ff'
        }
      },
      {
        name: '置信区间下限',
        type: 'line',
        smooth: true,
        data: lowerBounds,
        lineStyle: {
          opacity: 0.3,
          type: 'dashed'
        },
        itemStyle: {
          opacity: 0
        }
      },
      {
        name: '置信区间上限',
        type: 'line',
        smooth: true,
        data: upperBounds,
        lineStyle: {
          opacity: 0.3,
          type: 'dashed'
        },
        itemStyle: {
          opacity: 0
        },
        areaStyle: {
          color: '#1890ff',
          opacity: 0.1
        }
      }
    ]
  });
}

// 工具函数 - 格式化日期
function formatDate(timestamp) {
  if (!timestamp) return '未知';
  const date = new Date(timestamp);
  return `${date.getMonth()+1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
}

// 格式化预测日期
function formatPredictionDate(index) {
  const date = new Date();
  date.setDate(date.getDate() + index + 1);
  return `${date.getMonth()+1}/${date.getDate()}`;
}

// 获取价格变化百分比
function getChangePercent(index) {
  if (!predictionData.value || index === 0) return '0.00%';
  
  const current = predictionData.value.predictions[index].predicted_price;
  const prev = index === 0 ? 
    predictionData.value.current_price : 
    predictionData.value.predictions[index-1].predicted_price;
  
  const change = ((current - prev) / prev * 100).toFixed(2);
  return `${change > 0 ? '+' : ''}${change}%`;
}

// 获取价格变化样式
function getChangeClass(index) {
  if (!predictionData.value) return '';
  
  const current = predictionData.value.predictions[index].predicted_price;
  const prev = index === 0 ? 
    predictionData.value.current_price : 
    predictionData.value.predictions[index-1].predicted_price;
  
  return current > prev ? 'positive' : current < prev ? 'negative' : '';
}

// 监听模型类型变化
watch(selectedModelType, () => {
  fetchModelPerformance();
});

// 组件挂载后初始化
onMounted(() => {
  // 初始化图表实例
  lossChart = echarts.init(document.getElementById('loss-chart'));
  accuracyChart = echarts.init(document.getElementById('accuracy-chart'));
  predictionChart = echarts.init(document.getElementById('prediction-chart'));
  
  // 默认数据加载
  refreshData();
  
  // 窗口大小变化时重绘图表
  window.addEventListener('resize', () => {
    lossChart?.resize();
    accuracyChart?.resize();
    predictionChart?.resize();
  });
  
  // 示例数据 - 实际项目中应删除
  trainingProgress.value = [
    {
      name: 'price_prediction',
      displayName: '价格预测模型',
      status: 'training',
      progress: 65,
      startTime: Date.now() - 3600000,
      estimatedCompletion: Date.now() + 1800000,
      currentEpoch: 32,
      totalEpochs: 50
    },
    {
      name: 'strategy_optimizer',
      displayName: '策略优化模型',
      status: 'complete',
      progress: 100,
      startTime: Date.now() - 7200000,
      estimatedCompletion: Date.now() - 3600000,
      currentEpoch: 50,
      totalEpochs: 50
    },
    {
      name: 'risk_assessment',
      displayName: '风险评估模型',
      status: 'idle',
      progress: 0,
      startTime: null,
      estimatedCompletion: null,
      currentEpoch: 0,
      totalEpochs: 40
    }
  ];
  
  performanceMetrics.value = [
    { name: 'mse', displayName: '均方误差', value: '0.0324', trend: 'down', changePercent: '5.2' },
    { name: 'mae', displayName: '平均绝对误差', value: '0.1253', trend: 'down', changePercent: '3.7' },
    { name: 'accuracy', displayName: '准确率', value: '87.6%', trend: 'up', changePercent: '2.1' },
    { name: 'recall', displayName: '召回率', value: '0.825', trend: 'up', changePercent: '1.8' }
  ];
  
  // 模拟性能数据
  const mockHistory = {
    epochs: Array.from({ length: 50 }, (_, i) => i + 1),
    train_loss: Array.from({ length: 50 }, () => Math.random() * 0.5 + 0.1).sort((a, b) => b - a),
    val_loss: Array.from({ length: 50 }, () => Math.random() * 0.7 + 0.2).sort((a, b) => b - a),
    train_accuracy: Array.from({ length: 50 }, (_, i) => Math.min(0.95, 0.5 + i * 0.01)),
    val_accuracy: Array.from({ length: 50 }, (_, i) => Math.min(0.9, 0.45 + i * 0.009))
  };
  
  updatePerformanceCharts(mockHistory);
  
  // 模拟预测数据
  predictionData.value = {
    stock_code: '000001',
    current_price: 15.72,
    predictions: Array.from({ length: 10 }, (_, i) => {
      const basePrice = 15.72;
      const trend = Math.random() > 0.5 ? 1 : -1;
      const randomFactor = Math.random() * 0.05;
      const dayFactor = i * 0.02;
      const price = basePrice * (1 + trend * (randomFactor + dayFactor));
      return {
        time_step: i + 1,
        predicted_price: price,
        lower_bound: price * 0.95,
        upper_bound: price * 1.05,
        confidence: 0.95
      };
    })
  };
  
  updatePredictionChart();
});
</script>

<style scoped>
.ai-analytics-dashboard {
  padding: 20px;
  background-color: #f5f7f9;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dashboard-section {
  margin-bottom: 30px;
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
}

.dashboard-section h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 18px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

/* 训练进度卡片样式 */
.training-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.training-card {
  background: #fff;
  border-radius: 6px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e8eaed;
  transition: all 0.3s ease;
}

.training-card.active {
  border-color: #1890ff;
  box-shadow: 0 2px 12px rgba(24, 144, 255, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.card-header h4 {
  margin: 0;
  font-size: 16px;
}

.status-badge {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.idle {
  background-color: #f5f5f5;
  color: #999;
}

.status-badge.training {
  background-color: #e6f7ff;
  color: #1890ff;
}

.status-badge.complete {
  background-color: #f6ffed;
  color: #52c41a;
}

.status-badge.failed {
  background-color: #fff2f0;
  color: #ff4d4f;
}

.progress-container {
  height: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  margin-bottom: 15px;
  position: relative;
}

.progress-bar {
  height: 100%;
  background-color: #1890ff;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  right: 0;
  top: -18px;
  font-size: 12px;
  color: #888;
}

.card-details {
  margin-bottom: 15px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}

.detail-item .label {
  color: #888;
}

.card-actions {
  text-align: right;
}

/* 模型性能部分样式 */
.model-selector {
  display: flex;
  margin-bottom: 20px;
  overflow-x: auto;
  padding-bottom: 5px;
}

.model-type-btn {
  padding: 8px 16px;
  background: none;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
  transition: all 0.2s;
  white-space: nowrap;
}

.model-type-btn.active {
  background-color: #1890ff;
  border-color: #1890ff;
  color: #fff;
}

.metrics-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-container {
  background: #fff;
  border-radius: 6px;
  padding: 15px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.chart-container h4 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 15px;
  color: #666;
}

.chart {
  height: 300px;
}

.metrics-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.metric-card {
  background: #fff;
  border-radius: 6px;
  padding: 15px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.metric-value {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 5px;
}

.metric-name {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.trend-indicator {
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.trend-indicator.up {
  color: #52c41a;
}

.trend-indicator.down {
  color: #ff4d4f;
}

/* 预测结果部分样式 */
.prediction-controls {
  display: flex;
  align-items: flex-end;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.control-group {
  display: flex;
  flex-direction: column;
  min-width: 150px;
}

.control-group label {
  margin-bottom: 5px;
  font-size: 14px;
  color: #666;
}

.control-group input,
.control-group select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}

.action-btn {
  background-color: #1890ff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.action-btn:hover {
  background-color: #40a9ff;
}

.action-btn:disabled {
  background-color: #d9d9d9;
  cursor: not-allowed;
}

.prediction-visualization {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 20px;
}

.prediction-chart {
  height: 400px;
}

.prediction-table {
  width: 100%;
  border-collapse: collapse;
}

.prediction-table th,
.prediction-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.prediction-table th {
  font-weight: 500;
  color: #666;
}

.prediction-table .positive {
  color: #52c41a;
}

.prediction-table .negative {
  color: #ff4d4f;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .metrics-charts,
  .prediction-visualization {
    grid-template-columns: 1fr;
  }
  
  .training-cards {
    grid-template-columns: 1fr;
  }
}

/* 按钮和交互元素样式 */
.refresh-btn {
  background: none;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  padding: 6px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.refresh-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}
</style> 
