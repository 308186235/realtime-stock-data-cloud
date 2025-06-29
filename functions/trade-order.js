const { withErrorHandling, validateRequest, ERROR_TYPES, createErrorResponse } = require('./utils/error-handler');
const { validateTradeRequest, containsDangerousContent, sanitizeString } = require('./utils/validators');

/**
 * 交易下单API
 * 演示完整的数据验证和安全检查流程
 */
async function handleTradeOrder(event, context, requestId) {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json',
    'X-Request-ID': requestId
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  // 只允许POST请求
  if (event.httpMethod !== 'POST') {
    throw new Error(`不支持的请求方法: ${event.httpMethod}`);
  }

  // 解析请求体
  let requestBody;
  try {
    requestBody = JSON.parse(event.body || '{}');
  } catch (error) {
    throw new Error('请求体JSON格式不正确');
  }

  // 基础字段验证
  const requiredFields = ['stock_code', 'trade_type', 'quantity'];
  const missingFields = requiredFields.filter(field => !requestBody[field]);
  
  if (missingFields.length > 0) {
    throw new Error(`缺少必填字段: ${missingFields.join(', ')}`);
  }

  // 使用验证器进行详细验证
  const validation = validateTradeRequest(requestBody);
  
  if (!validation.isValid) {
    const error = new Error(validation.errors.join('; '));
    error.name = 'ValidationError';
    throw error;
  }

  // 获取清理后的数据
  const tradeData = validation.sanitizedData;

  // 模拟交易逻辑检查
  const tradingHours = isInTradingHours();
  if (!tradingHours.isOpen) {
    throw new Error(`当前不在交易时间内。交易时间：${tradingHours.schedule}`);
  }

  // 模拟风险检查
  const riskCheck = performRiskCheck(tradeData);
  if (!riskCheck.passed) {
    throw new Error(`风险检查未通过: ${riskCheck.reason}`);
  }

  // 模拟账户余额检查（买入时）
  if (['buy', '买入'].includes(tradeData.trade_type)) {
    const balanceCheck = checkAccountBalance(tradeData);
    if (!balanceCheck.sufficient) {
      throw new Error(`账户余额不足。需要: ¥${balanceCheck.required}, 可用: ¥${balanceCheck.available}`);
    }
  }

  // 模拟持仓检查（卖出时）
  if (['sell', '卖出'].includes(tradeData.trade_type)) {
    const positionCheck = checkPosition(tradeData);
    if (!positionCheck.sufficient) {
      throw new Error(`持仓数量不足。需要: ${positionCheck.required}股, 可用: ${positionCheck.available}股`);
    }
  }

  // 生成订单ID
  const orderId = generateOrderId();

  // 构造响应数据
  const orderResponse = {
    success: true,
    message: "交易订单提交成功",
    order: {
      order_id: orderId,
      stock_code: tradeData.stock_code,
      stock_name: getStockName(tradeData.stock_code), // 模拟获取股票名称
      trade_type: tradeData.trade_type,
      quantity: tradeData.quantity,
      price: tradeData.price || "市价",
      estimated_amount: tradeData.price ? (tradeData.price * tradeData.quantity).toFixed(2) : "待确定",
      status: "已提交",
      submit_time: new Date().toISOString(),
      expected_execution: "即时执行"
    },
    risk_assessment: {
      risk_level: riskCheck.level,
      risk_score: riskCheck.score,
      warnings: riskCheck.warnings || []
    },
    account_impact: {
      before_balance: balanceCheck?.available || 0,
      estimated_after_balance: balanceCheck?.afterTrade || 0,
      frozen_amount: tradeData.price ? (tradeData.price * tradeData.quantity * 1.001).toFixed(2) : 0 // 包含手续费
    },
    next_steps: [
      "订单已进入交易队列",
      "系统将在交易时间内自动执行",
      "执行结果将通过短信和App推送通知"
    ],
    server_info: {
      server: "netlify-functions",
      request_id: requestId,
      timestamp: new Date().toISOString(),
      processing_time: "< 100ms"
    }
  };

  return {
    statusCode: 200,
    headers,
    body: JSON.stringify(orderResponse, null, 2)
  };
}

// 辅助函数

/**
 * 检查是否在交易时间内
 */
function isInTradingHours() {
  const now = new Date();
  const hour = now.getHours();
  const minute = now.getMinutes();
  const currentTime = hour * 100 + minute;
  
  // A股交易时间：9:30-11:30, 13:00-15:00
  const morningStart = 930;
  const morningEnd = 1130;
  const afternoonStart = 1300;
  const afternoonEnd = 1500;
  
  const isOpen = (currentTime >= morningStart && currentTime <= morningEnd) ||
                 (currentTime >= afternoonStart && currentTime <= afternoonEnd);
  
  return {
    isOpen,
    schedule: "9:30-11:30, 13:00-15:00"
  };
}

/**
 * 执行风险检查
 */
function performRiskCheck(tradeData) {
  const warnings = [];
  let riskScore = 0;
  
  // 大额交易风险
  const tradeAmount = tradeData.price * tradeData.quantity;
  if (tradeAmount > 100000) {
    warnings.push("大额交易，请确认风险承受能力");
    riskScore += 30;
  }
  
  // ST股票风险
  if (tradeData.stock_code.startsWith('300')) {
    warnings.push("创业板股票，波动较大");
    riskScore += 20;
  }
  
  let riskLevel = "低";
  if (riskScore > 50) riskLevel = "高";
  else if (riskScore > 20) riskLevel = "中";
  
  return {
    passed: riskScore < 80, // 风险分数超过80拒绝交易
    level: riskLevel,
    score: riskScore,
    warnings: warnings,
    reason: riskScore >= 80 ? "风险评分过高" : null
  };
}

/**
 * 检查账户余额
 */
function checkAccountBalance(tradeData) {
  // 模拟账户余额
  const availableBalance = 50000;
  const requiredAmount = tradeData.price * tradeData.quantity * 1.001; // 包含手续费
  
  return {
    sufficient: availableBalance >= requiredAmount,
    available: availableBalance,
    required: requiredAmount.toFixed(2),
    afterTrade: (availableBalance - requiredAmount).toFixed(2)
  };
}

/**
 * 检查持仓数量
 */
function checkPosition(tradeData) {
  // 模拟持仓数据
  const positions = {
    '000001': 1000,
    '600519': 500,
    '000002': 800
  };
  
  const availableShares = positions[tradeData.stock_code] || 0;
  
  return {
    sufficient: availableShares >= tradeData.quantity,
    available: availableShares,
    required: tradeData.quantity
  };
}

/**
 * 生成订单ID
 */
function generateOrderId() {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substr(2, 6).toUpperCase();
  return `ORD${timestamp}${random}`;
}

/**
 * 获取股票名称（模拟）
 */
function getStockName(stockCode) {
  const stockNames = {
    '000001': '平安银行',
    '000002': '万科A',
    '600519': '贵州茅台',
    '600036': '招商银行',
    '000858': '五粮液'
  };
  
  return stockNames[stockCode] || `股票${stockCode}`;
}

// 导出包装后的处理函数
exports.handler = async (event, context) => {
  return withErrorHandling(handleTradeOrder, event, context);
};
