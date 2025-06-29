<template>
  <view class="stock-chart-container">
    <view class="chart-header">
      <text class="chart-title">{{ title || '股票走势图' }}</text>
      
      <!-- 数据源选择器 -->
      <DataSourceSelector :defaultSource="dataSource" @change="onDataSourceChange" />
    </view>
    
    <!-- 图表周期选择器 -->
    <view class="period-selector">
      <view 
        v-for="(period, index) in periods" 
        :key="index"
        :class="['period-item', { active: currentPeriod === period.value }]"
        @tap="changePeriod(period.value)"
      >
        {{ period.label }}
      </view>
    </view>
    
    <!-- 图表容器 -->
    <view class="chart-canvas-container">
      <!-- 这里将来放置实际图表组件 -->
      <view v-if="loading" class="loading-indicator">
        <text>加载中...</text>
      </view>
      <view v-else-if="error" class="error-message">
        <text>{{ error }}</text>
        <button @tap="fetchData" class="retry-button">重试</button>
      </view>
      <view v-else class="canvas-placeholder">
        <!-- 实际项目中,这里应该引入图表组件,如 echarts 或其他 -->
        <text>K线图将显示在这里</text>
      </view>
    </view>
    
    <!-- 数据对比按钮 -->
    <view v-if="showCompare" class="compare-button" @tap="compareDataSources">
      对比数据源
    </view>
  </view>
</template>

<script>
import marketDataService from '../../股票5/components/services/marketDataService.js';
import DataSourceSelector from './DataSourceSelector.vue';

export default {
  name: 'StockChart',
  components: {
    DataSourceSelector
  },
  props: {
    code: {
      type: String,
      required: true
    },
    title: {
      type: String,
      default: ''
    },
    showCompare: {
      type: Boolean,
      default: false
    },
    defaultDataSource: {
      type: String,
      default: 'auto'
    }
  },
  data() {
    return {
      loading: false,
      error: null,
      chartData: [],
      currentPeriod: 'daily',
      dataSource: this.defaultDataSource,
      periods: [
        { label: '日K', value: 'daily' },
        { label: '周K', value: 'weekly' },
        { label: '月K', value: 'monthly' }
      ]
    };
  },
  created() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      if (!this.code) return;
      
      this.loading = true;
      this.error = null;
      
      try {
        const params = {
          freq: this.currentPeriod,
          merge_sources: this.dataSource === 'merge',
          data_source: this.dataSource === 'merge' ? 'auto' : this.dataSource
        };
        
        const response = await marketDataService.getKData(this.code, params);
        
        if (response.success) {
          this.chartData = response.data;
          this.renderChart();
        } else {
          this.error = '获取数据失败';
        }
      } catch (error) {
        console.error('获取K线数据出错:', error);
        this.error = '获取数据出错: ' + (error.message || '未知错误');
      } finally {
        this.loading = false;
      }
    },
    onDataSourceChange(source) {
      this.dataSource = source;
      this.fetchData();
    },
    changePeriod(period) {
      this.currentPeriod = period;
      this.fetchData();
    },
    async compareDataSources() {
      try {
        this.loading = true;
        
        const response = await marketDataService.compareDataSources(this.code, {
          freq: this.currentPeriod
        });
        
        if (response.success) {
          // 这里可以显示数据源对比的结果
          // 在实际应用中,可能会打开一个新页面或对话框展示对比结果
          uni.showModal({
            title: '数据源对比',
            content: `通达信: ${response.data.tdx.count}条数据\n同花顺: ${response.data.ths.count}条数据`,
            showCancel: false
          });
        } else {
          uni.showToast({
            title: '对比数据失败',
            icon: 'none'
          });
        }
      } catch (error) {
        console.error('对比数据源出错:', error);
        uni.showToast({
          title: '对比数据源出错',
          icon: 'none'
        });
      } finally {
        this.loading = false;
      }
    },
    renderChart() {
      // 这里实现图表渲染逻辑
      // 在实际应用中,这里应该使用图表库(如ECharts)来渲染K线图
      console.log('渲染图表', this.chartData.length + '条数据');
      
      // 示例:简单地显示数据条数和日期范围
      if (this.chartData.length > 0) {
        const firstDate = this.chartData[0].date;
        const lastDate = this.chartData[this.chartData.length - 1].date;
        console.log(`数据范围: ${firstDate} 至 ${lastDate}`);
      }
    }
  }
}
</script>

<style>
.stock-chart-container {
  width: 100%;
  border-radius: 8px;
  background-color: #fff;
  padding: 12px;
  margin-bottom: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chart-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.data-source-selector {
  background-color: #f5f5f5;
  border-radius: 4px;
  padding: 4px 8px;
}

.picker {
  display: flex;
  align-items: center;
}

.source-label {
  font-size: 12px;
  color: #666;
  margin-right: 4px;
}

.source-value {
  font-size: 12px;
  color: #333;
  margin-right: 4px;
}

.source-arrow {
  font-size: 10px;
  color: #999;
}

.period-selector {
  display: flex;
  background-color: #f5f5f5;
  border-radius: 4px;
  margin-bottom: 12px;
  overflow: hidden;
}

.period-item {
  flex: 1;
  text-align: center;
  padding: 6px 0;
  font-size: 12px;
  color: #666;
  transition: background-color 0.3s;
}

.period-item.active {
  background-color: #0066cc;
  color: #fff;
}

.chart-canvas-container {
  width: 100%;
  height: 250px;
  background-color: #f9f9f9;
  border-radius: 4px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading-indicator {
  color: #999;
  font-size: 14px;
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  text-align: center;
}

.retry-button {
  margin-top: 8px;
  background-color: #0066cc;
  color: #fff;
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 4px;
}

.canvas-placeholder {
  color: #999;
  font-size: 14px;
}

.compare-button {
  margin-top: 12px;
  background-color: #f5f5f5;
  color: #333;
  text-align: center;
  padding: 8px;
  border-radius: 4px;
  font-size: 14px;
}
</style> 
