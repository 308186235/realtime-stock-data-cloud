/**
 * 六脉神剑策略模型
 * 包含六脉神剑的六种主要策略:天字诀,地字诀,人字诀,和字诀,顺字诀,凌字诀
 */

// 导入必要的指标计算工具
import { calculateMA, calculateMACD, calculateKDJ, calculateRSI, calculateBOLL } from '../indicators/technicalIndicators.js';

/**
 * 六脉神剑策略类
 */
class SixSwordStrategy {
  constructor() {
    this.strategies = {
      tian: this.tianStrategy, // 天字诀 - 趋势突破策略
      di: this.diStrategy,     // 地字诀 - 支撑阻力策略
      ren: this.renStrategy,   // 人字诀 - 量价关系策略
      he: this.heStrategy,     // 和字诀 - 调整企稳策略
      shun: this.shunStrategy, // 顺字诀 - 顺势而为策略
      ling: this.lingStrategy  // 凌字诀 - 高级组合策略
    };
  }

  /**
   * 分析股票数据并返回六脉神剑综合分析结果
   * @param {Object} stockData 股票数据
   * @returns {Object} 分析结果
   */
  analyze(stockData) {
    const results = {};
    
    // 对每种策略进行分析
    for (const [name, strategy] of Object.entries(this.strategies)) {
      results[name] = strategy.call(this, stockData);
    }
    
    // 综合分析结果
    const overallScore = this.calculateOverallScore(results);
    const recommendation = this.generateRecommendation(overallScore, results);
    
    return {
      strategies: results,
      overallScore,
      recommendation
    };
  }

  /**
   * 天字诀 - 趋势突破策略
   * 主要识别股价突破重要均线,突破箱体,突破趋势线等情况
   */
  tianStrategy(stockData) {
    const { prices, volumes } = stockData;
    const ma20 = calculateMA(prices, 20);
    const ma60 = calculateMA(prices, 60);
    
    // 判断是否突破20日均线
    const breakMA20 = prices[prices.length - 1] > ma20[ma20.length - 1] && 
                      prices[prices.length - 2] <= ma20[ma20.length - 2];
    
    // 判断是否突破60日均线
    const breakMA60 = prices[prices.length - 1] > ma60[ma60.length - 1] && 
                      prices[prices.length - 2] <= ma60[ma60.length - 2];
    
    // 计算近期高点和低点,判断是否突破箱体
    const recentHigh = Math.max(...prices.slice(-20));
    const breakBox = prices[prices.length - 1] > recentHigh && 
                    prices[prices.length - 2] <= recentHigh;
    
    // 综合评分
    let score = 0;
    if (breakMA20) score += 30;
    if (breakMA60) score += 40;
    if (breakBox) score += 30;
    
    return {
      score,
      signals: {
        breakMA20,
        breakMA60,
        breakBox
      },
      interpretation: this.interpretTianStrategy(score, { breakMA20, breakMA60, breakBox })
    };
  }

  /**
   * 地字诀 - 支撑阻力策略
   * 主要识别股价在支撑位反弹或阻力位回落的情况
   */
  diStrategy(stockData) {
    const { prices } = stockData;
    const boll = calculateBOLL(prices);
    
    // 判断是否接近布林带下轨(支撑位)
    const nearLowerBand = prices[prices.length - 1] < boll.lower[boll.lower.length - 1] * 1.02;
    
    // 判断是否接近布林带上轨(阻力位)
    const nearUpperBand = prices[prices.length - 1] > boll.upper[boll.upper.length - 1] * 0.98;
    
    // 判断是否从下轨反弹
    const bounceFromLower = prices[prices.length - 1] > prices[prices.length - 2] && 
                           prices[prices.length - 2] < boll.lower[boll.lower.length - 2];
    
    // 判断是否从上轨回落
    const fallFromUpper = prices[prices.length - 1] < prices[prices.length - 2] && 
                         prices[prices.length - 2] > boll.upper[boll.upper.length - 2];
    
    // 综合评分
    let score = 0;
    if (nearLowerBand && bounceFromLower) score += 40; // 支撑位反弹,看多信号
    if (nearUpperBand && fallFromUpper) score -= 40;   // 阻力位回落,看空信号
    if (nearLowerBand && !bounceFromLower) score += 20; // 接近支撑位,潜在反弹机会
    if (nearUpperBand && !fallFromUpper) score -= 20;   // 接近阻力位,潜在回落风险
    
    return {
      score,
      signals: {
        nearLowerBand,
        nearUpperBand,
        bounceFromLower,
        fallFromUpper
      },
      interpretation: this.interpretDiStrategy(score, { nearLowerBand, nearUpperBand, bounceFromLower, fallFromUpper })
    };
  }

