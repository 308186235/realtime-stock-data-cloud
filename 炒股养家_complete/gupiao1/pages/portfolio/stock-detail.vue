<template>
  <view :class="['container', isDarkMode ? 'dark-theme' : 'light-theme']">
    <view class="header">
      <view class="back-btn" @click="navigateBack">
        <text class="back-icon">←</text>
      </view>
      <view class="stock-info">
        <text class="stock-name">{{stock.name}}</text>
        <text class="stock-code">{{stock.code}}</text>
      </view>
      <view class="stock-price" :class="stock.priceChange >= 0 ? 'up' : 'down'">
        <text class="price">{{stock.currentPrice}}</text>
        <text class="change">{{stock.priceChange >= 0 ? '+' : ''}}{{stock.priceChange}}%</text>
      </view>
    </view>
    
    <!-- 加载中提示 -->
    <view v-if="loading" class="loading-container">
      <view class="loading-spinner"></view>
      <text class="loading-text">正在获取东吴秀才交易数据...</text>
    </view>
    
    <!-- 错误提示 -->
    <view v-else-if="error" class="error-container">
      <text class="error-icon">!</text>
      <text class="error-message">{{error}}</text>
      <button class="retry-button" @click="fetchStockData(stockCode)">重新获取</button>
    </view>
    
    <!-- 主要内容 -->
    <view v-else>
      <!-- K线图表 -->
      <view class="chart-section">
        <view class="card-title">
          <text class="title-text">股票行情</text>
          <text class="subtitle">持仓:{{stock.quantity}}股 成本:{{stock.costPrice}}</text>
          
          <!-- 添加Agent交易显示开关 -->
          <view class="ai-trade-toggle">
            <text class="toggle-label">显示Agent交易</text>
            <switch :checked="showAITrades" @change="toggleAITrades" color="#4C8DFF" />
          </view>
        </view>
        
        <!-- MA指标头部 -->
        <view class="ma-indicator-bar">
          <view class="ma-left">
            <text class="ma-title">MA</text>
            <text class="ma-item ma5">MA5:<text>1825.30</text><text class="arrow down">↓</text></text>
            <text class="ma-item ma10">10:<text>1810.75</text><text class="arrow down">↓</text></text>
            <text class="ma-item ma20">20:<text>1795.62</text><text class="arrow down">↓</text></text>
            <text class="ma-item ma60">60:<text>1780.03</text><text class="arrow up">↑</text></text>
          </view>
          <view class="ma-right">
            <text class="current-price">{{stock.currentPrice}}</text>
          </view>
        </view>
        
        <!-- 专业K线图 -->
        <view class="pro-chart-container">
          <!-- 价格轴 -->
          <view class="price-axis left">
            <text class="price-label">{{Math.round(parseFloat(stock.currentPrice) * 1.05)}}</text>
            <text class="price-label">{{Math.round(parseFloat(stock.currentPrice) * 1.025)}}</text>
            <text class="price-label">{{Math.round(parseFloat(stock.currentPrice))}}</text>
            <text class="price-label">{{Math.round(parseFloat(stock.currentPrice) * 0.975)}}</text>
            <text class="price-label">{{Math.round(parseFloat(stock.currentPrice) * 0.95)}}</text>
          </view>
          
          <!-- K线主图区域 -->
          <view class="chart-main-area">
            <!-- 网格线 -->
            <view class="grid-lines">
              <view class="grid-line"></view>
              <view class="grid-line"></view>
              <view class="grid-line"></view>
              <view class="grid-line"></view>
              <view class="grid-line"></view>
            </view>
            
            <!-- 蜡烛图 -->
            <view class="candlestick-chart">
              <!-- 蜡烛图示例 - 实际项目中应由Canvas API绘制 -->
              <view class="candlestick red" style="left: 0%; height: 40px; top: 30%;">
                <view class="wick" style="height: 60px;"></view>
              </view>
              <view class="candlestick green" style="left: 4%; height: 36px; top: 35%;">
                <view class="wick" style="height: 55px;"></view>
              </view>
              <view class="candlestick red" style="left: 8%; height: 42px; top: 25%;">
                <view class="wick" style="height: 65px;"></view>
              </view>
              <view class="candlestick red" style="left: 12%; height: 38px; top: 32%;">
                <view class="wick" style="height: 58px;"></view>
              </view>
              <view class="candlestick green" style="left: 16%; height: 45px; top: 40%;">
                <view class="wick" style="height: 70px;"></view>
              </view>
              <view class="candlestick red" style="left: 20%; height: 30px; top: 35%;">
                <view class="wick" style="height: 50px;"></view>
              </view>
              <view class="candlestick red" style="left: 24%; height: 35px; top: 30%;">
                <view class="wick" style="height: 55px;"></view>
              </view>
              <view class="candlestick green" style="left: 28%; height: 28px; top: 45%;">
                <view class="wick" style="height: 48px;"></view>
              </view>
              <view class="candlestick red" style="left: 32%; height: 25px; top: 35%;">
                <view class="wick" style="height: 45px;"></view>
              </view>
              <view class="candlestick red" style="left: 36%; height: 32px; top: 33%;">
                <view class="wick" style="height: 52px;"></view>
              </view>
              <view class="candlestick green" style="left: 40%; height: 38px; top: 42%;">
                <view class="wick" style="height: 58px;"></view>
              </view>
              <view class="candlestick red" style="left: 44%; height: 30px; top: 38%;">
                <view class="wick" style="height: 50px;"></view>
              </view>
              <view class="candlestick red" style="left: 48%; height: 35px; top: 36%;">
                <view class="wick" style="height: 55px;"></view>
              </view>
              <view class="candlestick green" style="left: 52%; height: 40px; top: 45%;">
                <view class="wick" style="height: 60px;"></view>
              </view>
              <view class="candlestick red" style="left: 56%; height: 30px; top: 35%;">
                <view class="wick" style="height: 50px;"></view>
              </view>
              <view class="candlestick red" style="left: 60%; height: 42px; top: 30%;">
                <view class="wick" style="height: 62px;"></view>
              </view>
              <view class="candlestick green" style="left: 64%; height: 35px; top: 38%;">
                <view class="wick" style="height: 55px;"></view>
              </view>
              <view class="candlestick red" style="left: 68%; height: 45px; top: 25%;">
                <view class="wick" style="height: 65px;"></view>
              </view>
              <view class="candlestick green" style="left: 72%; height: 50px; top: 35%;">
                <view class="wick" style="height: 70px;"></view>
              </view>
              <view class="candlestick green" style="left: 76%; height: 45px; top: 40%;">
                <view class="wick" style="height: 65px;"></view>
              </view>
              <view class="candlestick red" style="left: 80%; height: 40px; top: 35%;">
                <view class="wick" style="height: 60px;"></view>
              </view>
              <view class="candlestick green" style="left: 84%; height: 35px; top: 45%;">
                <view class="wick" style="height: 55px;"></view>
              </view>
              <view class="candlestick red" style="left: 88%; height: 30px; top: 40%;">
                <view class="wick" style="height: 50px;"></view>
              </view>
              <view class="candlestick red" style="left: 92%; height: 38px; top: 32%;">
                <view class="wick" style="height: 58px;"></view>
              </view>
              <view class="candlestick green" style="left: 96%; height: 42px; top: 38%;">
                <view class="wick" style="height: 62px;"></view>
              </view>
            </view>
            
            <!-- MA线 -->
            <view class="ma-lines">
              <view class="ma-line ma5"></view>
              <view class="ma-line ma10"></view>
              <view class="ma-line ma20"></view>
              <view class="ma-line ma60"></view>
            </view>
            
            <!-- 实际买卖点标记 -->
            <view class="trade-signals">
              <view v-if="buySignals.length > 0" class="trade-signal buy" style="left: 28%; top: 50%;">
                <text class="signal-icon">买</text>
                <view class="signal-connector"></view>
                <view class="signal-label">
                  <text class="label-type">实际买入</text>
                  <text class="label-details">{{buySignals[0].date}} ¥{{buySignals[0].price}}</text>
                </view>
              </view>
              <view v-if="buySignals.length > 1" class="trade-signal buy" style="left: 50%; top: 45%;">
                <text class="signal-icon">买</text>
                <view class="signal-connector"></view>
                <view class="signal-label">
                  <text class="label-type">实际买入</text>
                  <text class="label-details">{{buySignals[1].date}} ¥{{buySignals[1].price}}</text>
                </view>
              </view>
              <view v-if="sellSignals && sellSignals.length > 0" class="trade-signal sell" style="left: 70%; top: 30%;">
                <text class="signal-icon">卖</text>
                <view class="signal-connector"></view>
                <view class="signal-label">
                  <text class="label-type">实际卖出</text>
                  <text class="label-details">{{sellSignals[0].date}} ¥{{sellSignals[0].price}}</text>
                </view>
              </view>
            </view>
            
            <!-- AI买卖点标记 -->
            <view class="ai-signals" v-if="showAITrades">
              <!-- 现有的AI信号 -->
              <view v-if="aiSignals && aiSignals.length > 0" v-for="(signal, index) in aiSignals" :key="index"
                :class="['ai-signal', signal.type || 'buy']" 
                :style="signal.type === 'sell' ? 'left: 85%; top: 30%;' : 'left: 90%; top: 45%;'">
                <text class="signal-icon">AI</text>
                <view class="signal-connector"></view>
                <view class="signal-label">
                  <text class="label-type">{{signal.type === 'sell' ? 'AI推荐卖出' : 'AI推荐买入'}}</text>
                  <text class="label-details">¥{{signal.price}}</text>
                </view>
              </view>
              
              <!-- AI历史交易点位 -->
              <view v-for="(trade, index) in aiHistoryTrades" :key="'ai-history-'+index"
                :class="['ai-signal', trade.action === 'sell' ? 'sell' : 'buy']" 
                :style="getAITradePosition(trade, index)">
                <text class="signal-icon">AI</text>
                <view class="signal-connector"></view>
                <view class="signal-label">
                  <text class="label-type">{{trade.action === 'sell' ? 'AI卖出' : 'AI买入'}}</text>
                  <text class="label-details">{{formatDate(trade.tradeTime, 'MM-DD')}} ¥{{trade.price}}</text>
                  <text class="label-strategy">{{trade.strategy}}</text>
                </view>
              </view>
            </view>
          </view>
          
          <!-- 右侧价格轴 -->
          <view class="price-axis right">
            <text class="price-label">{{Math.round(parseFloat(stock.currentPrice) * 1.05)}}</text>
            <text class="price-label">{{Math.round(parseFloat(stock.currentPrice) * 1.025)}}</text>
            <text class="price-label">{{Math.round(parseFloat(stock.currentPrice))}}</text>
            <text class="price-label">{{Math.round(parseFloat(stock.currentPrice) * 0.975)}}</text>
            <text class="price-label">{{Math.round(parseFloat(stock.currentPrice) * 0.95)}}</text>
          </view>
        </view>
        
        <!-- 成交量图表 -->
        <view class="volume-chart">
          <view class="volume-bars">
            <view class="volume-bar red" style="height: 40%; left: 0%"></view>
            <view class="volume-bar green" style="height: 30%; left: 4%"></view>
            <view class="volume-bar red" style="height: 60%; left: 8%"></view>
            <view class="volume-bar red" style="height: 35%; left: 12%"></view>
            <view class="volume-bar green" style="height: 45%; left: 16%"></view>
            <view class="volume-bar red" style="height: 55%; left: 20%"></view>
            <view class="volume-bar red" style="height: 40%; left: 24%"></view>
            <view class="volume-bar green" style="height: 25%; left: 28%"></view>
            <view class="volume-bar red" style="height: 35%; left: 32%"></view>
            <view class="volume-bar red" style="height: 30%; left: 36%"></view>
            <view class="volume-bar green" style="height: 45%; left: 40%"></view>
            <view class="volume-bar red" style="height: 50%; left: 44%"></view>
            <view class="volume-bar red" style="height: 35%; left: 48%"></view>
            <view class="volume-bar green" style="height: 30%; left: 52%"></view>
            <view class="volume-bar red" style="height: 40%; left: 56%"></view>
            <view class="volume-bar red" style="height: 60%; left: 60%"></view>
            <view class="volume-bar green" style="height: 35%; left: 64%"></view>
            <view class="volume-bar red" style="height: 55%; left: 68%"></view>
            <view class="volume-bar green" style="height: 70%; left: 72%"></view>
            <view class="volume-bar green" style="height: 50%; left: 76%"></view>
            <view class="volume-bar red" style="height: 40%; left: 80%"></view>
            <view class="volume-bar green" style="height: 30%; left: 84%"></view>
            <view class="volume-bar red" style="height: 25%; left: 88%"></view>
            <view class="volume-bar red" style="height: 35%; left: 92%"></view>
            <view class="volume-bar green" style="height: 45%; left: 96%"></view>
          </view>
        </view>
        
        <!-- 日期轴 -->
        <view class="date-axis">
          <text class="date-label">05-01</text>
          <text class="date-label">06-01</text>
          <text class="date-label">07-01</text>
          <text class="date-label">08-01</text>
          <text class="date-label">今日</text>
        </view>
      </view>
      
      <!-- 持仓收益信息 -->
      <view class="position-card">
        <view class="position-title">持仓收益</view>
        <view class="position-info">
          <view class="info-row">
            <view class="info-item">
              <text class="info-label">持仓数量</text>
              <text class="info-value">{{stock.quantity}}股</text>
            </view>
            <view class="info-item">
              <text class="info-label">持仓成本</text>
              <text class="info-value">¥{{stock.costPrice}}</text>
            </view>
          </view>
          <view class="info-row">
            <view class="info-item">
              <text class="info-label">持仓市值</text>
              <text class="info-value">¥{{stock.marketValue}}</text>
            </view>
            <view class="info-item">
              <text class="info-label">买入时间</text>
              <text class="info-value">{{stock.buyDate}}</text>
            </view>
          </view>
          <view class="info-row">
            <view class="info-item">
              <text class="info-label">盈亏金额</text>
              <text :class="['info-value', stock.profit >= 0 ? 'profit' : 'loss']">
                {{stock.profit >= 0 ? '+' : ''}}¥{{stock.profit}}
              </text>
            </view>
            <view class="info-item">
              <text class="info-label">盈亏比例</text>
              <text :class="['info-value', stock.profitRate >= 0 ? 'profit' : 'loss']">
                {{stock.profitRate >= 0 ? '+' : ''}}{{stock.profitRate}}%
              </text>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 操作按钮 -->
      <view class="action-buttons">
        <view class="action-button trade" @click="showBuyDialog">
          <text class="button-text">买入</text>
        </view>
        <view class="action-button trade sell" @click="showSellDialog">
          <text class="button-text">卖出</text>
        </view>
        <view class="action-button detail" @click="showTradeDetail">
          <text class="button-text">交易记录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import tradingService from '../../services/tradingService.js';
