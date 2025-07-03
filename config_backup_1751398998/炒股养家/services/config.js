/**
 * 服务配置文件
 */

// API基础URL,根据环境设置
const baseUrl = process.env.NODE_ENV === 'development'
  ? 'https://realtime-stock-api.pages.dev'  // 开发环境使用Cloudflare Pages
  : 'https://realtime-stock-api.pages.dev';  // 生产环境使用Cloudflare Pages

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
