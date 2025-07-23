/**
 * 云服务器到本地交易执行延迟测试
 * 测试云端Agent决策 → 本地电脑交易执行的真实延迟
 */

const https = require('https');
const http = require('http');
const { performance } = require('perf_hooks');

// 本地交易服务器配置
const LOCAL_TRADING_CONFIG = {
  host: 'localhost',
  port: 8001,  // 本地交易服务器端口
  endpoints: {
    trade: '/trade',
    export: '/export',
    health: '/health'
  }
};

// 云服务器配置
const CLOUD_CONFIG = {
  host: 'aigupiao.me',
  endpoints: {
    agentBuy: '/api/agent/buy',
    agentSell: '/api/agent/sell',
    agentExport: '/api/agent/export'
  }
};

/**
 * 测试本地交易服务器延迟
 */
async function testLocalTradingLatency() {
  console.log('🔧 测试本地交易服务器延迟...\n');
  
  const tests = [
    {
      name: '健康检查',
      method: 'GET',
      path: LOCAL_TRADING_CONFIG.endpoints.health,
      data: null
    },
    {
      name: '模拟买入交易',
      method: 'POST',
      path: LOCAL_TRADING_CONFIG.endpoints.trade,
      data: {
        action: 'buy',
        stock_code: '000001',
        quantity: 100,
        price: 10.50
      }
    },
    {
      name: '模拟卖出交易',
      method: 'POST',
      path: LOCAL_TRADING_CONFIG.endpoints.trade,
      data: {
        action: 'sell',
        stock_code: '000001',
        quantity: 100,
        price: 10.60
      }
    },
    {
      name: '导出持仓数据',
      method: 'POST',
      path: LOCAL_TRADING_CONFIG.endpoints.export,
      data: {
        data_type: 'holdings'
      }
    },
    {
      name: '导出交易记录',
      method: 'POST',
      path: LOCAL_TRADING_CONFIG.endpoints.export,
      data: {
        data_type: 'transactions'
      }
    }
  ];
  
  const results = [];
  
  for (const test of tests) {
    try {
      console.log(`📊 测试: ${test.name}`);
      const startTime = performance.now();
      
      const result = await makeLocalRequest(test.method, test.path, test.data);
      const latency = Math.round(performance.now() - startTime);
      
      results.push({
        name: test.name,
        latency,
        success: true,
        statusCode: result.statusCode,
        responseSize: JSON.stringify(result.data || '').length
      });
      
      console.log(`✅ ${test.name}: ${latency}ms`);
      
    } catch (error) {
      results.push({
        name: test.name,
        latency: 9999,
        success: false,
        error: error.message
      });
      
      console.log(`❌ ${test.name}: 失败 - ${error.message}`);
    }
    
    // 避免请求过快
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  
  return results;
}

/**
 * 测试云端到本地的完整交易链路延迟
 */
async function testCloudToLocalChainLatency() {
  console.log('\n🌐 测试云端到本地完整交易链路延迟...\n');
  
  const chainTests = [
    {
      name: '云端Agent买入决策 → 本地执行',
      cloudEndpoint: CLOUD_CONFIG.endpoints.agentBuy,
      data: {
        stock_code: '000001',
        quantity: 100,
        price: 10.50,
        agent_id: 'test_agent'
      }
    },
    {
      name: '云端Agent卖出决策 → 本地执行',
      cloudEndpoint: CLOUD_CONFIG.endpoints.agentSell,
      data: {
        stock_code: '000001',
        quantity: 100,
        price: 10.60,
        agent_id: 'test_agent'
      }
    },
    {
      name: '云端Agent导出请求 → 本地执行',
      cloudEndpoint: CLOUD_CONFIG.endpoints.agentExport + '/holdings',
      data: {
        agent_id: 'test_agent'
      }
    }
  ];
  
  const results = [];
  
  for (const test of chainTests) {
    try {
      console.log(`🔗 测试: ${test.name}`);
      const startTime = performance.now();
      
      // 发送到云端,云端会转发到本地
      const result = await makeCloudRequest('POST', test.cloudEndpoint, test.data);
      const totalLatency = Math.round(performance.now() - startTime);
      
      results.push({
        name: test.name,
        totalLatency,
        success: true,
        statusCode: result.statusCode,
        responseData: result.data
      });
      
      console.log(`✅ ${test.name}: ${totalLatency}ms (完整链路)`);
      
    } catch (error) {
      results.push({
        name: test.name,
        totalLatency: 9999,
        success: false,
        error: error.message
      });
      
      console.log(`❌ ${test.name}: 失败 - ${error.message}`);
    }
    
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  return results;
}

/**
 * 发送本地请求
 */
function makeLocalRequest(method, path, data) {
  return new Promise((resolve, reject) => {
    const postData = data ? JSON.stringify(data) : null;
    
    const options = {
      hostname: LOCAL_TRADING_CONFIG.host,
      port: LOCAL_TRADING_CONFIG.port,
      path: path,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };
    
    if (postData) {
      options.headers['Content-Length'] = Buffer.byteLength(postData);
    }
    
    const req = http.request(options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        try {
          const data = responseData ? JSON.parse(responseData) : null;
          resolve({
            statusCode: res.statusCode,
            data: data
          });
        } catch (error) {
          resolve({
            statusCode: res.statusCode,
            data: responseData
          });
        }
      });
    });
    
    req.on('error', (error) => {
      reject(error);
    });
    
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
    
    req.setTimeout(5000);
    
    if (postData) {
      req.write(postData);
    }
    
    req.end();
  });
}

