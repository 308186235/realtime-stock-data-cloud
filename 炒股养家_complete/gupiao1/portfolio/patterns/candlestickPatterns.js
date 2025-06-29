/**
 * 蜡烛图形态识别模块
 * 包含各种经典蜡烛图形态,如乌云盖顶,锤子线,吞噬线等
 */

/**
 * 检测乌云盖顶形态
 * 乌云盖顶是一种顶部反转信号,出现在上涨趋势末端
 * 特征:
 * 1. 第一根K线为较长的阳线
 * 2. 第二根K线高开,但收盘价在第一根阳线实体的50%以下
 * 3. 通常在上涨趋势末端
 */
export function detectDarkCloudCover(candles, options = {}) {
  const {
    penetrationRatio = 0.5,
    volumeIncrease = 0.3,
    upTrendBars = 3,
    upTrendThreshold = 0.02,
    minBodySize = 0.6,  // 实体占整个K线的最小比例
  } = options;
  
  if (candles.length < upTrendBars + 2) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'dark_cloud_cover',
      direction: 'neutral'
    };
  }
  
  // 获取最近的两根K线
  const secondDay = candles[candles.length - 1];
  const firstDay = candles[candles.length - 2];
  
  // 检查上涨趋势(查看前N天是否有明显上涨)
  const trendCandles = candles.slice(candles.length - upTrendBars - 2, candles.length - 2);
  const isUptrend = checkUptrend(trendCandles, upTrendThreshold);
  
  if (!isUptrend) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'dark_cloud_cover',
      direction: 'neutral'
    };
  }
  
  // 检查第一天是否为阳线且实体较大
  const firstDayIsPositive = firstDay.close > firstDay.open;
  const firstDayBodySize = Math.abs(firstDay.close - firstDay.open) / (firstDay.high - firstDay.low);
  const firstDayHasLargeBody = firstDayBodySize >= minBodySize;
  
  // 检查第二天是否为阴线
  const secondDayIsNegative = secondDay.close < secondDay.open;
  
  // 检查第二天是否高开
  const secondDayOpenedHigher = secondDay.open > firstDay.close;
  
  // 检查阴线是否深入阳线实体50%以上
  const penetrationDepth = (firstDay.close + firstDay.open) / 2;
  const isPenetrationDeep = secondDay.close < penetrationDepth;
  
  // 检查成交量是否放大
  const volumeIncreased = secondDay.volume > firstDay.volume * (1 + volumeIncrease);
  
  // 所有条件是否满足
  const isDarkCloudCover = firstDayIsPositive && firstDayHasLargeBody && 
                           secondDayIsNegative && secondDayOpenedHigher && 
                           isPenetrationDeep;
  
  if (!isDarkCloudCover) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'dark_cloud_cover',
      direction: 'neutral'
    };
  }
  
  // 计算置信度
  // - 阴线覆盖程度越深,置信度越高
  // - 成交量放大程度越高,置信度越高
  // - 趋势越明显,置信度越高
  
  // 计算阴线覆盖比例
  const penetrationAmount = (secondDay.open - secondDay.close) / (firstDay.close - firstDay.open);
  const penetrationScore = Math.min(penetrationAmount / penetrationRatio, 1.5) * 0.5;
  
  // 计算成交量放大得分
  const volumeScore = volumeIncreased ? 0.3 : 0;
  
  // 计算趋势强度得分
  const trendScore = calculateTrendStrength(trendCandles) * 0.2;
  
  // 计算总体置信度(最高1.0)
  const confidence = Math.min(penetrationScore + volumeScore + trendScore, 1.0);
  
  return {
    detected: true,
    confidence,
    pattern: 'dark_cloud_cover',
    direction: 'bearish',
    penetrationRatio: penetrationAmount,
    volumeIncrease: secondDay.volume / firstDay.volume - 1,
    signal: generateActionSignal(confidence, secondDay),
    key_levels: {
      resistance: secondDay.high,
      stop_loss: Math.max(firstDay.high, secondDay.high),
      target1: secondDay.close - (firstDay.close - firstDay.open),  // 1:1目标
      target2: 2 * secondDay.close - (firstDay.close - firstDay.open) * 1.5  // 1.5:1目标
    }
  };
}

/**
 * 检测曙光初现形态
 * 曙光初现是一种底部反转信号,出现在下跌趋势末端
 * 特征:
 * 1. 第一根K线为阴线,延续下跌趋势
 * 2. 第二根K线低开,但收盘价深入第一根阴线实体的50%以上
 * 3. 成交量通常放大,显示买盘积极介入
 */
export function detectMorningStar(candles, options = {}) {
  const {
    penetrationRatio = 0.5,      // 阳线深入阴线实体的最小比例(50%)
    idealPenetration = 0.6,      // 理想深入比例(60%)
    volumeIncrease = 0.3,        // 成交量增加比例(30%)
    downTrendBars = 3,           // 下跌趋势确认K线数
    downTrendThreshold = 0.02,   // 下跌趋势确认阈值
    minBodySize = 0.5,           // 实体占整个K线的最小比例
  } = options;
  
  // 确保有足够的K线数据
  if (candles.length < downTrendBars + 2) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'morning_star',
      direction: 'neutral'
    };
  }
  
  // 获取最近的两根K线
  const secondDay = candles[candles.length - 1];  // 阳线
  const firstDay = candles[candles.length - 2];   // 阴线
  
  // 检查下跌趋势(查看前N天是否有明显下跌)
  const trendCandles = candles.slice(candles.length - downTrendBars - 2, candles.length - 2);
  const isDowntrend = checkDowntrend(trendCandles, downTrendThreshold);
  
  if (!isDowntrend) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'morning_star',
      direction: 'neutral'
    };
  }
  
  // 检查第一天是否为阴线且实体较大
  const firstDayIsNegative = firstDay.close < firstDay.open;
  const firstDayBodySize = Math.abs(firstDay.close - firstDay.open) / (firstDay.high - firstDay.low);
  const firstDayHasLargeBody = firstDayBodySize >= minBodySize;
  
  // 检查第二天是否为阳线
  const secondDayIsPositive = secondDay.close > secondDay.open;
  
  // 检查第二天是否低开
  const secondDayOpenedLower = secondDay.open < firstDay.close;
  
  // 检查阳线是否深入阴线实体50%以上
  const penetrationDepth = (firstDay.open + firstDay.close) / 2;
  const isPenetrationDeep = secondDay.close > penetrationDepth;
  
  // 检查成交量是否放大
  const volumeIncreased = secondDay.volume > firstDay.volume * (1 + volumeIncrease);
  
  // 所有条件是否满足
  const isMorningStar = firstDayIsNegative && firstDayHasLargeBody && 
                        secondDayIsPositive && secondDayOpenedLower && 
                        isPenetrationDeep;
  
  if (!isMorningStar) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'morning_star',
      direction: 'neutral'
    };
  }
  
  // 计算置信度
  // - 阳线深入程度越深,置信度越高
  // - 成交量放大程度越高,置信度越高
  // - 趋势越明显,置信度越高
  
  // 计算阳线覆盖比例 (0-1, 其中1表示完全覆盖阴线实体)
  const penetrationAmount = (secondDay.close - firstDay.close) / (firstDay.open - firstDay.close);
  
  // 阳线完全覆盖阴线实体为"阳包阴"形态,反转信号更强
  const isEngulfing = secondDay.close >= firstDay.open;
  
  // 计算penetration得分 (最大贡献50%)
  const penetrationScore = isEngulfing ? 
    0.5 : // 阳包阴,满分
    Math.min(penetrationAmount / penetrationRatio, 1.5) * 0.5;
  
  // 计算成交量放大得分 (最大贡献30%)
  const volumeScore = volumeIncreased ? 
    Math.min((secondDay.volume / firstDay.volume - 1) / volumeIncrease, 1.5) * 0.3 : 
    0;
  
  // 计算下跌趋势强度得分 (最大贡献20%)
  const trendScore = calculateTrendStrength(trendCandles, true) * 0.2;
  
  // 计算总体置信度(最高1.0)
  const confidence = Math.min(penetrationScore + volumeScore + trendScore, 1.0);
  
  // 判断是否为阳包阴形态(更强的信号)
  const patternType = isEngulfing ? 'bullish_engulfing' : 'morning_star';
  
  return {
    detected: true,
    confidence,
    pattern: patternType,
    direction: 'bullish',
    penetrationRatio: penetrationAmount,
    isEngulfing,
    volumeIncrease: secondDay.volume / firstDay.volume - 1,
    signal: generateBuySignal(confidence, penetrationAmount, volumeIncreased, secondDay),
    key_levels: {
      support: secondDay.low,
      stop_loss: Math.min(firstDay.low, secondDay.low),
      target1: secondDay.close + (secondDay.close - firstDay.close),  // 1:1目标
      target2: secondDay.close + (secondDay.close - firstDay.close) * 1.5  // 1.5:1目标
    }
  };
}

