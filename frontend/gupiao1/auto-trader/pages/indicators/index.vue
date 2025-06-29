<template>
  <div class="indicators-page">
    <h2 class="page-title">技术指标库</h2>
    <p class="page-description">我们提供多种常用技术分析指标,帮助您做出更明智的交易决策。</p>
    
    <div class="indicator-list">
      <div class="indicator-card" v-for="(indicator, index) in indicators" :key="index" @click="showIndicatorDetail(indicator)">
        <div class="indicator-icon" :class="indicator.category">
          <i :class="indicator.icon"></i>
        </div>
        <div class="indicator-info">
          <h3>{{ indicator.name }}</h3>
          <p>{{ indicator.description }}</p>
        </div>
      </div>
    </div>
    
    <div class="indicator-modal" v-if="selectedIndicator" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ selectedIndicator.name }}</h2>
          <button class="close-button" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="indicator-detail">
            <h3>指标说明</h3>
            <p>{{ selectedIndicator.detailedDescription }}</p>
            
            <h3>计算方法</h3>
            <p>{{ selectedIndicator.calculation }}</p>
            
            <h3>使用方法</h3>
            <p>{{ selectedIndicator.usage }}</p>
            
            <h3>交易信号</h3>
            <ul>
              <li v-for="(signal, i) in selectedIndicator.signals" :key="i">
                {{ signal }}
              </li>
            </ul>
          </div>
        </div>
        <div class="modal-footer">
          <button class="primary-button" @click="learnMore">了解更多</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedIndicator: null,
      indicators: [
        {
          name: "MACD (移动平均线汇聚背离)",
          category: "momentum",
          icon: "chart-line",
          description: "结合三条移动平均线的趋势指标,用于识别动量变化和潜在反转",
          detailedDescription: "MACD是一种趋势跟踪动量指标,显示两条移动平均线之间的关系。MACD由MACD线(快线-慢线),信号线(MACD的移动平均线)和直方图(两线之差)组成。",
          calculation: "MACD线 = 12日EMA - 26日EMA\n信号线 = 9日MACD线EMA\n直方图 = MACD线 - 信号线",
          usage: "MACD可用于识别新趋势的形成,趋势方向的确认和趋势动量的判断。还可用于发现背离现象,预测可能的价格反转。",
          signals: [
            "金叉:MACD线上穿信号线,看涨信号",
            "死叉:MACD线下穿信号线,看跌信号",
            "零线穿越:MACD线穿越零线,表明趋势可能转变",
            "背离:价格与MACD走势不一致,可能预示反转"
          ]
        },
        {
          name: "RSI (相对强弱指数)",
          category: "oscillator",
          icon: "chart-bar",
          description: "测量价格变动速度和幅度的动量振荡器,用于识别超买和超卖条件",
          detailedDescription: "RSI是一种动量振荡指标,衡量当前价格相对于其历史价格的强度。RSI的值介于0和100之间,通常用于识别超买和超卖水平。",
          calculation: "RSI = 100 - (100 / (1 + RS))\nRS = 平均上涨幅度 / 平均下跌幅度\n通常基于14个周期计算",
          usage: "RSI主要用于识别超买和超卖条件,以及判断价格趋势的强度。还可用于发现背离现象,预测可能的价格反转。",
          signals: [
            "RSI > 70:市场可能超买,价格可能即将下跌",
            "RSI < 30:市场可能超卖,价格可能即将上涨",
            "中线穿越:RSI穿越50线,可能表明趋势发生变化",
            "背离:价格与RSI走势不一致,可能预示反转"
          ]
        },
        {
          name: "布林带 (Bollinger Bands)",
          category: "volatility",
          icon: "chart-area",
          description: "根据价格波动性动态调整的价格通道,用于识别价格波动和突破",
          detailedDescription: "布林带由三条线组成:中轨(通常为20日移动平均线),上轨(中轨加上两个标准差)和下轨(中轨减去两个标准差)。这些带根据市场波动性自动调整宽度。",
          calculation: "中轨 = 20日简单移动平均线(SMA)\n上轨 = 中轨 + (20日价格标准差 × 2)\n下轨 = 中轨 - (20日价格标准差 × 2)",
          usage: "布林带可用于识别价格波动性的变化,潜在的支撑和阻力位,以及价格突破。布林带收窄通常预示着即将出现大幅波动。",
          signals: [
            "价格触及上轨:可能的超买状态或强劲上涨趋势",
            "价格触及下轨:可能的超卖状态或强劲下跌趋势",
            "布林带收窄(挤压):预示即将出现大幅波动",
            "价格在通道内波动:可能处于震荡市场"
          ]
        },
        {
          name: "KDJ 指标",
          category: "oscillator",
          icon: "chart-line",
          description: "基于随机指标的修改版,加入J值提高敏感度,用于判断超买超卖和趋势",
          detailedDescription: "KDJ是随机指标的变种,增加了J值以提高敏感度。K线和D线类似于随机指标中的%K和%D线,而J线则根据K和D的差值计算,放大了K和D的变动。",
          calculation: "未成熟随机值RSV = (收盘价 - N日最低价) / (N日最高价 - N日最低价) × 100\nK = 前一日K值 × (2/3) + 当日RSV × (1/3)\nD = 前一日D值 × (2/3) + 当日K值 × (1/3)\nJ = 3 × K - 2 × D",
          usage: "KDJ主要用于判断超买超卖状态和潜在的价格反转点。J线由于其敏感性,常被用来提前确认K和D的交叉信号。",
          signals: [
            "K线上穿D线:看涨信号",
            "K线下穿D线:看跌信号",
            "KDJ三线在80以上:超买状态,可能即将回落",
            "KDJ三线在20以下:超卖状态,可能即将反弹"
          ]
        },
        {
          name: "威廉指标 (Williams %R)",
          category: "oscillator",
          icon: "chart-bar",
          description: "测量收盘价相对于近期最高价范围的位置,用于识别超买和超卖区域",
          detailedDescription: "威廉指标(Williams %R)是一种动量振荡器,测量收盘价在最近N个交易日的高低价格范围中的位置。该指标在0到-100之间波动,与随机指标类似但更为敏感。",
          calculation: "%R = ((N日最高价 - 收盘价) / (N日最高价 - N日最低价)) × -100\n通常基于14个周期计算",
          usage: "威廉指标主要用于识别超买和超卖条件,以及潜在的价格反转点。它对市场短期反转特别敏感,可用于日内交易和短线交易策略。",
          signals: [
            "指标低于-80:市场可能超卖,潜在买入机会",
            "指标高于-20:市场可能超买,潜在卖出机会",
            "指标从超卖区上穿-80线:较强的买入信号",
            "指标从超买区下穿-20线:较强的卖出信号",
            "指标与价格走势出现背离:可能预示趋势即将反转"
          ]
        },
        {
          name: "移动平均线 (MA)",
          category: "trend",
          icon: "chart-line",
          description: "平滑价格数据以识别趋势方向和潜在支撑/阻力位",
          detailedDescription: "移动平均线是最常用和最简单的技术指标之一,用于平滑价格数据并帮助识别趋势。有多种类型的移动平均线,包括简单移动平均线(SMA),指数移动平均线(EMA)等。",
          calculation: "简单移动平均线(SMA) = N日收盘价之和 / N\n指数移动平均线(EMA) = 当日收盘价 × K + 前一日EMA × (1-K),其中K = 2/(N+1)",
          usage: "移动平均线主要用于识别趋势方向,趋势强度和潜在的支撑/阻力位。多条不同周期的移动平均线交叉可提供买卖信号。",
          signals: [
            "价格上穿移动平均线:看涨信号",
            "价格下穿移动平均线:看跌信号",
            "短期MA上穿长期MA(金叉):看涨信号",
            "短期MA下穿长期MA(死叉):看跌信号",
            "多条MA呈多头排列(短期在上,长期在下):强烈上升趋势",
            "多条MA呈空头排列(短期在下,长期在上):强烈下降趋势"
          ]
        },
        {
          name: "成交量 (Volume)",
          category: "volume",
          icon: "chart-bar",
          description: "衡量市场活动和参与度的指标,用于确认价格趋势和识别潜在反转",
          detailedDescription: "成交量是市场中交易的股票,合约或商品的数量,是衡量市场参与度和流动性的重要指标。成交量通常与价格结合分析,用于确认趋势和识别潜在的市场反转。",
          calculation: "成交量本身不需要特殊计算,但通常会结合移动平均线来平滑数据,如5日或10日成交量移动平均线。",
          usage: "成交量主要用于确认价格趋势的强度,识别潜在的价格反转点,以及判断市场情绪。价格变动与成交量的关系可提供重要的交易信号。",
          signals: [
            "价格上涨+成交量增加:强劲上升趋势,看涨信号",
            "价格上涨+成交量减少:上升趋势可能减弱",
            "价格下跌+成交量增加:强劲下降趋势,看跌信号",
            "价格下跌+成交量减少:下降趋势可能减弱",
            "成交量突然放大:可能的突破或转折点",
            "价格创新高/新低但成交量未相应增加:可能的背离信号"
          ]
        }
      ]
    };
  },
  methods: {
    showIndicatorDetail(indicator) {
      this.selectedIndicator = indicator;
    },
    closeModal() {
      this.selectedIndicator = null;
    },
    learnMore() {
      // 根据所选指标跳转到详情页
      if (this.selectedIndicator.name.includes('威廉指标')) {
        this.$router.push('/indicators/williams-r');
      } else if (this.selectedIndicator.name.includes('MACD')) {
        this.$router.push('/indicators/macd');
      } else if (this.selectedIndicator.name.includes('RSI')) {
        this.$router.push('/indicators/rsi');
      } else {
        // 其他指标的详情页
        this.$router.push('/indicators/detail');
      }
      this.closeModal();
    }
  }
};
</script>