import { getAITradeHistory } from '../../services/agentTradingService.js';

export default {
  data() {
    return {
      isDarkMode: false,
      stockCode: '',
      stock: {
        name: '',
        code: '',
        currentPrice: '0.00',
        priceChange: 0,
        quantity: 0,
        costPrice: '0.00',
        marketValue: '0.00',
        profit: 0,
        profitRate: 0,
        isRecommended: false,
        isWarning: false,
        buyDate: ''
      },
      buySignals: [],
      sellSignals: [],
      aiSignals: [],
      aiHistoryTrades: [], // 存储AI历史交易数据
      showAITrades: true, // 是否显示Agent交易点位
      highlightTradeTime: '', // 需要高亮显示的交易时间
      loading: false,
      error: null
    }
  },
  onLoad(options) {
    if (options.code) {
      this.stockCode = options.code;
      this.fetchStockData(this.stockCode);
      
      // 处理Agent交易显示参数
      if (options.showAITrade === 'true') {
        this.showAITrades = true;
        
        // 如果指定了交易时间,需要定位到该交易
        if (options.tradeTime) {
          this.highlightTradeTime = decodeURIComponent(options.tradeTime);
        }
      }
    }
    
    // 获取当前主题设置
    const app = getApp();
    this.isDarkMode = app.globalData.isDarkMode;
  },
  methods: {
    navigateBack() {
      uni.navigateBack();
    },
    
    showBuyDialog() {
      uni.navigateTo({
        url: `/pages/trade-settings/index?code=${this.stock.code}&action=buy`
      });
    },
    
    showSellDialog() {
      uni.navigateTo({
        url: `/pages/trade-settings/index?code=${this.stock.code}&action=sell`
      });
    },
    
    showTradeDetail() {
      uni.navigateTo({
        url: `/pages/portfolio/trade-detail?code=${this.stock.code}`
      });
    },
    
    // 切换Agent交易显示
    toggleAITrades(e) {
      this.showAITrades = e.detail.value;
    },
    
    // 计算Agent交易点位位置
    getAITradePosition(trade, index) {
      // 将交易日期映射到图表位置(范围0-100%)
      const now = new Date();
      const tradeDate = new Date(trade.tradeTime);
      const dateDiff = Math.min(180, Math.floor((now - tradeDate) / (24 * 60 * 60 * 1000))); // 最多显示180天数据
      
      // 计算横坐标位置 (越近的日期越靠右)
      const xPosition = Math.max(5, 100 - (dateDiff / 180) * 95);
      
      // 计算纵坐标位置 (买入点在底部,卖出点在顶部)
      let yPosition = 0;
      if (trade.action === 'buy') {
        yPosition = 45 + (index % 3) * 5; // 买入点位于下方
      } else {
        yPosition = 25 + (index % 3) * 5; // 卖出点位于上方
      }
      
      return `left: ${xPosition}%; top: ${yPosition}%;`;
    },
    
    // 获取Agent交易历史
    async fetchAITradeHistory(code) {
      try {
        const response = await getAITradeHistory(50);
        
        if (response.success && response.data && response.data.trades) {
          // 筛选当前股票的Agent交易
          this.aiHistoryTrades = response.data.trades.filter(trade => 
            trade.stockCode === code || trade.stockCode.endsWith(code)
          );
          
          console.log(`获取到${this.aiHistoryTrades.length}条Agent交易历史数据`);
          
          // 如果需要高亮显示特定交易,找到该交易并在UI上高亮显示
          if (this.highlightTradeTime) {
            const highlightedTrade = this.aiHistoryTrades.find(trade => 
              trade.tradeTime === this.highlightTradeTime
            );
            
            if (highlightedTrade) {
              this.highlightAITrade(highlightedTrade);
            }
          }
        }
      } catch (error) {
        console.error('获取Agent交易历史失败:', error);
      }
    },
    
    // 高亮显示特定Agent交易
    highlightAITrade(trade) {
      setTimeout(() => {
        // 使用uni-app提供的showToast显示交易信息
        uni.showToast({
          title: `${trade.action === 'buy' ? '买入' : '卖出'}${trade.stockName} ¥${trade.price}`,
          icon: 'none',
          duration: 3000
        });
        
        // 此处可添加K线图滚动到指定日期的逻辑
        // 由于当前K线图为静态模拟,实际项目中应该调用图表库API定位到特定日期
      }, 500);
    },
    
    // 从东吴秀才获取持仓数据
    async fetchStockData(code) {
      this.loading = true;
      this.error = null;
      
      try {
        // 获取持仓信息
        const positionResult = await tradingService.getPositions();
        if (!positionResult || !positionResult.success) {
          throw new Error(positionResult?.message || '获取持仓信息失败');
        }
        
        // 查找当前股票持仓
        const stockPosition = Array.isArray(positionResult.data) ? 
          positionResult.data.find(pos => pos.symbol === code) : null;
        
        if (!stockPosition) {
          throw new Error(`未找到代码为${code}的持仓信息`);
        }
        
        // 更新股票信息
        this.stock = {
          name: stockPosition.name || '',
          code: stockPosition.symbol,
          currentPrice: stockPosition.current_price,
          priceChange: stockPosition.price_change_pct || 0,
          quantity: stockPosition.volume,
          costPrice: stockPosition.cost_price,
          marketValue: stockPosition.market_value,
          profit: stockPosition.profit_loss,
          profitRate: stockPosition.profit_loss_ratio,
          isRecommended: stockPosition.profit_loss > 0,
          isWarning: stockPosition.profit_loss < 0,
          buyDate: this.formatDate(stockPosition.position_date || new Date().toISOString())
        };
        
        // 获取交易记录
        await this.fetchTradeRecords(code);
        
        // 获取Agent交易历史
        await this.fetchAITradeHistory(code);
      } catch (error) {
        console.error('获取股票数据失败:', error);
        this.error = error.message || '获取股票数据失败';
        
        // 使用备用静态数据
        this.useBackupData(code);
      } finally {
        this.loading = false;
      }
    },
    
    // 获取交易记录
    async fetchTradeRecords(code) {
      try {
        // 获取近一个月的交易记录
        const endDate = new Date();
        const startDate = new Date();
        startDate.setMonth(startDate.getMonth() - 1);
        
        const tradesResult = await tradingService.getTrades({
          start_date: this.formatDate(startDate, 'YYYY-MM-DD'),
          end_date: this.formatDate(endDate, 'YYYY-MM-DD')
        });
        
        if (!tradesResult || !tradesResult.success) {
          throw new Error(tradesResult?.message || '获取交易记录失败');
        }
        
        // 筛选出当前股票的交易记录
        const stockTrades = Array.isArray(tradesResult.data) ? 
          tradesResult.data.filter(trade => trade.symbol === code) : [];
        
        if (stockTrades.length === 0) {
          console.log(`未找到代码为${code}的历史交易记录`);
          // 使用股票持仓记录生成买入信号
          this.generateSignalsFromPosition();
          return;
        }
        
        // 处理买入记录
        const buyTrades = stockTrades.filter(trade => trade.direction === 'BUY');
        this.buySignals = buyTrades.map(trade => ({
          date: this.formatDate(trade.trade_time, 'MM-DD'),
          price: trade.price.toFixed(2)
        })).slice(0, 3); // 最多显示3个买入点
        
        // 处理卖出记录
        const sellTrades = stockTrades.filter(trade => trade.direction === 'SELL');
        this.sellSignals = sellTrades.map(trade => ({
          date: this.formatDate(trade.trade_time, 'MM-DD'),
          price: trade.price.toFixed(2)
        })).slice(0, 2); // 最多显示2个卖出点
        
        // 生成AI买点建议
        this.generateAISignals();
      } catch (error) {
        console.error('获取交易记录失败:', error);
        // 使用持仓信息生成信号
        this.generateSignalsFromPosition();
      }
    },
    
    // 使用持仓信息生成交易信号
    generateSignalsFromPosition() {
      // 生成买入信号
      this.buySignals = [{
        date: this.formatDate(this.stock.buyDate, 'MM-DD'),
        price: this.stock.costPrice
      }];
      
      // 如果股票盈利,生成一个卖出信号
      if (this.stock.profit > 0) {
        const sellDate = new Date();
        sellDate.setDate(sellDate.getDate() - Math.floor(Math.random() * 15));
        
        this.sellSignals = [{
          date: this.formatDate(sellDate, 'MM-DD'),
          price: (parseFloat(this.stock.currentPrice) * 0.95).toFixed(2)
        }];
      } else {
        this.sellSignals = [];
      }
      
      // 生成AI信号
      this.generateAISignals();
    },
    
    // 生成AI买卖点建议
    generateAISignals() {
      if (parseFloat(this.stock.profit) < 0) {
        // 亏损股票更可能有AI买点
        this.aiSignals = [{
          type: 'buy',
          price: (parseFloat(this.stock.currentPrice) * 0.98).toFixed(2)
        }];
      } else if (parseFloat(this.stock.profitRate) > 10) {
        // 盈利较多的股票可能有AI卖点
        this.aiSignals = [{
          type: 'sell',
          price: (parseFloat(this.stock.currentPrice) * 1.02).toFixed(2)
        }];
      } else {
        this.aiSignals = [];
      }
    },
    
    // 使用备用静态数据
    useBackupData(code) {
      // 股票静态数据
      const stocksData = {
        '600519': {
          name: '贵州茅台',
          code: '600519',
          currentPrice: '1760.88',
          priceChange: 2.15,
          quantity: 10,
          costPrice: '1680.25',
          marketValue: '17,608.80',
          profit: 806.30,
          profitRate: 4.80,
          isRecommended: true,
          isWarning: false,
          buyDate: '2023-06-15'
        },
        '000001': {
          name: '平安银行',
          code: '000001',
          currentPrice: '15.23',
          priceChange: -1.36,
          quantity: 1000,
          costPrice: '16.05',
          marketValue: '15,230.00',
          profit: -820.00,
          profitRate: -5.11,
          isRecommended: false,
          isWarning: true,
          buyDate: '2023-05-22'
        },
        '601318': {
          name: '中国平安',
          code: '601318',
          currentPrice: '48.75',
          priceChange: 0.56,
          quantity: 200,
          costPrice: '45.30',
          marketValue: '9,750.00',
          profit: 690.00,
          profitRate: 7.61,
          isRecommended: true,
          isWarning: false,
          buyDate: '2023-07-03'
        },
        '300750': {
          name: '宁德时代',
          code: '300750',
          currentPrice: '226.60',
          priceChange: 4.25,
          quantity: 50,
          costPrice: '200.40',
          marketValue: '11,330.00',
          profit: 1310.00,
          profitRate: 13.07,
          isRecommended: true,
          isWarning: false,
          buyDate: '2023-04-18'
        },
        '600050': {
          name: '中国联通',
          code: '600050',
          currentPrice: '4.68',
          priceChange: -0.21,
          quantity: 5000,
          costPrice: '5.12',
          marketValue: '23,400.00',
          profit: -2200.00,
          profitRate: -8.59,
          isRecommended: false,
          isWarning: true,
          buyDate: '2023-01-30'
        }
      };
    
      // 使用静态数据
      if (stocksData[code]) {
        this.stock = stocksData[code];
        
        // 生成交易信号
        if (code === '600519') {
          this.buySignals = [
            { date: '05-20', price: '1670.50' },
            { date: '06-15', price: '1680.25' }
          ];
          this.sellSignals = [
            { date: '07-10', price: '1725.80' }
          ];
        } else {
          // 生成通用信号
          this.generateSignalsFromPosition();
        }
      }
    },
    
    // 日期格式化
    formatDate(dateStr, format = 'YYYY-MM-DD') {
      const date = new Date(dateStr);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      
      if (format === 'YYYY-MM-DD') {
        return `${year}-${month}-${day}`;
      } else if (format === 'MM-DD') {
        return `${month}-${day}`;
      }
      
      return dateStr;
    }
  }
}
</script>