/**
 * 检查一段K线是否处于上涨趋势
 * @param {Array} candles K线数组
 * @param {number} threshold 上涨趋势确认阈值
 * @returns {boolean} 是否处于上涨趋势
 */
function checkUptrend(candles, threshold) {
  if (candles.length < 2) return false;
  
  // 计算开始价格和结束价格
  const startPrice = candles[0].close;
  const endPrice = candles[candles.length - 1].close;
  
  // 计算价格涨幅
  const priceGain = (endPrice - startPrice) / startPrice;
  
  // 判断是否满足上涨趋势阈值
  if (priceGain < threshold) return false;
  
  // 检查过程中是否形成上涨趋势
  // 计算收盘价的高点数量,如果高点占比超过60%则认为是上涨趋势
  let higherCloses = 0;
  for (let i = 1; i < candles.length; i++) {
    if (candles[i].close > candles[i-1].close) {
      higherCloses++;
    }
  }
  
  // 计算上涨天数占比
  const upRatio = higherCloses / (candles.length - 1);
  
  // 满足涨幅阈值且上涨天数占比超过60%,则确认为上涨趋势
  return priceGain >= threshold && upRatio >= 0.6;
}

/**
 * 检查是否处于下跌趋势
 */
function checkDowntrend(candles, threshold) {
  if (candles.length < 2) return false;
  
  // 简单方法:收盘价连续下跌或至少从起点到终点下跌一定比例
  const firstClose = candles[0].close;
  const lastClose = candles[candles.length - 1].close;
  
  // 判断整体跌幅
  const overallLoss = (firstClose - lastClose) / firstClose;
  if (overallLoss >= threshold) {
    return true;
  }
  
  // 判断连续下跌K线数量
  let consecutiveFalls = 0;
  let maxConsecutiveFalls = 0;
  
  for (let i = 1; i < candles.length; i++) {
    if (candles[i].close < candles[i-1].close) {
      consecutiveFalls++;
      maxConsecutiveFalls = Math.max(maxConsecutiveFalls, consecutiveFalls);
    } else {
      consecutiveFalls = 0;
    }
  }
  
  return maxConsecutiveFalls >= Math.floor(candles.length / 2);
}

/**
 * 计算趋势强度
 * @param {Array} candles K线数据
 * @param {Boolean} isDowntrend 是否为下跌趋势
 */
function calculateTrendStrength(candles, isDowntrend = false) {
  if (candles.length < 2) return 0;
  
  // 计算总涨跌幅与平均K线波动的比值
  const priceChange = isDowntrend ? 
    candles[0].close / candles[candles.length - 1].close - 1 : // 下跌幅度
    candles[candles.length - 1].close / candles[0].close - 1;  // 上涨幅度
  
  let avgCandle = 0;
  for (let i = 0; i < candles.length; i++) {
    avgCandle += Math.abs(candles[i].close / candles[i].open - 1);
  }
  avgCandle /= candles.length;
  
  // 趋势强度 = 总涨跌幅 / 平均K线波动
  return Math.min(Math.abs(priceChange) / (avgCandle * 3), 1.0);
}

/**
 * 生成卖出操作信号
 */
function generateActionSignal(confidence, currentCandle) {
  if (confidence >= 0.8) {
    return {
      action: "sell",
      urgency: "high",
      message: "乌云盖顶形态确认,建议立即减仓或设置保护性止损",
      lookFor: "次日开盘确认无法收复失地时加大卖出力度"
    };
  } else if (confidence >= 0.6) {
    return {
      action: "reduce",
      urgency: "medium",
      message: "乌云盖顶形态出现,建议减仓50%,设置剩余仓位止损",
      lookFor: "关注次日是否有效突破昨日低点"
    };
  } else {
    return {
      action: "watch",
      urgency: "low",
      message: "出现弱乌云盖顶形态,建议设置保护性止损",
      lookFor: "观察后续2-3个交易日确认"
    };
  }
}

/**
 * 生成买入操作信号
 */
function generateBuySignal(confidence, penetrationAmount, volumeIncreased, currentCandle) {
  // 高置信度,建议积极买入
  if (confidence >= 0.8) {
    return {
      action: "buy",
      urgency: "high",
      message: "曙光初现形态确认,建议积极买入",
      lookFor: "设置止损在形态最低点,关注后续突破阻力位",
      position: "建议第一阶段仓位20%-30%,次日若继续上涨可加至50%"
    };
  } 
  // 中等置信度,建议观察后买入
  else if (confidence >= 0.6) {
    return {
      action: "watch_buy",
      urgency: "medium",
      message: "曙光初现形态出现,建议观察后买入",
      lookFor: "若次日突破短期阻力位或确认站稳5日均线可买入",
      position: "建议控制首次买入仓位在20%以内,分批建仓"
    };
  } 
  // 低置信度,建议谨慎观望
  else {
    return {
      action: "watch",
      urgency: "low",
      message: "出现弱曙光初现形态,建议谨慎观望",
      lookFor: "等待更多确认信号,如MACD底背离或KDJ金叉",
      position: "暂不建仓,等待形态确认"
    };
  }
}

/**
 * 检测暴跌三杰形态
 * 暴跌三杰形是一种强烈的下跌趋势延续或加速信号,由三根连续的大阴线或中阴线组成
 * 特征:
 * 1. 三根阴线依次排列,每日收盘价均低于前一日收盘价
 * 2. 至少两根阴线为大阴线(跌幅≥3%)
 * 3. 可能伴随跳空低开缺口
 * 4. 成交量可放大(恐慌抛售)或缩量(阴跌无承接)
 */
