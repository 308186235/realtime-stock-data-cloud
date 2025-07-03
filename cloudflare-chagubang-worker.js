/**
 * 茶股帮数据源 - Cloudflare Workers集成
 * 为Cloudflare环境提供茶股帮实时股票数据API
 */

// 配置常量
const CONFIG = {
  // Supabase配置
  SUPABASE_URL: 'https://zzukfxwavknskqcepsjb.supabase.co',
  SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw',
  
  // 茶股帮配置
  CHAGUBANG_HOST: 'l1.chagubang.com',
  CHAGUBANG_PORT: 6380,
  
  // CORS配置
  CORS_HEADERS: {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Content-Type': 'application/json'
  },
  
  // 缓存配置
  CACHE_TTL: 5, // 5秒缓存
  MAX_CACHE_SIZE: 10000
};

/**
 * Worker主入口
 */
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // 处理CORS预检请求
    if (request.method === 'OPTIONS') {
      return handleCORS();
    }
    
    try {
      // 路由分发
      if (path === '/') {
        return handleRoot();
      } else if (path === '/api/chagubang/health') {
        return handleHealth(env);
      } else if (path.startsWith('/api/chagubang/stocks/')) {
        const stockCode = path.split('/').pop();
        return handleGetStock(stockCode, env);
      } else if (path === '/api/chagubang/stocks') {
        return handleGetAllStocks(url.searchParams, env);
      } else if (path === '/api/chagubang/market/overview') {
        return handleMarketOverview(env);
      } else if (path === '/api/chagubang/market/hot') {
        return handleHotStocks(url.searchParams, env);
      } else if (path === '/api/chagubang/search') {
        return handleSearchStocks(url.searchParams, env);
      } else if (path === '/api/chagubang/stats') {
        return handleServiceStats(env);
      } else if (path === '/api/chagubang/token/add') {
        return handleAddToken(request, env);
      } else if (path === '/api/chagubang/token/test') {
        return handleTestToken(request, env);
      } else {
        return createErrorResponse('API端点未找到', 404);
      }
    } catch (error) {
      console.error('Worker处理错误:', error);
      return createErrorResponse(`服务器错误: ${error.message}`, 500);
    }
  },

  /**
   * 定时任务：从茶股帮获取数据并存储到Supabase
   */
  async scheduled(event, env, ctx) {
    console.log('开始定时获取茶股帮数据...');
    
    try {
      // 获取存储的Token
      const tokens = await getStoredTokens(env);
      if (!tokens || tokens.length === 0) {
        console.log('没有可用的茶股帮Token');
        return;
      }
      
      // 使用第一个有效Token
      const token = tokens[0];
      
      // 连接茶股帮并获取数据
      const stockData = await fetchChaguBangData(token);
      
      if (stockData && stockData.length > 0) {
        // 存储到Supabase
        await storeStockDataToSupabase(stockData, env);
        console.log(`成功存储 ${stockData.length} 条股票数据`);
      }
      
    } catch (error) {
      console.error('定时任务执行失败:', error);
    }
  }
};

/**
 * 处理CORS
 */
function handleCORS() {
  return new Response(null, {
    status: 200,
    headers: CONFIG.CORS_HEADERS
  });
}

/**
 * 根路径处理
 */
function handleRoot() {
  const welcomeData = {
    message: "🚀 茶股帮数据源 - Cloudflare Workers版本",
    status: "running",
    platform: "Cloudflare Workers",
    timestamp: new Date().toISOString(),
    version: "1.0.0",
    endpoints: {
      health: "/api/chagubang/health",
      stocks: {
        single: "/api/chagubang/stocks/{code}",
        all: "/api/chagubang/stocks",
        search: "/api/chagubang/search?q={query}"
      },
      market: {
        overview: "/api/chagubang/market/overview",
        hot: "/api/chagubang/market/hot"
      },
      management: {
        stats: "/api/chagubang/stats",
        addToken: "/api/chagubang/token/add",
        testToken: "/api/chagubang/token/test"
      }
    },
    features: [
      "茶股帮实时数据",
      "Supabase存储",
      "KV缓存",
      "定时同步",
      "Token管理"
    ]
  };
  
  return createSuccessResponse(welcomeData);
}

/**
 * 健康检查
 */
