/**
 * OneDrive集成的Cloudflare Worker
 * 直接从OneDrive读取本地导出的交易数据
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

// 配置
const CONFIG = {
  // OneDrive Graph API配置
  GRAPH_API_BASE: 'https://graph.microsoft.com/v1.0',
  
  // CORS配置
  CORS_HEADERS: {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400'
  },
  
  // 缓存配置
  CACHE_TTL: 30, // 30秒缓存
  
  // OneDrive文件路径
  ONEDRIVE_PATHS: {
    positions: '/TradingData/latest_positions.json',
    balance: '/TradingData/latest_balance.json'
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
    } else if (path === '/api/local-trading/positions') {
      return handlePositionsAPI(request)
    } else if (path === '/api/local-trading/balance') {
      return handleBalanceAPI(request)
    } else if (path === '/api/onedrive/test') {
      return handleOneDriveTest(request)
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
    message: "🚀 OneDrive交易数据API",
    status: "running",
    platform: "Cloudflare Workers",
    timestamp: new Date().toISOString(),
    version: "2.0.0",
    data_source: "OneDrive (rclone挂载)",
    endpoints: {
      positions: "/api/local-trading/positions",
      balance: "/api/local-trading/balance",
      test: "/api/onedrive/test",
      health: "/health"
    },
    features: [
      "OneDrive实时数据读取",
      "Microsoft Graph API集成", 
      "智能缓存机制",
      "CORS支持",
      "错误处理"
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
    uptime: "running",
    data_source: "OneDrive"
  })
}

/**
 * 处理持仓数据API
 */
async function handlePositionsAPI(request) {
  try {
    console.log('📊 获取OneDrive持仓数据')
    
    // 尝试从OneDrive获取数据
    const oneDriveData = await getOneDriveFile('positions', request)
    
    if (oneDriveData) {
      console.log('✅ 成功从OneDrive获取持仓数据')
      return createSuccessResponse({
        ...oneDriveData,
        api_source: 'onedrive_realtime',
        api_note: '从OneDrive实时读取的本地导出数据',
        api_timestamp: new Date().toISOString()
      })
    }
    
    // 如果OneDrive数据不可用，返回备用数据
    console.log('⚠️ OneDrive数据不可用，使用备用数据')
    return createSuccessResponse(getBackupPositionsData())
    
  } catch (error) {
    console.error('获取持仓数据失败:', error)
    return createErrorResponse(`获取持仓数据失败: ${error.message}`, 500)
  }
}

/**
 * 处理余额数据API
 */
async function handleBalanceAPI(request) {
  try {
    console.log('💰 获取OneDrive余额数据')
    
    // 尝试从OneDrive获取数据
    const oneDriveData = await getOneDriveFile('balance', request)
    
    if (oneDriveData) {
      console.log('✅ 成功从OneDrive获取余额数据')
      return createSuccessResponse({
        ...oneDriveData,
        api_source: 'onedrive_realtime',
        api_note: '从OneDrive实时读取的本地导出数据',
        api_timestamp: new Date().toISOString()
      })
    }
    
    // 如果OneDrive数据不可用，返回备用数据
    console.log('⚠️ OneDrive数据不可用，使用备用数据')
    return createSuccessResponse(getBackupBalanceData())
    
  } catch (error) {
    console.error('获取余额数据失败:', error)
    return createErrorResponse(`获取余额数据失败: ${error.message}`, 500)
  }
}

/**
 * OneDrive测试API
 */
async function handleOneDriveTest(request) {
  try {
    const testResults = {
      timestamp: new Date().toISOString(),
      tests: {}
    }
    
    // 测试持仓数据
    try {
      const positionsData = await getOneDriveFile('positions', request)
      testResults.tests.positions = {
        success: !!positionsData,
        data_available: !!positionsData,
        timestamp: positionsData?.timestamp || null,
        test_id: positionsData?.test_id || null
      }
    } catch (error) {
      testResults.tests.positions = {
        success: false,
        error: error.message
      }
    }
    
    // 测试余额数据
    try {
      const balanceData = await getOneDriveFile('balance', request)
      testResults.tests.balance = {
        success: !!balanceData,
        data_available: !!balanceData,
        timestamp: balanceData?.timestamp || null,
        test_id: balanceData?.test_id || null
      }
    } catch (error) {
      testResults.tests.balance = {
        success: false,
        error: error.message
      }
    }
    
    return createSuccessResponse(testResults)
    
  } catch (error) {
    return createErrorResponse(`测试失败: ${error.message}`, 500)
  }
}

/**
 * 从OneDrive获取文件数据
 */
async function getOneDriveFile(dataType, request) {
  try {
    // 方案1: 通过公共分享链接访问 (临时方案)
    const shareUrls = {
      positions: 'https://1drv.ms/u/c/f988d396f8de5959/EcLi6OcK2R5KoQumcE8dx6EB0pb8rjeD8ghYFQvb0bR1rw?e=3mxWXi',
      balance: 'https://1drv.ms/u/c/f988d396f8de5959/EZWBY0aF7KhPmWSOX-9OlBEBFzgJeOWhmicQhfMoyjNwgA?e=IksT7e'
    }
    
    const shareUrl = shareUrls[dataType]
    if (!shareUrl) {
      throw new Error(`未知的数据类型: ${dataType}`)
    }
    
    console.log(`🔍 从OneDrive分享链接获取${dataType}数据: ${shareUrl}`)
    
    // 转换分享链接为直接下载链接
    const downloadUrl = convertShareUrlToDownload(shareUrl)
    
    // 获取数据
    const response = await fetch(downloadUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    })
    
    if (!response.ok) {
      throw new Error(`OneDrive访问失败: ${response.status} ${response.statusText}`)
    }
    
    const data = await response.json()
    console.log(`✅ 成功获取${dataType}数据，大小: ${JSON.stringify(data).length} 字符`)
    
    return data
    
  } catch (error) {
    console.error(`从OneDrive获取${dataType}数据失败:`, error)
    throw error
  }
}

/**
 * 转换OneDrive分享链接为直接下载链接
 */
function convertShareUrlToDownload(shareUrl) {
  try {
    // 提取分享ID
    const url = new URL(shareUrl)
    const pathParts = url.pathname.split('/')
    const shareId = pathParts[pathParts.length - 1]
    
    // 构建直接下载链接
    const downloadUrl = `https://api.onedrive.com/v1.0/shares/u!${btoa(shareUrl).replace(/=+$/, '').replace(/\//g, '_').replace(/\+/g, '-')}/root/content`
    
    return downloadUrl
    
  } catch (error) {
    console.error('转换分享链接失败:', error)
    // 如果转换失败，尝试使用原链接
    return shareUrl
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
    api_note: 'OneDrive数据不可用，使用备用数据',
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
    api_note: 'OneDrive数据不可用，使用备用数据',
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
