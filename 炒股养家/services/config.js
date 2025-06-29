/**
 * 服务配置文件
 */

// API基础URL,根据环境设置
const baseUrl = process.env.NODE_ENV === 'development'
  ? 'https://trading-system-api.netlify.app'  // 开发环境使用Netlify
  : 'https://trading-system-api.netlify.app';  // 生产环境使用Netlify

// 超时设置(毫秒)
const timeout = 30000;

// 重试次数
const retryCount = 3;

// 导出配置
export {
  baseUrl,
  timeout,
  retryCount
}; 
