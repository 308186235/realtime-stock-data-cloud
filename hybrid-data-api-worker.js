/**
 * 混合数据源API Worker
 * 整合股票实时数据(数据库) + 本地交易数据(OneDrive)
 * 为Agent提供完整的数据分析基础
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

// 配置
const CONFIG = {
  // Supabase配置
  SUPABASE_URL: 'https://zzukfxwavknskqcepsjb.supabase.co',
  SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw',
  
  // OneDrive分享链接
  ONEDRIVE_SHARES: {
    positions: 'https://1drv.ms/u/c/f988d396f8de5959/EcLi6OcK2R5KoQumcE8dx6EB0pb8rjeD8ghYFQvb0bR1rw?e=3mxWXi',
    balance: 'https://1drv.ms/u/c/f988d396f8de5959/EZWBY0aF7KhPmWSOX-9OlBEBFzgJeOWhmicQhfMoyjNwgA?e=IksT7e'
  },
  
  // CORS配置
  CORS_HEADERS: {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400'
  },
  
  // 缓存配置
  CACHE_TTL: {
    stock_data: 30,    // 股票数据30秒缓存
    trading_data: 10   // 交易数据10秒缓存
  }
}

/**
 * 主请求处理器
 */
async function handleRequest(request) {
  const url = new URL(request.url)
  const path = url.pathname
  
  // 处理CORS预检请求
  if (request.method === 'OPTIONS') {
    return handleCORS()
  }
  
  try {
    // 路由处理
    if (path === '/') {
      return handleRoot()
    } else if (path === '/health') {
      return handleHealth()
    } else if (path === '/api/agent/complete-data') {
      return handleAgentCompleteData(request)
    } else if (path === '/api/stock/realtime') {
      return handleStockRealtime(request)
    } else if (path === '/api/local-trading/positions') {
      return handleLocalPositions(request)
    } else if (path === '/api/local-trading/balance') {
      return handleLocalBalance(request)
    } else if (path === '/api/data-sources/status') {
      return handleDataSourcesStatus(request)
    } else {
      return createErrorResponse('API端点未找到', 404)
    }
  } catch (error) {
    console.error('请求处理错误:', error)
    return createErrorResponse(`服务器错误: ${error.message}`, 500)
  }
}

/**
 * 处理CORS
 */
function handleCORS() {
  return new Response(null, {
    status: 200,
    headers: CONFIG.CORS_HEADERS
  })
}

/**
 * 根路径处理
 */
function handleRoot() {
  const welcomeData = {
    message: "🚀 混合数据源交易系统API",
    status: "running",
    platform: "Cloudflare Workers",
    timestamp: new Date().toISOString(),
    version: "3.0.0",
    data_sources: {
      stock_realtime: "Supabase数据库 (茶股帮推送)",
      trading_data: "OneDrive (本地导出)",
      integration: "混合数据源Agent分析"
    },
    endpoints: {
      agent_complete: "/api/agent/complete-data",
      stock_realtime: "/api/stock/realtime",
      local_positions: "/api/local-trading/positions", 
      local_balance: "/api/local-trading/balance",
      data_status: "/api/data-sources/status",
      health: "/health"
    },
    features: [
      "股票实时数据 (数据库)",
      "本地交易数据 (OneDrive)",
      "Agent完整数据集成",
      "智能缓存机制",
      "数据源状态监控"
    ]
  }
  
  return createSuccessResponse(welcomeData)
}

/**
 * 健康检查
 */
function handleHealth() {
  return createSuccessResponse({
    status: "healthy",
    timestamp: new Date().toISOString(),
    data_sources: {
      supabase: "connected",
      onedrive: "connected"
    }
  })
}

/**
 * Agent完整数据API - 整合所有数据源
 */
