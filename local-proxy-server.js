/**
 * 本地代理服务器 - 解决云端访问慢的问题
 * 
 * 功能:
 * 1. 本地高速API服务
 * 2. 智能云端备份
 * 3. 自动故障转移
 * 4. 缓存优化
 */

const http = require('http');
const https = require('https');
const url = require('url');

// 配置
const LOCAL_PORT = 8788; // 避免与wrangler dev冲突
const CLOUD_ENDPOINTS = [
  'https://api.aigupiao.me',
  'https://ai-stock-trading-agent.308186235.workers.dev'
];

// 缓存
const responseCache = new Map();
const CACHE_TTL = 30000; // 30秒

// 健康状态
const endpointHealth = new Map();

// 创建本地服务器
const server = http.createServer(async (req, res) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  try {
    // 1. 首先尝试本地Worker (如果运行中)
    const localResponse = await tryLocalWorker(req);
    if (localResponse) {
      console.log('✅ 使用本地Worker');
      return sendResponse(res, localResponse);
    }
    
    // 2. 检查缓存
    const cacheKey = `${req.method}:${req.url}`;
    const cached = responseCache.get(cacheKey);
    if (cached && (Date.now() - cached.timestamp) < CACHE_TTL) {
      console.log('📦 使用缓存响应');
      return sendResponse(res, cached.response);
    }
    
    // 3. 尝试云端端点
    for (const endpoint of CLOUD_ENDPOINTS) {
      try {
        const cloudResponse = await tryCloudEndpoint(req, endpoint);
        if (cloudResponse) {
          console.log(`☁️ 使用云端: ${endpoint}`);
          
          // 缓存成功的响应
          if (req.method === 'GET') {
            responseCache.set(cacheKey, {
              response: cloudResponse,
              timestamp: Date.now()
            });
          }
          
          return sendResponse(res, cloudResponse);
        }
      } catch (error) {
        console.error(`云端端点失败 ${endpoint}:`, error.message);
        continue;
      }
    }
    
    // 4. 所有端点都失败
    const errorResponse = {
      success: false,
      error: '所有服务端点都不可用',
      message: '本地Worker未运行,云端服务不可达',
      suggestions: [
        '1. 启动本地Worker: wrangler dev',
        '2. 检查网络连接',
        '3. 稍后重试'
      ],
      timestamp: new Date().toISOString()
    };
    
    res.writeHead(503, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(errorResponse, null, 2));
    
  } catch (error) {
    console.error('代理服务器错误:', error);
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    }));
  }
});

// 尝试本地Worker
async function tryLocalWorker(req) {
  try {
    const localUrl = `http://127.0.0.1:8787${req.url}`;
    const response = await makeRequest(localUrl, req.method, req.headers);
    return response;
  } catch (error) {
    return null; // 本地Worker未运行
  }
}

// 尝试云端端点
async function tryCloudEndpoint(req, endpoint) {
  const cloudUrl = `${endpoint}${req.url}`;
  return await makeRequest(cloudUrl, req.method, req.headers, 10000); // 10秒超时
}

// 发起HTTP请求
function makeRequest(targetUrl, method, headers, timeout = 5000) {
  return new Promise((resolve, reject) => {
    const parsedUrl = url.parse(targetUrl);
    const isHttps = parsedUrl.protocol === 'https:';
    const httpModule = isHttps ? https : http;
    
    const options = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || (isHttps ? 443 : 80),
      path: parsedUrl.path,
      method: method,
      headers: {
        ...headers,
        'Host': parsedUrl.hostname,
        'User-Agent': 'Local-Proxy-Server/1.0'
      },
      timeout: timeout
    };
    
    const req = httpModule.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          body: data
        });
      });
    });
    
    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
    
    req.end();
  });
}

// 发送响应
function sendResponse(res, response) {
  res.writeHead(response.statusCode, {
    'Content-Type': response.headers['content-type'] || 'application/json',
    'Access-Control-Allow-Origin': '*',
    'X-Proxy-Server': 'Local-Hybrid-Proxy/1.0'
  });
  res.end(response.body);
}

// 启动服务器
server.listen(LOCAL_PORT, () => {
  console.log(`
🚀 本地代理服务器启动成功!

📍 服务地址: http://127.0.0.1:${LOCAL_PORT}
🎯 功能特性:
   ✅ 本地Worker优先 (60ms响应)
   ☁️ 云端智能备份
   📦 响应缓存优化
   🔄 自动故障转移

💡 使用方法:
   前端API地址改为: http://127.0.0.1:${LOCAL_PORT}
   
🔧 建议配置:
   1. 启动本地Worker: wrangler dev
   2. 更新前端配置指向此代理
   3. 享受高速本地服务!
`);
});

// 优雅关闭
process.on('SIGINT', () => {
  console.log('\n🛑 正在关闭代理服务器...');
  server.close(() => {
    console.log('✅ 代理服务器已关闭');
    process.exit(0);
  });
});