  /**
   * 人字诀 - 量价关系策略
   * 主要分析成交量与股价变动的关系
   */
  renStrategy(stockData) {
    const { prices, volumes } = stockData;
    
    // 计算近期平均成交量
    const avgVolume = volumes.slice(-5).reduce((sum, vol) => sum + vol, 0) / 5;
    
    // 判断是否放量上涨
    const volumeIncrease = volumes[volumes.length - 1] > avgVolume * 1.5;
    const priceIncrease = prices[prices.length - 1] > prices[prices.length - 2];
    const volumeUpWithPrice = volumeIncrease && priceIncrease;
    
    // 判断是否缩量下跌
    const volumeDecrease = volumes[volumes.length - 1] < avgVolume * 0.7;
    const priceDecrease = prices[prices.length - 1] < prices[prices.length - 2];
    const volumeDownWithPrice = volumeDecrease && priceDecrease;
    
    // 综合评分
    let score = 0;
    if (volumeUpWithPrice) score += 40;     // 放量上涨,看多信号
    if (volumeDownWithPrice) score -= 20;   // 缩量下跌,弱势信号
    if (volumeIncrease && priceDecrease) score -= 30; // 放量下跌,看空信号
    if (volumeDecrease && priceIncrease) score += 20; // 缩量上涨,需观察
    
    return {
      score,
      signals: {
        volumeUpWithPrice,
        volumeDownWithPrice,
        volumeIncrease,
        priceIncrease,
        volumeDecrease,
        priceDecrease
      },
      interpretation: this.interpretRenStrategy(score, { 
        volumeUpWithPrice, volumeDownWithPrice, 
        volumeIncrease, priceIncrease, 
        volumeDecrease, priceDecrease 
      })
    };
  }

  /**
   * 和字诀 - 调整企稳策略
   * 主要识别股价调整后企稳回升的情况
   */
  heStrategy(stockData) {
    const { prices } = stockData;
    const rsi = calculateRSI(prices);
    const kdj = calculateKDJ(prices);
    
    // 判断RSI是否超卖后回升
    const rsiOversold = rsi[rsi.length - 2] < 30;
    const rsiRising = rsi[rsi.length - 1] > rsi[rsi.length - 2];
    const rsiRecovery = rsiOversold && rsiRising;
    
    // 判断KDJ是否金叉
    const kdjGoldenCross = kdj.k[kdj.k.length - 1] > kdj.d[kdj.d.length - 1] && 
                          kdj.k[kdj.k.length - 2] <= kdj.d[kdj.d.length - 2];
    
    // 判断股价是否连续下跌后企稳
    let consecutiveFall = 0;
    for (let i = prices.length - 6; i < prices.length - 1; i++) {
      if (prices[i] < prices[i-1]) consecutiveFall++;
    }
    const stabilizing = consecutiveFall >= 3 && prices[prices.length - 1] > prices[prices.length - 2];
    
    // 综合评分
    let score = 0;
    if (rsiRecovery) score += 30;
    if (kdjGoldenCross) score += 30;
    if (stabilizing) score += 40;
    
    return {
      score,
      signals: {
        rsiRecovery,
        kdjGoldenCross,
        stabilizing
      },
      interpretation: this.interpretHeStrategy(score, { rsiRecovery, kdjGoldenCross, stabilizing })
    };
  }

  /**
   * 顺字诀 - 顺势而为策略
   * 主要识别大趋势方向,顺势操作
   */
  shunStrategy(stockData) {
    const { prices } = stockData;
    const macd = calculateMACD(prices);
    
    // 判断MACD柱状线是否转正
    const macdPositive = macd.histogram[macd.histogram.length - 1] > 0;
    const macdTurningPositive = macd.histogram[macd.histogram.length - 1] > 0 && 
                               macd.histogram[macd.histogram.length - 2] <= 0;
    
    // 判断长期趋势(通过60日均线斜率)
    const ma60 = calculateMA(prices, 60);
    const ma60Trend = ma60[ma60.length - 1] > ma60[ma60.length - 10];
    
    // 判断中期趋势(通过20日均线斜率)
    const ma20 = calculateMA(prices, 20);
    const ma20Trend = ma20[ma20.length - 1] > ma20[ma20.length - 5];
    
    // 综合评分
    let score = 0;
    if (macdPositive) score += 20;
    if (macdTurningPositive) score += 30;
    if (ma60Trend) score += 25;
    if (ma20Trend) score += 25;
    
    return {
      score,
      signals: {
        macdPositive,
        macdTurningPositive,
        ma60Trend,
        ma20Trend
      },
      interpretation: this.interpretShunStrategy(score, { macdPositive, macdTurningPositive, ma60Trend, ma20Trend })
    };
  }

