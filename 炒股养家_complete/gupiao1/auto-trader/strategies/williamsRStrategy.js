/**
 * 威廉指标交易策略
 * 实现威廉指标(Williams %R)的分析和交易信号生成
 */

import { calculateWilliamsR, calculateMA, calculateRSI } from '../indicators/technicalIndicators.js';

/**
 * 威廉指标策略类
 */
class WilliamsRStrategy {
  constructor() {
    // 策略名称和描述
    this.name = "威廉指标交易策略";
    this.description = "威廉指标(Williams %R)是一种动量指标,测量收盘价相对于最高价的位置。该指标在-20以上通常被视为超买区域,在-80以下视为超卖区域,可以用于识别市场反转点和趋势强度。";
  }

  /**
   * 分析股票数据并生成交易信号
   * @param {Object} stockData 股票数据对象,包含价格,交易量等信息
   * @returns {Object} 分析结果,包含信号,评分和解释
   */
  analyze(stockData) {
    const { prices, highPrices, lowPrices, volumes } = stockData;

    // 计算不同周期的威廉指标
    const williamsR14 = calculateWilliamsR(prices, highPrices, lowPrices, 14);
    const williamsR7 = calculateWilliamsR(prices, highPrices, lowPrices, 7);
    const williamsR21 = calculateWilliamsR(prices, highPrices, lowPrices, 21);

    // 计算RSI作为确认指标
    const rsi14 = calculateRSI(prices, 14);
    
    // 计算20日均线作为趋势过滤器
    const ma20 = calculateMA(prices, 20);

    // 获取最新的指标值
    const currentWR14 = williamsR14[williamsR14.length - 1];
    const currentWR7 = williamsR7[williamsR7.length - 1];
    const currentWR21 = williamsR21[williamsR21.length - 1];
    const prevWR14 = williamsR14[williamsR14.length - 2];
    const currentRSI = rsi14[rsi14.length - 1];
    const currentPrice = prices[prices.length - 1];
    const ma20Value = ma20[ma20.length - 1];

    // 判断超买超卖状态
    const isOversold = currentWR14 <= -80;
    const isOverbought = currentWR14 >= -20;
    
    // 判断指标是否从超卖区上穿或从超买区下穿
    const crossingFromOversold = prevWR14 < -80 && currentWR14 > -80;
    const crossingFromOverbought = prevWR14 > -20 && currentWR14 < -20;

    // 判断威廉指标各周期之间的一致性
    const indicatorConsistency = this._checkIndicatorConsistency(currentWR7, currentWR14, currentWR21);

    // 判断RSI确认信号
    const rsiConfirmation = this._checkRSIConfirmation(currentRSI, isOversold, isOverbought);

    // 判断价格相对于均线的位置(趋势方向)
    const trendDirection = currentPrice > ma20Value ? "uptrend" : "downtrend";

    // 生成交易信号和评分
    const signals = this._generateSignals(
      isOversold,
      isOverbought,
      crossingFromOversold,
      crossingFromOverbought,
      indicatorConsistency,
      rsiConfirmation,
      trendDirection
    );

    // 生成解释文本
    const interpretation = this._generateInterpretation(
      currentWR14,
      isOversold,
      isOverbought,
      crossingFromOversold,
      crossingFromOverbought,
      rsiConfirmation,
      trendDirection,
      signals.action
    );

    return {
      indicator: {
        williamsR14: currentWR14.toFixed(2),
        williamsR7: currentWR7.toFixed(2),
        williamsR21: currentWR21.toFixed(2),
        rsi: currentRSI.toFixed(2)
      },
      signals: signals.signalDetails,
      score: signals.score,
      action: signals.action,
      interpretation: interpretation
    };
  }

  /**
   * 检查各周期威廉指标之间的一致性
   * @param {Number} wr7 7日威廉指标值
   * @param {Number} wr14 14日威廉指标值
   * @param {Number} wr21 21日威廉指标值
   * @returns {Object} 一致性分析结果
   */
  _checkIndicatorConsistency(wr7, wr14, wr21) {
    // 检查是否所有周期都显示超买状态
    const allOverbought = wr7 >= -20 && wr14 >= -20 && wr21 >= -20;
    
    // 检查是否所有周期都显示超卖状态
    const allOversold = wr7 <= -80 && wr14 <= -80 && wr21 <= -80;
    
    // 检查短期和中期是否一致(方向一致性)
    const shortMidTermConsistency = (wr7 > -50 && wr14 > -50) || (wr7 < -50 && wr14 < -50);
    
    // 检查中期和长期是否一致(方向一致性)
    const midLongTermConsistency = (wr14 > -50 && wr21 > -50) || (wr14 < -50 && wr21 < -50);
    
    return {
      allOverbought,
      allOversold,
      shortMidTermConsistency,
      midLongTermConsistency,
      // 整体一致性评分 (0-100)
      overallConsistency: (
        (allOverbought || allOversold ? 100 : 0) + 
        (shortMidTermConsistency ? 50 : 0) + 
        (midLongTermConsistency ? 50 : 0)
      ) / 2
    };
  }