<style>
.container {
  min-height: 100vh;
}

.dark-theme {
  background-color: #141414;
  color: #ffffff;
}

.light-theme {
  background-color: #f5f5f5;
  color: #333333;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 30rpx;
}

.dark-theme .header {
  background-color: #222222;
  border-bottom: 1px solid #333333;
}

.light-theme .header {
  background-color: #ffffff;
  border-bottom: 1px solid #eeeeee;
}

.back-btn {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}

.dark-theme .back-icon {
  font-size: 40rpx;
  color: #ffffff;
}

.light-theme .back-icon {
  font-size: 40rpx;
  color: #333333;
}

.stock-info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stock-name {
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 5rpx;
}

.dark-theme .stock-name {
  color: #ffffff;
}

.light-theme .stock-name {
  color: #333333;
}

.stock-code {
  font-size: 24rpx;
}

.dark-theme .stock-code {
  color: #999999;
}

.light-theme .stock-code {
  color: #666666;
}

.stock-price {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.price {
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 5rpx;
}

.change {
  font-size: 24rpx;
}

.up {
  color: #ff5252;
}

.down {
  color: #4caf50;
}

/* K线图表部分 */
.chart-section {
  margin: 20rpx;
  padding: 20rpx;
  border-radius: 12rpx;
}

.dark-theme .chart-section {
  background-color: #222222;
}

.light-theme .chart-section {
  background-color: #ffffff;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.card-title {
  display: flex;
  align-items: center;
  margin-bottom: 15rpx;
  flex-wrap: wrap;
}

.title-text {
  font-size: 32rpx;
  font-weight: bold;
  margin-right: 20rpx;
}

.subtitle {
  font-size: 24rpx;
  color: #666666;
}

.ai-trade-toggle {
  margin-left: auto;
  display: flex;
  align-items: center;
}

.toggle-label {
  font-size: 24rpx;
  color: #666666;
  margin-right: 10rpx;
}

.ma-indicator-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10rpx;
  height: 40rpx;
}

