/**
 * 策略AI模块
 * 整合不同策略系统的输出,并提供智能决策建议
 */

import SixSwordStrategy from '../strategies/sixSwordStrategy.js';
import JiuFangStrategy from '../strategies/jiuFangStrategy.js';
import CompassStrategy from '../strategies/compassStrategy.js';
import WilliamsRStrategy from '../strategies/williamsRStrategy.js';
import LearningEngine from './learningEngine.js';

/**
 * 策略AI类
 * 负责整合并管理各种交易策略
 */
class StrategyAI {
  constructor(options = {}) {
    // 初始化策略组件
    this.sixSwordStrategy = new SixSwordStrategy();
    this.jiuFangStrategy = new JiuFangStrategy();
    this.compassStrategy = new CompassStrategy();
    this.williamsRStrategy = new WilliamsRStrategy();
    
    // 设置风险偏好
    this.riskProfile = options.riskProfile || 'moderate'; // conservative, moderate, aggressive
    
    // 设置初始权重
    this.weights = {
      sixSword: 0.3,
      jiuFang: 0.25,
      compass: 0.25,
      williamsR: 0.2
    };
    
    // 学习记录
    this.learningHistory = [];
    
    // 策略表现跟踪
    this.strategyPerformance = {
      sixSword: { wins: 0, losses: 0 },
      jiuFang: { wins: 0, losses: 0 },
      compass: { wins: 0, losses: 0 },
      williamsR: { wins: 0, losses: 0 }
    };
    
    // 初始化市场状态感知
    this.marketAwareness = options.marketAwareness || true;
    
    // 历史决策记录
    this.decisionHistory = [];
    
    // 交易策略列表
    this.strategies = [];
    
    // 策略权重
    this.strategyWeights = {
      sixSword: 0.35,  // 六脉神剑
      jiuFang: 0.35,   // 九方智投
      compass: 0.30    // 指南针
    };
    
    // 初始化学习引擎
    this.learningEngine = new LearningEngine();
    
    // 是否已应用学习优化
    this.learningOptimized = false;
    
    // 股票特性记忆库
    this.stockCharacteristics = {};
  }

  /**
   * 添加策略
   * @param {Object} strategy 交易策略
   * @param {Number} weight 权重
   */
  addStrategy(strategy, weight) {
    this.strategies.push({
      strategy,
      weight
    });
  }
  
  /**
   * 设置策略权重
   * @param {String} strategyName 策略名称
   * @param {Number} weight 权重
   */
  setStrategyWeight(strategyName, weight) {
    this.strategyWeights[strategyName] = weight;
  }
  
  /**
   * 批量设置策略权重
   * @param {Object} weights 策略权重配置
   */
  setStrategyWeights(weights) {
    Object.keys(weights).forEach(strategy => {
      if (this.strategyWeights.hasOwnProperty(strategy)) {
        this.strategyWeights[strategy] = weights[strategy];
      }
    });
  }

  /**
   * 分析股票并给出建议
   * @param {Object} stockData 股票数据
   * @returns {Object} 分析结果和建议
   */
  analyzeStock(stockData) {
    // 根据股票特性调整策略权重
    this.adjustWeightsForSpecificStock(stockData.code);
    
    // 根据市场状况调整策略权重
    this.adjustWeightsBasedOnMarket(stockData);
    
    // 策略分析结果
    const strategyResults = {
      sixSword: null,  // 六脉神剑策略分析结果
      jiuFang: null,   // 九方智投策略分析结果
      compass: null    // 指南针策略分析结果
    };
    
    // 执行各个策略的分析
    this.strategies.forEach(({ strategy }) => {
      const result = strategy.analyze(stockData);
      strategyResults[strategy.name] = result;
    });
    
    // 根据权重综合各策略的结果
    const decision = this.makeDecision(strategyResults);
    
    // 整合分析结果
    const analysisResult = {
      decision,
      overallScore: decision.score,
      strategyResults,
      weights: { ...this.strategyWeights }
    };
    
    return analysisResult;
  }

