/**
 * 测试API修复效果
 */

const https = require('https');

// 测试API端点
const testEndpoints = [
  'https://aigupiao.me/api/virtual-account/accounts',
  'https://aigupiao.me/api/realtime',
  'https://aigupiao.me/api/market/indices',
  'https://aigupiao.me/api/agent-analysis/status'
];

async function testAPI(url) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const req = https.get(url, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        const endTime = Date.now();
        const responseTime = endTime - startTime;
        
        try {
          const jsonData = JSON.parse(data);
          resolve({
            url,
            status: res.statusCode,
            responseTime,
            success: jsonData.success || (res.statusCode === 200),
            data: jsonData
          });
        } catch (error) {
          resolve({
            url,
            status: res.statusCode,
            responseTime,
            success: false,
            error: 'JSON解析失败',
            rawData: data
          });
        }
      });
    });
    
    req.on('error', (error) => {
      const endTime = Date.now();
      const responseTime = endTime - startTime;
      
      resolve({
        url,
        status: 'ERROR',
        responseTime,
        success: false,
        error: error.message
      });
    });
    
    req.setTimeout(5000, () => {
      req.destroy();
      const endTime = Date.now();
      const responseTime = endTime - startTime;
      
      resolve({
        url,
        status: 'TIMEOUT',
        responseTime,
        success: false,
        error: '请求超时'
      });
    });
  });
}

async function runTests() {
  console.log('🚀 开始测试API修复效果...\n');
  
  for (const endpoint of testEndpoints) {
    console.log(`测试: ${endpoint}`);
    
    const result = await testAPI(endpoint);
    
    if (result.success) {
      console.log(`✅ 成功 - ${result.responseTime}ms`);
      if (result.data && result.data.data) {
        if (Array.isArray(result.data.data)) {
          console.log(`   数据: ${result.data.data.length} 条记录`);
        } else if (result.data.data.stocks) {
          console.log(`   股票数据: ${result.data.data.stocks.length} 只股票`);
        } else {
          console.log(`   数据类型: ${typeof result.data.data}`);
        }
      }
    } else {
      console.log(`❌ 失败 - ${result.responseTime}ms`);
      console.log(`   错误: ${result.error || result.status}`);
    }
    
    console.log('');
  }
  
  console.log('🏁 测试完成');
}

runTests().catch(console.error);