export function detectTripleCrashPattern(candles, options = {}) {
  const {
    minBigDownBarPct = 0.03,       // 大阴线最小跌幅(3%)
    minBigDownBars = 2,            // 至少需要的大阴线数量
    volumeIncreasePct = 0.3,       // 成交量放大确认阈值(30%)
    minTotalDownPct = 0.06,        // 三日累计最小跌幅(6%)
    upTrendConfirmBars = 5,        // 之前上涨趋势确认K线数量
  } = options;
  
  // 确保有足够的K线数据(至少3根K线用于形态识别 + 额外的K线用于上下文判断)
  if (candles.length < 3 + upTrendConfirmBars) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'triple_crash',
      direction: 'neutral'
    };
  }
  
  // 获取最近的三根K线
  const thirdDay = candles[candles.length - 1];   // 最近的K线
  const secondDay = candles[candles.length - 2];  // 倒数第二根K线
  const firstDay = candles[candles.length - 3];   // 倒数第三根K线
  
  // 检查三根K线是否均为阴线
  const firstDayIsNegative = firstDay.close < firstDay.open;
  const secondDayIsNegative = secondDay.close < secondDay.open;
  const thirdDayIsNegative = thirdDay.close < thirdDay.open;
  
  const allNegativeCandles = firstDayIsNegative && secondDayIsNegative && thirdDayIsNegative;
  
  if (!allNegativeCandles) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'triple_crash',
      direction: 'neutral'
    };
  }
  
  // 检查每日收盘价是否均低于前一日收盘价
  const sequentialDownClose = (secondDay.close < firstDay.close) && (thirdDay.close < secondDay.close);
  
  if (!sequentialDownClose) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'triple_crash',
      direction: 'neutral'
    };
  }
  
  // 计算每根K线的跌幅百分比
  const firstDayDownPct = (firstDay.open - firstDay.close) / firstDay.open;
  const secondDayDownPct = (secondDay.open - secondDay.close) / secondDay.open;
  const thirdDayDownPct = (thirdDay.open - thirdDay.close) / thirdDay.open;
  
  // 计算总跌幅(从第一根K线的开盘到第三根K线的收盘)
  const totalDownPct = (firstDay.open - thirdDay.close) / firstDay.open;
  
  // 检查至少两根K线为大阴线(跌幅≥3%)
  const bigDownBars = [firstDayDownPct, secondDayDownPct, thirdDayDownPct]
    .filter(pct => pct >= minBigDownBarPct).length;
    
  const hasSufficientBigBars = bigDownBars >= minBigDownBars;
  
  // 检查是否存在跳空缺口
  const hasGapDown1 = secondDay.high < firstDay.low;  // 第一根与第二根之间的跳空
  const hasGapDown2 = thirdDay.high < secondDay.low;  // 第二根与第三根之间的跳空
  const hasAnyGapDown = hasGapDown1 || hasGapDown2;
  
  // 检查成交量特征
  const volumeChange1 = secondDay.volume / firstDay.volume - 1;
  const volumeChange2 = thirdDay.volume / secondDay.volume - 1;
  
  // 成交量放大(恐慌抛售)
  const volumeIncreasing = volumeChange1 > volumeIncreasePct || volumeChange2 > volumeIncreasePct;
  
  // 成交量萎缩(阴跌无承接)- 第三天成交量小于前两天平均值的80%
  const avgVolume = (firstDay.volume + secondDay.volume) / 2;
  const volumeShrinking = thirdDay.volume < avgVolume * 0.8;
  
  // 检查之前是否存在上涨趋势(形态更有效)
  const priorCandles = candles.slice(candles.length - 3 - upTrendConfirmBars, candles.length - 3);
  const priorUptrend = checkUptrend(priorCandles, 0.02);
  
  // 综合判断是否为暴跌三杰形
  const isTripleCrashPattern = allNegativeCandles && sequentialDownClose && 
                              hasSufficientBigBars && totalDownPct >= minTotalDownPct;
                              
  if (!isTripleCrashPattern) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'triple_crash',
      direction: 'neutral'
    };
  }
  
  // 计算暴跌三杰形态的可信度
  let confidence = 0.5; // 基础可信度
  
  // 根据各种因素调整可信度
  // 1. 大阴线数量(最多+0.15)
  confidence += (bigDownBars / 3) * 0.15;
  
  // 2. 总跌幅(最多+0.15)
  confidence += Math.min(totalDownPct / minTotalDownPct, 2) * 0.075;
  
  // 3. 存在跳空缺口(最多+0.1)
  confidence += hasAnyGapDown ? 0.1 : 0;
  
  // 4. 成交量特征(最多+0.1)
  if (volumeIncreasing) {
    confidence += 0.1; // 成交量放大,恐慌抛售
  } else if (volumeShrinking) {
    confidence += 0.05; // 成交量萎缩,阴跌无承接
  }
  
  // 5. 先前上涨趋势(最多+0.1)
  confidence += priorUptrend ? 0.1 : 0;
  
  // 限制最大可信度为1.0
  confidence = Math.min(confidence, 1.0);
  
  // 计算相关的重要价格水平
  const bounceTarget1 = thirdDay.close + (firstDay.open - thirdDay.close) * 0.382; // 38.2%回抽目标
  const bounceTarget2 = thirdDay.close + (firstDay.open - thirdDay.close) * 0.5;   // 50%回抽目标
  const supportLevel = Math.min(firstDay.low, secondDay.low, thirdDay.low);
  
  return {
    detected: true,
    confidence,
    pattern: 'triple_crash',
    direction: 'bearish',
    candleBars: [
      {day: 1, downPct: firstDayDownPct, isBigDown: firstDayDownPct >= minBigDownBarPct},
      {day: 2, downPct: secondDayDownPct, isBigDown: secondDayDownPct >= minBigDownBarPct},
      {day: 3, downPct: thirdDayDownPct, isBigDown: thirdDayDownPct >= minBigDownBarPct}
    ],
    totalDownPct,
    hasGapDown: hasAnyGapDown,
    volumePattern: volumeIncreasing ? 'increasing' : (volumeShrinking ? 'shrinking' : 'neutral'),
    signal: generateTripleCrashSignal(confidence, totalDownPct, thirdDay),
    key_levels: {
      critical_support: supportLevel,
      bounce_target_1: bounceTarget1,
      bounce_target_2: bounceTarget2,
      stop_loss: thirdDay.low * 0.98, // 破位止损点
      breakdown_target: thirdDay.close * (1 - totalDownPct) // 下跌延续目标
    }
  };
}

/**
 * 生成暴跌三杰形态的操作信号
 */
function generateTripleCrashSignal(confidence, totalDownPct, currentCandle) {
  // 已是超跌区域,可能有短期反弹机会(跌幅超过15%)
  if (totalDownPct >= 0.15) {
    return {
      action: "watch_bounce",
      urgency: "medium",
      message: "暴跌三杰形态已形成超跌区域,可能出现技术性反弹",
      lookFor: "关注第四天是否出现止跌信号,如长下影线,缩量十字星",
      position: "仅适合短线交易者轻仓博反弹(≤20%仓位),反弹目标为第二根阴线收盘价"
    };
  }
  // 高置信度,趋势加速向下
  else if (confidence >= 0.8) {
    return {
      action: "strong_sell",
      urgency: "high",
      message: "暴跌三杰形态已确认,下跌趋势极强,建议回避或做空",
      lookFor: "已持仓者应无条件止损,空仓者需远离,直到出现明确底部信号",
      position: "已持仓应减仓至少70%,止损线设在第三根阴线最低点"
    };
  } 
  // 中等置信度,下跌趋势明显
  else if (confidence >= 0.6) {
    return {
      action: "sell",
      urgency: "medium",
      message: "暴跌三杰形态形成,下跌趋势明显,建议减仓或观望",
      lookFor: "持仓者可设置移动止损,空仓者等待反弹后再考虑介入",
      position: "已持仓应减仓50%,第四日若继续下跌应完全清仓"
    };
  } 
  // 低置信度,需进一步观察
  else {
    return {
      action: "caution",
      urgency: "low",
      message: "出现疑似暴跌三杰形态,建议谨慎持仓",
      lookFor: "观察后续走势,特别是成交量变化和是否跌破支撑位",
      position: "可减仓30%,设置好止损位"
    };
  }
}

/**
 * 检测上升受阻形态
 * 上升受阻形是股价在上升趋势中遇阻,多头动能衰减的信号
 * 特征:
 * 1. 出现在一段上涨趋势末端,由2-3根K线组成
 * 2. 第一根为中阳线或大阳线(延续涨势)
 * 3. 随后1-2根K线为带长上影线的小阳线,十字星或小阴线
 * 4. 实体较短,上影线长度≥实体2倍(表明冲高后回落,空方开始反击)
 */