  /**
   * 根据市场状况调整策略权重
   * @param {Object} stockData 股票数据
   */
  adjustWeightsBasedOnMarket(stockData) {
    // 计算市场波动性
    const volatility = this.calculateMarketVolatility(stockData);
    
    // 根据波动性调整权重
    if (volatility === 'high') {
      // 高波动性市场,增加形态识别和技术分析的权重
      this.weights.jiuFang += 0.05;
      this.weights.compass += 0.05;
      this.weights.williamsR += 0.05;
      this.weights.sixSword -= 0.15;
    } else if (volatility === 'low') {
      // 低波动性市场,增加趋势跟踪的权重
      this.weights.sixSword += 0.1;
      this.weights.williamsR += 0.05;
      this.weights.jiuFang -= 0.05;
      this.weights.compass -= 0.1;
    }
    
    // 确保权重总和为1
    const totalWeight = this.weights.sixSword + this.weights.jiuFang + this.weights.compass + this.weights.williamsR;
    this.weights.sixSword /= totalWeight;
    this.weights.jiuFang /= totalWeight;
    this.weights.compass /= totalWeight;
    this.weights.williamsR /= totalWeight;
  }

  /**
   * 计算综合评分
   * @param {Number} sixSwordScore 六脉神剑评分
   * @param {Array} jiuFangPatterns 九方智投识别的形态
   * @param {Number} compassScore 指南针评分
   * @returns {Number} 综合评分
   */
  calculateOverallScore(sixSwordScore, jiuFangPatterns, compassScore) {
    // 计算九方智投的评分
    let jiuFangScore = 50; // 默认中性评分
    
    if (jiuFangPatterns.length > 0) {
      // 根据检测到的形态计算评分
      let patternScore = 0;
      let totalConfidence = 0;
      
      jiuFangPatterns.forEach(pattern => {
        const directionScore = pattern.direction === 'bullish' ? 1 : 
                              pattern.direction === 'bearish' ? -1 : 0;
        patternScore += directionScore * pattern.confidence * 100;
        totalConfidence += pattern.confidence;
      });
      
      // 归一化到0-100区间
      if (totalConfidence > 0) {
        jiuFangScore = 50 + (patternScore / totalConfidence) / 2;
        jiuFangScore = Math.min(100, Math.max(0, jiuFangScore));
      }
    }
    
    // 根据权重计算综合评分
    return (
      this.weights.sixSword * sixSwordScore +
      this.weights.jiuFang * jiuFangScore +
      this.weights.compass * compassScore
    );
  }

  /**
   * 根据综合评分和风险偏好做出决策
   * @param {Number} overallScore 综合评分
   * @param {Object} results 各策略系统的结果
   * @returns {Object} 决策建议
   */
  makeDecision(strategyResults) {
    // 综合评分
    let overallScore = 0;
    
    // 买入信号计数
    let buySignals = 0;
    
    // 卖出信号计数
    let sellSignals = 0;
    
    // 各个策略的具体建议和评分,用于生成详细理由
    const strategyDetails = {};
    
    // 计算综合得分和信号统计
    Object.keys(this.strategyWeights).forEach(strategy => {
      if (strategyResults[strategy]) {
        // 策略权重
        const weight = this.strategyWeights[strategy];
        
        // 策略评分
        const score = strategyResults[strategy].overallScore || 0;
        
        // 加权计算
        overallScore += score * weight;
        
        // 保存策略详情用于生成理由
        strategyDetails[strategy] = {
          score: score,
          weight: weight,
          weightedScore: score * weight,
          recommendation: strategyResults[strategy].recommendation?.action || '未知',
          details: strategyResults[strategy].strategies || strategyResults[strategy].signals || {}
        };
        
        // 统计买卖信号
        const action = strategyResults[strategy].recommendation?.action;
        
        if (action === '建议买入' || action === '强烈推荐') {
          buySignals++;
        } else if (action === '建议卖出' || action === '建议减仓') {
          sellSignals++;
        }
      }
    });
    
    // 确定操作方向
    let action = 'hold';  // 默认持有
    let confidence = 'low';  // 默认低信心
    let allocation = 0;
    
    // 根据综合评分和信号确定操作
    if (overallScore >= 75) {
      action = 'strong_buy';
      confidence = 'high';
      allocation = 0.8;
    } else if (overallScore >= 60) {
      action = 'buy';
      confidence = 'medium';
      allocation = 0.5;
    } else if (overallScore <= 30) {
      action = 'strong_sell';
      confidence = 'high';
      allocation = 0;
    } else if (overallScore <= 40) {
      action = 'sell';
      confidence = 'medium';
      allocation = 0.2;
    } else {
      // 在中间区域,根据信号确定
      if (buySignals > sellSignals) {
        action = 'buy';
        confidence = 'low';
        allocation = 0.3;
      } else if (sellSignals > buySignals) {
        action = 'sell';
        confidence = 'low';
        allocation = 0.2;
      }
    }
    
    // 生成决策描述
    let description = '';
    if (action === 'strong_buy') {
      description = '多项指标显示强烈买入信号,市场走势非常有利。';
    } else if (action === 'buy') {
      description = '大部分指标显示积极信号,市场走势向好。';
    } else if (action === 'hold') {
      description = '指标显示混合信号,建议持有观望。';
    } else if (action === 'sell') {
      description = '多项指标显示卖出信号,市场可能面临调整。';
    } else if (action === 'strong_sell') {
      description = '多项指标显示强烈卖出信号,市场走势不利。';
    }
    
    // 生成详细理由
    const detailedReasons = this.generateDetailedReasons(strategyDetails, action, overallScore);
    
    // 指标信号详情
    const signalDetails = this.extractKeySignals(strategyDetails);
    
    return {
      action,
      confidence,
      allocation,
      score: overallScore,
      description,
      detailedReasons,
      signalDetails,
      buySignals,
      sellSignals,
      strategyDetails
    };
  }