  /**
   * 凌字诀 - 高级组合策略
   * 结合多种指标和形态,进行更复杂的分析
   */
  lingStrategy(stockData) {
    const { prices, volumes } = stockData;
    const ma20 = calculateMA(prices, 20);
    const ma60 = calculateMA(prices, 60);
    const macd = calculateMACD(prices);
    const kdj = calculateKDJ(prices);
    
    // 判断均线多头排列
    const bullishAlignment = ma20[ma20.length - 1] > ma60[ma60.length - 1];
    
    // 判断MACD和KDJ同时金叉
    const macdGoldenCross = macd.signal[macd.signal.length - 1] > macd.signal[macd.signal.length - 2] &&
                           macd.histogram[macd.histogram.length - 1] > 0 &&
                           macd.histogram[macd.histogram.length - 2] <= 0;
    
    const kdjGoldenCross = kdj.k[kdj.k.length - 1] > kdj.d[kdj.d.length - 1] && 
                          kdj.k[kdj.k.length - 2] <= kdj.d[kdj.d.length - 2];
    
    const doubleGoldenCross = macdGoldenCross && kdjGoldenCross;
    
    // 判断放量突破
    const breakout = prices[prices.length - 1] > Math.max(...prices.slice(-20, -1));
    const volumeIncrease = volumes[volumes.length - 1] > volumes.slice(-5).reduce((sum, vol) => sum + vol, 0) / 5 * 1.5;
    const volumeBreakout = breakout && volumeIncrease;
    
    // 综合评分
    let score = 0;
    if (bullishAlignment) score += 20;
    if (doubleGoldenCross) score += 40;
    if (volumeBreakout) score += 40;
    
    return {
      score,
      signals: {
        bullishAlignment,
        doubleGoldenCross,
        volumeBreakout
      },
      interpretation: this.interpretLingStrategy(score, { bullishAlignment, doubleGoldenCross, volumeBreakout })
    };
  }

  /**
   * 计算综合评分
   */
  calculateOverallScore(results) {
    let totalScore = 0;
    const weights = {
      tian: 1.0,  // 天字诀权重
      di: 0.8,    // 地字诀权重
      ren: 0.9,   // 人字诀权重
      he: 0.8,    // 和字诀权重
      shun: 1.1,  // 顺字诀权重
      ling: 1.2   // 凌字诀权重
    };
    
    for (const [strategy, result] of Object.entries(results)) {
      totalScore += result.score * weights[strategy];
    }
    
    // 归一化到0-100区间
    return Math.min(100, Math.max(0, totalScore / 6));
  }

  /**
   * 生成交易建议
   */
  generateRecommendation(overallScore, results) {
    if (overallScore >= 80) {
      return {
        action: '强烈建议买入',
        confidence: '高',
        description: '多项指标显示强烈的买入信号,市场走势强劲。'
      };
    } else if (overallScore >= 60) {
      return {
        action: '建议买入',
        confidence: '中高',
        description: '大部分指标显示积极信号,市场走势向好。'
      };
    } else if (overallScore >= 45) {
      return {
        action: '观望',
        confidence: '中',
        description: '指标信号混合,建议等待更明确的市场方向。'
      };
    } else if (overallScore >= 30) {
      return {
        action: '建议卖出',
        confidence: '中高',
        description: '多项指标显示负面信号,市场走势转弱。'
      };
    } else {
      return {
        action: '强烈建议卖出',
        confidence: '高',
        description: '多项指标显示强烈的卖出信号,市场走势恶化。'
      };
    }
  }

  /**
   * 解释天字诀分析结果
   */
  interpretTianStrategy(score, signals) {
    if (score >= 60) {
      return '出现明显的突破信号,趋势向上,可考虑买入';
    } else if (score >= 30) {
      return '有一定突破迹象,但需确认,可小仓位试探';
    } else {
      return '未出现有效突破信号,建议观望';
    }
  }

  /**
   * 解释地字诀分析结果
   */
  interpretDiStrategy(score, signals) {
    if (score >= 30) {
      return '股价在支撑位有效反弹,可能开始上涨';
    } else if (score <= -30) {
      return '股价在阻力位回落,可能开始下跌';
    } else {
      return '股价运行在支撑位与阻力位之间,暂无明确方向';
    }
  }

  /**
   * 解释人字诀分析结果
   */
  interpretRenStrategy(score, signals) {
    if (score >= 30) {
      return '量价配合良好,放量上涨,看多信号明确';
    } else if (score <= -20) {
      return '量价背离,市场走势不佳,需谨慎';
    } else {
      return '量价关系一般,需结合其他指标判断';
    }
  }

  /**
   * 解释和字诀分析结果
   */
  interpretHeStrategy(score, signals) {
    if (score >= 60) {
      return '股价调整后明显企稳回升,可能是买入机会';
    } else if (score >= 30) {
      return '有企稳迹象,但需进一步确认';
    } else {
      return '未见明显企稳信号,建议观望';
    }
  }

  /**
   * 解释顺字诀分析结果
   */
  interpretShunStrategy(score, signals) {
    if (score >= 60) {
      return '大趋势向上,建议顺势操作,持股或买入';
    } else if (score <= 30) {
      return '大趋势向下,建议顺势操作,减仓或观望';
    } else {
      return '趋势不明朗,建议观望或小仓位操作';
    }
  }

  /**
   * 解释凌字诀分析结果
   */
  interpretLingStrategy(score, signals) {
    if (score >= 60) {
      return '多项高级指标共振,强烈看多信号';
    } else if (score >= 30) {
      return '部分高级指标显示积极,谨慎看多';
    } else {
      return '高级指标未显示明确信号,建议观望';
    }
  }
}

export default SixSwordStrategy; 
