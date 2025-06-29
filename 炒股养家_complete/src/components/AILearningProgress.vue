<template>
  <div class="agent-learning-progress">
    <h2 class="title">AI 学习进度</h2>
    
    <div class="progress-container">
      <div class="progress-section">
        <h3>模型训练状态</h3>
        <div class="status-card">
          <div class="status-item">
            <span class="label">当前训练轮次:</span>
            <span class="value">{{ currentEpoch }}</span>
          </div>
          <div class="status-item">
            <span class="label">总训练轮次:</span>
            <span class="value">{{ totalEpochs }}</span>
          </div>
          <div class="status-item">
            <span class="label">训练状态:</span>
            <span class="value" :class="trainingStatus">{{ trainingStatusText }}</span>
          </div>
        </div>
      </div>

      <div class="progress-section">
        <h3>学习指标</h3>
        <div class="metrics-card">
          <div class="metric-item">
            <span class="label">准确率:</span>
            <div class="progress-bar">
              <div class="progress" :style="{ width: accuracy + '%' }"></div>
            </div>
            <span class="value">{{ accuracy }}%</span>
          </div>
          <div class="metric-item">
            <span class="label">损失值:</span>
            <div class="progress-bar">
              <div class="progress" :style="{ width: (100 - loss) + '%' }"></div>
            </div>
            <span class="value">{{ loss.toFixed(4) }}</span>
          </div>
        </div>
      </div>

      <div class="progress-section">
        <h3>训练历史</h3>
        <div class="history-card">
          <div class="history-item" v-for="(item, index) in trainingHistory" :key="index">
            <span class="time">{{ item.time }}</span>
            <span class="event">{{ item.event }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AILearningProgress',
  data() {
    return {
      currentEpoch: 0,
      totalEpochs: 100,
      trainingStatus: 'running', // running, paused, completed
      accuracy: 75,
      loss: 0.2345,
      trainingHistory: [
        { time: '2024-03-20 10:00', event: '开始训练' },
        { time: '2024-03-20 10:30', event: '完成第1轮训练' },
        { time: '2024-03-20 11:00', event: '完成第2轮训练' }
      ]
    }
  },
  computed: {
    trainingStatusText() {
      const statusMap = {
        running: '训练中',
        paused: '已暂停',
        completed: '已完成'
      }
      return statusMap[this.trainingStatus]
    }
  },
  methods: {
    // 这里可以添加更新数据的方法
    updateProgress(data) {
      this.currentEpoch = data.currentEpoch
      this.accuracy = data.accuracy
      this.loss = data.loss
      this.trainingStatus = data.status
    }
  }
}
</script>

<style scoped>
.agent-learning-progress {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.title {
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #eee;
}

.progress-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.progress-section {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 15px;
}

.progress-section h3 {
  font-size: 18px;
  color: #444;
  margin-bottom: 15px;
}

.status-card, .metrics-card, .history-card {
  background: white;
  border-radius: 6px;
  padding: 15px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.status-item, .metric-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.label {
  color: #666;
  width: 120px;
}

.value {
  font-weight: 500;
  color: #333;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #eee;
  border-radius: 4px;
  margin: 0 10px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background: #4CAF50;
  transition: width 0.3s ease;
}

.training-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
}

.running {
  background: #e3f2fd;
  color: #1976d2;
}

.paused {
  background: #fff3e0;
  color: #f57c00;
}

.completed {
  background: #e8f5e9;
  color: #388e3c;
}

.history-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.history-item:last-child {
  border-bottom: none;
}

.time {
  color: #999;
  font-size: 14px;
}

.event {
  color: #333;
}
</style> 