export function detectRisingObstaclePattern(candles, options = {}) {
  const {
    upTrendBars = 5,                // 上涨趋势确认K线数量
    upTrendThreshold = 0.05,        // 上涨趋势确认阈值(5%)
    minBodySize = 0.6,              // 第一根阳线实体占比的最小值
    upperShadowMultiple = 2.0,      // 上影线长度是实体的倍数(至少2倍)
    volumeIncreasePct = 0.3,        // 成交量增加比例(30%)
    maxBodySizeRatio = 0.4,         // 后续K线的最大实体/前一根实体比例
    resistanceZone = 0.01,          // 阻力区域定义(前高的1%以内)
    minPriorGain = 0.08             // 此前最小涨幅(8%)
  } = options;
  
  // 确保有足够的K线数据
  if (candles.length < upTrendBars + 3) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'rising_obstacle',
      direction: 'neutral'
    };
  }
  
  // 获取最近的几根K线
  const lastCandle = candles[candles.length - 1];     // 最近的K线
  const secondLastCandle = candles[candles.length - 2]; // 倒数第二根K线
  const thirdLastCandle = candles[candles.length - 3];  // 倒数第三根K线
  
  // 检查前期是否有明显上涨趋势
  const trendCandles = candles.slice(candles.length - upTrendBars - 3, candles.length - 3);
  const isUptrend = checkUptrend(trendCandles, upTrendThreshold);
  
  if (!isUptrend) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'rising_obstacle',
      direction: 'neutral'
    };
  }
  
  // 计算此前的累计涨幅
  const priorGain = (thirdLastCandle.close - trendCandles[0].close) / trendCandles[0].close;
  if (priorGain < minPriorGain) {
    // 涨幅不足,不算明显上涨趋势
    return {
      detected: false,
      confidence: 0,
      pattern: 'rising_obstacle',
      direction: 'neutral'
    };
  }
  
  // 检查第一根是否为阳线且实体较大
  const thirdLastIsPositive = thirdLastCandle.close > thirdLastCandle.open;
  const thirdLastBodySize = Math.abs(thirdLastCandle.close - thirdLastCandle.open) / (thirdLastCandle.high - thirdLastCandle.low);
  const thirdLastHasLargeBody = thirdLastIsPositive && thirdLastBodySize >= minBodySize;
  
  if (!thirdLastHasLargeBody) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'rising_obstacle',
      direction: 'neutral'
    };
  }
  
  // 检查是否处于阻力区域(前期高点附近)
  const priorHighs = [];
  // 查找前20根K线的高点
  for (let i = 0; i < Math.min(20, candles.length - upTrendBars - 3); i++) {
    priorHighs.push(candles[i].high);
  }
  const maxPriorHigh = Math.max(...priorHighs);
  const nearResistance = Math.abs(secondLastCandle.high - maxPriorHigh) / maxPriorHigh <= resistanceZone;
  
  // 检查随后的K线是否有长上影线
  // 计算第二根K线的特征
  const secondLastUpperShadow = secondLastCandle.high - Math.max(secondLastCandle.open, secondLastCandle.close);
  const secondLastBody = Math.abs(secondLastCandle.close - secondLastCandle.open);
  const secondLastHasLongUpperShadow = secondLastUpperShadow >= secondLastBody * upperShadowMultiple;
  const secondLastSmallBody = secondLastBody <= (Math.abs(thirdLastCandle.close - thirdLastCandle.open) * maxBodySizeRatio);
  
  // 计算最后一根K线的特征
  const lastUpperShadow = lastCandle.high - Math.max(lastCandle.open, lastCandle.close);
  const lastBody = Math.abs(lastCandle.close - lastCandle.open);
  const lastHasLongUpperShadow = lastUpperShadow >= lastBody * upperShadowMultiple;
  const lastSmallBody = lastBody <= (Math.abs(thirdLastCandle.close - thirdLastCandle.open) * maxBodySizeRatio);
  
  // 判断是否为"阳孕线"形态 - 第二根K线完全被第一根K线包含
  const isHaramiPattern = (secondLastCandle.high <= thirdLastCandle.high) && 
                          (secondLastCandle.low >= thirdLastCandle.low) &&
                          (secondLastBody <= thirdLastBodySize * 0.5);
  
  // 判断是否为"平顶形态" - 连续K线的最高价几乎相同
  const isFlatTopPattern = Math.abs(secondLastCandle.high - thirdLastCandle.high) / thirdLastCandle.high < 0.005 ||
                           Math.abs(lastCandle.high - secondLastCandle.high) / secondLastCandle.high < 0.005;
  
  // 量能特征检查
  const volumeIncreased = secondLastCandle.volume > thirdLastCandle.volume * (1 + volumeIncreasePct);
  const volumeDecreased = secondLastCandle.volume < thirdLastCandle.volume * 0.7;
  
  // 检查是否符合上升受阻形态的任一种表现
  const hasLongUpperShadowPattern = (secondLastHasLongUpperShadow && secondLastSmallBody) || 
                                    (lastHasLongUpperShadow && lastSmallBody);
  
  // 确认是否为上升受阻形态
  const isRisingObstaclePattern = thirdLastHasLargeBody && 
                                  (hasLongUpperShadowPattern || isHaramiPattern || isFlatTopPattern);
  
  if (!isRisingObstaclePattern) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'rising_obstacle',
      direction: 'neutral'
    };
  }
  
  // 计算置信度
  // 1. 基础置信度
  let confidence = 0.5;
  
  // 2. 根据上影线长度调整(最多+0.15)
  if (secondLastHasLongUpperShadow) {
    confidence += Math.min(secondLastUpperShadow / (secondLastBody * upperShadowMultiple), 1.5) * 0.1;
  }
  if (lastHasLongUpperShadow) {
    confidence += Math.min(lastUpperShadow / (lastBody * upperShadowMultiple), 1.5) * 0.05;
  }
  
  // 3. 处于阻力位附近(+0.1)
  if (nearResistance) {
    confidence += 0.1;
  }
  
  // 4. 成交量特征(最多+0.1)
  if (volumeIncreased) {
    // 成交量放大,抛压释放更明显
    confidence += 0.1;
  } else if (volumeDecreased) {
    // 成交量萎缩,上涨动能不足
    confidence += 0.05;
  }
  
  // 5. 前期累计涨幅(最多+0.15)
  confidence += Math.min(priorGain / minPriorGain, 3) * 0.05;
  
  // 6. 特殊形态额外加分
  if (isHaramiPattern) {
    confidence += 0.05; // 阳孕线形态
  }
  if (isFlatTopPattern) {
    confidence += 0.05; // 平顶形态
  }
  
  // 限制最大置信度为1.0
  confidence = Math.min(confidence, 1.0);
  
  // 生成警示级别和操作建议
  const action = generateRisingObstacleAction(confidence, volumeIncreased, nearResistance, lastCandle);
  
  // 计算关键价格水平
  const obstacleLevel = Math.max(secondLastCandle.high, lastCandle.high);
  const supportLevel = Math.min(
    Math.min(secondLastCandle.low, lastCandle.low),
    thirdLastCandle.close
  );
  
  // 基于模式特征生成预期目标
  const shortTermTarget = supportLevel - (obstacleLevel - supportLevel) * 0.618; // 短期回调目标
  const breakoutTarget = obstacleLevel + (obstacleLevel - supportLevel) * 0.5;  // 突破目标
  
  return {
    detected: true,
    confidence,
    pattern: 'rising_obstacle',
    direction: 'bearish',
    subPattern: hasLongUpperShadowPattern ? 'long_upper_shadow' : 
                isHaramiPattern ? 'harami' : 
                isFlatTopPattern ? 'flat_top' : 'combined',
    volumeFeature: volumeIncreased ? 'increasing' : (volumeDecreased ? 'decreasing' : 'neutral'),
    nearResistance,
    priorGain,
    signal: action,
    key_levels: {
      obstacle: obstacleLevel,               // 阻力位/受阻点
      immediate_support: supportLevel,       // 即时支撑位
      ma_support: null,                      // 移动平均线支撑位(需在策略中计算)
      stop_loss: supportLevel * 0.98,        // 建议止损点(支撑位下方2%)
      short_term_target: shortTermTarget,    // 短期回调目标
      breakout_target: breakoutTarget        // 突破目标
    }
  };
}

/**
 * 生成上升受阻形态的操作建议
 */