.dark-theme .ma-indicator-bar {
  background-color: #1a1a1a;
}

.light-theme .ma-indicator-bar {
  background-color: #f5f5f5;
}

.ma-left {
  display: flex;
  align-items: center;
}

.ma-title {
  font-size: 22rpx;
  margin-right: 8rpx;
}

.dark-theme .ma-title {
  color: #999999;
}

.light-theme .ma-title {
  color: #666666;
}

.ma-item {
  font-size: 22rpx;
  margin-right: 12rpx;
  display: flex;
  align-items: center;
}

.ma5 {
  color: #ffffff;
}

.ma10 {
  color: #ffb74d;
}

.ma20 {
  color: #ce93d8;
}

.ma60 {
  color: #81d4fa;
}

.arrow {
  font-size: 18rpx;
  margin-left: 4rpx;
}

.arrow.up {
  color: #ff5252;
}

.arrow.down {
  color: #4caf50;
}

.current-price {
  font-size: 22rpx;
  font-weight: bold;
}

.dark-theme .current-price {
  color: #ffffff;
}

.light-theme .current-price {
  color: #333333;
}

.pro-chart-container {
  position: relative;
  height: 400rpx;
  border-radius: 8rpx;
  margin-bottom: 20rpx;
  display: flex;
}

.dark-theme .pro-chart-container {
  background-color: #333333;
}

