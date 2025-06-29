/**
 * 安全配置和工具模块
 * 提供API安全防护功能
 */

// 安全配置
const SECURITY_CONFIG = {
  // 请求频率限制配置
  RATE_LIMITS: {
    DEFAULT: { requests: 100, window: 3600 }, // 默认每小时100次
    HEALTH: { requests: 200, window: 3600 },  // 健康检查每小时200次
    BALANCE: { requests: 120, window: 3600 }, // 余额查询每小时120次
    POSITIONS: { requests: 100, window: 3600 }, // 持仓查询每小时100次
    ANALYSIS: { requests: 60, window: 3600 },  // 分析查询每小时60次
    TRADE: { requests: 50, window: 3600 }      // 交易操作每小时50次
  },
  
  // 请求大小限制
  MAX_REQUEST_SIZE: 1024 * 1024, // 1MB
  
  // 允许的请求头
  ALLOWED_HEADERS: [
    'Content-Type',
    'Authorization',
    'X-Requested-With',
    'Accept',
    'Origin',
    'User-Agent'
  ],
  
  // 允许的HTTP方法
  ALLOWED_METHODS: ['GET', 'POST', 'OPTIONS'],
  
  // 敏感信息字段（需要脱敏）
  SENSITIVE_FIELDS: [
    'password',
    'token',
    'secret',
    'key',
    'phone',
    'mobile',
    'email',
    'id_card',
    'bank_card'
  ],
  
  // IP白名单（可选）
  IP_WHITELIST: [],
  
  // IP黑名单
  IP_BLACKLIST: [],
  
  // 用户代理黑名单（阻止恶意爬虫）
  USER_AGENT_BLACKLIST: [
    /bot/i,
    /crawler/i,
    /spider/i,
    /scraper/i,
    /curl/i,
    /wget/i,
    /python-requests/i
  ]
};

/**
 * 检查IP是否被允许
 * @param {string} ip - 客户端IP
 * @returns {boolean} 是否允许访问
 */
function isIPAllowed(ip) {
  if (!ip) return false;
  
  // 检查黑名单
  if (SECURITY_CONFIG.IP_BLACKLIST.includes(ip)) {
    return false;
  }
  
  // 如果有白名单，只允许白名单IP
  if (SECURITY_CONFIG.IP_WHITELIST.length > 0) {
    return SECURITY_CONFIG.IP_WHITELIST.includes(ip);
  }
  
  return true;
}

/**
 * 检查User-Agent是否被允许
 * @param {string} userAgent - 用户代理字符串
 * @returns {boolean} 是否允许访问
 */
function isUserAgentAllowed(userAgent) {
  if (!userAgent) return false;
  
  // 检查是否匹配黑名单模式
  return !SECURITY_CONFIG.USER_AGENT_BLACKLIST.some(pattern => 
    pattern.test(userAgent)
  );
}

/**
 * 验证请求头
 * @param {Object} headers - 请求头对象
 * @returns {Object} 验证结果
 */
function validateHeaders(headers) {
  const issues = [];
  
  // 检查Content-Type（对于POST请求）
  const contentType = headers['content-type'];
  if (contentType && !contentType.includes('application/json')) {
    issues.push('不支持的Content-Type，仅支持application/json');
  }
  
  // 检查Authorization格式（如果存在）
  const auth = headers['authorization'];
  if (auth && !auth.startsWith('Bearer ') && !auth.startsWith('Basic ')) {
    issues.push('Authorization头格式不正确');
  }
  
  // 检查Origin（CORS预检）
  const origin = headers['origin'];
  if (origin && !isOriginAllowed(origin)) {
    issues.push('不允许的Origin');
  }
  
  return {
    isValid: issues.length === 0,
    issues: issues
  };
}

/**
 * 检查Origin是否被允许
 * @param {string} origin - 请求来源
 * @returns {boolean} 是否允许
 */
function isOriginAllowed(origin) {
  // 允许的域名列表
  const allowedOrigins = [
    'https://aigupiao.me',
    'https://www.aigupiao.me',
    'https://trading-system-api.netlify.app',
    'http://localhost:3000',
    'http://localhost:8080',
    'http://127.0.0.1:3000'
  ];
  
  return allowedOrigins.includes(origin);
}

/**
 * 脱敏敏感信息
 * @param {Object} data - 数据对象
 * @returns {Object} 脱敏后的数据
 */
