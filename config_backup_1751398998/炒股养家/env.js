/**
 * 环境配置文件
 * 用于统一管理不同环境的配置
 */

// 环境类型
const ENV_TYPE = {
  DEV: 'development',
  PROD: 'production'
};

// 当前环境
const currentEnv = process.env.NODE_ENV || ENV_TYPE.DEV;

// 基础配置
const baseConfig = {
  // 版本号
  version: '1.0.0',
  
  // 缓存过期时间(毫秒)
  cacheExpiration: 5 * 60 * 1000, // 5分钟
  
  // WebSocket心跳间隔(毫秒)
  wsHeartbeatInterval: 30000, // 30秒
  
  // 请求超时(毫秒)
  requestTimeout: 30000, // 30秒
};

// 环境特定配置
const envConfigs = {
  // 开发环境
  [ENV_TYPE.DEV]: {
    // API基础URL
    apiBaseUrl: 'https://trading-system-api.netlify.app',

    // WebSocket地址
    wsUrl: 'wss://trading-system-api.netlify.app/ws',
    
    // 是否启用调试
    debug: true,
    
    // 是否使用模拟数据
    useMockData: true,
    
    // 默认主题
    defaultTheme: 'light',
    
    // 日志级别
    logLevel: 'debug'
  },
  
  // 生产环境
  [ENV_TYPE.PROD]: {
    // API基础URL
    apiBaseUrl: 'https://trading-system-api.netlify.app',

    // WebSocket地址
    wsUrl: 'wss://trading-system-api.netlify.app/ws',

    // 是否启用调试
    debug: false,

    // 是否使用模拟数据
    useMockData: false,

    // 默认主题
    defaultTheme: 'dark',

    // 日志级别
    logLevel: 'error'
  }
};

// 导出当前环境的配置
export default {
  ...baseConfig,
  ...envConfigs[currentEnv],
  
  // 导出环境类型常量
  ENV_TYPE,
  
  // 当前环境
  currentEnv,
  
  // 是否为开发环境
  isDev: currentEnv === ENV_TYPE.DEV,
  
  // 是否为生产环境
  isProd: currentEnv === ENV_TYPE.PROD,
  
  // 获取当前环境
  get current() {
    // 根据构建类型判断环境
    const isDev = process.env.NODE_ENV === 'development';
    return isDev ? envConfigs[ENV_TYPE.DEV] : envConfigs[ENV_TYPE.PROD];
  }
}; 
