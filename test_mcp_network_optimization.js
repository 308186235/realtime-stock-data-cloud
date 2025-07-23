/**
 * MCP网络优化测试脚本
 * 验证基于MCP分析的网络优化效果
 */

const https = require('https');
const { performance } = require('perf_hooks');

// MCP发现的最优CDN节点
const MCP_OPTIMAL_CDNS = [
  {
    name: 'StaticFile CDN (修复版)',
    testUrl: 'https://cdn.staticfile.net/jquery/3.6.0/jquery.min.js',
    expectedLatency: 840,
    mcpRanking: 1,
    mcpFixed: true
  },
  {
    name: 'BootCDN',
    testUrl: 'https://cdn.bootcdn.net/ajax/libs/jquery/3.6.0/jquery.min.js',
    expectedLatency: 125,
    mcpRanking: 2
  },
  {
    name: 'JSDelivr CDN',
    testUrl: 'https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js',
    expectedLatency: 168,
    mcpRanking: 3
  },
  {
    name: 'unpkg CDN',
    testUrl: 'https://unpkg.com/jquery@3.6.0/dist/jquery.min.js',
    expectedLatency: 246,
    mcpRanking: 4
  },
  {
    name: 'Cloudflare CDN (原域名)',
    testUrl: 'https://aigupiao.me/health',
    expectedLatency: 5000,
    mcpRanking: 5
  }
];

/**
 * 测试单个CDN的延迟
 */
async function testCDNLatency(cdn) {
  return new Promise((resolve) => {
    const startTime = performance.now();
    const url = new URL(cdn.testUrl);
    
    const options = {
      hostname: url.hostname,
      port: 443,
      path: url.pathname,
      method: 'GET',
      timeout: 5000,
      headers: {
        'User-Agent': 'MCP-Network-Optimizer/1.0',
        'Accept': '*/*',
        'Cache-Control': 'no-cache'
      }
    };
    
    const req = https.request(options, (res) => {
      const latency = Math.round(performance.now() - startTime);
      
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        resolve({
          ...cdn,
          actualLatency: latency,
          statusCode: res.statusCode,
          success: res.statusCode === 200,
          responseSize: data.length,
          testTime: new Date().toISOString()
        });
      });
    });
    
    req.on('error', (error) => {
      resolve({
        ...cdn,
        actualLatency: 9999,
        statusCode: 0,
        success: false,
        error: error.message,
        testTime: new Date().toISOString()
      });
    });
    
    req.on('timeout', () => {
      req.destroy();
      resolve({
        ...cdn,
        actualLatency: 9999,
        statusCode: 0,
        success: false,
        error: 'Timeout',
        testTime: new Date().toISOString()
      });
    });
    
    req.end();
  });
}

/**
 * 运行MCP网络优化测试
 */
async function runMCPNetworkTest() {
  console.log('🚀 MCP网络优化测试开始');
  console.log('='.repeat(60));
  console.log('基于MCP全面分析,测试最优CDN节点性能\n');
  
  // 并行测试所有CDN
  console.log('📊 开始并行测试所有CDN节点...\n');
  const testPromises = MCP_OPTIMAL_CDNS.map(testCDNLatency);
  const results = await Promise.all(testPromises);
  
  // 按实际延迟排序
  const sortedResults = results.sort((a, b) => a.actualLatency - b.actualLatency);
  
  console.log('📈 MCP网络优化测试结果:');
  console.log('-'.repeat(80));
  console.log('排名 | CDN名称           | 实际延迟 | MCP预期 | 状态码 | MCP排名 | 优化效果');
  console.log('-'.repeat(80));
  
  sortedResults.forEach((result, index) => {
    const rank = index + 1;
    const latencyStr = result.success ? `${result.actualLatency}ms` : 'FAIL';
    const expectedStr = `${result.expectedLatency}ms`;
    const statusStr = result.success ? result.statusCode.toString() : 'ERR';
    const mcpRankStr = `#${result.mcpRanking}`;
    
    // 计算优化效果
    let optimizationEffect = '';
    if (result.success && result.name !== 'Cloudflare CDN (原域名)') {
      const cloudflareExpected = 5000;
      const improvement = Math.round((cloudflareExpected - result.actualLatency) / cloudflareExpected * 100);
      optimizationEffect = `+${improvement}%`;
    } else if (result.name === 'Cloudflare CDN (原域名)') {
      optimizationEffect = 'BASELINE';
    } else {
      optimizationEffect = 'FAILED';
    }
    
    console.log(`${rank.toString().padStart(2)} | ${result.name.padEnd(17)} | ${latencyStr.padEnd(8)} | ${expectedStr.padEnd(7)} | ${statusStr.padEnd(6)} | ${mcpRankStr.padEnd(7)} | ${optimizationEffect}`);
  });
  
  console.log('-'.repeat(80));
  
  // 分析结果
  const successfulResults = sortedResults.filter(r => r.success);
  const fastestCDN = successfulResults[0];
  
  if (fastestCDN) {
    console.log('\n🎯 MCP优化分析结果:');
    console.log(`✅ 最快CDN: ${fastestCDN.name} (${fastestCDN.actualLatency}ms)`);
    console.log(`📊 MCP预期: ${fastestCDN.expectedLatency}ms`);
    console.log(`🎯 预测准确度: ${Math.round((1 - Math.abs(fastestCDN.actualLatency - fastestCDN.expectedLatency) / fastestCDN.expectedLatency) * 100)}%`);
    
    // 与Cloudflare对比
    const cloudflareResult = results.find(r => r.name === 'Cloudflare CDN (原域名)');
    if (cloudflareResult && !cloudflareResult.success) {
      console.log(`🚀 优化效果: 从Cloudflare超时(>5000ms) → ${fastestCDN.name}(${fastestCDN.actualLatency}ms)`);
      console.log(`📈 性能提升: ${Math.round(5000 / fastestCDN.actualLatency)}倍以上`);
    }
    
    console.log('\n💡 MCP优化建议:');
    console.log(`1. 立即切换到 ${fastestCDN.name}`);
    console.log(`2. 预期延迟降低到 ${fastestCDN.actualLatency}ms`);
    console.log(`3. 用户体验将显著改善`);
    
  } else {
    console.log('\n❌ 所有CDN测试失败,网络环境可能存在问题');
  }
  
  // MCP验证结果
  console.log('\n🔍 MCP分析验证:');
  const mcpTop3 = MCP_OPTIMAL_CDNS.slice(0, 3);
  const actualTop3 = successfulResults.slice(0, 3);
  
  let mcpAccuracy = 0;
  mcpTop3.forEach(mcpCdn => {
    const actualResult = actualTop3.find(actual => actual.name === mcpCdn.name);
    if (actualResult) {
      mcpAccuracy++;
    }
  });
  
  console.log(`📊 MCP预测准确率: ${Math.round(mcpAccuracy / 3 * 100)}%`);
  console.log(`✅ MCP分析${mcpAccuracy >= 2 ? '准确' : '需要调整'}`);
  
  console.log('\n🎉 MCP网络优化测试完成!');
  
  return {
    fastestCDN,
    allResults: sortedResults,
    mcpAccuracy: mcpAccuracy / 3
  };
}

// 运行测试
if (require.main === module) {
  runMCPNetworkTest().catch(console.error);
}

module.exports = { runMCPNetworkTest, testCDNLatency };
