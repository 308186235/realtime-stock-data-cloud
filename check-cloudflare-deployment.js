#!/usr/bin/env node

/**
 * Cloudflare部署状态检查脚本
 * 验证所有服务是否正常运行
 */

const https = require('https');
const http = require('http');

// 配置
const CONFIG = {
  domains: {
    api: 'api.aigupiao.me',
    app: 'app.aigupiao.me', 
    mobile: 'mobile.aigupiao.me',
    admin: 'admin.aigupiao.me',
    main: 'aigupiao.me'
  },
  
  apiEndpoints: [
    '/api/health',
    '/api/agent/status',
    '/api/trading/balance',
    '/api/stock/quote?code=000001',
    '/api/realtime/stocks',
    '/api/strategy/',
    '/api/portfolio/summary'
  ],
  
  timeout: 10000 // 10秒超时
};

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// HTTP请求函数
function makeRequest(url, timeout = CONFIG.timeout) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const req = https.get(url, { timeout }, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        const responseTime = Date.now() - startTime;
        
        try {
          const jsonData = JSON.parse(data);
          resolve({
            status: res.statusCode,
            data: jsonData,
            responseTime,
            headers: res.headers
          });
        } catch (error) {
          resolve({
            status: res.statusCode,
            data: data,
            responseTime,
            headers: res.headers,
            isJson: false
          });
        }
      });
    });
    
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('请求超时'));
    });
    
    req.on('error', (error) => {
      reject(error);
    });
  });
}

// 检查域名解析
async function checkDNS() {
  log('\n🌐 检查DNS解析...', 'cyan');
  
  const dns = require('dns').promises;
  
  for (const [name, domain] of Object.entries(CONFIG.domains)) {
    try {
      const addresses = await dns.resolve4(domain);
      log(`✅ ${domain}: ${addresses.join(', ')}`, 'green');
    } catch (error) {
      log(`❌ ${domain}: DNS解析失败 - ${error.message}`, 'red');
    }
  }
}

// 检查API端点
async function checkAPIEndpoints() {
  log('\n📡 检查API端点...', 'cyan');
  
  const results = [];
  
  for (const endpoint of CONFIG.apiEndpoints) {
    const url = `https://${CONFIG.domains.api}${endpoint}`;
    
    try {
      log(`🔍 测试: ${endpoint}`, 'yellow');
      const result = await makeRequest(url);
      
      if (result.status === 200) {
        log(`✅ ${endpoint}: ${result.responseTime}ms`, 'green');
        
        // 显示响应数据摘要
        if (result.data && typeof result.data === 'object') {
          if (result.data.success !== undefined) {
            log(`   状态: ${result.data.success ? '成功' : '失败'}`, 'blue');
          }
          if (result.data.message) {
            log(`   消息: ${result.data.message}`, 'blue');
          }
          if (result.data.data && typeof result.data.data === 'object') {
            const keys = Object.keys(result.data.data);
            log(`   数据字段: ${keys.slice(0, 3).join(', ')}${keys.length > 3 ? '...' : ''}`, 'blue');
          }
        }
      } else {
        log(`⚠️ ${endpoint}: HTTP ${result.status}`, 'yellow');
      }
      
      results.push({
        endpoint,
        status: result.status,
        responseTime: result.responseTime,
        success: result.status === 200
      });
      
    } catch (error) {
      log(`❌ ${endpoint}: ${error.message}`, 'red');
      results.push({
        endpoint,
        error: error.message,
        success: false
      });
    }
  }
  
  return results;
}

// 检查前端页面
async function checkFrontendPages() {
  log('\n🎨 检查前端页面...', 'cyan');
  
  const frontendDomains = ['app', 'mobile', 'admin', 'main'];
  const results = [];
  
  for (const domainKey of frontendDomains) {
    const domain = CONFIG.domains[domainKey];
    const url = `https://${domain}`;
    
    try {
      log(`🔍 测试: ${domain}`, 'yellow');
      const result = await makeRequest(url);
      
      if (result.status === 200) {
        log(`✅ ${domain}: ${result.responseTime}ms`, 'green');
        
        // 检查是否是HTML页面
        if (result.headers['content-type'] && result.headers['content-type'].includes('text/html')) {
          log(`   类型: HTML页面`, 'blue');
        } else {
          log(`   类型: ${result.headers['content-type'] || '未知'}`, 'blue');
        }
      } else if (result.status === 302 || result.status === 301) {
        log(`🔄 ${domain}: 重定向到 ${result.headers.location}`, 'yellow');
      } else {
        log(`⚠️ ${domain}: HTTP ${result.status}`, 'yellow');
      }
      
      results.push({
        domain,
        status: result.status,
        responseTime: result.responseTime,
        success: result.status === 200 || result.status === 302
      });
      
    } catch (error) {
      log(`❌ ${domain}: ${error.message}`, 'red');
      results.push({
        domain,
        error: error.message,
        success: false
      });
    }
  }
  
  return results;
}

