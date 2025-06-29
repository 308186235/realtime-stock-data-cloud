<template>
  <div class="backtest-container">
    <div class="backtest-form">
      <h2>回测参数配置</h2>
      
      <div class="form-group">
        <label>股票代码</label>
        <div class="symbol-select">
          <input 
            v-model="symbolInput" 
            @keyup.enter="addSymbol"
            placeholder="输入股票代码后按回车添加"
          >
          <button @click="addSymbol" class="add-btn">添加</button>
        </div>
        <div class="selected-symbols">
          <div v-for="(symbol, index) in symbols" :key="index" class="symbol-tag">
            {{ symbol }}
            <span @click="removeSymbol(index)" class="remove-symbol">&times;</span>
          </div>
        </div>
      </div>
      
      <div class="form-group date-range">
        <div class="date-input">
          <label>起始日期</label>
          <input type="date" v-model="startDate">
        </div>
        <div class="date-input">
          <label>结束日期</label>
          <input type="date" v-model="endDate">
        </div>
      </div>
      
      <div class="form-group">
        <label>初始资金</label>
        <input type="number" v-model="initialCapital" min="1000" step="1000">
      </div>
      
      <div class="form-group">
        <label>手续费率</label>
        <input type="number" v-model="commission" min="0" max="0.01" step="0.0001">
      </div>
      
      <div class="strategies-section">
        <h3>策略配置</h3>
        <div v-for="(strategy, index) in strategies" :key="index" class="strategy-config">
          <div class="strategy-header">
            <select v-model="strategy.type">
              <option value="inverted_three_red">倒三红形</option>
              <option value="red_three_soldiers">红三兵</option>
            </select>
            <button @click="removeStrategy(index)" class="remove-btn">删除</button>
          </div>
          
          <div class="strategy-params" v-if="strategy.type === 'inverted_three_red'">
            <div class="param-item">
              <label>实体减小阈值</label>
              <input type="number" v-model="strategy.params.body_decrease_threshold" min="0.1" max="0.99" step="0.01">
            </div>
            <div class="param-item">
              <label>上影线增长阈值</label>
              <input type="number" v-model="strategy.params.upper_shadow_increase_threshold" min="1" max="2" step="0.1">
            </div>
            <div class="param-item">
              <label>成交量阈值</label>
              <input type="number" v-model="strategy.params.volume_threshold" min="0.5" max="3" step="0.1">
            </div>
            <!-- 高级参数切换 -->
            <div class="param-toggle">
              <button @click="toggleAdvancedParams(index)" class="toggle-btn">
                {{ strategy.showAdvanced ? '隐藏高级参数' : '显示高级参数' }}
              </button>
            </div>
            
            <!-- 高级参数区域 -->
            <div v-if="strategy.showAdvanced" class="advanced-params">
              <div class="param-item">
                <label>高位阈值</label>
                <input type="number" v-model="strategy.params.high_position_threshold" min="0.6" max="0.9" step="0.05">
              </div>
              <div class="param-item">
                <label>低位阈值</label>
                <input type="number" v-model="strategy.params.low_position_threshold" min="0.1" max="0.4" step="0.05">
              </div>
              <div class="param-item">
                <label>高位减仓比例</label>
                <input type="number" v-model="strategy.params.high_position_reduction" min="0.1" max="1.0" step="0.1">
              </div>
              <div class="param-item">
                <label>中位减仓比例</label>
                <input type="number" v-model="strategy.params.mid_position_reduction" min="0.1" max="0.5" step="0.1">
              </div>
              <div class="param-item">
                <label>低位试仓仓位</label>
                <input type="number" v-model="strategy.params.low_position_position" min="0.1" max="0.5" step="0.1">
              </div>
            </div>
          </div>
          
          <div class="strategy-params" v-if="strategy.type === 'red_three_soldiers'">
            <div class="param-item">
              <label>实体相似度阈值</label>
              <input type="number" v-model="strategy.params.body_size_similarity" min="0.5" max="1.0" step="0.05">
            </div>
            <div class="param-item">
              <label>上影线最大比例</label>
              <input type="number" v-model="strategy.params.max_upper_shadow_ratio" min="0.1" max="0.5" step="0.05">
            </div>
            <div class="param-item">
              <label>最小总涨幅</label>
              <input type="number" v-model="strategy.params.min_total_increase" min="0.01" max="0.1" step="0.01">
            </div>
            <!-- 高级参数切换 -->
            <div class="param-toggle">
              <button @click="toggleAdvancedParams(index)" class="toggle-btn">
                {{ strategy.showAdvanced ? '隐藏高级参数' : '显示高级参数' }}
              </button>
            </div>
            
            <!-- 高级参数区域 -->
            <div v-if="strategy.showAdvanced" class="advanced-params">
              <div class="param-item">
                <label>高位阈值</label>
                <input type="number" v-model="strategy.params.high_position_threshold" min="0.6" max="0.9" step="0.05">
              </div>
              <div class="param-item">
                <label>低位阈值</label>
                <input type="number" v-model="strategy.params.low_position_threshold" min="0.1" max="0.4" step="0.05">
              </div>
              <div class="param-item">
                <label>高位放量阈值</label>
                <input type="number" v-model="strategy.params.high_volume_warning_threshold" min="1.5" max="3.0" step="0.1">
              </div>
              <div class="param-item">
                <label>高位试探仓位</label>
                <input type="number" v-model="strategy.params.high_position_position" min="0.1" max="0.5" step="0.05">
              </div>
              <div class="param-item">
                <label>中位加仓仓位</label>
                <input type="number" v-model="strategy.params.mid_position_position" min="0.2" max="0.7" step="0.05">
              </div>
              <div class="param-item">
                <label>低位买入仓位</label>
                <input type="number" v-model="strategy.params.low_position_position" min="0.3" max="1.0" step="0.05">
              </div>
            </div>
          </div>
        </div>
        
        <button @click="addStrategy" class="add-strategy-btn">添加策略</button>
      </div>
      
      <button @click="runBacktest" class="run-btn" :disabled="isRunning || symbols.length === 0">
        {{ isRunning ? '回测中...' : '运行回测' }}
      </button>
    </div>
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <div v-if="isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>正在执行回测,请稍候...</p>
    </div>

    <BacktestResults v-if="backtestResults" :results="backtestResults" @save="saveBacktestResults" />
  </div>