/**
 * 发送云端请求
 */
function makeCloudRequest(method, path, data) {
  return new Promise((resolve, reject) => {
    const postData = data ? JSON.stringify(data) : null;
    
    const options = {
      hostname: CLOUD_CONFIG.host,
      port: 443,
      path: path,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Cloud-Local-Trading-Test/1.0'
      }
    };
    
    if (postData) {
      options.headers['Content-Length'] = Buffer.byteLength(postData);
    }
    
    const req = https.request(options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        try {
          const data = responseData ? JSON.parse(responseData) : null;
          resolve({
            statusCode: res.statusCode,
            data: data
          });
        } catch (error) {
          resolve({
            statusCode: res.statusCode,
            data: responseData
          });
        }
      });
    });
    
    req.on('error', (error) => {
      reject(error);
    });
    
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
    
    req.setTimeout(10000);
    
    if (postData) {
      req.write(postData);
    }
    
    req.end();
  });
}

/**
 * 运行完整的延迟测试
 */
async function runTradingLatencyTest() {
  console.log('🚀 云服务器到本地交易执行延迟测试开始');
  console.log('='.repeat(60));
  console.log('测试架构: 云端Agent决策 → 本地电脑交易执行\n');
  
  // 1. 测试本地交易服务器延迟
  const localResults = await testLocalTradingLatency();
  
  // 2. 测试云端到本地完整链路延迟
  const chainResults = await testCloudToLocalChainLatency();
  
  // 3. 分析结果
  console.log('\n📊 延迟测试结果分析:');
  console.log('='.repeat(60));
  
  console.log('\n🖥️ 本地交易服务器延迟:');
  console.log('-'.repeat(50));
  localResults.forEach(result => {
    if (result.success) {
      console.log(`✅ ${result.name.padEnd(20)}: ${result.latency}ms`);
    } else {
      console.log(`❌ ${result.name.padEnd(20)}: 失败`);
    }
  });
  
  console.log('\n🌐 云端到本地完整链路延迟:');
  console.log('-'.repeat(50));
  chainResults.forEach(result => {
    if (result.success) {
      console.log(`✅ ${result.name}: ${result.totalLatency}ms`);
    } else {
      console.log(`❌ ${result.name}: 失败`);
    }
  });
  
  // 4. 计算平均延迟
  const successfulLocal = localResults.filter(r => r.success);
  const successfulChain = chainResults.filter(r => r.success);
  
  if (successfulLocal.length > 0) {
    const avgLocalLatency = Math.round(
      successfulLocal.reduce((sum, r) => sum + r.latency, 0) / successfulLocal.length
    );
    console.log(`\n📊 本地交易平均延迟: ${avgLocalLatency}ms`);
  }
  
  if (successfulChain.length > 0) {
    const avgChainLatency = Math.round(
      successfulChain.reduce((sum, r) => sum + r.totalLatency, 0) / successfulChain.length
    );
    console.log(`📊 云端到本地平均延迟: ${avgChainLatency}ms`);
  }
  
  console.log('\n🎯 延迟分析:');
  console.log('- 本地交易延迟: 主要是交易软件响应时间');
  console.log('- 云端到本地延迟: 网络传输 + 本地执行时间');
  console.log('- 实际交易延迟: 包含决策,传输,执行的完整时间');
  
  console.log('\n🎉 交易延迟测试完成!');
  
  return {
    localResults,
    chainResults,
    avgLocalLatency: successfulLocal.length > 0 ? 
      Math.round(successfulLocal.reduce((sum, r) => sum + r.latency, 0) / successfulLocal.length) : null,
    avgChainLatency: successfulChain.length > 0 ? 
      Math.round(successfulChain.reduce((sum, r) => sum + r.totalLatency, 0) / successfulChain.length) : null
  };
}

// 运行测试
if (require.main === module) {
  runTradingLatencyTest().catch(console.error);
}

module.exports = { runTradingLatencyTest };
