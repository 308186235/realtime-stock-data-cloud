/**
 * 前端生产环境配置
 * 连接到Cloudflare部署的后端API
 */

// 环境配置
const ENVIRONMENT = process.env.NODE_ENV || 'production';

// API配置
const API_CONFIG = {
  // 生产环境配置
  production: {
    BACKEND_URL: 'https://api.aigupiao.me',
    LOCAL_API_URL: 'http://localhost:5000',  // 本地API始终是localhost
    WS_URL: 'wss://api.aigupiao.me/ws',
    TIMEOUT: 30000,
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000
  },
  
  // 开发环境配置
  development: {
    BACKEND_URL: 'http://localhost:8000',
    LOCAL_API_URL: 'http://localhost:5000',
    WS_URL: 'ws://localhost:8000/ws',
    TIMEOUT: 30000,
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000
  }
};

// 当前环境配置
const CONFIG = API_CONFIG[ENVIRONMENT];

// API客户端配置
const API_CLIENT_CONFIG = {
  // 请求头
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Client-Version': '1.0.0',
    'X-Client-Type': 'web'
  },
  
  // 超时配置
  timeout: CONFIG.TIMEOUT,
  
  // 重试配置
  retry: {
    attempts: CONFIG.RETRY_ATTEMPTS,
    delay: CONFIG.RETRY_DELAY
  }
};

// WebSocket配置
const WEBSOCKET_CONFIG = {
  // 连接配置
  url: CONFIG.WS_URL,
  protocols: [],
  
  // 重连配置
  reconnect: {
    enabled: true,
    maxAttempts: 5,
    delay: 5000,
    backoff: 1.5
  },
  
  // 心跳配置
  heartbeat: {
    enabled: true,
    interval: 30000,
    timeout: 5000
  }
};

// 本地API配置
const LOCAL_API_CONFIG = {
  url: CONFIG.LOCAL_API_URL,
  timeout: 60000,  // 本地操作可能需要更长时间
  endpoints: {
    health: '/health',
    balance: '/balance',
    export: '/export',
    trade: '/trade',
    connectCloud: '/connect-cloud',
    cloudStatus: '/cloud-status'
  }
};

// 云端API配置
const CLOUD_API_CONFIG = {
  url: CONFIG.BACKEND_URL,
  timeout: CONFIG.TIMEOUT,
  endpoints: {
    health: '/api/health',
    analysis: '/api/agent/analysis',
    decision: '/api/agent/decision',
    execute: '/api/agent/execute',
    localProxy: '/api/local'
  }
};

// 应用配置
const APP_CONFIG = {
  // 应用信息
  name: 'AI股票交易系统',
  version: '1.0.0',
  
  // 功能开关
  features: {
    realTimeData: true,
    aiAnalysis: true,
    autoTrading: true,
    cloudSync: true,
    localTrading: true
  },
  
  // UI配置
  ui: {
    theme: 'light',
    language: 'zh-CN',
    refreshInterval: 5000,
    chartUpdateInterval: 1000
  },
  
  // 安全配置
  security: {
    maxRetries: 3,
    sessionTimeout: 3600000, // 1小时
    requireConfirmation: true
  }
};

// 错误处理配置
const ERROR_CONFIG = {
  // 错误类型
  types: {
    NETWORK_ERROR: 'network_error',
    API_ERROR: 'api_error',
    TIMEOUT_ERROR: 'timeout_error',
    AUTH_ERROR: 'auth_error',
    VALIDATION_ERROR: 'validation_error'
  },
  
  // 错误消息
  messages: {
    network_error: '网络连接失败，请检查网络设置',
    api_error: 'API服务异常，请稍后重试',
    timeout_error: '请求超时，请稍后重试',
    auth_error: '认证失败，请重新登录',
    validation_error: '数据验证失败，请检查输入'
  },
  
  // 重试配置
  retry: {
    network_error: true,
    api_error: true,
    timeout_error: true,
    auth_error: false,
    validation_error: false
  }
};

// 导出配置
export {
  CONFIG,
  API_CLIENT_CONFIG,
  WEBSOCKET_CONFIG,
  LOCAL_API_CONFIG,
  CLOUD_API_CONFIG,
  APP_CONFIG,
  ERROR_CONFIG,
  ENVIRONMENT
};

// 默认导出
export default {
  ...CONFIG,
  client: API_CLIENT_CONFIG,
  websocket: WEBSOCKET_CONFIG,
  local: LOCAL_API_CONFIG,
  cloud: CLOUD_API_CONFIG,
  app: APP_CONFIG,
  error: ERROR_CONFIG,
  environment: ENVIRONMENT
};