.light-theme .pro-chart-container {
  background-color: #f5f5f5;
}

.price-axis {
  width: 45rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 5rpx 0;
}

.dark-theme .price-axis {
  background-color: #1a1a1a;
}

.light-theme .price-axis {
  background-color: #eeeeee;
}

.price-axis.left {
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.price-axis.right {
  border-left: 1px solid rgba(255, 255, 255, 0.1);
}

.price-label {
  font-size: 18rpx;
  text-align: center;
}

.dark-theme .price-label {
  color: #999999;
}

.light-theme .price-label {
  color: #666666;
}

.chart-main-area {
  flex: 1;
  position: relative;
}

.grid-lines {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 1;
}

.grid-line {
  position: absolute;
  left: 0;
  width: 100%;
  height: 1px;
}

.dark-theme .grid-line {
  background-color: rgba(255, 255, 255, 0.05);
}

.light-theme .grid-line {
  background-color: rgba(0, 0, 0, 0.05);
}

.grid-line:nth-child(1) {
  top: 0%;
}

.grid-line:nth-child(2) {
  top: 25%;
}

.grid-line:nth-child(3) {
  top: 50%;
}

.grid-line:nth-child(4) {
  top: 75%;
}

.grid-line:nth-child(5) {
  top: 100%;
}

.candlestick-chart {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 2;
}

.candlestick {
  position: absolute;
  width: 6rpx;
  transform: translateX(-50%);
}

.candlestick .wick {
  position: absolute;
  width: 1px;
  left: 50%;
  transform: translateX(-50%);
}

.dark-theme .candlestick.red {
  background-color: #ff5252;
}

.dark-theme .candlestick.green {
  background-color: #4caf50;
}

.light-theme .candlestick.red {
  background-color: #ff5252;
}

.light-theme .candlestick.green {
  background-color: #4caf50;
}

.ma-lines {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 3;
}

.ma-line {
  position: absolute;
  width: 100%;
  height: 1px;
}

.ma-line.ma5 {
  top: 30%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5) 10%, rgba(255, 255, 255, 0.5) 90%, transparent);
}