function maskSensitiveData(data) {
  if (!data || typeof data !== 'object') return data;
  
  const masked = { ...data };
  
  for (const field of SECURITY_CONFIG.SENSITIVE_FIELDS) {
    if (masked[field]) {
      if (typeof masked[field] === 'string') {
        // 保留前2位和后2位，中间用*替换
        const value = masked[field];
        if (value.length > 4) {
          masked[field] = value.substring(0, 2) + '*'.repeat(value.length - 4) + value.substring(value.length - 2);
        } else {
          masked[field] = '*'.repeat(value.length);
        }
      } else {
        masked[field] = '***';
      }
    }
  }
  
  return masked;
}

/**
 * 生成安全的响应头
 * @param {Object} additionalHeaders - 额外的响应头
 * @returns {Object} 完整的安全响应头
 */
function getSecurityHeaders(additionalHeaders = {}) {
  const securityHeaders = {
    // CORS头
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': SECURITY_CONFIG.ALLOWED_HEADERS.join(', '),
    'Access-Control-Allow-Methods': SECURITY_CONFIG.ALLOWED_METHODS.join(', '),
    'Access-Control-Max-Age': '86400', // 24小时
    
    // 安全头
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Content-Security-Policy': "default-src 'self'; script-src 'none'; object-src 'none';",
    
    // 缓存控制
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
    
    // 服务器信息隐藏
    'Server': 'TradingAPI/1.0'
  };
  
  return { ...securityHeaders, ...additionalHeaders };
}

/**
 * 记录安全事件
 * @param {string} eventType - 事件类型
 * @param {Object} details - 事件详情
 * @param {string} ip - 客户端IP
 * @param {string} userAgent - 用户代理
 */
function logSecurityEvent(eventType, details, ip, userAgent) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    event_type: eventType,
    client_ip: ip,
    user_agent: userAgent,
    details: details,
    severity: getSeverityLevel(eventType)
  };
  
  // 在生产环境中，这里应该发送到日志系统
  console.warn(`[SECURITY] ${eventType}:`, logEntry);
  
  // 如果是高危事件，可以触发告警
  if (logEntry.severity === 'HIGH') {
    console.error(`[SECURITY ALERT] High severity security event detected:`, logEntry);
  }
}

/**
 * 获取安全事件严重程度
 * @param {string} eventType - 事件类型
 * @returns {string} 严重程度
 */
function getSeverityLevel(eventType) {
  const highSeverityEvents = [
    'SQL_INJECTION_ATTEMPT',
    'XSS_ATTEMPT',
    'BRUTE_FORCE_ATTACK',
    'UNAUTHORIZED_ACCESS'
  ];
  
  const mediumSeverityEvents = [
    'RATE_LIMIT_EXCEEDED',
    'INVALID_TOKEN',
    'SUSPICIOUS_USER_AGENT'
  ];
  
  if (highSeverityEvents.includes(eventType)) return 'HIGH';
  if (mediumSeverityEvents.includes(eventType)) return 'MEDIUM';
  return 'LOW';
}

/**
 * 执行安全检查
 * @param {Object} event - Netlify event对象
 * @returns {Object} 检查结果
 */
function performSecurityCheck(event) {
  const issues = [];
  const clientIP = event.headers['x-forwarded-for'] || event.headers['x-real-ip'] || 'unknown';
  const userAgent = event.headers['user-agent'] || '';
  
  // IP检查
  if (!isIPAllowed(clientIP)) {
    issues.push('IP地址被禁止访问');
    logSecurityEvent('IP_BLOCKED', { ip: clientIP }, clientIP, userAgent);
  }
  
  // User-Agent检查
  if (!isUserAgentAllowed(userAgent)) {
    issues.push('不允许的User-Agent');
    logSecurityEvent('SUSPICIOUS_USER_AGENT', { user_agent: userAgent }, clientIP, userAgent);
  }
  
  // 请求头检查
  const headerValidation = validateHeaders(event.headers);
  if (!headerValidation.isValid) {
    issues.push(...headerValidation.issues);
  }
  
  // 请求大小检查
  if (event.body && event.body.length > SECURITY_CONFIG.MAX_REQUEST_SIZE) {
    issues.push('请求体过大');
    logSecurityEvent('REQUEST_TOO_LARGE', { size: event.body.length }, clientIP, userAgent);
  }
  
  return {
    passed: issues.length === 0,
    issues: issues,
    clientIP: clientIP,
    userAgent: userAgent
  };
}

module.exports = {
  SECURITY_CONFIG,
  isIPAllowed,
  isUserAgentAllowed,
  validateHeaders,
  isOriginAllowed,
  maskSensitiveData,
  getSecurityHeaders,
  logSecurityEvent,
  performSecurityCheck
};