function generateRisingObstacleAction(confidence, volumeIncreased, nearResistance, currentCandle) {
  // 高置信度,强烈警示信号
  if (confidence >= 0.8) {
    return {
      action: "reduce_position",
      urgency: "high",
      message: "上升受阻形态确认,建议大幅减仓至少50%,设置剩余仓位止损",
      lookFor: "关注能否站稳当前支撑,跌破支撑则清仓,企稳反弹则可少量回补",
      position: "建议减仓50%-70%,剩余仓位止损设在支撑位下方2%处"
    };
  } 
  // 中等置信度,减仓观望
  else if (confidence >= 0.6) {
    return {
      action: "partial_reduce",
      urgency: "medium",
      message: "上升受阻形态初现,建议减仓30%观望",
      lookFor: "若接下来2-3个交易日内突破受阻点,可重新买入;若跌破支撑位则继续减仓",
      position: "建议减仓30%,暂时观望,设置移动止损位"
    };
  } 
  // 低置信度,需更多确认信号
  else {
    return {
      action: "watch",
      urgency: "low",
      message: "出现疑似上升受阻信号,建议保持警惕",
      lookFor: "关注接下来的量价配合,若缩量整理企稳可持仓,否则考虑减仓",
      position: "可考虑小幅减仓10%-20%降低风险,同时设置止损位"
    };
  }
}

/**
 * 检测三个白武士形态
 * 三个白武士是一种强烈的底部反转信号,通常出现在下跌趋势末端
 * 特征:
 * 1. 连续三根中大阳线,每根K线收盘价都高于前一根
 * 2. 每根K线的开盘价都在前一根实体范围内或接近前一根收盘价
 * 3. 实体较长,上影线较短,表明买方强势推动
 * 4. 成交量随着形态的发展逐渐放大
 */
export function detectThreeWhiteSoldiers(candles, options = {}) {
  const {
    minBodySizeRatio = 0.6,       // 实体占整个K线的最小比例(60%)
    maxUpperShadowRatio = 0.15,   // 上影线占实体的最大比例(15%)
    minBodyOverlap = 0.1,         // 开盘价与前一日收盘价最小重叠比例(10%)
    volumeIncreasePct = 0.1,      // 成交量逐步放大的最小比例(10%)
    downTrendBars = 5,            // 下跌趋势确认K线数量
    downTrendThreshold = 0.05,    // 下跌趋势确认阈值(5%)
    minGainPct = 0.04             // 三根K线最小累计涨幅(4%)
  } = options;
  
  // 确保有足够的K线数据
  if (candles.length < downTrendBars + 3) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'three_white_soldiers',
      direction: 'neutral'
    };
  }
  
  // 获取最近的三根K线
  const firstDay = candles[candles.length - 3];   // 第一根阳线
  const secondDay = candles[candles.length - 2];  // 第二根阳线 
  const thirdDay = candles[candles.length - 1];   // 第三根阳线
  
  // 检查下跌趋势(确认是否处于底部区域)
  const trendCandles = candles.slice(candles.length - downTrendBars - 3, candles.length - 3);
  const isDowntrend = checkDowntrend(trendCandles, downTrendThreshold);
  
  if (!isDowntrend) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'three_white_soldiers',
      direction: 'neutral'
    };
  }
  
  // 检查三根K线是否均为阳线
  const firstDayIsBullish = firstDay.close > firstDay.open;
  const secondDayIsBullish = secondDay.close > secondDay.open; 
  const thirdDayIsBullish = thirdDay.close > thirdDay.open;
  const allBullishCandles = firstDayIsBullish && secondDayIsBullish && thirdDayIsBullish;
  
  if (!allBullishCandles) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'three_white_soldiers',
      direction: 'neutral'
    };
  }
  
  // 检查每根K线收盘价是否高于前一根
  const sequentialHigherClose = (secondDay.close > firstDay.close) && (thirdDay.close > secondDay.close);
  
  if (!sequentialHigherClose) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'three_white_soldiers',
      direction: 'neutral'
    };
  }
  
  // 计算实体占比和上影线比例
  const getBodySize = (candle) => Math.abs(candle.close - candle.open) / (candle.high - candle.low);
  const getUpperShadow = (candle) => (candle.high - candle.close) / Math.abs(candle.close - candle.open);
  
  const firstDayBodySize = getBodySize(firstDay);
  const secondDayBodySize = getBodySize(secondDay);
  const thirdDayBodySize = getBodySize(thirdDay);
  
  const firstDayUpperShadow = getUpperShadow(firstDay);
  const secondDayUpperShadow = getUpperShadow(secondDay);
  const thirdDayUpperShadow = getUpperShadow(thirdDay);
  
  // 检查实体是否足够长
  const allLargeBodies = (firstDayBodySize >= minBodySizeRatio) && 
                         (secondDayBodySize >= minBodySizeRatio) && 
                         (thirdDayBodySize >= minBodySizeRatio);
  
  // 检查上影线是否足够短
  const allSmallUpperShadows = (firstDayUpperShadow <= maxUpperShadowRatio) && 
                               (secondDayUpperShadow <= maxUpperShadowRatio) && 
                               (thirdDayUpperShadow <= maxUpperShadowRatio);
  
  // 检查开盘价是否在前一根实体范围内或接近前一根收盘价
  const openWithinPrevBody = ((secondDay.open >= firstDay.open) && (secondDay.open <= firstDay.close)) ||
                             (Math.abs(secondDay.open - firstDay.close) / firstDay.close <= minBodyOverlap);
  
  const thirdOpenWithinPrevBody = ((thirdDay.open >= secondDay.open) && (thirdDay.open <= secondDay.close)) ||
                                  (Math.abs(thirdDay.open - secondDay.close) / secondDay.close <= minBodyOverlap);
  
  const properOpeningPrices = openWithinPrevBody && thirdOpenWithinPrevBody;
  
  // 检查成交量是否逐渐放大
  const volumeIncreasing = (secondDay.volume >= firstDay.volume * (1 + volumeIncreasePct)) && 
                          (thirdDay.volume >= secondDay.volume * (1 + volumeIncreasePct));
  
  // 计算三根K线累计涨幅
  const totalGainPct = (thirdDay.close - firstDay.open) / firstDay.open;
  const hasMinimumGain = totalGainPct >= minGainPct;
  
  // 综合判断是否为三个白武士形态
  const isThreeWhiteSoldiers = allBullishCandles && sequentialHigherClose && 
                               allLargeBodies && allSmallUpperShadows && 
                               properOpeningPrices && hasMinimumGain;
                              
  if (!isThreeWhiteSoldiers) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'three_white_soldiers',
      direction: 'neutral'
    };
  }
  
  // 计算三个白武士形态的可信度
  let confidence = 0.5; // 基础可信度
  
  // 根据各种因素调整可信度
  // 1. 实体大小和上影线比例(最多+0.15)
  const bodySizeScore = ((firstDayBodySize + secondDayBodySize + thirdDayBodySize) / 3 - minBodySizeRatio) / (1 - minBodySizeRatio);
  const upperShadowScore = 1 - ((firstDayUpperShadow + secondDayUpperShadow + thirdDayUpperShadow) / 3) / maxUpperShadowRatio;
  confidence += Math.min(bodySizeScore * 0.075 + upperShadowScore * 0.075, 0.15);
  
  // 2. 开盘价位置(最多+0.1)
  confidence += properOpeningPrices ? 0.1 : 0;
  
  // 3. 下跌趋势强度和反转价值(最多+0.15)
  const trendStrengthScore = calculateTrendStrength(trendCandles, true);
  confidence += trendStrengthScore * 0.15;
  
  // 4. 成交量特征(最多+0.1)
  if (volumeIncreasing) {
    confidence += 0.1;
  } else if (thirdDay.volume > firstDay.volume * (1 + volumeIncreasePct)) {
    confidence += 0.05; // 至少第三天成交量有明显放大
  }
  
  // 5. 总涨幅(最多+0.1)
  confidence += Math.min(totalGainPct / (minGainPct * 2), 1) * 0.1;
  
  // 限制最大可信度为1.0
  confidence = Math.min(confidence, 1.0);
  
  // 计算关键价格水平
  const breakoutLevel = thirdDay.close; // 突破水平为第三根K线收盘价
  const supportLevel = Math.min(firstDay.low, secondDay.low, thirdDay.low); // 支撑位为三根K线最低点
  const initialTarget = thirdDay.close * (1 + totalGainPct); // 初始目标为同等涨幅延续
  const stopLoss = supportLevel * 0.98; // 止损位为支撑位下方2%
  
  return {
    detected: true,
    confidence,
    pattern: 'three_white_soldiers',
    direction: 'bullish',
    totalGainPct,
    volumeIncreasing,
    candleBars: [
      {day: 1, bodySize: firstDayBodySize, upperShadow: firstDayUpperShadow},
      {day: 2, bodySize: secondDayBodySize, upperShadow: secondDayUpperShadow},
      {day: 3, bodySize: thirdDayBodySize, upperShadow: thirdDayUpperShadow}
    ],
    signal: generateThreeWhiteSoldiersSignal(confidence, totalGainPct, volumeIncreasing, thirdDay),
    key_levels: {
      breakout: breakoutLevel,
      support: supportLevel,
      target_1: initialTarget,
      target_2: initialTarget * 1.5, // 进取目标
      stop_loss: stopLoss
    }
  };
}