.ma-line.ma10 {
  top: 40%;
  background: linear-gradient(90deg, transparent, rgba(255, 183, 77, 0.5) 10%, rgba(255, 183, 77, 0.5) 90%, transparent);
}

.ma-line.ma20 {
  top: 50%;
  background: linear-gradient(90deg, transparent, rgba(206, 147, 216, 0.5) 10%, rgba(206, 147, 216, 0.5) 90%, transparent);
}

.ma-line.ma60 {
  top: 60%;
  background: linear-gradient(90deg, transparent, rgba(129, 212, 250, 0.5) 10%, rgba(129, 212, 250, 0.5) 90%, transparent);
}

.trade-signals, .ai-signals {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 4;
}

.trade-signal, .ai-signal {
  position: absolute;
  width: 30rpx;
  height: 30rpx;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 10rpx rgba(0, 0, 0, 0.7);
  z-index: 5;
  display: flex;
  justify-content: center;
  align-items: center;
}

.trade-signal.buy {
  background-color: #ff5252;
  border: 2rpx solid #ffffff;
}

.trade-signal.sell {
  background-color: #33cc33;
  border: 2rpx solid #ffffff;
}

.ai-signal.buy {
  background-color: #4c8dff;
  border: 2rpx solid #ffffff;
}

.ai-signal.sell {
  background-color: #4c8dff;
  border: 2rpx solid #ffffff;
}

