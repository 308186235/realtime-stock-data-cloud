/**
 * Cloudflare Worker for Trading System API Proxy
 * 提供API代理、缓存功能和Supabase集成
 */

import { createKVManager, cacheMiddleware, rateLimitMiddleware } from '../kv-storage-config.js';

// 配置
const CONFIG = {
  API_BASE_URL: 'https://realtime-stock-api.pages.dev',
  CACHE_TTL: 300, // 5分钟缓存
  CORS_HEADERS: {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
  },
  SUPABASE_CONFIG: {
    url: 'https://zzukfxwavknskqcepsjb.supabase.co',
    anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw'
  }
};

// 主处理函数
export default {
  async fetch(request, env, ctx) {
    // 处理CORS预检请求
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 200,
        headers: CONFIG.CORS_HEADERS
      });
    }

    try {
      const url = new URL(request.url);
      const path = url.pathname;

      // 创建KV管理器
      const kvManager = createKVManager(env);

      // 应用中间件
      const middlewareChain = async () => {
        // 路由处理
        if (path.startsWith('/api/realtime/')) {
          return await handleRealtimeAPI(request, env, kvManager);
        } else if (path.startsWith('/api/supabase/')) {
          return await handleSupabaseAPI(request, env, kvManager);
        } else if (path.startsWith('/api/')) {
          return await handleAPIRequest(request, env, kvManager);
        } else if (path === '/health') {
          return await handleHealthCheck(kvManager);
        } else if (path === '/') {
          return await handleRoot();
        } else {
          return new Response('Not Found', { status: 404 });
        }
      };

      // 应用限流中间件
      return await rateLimitMiddleware(request, env, middlewareChain);

    } catch (error) {
      console.error('Worker error:', error);
      return new Response(JSON.stringify({
        error: 'Internal Server Error',
        message: error.message,
        timestamp: new Date().toISOString()
      }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          ...CONFIG.CORS_HEADERS
        }
      });
    }
  }
};

/**
 * 处理实时股票API请求
 */
async function handleRealtimeAPI(request, env, kvManager) {
  const url = new URL(request.url);
  const path = url.pathname.replace('/api/realtime', '');
  
  // 检查缓存
  const cacheKey = `realtime:${path}:${url.search}`;
  const cached = await kvManager.getStockData(cacheKey);
  
  if (cached && request.method === 'GET') {
    return new Response(JSON.stringify(cached), {
      headers: {
        'Content-Type': 'application/json',
        'X-Cache': 'HIT',
        ...CONFIG.CORS_HEADERS
      }
    });
  }

  // 代理到后端API
  const backendUrl = `${CONFIG.API_BASE_URL}/api/realtime${path}${url.search}`;
  const backendRequest = new Request(backendUrl, {
    method: request.method,
    headers: request.headers,
    body: request.method !== 'GET' ? request.body : null
  });

  const response = await fetch(backendRequest);
  const responseData = await response.json();

  // 缓存GET请求的响应
  if (request.method === 'GET' && response.ok) {
    await kvManager.setStockData(cacheKey, responseData, 60); // 1分钟缓存
  }

  return new Response(JSON.stringify(responseData), {
    status: response.status,
    headers: {
      'Content-Type': 'application/json',
      'X-Cache': 'MISS',
      ...CONFIG.CORS_HEADERS
    }
  });
}

/**
 * 处理Supabase API请求
 */
async function handleSupabaseAPI(request, env, kvManager) {
  const url = new URL(request.url);
  const path = url.pathname.replace('/api/supabase', '');
  
  // 检查缓存
  const cacheKey = `supabase:${path}:${url.search}`;
  const cached = await kvManager.getStockData(cacheKey);
  
  if (cached && request.method === 'GET') {
    return new Response(JSON.stringify(cached), {
      headers: {
        'Content-Type': 'application/json',
        'X-Cache': 'HIT',
        ...CONFIG.CORS_HEADERS
      }
    });
  }

  // 代理到后端API
  const backendUrl = `${CONFIG.API_BASE_URL}/api/supabase${path}${url.search}`;
  const backendRequest = new Request(backendUrl, {
    method: request.method,
    headers: request.headers,
    body: request.method !== 'GET' ? request.body : null
  });

  const response = await fetch(backendRequest);
  const responseData = await response.json();

  // 缓存GET请求的响应
  if (request.method === 'GET' && response.ok) {
    await kvManager.setStockData(cacheKey, responseData, 300); // 5分钟缓存
  }

  return new Response(JSON.stringify(responseData), {
    status: response.status,
    headers: {
      'Content-Type': 'application/json',
      'X-Cache': 'MISS',
      ...CONFIG.CORS_HEADERS
    }
  });
}

/**
 * 处理通用API请求
 */
async function handleAPIRequest(request, env, kvManager) {
  const url = new URL(request.url);
  
  // 代理到后端API
  const backendUrl = `${CONFIG.API_BASE_URL}${url.pathname}${url.search}`;
  const backendRequest = new Request(backendUrl, {
    method: request.method,
    headers: request.headers,
    body: request.method !== 'GET' ? request.body : null
  });

  const response = await fetch(backendRequest);
  const responseText = await response.text();

  return new Response(responseText, {
    status: response.status,
    headers: {
      'Content-Type': response.headers.get('Content-Type') || 'application/json',
      ...CONFIG.CORS_HEADERS
    }
  });
}

/**
 * 健康检查
 */
async function handleHealthCheck(kvManager) {
  try {
    // 检查后端API健康状态
    const backendHealth = await fetch(`${CONFIG.API_BASE_URL}/health`);
    const backendStatus = backendHealth.ok;

    // 检查KV存储
    const kvTest = await kvManager.setStockData('health_check', { test: true }, 60);
    const kvStatus = true; // KV操作成功

    // 检查Supabase连接
    const supabaseHealth = await fetch(`${CONFIG.SUPABASE_CONFIG.url}/rest/v1/`, {
      headers: {
        'apikey': CONFIG.SUPABASE_CONFIG.anonKey,
        'Authorization': `Bearer ${CONFIG.SUPABASE_CONFIG.anonKey}`
      }
    });
    const supabaseStatus = supabaseHealth.ok;

    const healthData = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        worker: true,
        backend_api: backendStatus,
        kv_storage: kvStatus,
        supabase: supabaseStatus
      },
      version: '1.0.0'
    };

    return new Response(JSON.stringify(healthData), {
      headers: {
        'Content-Type': 'application/json',
        ...CONFIG.CORS_HEADERS
      }
    });
  } catch (error) {
    return new Response(JSON.stringify({
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString()
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        ...CONFIG.CORS_HEADERS
      }
    });
  }
}

/**
 * 根路径处理
 */
async function handleRoot() {
  const welcomeMessage = {
    message: 'Trading System API Proxy',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      realtime_api: '/api/realtime/*',
      supabase_api: '/api/supabase/*',
      general_api: '/api/*'
    },
    features: [
      'API代理',
      'KV缓存',
      '限流保护',
      'CORS支持',
      'Supabase集成'
    ],
    timestamp: new Date().toISOString()
  };

  return new Response(JSON.stringify(welcomeMessage), {
    headers: {
      'Content-Type': 'application/json',
      ...CONFIG.CORS_HEADERS
    }
  });
}

/**
 * 定时任务：清理缓存
 */
export async function scheduled(event, env, ctx) {
  const kvManager = createKVManager(env);
  
  try {
    await kvManager.cleanup();
    console.log('定时清理任务完成');
  } catch (error) {
    console.error('定时清理任务失败:', error);
  }
}
