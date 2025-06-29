<template>
  <view :class="['container', isDarkMode ? 'dark-theme' : 'light-theme']">
    <view class="header">
      <text class="title">我的持仓</text>
      <view class="summary">
        <view class="summary-item">
          <text class="summary-label">总市值</text>
          <text class="summary-value">¥{{totalMarketValue}}</text>
        </view>
        <view class="summary-item">
          <text class="summary-label">今日收益</text>
          <text :class="['summary-value', todayProfit >= 0 ? 'profit' : 'loss']">{{todayProfit >= 0 ? '+' : ''}}¥{{todayProfit}}</text>
        </view>
        <view class="summary-item">
          <text class="summary-label">总收益</text>
          <text :class="['summary-value', totalProfit >= 0 ? 'profit' : 'loss']">{{totalProfit >= 0 ? '+' : ''}}¥{{totalProfit}}</text>
        </view>
      </view>
    </view>
    
    <view class="portfolio-chart">
      <!-- 使用纯色块和百分比文本方式显示资产分布 -->
      <view class="distribution-container">
        <view class="distribution-title">资产分布</view>
        
        <view class="distribution-row">
          <view class="distribution-bar">
            <view class="bar-segment" style="width: 25%; background-color: #FF5252;"></view>
            <view class="bar-segment" style="width: 22%; background-color: #4CAF50;"></view>
            <view class="bar-segment" style="width: 15%; background-color: #4C8DFF;"></view>
            <view class="bar-segment" style="width: 16%; background-color: #FF9800;"></view>
            <view class="bar-segment" style="width: 22%; background-color: #9C27B0;"></view>
          </view>
        </view>
        
        <view class="distribution-labels">
          <view class="distribution-item">
            <view class="item-color" style="background-color: #FF5252;"></view>
            <text class="item-name">贵州茅台</text>
            <text class="item-percent">25%</text>
          </view>
          <view class="distribution-item">
            <view class="item-color" style="background-color: #4CAF50;"></view>
            <text class="item-name">平安银行</text>
            <text class="item-percent">22%</text>
          </view>
          <view class="distribution-item">
            <view class="item-color" style="background-color: #4C8DFF;"></view>
            <text class="item-name">中国平安</text>
            <text class="item-percent">15%</text>
          </view>
          <view class="distribution-item">
            <view class="item-color" style="background-color: #FF9800;"></view>
            <text class="item-name">宁德时代</text>
            <text class="item-percent">16%</text>
          </view>
          <view class="distribution-item">
            <view class="item-color" style="background-color: #9C27B0;"></view>
            <text class="item-name">中国联通</text>
            <text class="item-percent">22%</text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="filter-bar">
      <text :class="['filter-item', currentFilter === 'all' ? 'active' : '']" @click="setFilter('all')">全部</text>
      <text :class="['filter-item', currentFilter === 'profit' ? 'active' : '']" @click="setFilter('profit')">盈利</text>
      <text :class="['filter-item', currentFilter === 'loss' ? 'active' : '']" @click="setFilter('loss')">亏损</text>
    </view>
    
    <view class="stock-list">
      <view v-for="(stock, index) in filteredStocks" :key="index" class="stock-item" @click="showTradeDetail(stock)">
        <view class="stock-info">
          <text class="stock-name">{{stock.name}}</text>
          <text class="stock-code">{{stock.code}}</text>
          <view class="stock-tags">
            <text v-if="stock.isRecommended" class="tag recommended">推荐</text>
            <text v-if="stock.isWarning" class="tag warning">风险</text>
            <text v-if="stock.tradeSource === 'ai'" class="tag ai-trade">Agent交易</text>
          </view>
        </view>
        
        <view class="stock-price">
          <text class="current-price">{{stock.currentPrice}}</text>
          <text :class="['price-change', stock.priceChange >= 0 ? 'profit' : 'loss']">
            {{stock.priceChange >= 0 ? '+' : ''}}{{stock.priceChange}}%
          </text>
        </view>
        
        <view class="holding-info">
          <view class="holding-row">
            <text class="holding-label">持仓</text>
            <text class="holding-value">{{stock.quantity}}股</text>
          </view>
          <view class="holding-row">
            <text class="holding-label">成本</text>
            <text class="holding-value">{{stock.costPrice}}</text>
          </view>
          <view class="holding-row">
            <text class="holding-label">买入时间</text>
            <text class="holding-value">{{stock.buyDate || '未知'}}</text>
          </view>
          <view class="holding-row">
            <text class="holding-label">交易来源</text>
            <text class="holding-value">{{stock.tradeSource === 'ai' ? 'AI自动' : '手动'}}</text>
          </view>
          <view class="holding-row">
            <text class="holding-label">市值</text>
            <text class="holding-value">{{stock.marketValue}}</text>
          </view>
        </view>
        
        <view class="profit-info">
          <view class="profit-row">
            <text class="profit-label">盈亏</text>
            <text :class="['profit-value', stock.profit >= 0 ? 'profit' : 'loss']">
              {{stock.profit >= 0 ? '+' : ''}}¥{{stock.profit}}
            </text>
          </view>
          <view class="profit-row">
            <text class="profit-label">盈亏率</text>
            <text :class="['profit-value', stock.profitRate >= 0 ? 'profit' : 'loss']">
              {{stock.profitRate >= 0 ? '+' : ''}}{{stock.profitRate}}%
            </text>
          </view>
        </view>
        
        <view class="action-buttons">
          <button class="action-btn buy" @click.stop="buyStock(stock)">买入</button>
          <button class="action-btn sell" @click.stop="sellStock(stock)">卖出</button>
        </view>
      </view>
      
      <view v-if="filteredStocks.length === 0" class="empty-state">
        <text class="empty-text">暂无持仓</text>
      </view>
    </view>
    
    <view class="floating-button" @click="showAddStockModal">
      <text class="add-icon">+</text>
    </view>
  </view>
