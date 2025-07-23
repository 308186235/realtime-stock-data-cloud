/**
 * 简单的交易测试 - 检查是否真的执行了交易
 */

const http = require('http');

async function testLocalTrading() {
  console.log('🔍 检查本地交易服务器是否真的执行交易...\n');
  
  // 测试健康检查
  console.log('1. 测试健康检查...');
  try {
    const healthResult = await makeRequest('GET', '/health', null);
    console.log('状态码:', healthResult.statusCode);
    console.log('健康检查响应:', JSON.stringify(healthResult.data, null, 2));
    console.log('原始响应:', healthResult.raw);
  } catch (error) {
    console.log('健康检查失败:', error.message);
  }
  
  // 测试交易请求
  console.log('\n2. 测试买入交易...');
  try {
    const tradeResult = await makeRequest('POST', '/trade', {
      action: 'buy',
      stock_code: '000001',
      quantity: 100,
      price: 10.50
    });
    console.log('买入交易响应:', JSON.stringify(tradeResult.data, null, 2));
  } catch (error) {
    console.log('买入交易失败:', error.message);
  }
  
  // 测试导出请求
  console.log('\n3. 测试数据导出...');
  try {
    const exportResult = await makeRequest('POST', '/export', {
      data_type: 'holdings'
    });
    console.log('数据导出响应:', JSON.stringify(exportResult.data, null, 2));
  } catch (error) {
    console.log('数据导出失败:', error.message);
  }
}

function makeRequest(method, path, data) {
  return new Promise((resolve, reject) => {
    const postData = data ? JSON.stringify(data) : null;
    
    const options = {
      hostname: 'localhost',
      port: 8888,
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
            data: data,
            raw: responseData
          });
        } catch (error) {
          resolve({
            statusCode: res.statusCode,
            data: responseData,
            raw: responseData
          });
        }
      });
    });
    
    req.on('error', (error) => {
      reject(error);
    });
    
    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
    
    if (postData) {
      req.write(postData);
    }
    
    req.end();
  });
}

// 运行测试
testLocalTrading().catch(console.error);