  /**
   * 生成详细的交易决策理由
   * @param {Object} strategyDetails 各策略详情
   * @param {String} action 决策动作
   * @param {Number} overallScore 综合评分
   * @returns {String} 详细理由
   */
  generateDetailedReasons(strategyDetails, action, overallScore) {
    // 获取最主要贡献的策略(得分最高的两个策略)
    const topStrategies = Object.entries(strategyDetails)
      .sort((a, b) => b[1].weightedScore - a[1].weightedScore)
      .slice(0, 2);
    
    // 基于顶级策略和具体指标生成详细理由
    let reasons = '';
    
    // 首先添加总体决策原因
    if (action === 'strong_buy' || action === 'buy') {
      reasons += `综合评分 ${Math.round(overallScore)} 分,显示较强的买入信号。`;
    } else if (action === 'strong_sell' || action === 'sell') {
      reasons += `综合评分 ${Math.round(overallScore)} 分,显示较强的卖出信号。`;
    } else {
      reasons += `综合评分 ${Math.round(overallScore)} 分,市场信号中性。`;
    }
    
    // 添加顶级策略的详细理由
    reasons += ' 主要依据:';
    
    topStrategies.forEach(([strategyName, details], index) => {
      const strategyDisplayName = this.getStrategyDisplayName(strategyName);
      const contribution = Math.round(details.weight * 100);
      
      reasons += `${index > 0 ? ',' : ''}${strategyDisplayName}(贡献${contribution}%)`;
      
      // 添加该策略的关键指标
      if (strategyName === 'sixSword' && details.details) {
        // 六脉神剑策略特有的详情解析
        if (details.details.tian && details.details.tian.signals) {
          const tianSignals = details.details.tian.signals;
          if (tianSignals.breakMA20) reasons += '突破20日均线';
          if (tianSignals.breakMA60) reasons += '突破60日均线';
          if (tianSignals.breakBox) reasons += '突破箱体';
        }
        
        if (details.details.di && details.details.di.signals) {
          const diSignals = details.details.di.signals;
          if (diSignals.bounceFromLower) reasons += '支撑位反弹';
          if (diSignals.fallFromUpper) reasons += '阻力位回落';
        }
      } else if (strategyName === 'jiuFang' && details.details) {
        // 九方智投策略特有的详情解析
        const patterns = details.details.patterns || [];
        if (patterns.length > 0) {
          reasons += `识别出${patterns[0].name}形态`;
        }
      } else if (strategyName === 'compass' && details.details) {
        // 指南针策略特有的详情解析
        const trends = details.details.trends || {};
        if (trends.macdTrend) reasons += `MACD${trends.macdTrend === 'up' ? '上升' : '下降'}`;
        if (trends.rsiTrend) reasons += `RSI${trends.rsiTrend === 'up' ? '上升' : '下降'}`;
      }
    });
    
    // 添加风险提示
    if (action === 'strong_buy' || action === 'buy') {
      reasons += '。需注意:投资有风险,AI建议仅供参考,请结合自身风险承受能力决策。';
    } else if (action === 'strong_sell' || action === 'sell') {
      reasons += '。需注意:卖出决策可能导致错过后续上涨行情,请综合考虑。';
    }
    
    return reasons;
  }

