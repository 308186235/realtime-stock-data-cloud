import { defineStore } from 'pinia'
import StrategyManager from '../utils/strategies/strategyManager.js'

export const useStrategyStore = defineStore('strategy', {
  state: () => ({
    stockInfo: {
      name: '示例股票',
      code: 'SH000001',
      price: 3258.63,
      change: 18.25,
      changePercent: 0.56
    },
    stockData: {
      prices: [],
      volumes: [],
      highs: [],
      lows: [],
      opens: [],
      closes: [],
      dates: []
    },
    analysisResult: {
      overallScore: 65,
      decision: {
        action: 'buy',
        confidence: 'medium',
        allocation: 0.6,
        description: '大部分指标显示积极信号,市场走势向好。'
      },
      weights: {
        sixSword: 0.35,
        jiuFang: 0.35,
        compass: 0.30
      }
    },
    strategyResults: {
      sixSword: null,
      jiuFang: null,
      compass: null
    },
    isLoading: false,
    lastUpdated: null,
    selectedTimeframe: 'daily', // 'daily', 'weekly', 'monthly'
    detectedPatterns: []
  }),
  
  getters: {
    priceChangeClass: (state) => {
      return state.stockInfo.change > 0 ? 'increase' : state.stockInfo.change < 0 ? 'decrease' : '';
    },
    
    formattedLastUpdated: (state) => {
      if (!state.lastUpdated) return '未更新';
      return new Date(state.lastUpdated).toLocaleString('zh-CN');
    },
    
    bullishPatterns: (state) => {
      return state.detectedPatterns.filter(pattern => pattern.direction === 'bullish');
    },
    
    bearishPatterns: (state) => {
      return state.detectedPatterns.filter(pattern => pattern.direction === 'bearish');
    }
  },
  
  actions: {
    async fetchStockData(stockCode) {
      this.isLoading = true;
      
      try {
        // 实际应用中,这里会调用API获取股票数据
        // 为了演示,这里使用模拟数据
        const mockStockData = this.generateMockStockData();
        
        // 保存原始数据用于可视化
        this.stockData = mockStockData;
        
        // 分析股票数据
        this.analyzeStockData(mockStockData);
        
        // 更新股票信息
        if (stockCode) {
          this.stockInfo.code = stockCode;
        }
        
        this.lastUpdated = new Date();
      } catch (error) {
        console.error('获取股票数据失败:', error);
        uni.showToast({
          title: '获取数据失败',
          icon: 'none'
        });
      } finally {
        this.isLoading = false;
      }
    },
    
    // 生成模拟股票数据
    generateMockStockData() {
      const prices = [];
      const volumes = [];
      const highs = [];
      const lows = [];
      const opens = [];
      const closes = [];
      const dates = [];
      
      // 生成60天的模拟数据
      let price = 100;
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 60);
      
      for (let i = 0; i < 60; i++) {
        const change = (Math.random() - 0.5) * 2;
        price = Math.max(50, price + change);
        prices.push(price);
        
        const high = price + Math.random() * 1;
        const low = price - Math.random() * 1;
        highs.push(high);
        lows.push(low);
        
        opens.push(price - change / 2);
        closes.push(price);
        
        volumes.push(Math.random() * 1000000 + 500000);
        
        const currentDate = new Date(startDate);
        currentDate.setDate(startDate.getDate() + i);
        dates.push(currentDate.toISOString().split('T')[0]);
      }
      
      return {
        prices,
        volumes,
        highs,
        lows,
        opens,
        closes,
        dates
      };
    },
    
    // 分析股票数据
    analyzeStockData(stockData) {
      const strategyManager = new StrategyManager();
      
      // 使用策略管理器分析数据
      const result = strategyManager.analyzeStock(stockData);
      
      // 更新分析结果
      this.analysisResult = {
        overallScore: result.overallScore,
        decision: result.decision,
        weights: result.weights
      };
      
      // 更新各个策略的结果
      this.strategyResults = {
        sixSword: result.strategyResults.sixSword,
        jiuFang: result.strategyResults.jiuFang,
        compass: result.strategyResults.compass
      };
      
      // 更新检测到的形态
      if (result.strategyResults.jiuFang && result.strategyResults.jiuFang.detectedPatterns) {
        this.detectedPatterns = result.strategyResults.jiuFang.detectedPatterns;
      }
    },
    
    // 切换时间周期
    changeTimeframe(timeframe) {
      this.selectedTimeframe = timeframe;
      this.fetchStockData();
    },
    
    // 更新策略权重
    updateStrategyWeights(weights) {
      this.analysisResult.weights = weights;
      this.analyzeStockData(this.stockData);
    }
  }
}); 