/**
 * 生成三个白武士形态的操作信号
 */
function generateThreeWhiteSoldiersSignal(confidence, totalGainPct, volumeIncreasing, currentCandle) {
  // 高置信度,强烈买入信号
  if (confidence >= 0.8) {
    return {
      action: "strong_buy",
      urgency: "high",
      message: "三个白武士形态确认,强烈看涨信号已形成",
      lookFor: "可以在短期回调时介入,止损设在支撑位下方",
      position: "建议仓位60%-80%,可分批建仓,第一批30%仓位"
    };
  } 
  // 中等置信度,积极买入信号
  else if (confidence >= 0.6) {
    return {
      action: "buy",
      urgency: "medium",
      message: "三个白武士形态形成,看涨反转信号已确认",
      lookFor: "可在第四天若继续上涨时跟进,或在回调至第三根K线实体中部时买入",
      position: "建议仓位40%-60%,分批建仓,第一批20%仓位"
    };
  } 
  // 低置信度,谨慎买入信号
  else {
    return {
      action: "watch_buy",
      urgency: "low",
      message: "出现疑似三个白武士形态,需进一步确认",
      lookFor: "关注第四天能否继续上涨,若出现回调,关注是否能守住第二根K线收盘价",
      position: "建议先观望,确认突破后轻仓介入(20%仓位)"
    };
  }
}

/**
 * 检测顶部三鸭形态
 * 顶部三鸭形是一种常见的顶部反转信号,通常出现在上涨趋势末端
 * 特征:
 * 1. 连续三根阴线,每根K线收盘价低于前一根
 * 2. 出现在明显的上涨趋势后(股价创新高或加速上涨后)
 * 3. 可能伴随跳空低开,放量下跌或跌破关键支撑
 * 4. 表明多方力量衰竭,空方开始主导市场
 */
export function detectTopThreeDucks(candles, options = {}) {
  const {
    upTrendBars = 5,               // 上涨趋势确认K线数量
    upTrendThreshold = 0.05,       // 上涨趋势确认阈值(5%)
    volumeIncreasePct = 0.2,       // 成交量放大确认阈值(20%)
    minBodySizeRatio = 0.4,        // 阴线实体占K线的最小比例(40%)
    bearCandlesRequired = 3,       // 需要的连续阴线数量
    mustBreakMA5 = true,           // 是否必须跌破5日均线
    checkWithPriorHigh = true,     // 是否检查是否接近前期高点
    priorHighThreshold = 0.03      // 接近前期高点的阈值(3%)
  } = options;
  
  // 确保有足够的K线数据
  if (candles.length < upTrendBars + bearCandlesRequired) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'top_three_ducks',
      direction: 'neutral'
    };
  }
  
  // 获取最近的三根K线
  const recentCandles = candles.slice(candles.length - bearCandlesRequired);
  
  // 检查上涨趋势(查看前N天是否有明显上涨)
  const trendCandles = candles.slice(candles.length - upTrendBars - bearCandlesRequired, candles.length - bearCandlesRequired);
  const isUptrend = checkUptrend(trendCandles, upTrendThreshold);
  
  if (!isUptrend) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'top_three_ducks',
      direction: 'neutral'
    };
  }
  
  // 检查是否处于高位(接近前期高点)
  let nearPriorHigh = false;
  if (checkWithPriorHigh) {
    const priorCandles = candles.slice(0, candles.length - bearCandlesRequired - upTrendBars);
    if (priorCandles.length > 10) {
      const priorHigh = Math.max(...priorCandles.map(c => c.high));
      const currentHigh = Math.max(...trendCandles.map(c => c.high));
      nearPriorHigh = (Math.abs(currentHigh - priorHigh) / priorHigh) <= priorHighThreshold;
    }
  }
  
  // 检查最近三根K线是否均为阴线
  const allBearish = recentCandles.every(candle => candle.close < candle.open);
  
  if (!allBearish) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'top_three_ducks',
      direction: 'neutral'
    };
  }
  
  // 检查是否连续收低(每根K线收盘价低于前一根)
  let sequentialLowerClose = true;
  for (let i = 1; i < recentCandles.length; i++) {
    if (recentCandles[i].close >= recentCandles[i-1].close) {
      sequentialLowerClose = false;
      break;
    }
  }
  
  if (!sequentialLowerClose) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'top_three_ducks',
      direction: 'neutral'
    };
  }
  
  // 检查阴线实体是否足够大
  const bodySizes = recentCandles.map(candle => {
    return Math.abs(candle.open - candle.close) / (candle.high - candle.low);
  });
  
  const allLargeBodies = bodySizes.every(size => size >= minBodySizeRatio);
  
  // 检查是否有跳空低开
  const hasGapDown = recentCandles.some((candle, i) => {
    if (i === 0) return false;
    return candle.high < recentCandles[i-1].low;
  });
  
  // 检查成交量特征
  // 1. 放量下跌:后续阴线成交量大于前面阴线
  const volumeIncreasing = (recentCandles[1].volume > recentCandles[0].volume) || 
                           (recentCandles[2].volume > recentCandles[1].volume);
  
  // 2. 第三根阴线成交量是否显著高于前两根阴线的平均值
  const avgVolume = (recentCandles[0].volume + recentCandles[1].volume) / 2;
  const lastCandleVolumeIncreased = recentCandles[2].volume > avgVolume * (1 + volumeIncreasePct);
  
  // 计算5日均线
  const ma5 = calculateMA(candles, 5);
  
  // 检查是否跌破5日均线
  let breakMA5 = false;
  if (ma5.length >= 3) {
    // 至少有一根阴线的收盘价跌破5日均线
    breakMA5 = recentCandles.some((candle, i) => {
      const ma5Index = ma5.length - bearCandlesRequired + i;
      return ma5Index >= 0 && candle.close < ma5[ma5Index];
    });
  }
  
  if (mustBreakMA5 && !breakMA5) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'top_three_ducks',
      direction: 'neutral'
    };
  }
  
  // 计算累计跌幅
  const totalDeclinePct = (recentCandles[0].open - recentCandles[recentCandles.length - 1].close) / recentCandles[0].open;
  
  // 综合判断是否为顶部三鸭形态
  const isTopThreeDucks = allBearish && sequentialLowerClose && 
                         (allLargeBodies || breakMA5 || hasGapDown || lastCandleVolumeIncreased);
                         
  if (!isTopThreeDucks) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'top_three_ducks',
      direction: 'neutral'
    };
  }
  
  // 计算形态可信度
  let confidence = 0.5; // 基础可信度
  
  // 基于各种因素调整可信度
  // 1. 阴线实体大小(最多+0.1)
  const bodyScore = Math.min(bodySizes.reduce((sum, size) => sum + size, 0) / bodySizes.length / minBodySizeRatio, 2) * 0.05;
  confidence += bodyScore;
  
  // 2. 是否跳空低开(+0.1)
  if (hasGapDown) {
    confidence += 0.1;
  }
  
  // 3. 成交量特征(最多+0.1)
  if (lastCandleVolumeIncreased) {
    confidence += 0.1;
  } else if (volumeIncreasing) {
    confidence += 0.05;
  }
  
  // 4. 跌破5日均线(+0.1)
  if (breakMA5) {
    confidence += 0.1;
  }
  
  // 5. 接近前期高点(+0.1)
  if (nearPriorHigh) {
    confidence += 0.1;
  }
  
  // 6. 累计跌幅(最多+0.1)
  confidence += Math.min(totalDeclinePct / 0.05, 1) * 0.1; // 如果跌幅达到5%,加分0.1
  
  // 限制最大可信度为1.0
  confidence = Math.min(confidence, 1.0);
  
  // 计算关键价格水平
  const resistanceLevel = recentCandles[0].high; // 阻力位为第一根阴线的最高点
  const supportLevel = recentCandles[recentCandles.length - 1].low; // 支撑位为最后一根阴线的最低点
  const stopLossLevel = resistanceLevel * 1.02; // 止损位为阻力位上方2%
  
  return {
    detected: true,
    confidence,
    pattern: 'top_three_ducks',
    direction: 'bearish',
    hasGapDown,
    breakMA5,
    totalDeclinePct,
    volumeFeature: lastCandleVolumeIncreased ? 'increasing' : (volumeIncreasing ? 'slightly_increasing' : 'neutral'),
    signal: generateTopThreeDucksSignal(confidence, breakMA5, lastCandleVolumeIncreased, totalDeclinePct),
    key_levels: {
      resistance: resistanceLevel,
      stop_loss: stopLossLevel,
      support: supportLevel,
      target1: supportLevel * (1 - totalDeclinePct), // 目标1: 延续同等跌幅
      target2: supportLevel * (1 - totalDeclinePct * 1.5) // 目标2: 延续更大跌幅
    }
  };
}