  /**
   * 获取策略的显示名称
   * @param {String} strategyKey 策略键名
   * @returns {String} 显示名称
   */
  getStrategyDisplayName(strategyKey) {
    const nameMap = {
      sixSword: '六脉神剑',
      jiuFang: '九方智投',
      compass: '指南针',
      williamsR: '威廉指标'
    };
    
    return nameMap[strategyKey] || strategyKey;
  }

  /**
   * 提取关键指标信号
   * @param {Object} strategyDetails 策略详情
   * @returns {Object} 关键指标信号
   */
  extractKeySignals(strategyDetails) {
    const signals = {
      technical: [], // 技术指标信号
      pattern: [],   // 形态信号
      trend: [],     // 趋势信号
      volume: []     // 量价信号
    };
    
    // 解析六脉神剑策略信号
    if (strategyDetails.sixSword && strategyDetails.sixSword.details) {
      const sixSwordDetails = strategyDetails.sixSword.details;
      
      // 天字诀 - 趋势突破
      if (sixSwordDetails.tian) {
        if (sixSwordDetails.tian.signals.breakMA20) {
          signals.technical.push({ name: '突破MA20', type: 'bullish' });
        }
        if (sixSwordDetails.tian.signals.breakMA60) {
          signals.technical.push({ name: '突破MA60', type: 'bullish' });
        }
        if (sixSwordDetails.tian.signals.breakBox) {
          signals.pattern.push({ name: '箱体突破', type: 'bullish' });
        }
      }
      
      // 地字诀 - 支撑阻力
      if (sixSwordDetails.di) {
        if (sixSwordDetails.di.signals.bounceFromLower) {
          signals.technical.push({ name: '支撑位反弹', type: 'bullish' });
        }
        if (sixSwordDetails.di.signals.fallFromUpper) {
          signals.technical.push({ name: '阻力位回落', type: 'bearish' });
        }
      }
      
      // 人字诀 - 量价关系
      if (sixSwordDetails.ren) {
        if (sixSwordDetails.ren.signals.volumeUpWithPrice) {
          signals.volume.push({ name: '放量上涨', type: 'bullish' });
        }
        if (sixSwordDetails.ren.signals.volumeDownWithPrice) {
          signals.volume.push({ name: '缩量下跌', type: 'bearish' });
        }
      }
    }
    
    // 解析九方智投策略信号
    if (strategyDetails.jiuFang && strategyDetails.jiuFang.details && strategyDetails.jiuFang.details.patterns) {
      strategyDetails.jiuFang.details.patterns.forEach(pattern => {
        signals.pattern.push({
          name: pattern.name,
          type: pattern.direction === 'bullish' ? 'bullish' : 'bearish',
          confidence: pattern.confidence
        });
      });
    }
    
    // 解析指南针策略信号
    if (strategyDetails.compass && strategyDetails.compass.details) {
      const compassDetails = strategyDetails.compass.details;
      
      if (compassDetails.macd) {
        signals.technical.push({
          name: 'MACD',
          type: compassDetails.macd.histogram > 0 ? 'bullish' : 'bearish'
        });
      }
      
      if (compassDetails.rsi) {
        if (compassDetails.rsi.value < 30) {
          signals.technical.push({ name: 'RSI超卖', type: 'bullish' });
        } else if (compassDetails.rsi.value > 70) {
          signals.technical.push({ name: 'RSI超买', type: 'bearish' });
        }
      }
    }
    
    return signals;
  }

  /**
   * 根据风险偏好获取决策阈值
   * @returns {Object} 决策阈值
   */
  getThresholdsByRiskProfile() {
    switch (this.riskProfile) {
      case 'conservative':
        return {
          strongBuy: 80, // 保守型投资者需要更高的确信度才会强烈买入
          buy: 65,
          hold: 45,
          sell: 35,
          strongSell: 20
        };
      case 'aggressive':
        return {
          strongBuy: 70, // 激进型投资者在较低确信度时也会考虑强烈买入
          buy: 55,
          hold: 40,
          sell: 30,
          strongSell: 15
        };
      case 'moderate':
      default:
        return {
          strongBuy: 75,
          buy: 60,
          hold: 45,
          sell: 35,
          strongSell: 20
        };
    }
  }

