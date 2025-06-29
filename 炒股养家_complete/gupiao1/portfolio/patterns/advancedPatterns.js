/**
 * 高级形态识别模块
 * 包含波浪理论,江恩理论等高级分析方法
 */

// 波浪理论分析
export function analyzeElliottWaves(prices) {
  // 波浪理论基本参数
  const minWaveLength = 5; // 最小波浪长度
  const maxImpulseWaveCount = 5; // 推动浪数量
  const maxCorrectiveWaveCount = 3; // 调整浪数量
  
  // 寻找关键点位
  const peaks = findPeaks(prices, 5);
  const troughs = findTroughs(prices, 5);
  
  if (peaks.length < 3 || troughs.length < 3) {
    return {
      detected: false,
      confidence: 0,
      waveCount: 0,
      currentWave: 0,
      pattern: 'unknown',
      direction: 'neutral',
      points: []
    };
  }
  
  // 合并并排序所有关键点位
  const allPoints = [...peaks.map(p => ({ index: p, value: prices[p], type: 'peak' })),
                     ...troughs.map(t => ({ index: t, value: prices[t], type: 'trough' }))];
  allPoints.sort((a, b) => a.index - b.index);
  
  // 识别推动浪和调整浪
  const waves = identifyWaves(allPoints, prices);
  
  if (waves.length < 3) {
    return {
      detected: false,
      confidence: 0,
      waveCount: 0,
      currentWave: 0,
      pattern: 'unknown',
      direction: 'neutral',
      points: []
    };
  }
  
  // 确定当前波浪位置
  const currentWaveInfo = determineCurrentWave(waves, prices);
  
  // 计算可信度
  const confidence = calculateWaveConfidence(waves, prices);
  
  // 确定整体趋势方向
  const direction = waves[0].direction === 'up' ? 'bullish' : 'bearish';
  
  return {
    detected: true,
    confidence: confidence,
    waveCount: waves.length,
    currentWave: currentWaveInfo.currentWave,
    pattern: 'elliott_wave',
    direction: direction,
    nextTargets: currentWaveInfo.nextTargets,
    waves: waves,
    points: waves.map(w => w.startPoint.index)
  };
}

