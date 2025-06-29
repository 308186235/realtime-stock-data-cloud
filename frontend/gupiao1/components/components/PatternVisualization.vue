<template>
  <view class="pattern-visualization">
    <view class="visualization-header">
      <text class="title">形态可视化</text>
      <text class="pattern-name">{{ currentPattern ? currentPattern.name : '未选择形态' }}</text>
    </view>
    
    <!-- K线图表区域 -->
    <view class="chart-container">
      <!-- 这里将使用Canvas绘制K线图 -->
      <canvas canvas-id="patternChart" class="pattern-chart" :canvas-will-read-frequently="true" @touchstart="touchStart" @touchmove="touchMove" @touchend="touchEnd"></canvas>
      
      <!-- 形态标记 -->
      <view v-if="currentPattern && currentPattern.detected" class="pattern-markers">
        <view v-for="(marker, index) in patternMarkers" :key="index" 
              class="pattern-marker" 
              :class="marker.type"
              :style="{ left: marker.x + 'px', top: marker.y + 'px' }">
          <text class="marker-label">{{ marker.label }}</text>
        </view>
      </view>
    </view>
    
    <!-- 形态说明 -->
    <view v-if="currentPattern" class="pattern-description">
      <view class="description-header">
        <text class="direction-label" :class="getDirectionClass(currentPattern.direction)">
          {{ getDirectionText(currentPattern.direction) }}
        </text>
        <view class="confidence-indicator">
          <text class="confidence-label">可信度:</text>
          <view class="confidence-bar">
            <view class="confidence-fill" :style="{ width: `${currentPattern.confidence * 100}%` }"></view>
          </view>
          <text class="confidence-value">{{ Math.round(currentPattern.confidence * 100) }}%</text>
        </view>
      </view>
      
      <text class="description-text">{{ currentPattern.description }}</text>
      
      <view class="pattern-features">
        <text class="features-title">形态特征:</text>
        <view class="feature-list">
          <view v-for="(feature, index) in patternFeatures" :key="index" class="feature-item">
            <text class="feature-bullet">•</text>
            <text class="feature-text">{{ feature }}</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 形态选择器 -->
    <scroll-view scroll-x="true" class="pattern-selector">
      <view 
        v-for="(pattern, index) in detectedPatterns" 
        :key="index" 
        class="pattern-item" 
        :class="{ active: currentPatternIndex === index }"
        @click="selectPattern(index)">
        <text class="pattern-item-name">{{ pattern.name }}</text>
        <text class="pattern-item-direction" :class="getDirectionClass(pattern.direction)">
          {{ getDirectionText(pattern.direction) }}
        </text>
      </view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  props: {
    detectedPatterns: {
      type: Array,
      default: () => []
    },
    stockData: {
      type: Object,
      default: () => ({
        prices: [],
        highs: [],
        lows: [],
        opens: [],
        closes: [],
        volumes: [],
        dates: []
      })
    }
  },
  
  data() {
    return {
      currentPatternIndex: 0,
      chartContext: null,
      chartWidth: 0,
      chartHeight: 0,
      patternMarkers: [],
      patternFeatures: [],
      // 图表配置
      chartConfig: {
        padding: { top: 20, right: 10, bottom: 20, left: 40 },
        candleWidth: 8,
        candleGap: 2,
        colors: {
          up: '#f5222d',
          down: '#52c41a',
          grid: '#f0f0f0',
          axis: '#d9d9d9',
          text: '#666666'
        }
      }
    };
  },
  
  computed: {
    currentPattern() {
      if (this.detectedPatterns.length === 0) return null;
      return this.detectedPatterns[this.currentPatternIndex];
    }
  },
  
  watch: {
    detectedPatterns: {
      handler(newPatterns) {
        if (newPatterns.length > 0) {
          this.currentPatternIndex = 0;
          this.renderChart();
          this.generatePatternFeatures();
        }
      },
      immediate: true
    },
    
    currentPatternIndex() {
      this.renderChart();
      this.generatePatternFeatures();
    }
  },
  
  mounted() {
    this.initChart();
  },
  
  methods: {
    initChart() {
      // 获取画布上下文
      const query = uni.createSelectorQuery().in(this);
      query.select('.pattern-chart').fields({ node: true, size: true }).exec(res => {
        if (res[0]) {
          this.chartWidth = res[0].width;
          this.chartHeight = res[0].height;
          
          // 创建绘图上下文
          this.chartContext = uni.createCanvasContext('patternChart', this);
          
          // 渲染图表
          this.renderChart();
        }
      });
    },
    
    renderChart() {
      if (!this.chartContext || !this.currentPattern) return;
      
      const ctx = this.chartContext;
      const { padding, candleWidth, candleGap, colors } = this.chartConfig;
      const { prices, highs, lows, opens, closes } = this.stockData;
      
      // 清空画布
      ctx.clearRect(0, 0, this.chartWidth, this.chartHeight);
      
      // 计算绘图区域
      const drawWidth = this.chartWidth - padding.left - padding.right;
      const drawHeight = this.chartHeight - padding.top - padding.bottom;
      
      // 计算数据范围
      const dataLength = Math.min(30, prices.length); // 最多显示30个数据点
      const startIndex = Math.max(0, prices.length - dataLength);
      const endIndex = prices.length;
      
      const visibleData = {
        highs: highs.slice(startIndex, endIndex),
        lows: lows.slice(startIndex, endIndex),
        opens: opens.slice(startIndex, endIndex),
        closes: closes.slice(startIndex, endIndex)
      };
      
      // 计算价格范围
      const maxPrice = Math.max(...visibleData.highs);
      const minPrice = Math.min(...visibleData.lows);
      const priceRange = maxPrice - minPrice;
      
      // 绘制网格
      this.drawGrid(ctx, padding, drawWidth, drawHeight);
      
      // 绘制K线
      this.patternMarkers = []; // 重置形态标记
      
      for (let i = 0; i < visibleData.highs.length; i++) {
        const x = padding.left + i * (candleWidth + candleGap);
        const open = visibleData.opens[i];
        const close = visibleData.closes[i];
        const high = visibleData.highs[i];
        const low = visibleData.lows[i];
        
        // 计算Y坐标
        const highY = padding.top + drawHeight * (1 - (high - minPrice) / priceRange);
        const lowY = padding.top + drawHeight * (1 - (low - minPrice) / priceRange);
        const openY = padding.top + drawHeight * (1 - (open - minPrice) / priceRange);
        const closeY = padding.top + drawHeight * (1 - (close - minPrice) / priceRange);
        
        // 判断是上涨还是下跌
        const isUp = close >= open;
        ctx.setStrokeStyle(isUp ? colors.up : colors.down);
        ctx.setFillStyle(isUp ? colors.up : colors.down);
        
        // 绘制影线
        ctx.beginPath();
        ctx.moveTo(x + candleWidth / 2, highY);
        ctx.lineTo(x + candleWidth / 2, lowY);
        ctx.stroke();
        
        // 绘制实体
        const candleHeight = Math.abs(closeY - openY);
        const y = isUp ? closeY : openY;
        
        if (candleHeight < 1) {
          // 如果实体太小,绘制一条线
          ctx.beginPath();
          ctx.moveTo(x, openY);
          ctx.lineTo(x + candleWidth, openY);
          ctx.stroke();
        } else {
          // 绘制矩形实体
          ctx.fillRect(x, y, candleWidth, candleHeight);
        }
        
        // 为当前形态添加标记
        if (this.currentPattern && this.shouldMarkCandle(i, startIndex)) {
          this.patternMarkers.push({
            x: x,
            y: highY - 15,
            type: this.getMarkerType(i, startIndex),
            label: this.getMarkerLabel(i, startIndex)
          });
        }
      }
      
      // 绘制坐标轴
      this.drawAxis(ctx, padding, drawWidth, drawHeight, minPrice, maxPrice);
      
      // 应用绘制
      ctx.draw();
    },
    
    drawGrid(ctx, padding, width, height) {
      const { colors } = this.chartConfig;
      ctx.setStrokeStyle(colors.grid);
      ctx.setLineWidth(0.5);
      
      // 绘制水平网格线
      const horizontalLines = 5;
      for (let i = 0; i <= horizontalLines; i++) {
        const y = padding.top + (height / horizontalLines) * i;
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(padding.left + width, y);
        ctx.stroke();
      }
      
      // 绘制垂直网格线
      const verticalLines = 6;
      for (let i = 0; i <= verticalLines; i++) {
        const x = padding.left + (width / verticalLines) * i;
        ctx.beginPath();
        ctx.moveTo(x, padding.top);
        ctx.lineTo(x, padding.top + height);
        ctx.stroke();
      }
    },
    
    drawAxis(ctx, padding, width, height, minPrice, maxPrice) {
      const { colors } = this.chartConfig;
      ctx.setStrokeStyle(colors.axis);
      ctx.setFillStyle(colors.text);
      ctx.setFontSize(10);
      
      // 绘制Y轴价格标签
      const priceStep = (maxPrice - minPrice) / 5;
      for (let i = 0; i <= 5; i++) {
        const price = minPrice + priceStep * i;
        const y = padding.top + height * (1 - i / 5);
        
        ctx.fillText(price.toFixed(2), 5, y + 3);
      }
    },
    
    shouldMarkCandle(index, startIndex) {
      // 根据形态类型确定是否标记该K线
      // 这里简化处理,实际应用中需要根据形态特点确定
      const realIndex = index + startIndex;
      const totalCandles = this.stockData.prices.length;
      
      if (this.currentPattern.name.includes('MACD')) {
        // 对于MACD形态,标记最近的几根K线
        return realIndex >= totalCandles - 3;
      } else if (this.currentPattern.name.includes('双底')) {
        // 对于双底形态,标记底部位置
        return index === 5 || index === 15;
      } else if (this.currentPattern.name.includes('头肩')) {
        // 对于头肩形态,标记头和肩的位置
        return index === 5 || index === 10 || index === 15;
      }
      
      // 默认标记最近的K线
      return realIndex >= totalCandles - 2;
    },
    
    getMarkerType(index, startIndex) {
      // 根据形态和位置确定标记类型
      const realIndex = index + startIndex;
      const totalCandles = this.stockData.prices.length;
      
      if (realIndex === totalCandles - 1) {
        return 'marker-primary';
      }
      return 'marker-secondary';
    },
    
    getMarkerLabel(index, startIndex) {
      // 根据形态和位置确定标记标签
      const realIndex = index + startIndex;
      const totalCandles = this.stockData.prices.length;
      
      if (this.currentPattern.name.includes('双底')) {
        if (index === 5) return '底1';
        if (index === 15) return '底2';
      } else if (this.currentPattern.name.includes('头肩')) {
        if (index === 5) return '左肩';
        if (index === 10) return '头部';
        if (index === 15) return '右肩';
      } else if (this.currentPattern.name.includes('MACD')) {
        if (realIndex === totalCandles - 2) return '金叉';
      }
      
      return '';
    },
    
    generatePatternFeatures() {
      // 根据当前选中的形态生成特征描述
      if (!this.currentPattern) {
        this.patternFeatures = [];
        return;
      }
      
      const features = [];
      
      // 根据形态类型添加特征描述
      if (this.currentPattern.name.includes('MACD金叉')) {
        features.push('DIFF线从下向上穿越DEA线');
        features.push('MACD柱状图由负转正');
        features.push('短期均线上穿长期均线');
      } else if (this.currentPattern.name.includes('MACD死叉')) {
        features.push('DIFF线从上向下穿越DEA线');
        features.push('MACD柱状图由正转负');
        features.push('短期均线下穿长期均线');
      } else if (this.currentPattern.name.includes('双底')) {
        features.push('形成两个相近的低点');
        features.push('第二个低点成交量通常小于第一个低点');
        features.push('颈线突破后常伴随成交量放大');
      } else if (this.currentPattern.name.includes('双顶')) {
        features.push('形成两个相近的高点');
        features.push('第二个高点成交量通常小于第一个高点');
        features.push('颈线跌破后常伴随成交量放大');
      }
      
      // 添加通用特征
      if (this.currentPattern.direction === 'bullish') {
        features.push('此形态通常预示着价格可能上涨');
      } else if (this.currentPattern.direction === 'bearish') {
        features.push('此形态通常预示着价格可能下跌');
      }
      
      this.patternFeatures = features;
    },
    
    selectPattern(index) {
      this.currentPatternIndex = index;
    },
    
    getDirectionClass(direction) {
      if (direction === 'bullish') return 'direction-bullish';
      if (direction === 'bearish') return 'direction-bearish';
      return 'direction-neutral';
    },
    
    getDirectionText(direction) {
      if (direction === 'bullish') return '看涨';
      if (direction === 'bearish') return '看跌';
      return '中性';
    },
    
    // 触摸事件处理
    touchStart(e) {
      // 处理触摸开始
    },
    
    touchMove(e) {
      // 处理触摸移动
    },
    
    touchEnd(e) {
      // 处理触摸结束
    }
  }
};
</script>

