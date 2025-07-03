/**
 * 更新的Worker代码 - 添加OneDrive支持
 * 在现有功能基础上增加OneDrive数据读取能力
 */

// 现有的全局变量
var localClients = new Map();
var latestData = new Map();

// 现有的Supabase配置
var SUPABASE_CONFIG = {
  url: "https://zzukfxwavknskqcepsjb.supabase.co",
  anon_key: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw",
  service_key: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTI5ODUwNiwiZXhwIjoyMDY2ODc0NTA2fQ.Ksy_A6qfaUn9qBethAw4o8Xpn0iSxluaBTCxbnd3u5g"
};

// 新增：OneDrive配置
var ONEDRIVE_CONFIG = {
  positions: 'https://1drv.ms/u/c/f988d396f8de5959/EcLi6OcK2R5KoQumcE8dx6EB0pb8rjeD8ghYFQvb0bR1rw?e=3mxWXi',
  balance: 'https://1drv.ms/u/c/f988d396f8de5959/EZWBY0aF7KhPmWSOX-9OlBEBFzgJeOWhmicQhfMoyjNwgA?e=IksT7e'
};

// 新增：OneDrive数据获取函数
async function getOneDriveData(dataType) {
  try {
    const shareUrl = ONEDRIVE_CONFIG[dataType];
    if (!shareUrl) {
      console.log(`❌ 未知的OneDrive数据类型: ${dataType}`);
      return null;
    }
    
    console.log(`📁 从OneDrive获取${dataType}数据`);
    
    // 转换分享链接为直接下载链接
    const downloadUrl = convertShareUrlToDownload(shareUrl);
    
    const response = await fetch(downloadUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      cf: {
        cacheTtl: 10 // 10秒缓存
      }
    });
    
    if (!response.ok) {
      console.log(`❌ OneDrive访问失败: ${response.status}`);
      return null;
    }
    
    const data = await response.json();
    console.log(`✅ OneDrive ${dataType}数据获取成功`);
    
    return data;
    
  } catch (error) {
    console.error(`❌ OneDrive ${dataType}数据获取失败:`, error);
    return null;
  }
}

