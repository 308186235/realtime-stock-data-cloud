/**
 * 部署测试脚本
 * 用于验证 aigupiao.me 系统各项功能
 */

const DOMAIN = 'https://aigupiao.me';
const TEST_ENDPOINTS = [
  '/',
  '/mobile/',
  '/admin/',
  '/api/stock-data?symbol=000001',
  '/api/account-info',
  '/api/realtime-data?symbols=000001,000002'
];

async function runTests() {
  console.log('🚀 开始测试 AI股票交易系统部署...\n');
  
  const results = [];
  
  for (const endpoint of TEST_ENDPOINTS) {
    const url = `${DOMAIN}${endpoint}`;
    console.log(`测试: ${url}`);
    
    try {
      const startTime = Date.now();
      const response = await fetch(url);
      const endTime = Date.now();
      const responseTime = endTime - startTime;
      
      const result = {
        url,
        status: response.status,
        statusText: response.statusText,
        responseTime: `${responseTime}ms`,
        contentType: response.headers.get('content-type'),
        success: response.ok
      };
      
      results.push(result);
      
      if (response.ok) {
        console.log(`✅ 成功 - ${response.status} (${responseTime}ms)`);
      } else {
        console.log(`❌ 失败 - ${response.status} ${response.statusText}`);
      }
      
      // 如果是API接口,显示响应内容
      if (endpoint.startsWith('/api/')) {
        try {
          const data = await response.json();
          console.log(`   响应: ${JSON.stringify(data).substring(0, 100)}...`);
        } catch (e) {
          console.log(`   响应: 非JSON格式`);
        }
      }
      
    } catch (error) {
      console.log(`❌ 错误 - ${error.message}`);
      results.push({
        url,
        error: error.message,
        success: false
      });
    }
    
    console.log('');
  }
  
  // 生成测试报告
  generateReport(results);
}

function generateReport(results) {
  console.log('📊 测试报告');
  console.log('='.repeat(50));
  
  const successful = results.filter(r => r.success).length;
  const total = results.length;
  const successRate = ((successful / total) * 100).toFixed(1);
  
  console.log(`总测试数: ${total}`);
  console.log(`成功数: ${successful}`);
  console.log(`失败数: ${total - successful}`);
  console.log(`成功率: ${successRate}%\n`);
  
  // 详细结果
  console.log('详细结果:');
  results.forEach((result, index) => {
    console.log(`${index + 1}. ${result.url}`);
    console.log(`   状态: ${result.success ? '✅ 成功' : '❌ 失败'}`);
    if (result.status) {
      console.log(`   HTTP: ${result.status} ${result.statusText || ''}`);
      console.log(`   响应时间: ${result.responseTime}`);
      console.log(`   内容类型: ${result.contentType || 'N/A'}`);
    }
    if (result.error) {
      console.log(`   错误: ${result.error}`);
    }
    console.log('');
  });
  
  // 建议
  console.log('🔧 建议:');
  if (successRate < 100) {
    console.log('- 检查失败的端点配置');
    console.log('- 验证 Cloudflare Worker 部署状态');
    console.log('- 确认自定义域名绑定');
    console.log('- 检查 Supabase 连接配置');
  } else {
    console.log('- 所有测试通过!系统运行正常 🎉');
  }
}

// 测试 WebSocket 连接
async function testWebSocket() {
  console.log('🔌 测试 WebSocket 连接...');
  
  return new Promise((resolve) => {
    try {
      const ws = new WebSocket(`wss://aigupiao.me/ws/`);
      
      ws.onopen = function() {
        console.log('✅ WebSocket 连接成功');
        
        // 发送订阅消息
        ws.send(JSON.stringify({
          type: 'subscribe',
          symbols: ['000001', '000002']
        }));
      };
      
      ws.onmessage = function(event) {
        console.log('📨 收到消息:', event.data.substring(0, 100) + '...');
      };
      
      ws.onerror = function(error) {
        console.log('❌ WebSocket 错误:', error);
        resolve(false);
      };
      
      ws.onclose = function() {
        console.log('🔌 WebSocket 连接关闭');
        resolve(true);
      };
      
      // 5秒后关闭连接
      setTimeout(() => {
        ws.close();
      }, 5000);
      
    } catch (error) {
      console.log('❌ WebSocket 测试失败:', error.message);
      resolve(false);
    }
  });
}

// 测试交易功能
async function testTrading() {
  console.log('💰 测试交易功能...');
  
  try {
    // 测试获取账户信息
    const accountResponse = await fetch(`${DOMAIN}/api/account-info`);
    const accountData = await accountResponse.json();
    console.log('✅ 账户信息获取成功:', accountData.success ? '成功' : '失败');
    
    // 测试AI决策
    const decisionResponse = await fetch(`${DOMAIN}/api/trading-decision`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        symbol: '000001',
        amount: 1000,
        strategy: 'momentum'
      })
    });
    
    const decisionData = await decisionResponse.json();
    console.log('✅ AI决策测试:', decisionData.success ? '成功' : '失败');
    if (decisionData.decision) {
      console.log(`   建议: ${decisionData.decision.action}`);
      console.log(`   置信度: ${(decisionData.decision.confidence * 100).toFixed(1)}%`);
    }
    
    // 测试提交交易(模拟)
    const tradeResponse = await fetch(`${DOMAIN}/api/submit-trade`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        symbol: '000001',
        action: 'BUY',
        amount: 100,
        price: 0
      })
    });
    
    const tradeData = await tradeResponse.json();
    console.log('✅ 交易提交测试:', tradeData.success ? '成功' : '失败');
    
  } catch (error) {
    console.log('❌ 交易功能测试失败:', error.message);
  }
}

// 主函数
async function main() {
  console.log('🎯 AI股票交易系统 - 部署测试工具');
  console.log('域名: aigupiao.me');
  console.log('时间:', new Date().toLocaleString());
  console.log('='.repeat(50));
  console.log('');
  
  // 基础功能测试
  await runTests();
  
  console.log('\n');
  
  // WebSocket 测试
  if (typeof WebSocket !== 'undefined') {
    await testWebSocket();
  } else {
    console.log('⚠️  WebSocket 测试跳过(Node.js环境)');
  }
  
  console.log('\n');
  
  // 交易功能测试
  await testTrading();
  
  console.log('\n🎉 测试完成!');
}

// 运行测试
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { runTests, testWebSocket, testTrading };
} else {
  main();
}
