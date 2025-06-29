/**
 * 服务配置文件
 */

// API基础URL,根据环境设置
const baseUrl = process.env.NODE_ENV === 'development'
  ? 'https://aigupiao.me'  // 开发环境 - 使用自定义域名
  : 'https://aigupiao.me';  // 生产环境 - 使用自定义域名

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