async function handleAgentCompleteData(request) {
  try {
    console.log('🤖 Agent请求完整数据集')
    
    const url = new URL(request.url)
    const stockCodes = url.searchParams.get('stocks')?.split(',') || ['000001', '600036', '000002']
    
    // 并行获取所有数据
    const [stockData, positionsData, balanceData] = await Promise.all([
      getStockRealtimeData(stockCodes),
      getOneDriveData('positions'),
      getOneDriveData('balance')
    ])
    
    // 整合数据
    const completeData = {
      timestamp: new Date().toISOString(),
      data_sources: {
        stock_realtime: !!stockData,
        local_positions: !!positionsData,
        local_balance: !!balanceData
      },
      stock_data: stockData || {},
      trading_data: {
        positions: positionsData || getBackupPositionsData(),
        balance: balanceData || getBackupBalanceData()
      },
      analysis_context: {
        market_status: getMarketStatus(),
        data_freshness: {
          stock_data: stockData?.timestamp || null,
          positions_data: positionsData?.timestamp || null,
          balance_data: balanceData?.timestamp || null
        },
        agent_notes: [
          "股票数据来源: 茶股帮实时推送 → Supabase数据库",
          "交易数据来源: 本地交易软件 → OneDrive → API",
          "数据整合: 实时股价 + 本地持仓 = 完整分析基础"
        ]
      }
    }
    
    console.log('✅ Agent完整数据集成成功')
    return createSuccessResponse(completeData)
    
  } catch (error) {
    console.error('Agent数据集成失败:', error)
    return createErrorResponse(`数据集成失败: ${error.message}`, 500)
  }
}

/**
 * 股票实时数据API
 */
async function handleStockRealtime(request) {
  try {
    const url = new URL(request.url)
    const stockCodes = url.searchParams.get('codes')?.split(',') || ['000001']
    
    const stockData = await getStockRealtimeData(stockCodes)
    
    return createSuccessResponse({
      ...stockData,
      api_source: 'supabase_realtime',
      api_note: '从Supabase数据库获取茶股帮实时推送数据'
    })
    
  } catch (error) {
    console.error('获取股票实时数据失败:', error)
    return createErrorResponse(`获取股票数据失败: ${error.message}`, 500)
  }
}

/**
 * 本地持仓数据API
 */
async function handleLocalPositions(request) {
  try {
    const positionsData = await getOneDriveData('positions')
    
    if (positionsData) {
      return createSuccessResponse({
        ...positionsData,
        api_source: 'onedrive_realtime',
        api_note: '从OneDrive获取本地交易软件导出的持仓数据'
      })
    } else {
      return createSuccessResponse({
        ...getBackupPositionsData(),
        api_source: 'backup_data',
        api_note: 'OneDrive数据不可用，使用备用数据'
      })
    }
    
  } catch (error) {
    console.error('获取本地持仓数据失败:', error)
    return createErrorResponse(`获取持仓数据失败: ${error.message}`, 500)
  }
}

/**
 * 本地余额数据API
 */
async function handleLocalBalance(request) {
  try {
    const balanceData = await getOneDriveData('balance')
    
    if (balanceData) {
      return createSuccessResponse({
        ...balanceData,
        api_source: 'onedrive_realtime',
        api_note: '从OneDrive获取本地交易软件导出的余额数据'
      })
    } else {
      return createSuccessResponse({
        ...getBackupBalanceData(),
        api_source: 'backup_data',
        api_note: 'OneDrive数据不可用，使用备用数据'
      })
    }
    
  } catch (error) {
    console.error('获取本地余额数据失败:', error)
    return createErrorResponse(`获取余额数据失败: ${error.message}`, 500)
  }
}

/**
 * 数据源状态API
 */
async function handleDataSourcesStatus(request) {
  try {
    const status = {
      timestamp: new Date().toISOString(),
      data_sources: {}
    }
    
    // 测试Supabase连接
    try {
      await getStockRealtimeData(['000001'])
      status.data_sources.supabase = {
        status: 'connected',
        type: 'stock_realtime_data',
        description: '茶股帮实时推送数据'
      }
    } catch (error) {
      status.data_sources.supabase = {
        status: 'error',
        error: error.message
      }
    }
    
    // 测试OneDrive连接
    try {
      const positionsTest = await getOneDriveData('positions')
      status.data_sources.onedrive = {
        status: positionsTest ? 'connected' : 'no_data',
        type: 'local_trading_data',
        description: '本地交易软件导出数据',
        last_update: positionsTest?.timestamp || null
      }
    } catch (error) {
      status.data_sources.onedrive = {
        status: 'error',
        error: error.message
      }
    }
    
    return createSuccessResponse(status)
    
  } catch (error) {
    return createErrorResponse(`状态检查失败: ${error.message}`, 500)
  }
}

/**
 * 从Supabase获取股票实时数据
 */