  /**
   * 检查RSI与威廉指标的确认关系
   * @param {Number} rsi RSI值
   * @param {Boolean} isOversold 是否处于超卖状态
   * @param {Boolean} isOverbought 是否处于超买状态
   * @returns {Object} RSI确认分析结果
   */
  _checkRSIConfirmation(rsi, isOversold, isOverbought) {
    // RSI超买超卖状态
    const rsiOverbought = rsi > 70;
    const rsiOversold = rsi < 30;
    
    // 确认状态
    const confirmsOverbought = isOverbought && rsiOverbought;
    const confirmsOversold = isOversold && rsiOversold;
    
    // 判断背离情况
    const divergenceOverbought = isOverbought && !rsiOverbought;
    const divergenceOversold = isOversold && !rsiOversold;
    
    return {
      confirmsOverbought,
      confirmsOversold,
      divergenceOverbought,
      divergenceOversold,
      // 整体确认强度 (0-100)
      confirmationStrength: confirmsOverbought || confirmsOversold ? 100 : 
                           (divergenceOverbought || divergenceOversold ? 30 : 70)
    };
  }

  /**
   * 生成交易信号和评分
   * @param {Boolean} isOversold 是否处于超卖状态
   * @param {Boolean} isOverbought 是否处于超买状态
   * @param {Boolean} crossingFromOversold 是否从超卖区上穿
   * @param {Boolean} crossingFromOverbought 是否从超买区下穿
   * @param {Object} indicatorConsistency 指标一致性结果
   * @param {Object} rsiConfirmation RSI确认结果
   * @param {String} trendDirection 趋势方向
   * @returns {Object} 交易信号和评分
   */
  _generateSignals(
    isOversold,
    isOverbought,
    crossingFromOversold,
    crossingFromOverbought,
    indicatorConsistency,
    rsiConfirmation,
    trendDirection
  ) {
    let score = 50; // 中性起点
    let action = "hold";
    
    // 构建信号详情对象
    const signalDetails = {
      isOversold,
      isOverbought,
      crossingFromOversold,
      crossingFromOverbought,
      indicatorConsistency: indicatorConsistency.overallConsistency > 50,
      rsiConfirmation: rsiConfirmation.confirmationStrength > 50,
      trendDirection
    };
    
    // 根据超买超卖状态调整评分
    if (isOversold) score -= 20;
    if (isOverbought) score += 20;
    
    // 根据穿越信号调整评分
    if (crossingFromOversold) {
      score += 25;
      action = "buy";
    }
    if (crossingFromOverbought) {
      score -= 25;
      action = "sell";
    }
    
    // 根据指标一致性调整评分
    score += (indicatorConsistency.overallConsistency - 50) / 5;
    
    // 根据RSI确认调整评分
    if (rsiConfirmation.confirmsOversold) {
      score += 10;
      if (trendDirection === "uptrend") score += 5;
    }
    if (rsiConfirmation.confirmsOverbought) {
      score -= 10;
      if (trendDirection === "downtrend") score -= 5;
    }
    
    // 根据背离情况调整评分
    if (rsiConfirmation.divergenceOversold) score += 5;
    if (rsiConfirmation.divergenceOverbought) score -= 5;
    
    // 根据趋势方向进行最终调整
    if (trendDirection === "uptrend" && score > 60) action = "buy";
    if (trendDirection === "downtrend" && score < 40) action = "sell";
    
    // 确保评分在0-100范围内
    score = Math.min(100, Math.max(0, score));
    
    return {
      score,
      action,
      signalDetails
    };
  }