// 江恩理论分析
export function analyzeGannTheory(prices, dates) {
  // 江恩角度线参数
  const gannAngles = [
    { angle: 45, ratio: 1, name: '1x1' },   // 45度角,价格时间比为1:1
    { angle: 63.75, ratio: 2, name: '2x1' }, // 价格时间比为2:1
    { angle: 26.25, ratio: 0.5, name: '1x2' }, // 价格时间比为1:2
    { angle: 75, ratio: 3, name: '3x1' },   // 价格时间比为3:1
    { angle: 18.75, ratio: 1/3, name: '1x3' }, // 价格时间比为1:3
    { angle: 82.5, ratio: 4, name: '4x1' },  // 价格时间比为4:1
    { angle: 15, ratio: 1/4, name: '1x4' },  // 价格时间比为1:4
    { angle: 78.75, ratio: 8, name: '8x1' },  // 价格时间比为8:1
    { angle: 7.5, ratio: 1/8, name: '1x8' }   // 价格时间比为1:8
  ];
  
  if (prices.length < 20) {
    return {
      detected: false,
      confidence: 0,
      supportLines: [],
      resistanceLines: [],
      timeSquares: [],
      priceSquares: []
    };
  }
  
  // 寻找关键的高点和低点
  const significantHigh = findSignificantHigh(prices);
  const significantLow = findSignificantLow(prices);
  
  if (!significantHigh || !significantLow) {
    return {
      detected: false,
      confidence: 0,
      supportLines: [],
      resistanceLines: [],
      timeSquares: [],
      priceSquares: []
    };
  }
  
  // 计算江恩角度线
  const angleLines = calculateGannAngles(
    significantLow.index, significantLow.value,
    significantHigh.index, significantHigh.value,
    prices.length,
    gannAngles
  );
  
  // 计算江恩时间平方
  const timeSquares = calculateTimeSquares(
    significantLow.index,
    prices.length
  );
  
  // 计算江恩价格平方
  const priceSquares = calculatePriceSquares(
    significantLow.value,
    significantHigh.value
  );
  
  // 计算支撑和阻力水平
  const supportLines = angleLines.filter(line => line.values[line.values.length - 1] < prices[prices.length - 1]);
  const resistanceLines = angleLines.filter(line => line.values[line.values.length - 1] >= prices[prices.length - 1]);
  
  // 计算当前价格与江恩线的关系
  const currentPrice = prices[prices.length - 1];
  const nearestSupport = supportLines.length > 0 ? 
    supportLines.reduce((prev, curr) => 
      Math.abs(curr.values[curr.values.length - 1] - currentPrice) < Math.abs(prev.values[prev.values.length - 1] - currentPrice) ? curr : prev
    ) : null;
  
  const nearestResistance = resistanceLines.length > 0 ? 
    resistanceLines.reduce((prev, curr) => 
      Math.abs(curr.values[curr.values.length - 1] - currentPrice) < Math.abs(prev.values[prev.values.length - 1] - currentPrice) ? curr : prev
    ) : null;
  
  // 计算可信度
  let confidence = 0.5;
  
  // 如果价格接近支撑或阻力线,增加可信度
  if (nearestSupport) {
    const supportDiff = Math.abs(nearestSupport.values[nearestSupport.values.length - 1] - currentPrice) / currentPrice;
    if (supportDiff < 0.01) confidence += 0.2;
    else if (supportDiff < 0.03) confidence += 0.1;
  }
  
  if (nearestResistance) {
    const resistanceDiff = Math.abs(nearestResistance.values[nearestResistance.values.length - 1] - currentPrice) / currentPrice;
    if (resistanceDiff < 0.01) confidence += 0.2;
    else if (resistanceDiff < 0.03) confidence += 0.1;
  }
  
  // 如果价格接近时间平方点,增加可信度
  const currentIndex = prices.length - 1;
  const nearestTimeSquare = timeSquares.find(ts => Math.abs(ts - currentIndex) <= 1);
  if (nearestTimeSquare) confidence += 0.1;
  
  // 如果价格接近价格平方点,增加可信度
  const nearestPriceSquare = priceSquares.find(ps => Math.abs(ps - currentPrice) / currentPrice <= 0.01);
  if (nearestPriceSquare) confidence += 0.1;
  
  return {
    detected: true,
    confidence: Math.min(confidence, 0.95),
    pattern: 'gann_theory',
    direction: currentPrice > (significantHigh.value + significantLow.value) / 2 ? 'bullish' : 'bearish',
    supportLines,
    resistanceLines,
    timeSquares,
    priceSquares,
    significantHigh,
    significantLow,
    nearestSupport: nearestSupport ? {
      name: nearestSupport.name,
      value: nearestSupport.values[nearestSupport.values.length - 1]
    } : null,
    nearestResistance: nearestResistance ? {
      name: nearestResistance.name,
      value: nearestResistance.values[nearestResistance.values.length - 1]
    } : null
  };
}

// 辅助函数:识别波浪
function identifyWaves(points, prices) {
  const waves = [];
  
  if (points.length < 2) return waves;
  
  let waveStart = points[0];
  let prevPoint = points[0];
  let currentDirection = null;
  
  for (let i = 1; i < points.length; i++) {
    const point = points[i];
    const direction = point.value > prevPoint.value ? 'up' : 'down';
    
    if (currentDirection === null) {
      currentDirection = direction;
    } else if (direction !== currentDirection) {
      // 方向改变,结束当前波浪
      waves.push({
        startPoint: waveStart,
        endPoint: prevPoint,
        direction: currentDirection,
        magnitude: Math.abs(prevPoint.value - waveStart.value),
        duration: prevPoint.index - waveStart.index
      });
      
      // 开始新波浪
      waveStart = prevPoint;
      currentDirection = direction;
    }
    
    prevPoint = point;
  }
  
  // 添加最后一个波浪
  if (currentDirection !== null) {
    waves.push({
      startPoint: waveStart,
      endPoint: prevPoint,
      direction: currentDirection,
      magnitude: Math.abs(prevPoint.value - waveStart.value),
      duration: prevPoint.index - waveStart.index
    });
  }
  
  return waves;
}

