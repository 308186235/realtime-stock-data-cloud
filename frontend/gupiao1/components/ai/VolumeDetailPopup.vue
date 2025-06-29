<template>
  <view class="volume-detail-modal">
    <view class="modal-header">
      <text class="modal-title">{{ stock ? stock.name : '' }}({{ stock ? stock.symbol : '' }}) 成交量分析</text>
      <text class="modal-close" @click="closePopup">×</text>
    </view>
    
    <view class="modal-content" v-if="stock">
      <!-- 成交量模式信息 -->
      <view class="volume-pattern-info" v-if="stock.volumeAnalysis && stock.volumeAnalysis.pattern">
        <text class="pattern-title">成交量模式: </text>
        <text class="pattern-value" :class="getPatternClass(stock)">
          {{ stock.volumeAnalysis.pattern.name }}
        </text>
        <text class="pattern-desc">{{ stock.volumeAnalysis.pattern.description }}</text>
      </view>
      
      <!-- 主要指标 -->
      <view class="volume-metrics">
        <view class="metric-item">
          <text class="metric-label">量比</text>
          <text class="metric-value" :class="getVolumeRatioClass(stock)">
            {{ stock.volumeAnalysis ? stock.volumeAnalysis.volumeRatio.toFixed(2) : '1.00' }}
          </text>
        </view>
        <view class="metric-item">
          <text class="metric-label">主力资金</text>
          <text class="metric-value" :class="getMainInflow(stock) >= 0 ? 'positive' : 'negative'">
            {{ getMainInflow(stock) >= 0 ? '+' : '' }}{{ getMainInflow(stock) }}万
          </text>
        </view>
        <view class="metric-item">
          <text class="metric-label">大单占比</text>
          <text class="metric-value">
            {{ stock.volumeAnalysis ? stock.volumeAnalysis.volumeAnalysis.largeOrders : '45' }}%
          </text>
        </view>
      </view>
      
      <!-- 尾盘成交量分析 -->
      <view class="volume-distribution">
        <text class="section-title">成交量分布</text>
        <view class="time-slots">
          <view class="time-slot" v-for="(slot, index) in getTimeSlots(stock)" :key="index">
            <view class="slot-bar" :style="{ height: slot.ratio * 2 + 'rpx' }"></view>
            <text class="slot-time">{{ slot.time }}</text>
            <text class="slot-ratio">{{ slot.ratio }}%</text>
          </view>
        </view>
      </view>
      
      <!-- 成交量趋势 -->
      <view class="volume-trend">
        <text class="section-title">近5日量比趋势</text>
        <view class="trend-chart">
          <view 
            v-for="(value, index) in getVolumeTrend(stock)" 
            :key="index" 
            class="trend-bar" 
            :style="{ height: value * 0.6 + 'rpx' }"
            :class="getTrendBarClass(value, index, getVolumeTrend(stock))"
          ></view>
        </view>
        <view class="trend-labels">
          <text v-for="(_, index) in getVolumeTrend(stock)" :key="index" class="trend-day">
            Day {{ 5 - index }}
          </text>
        </view>
      </view>
      
      <!-- AI建议 -->
      <view class="ai-advice">
        <text class="advice-title">AI建议</text>
        <text class="advice-content">{{ generateAdvice(stock) }}</text>
      </view>
    </view>
    
    <view class="modal-footer">
      <button class="modal-btn buy-btn" @click="buyStock">买入</button>
      <button class="modal-btn close-btn" @click="closePopup">关闭</button>
    </view>
  </view>
</template>