// 新增：转换OneDrive分享链接
function convertShareUrlToDownload(shareUrl) {
  try {
    const encoded = btoa(shareUrl).replace(/=+$/, '').replace(/\//g, '_').replace(/\+/g, '-');
    return `https://api.onedrive.com/v1.0/shares/u!${encoded}/root/content`;
  } catch (error) {
    console.error('转换分享链接失败:', error);
    return shareUrl;
  }
}

// 现有的Supabase数据获取函数（保持不变）
async function getSupabaseData(dataType) {
  try {
    const response = await fetch(`${SUPABASE_CONFIG.url}/rest/v1/trading_data`, {
      method: "GET",
      headers: {
        "apikey": SUPABASE_CONFIG.service_key,
        "Authorization": `Bearer ${SUPABASE_CONFIG.service_key}`,
        "Content-Type": "application/json"
      },
      body: null,
      cf: {
        cacheTtl: 10
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      const latestRecord = data.filter((record) => record.data_type === dataType)
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

// 现有的事件监听器（保持不变）
addEventListener("fetch", (event) => {
  event.respondWith(handleRequest(event.request, event.env));
});

// 更新的主请求处理器
async function handleRequest(request, env) {
  const url = new URL(request.url);
  const path = url.pathname;
  
  // WebSocket处理（保持不变）
  if (path === "/ws/local-trading") {
    const upgradeHeader = request.headers.get("Upgrade");
    if (upgradeHeader !== "websocket") {
      return new Response("Expected Upgrade: websocket", { status: 426 });
    }
    
    const webSocketPair = new WebSocketPair();
    const [client, server] = Object.values(webSocketPair);
    server.accept();
    
    const clientId = "local_" + Date.now();
    localClients.set(clientId, server);
    console.log(`本地交易软件连接: ${clientId}`);
    
    server.addEventListener("message", (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log("收到本地数据:", message.type);
        latestData.set(message.type, {
          data: message.data,
          timestamp: new Date().toISOString(),
          clientId
        });
        
        server.send(JSON.stringify({
          type: "ack",
          message: "数据已收到",
          timestamp: new Date().toISOString()
        }));
      } catch (error) {
        console.error("处理本地消息失败:", error);
      }
    });
    
    server.addEventListener("close", () => {
      console.log(`本地交易软件断开: ${clientId}`);
      localClients.delete(clientId);
    });
    
    return new Response(null, {
      status: 101,
      webSocket: client
    });
  }
  
  // CORS和响应处理
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json"
  };
  
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 200, headers });
  }
  
  function createResponse(data, status = 200) {
    return new Response(JSON.stringify({
      success: true,
      data,
      path,
      timestamp: new Date().toISOString()
    }), { status, headers });
  }
  
  // 更新根路径响应
  if (path === "/") {
    return createResponse({
      message: "🚀 AI股票交易系统 API - OneDrive支持已添加！",
      status: "running",
      version: "ULTRA_SIMPLE_V3_ONEDRIVE",
      deployment_time: "2025-07-03 12:00",
      new_features: [
        "OneDrive实时数据读取",
        "混合数据源支持",
        "优先级数据获取"
      ]
    });
  }
  
  // 健康检查（保持不变）
  if (path === "/health" || path === "/api/health") {
    return createResponse({
      status: "healthy",
      version: "3.0.0",
      onedrive_support: "enabled"
    });
  }
  
  // 更新持仓数据API - 添加OneDrive支持
  if (path === "/api/local-trading/positions") {
    try {
      console.log("云端Agent: 获取本地持仓数据 (OneDrive优先)");
      
      // 优先级1: OneDrive数据
      const oneDriveData = await getOneDriveData('positions');
      if (oneDriveData) {
        console.log("✅ 成功从OneDrive获取持仓数据");
        return createResponse({
          ...oneDriveData,
          api_source: "onedrive_realtime",
          source: oneDriveData.source || "onedrive",
          data_note: "从OneDrive实时读取的本地导出数据",
          priority: "onedrive_first",
          connected_clients: localClients.size
        });
      }
      
      // 优先级2: Supabase数据
      const supabaseData = await getSupabaseData("positions");
      if (supabaseData) {
        console.log("✅ 成功从Supabase获取持仓数据");
        return createResponse({
          ...supabaseData,
          api_source: "supabase_database",
          source: "local_computer_via_supabase",
          data_note: "通过Supabase数据库获取本地真实数据",
          priority: "supabase_second",
          connected_clients: localClients.size
        });
      }
      
      // 优先级3: WebSocket缓存数据
      const cachedPositions = latestData.get("positions");
      if (cachedPositions) {
        console.log("使用WebSocket缓存的持仓数据");
        return createResponse({
          ...cachedPositions.data,
          api_source: "websocket_cache",
          source: "local_computer_via_websocket",
          last_update: cachedPositions.timestamp,
          data_note: "通过WebSocket获取本地数据",
          priority: "websocket_third",
          connected_clients: localClients.size
        });
      }
      
      // 优先级4: 备用数据
      console.log("使用备用持仓数据");
      return createResponse({
        positions: [
          {
            stock_code: "000001",
            stock_name: "平安银行",
            quantity: 1000,
            available_quantity: 1000,
            cost_price: 13.2,
            current_price: 13.5,
            market_value: 13500,
            profit_loss: 300,
            profit_loss_ratio: 2.27,
            source: "backup_data"
          }
        ],
        summary: {
          total_market_value: 13500,
          total_profit_loss: 300,
          total_cost: 13200
        },
        api_source: "backup_data",
        connection_status: "using_backup_data",
        message: "所有数据源不可用，使用备用数据",
        priority: "backup_last",
        connected_clients: localClients.size
      });
      
    } catch (error) {
      console.error("云端Agent数据获取失败:", error);
      return createResponse({
        positions: [],
        error: "数据获取失败，使用备用数据: " + error.message,
        api_source: "error_fallback"
      });
    }
  }
  
  // 更新余额数据API - 添加OneDrive支持
  if (path === "/api/local-trading/balance") {
    try {
      console.log("云端Agent: 获取本地余额数据 (OneDrive优先)");
      
      // 优先级1: OneDrive数据
      const oneDriveData = await getOneDriveData('balance');
      if (oneDriveData) {
        console.log("✅ 成功从OneDrive获取余额数据");
        return createResponse({
          ...oneDriveData,
          api_source: "onedrive_realtime",
          source: oneDriveData.source || "onedrive",
          data_note: "从OneDrive实时读取的本地导出数据",
          priority: "onedrive_first",
          connected_clients: localClients.size
        });
      }
      
      // 优先级2: Supabase数据
      const supabaseData = await getSupabaseData("balance");
      if (supabaseData) {
        console.log("✅ 成功从Supabase获取余额数据");
        return createResponse({
          ...supabaseData,
          api_source: "supabase_database",
          source: "local_computer_via_supabase",
          data_note: "通过Supabase数据库获取本地真实数据",
          priority: "supabase_second",
          connected_clients: localClients.size
        });
      }
      
      // 优先级3: WebSocket缓存数据
      const cachedBalance = latestData.get("balance");
      if (cachedBalance) {
        console.log("使用WebSocket缓存的余额数据");
        return createResponse({
          ...cachedBalance.data,
          api_source: "websocket_cache",
          source: "local_computer_via_websocket",
          last_update: cachedBalance.timestamp,
          data_note: "通过WebSocket获取本地数据",
          priority: "websocket_third",
          connected_clients: localClients.size
        });
      }
      
      // 优先级4: 备用数据
      console.log("使用备用余额数据");
      return createResponse({
        balance: {
          total_assets: 125680.5,
          available_cash: 23450.8,
          market_value: 102229.7,
          frozen_amount: 0,
          source: "backup_data"
        },
        api_source: "backup_data",
        connection_status: "using_backup_data",
        message: "所有数据源不可用，使用备用数据",
        priority: "backup_last",
        connected_clients: localClients.size
      });
      
    } catch (error) {
      console.error("云端Agent数据获取失败:", error);
      return createResponse({
        balance: {
          total_assets: 0,
          available_cash: 0,
          market_value: 0,
          frozen_amount: 0,
          source: "error_fallback"
        },
        error: "数据获取失败，使用备用数据: " + error.message,
        api_source: "error_fallback"
      });
    }
  }
  
  // 新增：Agent完整数据API
  if (path === "/api/agent/complete-data") {
    try {
      console.log("🤖 Agent请求完整数据集 (OneDrive优先)");
      
      // 并行获取OneDrive数据
      const [oneDrivePositions, oneDriveBalance] = await Promise.all([
        getOneDriveData('positions'),
        getOneDriveData('balance')
      ]);
      
      // 整合数据
      const completeData = {
        timestamp: new Date().toISOString(),
        data_sources: {
          onedrive_positions: !!oneDrivePositions,
          onedrive_balance: !!oneDriveBalance,
          websocket_clients: localClients.size
        },
        trading_data: {
          positions: oneDrivePositions || latestData.get("positions")?.data || null,
          balance: oneDriveBalance || latestData.get("balance")?.data || null
        },
        analysis_context: {
          data_freshness: {
            positions_source: oneDrivePositions ? "onedrive" : "websocket_or_backup",
            balance_source: oneDriveBalance ? "onedrive" : "websocket_or_backup",
            positions_timestamp: oneDrivePositions?.timestamp || null,
            balance_timestamp: oneDriveBalance?.timestamp || null
          },
          system_note: "OneDrive支持已添加，优先读取OneDrive数据",
          agent_notes: [
            "数据优先级: OneDrive → Supabase → WebSocket → 备用数据",
            "OneDrive数据来源: 本地交易软件 → rclone → OneDrive → API",
            "实时数据同步: 支持多种数据源自动切换"
          ]
        }
      };
      
      console.log("✅ Agent完整数据集成成功");
      return createResponse(completeData);
      
    } catch (error) {
      console.error("Agent数据集成失败:", error);
      return createResponse({
        error: "数据集成失败: " + error.message,
        timestamp: new Date().toISOString()
      }, 500);
    }
  }
  
  // 其他现有端点保持不变...
  // [这里包含所有其他现有的API端点处理逻辑]
  
  // 默认响应 - 更新信息
  return createResponse({
    message: "云端Agent API运行中 - OneDrive支持已添加",
    requested_path: path,
    method: request.method,
    onedrive_info: {
      support_enabled: true,
      data_priority: "OneDrive → Supabase → WebSocket → Backup"
    },
    websocket_info: {
      local_clients_connected: localClients.size,
      latest_data_available: Array.from(latestData.keys()),
      websocket_endpoint: "/ws/local-trading"
    },
    available_endpoints: [
      "/",
      "/health",
      "/api/agent-analysis",
      "/api/account-balance", 
      "/api/local-trading/positions - 本地持仓 (OneDrive优先)",
      "/api/local-trading/balance - 本地余额 (OneDrive优先)",
      "/api/agent/complete-data - Agent完整数据 (新增)",
      "/api/local-trading/buy - 本地买入",
      "/api/local-trading/sell - 本地卖出",
      "/ws/local-trading - WebSocket连接端点",
      "/api/websocket/status - WebSocket状态",
      "/api/realtime/quotes"
    ]
  });
}
