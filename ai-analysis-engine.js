/**
 * AI分析引擎
 * 集成股票数据API和智能决策算法
 */

// 股票数据API配置
const STOCK_API_CONFIG = {
  // 茶股票数据API
  tea_api: {
    host: 'l1.chagubang.com',
    port: 6380,
    token: 'QT_wat5QfcJ6N9pDZM5',
    reconnect_interval: 5000,
    heartbeat_interval: 30000
  },
  
  // 备用数据源
  backup_sources: [
    'https://api.finance.yahoo.com',
    'https://api.alphavantage.co',
    'https://api.polygon.io'
  ]
};

// AI分析配置
const AI_CONFIG = {
  // 技术指标权重
  technical_weights: {
    ma: 0.2,      // 移动平均线
    rsi: 0.15,    // 相对强弱指数
    macd: 0.15,   // MACD
    kdj: 0.1,     // KDJ
    volume: 0.15, // 成交量
    price: 0.25   // 价格趋势
  },
  
  // 基本面权重
  fundamental_weights: {
    pe_ratio: 0.3,    // 市盈率
    pb_ratio: 0.2,    // 市净率
    roe: 0.2,         // 净资产收益率
    debt_ratio: 0.15, // 负债率
    growth: 0.15      // 增长率
  },
  
  // 风险控制
  risk_control: {
    max_position_ratio: 0.1,  // 单只股票最大仓位比例
    stop_loss_ratio: 0.05,    // 止损比例
    take_profit_ratio: 0.15,  // 止盈比例
    max_daily_trades: 10      // 每日最大交易次数
  }
};

// 股票数据管理器
class StockDataManager {
  constructor() {
    this.connection = null;
    this.isConnected = false;
    this.dataCache = new Map();
    this.subscribers = new Set();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }
  
  // 连接股票数据API
  async connect() {
    try {
      console.log('📡 尝试连接真实股票数据API...');

      // ❌ 拒绝使用模拟数据！
      throw new Error('❌ 拒绝连接模拟数据源！系统要求使用真实数据源');

    } catch (error) {
      console.error('❌ 股票数据API连接失败:', error);
      console.error('❌ 需要配置真实数据源:');
      console.error('1. 茶股帮实时数据源 (l1.chagubang.com:6380)');
      console.error('2. 淘宝股票数据推送服务 (QT_wat5QfcJ6N9pDZM5)');
      console.error('3. 其他真实股票数据API');
      throw error;
    }
  }
  
  // 开始接收数据
  startDataReceiving() {
    // ❌ 拒绝启动模拟数据推送！
    throw new Error('❌ 拒绝启动模拟数据推送！系统要求使用真实数据源');
  }

  // ❌ 已禁用模拟数据推送
  simulateDataPush() {
    throw new Error('❌ 模拟数据推送已被禁用！系统要求使用真实数据源');
  }
  