  /**
   * 计算建议仓位比例
   * @param {Number} score 评分
   * @param {String} actionType 操作类型
   * @returns {Number} 建议仓位比例
   */
  calculateAllocation(score, actionType) {
    if (actionType === 'buy') {
      // 买入仓位:根据评分和风险偏好计算
      let baseAllocation;
      
      if (score >= 90) {
        baseAllocation = 1.0; // 满仓
      } else if (score >= 80) {
        baseAllocation = 0.8;
      } else if (score >= 70) {
        baseAllocation = 0.6;
      } else {
        baseAllocation = 0.3;
      }
      
      // 根据风险偏好调整
      const riskMultiplier = this.riskProfile === 'conservative' ? 0.7 :
                           this.riskProfile === 'aggressive' ? 1.3 : 1.0;
      
      return Math.min(1.0, baseAllocation * riskMultiplier);
    } else {
      // 卖出仓位:根据评分计算要卖出的仓位比例
      if (score <= 10) {
        return 1.0; // 清仓
      } else if (score <= 20) {
        return 0.8;
      } else if (score <= 30) {
        return 0.5;
      } else {
        return 0.3;
      }
    }
  }

  /**
   * 生成详细分析描述
   * @param {Object} results 各策略系统的结果
   * @returns {String} 详细分析描述
   */
  generateDetailedAnalysis(results) {
    let analysis = '';
    
    // 添加六脉神剑分析
    if (results.sixSwordResult && results.sixSwordResult.recommendation) {
      analysis += ` 六脉神剑分析:${results.sixSwordResult.recommendation.description}`;
    }
    
    // 添加九方智投形态分析
    if (results.jiuFangResult && results.jiuFangResult.summary) {
      analysis += ` 九方智投形态分析:${results.jiuFangResult.summary.description}`;
    }
    
    // 添加指南针分析
    if (results.compassResult && results.compassResult.recommendation) {
      analysis += ` 指南针分析:${results.compassResult.recommendation.description}`;
    }
    
    return analysis;
  }

  /**
   * 记录决策历史
   * @param {Object} decision 决策
   * @param {Object} stockData 股票数据
   */
  recordDecision(decision, stockData) {
    this.decisionHistory.push({
      timestamp: new Date(),
      price: stockData.prices[stockData.prices.length - 1],
      decision: decision,
      weights: { ...this.weights }
    });
    
    // 限制历史记录长度
    if (this.decisionHistory.length > 100) {
      this.decisionHistory.shift();
    }
  }

  /**
   * 设置风险偏好
   * @param {String} profile 风险偏好
   */
  setRiskProfile(profile) {
    if (['conservative', 'moderate', 'aggressive'].includes(profile)) {
      this.riskProfile = profile;
    }
  }

  /**
   * 手动调整策略权重
   * @param {Object} newWeights 新的权重
   */
  setWeights(newWeights) {
    // 验证权重
    const sum = newWeights.sixSword + newWeights.jiuFang + newWeights.compass + newWeights.williamsR;
    if (Math.abs(sum - 1) > 0.01) {
      throw new Error('权重总和必须为1');
    }
    
    this.weights = { ...newWeights };
  }

  /**
   * 计算市场波动性
   * @param {Object} stockData 股票数据
   * @returns {String} 波动性级别
   */
  calculateMarketVolatility(stockData) {
    const { prices } = stockData;
    const returns = [];
    
    // 计算日收益率
    for (let i = 1; i < prices.length; i++) {
      returns.push((prices[i] - prices[i - 1]) / prices[i - 1]);
    }
    
    // 计算标准差
    const mean = returns.reduce((sum, r) => sum + r, 0) / returns.length;
    const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length;
    const stdDev = Math.sqrt(variance);
    
    // 根据标准差判断波动性
    if (stdDev > 0.02) {
      return 'high';
    } else if (stdDev < 0.01) {
      return 'low';
    } else {
      return 'medium';
    }
  }

  /**
   * 获取决策历史
   * @returns {Array} 决策历史记录
   */
  getDecisionHistory() {
    return this.decisionHistory;
  }

  /**
   * 评估历史决策准确性
   * @param {Array} actualPrices 实际价格走势
   * @returns {Object} 评估结果
   */
  evaluateDecisions(actualPrices) {
    // 实际应用中,这里会实现一个评估算法
    // 比较历史决策与实际价格走势的关系
    
    return {
      accuracy: 0.75, // 示例值
      profitLoss: 0.15, // 示例值
      details: []
    };
  }