<style scoped>
.indicators-page {
  padding: 20px;
}

.page-title {
  font-size: 24px;
  color: #333;
  margin-bottom: 10px;
}

.page-description {
  color: #666;
  margin-bottom: 30px;
}

.indicator-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.indicator-card {
  display: flex;
  align-items: center;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.indicator-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.indicator-icon {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  margin-right: 15px;
  font-size: 22px;
}

.indicator-icon.trend {
  background-color: #e3f2fd;
  color: #1976d2;
}

.indicator-icon.oscillator {
  background-color: #f3e5f5;
  color: #9c27b0;
}

.indicator-icon.momentum {
  background-color: #e8f5e9;
  color: #43a047;
}

.indicator-icon.volatility {
  background-color: #fff3e0;
  color: #ff9800;
}

.indicator-icon.volume {
  background-color: #ffebee;
  color: #e53935;
}

.indicator-info h3 {
  font-size: 16px;
  margin: 0 0 5px 0;
  color: #333;
}

.indicator-info p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.indicator-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 80%;
  max-width: 800px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.indicator-detail h3 {
  font-size: 18px;
  color: #333;
  margin: 15px 0 10px 0;
}

.indicator-detail p {
  font-size: 14px;
  line-height: 1.6;
  color: #555;
  white-space: pre-line;
}

.indicator-detail ul {
  padding-left: 20px;
}

.indicator-detail li {
  margin-bottom: 8px;
  font-size: 14px;
  color: #555;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
}

.primary-button {
  padding: 8px 16px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.primary-button:hover {
  background-color: #1565c0;
}
</style> 