// 辅助函数:确定当前波浪位置
function determineCurrentWave(waves, prices) {
  // 根据波浪理论的规则确定当前处于哪个波浪
  // 这是一个简化版本,实际应用中需要更复杂的逻辑
  
  const lastPrice = prices[prices.length - 1];
  const lastWave = waves[waves.length - 1];
  const isUptrend = lastWave.direction === 'up';
  
  // 简单假设:如果最后一个波浪是上升的,可能处于1,3,5浪;如果是下降的,可能处于2,4浪或ABC调整浪
  let currentWave = 0;
  const nextTargets = [];
  
  if (waves.length <= 2) {
    currentWave = isUptrend ? 1 : 2;
  } else if (waves.length <= 4) {
    currentWave = isUptrend ? 3 : 4;
  } else {
    currentWave = isUptrend ? 5 : 'A';
  }
  
  // 计算可能的目标价位
  if (currentWave === 1 || currentWave === 3) {
    // 上升浪的目标通常是前一浪的1.618倍
    const prevWaveMagnitude = waves.length > 1 ? waves[waves.length - 2].magnitude : 0;
    nextTargets.push(lastWave.startPoint.value + prevWaveMagnitude * 1.618);
    nextTargets.push(lastWave.startPoint.value + prevWaveMagnitude * 2.618);
  } else if (currentWave === 2) {
    // 2浪通常回调1浪的0.382到0.618
    const wave1Magnitude = waves[0].magnitude;
    nextTargets.push(waves[0].endPoint.value - wave1Magnitude * 0.382);
    nextTargets.push(waves[0].endPoint.value - wave1Magnitude * 0.5);
    nextTargets.push(waves[0].endPoint.value - wave1Magnitude * 0.618);
  } else if (currentWave === 4) {
    // 4浪通常回调3浪的0.382到0.5
    const wave3Magnitude = waves[waves.length - 2].magnitude;
    nextTargets.push(waves[waves.length - 2].endPoint.value - wave3Magnitude * 0.382);
    nextTargets.push(waves[waves.length - 2].endPoint.value - wave3Magnitude * 0.5);
  } else if (currentWave === 5) {
    // 5浪通常是1浪的0.618到1倍
    const wave1Magnitude = waves[0].magnitude;
    nextTargets.push(lastWave.startPoint.value + wave1Magnitude * 0.618);
    nextTargets.push(lastWave.startPoint.value + wave1Magnitude);
  }
  
  return {
    currentWave,
    nextTargets
  };
}

// 辅助函数:计算波浪可信度
function calculateWaveConfidence(waves, prices) {
  // 这是一个简化版本,实际应用中需要更复杂的逻辑
  let confidence = 0.5;
  
  // 波浪数量符合预期
  if (waves.length === 5) {
    confidence += 0.1;
  }
  
  // 检查波浪长度关系
  if (waves.length >= 3) {
    // 3浪通常是最长的推动浪
    const wave1 = waves[0];
    const wave3 = waves[2];
    
    if (wave3.magnitude > wave1.magnitude) {
      confidence += 0.1;
    }
    
    // 检查2浪回调幅度
    if (waves.length >= 2) {
      const wave2 = waves[1];
      const wave1Retracement = wave2.magnitude / wave1.magnitude;
      
      if (wave1Retracement >= 0.382 && wave1Retracement <= 0.618) {
        confidence += 0.1;
      }
    }
    
    // 检查4浪回调幅度
    if (waves.length >= 4) {
      const wave4 = waves[3];
      const wave3Retracement = wave4.magnitude / wave3.magnitude;
      
      if (wave3Retracement >= 0.236 && wave3Retracement <= 0.5) {
        confidence += 0.1;
      }
    }
  }
  
  return Math.min(confidence, 0.95);
}