  /**
   * 生成综合解释
   * @param {Object} sixSwordResult 六剑奇门结果
   * @param {Object} jiuFangResult 九方智能结果
   * @param {Object} compassResult 指南针结果
   * @param {Object} williamsRResult 威廉指标结果
   * @param {Number} weightedScore 加权评分
   * @param {String} action 建议操作
   * @returns {String} 综合解释
   */
  generateInterpretation(sixSwordResult, jiuFangResult, compassResult, williamsRResult, weightedScore, action) {
    let interpretation = `综合评分:${Math.round(weightedScore)}分,`;
    
    if (action === "buy") {
      interpretation += "建议买入";
    } else if (action === "sell") {
      interpretation += "建议卖出";
    } else {
      interpretation += "建议观望";
    }
    
    interpretation += "。\n\n分策略评分:";
    interpretation += `\n六剑奇门:${Math.round(sixSwordResult.score)}分`;
    interpretation += `\n九方智能:${Math.round(jiuFangResult.score)}分`;
    interpretation += `\n指南针:${Math.round(compassResult.score)}分`;
    interpretation += `\n威廉指标:${Math.round(williamsRResult.score)}分`;
    
    interpretation += "\n\n详细分析:";
    if (weightedScore >= 70) {
      interpretation += "\n市场整体呈现上升趋势,多个交易策略显示买入信号。";
    } else if (weightedScore <= 30) {
      interpretation += "\n市场整体呈现下降趋势,多个交易策略显示卖出信号。";
    } else {
      interpretation += "\n市场整体呈现震荡,各策略信号不一致,建议观望或小仓位操作。";
    }
    
    // 添加威廉指标特定解读
    interpretation += `\n\n威廉指标分析:当前威廉指标(%R)14日值为${williamsRResult.indicator.williamsR14}。`;
    if (williamsRResult.signals.isOversold) {
      interpretation += "当前处于超卖区域,可能存在反弹机会。";
    } else if (williamsRResult.signals.isOverbought) {
      interpretation += "当前处于超买区域,可能存在回调风险。";
    }
    
    if (williamsRResult.signals.crossingFromOversold) {
      interpretation += "指标刚从超卖区域上穿,提供较强买入信号。";
    } else if (williamsRResult.signals.crossingFromOverbought) {
      interpretation += "指标刚从超买区域下穿,提供较强卖出信号。";
    }
    
    return interpretation;
  }

  /**
   * 记录交易结果
   * @param {Object} trade 交易记录
   */
  recordTradeResult(trade) {
    // 将交易记录传递给学习引擎
    this.learningEngine.recordTrade(trade);
  }
  
  /**
   * 优化策略配置
   * @returns {Object} 优化结果
   */
  optimizeStrategies() {
    // 如果交易记录不足,返回
    if (this.learningEngine.tradingHistory.length < 10) {
      return {
        success: false,
        message: "需要更多的交易数据才能开始优化"
      };
    }
    
    // 执行学习分析
    const learningResult = this.learningEngine.learn();
    
    if (!learningResult.success) {
      return learningResult;
    }
    
    // 获取优化建议
    const optimizationSuggestions = this.learningEngine.getOptimizationSuggestions();
    
    // 应用策略权重优化
    this.applyWeightOptimization(optimizationSuggestions.weightSuggestions);
    
    this.learningOptimized = true;
    
    return {
      success: true,
      message: "策略配置已优化",
      weights: this.strategyWeights,
      learningResults: learningResult.results,
      optimizationSuggestions
    };
  }
  
  /**
   * 应用权重优化
   * @param {Object} weightSuggestions 权重建议
   */
  applyWeightOptimization(weightSuggestions) {
    if (!weightSuggestions) return;
    
    // 更新策略权重
    Object.keys(weightSuggestions).forEach(strategy => {
      if (this.strategyWeights.hasOwnProperty(strategy)) {
        // 平滑更新权重,避免剧烈变化
        this.strategyWeights[strategy] = this.strategyWeights[strategy] * 0.3 + weightSuggestions[strategy] * 0.7;
      }
    });
    
    // 归一化权重,确保总和为1
    const totalWeight = Object.values(this.strategyWeights).reduce((sum, weight) => sum + weight, 0);
    
    if (totalWeight > 0) {
      Object.keys(this.strategyWeights).forEach(strategy => {
        this.strategyWeights[strategy] /= totalWeight;
      });
    }
  }
  
  /**
   * 获取学习引擎
   * @returns {LearningEngine} 学习引擎实例
   */
  getLearningEngine() {
    return this.learningEngine;
  }
  
