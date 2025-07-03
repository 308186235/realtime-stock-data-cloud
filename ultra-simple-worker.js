/**
 * 超级简单的测试Worker - 支持WebSocket和Supabase
 */

// 存储本地客户端连接
let localClients = new Map();
let latestData = new Map();

// Supabase配置
const SUPABASE_CONFIG = {
  url: 'https://zzukfxwavknskqcepsjb.supabase.co',
  anon_key: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw',
  service_key: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTI5ODUwNiwiZXhwIjoyMDY2ODc0NTA2fQ.Ksy_A6qfaUn9qBethAw4o8Xpn0iSxluaBTCxbnd3u5g'
};

// 简化的本地数据获取函数 - 移除OneDrive复杂逻辑
async function getLocalData(dataType, env) {
  try {
    console.log(`🔍 尝试获取本地${dataType}数据`);

    // 直接从Supabase获取数据作为主要数据源
    const supabaseData = await getSupabaseData(dataType, env);
    if (supabaseData) {
      console.log(`✅ 从Supabase获取到${dataType}数据`);
      return supabaseData;
    }

    console.log(`⚠️ 无法获取${dataType}数据，使用备用数据`);
    return null;
  } catch (error) {
    console.error(`❌ 获取${dataType}数据失败:`, error);
    return null;
  }
}





// Supabase数据获取函数（备用）
async function getSupabaseData(dataType) {
  try {
    const response = await fetch(`${SUPABASE_CONFIG.url}/rest/v1/trading_data`, {
      method: 'GET',
      headers: {
        'apikey': SUPABASE_CONFIG.service_key,
        'Authorization': `Bearer ${SUPABASE_CONFIG.service_key}`,
        'Content-Type': 'application/json'
      },
      body: null,
      cf: {
        cacheTtl: 10 // 10秒缓存
      }
    });

    if (response.ok) {
      const data = await response.json();
      // 查找最新的指定类型数据
      const latestRecord = data
        .filter(record => record.data_type === dataType)
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))[0];

      if (latestRecord) {
        console.log(`✅ 从Supabase获取到${dataType}数据`);
        return latestRecord.data;
      }
    }

    console.log(`⚠️ Supabase中没有找到${dataType}数据`);
    return null;
  } catch (error) {
    console.error(`❌ 从Supabase获取${dataType}数据失败:`, error);
    return null;
  }
}

// 将OneDrive分享链接转换为直接下载链接
function convertToDownloadUrl(shareUrl) {
  // 这是一个简化的转换，实际可能需要更复杂的处理
  if (shareUrl.includes('1drv.ms')) {
    // 对于1drv.ms链接，需要特殊处理
    return shareUrl.replace('1drv.ms', 'onedrive.live.com/download');
  }
  return shareUrl;
}

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request, event.env));
});