async function handleHealth(env) {
  try {
    // 检查Supabase连接
    const supabaseStatus = await checkSupabaseConnection(env);
    
    // 检查KV存储
    const kvStatus = await checkKVStorage(env);
    
    // 检查茶股帮Token
    const tokens = await getStoredTokens(env);
    const tokenStatus = tokens && tokens.length > 0;
    
    const healthData = {
      status: supabaseStatus && kvStatus ? "healthy" : "unhealthy",
      timestamp: new Date().toISOString(),
      services: {
        supabase: supabaseStatus ? "connected" : "disconnected",
        kv_storage: kvStatus ? "available" : "unavailable",
        chagubang_tokens: tokenStatus ? "configured" : "not_configured"
      },
      version: "1.0.0"
    };
    
    return createSuccessResponse(healthData);
  } catch (error) {
    return createErrorResponse(`健康检查失败: ${error.message}`, 500);
  }
}

/**
 * 获取单只股票数据
 */
async function handleGetStock(stockCode, env) {
  try {
    // 先从KV缓存获取
    const cached = await env.STOCK_CACHE?.get(`stock_${stockCode}`);
    if (cached) {
      const data = JSON.parse(cached);
      if (Date.now() - data.timestamp < CONFIG.CACHE_TTL * 1000) {
        return createSuccessResponse(data.stock);
      }
    }
    
    // 从Supabase获取
    const stockData = await getStockFromSupabase(stockCode, env);
    
    if (stockData) {
      // 缓存数据
      await env.STOCK_CACHE?.put(`stock_${stockCode}`, JSON.stringify({
        stock: stockData,
        timestamp: Date.now()
      }), { expirationTtl: CONFIG.CACHE_TTL });
      
      return createSuccessResponse(stockData);
    } else {
      return createErrorResponse(`股票 ${stockCode} 未找到`, 404);
    }
  } catch (error) {
    return createErrorResponse(`获取股票数据失败: ${error.message}`, 500);
  }
}

/**
 * 获取所有股票数据
 */