  /**
   * 生成解释文本
   * @param {Number} williamsR 威廉指标值
   * @param {Boolean} isOversold 是否处于超卖状态
   * @param {Boolean} isOverbought 是否处于超买状态
   * @param {Boolean} crossingFromOversold 是否从超卖区上穿
   * @param {Boolean} crossingFromOverbought 是否从超买区下穿
   * @param {Object} rsiConfirmation RSI确认结果
   * @param {String} trendDirection 趋势方向
   * @param {String} action 交易动作
   * @returns {String} 解释文本
   */
  _generateInterpretation(
    williamsR,
    isOversold,
    isOverbought,
    crossingFromOversold,
    crossingFromOverbought,
    rsiConfirmation,
    trendDirection,
    action
  ) {
    let interpretation = `威廉指标(Williams %R)当前值为${williamsR.toFixed(2)},`;
    
    if (isOversold) {
      interpretation += "处于超卖区域(-80以下),表明市场可能超卖,有反弹可能。";
    } else if (isOverbought) {
      interpretation += "处于超买区域(-20以上),表明市场可能超买,有回调风险。";
    } else {
      interpretation += "处于中性区域,没有明显的超买或超卖信号。";
    }
    
    if (crossingFromOversold) {
      interpretation += " 指标刚从超卖区域上穿,提供较强的买入信号。";
    } else if (crossingFromOverbought) {
      interpretation += " 指标刚从超买区域下穿,提供较强的卖出信号。";
    }
    
    interpretation += ` RSI指标${rsiConfirmation.confirmsOversold || rsiConfirmation.confirmsOverbought ? "确认" : "不确认"}当前威廉指标的信号。`;
    
    interpretation += ` 当前市场趋势方向为${trendDirection === "uptrend" ? "上升" : "下降"}。`;
    
    interpretation += ` 综合分析建议:${action === "buy" ? "买入" : action === "sell" ? "卖出" : "持有"}。`;
    
    return interpretation;
  }

  /**
   * 获取威廉指标的实战指南
   * @returns {Object} 实战指南内容
   */
  getPracticalGuide() {
    return {
      title: "威廉指标(Williams %R)实战应用指南",
      introduction: "威廉指标是由Larry Williams开发的动量指标,测量当前收盘价相对于过去N个交易日最高价与最低价范围的位置。值域为0至-100,其中-20以上为超买区,-80以下为超卖区。",
      keyPoints: [
        "威廉指标是反向指标,当指标在-20以上时表示超买,而非表示强势;当指标在-80以下时表示超卖,而非表示弱势",
        "在趋势明显的市场中,威廉指标信号应该与趋势方向结合使用,避免在强劲趋势中反向操作",
        "威廉指标对短期市场反转非常敏感,尤其适合短线交易",
        "当指标在超卖区域(-80以下)停留后回升穿越-80线时,是较佳买入时机",
        "当指标在超买区域(-20以上)停留后回落穿越-20线时,是较佳卖出时机",
        "威廉指标与RSI,KDJ等指标结合使用,可以提高信号可靠性"
      ],
      strategies: [
        {
          name: "反转信号策略",
          description: "当威廉指标从超卖区上穿或从超买区下穿时产生交易信号",
          rules: [
            "当威廉指标从-80以下上穿至-80以上时,产生买入信号",
            "当威廉指标从-20以上下穿至-20以下时,产生卖出信号",
            "需结合市场趋势和其他指标确认,避免在强趋势中逆势操作"
          ]
        },
        {
          name: "双重时间框架策略",
          description: "同时使用不同周期的威廉指标,提高信号可靠性",
          rules: [
            "使用7日,14日和21日三个周期的威廉指标",
            "当所有三个周期的指标都处于超卖状态并开始上穿时,产生强力买入信号",
            "当所有三个周期的指标都处于超买状态并开始下穿时,产生强力卖出信号"
          ]
        },
        {
          name: "威廉指标与RSI结合策略",
          description: "结合RSI指标来过滤威廉指标的假信号",
          rules: [
            "当威廉指标显示超卖且RSI低于30时,寻找买入机会",
            "当威廉指标显示超买且RSI高于70时,寻找卖出机会",
            "当两个指标出现背离时,这种信号可能更为可靠"
          ]
        },
        {
          name: "尾盘交易策略",
          description: "特别适用于中国A股T+0交易的尾盘策略",
          rules: [
            "在收盘前30分钟观察威廉指标的变化",
            "如果威廉指标快速从超卖区回升,可能是尾盘拉升信号,适合T+0买入",
            "如果威廉指标快速从超买区回落,可能是尾盘跳水信号,应避免买入或考虑卖出",
            "此策略尤其适合A股市场14:30-15:00的尾盘时段操作"
          ]
        }
      ],
      bestPractices: [
        "不要仅依赖威廉指标一个信号进行交易,始终结合其他技术指标和市场环境",
        "在使用威廉指标时,要注意市场所处的宏观环境和总体趋势",
        "威廉指标在震荡市场中的效果往往优于趋势市场",
        "当威廉指标和价格走势出现背离时,可能预示着趋势即将逆转",
        "T+0交易中,尾盘威廉指标的变化尤其值得关注,可以帮助决策是否进行最后的买卖操作"
      ],
      realWorldExample: "实例分析:2022年A股市场在3月至4月底经历了一波急跌后,多只股票的威廉指标跌至-90以下的极度超卖区域。以某科技股为例,当其威廉指标从-95回升至-80并上穿该线时,随后两周股价上涨了超过15%。当时该股的RSI指标也从极低位回升,形成双指标确认,为投资者提供了较为明确的买入机会。"
    };
  }
}

export default WilliamsRStrategy; 
