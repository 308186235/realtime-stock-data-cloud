/**
 * MCP优化的CDN配置
 * 基于实测延迟数据优化
 */

export const OPTIMIZED_CDN_CONFIG = {
  // 主要CDN (最快)
  primary: {
    name: 'JSDelivr CDN',
    baseUrl: 'https://cdn.jsdelivr.net',
    latency: 919,
    region: 'Global'
  },
  
  // 备用CDN
  fallback: {
    name: 'BootCDN',
    baseUrl: 'https://cdn.bootcdn.net',
    latency: 1367,
    region: 'China'
  },
  
  // 智能切换配置
  smartSwitch: {
    enabled: true,
    failoverThreshold: 2000,
    healthCheckInterval: 300000,
    maxRetries: 3
  },
  
  // MCP优化标记
  mcpOptimized: true,
  lastOptimized: '2025-07-21T12:47:13.483198'
};

// 获取最优CDN URL
export function getOptimalCDN() {
  return OPTIMIZED_CDN_CONFIG.primary.baseUrl;
}

// CDN健康检查
export async function checkCDNHealth(cdnUrl) {
  try {
    const start = performance.now();
    const response = await fetch(`${cdnUrl}/npm/vue@3/dist/vue.global.js`, {
      method: 'HEAD',
      timeout: 5000
    });
    const latency = performance.now() - start;
    return { success: response.ok, latency: Math.round(latency) };
  } catch (error) {
    return { success: false, latency: 9999, error: error.message };
  }
}