<script>
export default {
  name: 'VolumeDetailPopup',
  props: {
    stock: {
      type: Object,
      default: null
    }
  },
  methods: {
    closePopup() {
      this.$emit('close');
    },
    buyStock() {
      this.$emit('buy', this.stock);
      this.closePopup();
    },
    getPatternClass(stock) {
      if (!stock.volumeAnalysis || !stock.volumeAnalysis.pattern) {
        return '';
      }
      
      return stock.volumeAnalysis.pattern.signal === 'bullish' ? 'bullish-pattern' : 'bearish-pattern';
    },
    getVolumeRatioClass(stock) {
      if (!stock.volumeAnalysis || !stock.volumeAnalysis.volumeRatio) {
        return '';
      }
      
      const ratio = stock.volumeAnalysis.volumeRatio;
      if (ratio >= 2.0) {
        return 'volume-high';
      } else if (ratio >= 1.5) {
        return 'volume-medium';
      } else if (ratio >= 1.0) {
        return 'volume-normal';
      } else {
        return 'volume-low';
      }
    },
    getMainInflow(stock) {
      if (!stock.volumeAnalysis || stock.volumeAnalysis.mainNetInflow === undefined) {
        return 0;
      }
      
      return stock.volumeAnalysis.mainNetInflow;
    },
    getTimeSlots(stock) {
      if (!stock.volumeAnalysis || !stock.volumeAnalysis.volumeAnalysis || !stock.volumeAnalysis.volumeAnalysis.keyTimeSlots) {
        return [
          { time: '14:30-15:00', ratio: 20 },
          { time: '13:00-14:30', ratio: 30 },
          { time: '11:30-13:00', ratio: 10 },
          { time: '10:00-11:30', ratio: 25 },
          { time: '9:30-10:00', ratio: 15 }
        ];
      }
      
      return stock.volumeAnalysis.volumeAnalysis.keyTimeSlots;
    },
    getVolumeTrend(stock) {
      if (!stock.volumeAnalysis || !stock.volumeAnalysis.volumeAnalysis || !stock.volumeAnalysis.volumeAnalysis.volumeTrend) {
        return [100, 105, 95, 120, 150];
      }
      
      return stock.volumeAnalysis.volumeAnalysis.volumeTrend;
    },
    getTrendBarClass(value, index, trend) {
      // 获取前一天的值
      const prevValue = index < trend.length - 1 ? trend[index + 1] : value;
      
      // 如果当天值比前一天高,返回上升类,否则返回下降类
      return value >= prevValue ? 'trend-up' : 'trend-down';
    },
    generateAdvice(stock) {
      if (!stock || !stock.volumeAnalysis) {
        return '暂无足够数据生成建议';
      }
      
      const pattern = stock.volumeAnalysis.pattern;
      const volumeRatio = stock.volumeAnalysis.volumeRatio;
      const mainInflow = stock.volumeAnalysis.mainNetInflow;
      
      let advice = '';
      
      // 基于成交量模式生成建议
      if (pattern.signal === 'bullish') {
        if (volumeRatio >= 2.0 && mainInflow > 0) {
          advice = `该股尾盘成交量显著放大(${volumeRatio.toFixed(2)}倍)且主力资金净流入${mainInflow.toFixed(0)}万元,形成"${pattern.name}"模式,次日早盘有较大概率高开,建议尾盘买入,次日早盘择机卖出。`;
        } else if (volumeRatio >= 1.5) {
          advice = `该股成交量较前期有所放大(${volumeRatio.toFixed(2)}倍),形成"${pattern.name}"模式,技术面向好,建议尾盘买入,次日开盘观察走势,高开2%以上可考虑卖出。`;
        } else {
          advice = `该股形成"${pattern.name}"模式但成交量配合一般,建议谨慎参与,可小仓位试探性买入,严格设置止损位。`;
        }
      } else {
        if (volumeRatio >= 2.0 && mainInflow < 0) {
          advice = `该股尾盘成交量显著放大(${volumeRatio.toFixed(2)}倍)但主力资金净流出${Math.abs(mainInflow).toFixed(0)}万元,形成"${pattern.name}"模式,存在较大抛压,不建议现阶段买入,可等待企稳后再考虑介入。`;
        } else if (pattern.name === '量价背离') {
          advice = `该股出现"量价背离"走势,价格虽创新高但成交量未配合,上涨动能减弱,不建议追高,可等待回调确认支撑后再考虑。`;
        } else {
          advice = `该股形成"${pattern.name}"模式,短期技术面偏弱,建议观望为主,不适合当前进行T+0操作。`;
        }
      }
      
      return advice;
    }
  }
};
</script>