// 检查SSL证书
async function checkSSL() {
  log('\n🔒 检查SSL证书...', 'cyan');
  
  const tls = require('tls');
  
  for (const [name, domain] of Object.entries(CONFIG.domains)) {
    try {
      const socket = tls.connect(443, domain, { servername: domain }, () => {
        const cert = socket.getPeerCertificate();
        const validFrom = new Date(cert.valid_from);
        const validTo = new Date(cert.valid_to);
        const now = new Date();
        
        if (now >= validFrom && now <= validTo) {
          const daysLeft = Math.floor((validTo - now) / (1000 * 60 * 60 * 24));
          log(`✅ ${domain}: 有效期至 ${validTo.toLocaleDateString()} (${daysLeft}天)`, 'green');
        } else {
          log(`❌ ${domain}: SSL证书已过期`, 'red');
        }
        
        socket.end();
      });
      
      socket.on('error', (error) => {
        log(`❌ ${domain}: SSL检查失败 - ${error.message}`, 'red');
      });
      
    } catch (error) {
      log(`❌ ${domain}: SSL检查失败 - ${error.message}`, 'red');
    }
  }
}

// 性能测试
async function performanceTest() {
  log('\n⚡ 性能测试...', 'cyan');
  
  const testEndpoints = [
    '/api/health',
    '/api/agent/status',
    '/api/stock/quote?code=000001'
  ];
  
  for (const endpoint of testEndpoints) {
    const url = `https://${CONFIG.domains.api}${endpoint}`;
    const times = [];
    
    log(`🏃 测试 ${endpoint} (5次请求)...`, 'yellow');
    
    for (let i = 0; i < 5; i++) {
      try {
        const result = await makeRequest(url);
        times.push(result.responseTime);
      } catch (error) {
        log(`   请求 ${i + 1} 失败: ${error.message}`, 'red');
      }
    }
    
    if (times.length > 0) {
      const avg = times.reduce((a, b) => a + b, 0) / times.length;
      const min = Math.min(...times);
      const max = Math.max(...times);
      
      log(`   平均响应时间: ${avg.toFixed(0)}ms`, 'blue');
      log(`   最快: ${min}ms, 最慢: ${max}ms`, 'blue');
      
      if (avg < 500) {
        log(`   性能评级: 优秀 🚀`, 'green');
      } else if (avg < 1000) {
        log(`   性能评级: 良好 👍`, 'yellow');
      } else {
        log(`   性能评级: 需要优化 ⚠️`, 'red');
      }
    }
  }
}

// 生成报告
function generateReport(apiResults, frontendResults) {
  log('\n📊 部署状态报告', 'magenta');
  log('=' * 50, 'magenta');
  
  // API状态
  const apiSuccess = apiResults.filter(r => r.success).length;
  const apiTotal = apiResults.length;
  log(`\n📡 API端点: ${apiSuccess}/${apiTotal} 正常`, apiSuccess === apiTotal ? 'green' : 'yellow');
  
  // 前端状态
  const frontendSuccess = frontendResults.filter(r => r.success).length;
  const frontendTotal = frontendResults.length;
  log(`🎨 前端页面: ${frontendSuccess}/${frontendTotal} 正常`, frontendSuccess === frontendTotal ? 'green' : 'yellow');
  
  // 总体状态
  const totalSuccess = apiSuccess + frontendSuccess;
  const totalTests = apiTotal + frontendTotal;
  const successRate = (totalSuccess / totalTests * 100).toFixed(1);
  
  log(`\n🎯 总体成功率: ${successRate}%`, successRate >= 90 ? 'green' : successRate >= 70 ? 'yellow' : 'red');
  
  if (successRate >= 90) {
    log('\n🎉 部署状态优秀！所有服务运行正常。', 'green');
  } else if (successRate >= 70) {
    log('\n⚠️ 部署状态良好，但有部分服务需要检查。', 'yellow');
  } else {
    log('\n❌ 部署存在问题，需要立即修复。', 'red');
  }
  
  log('\n📱 访问地址:', 'cyan');
  log(`   主应用: https://${CONFIG.domains.app}`, 'blue');
  log(`   移动端: https://${CONFIG.domains.mobile}`, 'blue');
  log(`   管理后台: https://${CONFIG.domains.admin}`, 'blue');
  log(`   API文档: https://${CONFIG.domains.api}`, 'blue');
}

// 主函数
async function main() {
  log('🔍 Cloudflare部署状态检查', 'magenta');
  log('=' * 40, 'magenta');
  
  try {
    // 检查DNS
    await checkDNS();
    
    // 检查API
    const apiResults = await checkAPIEndpoints();
    
    // 检查前端
    const frontendResults = await checkFrontendPages();
    
    // 检查SSL
    await checkSSL();
    
    // 性能测试
    await performanceTest();
    
    // 生成报告
    generateReport(apiResults, frontendResults);
    
  } catch (error) {
    log(`\n❌ 检查过程中发生错误: ${error.message}`, 'red');
    process.exit(1);
  }
}

// 运行检查
if (require.main === module) {
  main();
}

module.exports = { main, CONFIG };