</template>

<script>
import { getAITradeHistory, addAITradeToPortfolio } from '../../services/agentTradingService.js';

export default {
  data() {
    return {
      isDarkMode: false,
      currentFilter: 'all',
      stocks: [
        {
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
          buyDate: '2023-06-15',
          tradeSource: 'manual'
        },
        {
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
          buyDate: '2023-05-22',
          tradeSource: 'manual'
        },
        {
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
          buyDate: '2023-07-03',
          tradeSource: 'ai'
        },
        {
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
          buyDate: '2023-04-18',
          tradeSource: 'ai'
        },
        {
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
          buyDate: '2023-01-30',
          tradeSource: 'manual'
        }
      ],
      loadingAITrades: false
    }
  },
  computed: {
    filteredStocks() {
      if (this.currentFilter === 'all') {
        return this.stocks;
      } else if (this.currentFilter === 'profit') {
        return this.stocks.filter(stock => stock.profit >= 0);
      } else {
        return this.stocks.filter(stock => stock.profit < 0);
      }
    },

    // 计算总市值
    totalMarketValue() {
      const total = this.stocks.reduce((sum, stock) => {
        const marketValue = typeof stock.marketValue === 'string'
          ? parseFloat(stock.marketValue.replace(/,/g, ''))
          : stock.marketValue;
        return sum + (marketValue || 0);
      }, 0);
      return total.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },

    // 计算总收益
    totalProfit() {
      const total = this.stocks.reduce((sum, stock) => sum + (stock.profit || 0), 0);
      return total.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },

    // 计算今日收益（简化版，实际应该基于今日价格变化）
    todayProfit() {
      const total = this.stocks.reduce((sum, stock) => {
        const currentPrice = parseFloat(stock.currentPrice);
        const priceChange = stock.priceChange || 0;
        const quantity = stock.quantity || 0;
        const todayChange = (currentPrice * priceChange / 100) * quantity;
        return sum + todayChange;
      }, 0);
      return total.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
  },
  methods: {
    setFilter(filter) {
      this.currentFilter = filter;
    },
    buyStock(stock) {
      uni.navigateTo({
        url: `/pages/trade-settings/index?code=${stock.code}&action=buy`
      });
    },
    sellStock(stock) {
      uni.navigateTo({
        url: `/pages/trade-settings/index?code=${stock.code}&action=sell`
      });
    },
    showAddStockModal() {
      uni.navigateTo({
        url: '/pages/stock-picking/index'
      });
    },
    showTradeDetail(stock) {
      uni.navigateTo({
        url: `/pages/portfolio/stock-detail?code=${stock.code}`
      });
    },
    /**
     * 加载Agent交易并添加到持仓列表
     */
    async loadAITrades() {
      try {
        this.loadingAITrades = true;
        
        // 从东吴秀才获取Agent交易数据
        const response = await getAITradeHistory();
        
        if (response.success && response.data && response.data.trades) {
          // 处理每个Agent交易
          for (const trade of response.data.trades) {
            if (trade.action === 'buy') {
              // 添加到持仓列表
              await addAITradeToPortfolio(trade);
            }
          }
          
          // 重新加载持仓数据
          this.loadPortfolioData();
        }
      } catch (error) {
        console.error('加载Agent交易失败:', error);
        uni.showToast({
          title: '加载Agent交易失败',
          icon: 'none'
        });
      } finally {
        this.loadingAITrades = false;
      }
    },
    
    /**
     * 加载持仓数据
     */
    async loadPortfolioData() {
      try {
        // 首先尝试从交易服务获取真实持仓数据
        await this.loadRealPositions();

        // 然后从本地存储加载Agent交易的持仓数据
        const storedPortfolio = uni.getStorageSync('portfolio');
        if (storedPortfolio) {
          try {
            const portfolioData = JSON.parse(storedPortfolio);
            if (Array.isArray(portfolioData) && portfolioData.length > 0) {
              // 将持仓数据与真实数据合并
              this.stocks = [...this.stocks, ...portfolioData.filter(stock =>
                !this.stocks.some(s => s.code === stock.code)
              )];
            }
          } catch (e) {
            console.error('解析本地持仓数据失败:', e);
          }
        }
      } catch (error) {
        console.error('加载持仓数据失败:', error);
      }
    },

    /**
     * 从Agent系统获取真实持仓数据
     */
    async loadRealPositions() {
      try {
        // 首先尝试从agentDataService获取真实持仓数据
        const agentDataService = (await import('@/services/agentDataService.js')).default;

        try {
          const result = await agentDataService.getPositions();

          if (result.success && result.data && result.data.length > 0) {
            // 转换数据格式
            const realStocks = result.data.map(position => ({
              name: position.name,
              code: position.symbol,
              currentPrice: position.current_price.toFixed(2),
              priceChange: ((position.current_price - position.cost_price) / position.cost_price * 100).toFixed(2),
              quantity: position.volume,
              costPrice: position.cost_price.toFixed(2),
              marketValue: position.market_value.toFixed(2),
              profit: position.profit_loss,
              profitRate: (position.profit_loss_ratio * 100).toFixed(2),
              isRecommended: position.profit_loss > 0,
              isWarning: position.profit_loss < -1000,
              buyDate: position.position_date || '未知',
              tradeSource: 'agent' // Agent真实数据
            }));

            // 更新持仓数据
            this.stocks = realStocks;

            console.log('✅ 成功获取Agent真实持仓数据:', realStocks.length, '只股票');
            console.log('📊 总市值:', realStocks.reduce((sum, stock) => sum + parseFloat(stock.marketValue), 0).toFixed(2));
            return;
          }
        } catch (agentError) {
          console.warn('从Agent获取持仓数据失败:', agentError);
        }

        // 如果Agent数据获取失败，使用tradingService的备用数据
        const tradingService = (await import('@/services/tradingService.js')).default;
        const positionResult = await tradingService.getPositions();

        if (positionResult.success && positionResult.data && positionResult.data.length > 0) {
          // 转换数据格式
          const backupStocks = positionResult.data.map(position => ({
            name: position.name,
            code: position.symbol,
            currentPrice: position.current_price.toFixed(2),
            priceChange: position.price_change_pct.toFixed(2),
            quantity: position.volume,
            costPrice: position.cost_price.toFixed(2),
            marketValue: position.market_value.toFixed(2),
            profit: position.profit_loss,
            profitRate: (position.profit_loss_ratio * 100).toFixed(2),
            isRecommended: position.profit_loss > 0,
            isWarning: position.profit_loss < -1000,
            buyDate: position.position_date || '未知',
            tradeSource: 'backup' // 备用数据
          }));

          this.stocks = backupStocks;
          console.log('✅ 使用备用持仓数据:', backupStocks.length, '只股票');
        } else {
          console.warn('⚠️ 当前无持仓数据');
          this.stocks = [];
        }
      } catch (error) {
        console.error('获取持仓数据异常:', error);
        console.log('使用空持仓数据');
        this.stocks = [];
      }
    },

    /**
     * 获取API基础URL
     */
    getApiBaseUrl() {
      // 根据环境返回不同的API地址
      if (process.env.NODE_ENV === 'development') {
        return 'http://localhost:8000';
      } else {
        return 'https://aigupiao.me';
      }
    }
  },
  onLoad() {
    // 获取当前主题设置
    const app = getApp();
    this.isDarkMode = app.globalData.isDarkMode;
    
    // 加载持仓数据
    this.loadPortfolioData();
    
    // 加载Agent交易数据
    this.loadAITrades();
  },
  onShow() {
    // 每次显示页面时检查当前主题
    const app = getApp();
    this.isDarkMode = app.globalData.isDarkMode;
    
    // 重新加载持仓数据
    this.loadPortfolioData();
  }
}
</script>

<style>
/* 基础容器样式 */
.container {
  padding: 30rpx;
  min-height: 100vh;
}

/* 主题样式 */
.dark-theme {
  background-color: #141414;
  color: #ffffff;
}

.light-theme {
  background-color: #f5f5f5;
  color: #333333;
}

/* 头部样式 */
.header {
  margin-bottom: 30rpx;
  position: relative;
  display: flex;
  flex-direction: column;
}

.title {
  font-size: 40rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
}

.view-trade-history {
  position: absolute;
  right: 30rpx;
  top: 30rpx;
}

.trade-history-link {
  font-size: 28rpx;
  color: #4C8DFF;
  padding: 10rpx 20rpx;
  border-radius: 30rpx;
  background-color: rgba(76, 141, 255, 0.1);
}

.dark-theme .title {
  color: #ffffff;
}

.light-theme .title {
  color: #333333;
}

/* 概览信息 */
.summary {
  display: flex;
  justify-content: space-between;
  padding: 20rpx;
  border-radius: 12rpx;
  margin-bottom: 30rpx;
}

.dark-theme .summary {
  background-color: #222222;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.3);
}

.light-theme .summary {
  background-color: #ffffff;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.summary-label {
  font-size: 24rpx;
  margin-bottom: 5rpx;
}

.dark-theme .summary-label {
  color: #999999;
}

.light-theme .summary-label {
  color: #666666;
}

.summary-value {
  font-size: 32rpx;
  font-weight: bold;
}

.dark-theme .summary-value {
  color: #ffffff;
}

.light-theme .summary-value {
  color: #333333;
}

/* 资产分布图表样式 */
.portfolio-chart {
  border-radius: 12rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.dark-theme .portfolio-chart {
  background-color: #222222;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.3);
}

.light-theme .portfolio-chart {
  background-color: #ffffff;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.distribution-container {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.distribution-title {
  font-size: 30rpx;
  font-weight: bold;
  margin-bottom: 25rpx;
  text-align: center;
}

.dark-theme .distribution-title {
  color: #ffffff;
}

.light-theme .distribution-title {
  color: #333333;
}

.distribution-row {
  margin-bottom: 25rpx;
}

.distribution-bar {
  width: 100%;
  height: 30rpx;
  border-radius: 15rpx;
  overflow: hidden;
  display: flex;
}

.dark-theme .distribution-bar {
  background-color: #333333;
}

.light-theme .distribution-bar {
  background-color: #eeeeee;
}

.bar-segment {
  height: 100%;
  display: inline-block;
}

.distribution-labels {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  padding: 0 10rpx;
}

.distribution-item {
  display: flex;
  align-items: center;
  margin-bottom: 15rpx;
  width: 45%;
}

.item-color {
  width: 20rpx;
  height: 20rpx;
  border-radius: 4rpx;
  margin-right: 10rpx;
  flex-shrink: 0;
}

.item-name {
  font-size: 24rpx;
  margin-right: 10rpx;
  flex: 1;
}

.dark-theme .item-name {
  color: #dddddd;
}

.light-theme .item-name {
  color: #333333;
}

.item-percent {
  font-size: 24rpx;
  font-weight: bold;
}

.dark-theme .item-percent {
  color: #ffffff;
}

.light-theme .item-percent {
  color: #333333;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  margin-bottom: 20rpx;
  padding: 0 10rpx;
}

.filter-item {
  padding: 15rpx 25rpx;
  font-size: 28rpx;
  border-radius: 30rpx;
  margin-right: 20rpx;
}

.dark-theme .filter-item {
  color: #999999;
  background-color: #222222;
}

.light-theme .filter-item {
  color: #666666;
  background-color: #ffffff;
}

.filter-item.active {
  background-color: #4c8dff;
  color: #ffffff;
}

/* 股票列表 */
.stock-list {
  border-radius: 12rpx;
}

.dark-theme .stock-list {
  background-color: #222222;
}

.light-theme .stock-list {
  background-color: #ffffff;
}

.stock-item {
  padding: 30rpx 20rpx;
  border-bottom-width: 1px;
  display: flex;
  flex-direction: column;
}

.dark-theme .stock-item {
  border-bottom-color: #333333;
}

.light-theme .stock-item {
  border-bottom-color: #eeeeee;
}

/* 股票信息 */
.stock-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15rpx;
}

.stock-name {
  font-size: 32rpx;
  font-weight: bold;
}

.dark-theme .stock-name {
  color: #ffffff;
}

.light-theme .stock-name {
  color: #333333;
}

.stock-code {
  font-size: 24rpx;
  margin-left: 10rpx;
}

.dark-theme .stock-code {
  color: #999999;
}

.light-theme .stock-code {
  color: #666666;
}

.stock-tags {
  display: flex;
}

.tag {
  font-size: 22rpx;
  padding: 4rpx 10rpx;
  border-radius: 4rpx;
  margin-left: 10rpx;
}

.tag.recommended {
  background-color: #4c8dff;
  color: #ffffff;
}

.tag.warning {
  background-color: #ff9800;
  color: #ffffff;
}

.tag.ai-trade {
  background-color: #9C27B0;
  color: #ffffff;
}

/* 股票价格 */
.stock-price {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15rpx;
}

.current-price {
  font-size: 30rpx;
  font-weight: bold;
}

.dark-theme .current-price {
  color: #ffffff;
}

.light-theme .current-price {
  color: #333333;
}

.price-change {
  font-size: 26rpx;
}

/* 持仓信息 */
.holding-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15rpx;
}