  /**
   * 检查是否应该进行策略优化
   * @returns {Boolean} 是否应该优化
   */
  shouldOptimize() {
    // 检查交易记录数量是否增加了一定比例
    const tradingHistoryLength = this.learningEngine.tradingHistory.length;
    
    // 如果从未优化过且有足够的数据,应该优化
    if (!this.learningOptimized && tradingHistoryLength >= 10) {
      return true;
    }
    
    // 如果已优化过,且新增了25%以上的数据,应该重新优化
    if (this.learningOptimized && this.lastOptimizationSize && 
        tradingHistoryLength >= this.lastOptimizationSize * 1.25) {
      return true;
    }
    
    return false;
  }
  
  /**
   * 执行自动优化
   * @returns {Object} 优化结果
   */
  autoOptimize() {
    if (this.shouldOptimize()) {
      const result = this.optimizeStrategies();
      
      if (result.success) {
        this.lastOptimizationSize = this.learningEngine.tradingHistory.length;
      }
      
      return result;
    }
    
    return {
      success: false,
      message: "当前不需要优化"
    };
  }

  /**
   * 根据特定股票的特性调整策略权重
   * @param {String} stockCode 股票代码
   */
  adjustWeightsForSpecificStock(stockCode) {
    // 如果没有该股票的特性记录,使用默认权重
    if (!this.stockCharacteristics[stockCode]) {
      // 尝试从存储中加载此股票的特性记录
      try {
        const savedChar = uni.getStorageSync(`stock_characteristics_${stockCode}`);
        if (savedChar) {
          this.stockCharacteristics[stockCode] = savedChar;
        } else {
          // 没有历史记录,创建默认记录
          this.stockCharacteristics[stockCode] = {
            volatility: 'medium',
            tradingPattern: 'normal',
            sectorType: 'unknown',
            strategyEffectiveness: {
              sixSword: 0.5,
              jiuFang: 0.5,
              compass: 0.5,
              williamsR: 0.5
            },
            lastUpdated: new Date()
          };
          return; // 使用默认权重
        }
      } catch (error) {
        console.error('加载股票特性失败:', error);
        return; // 使用默认权重
      }
    }
    
    const stockChar = this.stockCharacteristics[stockCode];
    
    // 根据股票特性调整权重
    let weightsAdjustment = {
      sixSword: 0,
      jiuFang: 0, 
      compass: 0,
      williamsR: 0
    };
    
    // 根据波动性调整
    if (stockChar.volatility === 'high') {
      // 高波动性股票更适合技术指标和形态分析
      weightsAdjustment.jiuFang += 0.1;
      weightsAdjustment.williamsR += 0.05;
      weightsAdjustment.sixSword -= 0.1;
      weightsAdjustment.compass -= 0.05;
    } else if (stockChar.volatility === 'low') {
      // 低波动性股票更适合趋势跟踪
      weightsAdjustment.sixSword += 0.1;
      weightsAdjustment.compass += 0.05;
      weightsAdjustment.jiuFang -= 0.1;
      weightsAdjustment.williamsR -= 0.05;
    }
    
    // 根据交易模式调整
    if (stockChar.tradingPattern === 'ranging') {
      // 区间震荡股更适合支撑阻力和反转策略
      weightsAdjustment.jiuFang += 0.1;
      weightsAdjustment.williamsR += 0.1;
      weightsAdjustment.sixSword -= 0.15;
      weightsAdjustment.compass -= 0.05;
    } else if (stockChar.tradingPattern === 'trending') {
      // 趋势明显的股票适合趋势跟踪
      weightsAdjustment.sixSword += 0.15;
      weightsAdjustment.compass += 0.05;
      weightsAdjustment.jiuFang -= 0.1;
      weightsAdjustment.williamsR -= 0.1;
    }
    
    // 根据行业特性调整
    if (stockChar.sectorType === 'tech') {
      // 科技股通常波动较大,需要更敏感的技术指标
      weightsAdjustment.williamsR += 0.05;
      weightsAdjustment.jiuFang += 0.05;
    } else if (stockChar.sectorType === 'utilities') {
      // 公用事业股通常稳定,适合趋势和基本面
      weightsAdjustment.sixSword += 0.05;
      weightsAdjustment.compass += 0.05;
    }
    
    // 最重要的是根据历史策略有效性调整
    Object.keys(stockChar.strategyEffectiveness).forEach(strategy => {
      const effectiveness = stockChar.strategyEffectiveness[strategy];
      // 效果好的策略权重增加,效果差的减少
      if (effectiveness > 0.6) {
        weightsAdjustment[strategy] += 0.2 * (effectiveness - 0.6);
      } else if (effectiveness < 0.4) {
        weightsAdjustment[strategy] -= 0.2 * (0.4 - effectiveness);
      }
    });
    
    // 应用权重调整
    Object.keys(this.weights).forEach(strategy => {
      if (weightsAdjustment[strategy]) {
        this.weights[strategy] += weightsAdjustment[strategy];
      }
    });
    
    // 确保权重总和为1
    const totalWeight = Object.values(this.weights).reduce((sum, w) => sum + w, 0);
    Object.keys(this.weights).forEach(strategy => {
      this.weights[strategy] /= totalWeight;
    });
  }

