/**
 * Cloud Intelligent Agent Worker - Clean Deployment Version
 * Deployed on Cloudflare Workers, providing complete intelligent trading services
 * Includes: Real-time data reception, intelligent analysis, decision engine, trading instruction transmission
 */

// ChaguBang connection configuration
const CHAGUBANG_CONFIG = {
  host: 'l1.chagubang.com',
  port: 6380,
  token: 'QT_wat5QfcJ6N9pDZM5'
};

// Global variables
let stockDataCache = new Map();
let cloudAgent = null;
let tradingBridge = null;
let dataManager = null;

/**
 * Cloud Intelligent Agent
 */
class CloudIntelligentAgent {
  constructor() {
    this.name = 'CloudIntelligentAgent';
    this.version = '2.0.0';
    this.decisionHistory = [];
    this.stats = {
      totalDecisions: 0,
      buySignals: 0,
      sellSignals: 0,
      holdSignals: 0,
      avgConfidence: 0
    };
  }

  async performCloudIntelligentAnalysis(requestData) {
    try {
      console.log('Starting cloud intelligent analysis...');

      const { stockData, marketContext } = requestData;

      // 1. Real-time market analysis
      const marketAnalysis = this.analyzeRealTimeMarket(stockData, marketContext);

      // 2. Intelligent risk assessment
      const riskAssessment = this.assessIntelligentRisk(stockData, marketContext);

      // 3. Generate final decision
      const finalDecision = this.generateIntelligentDecision(marketAnalysis, riskAssessment);

      // 4. Record decision
      this.recordDecision(finalDecision);

      console.log(`Cloud intelligent analysis completed: ${finalDecision.action} (confidence: ${finalDecision.confidence.toFixed(3)})`);

      return {
        success: true,
        decision: finalDecision,
        analysis: { marketAnalysis, riskAssessment },
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      console.error('Cloud intelligent analysis failed:', error);
      return {
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  analyzeRealTimeMarket(stockData, marketContext) {
    const { price, change_percent, volume, high, low, open, prev_close } = stockData;
    const { risingCount, fallingCount, totalStocks, hotStocks } = marketContext;

    // 1. Technical indicator analysis (integrated existing strategies)
    const technicalAnalysis = this.performTechnicalAnalysis(stockData);

    // 2. Candlestick pattern recognition (integrated existing pattern strategies)
    const candlePatterns = this.identifyCandlePatterns(stockData);

    // 3. Volume-price relationship analysis
    const volumePriceAnalysis = this.analyzeVolumePriceRelationship(stockData);

    // 4. Market sentiment analysis
    const marketSentiment = this.analyzeMarketSentiment(marketContext);

    // 5. Six Sword Strategy analysis
    const sixSwordAnalysis = this.applySixSwordStrategy(stockData);

    // 6. Compass Strategy analysis
    const compassAnalysis = this.applyCompassStrategy(stockData);

    // 7. JiuFang Strategy analysis
    const jiuFangAnalysis = this.applyJiuFangStrategy(stockData);

    // 8. Limit Up Double Negative Strategy analysis
    const limitUpDoubleNegativeAnalysis = this.applyLimitUpDoubleNegativeStrategy(stockData);

    // Comprehensive scoring (integrating all strategies)
    const marketScore = this.calculateIntegratedMarketScore({
      technicalAnalysis,
      candlePatterns,
      volumePriceAnalysis,
      marketSentiment,
      sixSwordAnalysis,
      compassAnalysis,
      jiuFangAnalysis,
      limitUpDoubleNegativeAnalysis
    });

    return {
      marketScore,
      technicalAnalysis,
      candlePatterns,
      volumePriceAnalysis,
      marketSentiment,
      sixSwordAnalysis,
      compassAnalysis,
      jiuFangAnalysis,
      limitUpDoubleNegativeAnalysis,
      signal: this.determineIntegratedSignal(marketScore),
      confidence: this.calculateIntegratedConfidence(marketScore, technicalAnalysis)
    };
  }

  assessIntelligentRisk(stockData, marketContext) {
    const { change_percent, volume } = stockData;

    // Volatility risk
    const volatilityRisk = Math.min(Math.abs(change_percent) / 10, 1.0);

    // Liquidity risk
    const liquidityRisk = volume < 500000 ? 0.8 : volume < 1000000 ? 0.5 : 0.2;

    // Market risk
    const marketRisk = Math.abs(marketContext.averageChange || 0) / 5;

    // Comprehensive risk score
    const totalRiskScore = (volatilityRisk + liquidityRisk + marketRisk) / 3;

    return {
      totalRiskScore,
      riskLevel: totalRiskScore > 0.7 ? 'HIGH' : totalRiskScore > 0.4 ? 'MEDIUM' : 'LOW',
      riskApproved: totalRiskScore < 0.7
    };
  }

  generateIntelligentDecision(marketAnalysis, riskAssessment) {
    const { marketScore, signal, confidence } = marketAnalysis;
    const { riskApproved, totalRiskScore } = riskAssessment;

    // Final confidence
    const finalConfidence = confidence * (1 - totalRiskScore);

    // Decision logic
    let action = 'HOLD';
    if (finalConfidence > 0.6 && riskApproved) {
      action = signal;
    }

    const decision = {
      action,
      confidence: finalConfidence,
      shouldTrade: finalConfidence > 0.6 && riskApproved && action !== 'HOLD',
      reasoning: this.generateReasoning(marketAnalysis, riskAssessment),
      tradeParams: {
        symbol: '000001', // Example
        quantity: Math.floor(1000 * finalConfidence),
        orderType: 'LIMIT'
      },
      timestamp: new Date().toISOString()
    };

    return decision;
  }

  generateReasoning(marketAnalysis, riskAssessment) {
    const { marketScore, signal } = marketAnalysis;
    const { riskLevel } = riskAssessment;

    return `Market score: ${marketScore.toFixed(3)}, Signal: ${signal}, Risk level: ${riskLevel}`;
  }

  // ==================== Technical Indicator Analysis ====================

  performTechnicalAnalysis(stockData) {
    const { price, high, low, open, prev_close, volume } = stockData;

    // RSI calculation
    const rsi = this.calculateRSI(price, prev_close);

    // MACD calculation
    const macd = this.calculateMACD(price, prev_close);

    // Bollinger calculation
    const bollinger = this.calculateBollinger(price, high, low);

    // KDJ calculation
    const kdj = this.calculateKDJ(high, low, price);

    // Williams R calculation
    const williamsR = this.calculateWilliamsR(high, low, price);

    // Moving average
    const ma = this.calculateMA(price);

    return {
      rsi: { value: rsi, signal: rsi < 30 ? 'BUY' : rsi > 70 ? 'SELL' : 'HOLD' },
      macd: { value: macd, signal: macd > 0 ? 'BUY' : 'SELL' },
      bollinger: {
        position: bollinger,
        signal: bollinger < 0.2 ? 'BUY' : bollinger > 0.8 ? 'SELL' : 'HOLD'
      },
      kdj: { value: kdj, signal: kdj < 20 ? 'BUY' : kdj > 80 ? 'SELL' : 'HOLD' },
      williamsR: {
        value: williamsR,
        signal: williamsR < -80 ? 'BUY' : williamsR > -20 ? 'SELL' : 'HOLD'
      },
      ma: { value: ma, signal: price > ma ? 'BUY' : 'SELL' }
    };
  }

  // ==================== Candlestick Pattern Recognition ====================

  identifyCandlePatterns(stockData) {
    const { open, high, low, price: close, prev_close } = stockData;

    const patterns = {
      doji: this.isDoji(open, high, low, close),
      hammer: this.isHammer(open, high, low, close),
      shootingStar: this.isShootingStar(open, high, low, close),
      engulfing: this.isEngulfing(open, high, low, close, prev_close),
      morningStar: this.isMorningStar(stockData),
      darkCloudCover: this.isDarkCloudCover(stockData),
      threeWhiteSoldiers: this.isThreeWhiteSoldiers(stockData),
      threeBlackCrows: this.isThreeBlackCrows(stockData),
      risingObstacle: this.isRisingObstacle(stockData),
      doubleBlackCrows: this.isDoubleBlackCrows(stockData)
    };

    // Calculate pattern strength
    const patternStrength = this.calculatePatternStrength(patterns);

    return {
      patterns,
      strength: patternStrength,
      signal: this.determinePatternSignal(patterns, patternStrength)
    };
  }