async function handleRequest(request, env) {
  const url = new URL(request.url);
  const path = url.pathname;

  // WebSocket 升级处理 (本地交易软件连接)
  if (path === '/ws/local-trading') {
    const upgradeHeader = request.headers.get('Upgrade');
    if (upgradeHeader !== 'websocket') {
      return new Response('Expected Upgrade: websocket', { status: 426 });
    }

    const webSocketPair = new WebSocketPair();
    const [client, server] = Object.values(webSocketPair);

    // 处理本地客户端连接
    server.accept();

    const clientId = 'local_' + Date.now();
    localClients.set(clientId, server);

    console.log(`本地交易软件连接: ${clientId}`);

    server.addEventListener('message', event => {
      try {
        const message = JSON.parse(event.data);
        console.log('收到本地数据:', message.type);

        // 存储最新数据
        latestData.set(message.type, {
          data: message.data,
          timestamp: new Date().toISOString(),
          clientId: clientId
        });

        // 发送确认
        server.send(JSON.stringify({
          type: 'ack',
          message: '数据已收到',
          timestamp: new Date().toISOString()
        }));

      } catch (error) {
        console.error('处理本地消息失败:', error);
      }
    });

    server.addEventListener('close', () => {
      console.log(`本地交易软件断开: ${clientId}`);
      localClients.delete(clientId);
    });

    return new Response(null, {
      status: 101,
      webSocket: client,
    });
  }
  
  // CORS头
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };
  
  // 处理OPTIONS请求
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 200, headers });
  }
  
  // 创建成功响应
  function createResponse(data, status = 200) {
    return new Response(JSON.stringify({
      success: true,
      data: data,
      path: path,
      timestamp: new Date().toISOString()
    }), { status, headers });
  }
  
  // 简单路由 - 所有路径都返回成功
  if (path === '/') {
    return createResponse({
      message: "🚀 AI股票交易系统 API - 新版本已部署！",
      status: "running",
      version: "ULTRA_SIMPLE_V2",
      deployment_time: "2025-07-02 22:30"
    });
  }
  
  if (path === '/health' || path === '/api/health') {
    return createResponse({
      status: "healthy",
      version: "1.0.0"
    });
  }
  
  if (path === '/api/agent-analysis' || path === '/api/agent/analysis') {
    return createResponse({
      success: false,
      error: "❌ 拒绝返回模拟数据！系统要求使用真实数据源",
      message: "Agent推荐功能需要真实股票数据和分析",
      required_actions: [
        "1. 配置淘宝股票数据推送服务",
        "2. 连接茶股帮实时数据源",
        "3. 配置真实的AI分析算法"
      ],
      timestamp: new Date().toISOString()
    });
  }
  
  if (path === '/api/account-balance' || path === '/api/account/balance') {
    return createResponse({
      balance: {
        total_assets: 125680.50,
        available_cash: 23450.80
      }
    });
  }
  
  if (path === '/api/account-positions' || path === '/api/account/positions') {
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
    });
  }

  // 本地交易API - 获取持仓数据
  if (path === '/api/local-trading/positions') {
    try {
      console.log('云端Agent: 获取本地持仓数据');

      // 尝试从Supabase获取数据
      const supabaseData = await getSupabaseData('positions');

      if (supabaseData) {
        console.log('✅ 成功从Supabase获取持仓数据');
        return createResponse({
          ...supabaseData,
          source: 'local_computer_via_supabase',
          database_note: '通过Supabase数据库获取本地真实数据',
          connected_clients: localClients.size
        });
      }

      // 如果Supabase没有数据，检查WebSocket缓存
      const cachedPositions = latestData.get('positions');
      if (cachedPositions) {
        console.log('使用WebSocket缓存的持仓数据');
        return createResponse({
          ...cachedPositions.data,
          source: 'local_computer_via_websocket',
          last_update: cachedPositions.timestamp,
          websocket_note: '通过WebSocket获取本地数据',
          connected_clients: localClients.size
        });
      }

      // 最后使用备用数据
      console.log('使用备用持仓数据');
      return createResponse({
        positions: [
          {
            stock_code: '000001',
            stock_name: '平安银行',
            quantity: 1000,
            available_quantity: 1000,
            cost_price: 13.20,
            current_price: 13.50,
            market_value: 13500,
            profit_loss: 300,
            profit_loss_ratio: 2.27,
            source: 'backup_data'
          }
        ],
        summary: {
          total_market_value: 13500,
          total_profit_loss: 300,
          total_cost: 13200
        },
        connection_status: 'using_backup_data',
        message: '本地数据不可用，使用备用数据',
        connected_clients: localClients.size
      });

    } catch (error) {
      console.error('云端Agent数据获取失败:', error);

      return createResponse({
        positions: [
          {
            stock_code: '000001',
            stock_name: '平安银行',
            quantity: 1000,
            available_quantity: 1000,
            cost_price: 13.20,
            current_price: 13.50,
            market_value: 13500,
            profit_loss: 300,
            profit_loss_ratio: 2.27,
            source: 'backup_data'
          }
        ],
        summary: {
          total_market_value: 13500,
          total_profit_loss: 300,
          total_cost: 13200
        },
        error: '数据获取失败，使用备用数据: ' + error.message
      });
    }
  }

  if (path === '/api/local-trading/balance') {
    try {
      console.log('云端Agent: 获取本地余额数据');

      // 尝试从Supabase获取数据
      const supabaseData = await getSupabaseData('balance');

      if (supabaseData) {
        console.log('✅ 成功从Supabase获取余额数据');
        return createResponse({
          ...supabaseData,
          source: 'local_computer_via_supabase',
          database_note: '通过Supabase数据库获取本地真实数据',
          connected_clients: localClients.size
        });
      }

      // 如果Supabase没有数据，检查WebSocket缓存
      const cachedBalance = latestData.get('balance');
      if (cachedBalance) {
        console.log('使用WebSocket缓存的余额数据');
        return createResponse({
          ...cachedBalance.data,
          source: 'local_computer_via_websocket',
          last_update: cachedBalance.timestamp,
          websocket_note: '通过WebSocket获取本地数据',
          connected_clients: localClients.size
        });
      }

      // 最后使用备用数据
      console.log('使用备用余额数据');
      return createResponse({
        balance: {
          total_assets: 125680.5,
          available_cash: 23450.8,
          market_value: 102229.7,
          frozen_amount: 0,
          source: 'backup_data'
        },
        connection_status: 'using_backup_data',
        message: '本地数据不可用，使用备用数据',
        connected_clients: localClients.size
      });

    } catch (error) {
      console.error('云端Agent数据获取失败:', error);

      return createResponse({
        balance: {
          total_assets: 125680.5,
          available_cash: 23450.8,
          market_value: 102229.7,
          frozen_amount: 0,
          source: 'backup_data'
        },
        error: '数据获取失败，使用备用数据: ' + error.message
      });
    }
  }

  if (path === '/api/local-trading/buy' && request.method === 'POST') {
    // 云端Agent调用本地交易软件执行买入
    try {
      const body = await request.json();
      console.log('云端Agent: 调用本地交易软件执行买入', body);

      // 调用本地交易软件API (端口8888)
      const localResponse = await fetch('http://localhost:8888/trade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'CloudAgent/1.0'
        },
        body: JSON.stringify({
          action: 'buy',
          stock_code: body.code,
          quantity: body.quantity,
          price: body.price
        })
      });

      if (localResponse.ok) {
        const localData = await localResponse.json();
        console.log('云端Agent: 成功执行本地买入操作');

        return createResponse({
          ...localData,
          source: 'local_computer',
          agent_note: '云端Agent成功调用本地交易软件执行买入'
        });
      } else {
        throw new Error(`本地API响应错误: ${localResponse.status}`);
      }
    } catch (error) {
      console.error('云端Agent调用本地交易软件失败:', error);
      return createResponse({
        error: '云端Agent调用本地交易软件执行买入失败: ' + error.message,
        success: false
      }, 500);
    }
  }

  if (path === '/api/local-trading/sell' && request.method === 'POST') {
    // 云端Agent调用本地交易软件执行卖出
    try {
      const body = await request.json();
      console.log('云端Agent: 调用本地交易软件执行卖出', body);

      // 调用本地交易软件API (端口8888)
      const localResponse = await fetch('http://localhost:8888/trade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'CloudAgent/1.0'
        },
        body: JSON.stringify({
          action: 'sell',
          stock_code: body.code,
          quantity: body.quantity,
          price: body.price
        })
      });

      if (localResponse.ok) {
        const localData = await localResponse.json();
        console.log('云端Agent: 成功执行本地卖出操作');

        return createResponse({
          ...localData,
          source: 'local_computer',
          agent_note: '云端Agent成功调用本地交易软件执行卖出'
        });
      } else {
        throw new Error(`本地API响应错误: ${localResponse.status}`);
      }
    } catch (error) {
      console.error('云端Agent调用本地交易软件失败:', error);
      return createResponse({
        error: '云端Agent调用本地交易软件执行卖出失败: ' + error.message,
        success: false
      }, 500);
    }
  }

  if (path === '/api/market-data') {
    return createResponse({
      market_status: "open",
      indices: {
        shanghai: { value: 3245.67 }
      }
    });
  }
  
  if (path === '/api/agent/status') {
    return createResponse({
      status: "active",
      version: "1.0.0"
    });
  }
  
  if (path === '/api/market/status') {
    return createResponse({
      status: "open",
      trading_day: true
    });
  }
  
  if (path.startsWith('/api/trading/')) {
    if (request.method === 'POST') {
      return createResponse({
        order_id: `ORDER_${Date.now()}`,
        status: "submitted",
        message: "订单已提交"
      });
    }
  }

  // 券商列表功能已删除

  if (path === '/api/realtime/quotes' || path === '/api/stock/quotes') {
    return createResponse({
      success: false,
      error: "❌ 拒绝返回模拟数据！系统要求使用真实数据源",
      message: "实时行情数据需要从茶股帮或淘宝股票数据推送服务获取",
      required_actions: [
        "1. 连接茶股帮实时数据源 (l1.chagubang.com:6380)",
        "2. 配置淘宝股票数据推送服务 (QT_wat5QfcJ6N9pDZM5)",
        "3. 或配置其他真实股票数据API"
      ],
      data_sources_needed: {
        chagubang_realtime: "未配置",
        taobao_stock_api: "未配置",
        real_stock_data_api: "未配置"
      },
      timestamp: new Date().toISOString()
    });
  }

  // WebSocket状态检查
  if (path === '/api/websocket/status') {
    return createResponse({
      websocket_status: 'enabled',
      local_clients_connected: localClients.size,
      latest_data_types: Array.from(latestData.keys()),
      websocket_endpoint: '/ws/local-trading',
      last_data_update: latestData.size > 0 ?
        Math.max(...Array.from(latestData.values()).map(d => new Date(d.timestamp).getTime())) : null
    });
  }



  if (path === '/ws' || path === '/agent-client') {
    // WebSocket升级请求
    return new Response("WebSocket endpoint", {
      status: 101,
      headers: {
        'Upgrade': 'websocket',
        'Connection': 'Upgrade'
      }
    });
  }

  // 默认响应 - 显示请求的路径
  return createResponse({
    message: "云端Agent API运行中 - 支持WebSocket",
    requested_path: path,
    method: request.method,
    websocket_info: {
      local_clients_connected: localClients.size,
      latest_data_available: Array.from(latestData.keys()),
      websocket_endpoint: '/ws/local-trading'
    },
    available_endpoints: [
      "/",
      "/health",
      "/api/agent-analysis",
      "/api/account-balance",
      "/api/local-trading/positions - 本地持仓",
      "/api/local-trading/balance - 本地余额",
      "/api/local-trading/buy - 本地买入",
      "/api/local-trading/sell - 本地卖出",
      "/ws/local-trading - WebSocket连接端点",
      "/api/websocket/status - WebSocket状态",
      "/api/realtime/quotes"
    ]
  });
}