  // 通知订阅者
  notifySubscribers(data) {
    this.subscribers.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error('❌ 数据推送失败:', error);
      }
    });
  }
  
  // 订阅数据
  subscribe(callback) {
    this.subscribers.add(callback);
    return () => this.subscribers.delete(callback);
  }
  
  // 获取股票数据
  getStockData(code) {
    return this.dataCache.get(code);
  }
  
  // 获取所有股票数据
  getAllStockData() {
    return Array.from(this.dataCache.values());
  }
  
  // 处理重连
  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      
      console.log(`🔄 ${delay}ms后尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect();
      }, delay);
    } else {
      console.error('❌ 股票数据API重连次数已达上限');
    }
  }
}

// 技术分析器
class TechnicalAnalyzer {
  // 计算移动平均线
  static calculateMA(prices, period) {
    if (prices.length < period) return null;
    
    const sum = prices.slice(-period).reduce((a, b) => a + b, 0);
    return sum / period;
  }
  
  // 计算RSI
  static calculateRSI(prices, period = 14) {
    if (prices.length < period + 1) return null;
    
    let gains = 0;
    let losses = 0;
    
    for (let i = prices.length - period; i < prices.length; i++) {
      const change = prices[i] - prices[i - 1];
      if (change > 0) {
        gains += change;
      } else {
        losses -= change;
      }
    }
    
    const avgGain = gains / period;
    const avgLoss = losses / period;
    
    if (avgLoss === 0) return 100;
    
    const rs = avgGain / avgLoss;
    return 100 - (100 / (1 + rs));
  }
  
  // 计算MACD
  static calculateMACD(prices, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) {
    if (prices.length < slowPeriod) return null;
    
    const emaFast = this.calculateEMA(prices, fastPeriod);
    const emaSlow = this.calculateEMA(prices, slowPeriod);
    
    if (!emaFast || !emaSlow) return null;
    
    const macdLine = emaFast - emaSlow;
    return macdLine;
  }
  
  // 计算EMA
  static calculateEMA(prices, period) {
    if (prices.length < period) return null;
    
    const multiplier = 2 / (period + 1);
    let ema = prices[0];
    
    for (let i = 1; i < prices.length; i++) {
      ema = (prices[i] * multiplier) + (ema * (1 - multiplier));
    }
    
    return ema;
  }
  
  // 综合技术分析
  static analyzeTechnical(stockData, historicalPrices) {
    const analysis = {
      ma5: this.calculateMA(historicalPrices, 5),
      ma20: this.calculateMA(historicalPrices, 20),
      rsi: this.calculateRSI(historicalPrices),
      macd: this.calculateMACD(historicalPrices),
      score: 0,
      signals: []
    };
    
    // 计算技术分析得分
    let score = 0;
    
    // MA信号
    if (analysis.ma5 && analysis.ma20) {
      if (analysis.ma5 > analysis.ma20) {
        score += 20;
        analysis.signals.push('MA金叉信号');
      } else {
        score -= 10;
        analysis.signals.push('MA死叉信号');
      }
    }
    
    // RSI信号
    if (analysis.rsi) {
      if (analysis.rsi < 30) {
        score += 15;
        analysis.signals.push('RSI超卖信号');
      } else if (analysis.rsi > 70) {
        score -= 15;
        analysis.signals.push('RSI超买信号');
      }
    }
    
    // 价格趋势
    const currentPrice = stockData.price;
    if (analysis.ma20 && currentPrice > analysis.ma20) {
      score += 10;
      analysis.signals.push('价格在MA20之上');
    }
    
    analysis.score = Math.max(0, Math.min(100, score + 50));
    
    return analysis;
  }
}

// AI决策引擎
class AIDecisionEngine {
  constructor(stockDataManager) {
    this.stockDataManager = stockDataManager;
    this.portfolio = new Map(); // 当前持仓
    this.tradingHistory = [];   // 交易历史
    this.riskMetrics = {
      totalRisk: 0,
      positionRisk: new Map(),
      dailyTrades: 0
    };
  }
  
  // 分析单只股票
  async analyzeStock(stockCode) {
    const stockData = this.stockDataManager.getStockData(stockCode);
    if (!stockData) {
      throw new Error(`股票数据不存在: ${stockCode}`);
    }
    
    // ❌ 拒绝使用模拟历史价格数据
    throw new Error('❌ 拒绝使用模拟历史价格数据！系统要求使用真实数据源');
    
    // 技术分析
    const technicalAnalysis = TechnicalAnalyzer.analyzeTechnical(stockData, historicalPrices);
    
    // 基本面分析
    const fundamentalAnalysis = this.analyzeFundamental(stockData);
    
    // 综合评分
    const overallScore = this.calculateOverallScore(technicalAnalysis, fundamentalAnalysis);
    
    return {
      code: stockCode,
      name: stockData.name,
      currentPrice: stockData.price,
      change: stockData.change,
      technical: technicalAnalysis,
      fundamental: fundamentalAnalysis,
      overallScore: overallScore,
      recommendation: this.generateRecommendation(overallScore),
      timestamp: new Date().toISOString()
    };
  }
  
  // 基本面分析
  analyzeFundamental(stockData) {
    const analysis = {
      pe_ratio: stockData.pe_ratio,
      pb_ratio: stockData.pb_ratio,
      score: 0,
      signals: []
    };
    
    let score = 50; // 基础分数
    
    // PE分析
    if (stockData.pe_ratio < 15) {
      score += 15;
      analysis.signals.push('PE估值偏低');
    } else if (stockData.pe_ratio > 30) {
      score -= 15;
      analysis.signals.push('PE估值偏高');
    }
    
    // PB分析
    if (stockData.pb_ratio < 1) {
      score += 10;
      analysis.signals.push('PB估值偏低');
    } else if (stockData.pb_ratio > 3) {
      score -= 10;
      analysis.signals.push('PB估值偏高');
    }
    
    analysis.score = Math.max(0, Math.min(100, score));
    
    return analysis;
  }
  
  // 计算综合评分
  calculateOverallScore(technical, fundamental) {
    const techWeight = 0.6;
    const fundWeight = 0.4;
    
    return Math.round(technical.score * techWeight + fundamental.score * fundWeight);
  }
  
  // 生成投资建议
  generateRecommendation(score) {
    if (score >= 80) {
      return { action: 'strong_buy', confidence: 0.9, reason: '强烈买入信号' };
    } else if (score >= 65) {
      return { action: 'buy', confidence: 0.7, reason: '买入信号' };
    } else if (score >= 45) {
      return { action: 'hold', confidence: 0.5, reason: '持有观望' };
    } else if (score >= 30) {
      return { action: 'sell', confidence: 0.7, reason: '卖出信号' };
    } else {
      return { action: 'strong_sell', confidence: 0.9, reason: '强烈卖出信号' };
    }
  }
  
  // ❌ 已禁用模拟历史价格生成
  generateMockHistoricalPrices(currentPrice, days = 30) {
    throw new Error('❌ 模拟历史价格生成已被禁用！系统要求使用真实数据源');
  }
  
  // 批量分析
  async analyzeMultipleStocks(stockCodes) {
    const analyses = [];
    
    for (const code of stockCodes) {
      try {
        const analysis = await this.analyzeStock(code);
        analyses.push(analysis);
      } catch (error) {
        console.error(`❌ 分析股票${code}失败:`, error);
      }
    }
    
    // 按评分排序
    analyses.sort((a, b) => b.overallScore - a.overallScore);
    
    return analyses;
  }
  
  // 生成交易决策
  generateTradingDecisions(analyses, availableCash) {
    const decisions = [];
    const maxPositionValue = availableCash * AI_CONFIG.risk_control.max_position_ratio;
    
    for (const analysis of analyses) {
      const recommendation = analysis.recommendation;
      
      if (recommendation.action === 'strong_buy' || recommendation.action === 'buy') {
        const quantity = Math.floor(maxPositionValue / analysis.currentPrice / 100) * 100;
        
        if (quantity > 0) {
          decisions.push({
            action: 'buy',
            code: analysis.code,
            name: analysis.name,
            price: analysis.currentPrice,
            quantity: quantity,
            confidence: recommendation.confidence,
            reason: recommendation.reason,
            expectedReturn: this.calculateExpectedReturn(analysis),
            riskLevel: this.calculateRiskLevel(analysis)
          });
        }
      }
    }
    
    return decisions.slice(0, AI_CONFIG.risk_control.max_daily_trades);
  }
  
  // 计算预期收益
  calculateExpectedReturn(analysis) {
    const score = analysis.overallScore;
    return (score - 50) / 100; // 简化计算
  }
  
  // 计算风险等级
  calculateRiskLevel(analysis) {
    const volatility = Math.abs(analysis.change) / analysis.currentPrice;
    
    if (volatility < 0.02) return 'low';
    if (volatility < 0.05) return 'medium';
    return 'high';
  }
}

// 主AI分析引擎
class AIAnalysisEngine {
  constructor() {
    this.stockDataManager = new StockDataManager();
    this.decisionEngine = new AIDecisionEngine(this.stockDataManager);
    this.isRunning = false;
  }
  
  // 启动引擎
  async start() {
    console.log('🚀 启动AI分析引擎...');
    
    // 连接股票数据源
    const connected = await this.stockDataManager.connect();
    if (!connected) {
      throw new Error('无法连接股票数据源');
    }
    
    this.isRunning = true;
    console.log('✅ AI分析引擎启动成功');
    
    return true;
  }
  
  // 停止引擎
  stop() {
    this.isRunning = false;
    console.log('⏹️ AI分析引擎已停止');
  }
  
  // 执行分析
  async performAnalysis(options = {}) {
    if (!this.isRunning) {
      throw new Error('AI分析引擎未启动');
    }
    
    const stockCodes = options.stockCodes || ['000001', '000002'];
    const availableCash = options.availableCash || 100000;
    
    console.log('🧠 开始AI分析...');
    
    // 分析股票
    const analyses = await this.decisionEngine.analyzeMultipleStocks(stockCodes);
    
    // 生成交易决策
    const decisions = this.decisionEngine.generateTradingDecisions(analyses, availableCash);
    
    const result = {
      timestamp: new Date().toISOString(),
      analyses: analyses,
      decisions: decisions,
      summary: {
        totalAnalyzed: analyses.length,
        totalDecisions: decisions.length,
        avgScore: analyses.reduce((sum, a) => sum + a.overallScore, 0) / analyses.length,
        riskLevel: this.calculateOverallRisk(decisions)
      }
    };
    
    console.log('✅ AI分析完成');
    return result;
  }
  
  // 计算整体风险
  calculateOverallRisk(decisions) {
    if (decisions.length === 0) return 'none';
    
    const riskLevels = decisions.map(d => d.riskLevel);
    const highRiskCount = riskLevels.filter(r => r === 'high').length;
    const mediumRiskCount = riskLevels.filter(r => r === 'medium').length;
    
    if (highRiskCount > decisions.length * 0.5) return 'high';
    if (mediumRiskCount > decisions.length * 0.5) return 'medium';
    return 'low';
  }
  
  // 获取实时数据
  getRealTimeData() {
    return this.stockDataManager.getAllStockData();
  }
  
  // 订阅实时数据
  subscribeToRealTimeData(callback) {
    return this.stockDataManager.subscribe(callback);
  }
}

// 导出
export {
  AIAnalysisEngine,
  StockDataManager,
  TechnicalAnalyzer,
  AIDecisionEngine,
  STOCK_API_CONFIG,
  AI_CONFIG
};

export default AIAnalysisEngine;