.holding-row {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.holding-label {
  font-size: 24rpx;
  margin-bottom: 5rpx;
}

.dark-theme .holding-label {
  color: #999999;
}

.light-theme .holding-label {
  color: #666666;
}

.holding-value {
  font-size: 26rpx;
  font-weight: bold;
}

.dark-theme .holding-value {
  color: #ffffff;
}

.light-theme .holding-value {
  color: #333333;
}

/* 盈亏信息 */
.profit-info {
  display: flex;
  justify-content: space-around;
  margin-bottom: 15rpx;
}

.profit-row {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.profit-label {
  font-size: 24rpx;
  margin-bottom: 5rpx;
}

.dark-theme .profit-label {
  color: #999999;
}

.light-theme .profit-label {
  color: #666666;
}

.profit-value {
  font-size: 26rpx;
  font-weight: bold;
}

/* 按钮区域 */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  margin-top: 15rpx;
}

.action-btn {
  padding: 10rpx 30rpx;
  font-size: 26rpx;
  border-radius: 6rpx;
  margin-left: 20rpx;
}

.action-btn.buy {
  background-color: #ff5252;
  color: #ffffff;
}

.action-btn.sell {
  background-color: #4caf50;
  color: #ffffff;
}

/* 空状态 */
.empty-state {
  padding: 100rpx 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.empty-text {
  font-size: 30rpx;
}

.dark-theme .empty-text {
  color: #999999;
}

.light-theme .empty-text {
  color: #666666;
}

/* 浮动按钮 */
.floating-button {
  position: fixed;
  right: 30rpx;
  bottom: 50rpx;
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  background-color: #4c8dff;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 4rpx 10rpx rgba(0, 0, 0, 0.3);
}

.add-icon {
  font-size: 50rpx;
  color: #ffffff;
}

/* 涨跌样式 */
.profit {
  color: #ff5252 !important;
}

.loss {
  color: #4caf50 !important;
}
</style> 
