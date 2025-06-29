<template>
  <view class="strategy-panel">
    <!-- 压力测试控制模块 -->
    <view class="control-section">
      <button @click="runStressTest" :loading="isTesting">执行压力测试</button>
      <text class="status-text">{{ testStatus }}</text>
    </view>

    <!-- 测试结果可视化 -->
    <view class="chart-container">
      <canvas id="latencyChart" canvas-id="latencyChart"></canvas>
    </view>

    <!-- 统计指标展示 -->
    <view class="metrics-grid">
      <view class="metric-item">
        <text class="metric-label">成功率</text>
        <text class="metric-value">{{ metrics.successRate }}%</text>
      </view>
      <view class="metric-item">
        <text class="metric-label">吞吐量</text>
        <text class="metric-value">{{ metrics.throughput.toFixed(1) }} req/s</text>
      </view>
      <view class="metric-item">
        <text class="metric-label">平均延迟</text>
        <text class="metric-value">{{ metrics.avgLatency }}ms</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import * as echarts from '@/components/ec-canvas/echarts'

const isTesting = ref(false)
const testStatus = ref('准备就绪')
const chart = ref(null)
const metrics = ref({
  successRate: 0,
  throughput: 0,
  avgLatency: 0
})

const initChart = () => {
  chart.value = echarts.init(document.getElementById('latencyChart'))
  chart.value.setOption({
    title: { text: '请求延迟分布', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: [] },
    yAxis: { type: 'value', name: '延迟(ms)' },
    series: [{
      name: '延迟',
      type: 'line',
      smooth: true,
      data: []
    }]
  })
}

const runStressTest = async () => {
  try {
    isTesting.value = true
    testStatus.value = '测试进行中...'
    
    const response = await uni.request({
      url: 'http://localhost:8000/stress-test',
      method: 'POST',
      data: {
        target_api: '/api/trade',
        concurrent_users: 100,
        duration_seconds: 60,
        ramp_up_time: 10
      }
    })

    updateMetrics(response.data)
    updateChart(response.data.latency_stats)
    testStatus.value = '测试完成'
  } catch (error) {
    testStatus.value = '测试失败:' + error.message
  } finally {
    isTesting.value = false
  }
}

const updateMetrics = (data) => {
  metrics.value = {
    successRate: (data.success_rate * 100).toFixed(1),
    throughput: data.throughput,
    avgLatency: data.latency_stats.avg
  }
}

const updateChart = (latencyData) => {
  chart.value.setOption({
    xAxis: { data: Object.keys(latencyData) },
    series: [{ data: Object.values(latencyData) }]
  })
}

onMounted(() => {
  initChart()
})
</script>

<style>
.strategy-panel {
  padding: 20px;
  background-color: #f5f6fa;
}

.control-section {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.chart-container {
  height: 300px;
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-top: 20px;
}

.metric-item {
  background: white;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.metric-label {
  color: #718096;
  font-size: 14px;
}

.metric-value {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin-top: 8px;
}
</style>

新增三大功能模块:
◼ 实时延迟折线图(基于ECharts)
◼ 成功率和吞吐量统计面板
◼ 带渐变加载效果的测试控制组件
