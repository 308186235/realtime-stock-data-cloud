/**
 * 统一错误处理工具
 * 为Netlify Functions提供标准化的错误响应
 */

// 错误类型定义
const ERROR_TYPES = {
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR: 'AUTHORIZATION_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  RATE_LIMIT: 'RATE_LIMIT',
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
  TIMEOUT: 'TIMEOUT'
};

// HTTP状态码映射
const STATUS_CODE_MAP = {
  [ERROR_TYPES.VALIDATION_ERROR]: 400,
  [ERROR_TYPES.AUTHENTICATION_ERROR]: 401,
  [ERROR_TYPES.AUTHORIZATION_ERROR]: 403,
  [ERROR_TYPES.NOT_FOUND]: 404,
  [ERROR_TYPES.RATE_LIMIT]: 429,
  [ERROR_TYPES.INTERNAL_ERROR]: 500,
  [ERROR_TYPES.SERVICE_UNAVAILABLE]: 503,
  [ERROR_TYPES.TIMEOUT]: 504
};

// 用户友好的错误消息
const USER_FRIENDLY_MESSAGES = {
  [ERROR_TYPES.VALIDATION_ERROR]: '请求参数有误，请检查输入数据',
  [ERROR_TYPES.AUTHENTICATION_ERROR]: '身份验证失败，请重新登录',
  [ERROR_TYPES.AUTHORIZATION_ERROR]: '权限不足，无法访问此资源',
  [ERROR_TYPES.NOT_FOUND]: '请求的资源不存在',
  [ERROR_TYPES.RATE_LIMIT]: '请求过于频繁，请稍后再试',
  [ERROR_TYPES.INTERNAL_ERROR]: '服务器内部错误，请稍后重试',
  [ERROR_TYPES.SERVICE_UNAVAILABLE]: '服务暂时不可用，请稍后重试',
  [ERROR_TYPES.TIMEOUT]: '请求超时，请稍后重试'
};

/**
 * 创建标准化错误响应
 * @param {string} errorType - 错误类型
 * @param {string} message - 详细错误消息
 * @param {Object} details - 额外错误详情
 * @param {string} requestId - 请求ID（用于追踪）
 * @returns {Object} 标准化错误响应
 */
function createErrorResponse(errorType, message = null, details = null, requestId = null) {
  const statusCode = STATUS_CODE_MAP[errorType] || 500;
  const userMessage = USER_FRIENDLY_MESSAGES[errorType] || '未知错误';
  
  const errorResponse = {
    error: {
      type: errorType,
      message: userMessage,
      details: message || userMessage,
      timestamp: new Date().toISOString(),
      request_id: requestId || generateRequestId()
    },
    success: false,
    status_code: statusCode
  };

  // 添加额外详情（仅在开发环境或特定情况下）
  if (details && process.env.NODE_ENV !== 'production') {
    errorResponse.error.debug_info = details;
  }

  return {
    statusCode,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'X-Error-Type': errorType,
      'X-Request-ID': errorResponse.error.request_id
    },
    body: JSON.stringify(errorResponse, null, 2)
  };
}

/**
 * 包装函数执行，自动处理错误
 * @param {Function} handler - 要执行的处理函数
 * @param {Object} event - Netlify event对象
 * @param {Object} context - Netlify context对象
 * @returns {Promise<Object>} 响应对象
 */
async function withErrorHandling(handler, event, context) {
  const requestId = generateRequestId();
  
  try {
    // 记录请求开始
    console.log(`[${requestId}] Request started: ${event.httpMethod} ${event.path}`);
    
    const startTime = Date.now();
    const result = await handler(event, context, requestId);
    const duration = Date.now() - startTime;
    
    // 记录请求完成
    console.log(`[${requestId}] Request completed in ${duration}ms`);
    
    return result;
  } catch (error) {
    console.error(`[${requestId}] Error occurred:`, error);
    
    // 根据错误类型返回相应的错误响应
    if (error.name === 'ValidationError') {
      return createErrorResponse(ERROR_TYPES.VALIDATION_ERROR, error.message, error, requestId);
    } else if (error.name === 'TimeoutError') {
      return createErrorResponse(ERROR_TYPES.TIMEOUT, error.message, error, requestId);
    } else if (error.code === 'ENOTFOUND' || error.code === 'ECONNREFUSED') {
      return createErrorResponse(ERROR_TYPES.SERVICE_UNAVAILABLE, '外部服务连接失败', error, requestId);
    } else {
      return createErrorResponse(ERROR_TYPES.INTERNAL_ERROR, error.message, error, requestId);
    }
  }
}

/**
 * 生成唯一请求ID
 * @returns {string} 请求ID
 */
function generateRequestId() {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * 验证请求参数
 * @param {Object} data - 要验证的数据
 * @param {Object} schema - 验证规则
 * @throws {ValidationError} 验证失败时抛出
 */
function validateRequest(data, schema) {
  const errors = [];
  
  for (const [field, rules] of Object.entries(schema)) {
    const value = data[field];
    
    // 检查必填字段
    if (rules.required && (value === undefined || value === null || value === '')) {
      errors.push(`字段 '${field}' 是必填的`);
      continue;
    }
    
    // 如果字段不存在且不是必填，跳过其他验证
    if (value === undefined || value === null) {
      continue;
    }
    
    // 类型验证
    if (rules.type && typeof value !== rules.type) {
      errors.push(`字段 '${field}' 类型应为 ${rules.type}`);
    }
    
    // 长度验证
    if (rules.minLength && value.length < rules.minLength) {
      errors.push(`字段 '${field}' 长度不能少于 ${rules.minLength} 个字符`);
    }
    
    if (rules.maxLength && value.length > rules.maxLength) {
      errors.push(`字段 '${field}' 长度不能超过 ${rules.maxLength} 个字符`);
    }
    
    // 数值范围验证
    if (rules.min !== undefined && value < rules.min) {
      errors.push(`字段 '${field}' 值不能小于 ${rules.min}`);
    }
    
    if (rules.max !== undefined && value > rules.max) {
      errors.push(`字段 '${field}' 值不能大于 ${rules.max}`);
    }
    
    // 正则表达式验证
    if (rules.pattern && !rules.pattern.test(value)) {
      errors.push(`字段 '${field}' 格式不正确`);
    }
  }
  
  if (errors.length > 0) {
    const error = new Error(errors.join('; '));
    error.name = 'ValidationError';
    throw error;
  }
}

/**
 * 检查请求频率限制
 * @param {string} identifier - 标识符（IP、用户ID等）
 * @param {number} limit - 限制次数
 * @param {number} window - 时间窗口（秒）
 * @returns {boolean} 是否超出限制
 */
function checkRateLimit(identifier, limit = 100, window = 3600) {
  // 这里可以集成Redis或其他存储来实现真正的频率限制
  // 目前返回false表示未超出限制
  return false;
}

module.exports = {
  ERROR_TYPES,
  createErrorResponse,
  withErrorHandling,
  validateRequest,
  checkRateLimit,
  generateRequestId
};