/**
 * 计算移动平均线
 */
function calculateMA(candles, period) {
  if (candles.length < period) {
    return [];
  }
  
  const result = [];
  for (let i = period - 1; i < candles.length; i++) {
    const sum = candles.slice(i - period + 1, i + 1).reduce((acc, candle) => acc + candle.close, 0);
    result.push(sum / period);
  }
  
  return result;
}

/**
 * 生成顶部三鸭形态的操作信号
 */
function generateTopThreeDucksSignal(confidence, breakMA5, volumeIncreased, totalDeclinePct) {
  // 高置信度,强烈卖出信号
  if (confidence >= 0.8) {
    return {
      action: "strong_sell",
      urgency: "high",
      message: "顶部三鸭形态确认,强烈下跌信号,建议清仓离场",
      lookFor: "可在反弹至第二根阴线实体中部时加仓做空",
      position: "若持有多仓应立即清仓,空仓者可在反弹时少量做空(建议仓位20%-30%)"
    };
  } 
  // 中等置信度,减仓信号
  else if (confidence >= 0.6) {
    return {
      action: "reduce_position",
      urgency: "medium",
      message: "顶部三鸭形态形成,建议大幅减仓观望",
      lookFor: "密切关注能否企稳,跌破第三根阴线低点则清仓",
      position: "建议减仓50%-70%,设置止损在阻力位上方2%处"
    };
  } 
  // 低置信度,预警信号
  else {
    return {
      action: "caution",
      urgency: "low",
      message: "出现疑似顶部三鸭形态,需密切关注后市走向",
      lookFor: "若第四天继续下跌则减仓,若强势反弹站上5日线则可继续持有",
      position: "可考虑小幅减仓30%降低风险,并设置好止损位"
    };
  }
} 

/**
 * 检测双绿并行形态
 * 双绿并行形是一种常见的K线组合,通常出现在下跌趋势或盘整阶段
 * 特征:
 * 1. 由两根连续的阴线组成,两根阴线的实体长度相近
 * 2. 两根阴线的开盘价与收盘价区间基本平行
 * 3. 根据位置与量能配合判断是下跌中继,高位见顶还是低位探底信号
 */
