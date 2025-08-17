/**
 * StaticFile CDN修复测试 - 基于MCP全面分析
 * 发现: 旧域名 cdn.staticfile.org 已停止维护,新域名 cdn.staticfile.net 正常工作
 */

const https = require('https');
const { performance } = require('perf_hooks');

// MCP发现的StaticFile CDN域名变更
const STATICFILE_DOMAINS = [
  {
    name: 'StaticFile CDN (新域名)',
    domain: 'cdn.staticfile.net',
    testUrl: 'https://cdn.staticfile.net/jquery/3.6.0/jquery.min.js',
    status: 'active',
    note: 'MCP发现:官方已更新为.net域名'
  },
  {
    name: 'StaticFile CDN (旧域名)',
    domain: 'cdn.staticfile.org',
    testUrl: 'https://cdn.staticfile.org/jquery/3.6.0/jquery.min.js',
    status: 'deprecated',
    note: 'MCP发现:已停止维护,不再提供服务'
  }
];

// 对比测试的其他CDN
const OTHER_CDNS = [
  {
    name: 'BootCDN',
    testUrl: 'https://cdn.bootcdn.net/ajax/libs/jquery/3.6.0/jquery.min.js',
    expectedLatency: 843
  },
  {
    name: 'JSDelivr CDN',
    testUrl: 'https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js',
    expectedLatency: 1047
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
        'User-Agent': 'MCP-StaticFile-Fix-Test/1.0',
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
          contentType: res.headers['content-type'],
          server: res.headers['server'],
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
 * 运行StaticFile CDN修复测试
 */
async function runStaticFileCDNFixTest() {
  console.log('🔧 StaticFile CDN修复测试开始');
  console.log('='.repeat(60));
  console.log('基于MCP全面分析,测试域名变更修复效果\n');
  
  // 测试StaticFile CDN的新旧域名
  console.log('📊 测试StaticFile CDN域名变更...\n');
  const staticFilePromises = STATICFILE_DOMAINS.map(testCDNLatency);
  const staticFileResults = await Promise.all(staticFilePromises);
  
  console.log('🔍 StaticFile CDN域名测试结果:');
  console.log('-'.repeat(80));
  console.log('域名类型           | 域名                | 延迟     | 状态码 | 结果   | 说明');
  console.log('-'.repeat(80));
  
  staticFileResults.forEach(result => {
    const typeStr = result.name.padEnd(17);
    const domainStr = result.domain.padEnd(19);
    const latencyStr = result.success ? `${result.actualLatency}ms` : 'FAIL';
    const statusStr = result.success ? result.statusCode.toString() : 'ERR';
    const resultStr = result.success ? '✅ 成功' : '❌ 失败';
    
    console.log(`${typeStr} | ${domainStr} | ${latencyStr.padEnd(8)} | ${statusStr.padEnd(6)} | ${resultStr.padEnd(6)} | ${result.note}`);
  });
  
  console.log('-'.repeat(80));
  
  // 找到成功的StaticFile CDN
  const workingStaticFile = staticFileResults.find(r => r.success);
  
  if (workingStaticFile) {
    console.log(`\n🎉 StaticFile CDN修复成功!`);
    console.log(`✅ 工作域名: ${workingStaticFile.domain}`);
    console.log(`⚡ 实际延迟: ${workingStaticFile.actualLatency}ms`);
    console.log(`📊 响应大小: ${workingStaticFile.responseSize} bytes`);
    console.log(`🔧 服务器: ${workingStaticFile.server || 'Unknown'}`);
    
    // 与其他CDN对比测试
    console.log('\n📈 与其他CDN对比测试...');
    const otherPromises = OTHER_CDNS.map(testCDNLatency);
    const otherResults = await Promise.all(otherPromises);
    
    const allResults = [workingStaticFile, ...otherResults].sort((a, b) => a.actualLatency - b.actualLatency);
    
    console.log('\n🏆 最终CDN性能排名:');
    console.log('-'.repeat(60));
    console.log('排名 | CDN名称           | 延迟     | 性能等级');
    console.log('-'.repeat(60));
    
    allResults.forEach((result, index) => {
      if (!result.success) return;
      
      const rank = index + 1;
      const nameStr = (result.name || result.domain).padEnd(17);
      const latencyStr = `${result.actualLatency}ms`.padEnd(8);
      
      let performanceLevel;
      if (result.actualLatency < 200) performanceLevel = '🚀 优秀';
      else if (result.actualLatency < 500) performanceLevel = '✅ 良好';
      else if (result.actualLatency < 1000) performanceLevel = '🔄 一般';
      else performanceLevel = '⚠️ 较慢';
      
      console.log(`${rank.toString().padStart(2)} | ${nameStr} | ${latencyStr} | ${performanceLevel}`);
    });
    
    console.log('-'.repeat(60));
    
    // 分析结果
    const fastestCDN = allResults[0];
    console.log('\n🎯 MCP修复分析结果:');
    console.log(`🏆 最快CDN: ${fastestCDN.name || fastestCDN.domain} (${fastestCDN.actualLatency}ms)`);
    
    if (fastestCDN.domain === 'cdn.staticfile.net') {
      console.log('🎉 StaticFile CDN修复后成为最快选择!');
      console.log('💡 建议立即更新配置使用新域名');
    } else {
      console.log(`📊 StaticFile CDN (${workingStaticFile.actualLatency}ms) 排名第${allResults.findIndex(r => r.domain === 'cdn.staticfile.net') + 1}`);
      console.log('💡 StaticFile CDN已修复,可作为备用选择');
    }
    
  } else {
    console.log('\n❌ StaticFile CDN修复失败');
    console.log('🔍 两个域名都无法连接,可能存在其他问题');
    
    const failedOld = staticFileResults.find(r => r.domain === 'cdn.staticfile.org');
    const failedNew = staticFileResults.find(r => r.domain === 'cdn.staticfile.net');
    
    console.log(`\n📋 失败详情:`);
    console.log(`- 旧域名 (.org): ${failedOld.error}`);
    console.log(`- 新域名 (.net): ${failedNew.error}`);
  }
  
  console.log('\n🔧 MCP修复建议:');
  if (workingStaticFile) {
    console.log(`1. ✅ 立即更新配置使用: ${workingStaticFile.domain}`);
    console.log(`2. 🔄 移除旧域名: cdn.staticfile.org`);
    console.log(`3. 📊 预期延迟: ${workingStaticFile.actualLatency}ms`);
  } else {
    console.log('1. ⚠️ StaticFile CDN暂时不可用');
    console.log('2. 🔄 继续使用其他CDN作为主要选择');
    console.log('3. 📅 定期重新测试StaticFile CDN状态');
  }
  
  console.log('\n🎉 StaticFile CDN修复测试完成!');
  
  return {
    staticFileFixed: !!workingStaticFile,
    workingDomain: workingStaticFile?.domain,
    latency: workingStaticFile?.actualLatency,
    allResults: staticFileResults
  };
}

// 运行测试
if (require.main === module) {
  runStaticFileCDNFixTest().catch(console.error);
}

module.exports = { runStaticFileCDNFixTest, testCDNLatency };