  /**
   * 更新特定股票的特性记录
   * @param {String} stockCode 股票代码
   * @param {Object} tradeResult 交易结果
   */
  updateStockCharacteristics(stockCode, tradeResult) {
    // 确保有该股票的特性记录
    if (!this.stockCharacteristics[stockCode]) {
      this.stockCharacteristics[stockCode] = {
        volatility: 'medium',
        tradingPattern: 'normal',
        sectorType: 'unknown',
        strategyEffectiveness: {
          sixSword: 0.5,
          jiuFang: 0.5,
          compass: 0.5,
          williamsR: 0.5
        },
        lastUpdated: new Date()
      };
    }
    
    const stockChar = this.stockCharacteristics[stockCode];
    
    // 更新策略有效性
    if (tradeResult.strategyDetails) {
      Object.keys(tradeResult.strategyDetails).forEach(strategy => {
        if (!stockChar.strategyEffectiveness[strategy]) {
          stockChar.strategyEffectiveness[strategy] = 0.5; // 初始值
        }
        
        const strategyAction = tradeResult.strategyDetails[strategy].action;
        // 策略预测正确,提高有效性评分
        if ((strategyAction === 'buy' && tradeResult.result > 0) || 
            (strategyAction === 'sell' && tradeResult.result < 0)) {
          stockChar.strategyEffectiveness[strategy] = 
            stockChar.strategyEffectiveness[strategy] * 0.8 + 0.2; // 平滑更新
        } 
        // 策略预测错误,降低有效性评分
        else if ((strategyAction === 'buy' && tradeResult.result < 0) || 
                (strategyAction === 'sell' && tradeResult.result > 0)) {
          stockChar.strategyEffectiveness[strategy] = 
            stockChar.strategyEffectiveness[strategy] * 0.8; // 平滑更新
        }
      });
    }
    
    // 更新波动性特征
    if (tradeResult.priceData && tradeResult.priceData.length >= 20) {
      const prices = tradeResult.priceData;
      const returns = [];
      
      // 计算日收益率
      for (let i = 1; i < prices.length; i++) {
        returns.push((prices[i] - prices[i - 1]) / prices[i - 1]);
      }
      
      // 计算波动率
      const mean = returns.reduce((sum, r) => sum + r, 0) / returns.length;
      const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length;
      const stdDev = Math.sqrt(variance);
      
      // 根据标准差判断波动性
      if (stdDev > 0.02) {
        stockChar.volatility = 'high';
      } else if (stdDev < 0.01) {
        stockChar.volatility = 'low';
      } else {
        stockChar.volatility = 'medium';
      }
    }
    
    // 更新交易模式
    if (tradeResult.priceData && tradeResult.priceData.length >= 60) {
      // 判断是否为区间交易模式
      const prices = tradeResult.priceData;
      const max = Math.max(...prices.slice(-60));
      const min = Math.min(...prices.slice(-60));
      const range = (max - min) / min;
      
      // 计算趋势强度
      const ma20 = []; // 简单计算20日均线
      for (let i = 19; i < prices.length; i++) {
        const sum = prices.slice(i-19, i+1).reduce((s, p) => s + p, 0);
        ma20.push(sum / 20);
      }
      
      // 计算均线斜率
      const slope = (ma20[ma20.length-1] - ma20[ma20.length-20]) / ma20[ma20.length-20];
      
      if (Math.abs(slope) > 0.1) {
        stockChar.tradingPattern = 'trending'; // 趋势明显
      } else if (range < 0.1) {
        stockChar.tradingPattern = 'ranging'; // 区间震荡
      } else {
        stockChar.tradingPattern = 'normal';
      }
    }
    
    stockChar.lastUpdated = new Date();
    
    // 保存到存储
    try {
      uni.setStorageSync(`stock_characteristics_${stockCode}`, stockChar);
    } catch (error) {
      console.error('保存股票特性失败:', error);
    }
  }
}

export default StrategyAI;