.trade-signal::after, .ai-signal::after {
  content: '';
  position: absolute;
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  opacity: 0.6;
  animation: pulse 2s infinite;
}

.trade-signal.buy::after {
  background-color: #ff5252;
}

.trade-signal.sell::after {
  background-color: #33cc33;
}

.ai-signal.buy::after {
  background-color: #4c8dff;
  animation: pulse 1.5s infinite;
}

.ai-signal.sell::after {
  background-color: #4c8dff;
  animation: pulse 1.5s infinite;
}

/* 添加光晕效果 */
.trade-signal::before {
  content: '';
  position: absolute;
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  z-index: -1;
}

.ai-signal::before {
  content: '';
  position: absolute;
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  z-index: -1;
  border: 1rpx dashed #ffffff;
}

/* 添加AI买入卖出箭头指示器 */
.ai-signal.buy::before {
  content: '';
  display: block;
  width: 0;
  height: 0;
  border-left: 6rpx solid transparent;
  border-right: 6rpx solid transparent;
  border-bottom: 12rpx solid #ffffff;
  position: absolute;
  top: -14rpx;
  left: 50%;
  transform: translateX(-50%);
}

.ai-signal.sell::before {
  content: '';
  display: block;
  width: 0;
  height: 0;
  border-left: 6rpx solid transparent;
  border-right: 6rpx solid transparent;
  border-top: 12rpx solid #ffffff;
  position: absolute;
  bottom: -14rpx;
  left: 50%;
  transform: translateX(-50%);
}

.trade-signal .label-type {
  color: #ffffff;
  font-weight: bold;
}

.ai-signal .label-type {
  color: #4c8dff;
  font-weight: bold;
}

.signal-icon {
  position: absolute;
  font-size: 18rpx;
  color: #ffffff;
  font-weight: bold;
  text-shadow: 0 0 4rpx rgba(0, 0, 0, 0.7);
}

.signal-label {
  position: absolute;
  top: -55rpx;
  left: -80rpx;
  min-width: 160rpx;
  font-size: 22rpx;
  background-color: rgba(0, 0, 0, 0.9);
  color: #ffffff;
  padding: 8rpx 12rpx;
  border-radius: 6rpx;
  white-space: nowrap;
  z-index: 10;
  box-shadow: 0 4rpx 8rpx rgba(0, 0, 0, 0.5);
  font-weight: bold;
  text-align: center;
  display: flex;
  flex-direction: column;
  letter-spacing: 1rpx;
}

.label-type {
  font-weight: bold;
  font-size: 24rpx;
  padding-bottom: 4rpx;
  text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.5);
}

.label-details {
  font-size: 20rpx;
  opacity: 0.95;
  text-shadow: 0 1rpx 1rpx rgba(0, 0, 0, 0.3);
}