<style>
.pattern-visualization {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
}

.visualization-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.title {
  font-size: 28rpx;
  font-weight: bold;
}

.pattern-name {
  font-size: 26rpx;
  color: #1989fa;
  font-weight: bold;
}

.chart-container {
  position: relative;
  width: 100%;
  height: 400rpx;
  margin-bottom: 20rpx;
}

.pattern-chart {
  width: 100%;
  height: 100%;
}

.pattern-markers {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.pattern-marker {
  position: absolute;
  width: 16rpx;
  height: 16rpx;
  border-radius: 8rpx;
  transform: translate(-8rpx, -8rpx);
}

.marker-primary {
  background-color: #1989fa;
}

.marker-secondary {
  background-color: #ff9900;
}

.marker-label {
  position: absolute;
  top: -30rpx;
  left: 50%;
  transform: translateX(-50%);
  font-size: 20rpx;
  color: #666;
  background-color: rgba(255, 255, 255, 0.8);
  padding: 2rpx 6rpx;
  border-radius: 4rpx;
}

.pattern-description {
  padding: 20rpx;
  background-color: #f9f9f9;
  border-radius: 8rpx;
  margin-bottom: 20rpx;
}

.description-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15rpx;
}

.direction-label {
  font-size: 24rpx;
  padding: 4rpx 12rpx;
  border-radius: 4rpx;
}

