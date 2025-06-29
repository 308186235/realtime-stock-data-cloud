/**
 * 数据验证工具模块
 * 提供各种数据验证和安全检查功能
 */

// 常用正则表达式
const PATTERNS = {
  // 股票代码：6位数字
  STOCK_CODE: /^[0-9]{6}$/,
  // 手机号：11位数字，1开头
  MOBILE: /^1[3-9]\d{9}$/,
  // 邮箱
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  // 身份证号：18位
  ID_CARD: /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/,
  // 银行卡号：13-19位数字
  BANK_CARD: /^[1-9]\d{12,18}$/,
  // 密码：8-20位，包含字母和数字
  PASSWORD: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,20}$/,
  // IP地址
  IP_ADDRESS: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
  // URL
  URL: /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/
};

// 危险字符检测（防止XSS和SQL注入）
const DANGEROUS_PATTERNS = [
  /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
  /javascript:/gi,
  /on\w+\s*=/gi,
  /eval\s*\(/gi,
  /expression\s*\(/gi,
  /vbscript:/gi,
  /data:text\/html/gi,
  /(union|select|insert|update|delete|drop|create|alter|exec|execute)\s+/gi,
  /('|(\\')|(;)|(\\)|(\/\*)|(--)|(\*\/))/gi
];

/**
 * 验证股票代码
 * @param {string} code - 股票代码
 * @returns {boolean} 是否有效
 */
function validateStockCode(code) {
  if (!code || typeof code !== 'string') return false;
  return PATTERNS.STOCK_CODE.test(code.trim());
}

/**
 * 验证交易数量
 * @param {number|string} quantity - 交易数量
 * @returns {boolean} 是否有效
 */
function validateTradeQuantity(quantity) {
  const num = Number(quantity);
  if (isNaN(num) || num <= 0) return false;
  // A股最小交易单位是100股（1手）
  return num % 100 === 0 && num <= 1000000; // 最大100万股
}

/**
 * 验证价格
 * @param {number|string} price - 价格
 * @returns {boolean} 是否有效
 */
function validatePrice(price) {
  const num = Number(price);
  if (isNaN(num) || num <= 0) return false;
  // 价格不能超过1万元，保留2位小数
  return num <= 10000 && Number(num.toFixed(2)) === num;
}

/**
 * 验证日期格式
 * @param {string} dateStr - 日期字符串
 * @param {string} format - 期望格式 ('YYYY-MM-DD', 'YYYY-MM-DD HH:mm:ss')
 * @returns {boolean} 是否有效
 */
function validateDate(dateStr, format = 'YYYY-MM-DD') {
  if (!dateStr || typeof dateStr !== 'string') return false;
  
  let pattern;
  switch (format) {
    case 'YYYY-MM-DD':
      pattern = /^\d{4}-\d{2}-\d{2}$/;
      break;
    case 'YYYY-MM-DD HH:mm:ss':
      pattern = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/;
      break;
    default:
      return false;
  }
  
  if (!pattern.test(dateStr)) return false;
  
  const date = new Date(dateStr);
  return date instanceof Date && !isNaN(date.getTime());
}

/**
 * 验证手机号
 * @param {string} mobile - 手机号
 * @returns {boolean} 是否有效
 */
function validateMobile(mobile) {
  if (!mobile || typeof mobile !== 'string') return false;
  return PATTERNS.MOBILE.test(mobile.trim());
}

/**
 * 验证邮箱
 * @param {string} email - 邮箱地址
 * @returns {boolean} 是否有效
 */
function validateEmail(email) {
  if (!email || typeof email !== 'string') return false;
  return PATTERNS.EMAIL.test(email.trim().toLowerCase());
}

/**
 * 检测危险字符（防XSS和SQL注入）
 * @param {string} input - 输入字符串
 * @returns {boolean} 是否包含危险字符
 */
function containsDangerousContent(input) {
  if (!input || typeof input !== 'string') return false;
  
  return DANGEROUS_PATTERNS.some(pattern => pattern.test(input));
}

/**
 * 清理和转义字符串
 * @param {string} input - 输入字符串
 * @returns {string} 清理后的字符串
 */
function sanitizeString(input) {
  if (!input || typeof input !== 'string') return '';
  
  return input
    .trim()
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
}

/**
 * 验证IP地址
 * @param {string} ip - IP地址
 * @returns {boolean} 是否有效
 */
function validateIP(ip) {
  if (!ip || typeof ip !== 'string') return false;
  return PATTERNS.IP_ADDRESS.test(ip.trim());
}

/**
 * 验证URL
 * @param {string} url - URL地址
 * @returns {boolean} 是否有效
 */
function validateURL(url) {
  if (!url || typeof url !== 'string') return false;
  return PATTERNS.URL.test(url.trim());
}

/**
 * 验证数值范围
 * @param {number} value - 数值
 * @param {number} min - 最小值
 * @param {number} max - 最大值
 * @returns {boolean} 是否在范围内
 */
function validateRange(value, min, max) {
  const num = Number(value);
  if (isNaN(num)) return false;
  return num >= min && num <= max;
}

/**
 * 验证字符串长度
 * @param {string} str - 字符串
 * @param {number} minLength - 最小长度
 * @param {number} maxLength - 最大长度
 * @returns {boolean} 是否符合长度要求
 */
function validateLength(str, minLength = 0, maxLength = Infinity) {
  if (typeof str !== 'string') return false;
  const length = str.trim().length;
  return length >= minLength && length <= maxLength;
}

/**
 * 综合验证交易请求
 * @param {Object} tradeData - 交易数据
 * @returns {Object} 验证结果
 */
function validateTradeRequest(tradeData) {
  const errors = [];
  
  // 验证股票代码
  if (!validateStockCode(tradeData.stock_code)) {
    errors.push('股票代码格式不正确，应为6位数字');
  }
  
  // 验证交易数量
  if (!validateTradeQuantity(tradeData.quantity)) {
    errors.push('交易数量必须是100的整数倍，且不超过100万股');
  }
  
  // 验证价格
  if (tradeData.price && !validatePrice(tradeData.price)) {
    errors.push('价格格式不正确，应为正数且不超过10000元');
  }
  
  // 验证交易类型
  const validTradeTypes = ['buy', 'sell', '买入', '卖出'];
  if (!validTradeTypes.includes(tradeData.trade_type)) {
    errors.push('交易类型不正确，应为buy/sell或买入/卖出');
  }
  
  // 检测危险内容
  const fieldsToCheck = ['stock_code', 'trade_type', 'remark'];
  for (const field of fieldsToCheck) {
    if (tradeData[field] && containsDangerousContent(tradeData[field])) {
      errors.push(`${field}字段包含不安全内容`);
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors: errors,
    sanitizedData: {
      stock_code: sanitizeString(tradeData.stock_code),
      quantity: Number(tradeData.quantity),
      price: tradeData.price ? Number(tradeData.price) : null,
      trade_type: sanitizeString(tradeData.trade_type),
      remark: sanitizeString(tradeData.remark || '')
    }
  };
}

/**
 * 验证查询参数
 * @param {Object} queryParams - 查询参数
 * @returns {Object} 验证结果
 */
function validateQueryParams(queryParams) {
  const errors = [];
  const sanitized = {};
  
  // 验证页码
  if (queryParams.page) {
    const page = Number(queryParams.page);
    if (isNaN(page) || page < 1 || page > 1000) {
      errors.push('页码应为1-1000之间的整数');
    } else {
      sanitized.page = page;
    }
  }
  
  // 验证每页数量
  if (queryParams.limit) {
    const limit = Number(queryParams.limit);
    if (isNaN(limit) || limit < 1 || limit > 100) {
      errors.push('每页数量应为1-100之间的整数');
    } else {
      sanitized.limit = limit;
    }
  }
  
  // 验证日期范围
  if (queryParams.start_date && !validateDate(queryParams.start_date)) {
    errors.push('开始日期格式不正确，应为YYYY-MM-DD');
  } else if (queryParams.start_date) {
    sanitized.start_date = queryParams.start_date;
  }
  
  if (queryParams.end_date && !validateDate(queryParams.end_date)) {
    errors.push('结束日期格式不正确，应为YYYY-MM-DD');
  } else if (queryParams.end_date) {
    sanitized.end_date = queryParams.end_date;
  }
  
  // 验证股票代码
  if (queryParams.stock_code && !validateStockCode(queryParams.stock_code)) {
    errors.push('股票代码格式不正确');
  } else if (queryParams.stock_code) {
    sanitized.stock_code = queryParams.stock_code;
  }
  
  return {
    isValid: errors.length === 0,
    errors: errors,
    sanitizedData: sanitized
  };
}

module.exports = {
  // 基础验证函数
  validateStockCode,
  validateTradeQuantity,
  validatePrice,
  validateDate,
  validateMobile,
  validateEmail,
  validateIP,
  validateURL,
  validateRange,
  validateLength,
  
  // 安全检查
  containsDangerousContent,
  sanitizeString,
  
  // 综合验证
  validateTradeRequest,
  validateQueryParams,
  
  // 常量
  PATTERNS,
  DANGEROUS_PATTERNS
};
