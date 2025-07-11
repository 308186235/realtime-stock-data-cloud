/**
 * 服务配置文件 - 统一配置
 */

// API基础URL - 使用本地Agent后端
const baseUrl = 'http://localhost:9999';

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