.direction-bullish {
  background-color: rgba(7, 193, 96, 0.1);
  color: #07c160;
}

.direction-bearish {
  background-color: rgba(238, 10, 36, 0.1);
  color: #ee0a24;
}

.direction-neutral {
  background-color: rgba(25, 137, 250, 0.1);
  color: #1989fa;
}

.confidence-indicator {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.confidence-label {
  font-size: 22rpx;
  color: #666;
  margin-right: 10rpx;
}

.confidence-bar {
  width: 100rpx;
  height: 10rpx;
  background-color: #eee;
  border-radius: 5rpx;
  overflow: hidden;
  margin-right: 10rpx;
}

.confidence-fill {
  height: 100%;
  background-color: #1989fa;
  border-radius: 5rpx;
}

.confidence-value {
  font-size: 22rpx;
  color: #666;
}

.description-text {
  font-size: 26rpx;
  color: #333;
  line-height: 1.5;
  margin-bottom: 15rpx;
}

.pattern-features {
  margin-top: 15rpx;
}

.features-title {
  font-size: 24rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
}

.feature-list {
  padding-left: 10rpx;
}

.feature-item {
  display: flex;
  flex-direction: row;
  margin-bottom: 8rpx;
}

.feature-bullet {
  font-size: 24rpx;
  color: #1989fa;
  margin-right: 10rpx;
}

.feature-text {
  font-size: 24rpx;
  color: #666;
  line-height: 1.4;
}

.pattern-selector {
  white-space: nowrap;
  margin-top: 20rpx;
}

.pattern-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  padding: 15rpx 20rpx;
  margin-right: 15rpx;
  background-color: #f5f5f5;
  border-radius: 8rpx;
}

.pattern-item.active {
  background-color: #e6f7ff;
  border: 1rpx solid #91d5ff;
}

.pattern-item-name {
  font-size: 24rpx;
  color: #333;
  margin-bottom: 5rpx;
}

.pattern-item-direction {
  font-size: 20rpx;
  padding: 2rpx 8rpx;
  border-radius: 4rpx;
}
</style> 