<style>
.volume-detail-modal {
  width: 680rpx;
  padding: 30rpx;
  background-color: #222;
  border-radius: 16rpx;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
  padding-bottom: 20rpx;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-title {
  font-size: 32rpx;
  color: #fff;
  font-weight: bold;
}

.modal-close {
  font-size: 40rpx;
  color: #ccc;
  height: 40rpx;
  width: 40rpx;
  line-height: 36rpx;
  text-align: center;
}

.modal-content {
  margin-bottom: 30rpx;
}

.volume-pattern-info {
  background-color: rgba(255, 255, 255, 0.05);
  padding: 20rpx;
  border-radius: 10rpx;
  margin-bottom: 20rpx;
}

.pattern-title {
  font-size: 28rpx;
  color: #ccc;
  margin-right: 10rpx;
}

.pattern-value {
  font-size: 30rpx;
  font-weight: bold;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
  margin-right: 10rpx;
}

.bullish-pattern {
  color: #ee0a24;
  background-color: rgba(238, 10, 36, 0.1);
}

.bearish-pattern {
  color: #07c160;
  background-color: rgba(7, 193, 96, 0.1);
}

.pattern-desc {
  font-size: 26rpx;
  color: #fff;
  margin-top: 10rpx;
  display: block;
}

.volume-metrics {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.metric-item {
  text-align: center;
  flex: 1;
}

.metric-label {
  font-size: 24rpx;
  color: #ccc;
  margin-bottom: 8rpx;
  display: block;
}

.metric-value {
  font-size: 30rpx;
  font-weight: bold;
  color: #fff;
}

.volume-high {
  color: #ee0a24;
}

.volume-medium {
  color: #ff9900;
}

.volume-normal {
  color: #ffffff;
}

.volume-low {
  color: #07c160;
}

.positive {
  color: #ee0a24;
}

.negative {
  color: #07c160;
}

.volume-distribution, .volume-trend {
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 28rpx;
  color: #fff;
  margin-bottom: 16rpx;
  display: block;
}

.time-slots {
  display: flex;
  justify-content: space-between;
  height: 200rpx;
  align-items: flex-end;
}

.time-slot {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 18%;
}

.slot-bar {
  width: 30rpx;
  background: linear-gradient(to top, #07c160, #409eff);
  border-radius: 6rpx;
  margin-bottom: 10rpx;
}

.slot-time {
  font-size: 20rpx;
  color: #ccc;
  transform: scale(0.8);
  white-space: nowrap;
}

.slot-ratio {
  font-size: 22rpx;
  color: #fff;
}

.trend-chart {
  display: flex;
  justify-content: space-between;
  height: 200rpx;
  align-items: flex-end;
}

.trend-bar {
  width: 30rpx;
  border-radius: 6rpx;
  margin: 0 10rpx;
}

.trend-up {
  background: linear-gradient(to top, #ee0a24, #ff6b81);
}

.trend-down {
  background: linear-gradient(to top, #07c160, #42d392);
}

.trend-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 10rpx;
}

.trend-day {
  font-size: 22rpx;
  color: #ccc;
  width: 20%;
  text-align: center;
}

.ai-advice {
  background-color: rgba(255, 255, 255, 0.05);
  padding: 20rpx;
  border-radius: 10rpx;
}

.advice-title {
  font-size: 28rpx;
  color: #fff;
  margin-bottom: 10rpx;
  display: block;
}

.advice-content {
  font-size: 26rpx;
  color: #ccc;
  line-height: 1.5;
}

.modal-footer {
  display: flex;
  justify-content: space-between;
}

.modal-btn {
  flex: 1;
  margin: 0 10rpx;
  padding: 20rpx 0;
  border: none;
  border-radius: 10rpx;
  font-size: 28rpx;
  font-weight: bold;
}

.buy-btn {
  background-color: #ee0a24;
  color: #fff;
}

.close-btn {
  background-color: rgba(255, 255, 255, 0.1);
  color: #fff;
}
</style> 
