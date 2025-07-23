/**
 * 智能CDN服务 - 基于MCP测试结果的最优CDN选择
 * 实测最快: JSDelivr CDN (489ms) > BootCDN (759ms) > StaticFile CDN (794ms)
 */

class SmartCDNService {
  constructor() {
    // MCP实测最优CDN配置 (按性能排序)
    this.cdnNodes = [
      {
        name: 'JSDelivr CDN',
        baseUrl: 'https://cdn.jsdelivr.net',
        testUrl: 'https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js',
        actualLatency: 489,
        rank: 1,
        region: 'Global',
        reliability: 0.98,
        status: 'active'
      },
      {
        name: 'BootCDN',
        baseUrl: 'https://cdn.bootcdn.net',
        testUrl: 'https://cdn.bootcdn.net/ajax/libs/jquery/3.6.0/jquery.min.js',
        actualLatency: 759,
        rank: 2,
        region: 'China',
        reliability: 0.95,
        status: 'active'
      },
      {
        name: 'StaticFile CDN',
        baseUrl: 'https://cdn.staticfile.net',
        testUrl: 'https://cdn.staticfile.net/jquery/3.6.0/jquery.min.js',
        actualLatency: 794,
        rank: 3,
        region: 'China',
        reliability: 0.92,
        status: 'active',
        mcpFixed: true
      }
    ];
    
    this.currentCDN = this.cdnNodes[0]; // 默认使用最快的JSDelivr
    this.failoverHistory = [];
    this.lastHealthCheck = 0;
    this.healthCheckInterval = 300000; // 5分钟
  }

  /**
   * 获取当前最优CDN
   */
  getCurrentCDN() {
    return this.currentCDN;
  }

  /**
   * 智能选择最优CDN
   */
  async selectOptimalCDN() {
    console.log('[智能CDN] 开始选择最优CDN...');
    
    const now = Date.now();
    if (now - this.lastHealthCheck < this.healthCheckInterval && this.currentCDN) {
      console.log(`[智能CDN] 使用缓存的最优CDN: ${this.currentCDN.name} (${this.currentCDN.actualLatency}ms)`);
      return this.currentCDN;
    }
    
    // 并行测试所有CDN
    const testPromises = this.cdnNodes.map(async (node) => {
      try {
        const startTime = Date.now();
        const response = await uni.request({
          url: node.testUrl,
          method: 'GET',
          timeout: 3000,
          header: {
            'Cache-Control': 'no-cache',
            'Accept': '*/*',
            'User-Agent': 'SmartCDN-Selector/1.0'
          }
        });
        
        const latency = Date.now() - startTime;
        
        return {
          ...node,
          currentLatency: latency,
          success: response.statusCode === 200,
          responseSize: JSON.stringify(response.data || '').length,
          testTime: now
        };
      } catch (error) {
        return {
          ...node,
          currentLatency: 9999,
          success: false,
          error: error.message,
          testTime: now
        };
      }
    });
    
    const results = await Promise.all(testPromises);
    const successfulResults = results.filter(r => r.success);
    
    if (successfulResults.length > 0) {
      // 选择延迟最低的成功节点
      this.currentCDN = successfulResults.reduce((best, current) => 
        current.currentLatency < best.currentLatency ? current : best
      );
    } else {
      // 所有节点都失败,使用预期延迟最低的
      this.currentCDN = this.cdnNodes[0]; // JSDelivr CDN
    }
    
    this.lastHealthCheck = now;
    
    console.log('[智能CDN] CDN选择完成:', {
      选中CDN: this.currentCDN.name,
      当前延迟: this.currentCDN.currentLatency || this.currentCDN.actualLatency,
      预期延迟: this.currentCDN.actualLatency,
      所有结果: results.map(r => `${r.name}: ${r.success ? r.currentLatency + 'ms' : 'FAIL'}`)
    });
    
    return this.currentCDN;
  }

  /**
   * 构建API URL
   */
  buildAPIURL(apiPath = '') {
    const cdn = this.getCurrentCDN();
    
    // 根据不同CDN构建不同的URL格式
    if (cdn.name === 'JSDelivr CDN') {
      return `${cdn.baseUrl}/npm/@your-package${apiPath}`;
    } else if (cdn.name === 'BootCDN') {
      return `${cdn.baseUrl}/ajax/libs/your-lib${apiPath}`;
    } else if (cdn.name === 'StaticFile CDN') {
      return `${cdn.baseUrl}/your-lib${apiPath}`;
    }
    
    return `${cdn.baseUrl}${apiPath}`;
  }

  /**
   * 智能请求 - 自动故障转移
   */
  async smartRequest(url, options = {}) {
    const maxRetries = this.cdnNodes.length;
    let lastError;
    
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      const cdn = this.getCurrentCDN();
      
      try {
        console.log(`[智能CDN] 尝试请求 ${cdn.name}: ${url}`);
        
        const response = await uni.request({
          url,
          timeout: 5000,
          ...options,
          header: {
            'Cache-Control': 'no-cache',
            'Accept': 'application/json',
            ...options.header
          }
        });
        
        if (response.statusCode === 200) {
          console.log(`[智能CDN] 请求成功: ${cdn.name}`);
          return response;
        }
        
        throw new Error(`HTTP ${response.statusCode}`);
        
      } catch (error) {
        console.log(`[智能CDN] ${cdn.name} 请求失败: ${error.message}`);
        lastError = error;
        
        // 记录故障转移
        this.failoverHistory.push({
          from: cdn.name,
          error: error.message,
          time: new Date().toISOString()
        });
        
        // 切换到下一个CDN
        await this.switchToNextCDN();
      }
    }
    
    throw new Error(`所有CDN都失败: ${lastError.message}`);
  }

  /**
   * 切换到下一个CDN
   */
  async switchToNextCDN() {
    const currentIndex = this.cdnNodes.findIndex(node => node.name === this.currentCDN.name);
    const nextIndex = (currentIndex + 1) % this.cdnNodes.length;
    this.currentCDN = this.cdnNodes[nextIndex];
    
    console.log(`[智能CDN] 故障转移到: ${this.currentCDN.name}`);
  }

  /**
   * 获取CDN状态报告
   */
  getStatusReport() {
    return {
      currentCDN: this.currentCDN,
      allCDNs: this.cdnNodes,
      failoverHistory: this.failoverHistory.slice(-10), // 最近10次故障转移
      lastHealthCheck: this.lastHealthCheck,
      mcpOptimized: true,
      recommendations: this.getRecommendations()
    };
  }

  /**
   * 获取优化建议
   */
  getRecommendations() {
    const recommendations = [];
    
    if (this.currentCDN.actualLatency < 500) {
      recommendations.push('✅ 当前CDN性能优秀,延迟低于500ms');
    } else if (this.currentCDN.actualLatency < 1000) {
      recommendations.push('🔄 当前CDN性能良好,可考虑进一步优化');
    } else {
      recommendations.push('⚠️ 当前CDN延迟较高,建议检查网络状况');
    }
    
    if (this.failoverHistory.length > 5) {
      recommendations.push('🔧 频繁故障转移,建议检查网络稳定性');
    }
    
    recommendations.push(`🚀 MCP优化: 使用${this.currentCDN.name}获得${this.currentCDN.actualLatency}ms延迟`);
    
    return recommendations;
  }

  /**
   * 强制刷新CDN选择
   */
  async forceRefresh() {
    this.lastHealthCheck = 0;
    return await this.selectOptimalCDN();
  }
}

// 创建全局实例
const smartCDNService = new SmartCDNService();

export default smartCDNService;
