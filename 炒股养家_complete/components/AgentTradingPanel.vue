<template>
  <div class="agent-trading-panel">
    <!-- 系统状态卡片 -->
    <div class="status-card">
      <h3>🤖 Agent智能交易系统</h3>
      <div class="status-indicators">
        <div class="indicator" :class="{ active: systemStatus.hotkey_trader?.active }">
          <span class="dot"></span>
          快捷键交易器
        </div>
        <div class="indicator" :class="{ active: systemStatus.trading_agent?.active }">
          <span class="dot"></span>
          AI决策引擎
        </div>
        <div class="indicator" :class="{ active: systemStatus.hotkey_trader?.auto_trading_enabled }">
          <span class="dot"></span>
          自动交易
        </div>
      </div>
    </div>

    <!-- 控制面板 -->
    <div class="control-panel">
      <h4>🎛️ 系统控制</h4>
      <div class="control-buttons">
        <button 
          @click="startSystem" 
          :disabled="isSystemActive"
          class="btn btn-success"
        >
          🚀 启动系统
        </button>
        <button 
          @click="stopSystem" 
          :disabled="!isSystemActive"
          class="btn btn-danger"
        >
          🛑 停止系统
        </button>
        <button 
          @click="toggleAutoTrading"
          :disabled="!isSystemActive"
          class="btn btn-warning"
        >
          {{ autoTradingEnabled ? '⏸️ 暂停自动交易' : '▶️ 启用自动交易' }}
        </button>
      </div>
    </div>

    <!-- 手动交易面板 -->
    <div class="manual-trading">
      <h4>📝 手动交易</h4>
      <div class="trading-form">
        <div class="form-row">
          <label>股票代码:</label>
          <input v-model="manualTrade.symbol" placeholder="600000" maxlength="6" />
        </div>
        <div class="form-row">
          <label>价格:</label>
          <input v-model="manualTrade.price" type="number" step="0.01" placeholder="10.50" />
        </div>
        <div class="form-row">
          <label>数量:</label>
          <input v-model="manualTrade.quantity" type="number" step="100" placeholder="100" />
        </div>
        <div class="form-row">
          <label>操作:</label>
          <select v-model="manualTrade.action">
            <option value="buy">买入</option>
            <option value="sell">卖出</option>
          </select>
        </div>
        <div class="form-actions">
          <button @click="executeManualTrade" class="btn btn-primary" :disabled="!canExecuteTrade">
            🎯 执行交易
          </button>
          <button @click="getAgentDecision" class="btn btn-info" :disabled="!isSystemActive">
            🤖 获取AI建议
          </button>
        </div>
      </div>
    </div>

    <!-- 自动交易面板 -->
    <div class="auto-trading">
      <h4>🤖 自动交易</h4>
      <div class="auto-trading-form">
        <div class="form-row">
          <label>监控股票:</label>
          <input v-model="autoTrade.symbol" placeholder="600000" maxlength="6" />
        </div>
        <div class="form-actions">
          <button @click="executeAutoTrade" class="btn btn-success" :disabled="!canAutoTrade">
            🚀 启动自动交易
          </button>
        </div>
      </div>
    </div>

    <!-- 配置面板 -->
    <div class="config-panel">
      <h4>⚙️ 交易配置</h4>
      <div class="config-form">
        <div class="form-row">
          <label>最大日交易次数:</label>
          <input v-model="config.max_daily_trades" type="number" min="1" max="100" />
        </div>
        <div class="form-row">
          <label>最大仓位比例:</label>
          <input v-model="config.max_position_size" type="number" step="0.01" min="0.01" max="1.0" />
        </div>
        <div class="form-row">
          <label>最小置信度:</label>
          <input v-model="config.min_confidence_threshold" type="number" step="0.01" min="0.1" max="1.0" />
        </div>
        <div class="form-row">
          <label>自动确认订单:</label>
          <input v-model="config.auto_confirm" type="checkbox" />
        </div>
        <div class="form-actions">
          <button @click="updateConfig" class="btn btn-secondary">
            💾 保存配置
          </button>
        </div>
      </div>
    </div>

    <!-- 实时信息 -->
    <div class="info-panel">
      <h4>📊 实时信息</h4>
      <div class="info-grid">
        <div class="info-item">
          <label>今日交易次数:</label>
          <span>{{ systemStatus.hotkey_trader?.daily_trade_count || 0 }}</span>
        </div>
        <div class="info-item">
          <label>待处理订单:</label>
          <span>{{ systemStatus.hotkey_trader?.pending_orders || 0 }}</span>
        </div>
        <div class="info-item">
          <label>最后交易时间:</label>
          <span>{{ formatTime(systemStatus.hotkey_trader?.last_trade_time) }}</span>
        </div>
        <div class="info-item">
          <label>系统运行时间:</label>
          <span>{{ formatUptime(systemStatus.trading_agent?.uptime) }}</span>
        </div>
      </div>
    </div>

    <!-- 执行历史 -->
    <div class="history-panel">
      <h4>📋 执行历史</h4>
      <div class="history-controls">
        <button @click="refreshHistory" class="btn btn-info">🔄 刷新</button>
        <button @click="clearHistory" class="btn btn-warning">🗑️ 清空</button>
      </div>
      <div class="history-list">
        <div v-for="record in executionHistory" :key="record.execution_id" class="history-item">
          <div class="history-header">
            <span class="action" :class="record.decision.action">{{ record.decision.action.toUpperCase() }}</span>
            <span class="symbol">{{ record.decision.symbol }}</span>
            <span class="time">{{ formatTime(record.timestamp) }}</span>
          </div>
          <div class="history-details">
            <span>价格: ¥{{ record.decision.price }}</span>
            <span>数量: {{ record.decision.quantity }}</span>
            <span>置信度: {{ (record.decision.confidence * 100).toFixed(1) }}%</span>
            <span class="status" :class="record.result.status">{{ record.result.status }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'AgentTradingPanel',
  setup() {
    // 响应式数据
    const systemStatus = ref({})
    const executionHistory = ref([])
    const message = ref('')
    const messageType = ref('info')
    
    // 手动交易表单
    const manualTrade = reactive({
      symbol: '',
      price: '',
      quantity: 100,
      action: 'buy'
    })
    
    // 自动交易表单
    const autoTrade = reactive({
      symbol: ''
    })
    
    // 配置表单
    const config = reactive({
      auto_trading_enabled: false,
      auto_confirm: false,
      max_daily_trades: 20,
      max_position_size: 0.1,
      min_confidence_threshold: 0.75,
      min_trade_interval: 60
    })
    
    // 计算属性
    const isSystemActive = computed(() => {
      return systemStatus.value.hotkey_trader?.active || false
    })
    
    const autoTradingEnabled = computed(() => {
      return systemStatus.value.hotkey_trader?.auto_trading_enabled || false
    })
    
    const canExecuteTrade = computed(() => {
      return isSystemActive.value && 
             manualTrade.symbol && 
             manualTrade.price && 
             manualTrade.quantity
    })
    
    const canAutoTrade = computed(() => {
      return isSystemActive.value && autoTrade.symbol
    })
    
    // API调用函数
    const apiCall = async (endpoint, method = 'GET', data = null) => {
      try {
        const options = {
          method,
          headers: {
            'Content-Type': 'application/json'
          }
        }
        
        if (data) {
          options.body = JSON.stringify(data)
        }
        
        const response = await fetch(`/api/agent-trading${endpoint}`, options)
        const result = await response.json()
        
        if (!response.ok) {
          throw new Error(result.detail || '请求失败')
        }
        
        return result
      } catch (error) {
        showMessage(`API调用失败: ${error.message}`, 'error')
        throw error
      }
    }
    
    // 消息显示
    const showMessage = (msg, type = 'info') => {
      message.value = msg
      messageType.value = type
      setTimeout(() => {
        message.value = ''
      }, 5000)
    }
    
    // 系统控制函数
    const startSystem = async () => {
      try {
        const result = await apiCall('/start', 'POST')
        showMessage('系统启动成功', 'success')
        await refreshStatus()
      } catch (error) {
        showMessage('系统启动失败', 'error')
      }
    }
    
    const stopSystem = async () => {
      try {
        const result = await apiCall('/stop', 'POST')
        showMessage('系统已停止', 'info')
        await refreshStatus()
      } catch (error) {
        showMessage('系统停止失败', 'error')
      }
    }
    
    const toggleAutoTrading = async () => {
      try {
        const newConfig = { ...config, auto_trading_enabled: !autoTradingEnabled.value }
        await apiCall('/config/trading', 'POST', newConfig)
        showMessage(`自动交易已${newConfig.auto_trading_enabled ? '启用' : '禁用'}`, 'success')
        await refreshStatus()
      } catch (error) {
        showMessage('切换自动交易状态失败', 'error')
      }
    }
    
    // 交易执行函数
    const executeManualTrade = async () => {
      try {
        const decision = {
          action: manualTrade.action,
          symbol: manualTrade.symbol,
          price: parseFloat(manualTrade.price),
          quantity: parseInt(manualTrade.quantity),
          confidence: 1.0,
          reason: '手动交易'
        }
        
        const result = await apiCall('/execute-decision', 'POST', decision)
        showMessage('交易指令已发送', 'success')
        await refreshHistory()
      } catch (error) {
        showMessage('交易执行失败', 'error')
      }
    }
    
    const executeAutoTrade = async () => {
      try {
        const result = await apiCall(`/auto-trade?symbol=${autoTrade.symbol}`, 'POST')
        showMessage('自动交易已启动', 'success')
        await refreshHistory()
      } catch (error) {
        showMessage('自动交易启动失败', 'error')
      }
    }
    
    const getAgentDecision = async () => {
      try {
        const result = await apiCall(`/agent-decision?symbol=${manualTrade.symbol}`, 'POST')
        const decision = result.decision
        
        if (decision && !decision.error) {
          manualTrade.action = decision.action
          if (decision.price) manualTrade.price = decision.price.toString()
          if (decision.quantity) manualTrade.quantity = decision.quantity
          
          showMessage(`AI建议: ${decision.action.toUpperCase()} (置信度: ${(decision.confidence * 100).toFixed(1)}%)`, 'info')
        } else {
          showMessage('AI决策失败', 'error')
        }
      } catch (error) {
        showMessage('获取AI建议失败', 'error')
      }
    }
    
    // 配置更新
    const updateConfig = async () => {
      try {
        await apiCall('/config/trading', 'POST', config)
        showMessage('配置已保存', 'success')
      } catch (error) {
        showMessage('配置保存失败', 'error')
      }
    }
    
    // 数据刷新函数
    const refreshStatus = async () => {
      try {
        const result = await apiCall('/status')
        systemStatus.value = result.data
      } catch (error) {
        console.error('刷新状态失败:', error)
      }
    }
    
    const refreshHistory = async () => {
      try {
        const result = await apiCall('/history')
        executionHistory.value = result.data
      } catch (error) {
        console.error('刷新历史失败:', error)
      }
    }
    
    const clearHistory = async () => {
      try {
        await apiCall('/history', 'DELETE')
        executionHistory.value = []
        showMessage('历史记录已清空', 'info')
      } catch (error) {
        showMessage('清空历史失败', 'error')
      }
    }
    
    // 工具函数
    const formatTime = (timestamp) => {
      if (!timestamp) return '-'
      return new Date(timestamp).toLocaleString()
    }
    
    const formatUptime = (seconds) => {
      if (!seconds) return '-'
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      return `${hours}h ${minutes}m`
    }
    
    // 定时刷新
    let refreshInterval
    
    onMounted(() => {
      refreshStatus()
      refreshHistory()
      
      // 每5秒刷新一次状态
      refreshInterval = setInterval(() => {
        refreshStatus()
      }, 5000)
    })
    
    onUnmounted(() => {
      if (refreshInterval) {
        clearInterval(refreshInterval)
      }
    })
    
    return {
      systemStatus,
      executionHistory,
      message,
      messageType,
      manualTrade,
      autoTrade,
      config,
      isSystemActive,
      autoTradingEnabled,
      canExecuteTrade,
      canAutoTrade,
      startSystem,
      stopSystem,
      toggleAutoTrading,
      executeManualTrade,
      executeAutoTrade,
      getAgentDecision,
      updateConfig,
      refreshHistory,
      clearHistory,
      formatTime,
      formatUptime
    }
  }
}
</script>