// 辅助函数:寻找显著高点
function findSignificantHigh(prices) {
  if (prices.length === 0) return null;
  
  let highIndex = 0;
  let highValue = prices[0];
  
  for (let i = 1; i < prices.length; i++) {
    if (prices[i] > highValue) {
      highIndex = i;
      highValue = prices[i];
    }
  }
  
  return { index: highIndex, value: highValue };
}

// 辅助函数:寻找显著低点
function findSignificantLow(prices) {
  if (prices.length === 0) return null;
  
  let lowIndex = 0;
  let lowValue = prices[0];
  
  for (let i = 1; i < prices.length; i++) {
    if (prices[i] < lowValue) {
      lowIndex = i;
      lowValue = prices[i];
    }
  }
  
  return { index: lowIndex, value: lowValue };
}

// 辅助函数:计算江恩角度线
function calculateGannAngles(startX, startY, pivotX, pivotY, length, angles) {
  const lines = [];
  
  // 使用主要的高低点计算价格单位和时间单位的比例
  const priceRange = Math.abs(pivotY - startY);
  const timeRange = Math.abs(pivotX - startX);
  const unitRatio = priceRange / timeRange;
  
  for (const angle of angles) {
    const values = [];
    const adjustedRatio = unitRatio * angle.ratio;
    
    for (let i = 0; i < length; i++) {
      if (i < startX) {
        values.push(null); // 起始点之前的值为null
      } else {
        const timeDiff = i - startX;
        const priceDiff = timeDiff * adjustedRatio;
        const value = startY + priceDiff;
        values.push(value);
      }
    }
    
    lines.push({
      name: angle.name,
      angle: angle.angle,
      values
    });
  }
  
  return lines;
}

// 辅助函数:计算时间平方
function calculateTimeSquares(startIndex, length) {
  const squares = [];
  const fibNumbers = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144];
  
  for (const fib of fibNumbers) {
    const square = startIndex + fib;
    if (square < length) {
      squares.push(square);
    }
  }
  
  return squares;
}

// 辅助函数:计算价格平方
function calculatePriceSquares(lowPrice, highPrice) {
  const squares = [];
  const range = highPrice - lowPrice;
  
  // 添加一些基于价格的关键水平
  squares.push(lowPrice + range * 0.25);
  squares.push(lowPrice + range * 0.5);
  squares.push(lowPrice + range * 0.75);
  
  // 添加斐波那契水平
  squares.push(lowPrice + range * 0.382);
  squares.push(lowPrice + range * 0.618);
  squares.push(lowPrice + range * 0.786);
  
  return squares;
}

// 辅助函数:寻找局部高点
function findPeaks(prices, window) {
  const peaks = [];
  
  for (let i = window; i < prices.length - window; i++) {
    let isPeak = true;
    
    for (let j = i - window; j <= i + window; j++) {
      if (j !== i && prices[j] >= prices[i]) {
        isPeak = false;
        break;
      }
    }
    
    if (isPeak) {
      peaks.push(i);
    }
  }
  
  return peaks;
}

// 辅助函数:寻找局部低点
function findTroughs(prices, window) {
  const troughs = [];
  
  for (let i = window; i < prices.length - window; i++) {
    let isTrough = true;
    
    for (let j = i - window; j <= i + window; j++) {
      if (j !== i && prices[j] <= prices[i]) {
        isTrough = false;
        break;
      }
    }
    
    if (isTrough) {
      troughs.push(i);
    }
  }
  
  return troughs;
}