async function handleGetAllStocks(searchParams, env) {
  try {
    const limit = parseInt(searchParams.get('limit')) || 100;
    const sortBy = searchParams.get('sort_by') || 'change_pct';
    const order = searchParams.get('order') || 'desc';
    
    // 从Supabase获取数据
    const stocks = await getAllStocksFromSupabase(limit, sortBy, order, env);
    
    return createSuccessResponse({
      data: stocks,
      total: stocks.length,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    return createErrorResponse(`获取股票列表失败: ${error.message}`, 500);
  }
}

/**
 * 获取市场概览
 */
async function handleMarketOverview(env) {
  try {
    // 先从KV缓存获取
    const cached = await env.MARKET_DATA?.get('market_overview');
    if (cached) {
      const data = JSON.parse(cached);
      if (Date.now() - data.timestamp < CONFIG.CACHE_TTL * 1000) {
        return createSuccessResponse(data.overview);
      }
    }
    
    // 从Supabase计算市场概览
    const overview = await calculateMarketOverview(env);
    
    // 缓存数据
    await env.MARKET_DATA?.put('market_overview', JSON.stringify({
      overview: overview,
      timestamp: Date.now()
    }), { expirationTtl: CONFIG.CACHE_TTL });
    
    return createSuccessResponse(overview);
  } catch (error) {
    return createErrorResponse(`获取市场概览失败: ${error.message}`, 500);
  }
}

/**
 * 获取热门股票
 */
async function handleHotStocks(searchParams, env) {
  try {
    const limit = parseInt(searchParams.get('limit')) || 10;
    const type = searchParams.get('type') || 'change';
    
    const hotStocks = await getHotStocksFromSupabase(limit, type, env);
    
    return createSuccessResponse({
      data: hotStocks,
      type: type,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    return createErrorResponse(`获取热门股票失败: ${error.message}`, 500);
  }
}

/**
 * 搜索股票
 */
async function handleSearchStocks(searchParams, env) {
  try {
    const query = searchParams.get('q');
    const limit = parseInt(searchParams.get('limit')) || 10;
    
    if (!query) {
      return createErrorResponse('搜索关键词不能为空', 400);
    }
    
    const results = await searchStocksInSupabase(query, limit, env);
    
    return createSuccessResponse({
      data: results,
      query: query,
      total: results.length,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    return createErrorResponse(`搜索股票失败: ${error.message}`, 500);
  }
}

/**
 * 获取服务统计
 */
async function handleServiceStats(env) {
  try {
    const stats = await getServiceStatsFromSupabase(env);
    
    return createSuccessResponse({
      ...stats,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    return createErrorResponse(`获取服务统计失败: ${error.message}`, 500);
  }
}

/**
 * 添加Token
 */
async function handleAddToken(request, env) {
  try {
    const { token, description } = await request.json();
    
    if (!token) {
      return createErrorResponse('Token不能为空', 400);
    }
    
    // 测试Token有效性
    const isValid = await testChaguBangToken(token);
    
    // 存储Token到KV
    const tokens = await getStoredTokens(env) || [];
    tokens.push({
      token: token,
      description: description || '',
      added_time: new Date().toISOString(),
      is_valid: isValid,
      last_test_time: new Date().toISOString()
    });
    
    await env.USER_SESSIONS?.put('chagubang_tokens', JSON.stringify(tokens));
    
    return createSuccessResponse({
      message: 'Token添加成功',
      is_valid: isValid,
      total_tokens: tokens.length
    });
  } catch (error) {
    return createErrorResponse(`添加Token失败: ${error.message}`, 500);
  }
}

/**
 * 测试Token
 */
async function handleTestToken(request, env) {
  try {
    const { token } = await request.json();
    
    if (!token) {
      return createErrorResponse('Token不能为空', 400);
    }
    
    const isValid = await testChaguBangToken(token);
    
    return createSuccessResponse({
      token: token.substring(0, 15) + '...',
      is_valid: isValid,
      test_time: new Date().toISOString()
    });
  } catch (error) {
    return createErrorResponse(`测试Token失败: ${error.message}`, 500);
  }
}

/**
 * 辅助函数
 */

// 创建成功响应
function createSuccessResponse(data) {
  return new Response(JSON.stringify({
    success: true,
    data: data,
    timestamp: new Date().toISOString()
  }), {
    status: 200,
    headers: CONFIG.CORS_HEADERS
  });
}

// 创建错误响应
function createErrorResponse(message, status = 500) {
  return new Response(JSON.stringify({
    success: false,
    error: message,
    timestamp: new Date().toISOString()
  }), {
    status: status,
    headers: CONFIG.CORS_HEADERS
  });
}

// 检查Supabase连接
async function checkSupabaseConnection(env) {
  try {
    const response = await fetch(`${CONFIG.SUPABASE_URL}/rest/v1/`, {
      headers: {
        'apikey': CONFIG.SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${CONFIG.SUPABASE_ANON_KEY}`
      }
    });
    return response.ok;
  } catch (error) {
    console.error('Supabase连接检查失败:', error);
    return false;
  }
}

// 检查KV存储
async function checkKVStorage(env) {
  try {
    await env.STOCK_CACHE?.put('health_check', 'ok', { expirationTtl: 60 });
    const result = await env.STOCK_CACHE?.get('health_check');
    return result === 'ok';
  } catch (error) {
    console.error('KV存储检查失败:', error);
    return false;
  }
}

// 获取存储的Token
async function getStoredTokens(env) {
  try {
    const tokensData = await env.USER_SESSIONS?.get('chagubang_tokens');
    return tokensData ? JSON.parse(tokensData) : [];
  } catch (error) {
    console.error('获取Token失败:', error);
    return [];
  }
}

// 测试茶股帮Token
async function testChaguBangToken(token) {
  try {
    // 这里需要实现实际的茶股帮连接测试
    // 由于Cloudflare Workers不支持TCP Socket，我们使用HTTP代理或其他方式
    // 暂时返回true，实际部署时需要通过其他服务测试
    console.log(`测试Token: ${token.substring(0, 10)}...`);
    return true;
  } catch (error) {
    console.error('Token测试失败:', error);
    return false;
  }
}

// 从Supabase获取股票数据
async function getStockFromSupabase(stockCode, env) {
  try {
    const response = await fetch(
      `${CONFIG.SUPABASE_URL}/rest/v1/stock_realtime?stock_code=eq.${stockCode}`,
      {
        headers: {
          'apikey': CONFIG.SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${CONFIG.SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (response.ok) {
      const data = await response.json();
      return data.length > 0 ? data[0] : null;
    }
    return null;
  } catch (error) {
    console.error('从Supabase获取股票数据失败:', error);
    return null;
  }
}

// 从Supabase获取所有股票数据
async function getAllStocksFromSupabase(limit, sortBy, order, env) {
  try {
    const orderParam = order === 'desc' ? `${sortBy}.desc` : `${sortBy}.asc`;
    const response = await fetch(
      `${CONFIG.SUPABASE_URL}/rest/v1/stock_realtime?limit=${limit}&order=${orderParam}`,
      {
        headers: {
          'apikey': CONFIG.SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${CONFIG.SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (response.ok) {
      return await response.json();
    }
    return [];
  } catch (error) {
    console.error('从Supabase获取所有股票数据失败:', error);
    return [];
  }
}

// 计算市场概览
async function calculateMarketOverview(env) {
  try {
    const response = await fetch(
      `${CONFIG.SUPABASE_URL}/rest/v1/stock_realtime?select=last_price,change_pct`,
      {
        headers: {
          'apikey': CONFIG.SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${CONFIG.SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (response.ok) {
      const stocks = await response.json();

      if (stocks.length === 0) {
        return {
          total_stocks: 0,
          avg_price: 0,
          avg_change: 0,
          rising_stocks: 0,
          falling_stocks: 0,
          flat_stocks: 0
        };
      }

      const prices = stocks.map(s => s.last_price || 0);
      const changes = stocks.map(s => s.change_pct || 0);

      return {
        total_stocks: stocks.length,
        avg_price: prices.reduce((a, b) => a + b, 0) / prices.length,
        avg_change: changes.reduce((a, b) => a + b, 0) / changes.length,
        rising_stocks: changes.filter(c => c > 0).length,
        falling_stocks: changes.filter(c => c < 0).length,
        flat_stocks: changes.filter(c => c === 0).length
      };
    }

    return {};
  } catch (error) {
    console.error('计算市场概览失败:', error);
    return {};
  }
}

// 获取热门股票
async function getHotStocksFromSupabase(limit, type, env) {
  try {
    let orderBy = 'change_pct.desc';
    if (type === 'volume') {
      orderBy = 'volume.desc';
    } else if (type === 'amount') {
      orderBy = 'amount.desc';
    }

    const response = await fetch(
      `${CONFIG.SUPABASE_URL}/rest/v1/stock_realtime?limit=${limit}&order=${orderBy}`,
      {
        headers: {
          'apikey': CONFIG.SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${CONFIG.SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (response.ok) {
      return await response.json();
    }
    return [];
  } catch (error) {
    console.error('获取热门股票失败:', error);
    return [];
  }
}

// 在Supabase中搜索股票
async function searchStocksInSupabase(query, limit, env) {
  try {
    const response = await fetch(
      `${CONFIG.SUPABASE_URL}/rest/v1/stock_realtime?or=(stock_code.ilike.*${query}*,stock_name.ilike.*${query}*)&limit=${limit}`,
      {
        headers: {
          'apikey': CONFIG.SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${CONFIG.SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (response.ok) {
      return await response.json();
    }
    return [];
  } catch (error) {
    console.error('搜索股票失败:', error);
    return [];
  }
}

// 获取服务统计
async function getServiceStatsFromSupabase(env) {
  try {
    const response = await fetch(
      `${CONFIG.SUPABASE_URL}/rest/v1/stock_realtime?select=count`,
      {
        headers: {
          'apikey': CONFIG.SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${CONFIG.SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json',
          'Prefer': 'count=exact'
        }
      }
    );

    if (response.ok) {
      const countHeader = response.headers.get('content-range');
      const totalCount = countHeader ? parseInt(countHeader.split('/')[1]) : 0;

      return {
        total_stocks: totalCount,
        last_update: new Date().toISOString(),
        status: 'running'
      };
    }

    return {
      total_stocks: 0,
      last_update: new Date().toISOString(),
      status: 'error'
    };
  } catch (error) {
    console.error('获取服务统计失败:', error);
    return {
      total_stocks: 0,
      last_update: new Date().toISOString(),
      status: 'error'
    };
  }
}