export function detectDoubleGreenParallel(candles, options = {}) {
  const {
    parallelThreshold = 0.03,       // 开盘价与收盘价平行度阈值(3%)
    bodyLengthRatio = 0.7,          // 两根K线实体长度比例的最小值(70%)
    minBodySizeRatio = 0.4,         // 阴线实体占K线的最小比例(40%)
    volumeIncreaseThreshold = 0.3,  // 放量阈值(30%)
    volumeDecreaseThreshold = 0.3,  // 缩量阈值(30%)
    priorBarsToCheck = 10,          // 检查前期趋势的K线数量
    upTrendThreshold = 0.05,        // 上涨趋势确认阈值(5%)
    downTrendThreshold = 0.05,      // 下跌趋势确认阈值(5%)
    checkMA60 = true,               // 是否检查60日均线突破
    checkMA5 = true                 // 是否检查5日均线突破
  } = options;
  
  // 确保有足够的K线数据
  if (candles.length < priorBarsToCheck + 2) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'double_green_parallel',
      direction: 'neutral'
    };
  }
  
  // 获取最近的两根K线
  const secondBar = candles[candles.length - 1];  // 最新的K线
  const firstBar = candles[candles.length - 2];   // 倒数第二根K线
  
  // 检查是否都是阴线
  const firstIsBearish = firstBar.close < firstBar.open;
  const secondIsBearish = secondBar.close < secondBar.open;
  
  if (!firstIsBearish || !secondIsBearish) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'double_green_parallel',
      direction: 'neutral'
    };
  }
  
  // 计算两根K线的实体长度
  const firstBodyLength = Math.abs(firstBar.open - firstBar.close);
  const secondBodyLength = Math.abs(secondBar.open - secondBar.close);
  
  // 检查两根K线的实体长度是否相近
  const bodyLengthSimilarity = Math.min(firstBodyLength, secondBodyLength) / 
                               Math.max(firstBodyLength, secondBodyLength);
  
  if (bodyLengthSimilarity < bodyLengthRatio) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'double_green_parallel',
      direction: 'neutral'
    };
  }
  
  // 检查实体占比是否足够大
  const firstBodyRatio = firstBodyLength / (firstBar.high - firstBar.low);
  const secondBodyRatio = secondBodyLength / (secondBar.high - secondBar.low);
  
  if (firstBodyRatio < minBodySizeRatio || secondBodyRatio < minBodySizeRatio) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'double_green_parallel',
      direction: 'neutral'
    };
  }
  
  // 检查开盘价和收盘价是否平行
  const openPriceDiff = Math.abs(firstBar.open - secondBar.open) / firstBar.open;
  const closePriceDiff = Math.abs(firstBar.close - secondBar.close) / firstBar.close;
  
  const isPriceParallel = openPriceDiff <= parallelThreshold && 
                           closePriceDiff <= parallelThreshold;
  
  if (!isPriceParallel) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'double_green_parallel',
      direction: 'neutral'
    };
  }
  
  // 检查成交量特征
  const isVolumeIncreased = secondBar.volume > firstBar.volume * (1 + volumeIncreaseThreshold);
  const isVolumeDecreased = secondBar.volume < firstBar.volume * (1 - volumeDecreaseThreshold);
  
  // 确定成交量特征
  let volumeFeature;
  if (isVolumeIncreased) {
    volumeFeature = 'increasing';
  } else if (isVolumeDecreased) {
    volumeFeature = 'decreasing';
  } else {
    volumeFeature = 'neutral';
  }
  
  // 分析前期趋势
  const priorCandles = candles.slice(candles.length - priorBarsToCheck - 2, candles.length - 2);
  const isUptrend = checkUptrend(priorCandles, upTrendThreshold);
  const isDowntrend = checkDowntrend(priorCandles, downTrendThreshold);
  
  // 确定所处位置(高位,中继,低位)
  let positionType;
  if (isUptrend) {
    positionType = 'high'; // 高位见顶
  } else if (isDowntrend) {
    positionType = 'middle'; // 下跌中继
  } else {
    // 检查是否处于历史低位
    const historicalLows = candles.slice(0, candles.length - 2).map(c => c.low);
    const minLow = Math.min(...historicalLows);
    const currentLow = Math.min(firstBar.low, secondBar.low);
    
    if (Math.abs(currentLow - minLow) / minLow <= 0.05) {
      positionType = 'low'; // 低位探底
    } else {
      positionType = 'neutral'; // 中性位置
    }
  }
  
  // 计算均线
  let ma5Broken = false;
  let ma60Broken = false;
  
  if (checkMA5 || checkMA60) {
    const ma5 = calculateMA(candles, 5);
    const ma60 = checkMA60 ? calculateMA(candles, 60) : [];
    
    if (checkMA5 && ma5.length >= 2) {
      const lastMa5Index = ma5.length - 1;
      ma5Broken = secondBar.close < ma5[lastMa5Index] && firstBar.close < ma5[lastMa5Index - 1];
    }
    
    if (checkMA60 && ma60.length >= 2) {
      const lastMa60Index = ma60.length - 1;
      ma60Broken = secondBar.close < ma60[lastMa60Index] && firstBar.close < ma60[lastMa60Index - 1];
    }
  }
  
  // 确认双绿并行形态
  const isDoubleGreenParallel = isPriceParallel && 
                               bodyLengthSimilarity >= bodyLengthRatio && 
                               firstIsBearish && secondIsBearish;
  
  if (!isDoubleGreenParallel) {
    return {
      detected: false,
      confidence: 0,
      pattern: 'double_green_parallel',
      direction: 'neutral'
    };
  }
  
  // 计算形态可信度
  let confidence = 0.5; // 基础可信度
  
  // 基于各种因素调整可信度
  // 1. 实体长度相似度(最多+0.1)
  confidence += Math.min((bodyLengthSimilarity - bodyLengthRatio) / (1 - bodyLengthRatio), 1) * 0.1;
  
  // 2. 开盘价收盘价平行度(最多+0.1)
  const parallelScore = 1 - Math.max(openPriceDiff, closePriceDiff) / parallelThreshold;
  confidence += parallelScore * 0.1;
  
  // 3. 位置特征(最多+0.1)
  if (positionType === 'high' && isVolumeIncreased) {
    confidence += 0.1; // 高位放量,见顶信号更强
  } else if (positionType === 'low' && isVolumeDecreased) {
    confidence += 0.1; // 低位缩量,探底信号更强
  } else if (positionType === 'middle' && isVolumeIncreased) {
    confidence += 0.1; // 中继位置放量,下跌延续信号更强
  }
  
  // 4. 均线突破确认(最多+0.1)
  if (ma5Broken && positionType === 'high') {
    confidence += 0.05; // 高位跌破5日均线,增强信号
  }
  if (ma60Broken && positionType === 'middle') {
    confidence += 0.1; // 跌破60日均线,中继下跌信号更强
  }
  
  // 5. 趋势强度(最多+0.1)
  if (isUptrend) {
    const trendStrength = calculateTrendStrength(priorCandles, false);
    confidence += trendStrength * 0.1;
  } else if (isDowntrend) {
    const trendStrength = calculateTrendStrength(priorCandles, true);
    confidence += trendStrength * 0.1;
  }
  
  // 限制最大可信度为1.0
  confidence = Math.min(confidence, 1.0);
  
  // 确定K线组合的方向
  let direction;
  if (positionType === 'high') {
    direction = 'bearish'; // 看空
  } else if (positionType === 'middle') {
    direction = 'bearish'; // 看空
  } else if (positionType === 'low') {
    direction = isVolumeDecreased ? 'potential_bullish' : 'bearish'; // 低位缩量可能形成底部
  } else {
    direction = 'neutral';
  }
  
  // 计算关键价格水平
  const resistanceLevel = Math.max(firstBar.open, secondBar.open); // 阻力位
  const supportLevel = Math.min(firstBar.close, secondBar.close); // 支撑位
  const stopLossLevel = Math.min(firstBar.low, secondBar.low) * 0.98; // 止损位
  
  // 根据不同位置生成目标价格
  let target1, target2;
  if (positionType === 'high' || positionType === 'middle') {
    // 下跌目标
    const bodyHeight = Math.abs(firstBar.open - firstBar.close);
    target1 = supportLevel - bodyHeight; // 1:1目标
    target2 = supportLevel - bodyHeight * 1.5; // 1.5:1目标
  } else {
    // 反弹目标
    const priorHigh = Math.max(...priorCandles.map(c => c.high));
    target1 = firstBar.open; // 反弹至阴线开盘价
    target2 = Math.min(priorHigh, firstBar.open * 1.05); // 前期高点或阴线开盘价上方5%
  }
  
  return {
    detected: true,
    confidence,
    pattern: 'double_green_parallel',
    direction,
    positionType,
    volumeFeature,
    bodyLengthSimilarity,
    openPriceDiff,
    closePriceDiff,
    ma5Broken,
    ma60Broken,
    signal: generateDoubleGreenParallelSignal(confidence, positionType, volumeFeature, ma5Broken, ma60Broken),
    key_levels: {
      resistance: resistanceLevel,
      support: supportLevel,
      stop_loss: stopLossLevel,
      target1: target1,
      target2: target2
    }
  };
}

/**
 * 生成双绿并行形态的操作信号
 */
function generateDoubleGreenParallelSignal(confidence, positionType, volumeFeature, ma5Broken, ma60Broken) {
  // 高位见顶信号
  if (positionType === 'high') {
    if (confidence >= 0.8 && (volumeFeature === 'increasing' || ma5Broken)) {
      return {
        action: "strong_sell",
        urgency: "high",
        message: "高位双绿并行形态确认,建议清仓离场",
        lookFor: "密切关注后市能否有效企稳,若继续收阴线则保持空仓",
        position: "建议清仓100%,保护之前获利"
      };
    } else if (confidence >= 0.6) {
      return {
        action: "reduce_position",
        urgency: "medium",
        message: "高位出现双绿并行形态,建议减仓观望",
        lookFor: "关注能否重返阴线开盘价上方,否则继续减仓",
        position: "建议减仓50%-70%,设置止损在并行形态最低点下方"
      };
    } else {
      return {
        action: "caution",
        urgency: "low",
        message: "出现疑似双绿并行形态,需注意高位风险",
        lookFor: "设置好止损位,观察第三天走势",
        position: "可考虑减仓30%降低风险"
      };
    }
  }
  // 下跌中继信号
  else if (positionType === 'middle') {
    if (confidence >= 0.8 && (volumeFeature === 'increasing' || ma60Broken)) {
      return {
        action: "sell",
        urgency: "high",
        message: "下跌趋势中的双绿并行形态,下跌可能延续",
        lookFor: "关注支撑位是否被有效跌破",
        position: "建议减仓50%,设置止损在第二根阴线开盘价上方"
      };
    } else if (confidence >= 0.6) {
      return {
        action: "reduce_position",
        urgency: "medium",
        message: "中继位置的双绿并行形态,调整仍在进行",
        lookFor: "等待趋势明确,观察能否企稳",
        position: "建议减仓30%-50%,注意控制风险"
      };
    } else {
      return {
        action: "watch",
        urgency: "low",
        message: "中继位置出现双绿并行,需密切关注后市",
        lookFor: "第三天是否收阳线决定后续操作",
        position: "可保持观望或小幅减仓"
      };
    }
  }
  // 低位探底信号
  else if (positionType === 'low') {
    if (confidence >= 0.8 && volumeFeature === 'decreasing') {
      return {
        action: "watch_buy",
        urgency: "medium",
        message: "低位缩量双绿并行,可能是探底信号",
        lookFor: "等待第三天收阳线且放量确认反转",
        position: "若第三天收阳,可轻仓试探性买入(仓位≤20%)"
      };
    } else if (confidence >= 0.6) {
      return {
        action: "watch",
        urgency: "low",
        message: "低位出现双绿并行,需等待企稳信号",
        lookFor: "关注第三天是阳线还是阴线,以及成交量变化",
        position: "暂时观望,等待更明确的底部确认"
      };
    } else {
      return {
        action: "caution",
        urgency: "low",
        message: "低位出现双绿并行,但信号较弱",
        lookFor: "等待更多技术指标共振确认",
        position: "保持观望"
      };
    }
  }
  // 中性位置
  else {
    return {
      action: "watch",
      urgency: "low",
      message: "出现双绿并行形态,但位置不明确",
      lookFor: "结合其他技术指标判断",
      position: "建议暂时观望"
    };
  }
}