<style scoped>
.agent-trading-panel {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 状态卡片 */
.status-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.status-card h3 {
  margin: 0 0 15px 0;
  font-size: 1.5em;
}

.status-indicators {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255,255,255,0.1);
  border-radius: 20px;
  transition: all 0.3s ease;
}

.indicator.active {
  background: rgba(76, 175, 80, 0.3);
}

.indicator .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ff5722;
  transition: background 0.3s ease;
}

.indicator.active .dot {
  background: #4caf50;
}

/* 面板通用样式 */
.control-panel, .manual-trading, .auto-trading, .config-panel, .info-panel, .history-panel {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border: 1px solid #e0e0e0;
}

.control-panel h4, .manual-trading h4, .auto-trading h4, .config-panel h4, .info-panel h4, .history-panel h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 1.2em;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 8px;
}

/* 按钮样式 */
.control-buttons, .form-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-success {
  background: #4caf50;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #45a049;
  transform: translateY(-1px);
}

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #da190b;
  transform: translateY(-1px);
}

.btn-warning {
  background: #ff9800;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background: #e68900;
  transform: translateY(-1px);
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1976d2;
  transform: translateY(-1px);
}

.btn-info {
  background: #00bcd4;
  color: white;
}

.btn-info:hover:not(:disabled) {
  background: #00acc1;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #5a6268;
  transform: translateY(-1px);
}