</template>

<script>
import { backtestService } from '../../services/backtest-service.js';
import BacktestResults from './BacktestResults.vue';

export default {
  components: {
    BacktestResults
  },
  data() {
    // 获取默认日期(过去一年到今天)
    const today = new Date();
    const lastYear = new Date();
    lastYear.setFullYear(lastYear.getFullYear() - 1);
    
    return {
      symbolInput: '',
      symbols: [],
      startDate: this.formatDate(lastYear),
      endDate: this.formatDate(today),
      initialCapital: 100000,
      commission: 0.0003,
      strategies: [this.createDefaultStrategy()],
      isRunning: false,
      isLoading: false,
      backtestResults: null,
      error: null,
      backtestId: null
    };
  },
  methods: {
    formatDate(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    
    createDefaultStrategy() {
      return {
        type: 'inverted_three_red',
        params: {
          body_decrease_threshold: 0.67,
          upper_shadow_increase_threshold: 1.0,
          volume_threshold: 1.5,
          high_position_threshold: 0.8,
          low_position_threshold: 0.2,
          high_position_reduction: 0.7,
          mid_position_reduction: 0.3,
          low_position_position: 0.2
        },
        showAdvanced: false
      };
    },
    
    createRedThreeSoldiersStrategy() {
      return {
        type: 'red_three_soldiers',
        params: {
          body_size_similarity: 0.8,
          max_upper_shadow_ratio: 0.3,
          min_total_increase: 0.04,
          volume_increase_threshold: 0.1,
          high_position_threshold: 0.8,
          low_position_threshold: 0.2,
          high_volume_warning_threshold: 2.0,
          high_position_position: 0.2,
          mid_position_position: 0.5,
          low_position_position: 0.7
        },
        showAdvanced: false
      };
    },
    
    addSymbol() {
      if (this.symbolInput && !this.symbols.includes(this.symbolInput)) {
        this.symbols.push(this.symbolInput.toUpperCase());
        this.symbolInput = '';
      }
    },
    
    removeSymbol(index) {
      this.symbols.splice(index, 1);
    },
    
    addStrategy() {
      const strategyTypes = document.querySelectorAll('.strategy-config select');
      // 如果现有策略都是倒三红形,则添加红三兵策略,否则添加倒三红形策略
      const allInverted = Array.from(strategyTypes).every(select => select.value === 'inverted_three_red');
      
      if (allInverted) {
        this.strategies.push(this.createRedThreeSoldiersStrategy());
      } else {
        this.strategies.push(this.createDefaultStrategy());
      }
    },
    
    removeStrategy(index) {
      if (this.strategies.length > 1) {
        this.strategies.splice(index, 1);
      }
    },
    
    toggleAdvancedParams(index) {
      this.strategies[index].showAdvanced = !this.strategies[index].showAdvanced;
    },
    
    async runBacktest() {
      if (this.symbols.length === 0) {
        this.error = '请添加至少一个股票代码';
        return;
      }
      
      this.isRunning = true;
      this.isLoading = true;
      this.error = null;
      this.backtestResults = null;
      
      try {
        // 准备请求参数
        const payload = {
          strategies: this.strategies.map(s => ({
            type: s.type,
            params: s.params
          })),
          symbols: this.symbols,
          start_date: this.startDate,
          end_date: this.endDate,
          initial_capital: parseFloat(this.initialCapital),
          commission: parseFloat(this.commission)
        };
        
        // 执行回测
        const results = await backtestService.runBacktest(payload);
        this.backtestResults = results;
        this.backtestId = results.backtest_id;
      } catch (error) {
        console.error('回测失败', error);
        this.error = `回测失败: ${error.message}`;
      } finally {
        this.isRunning = false;
        this.isLoading = false;
      }
    },
    
    async saveBacktestResults(name) {
      if (!this.backtestId) return;
      
      try {
        await backtestService.saveBacktest(this.backtestId, name);
        this.$emit('saved', { id: this.backtestId, name });
      } catch (error) {
        console.error('保存回测结果失败', error);
        this.error = `保存失败: ${error.message}`;
      }
    }
  }
};
</script>

<style scoped>
.backtest-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.backtest-form {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-top: 0;
  color: #333;
  font-size: 1.5rem;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #444;
}

input[type="number"],
input[type="text"],
input[type="date"],
select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.date-range {
  display: flex;
  gap: 15px;
}

.date-input {
  flex: 1;
}

.symbol-select {
  display: flex;
  gap: 10px;
}

.symbol-select input {
  flex: 1;
}

.add-btn {
  background: #2196F3;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.selected-symbols {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.symbol-tag {
  background: #e1f5fe;
  color: #0277bd;
  padding: 5px 10px;
  border-radius: 16px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
}

.remove-symbol {
  margin-left: 5px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1.2rem;
}

.strategies-section {
  margin-top: 20px;
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.strategy-config {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 15px;
}

.strategy-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.strategy-params {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.param-toggle {
  grid-column: 1 / -1;
  margin-top: 10px;
}

.toggle-btn {
  background: transparent;
  color: #2196F3;
  border: 1px solid #2196F3;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.advanced-params {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed #ddd;
}

.add-strategy-btn, .run-btn {
  background: #4caf50;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  margin-top: 10px;
  font-size: 1rem;
}

.add-strategy-btn:hover, .run-btn:hover {
  background: #43a047;
}

.add-strategy-btn {
  background: #2196F3;
}

.add-strategy-btn:hover {
  background: #1976D2;
}

.remove-btn {
  background: #f44336;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.remove-btn:hover {
  background: #e53935;
}

button:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 10px 15px;
  border-radius: 4px;
  border-left: 4px solid #c62828;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #4caf50;
  animation: spin 1s ease infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style> 
