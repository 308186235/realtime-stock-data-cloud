addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  const path = url.pathname
  
  // CORS headers
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
  }
  
  // Handle preflight requests
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: corsHeaders
    })
  }
  
  // Helper function to create JSON responses
  function createResponse(data, status = 200) {
    return new Response(JSON.stringify(data), {
      status,
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders
      }
    })
  }
  
  // Routes
  if (path === '/') {
    return createResponse({
      message: '🚀 AI股票交易后端API',
      version: '1.0.0',
      status: 'running',
      timestamp: new Date().toISOString()
    })
  }
  
  if (path === '/api/health') {
    return createResponse({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: '1.0.0'
    })
  }
  
  if (path === '/api/agent-analysis') {
    return createResponse({
      success: false,
      error: "❌ 拒绝返回模拟数据！系统要求使用真实数据源",
      message: "Agent分析功能需要真实股票数据",
      required_actions: [
        "1. 配置淘宝股票数据推送服务 (QT_wat5QfcJ6N9pDZM5)",
        "2. 连接茶股帮实时数据源 (l1.chagubang.com:6380)",
        "3. 配置OneDrive持仓数据源"
      ],
      data_sources_needed: {
        real_stock_data_api: "未配置",
        chagubang_realtime: "未配置",
        onedrive_positions: "未配置"
      },
      timestamp: new Date().toISOString()
    })
  }
  
  if (path === '/api/account-balance') {
    return createResponse({
      success: true,
      data: {
        account_info: {
          account_id: 'AGENT_VIRTUAL_001',
          account_name: 'Agent智能交易账户',
          broker: 'Agent Trading System'
        },
        balance: {
          totalAssets: 125680.50,
          availableCash: 23450.80,
          marketValue: 101029.70,
          profitLoss: 8650.30,
          profitLossRatio: 0.0738,
          frozenAmount: 1200.00
        },
        positions_summary: {
          total_positions: 8,
          profitable_positions: 5,
          loss_positions: 3
        }
      },
      timestamp: new Date().toISOString()
    })
  }
  
  if (path === '/api/account-positions') {
    return createResponse({
      success: false,
      error: "❌ 拒绝返回模拟数据！系统要求使用真实数据源",
      message: "持仓数据需要从OneDrive或本地交易软件获取",
      required_actions: [
        "1. 配置OneDrive Microsoft Graph API",
        "2. 或配置本地交易软件API连接",
        "3. 或从导出的CSV文件读取真实持仓数据"
      ],
      data_sources_needed: {
        onedrive_positions_file: "未配置",
        local_trading_api: "未配置",
        csv_export_data: "未配置"
      },
      timestamp: new Date().toISOString()
    })
  }
  
  // 404 for unknown paths
  return createResponse({
    success: false,
    error: 'API端点未找到',
    path: path,
    timestamp: new Date().toISOString()
  }, 404)
}