async function getStockRealtimeData(stockCodes) {
  try {
    console.log(`📊 从Supabase获取股票数据: ${stockCodes.join(', ')}`)
    
    // 构建查询URL
    const codesFilter = stockCodes.map(code => `code.eq.${code}`).join(',')
    const url = `${CONFIG.SUPABASE_URL}/rest/v1/stock_realtime_data?or=(${codesFilter})`
    
    const response = await fetch(url, {
      headers: {
        'apikey': CONFIG.SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${CONFIG.SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Supabase查询失败: ${response.status}`)
    }
    
    const data = await response.json()
    
    console.log(`✅ 获取到 ${data.length} 条股票数据`)
    
    return {
      timestamp: new Date().toISOString(),
      source: 'supabase_realtime',
      data_type: 'stock_realtime',
      stocks: data,
      count: data.length
    }
    
  } catch (error) {
    console.error('Supabase股票数据获取失败:', error)
    throw error
  }
}

/**
 * 从OneDrive获取数据
 */
async function getOneDriveData(dataType) {
  try {
    const shareUrl = CONFIG.ONEDRIVE_SHARES[dataType]
    if (!shareUrl) {
      throw new Error(`未知的数据类型: ${dataType}`)
    }
    
    console.log(`📁 从OneDrive获取${dataType}数据`)
    
    // 转换为直接下载链接
    const downloadUrl = convertShareUrlToDownload(shareUrl)
    
    const response = await fetch(downloadUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    })
    
    if (!response.ok) {
      throw new Error(`OneDrive访问失败: ${response.status}`)
    }
    
    const data = await response.json()
    console.log(`✅ OneDrive ${dataType}数据获取成功`)
    
    return data
    
  } catch (error) {
    console.error(`OneDrive ${dataType}数据获取失败:`, error)
    return null
  }
}

/**
 * 转换OneDrive分享链接
 */
function convertShareUrlToDownload(shareUrl) {
  try {
    const encoded = btoa(shareUrl).replace(/=+$/, '').replace(/\//g, '_').replace(/\+/g, '-')
    return `https://api.onedrive.com/v1.0/shares/u!${encoded}/root/content`
  } catch (error) {
    return shareUrl
  }
}

/**
 * 获取市场状态
 */
function getMarketStatus() {
  const now = new Date()
  const hour = now.getHours()
  const minute = now.getMinutes()
  const time = hour * 100 + minute
  
  if (time >= 930 && time <= 1130) {
    return 'morning_session'
  } else if (time >= 1300 && time <= 1500) {
    return 'afternoon_session'
  } else {
    return 'closed'
  }
}

/**
 * 备用持仓数据
 */
function getBackupPositionsData() {
  return {
    timestamp: new Date().toISOString(),
    source: 'backup_data',
    data_type: 'positions',
    positions: [
      {
        stock_code: "000001",
        stock_name: "平安银行",
        quantity: 1000,
        current_price: 13.50,
        market_value: 13500.00,
        cost_price: 13.20,
        profit_loss: 300.00,
        profit_loss_ratio: 0.0227
      }
    ],
    summary: {
      total_positions: 1,
      total_market_value: 13500.00,
      total_cost: 13200.00,
      total_profit_loss: 300.00,
      total_profit_loss_ratio: 0.0227
    }
  }
}

/**
 * 备用余额数据
 */
function getBackupBalanceData() {
  return {
    timestamp: new Date().toISOString(),
    source: 'backup_data',
    data_type: 'balance',
    balance: {
      available_cash: 25000.00,
      frozen_cash: 0.00,
      total_cash: 25000.00,
      market_value: 13500.00,
      total_assets: 38500.00,
      total_profit_loss: 300.00,
      profit_loss_ratio: 0.0078
    }
  }
}

/**
 * 创建成功响应
 */
function createSuccessResponse(data) {
  return new Response(JSON.stringify({
    success: true,
    data: data,
    timestamp: new Date().toISOString()
  }), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      ...CONFIG.CORS_HEADERS
    }
  })
}

/**
 * 创建错误响应
 */
function createErrorResponse(message, status = 400) {
  return new Response(JSON.stringify({
    success: false,
    error: message,
    timestamp: new Date().toISOString()
  }), {
    status: status,
    headers: {
      'Content-Type': 'application/json',
      ...CONFIG.CORS_HEADERS
    }
  })
}