/* 表单样式 */
.trading-form, .auto-trading-form, .config-form {
  display: grid;
  gap: 15px;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-row label {
  min-width: 120px;
  font-weight: 500;
  color: #555;
}

.form-row input, .form-row select {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.form-row input:focus, .form-row select:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.form-row input[type="checkbox"] {
  flex: none;
  width: 18px;
  height: 18px;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #2196f3;
}

.info-item label {
  font-weight: 500;
  color: #666;
}

.info-item span {
  font-weight: 600;
  color: #333;
}

/* 历史记录 */
.history-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
}

.history-item {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s ease;
}

.history-item:hover {
  background: #f8f9fa;
}

.history-item:last-child {
  border-bottom: none;
}

.history-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.history-header .action {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.history-header .action.buy {
  background: #e8f5e8;
  color: #2e7d32;
}

.history-header .action.sell {
  background: #ffebee;
  color: #c62828;
}

.history-header .symbol {
  font-weight: 600;
  color: #333;
}

.history-header .time {
  margin-left: auto;
  font-size: 12px;
  color: #666;
}

.history-details {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #666;
  flex-wrap: wrap;
}

.history-details .status {
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 500;
}

.history-details .status.success {
  background: #e8f5e8;
  color: #2e7d32;
}

.history-details .status.error {
  background: #ffebee;
  color: #c62828;
}

.history-details .status.pending {
  background: #fff3e0;
  color: #ef6c00;
}

/* 消息提示 */
.message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 6px;
  color: white;
  font-weight: 500;
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

.message.success {
  background: #4caf50;
}

.message.error {
  background: #f44336;
}

.message.info {
  background: #2196f3;
}

.message.warning {
  background: #ff9800;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .agent-trading-panel {
    padding: 10px;
  }

  .status-indicators {
    flex-direction: column;
  }

  .control-buttons, .form-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .form-row {
    flex-direction: column;
    align-items: stretch;
  }

  .form-row label {
    min-width: auto;
    margin-bottom: 5px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .history-header {
    flex-wrap: wrap;
  }

  .history-header .time {
    margin-left: 0;
    order: -1;
    width: 100%;
  }
}
</style>