.trade-signal.buy .label-type {
  color: #ff5252;
}

.trade-signal.sell .label-type {
  color: #33cc33;
}

.ai-signal.buy .label-type {
  color: #4c8dff;
}

/* 添加更明显的连接线 */
.signal-label::after {
  content: '';
  position: absolute;
  bottom: -12rpx;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 10rpx solid transparent;
  border-right: 10rpx solid transparent;
  border-top: 12rpx solid rgba(0, 0, 0, 0.9);
}

/* 增加连接线 */
.signal-connector {
  position: absolute;
  width: 2rpx;
  height: 20rpx;
  background-color: #ffffff;
  bottom: -20rpx;
  left: 50%;
  transform: translateX(-50%);
}

/* 增加连接线 */
.signal-connector::after {
  content: '';
  position: absolute;
  bottom: -20rpx;
  left: 50%;
  transform: translateX(-50%);
  width: 2rpx;
  height: 20rpx;
  background-color: #ffffff;
}

.volume-chart {
  height: 60rpx;
  position: relative;
  margin-top: 2rpx;
}

.dark-theme .volume-chart {
  background-color: #1a1a1a;
}

.light-theme .volume-chart {
  background-color: #eeeeee;
}

.volume-bars {
  position: relative;
  height: 100%;
  width: 100%;
  padding: 0 45rpx;
}

.volume-bar {
  position: absolute;
  width: 6rpx;
  bottom: 0;
  transform: translateX(-50%);
}

.volume-bar.red {
  background-color: rgba(255, 82, 82, 0.6);
}

.volume-bar.green {
  background-color: rgba(76, 175, 80, 0.6);
}

.date-axis {
  display: flex;
  justify-content: space-between;
  padding: 0 45rpx;
  margin-top: 5rpx;
}

.date-label {
  font-size: 18rpx;
}

.dark-theme .date-label {
  color: #999999;
}

.light-theme .date-label {
  color: #666666;
}

/* 持仓收益信息 */
.position-card {
  margin: 20rpx;
  padding: 20rpx;
  border-radius: 12rpx;
}

.dark-theme .position-card {
  background-color: #222222;
}

.light-theme .position-card {
  background-color: #ffffff;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.position-title {
  font-size: 30rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
}

.dark-theme .position-title {
  color: #ffffff;
}

.light-theme .position-title {
  color: #333333;
}

.position-info {
  display: flex;
  flex-direction: column;
}

.info-row {
  display: flex;
  margin-bottom: 15rpx;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-item {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 24rpx;
  margin-bottom: 5rpx;
}

.dark-theme .info-label {
  color: #999999;
}

.light-theme .info-label {
  color: #666666;
}

.info-value {
  font-size: 28rpx;
  font-weight: bold;
}

.dark-theme .info-value {
  color: #ffffff;
}

.light-theme .info-value {
  color: #333333;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: space-between;
  margin: 20rpx;
}

.action-button {
  flex: 1;
  height: 80rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 6rpx;
  margin-right: 15rpx;
}

.action-button:last-child {
  margin-right: 0;
}

.action-button.trade {
  background-color: #ff5252;
}

.action-button.trade.sell {
  background-color: #4caf50;
}

.action-button.detail {
  background-color: #4c8dff;
}

.button-text {
  font-size: 28rpx;
  color: #ffffff;
  font-weight: bold;
}

.profit {
  color: #ff5252;
}

.loss {
  color: #4caf50;
}

/* 加载中提示 */
.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.loading-spinner {
  width: 40rpx;
  height: 40rpx;
  border: 4rpx solid rgba(255, 255, 255, 0.3);
  border-top: 4rpx solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-text {
  margin-top: 20rpx;
  font-size: 24rpx;
  color: #ffffff;
}

/* 错误提示 */
.error-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.error-icon {
  font-size: 40rpx;
  color: #ffffff;
  margin-bottom: 20rpx;
}

.error-message {
  font-size: 24rpx;
  color: #ffffff;
  margin-bottom: 20rpx;
}

.retry-button {
  background-color: #4caf50;
  color: #ffffff;
  border: none;
  padding: 10rpx 20rpx;
  border-radius: 6rpx;
  font-size: 28rpx;
  font-weight: bold;
}

@keyframes pulse {
  0% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.5);
    opacity: 0.2;
  }
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
}

/* 实际交易和AI推荐的不同标签样式 */
.trade-signal .signal-label {
  background-color: rgba(0, 0, 0, 0.9);
  border-left: 4rpx solid #ff5252;
}

.trade-signal.sell .signal-label {
  border-left: 4rpx solid #33cc33;
}

.ai-signal .signal-label {
  background-color: rgba(0, 0, 0, 0.85);
  border: 1rpx solid #4c8dff;
  border-left: 4rpx solid #4c8dff;
}

.ai-signal.buy .signal-label {
  border-top: 2rpx solid #4c8dff;
}

.ai-signal.sell .signal-label {
  border-bottom: 2rpx solid #4c8dff;
}

.ai-signal .label-strategy {
  font-size: 20rpx;
  color: #9C27B0;
  margin-top: 4rpx;
}

.dark-theme .ai-signal .label-strategy {
  color: #D48EF6;
}
</style> 
