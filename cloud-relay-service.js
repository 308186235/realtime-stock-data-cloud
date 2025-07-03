/**
 * 云端中转服务 - 连接前端和本地交易软件
 * 部署到 Cloudflare Workers
 */

// 存储本地客户端连接和数据
let localClients = new Map();
let latestData = new Map();

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // CORS 处理
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 200,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
      });
    }

    // 创建响应函数
    const createResponse = (data, status = 200) => {
      return new Response(JSON.stringify({
        success: status < 400,
        data: data,
        timestamp: new Date().toISOString(),
        path: path
      }), {
        status,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        },
      });
    };

    // WebSocket 升级处理 (本地客户端连接)
    if (path === '/ws/local-client') {
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
      
      console.log(`本地客户端连接: ${clientId}`);

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
          
        } catch (error) {
          console.error('处理本地消息失败:', error);
        }
      });

      server.addEventListener('close', () => {
        console.log(`本地客户端断开: ${clientId}`);
        localClients.delete(clientId);
      });

      return new Response(null, {
        status: 101,
        webSocket: client,
      });
    }

    // API 端点 - 前端调用
    if (path === '/api/relay/positions') {
      try {
        console.log('前端请求持仓信息');
        
        // 检查是否有本地客户端连接
        if (localClients.size === 0) {
          return createResponse({
            positions: [],
            summary: { total_market_value: 0 },
            status: 'no_local_connection',
            message: '本地交易软件未连接到云端中转服务'
          });
        }

        // 向本地客户端请求最新数据
        const requestId = 'req_' + Date.now();
        const request_message = {
          id: requestId,
          type: 'get_positions',
          timestamp: new Date().toISOString()
        };

        // 发送请求到所有连接的本地客户端
        for (const [clientId, ws] of localClients) {
          if (ws.readyState === 1) { // WebSocket.OPEN
            ws.send(JSON.stringify(request_message));
          }
        }

        // 等待响应或使用缓存数据
        const cachedPositions = latestData.get('positions');
        if (cachedPositions) {
          return createResponse({
            ...cachedPositions.data,
            source: 'local_computer_via_relay',
            last_update: cachedPositions.timestamp,
            relay_note: '通过云端中转服务获取本地数据'
          });
        } else {
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
                source: 'relay_backup'
              }
            ],
            summary: {
              total_market_value: 13500,
              total_profit_loss: 300,
              total_cost: 13200
            },
            status: 'waiting_for_local_data',
            message: '等待本地交易软件响应，使用备用数据'
          });
        }
      } catch (error) {
        return createResponse({ error: '中转服务错误: ' + error.message }, 500);
      }
    }

    if (path === '/api/relay/balance') {
      try {
        console.log('前端请求账户余额');
        
        if (localClients.size === 0) {
          return createResponse({
            balance: { total_assets: 0, available_cash: 0 },
            status: 'no_local_connection',
            message: '本地交易软件未连接到云端中转服务'
          });
        }

        // 向本地客户端请求余额数据
        const requestId = 'req_' + Date.now();
        const request_message = {
          id: requestId,
          type: 'get_balance',
          timestamp: new Date().toISOString()
        };

        for (const [clientId, ws] of localClients) {
          if (ws.readyState === 1) {
            ws.send(JSON.stringify(request_message));
          }
        }

        // 使用缓存数据或备用数据
        const cachedBalance = latestData.get('balance');
        if (cachedBalance) {
          return createResponse({
            ...cachedBalance.data,
            source: 'local_computer_via_relay',
            last_update: cachedBalance.timestamp,
            relay_note: '通过云端中转服务获取本地数据'
          });
        } else {
          return createResponse({
            balance: {
              total_assets: 125680.5,
              available_cash: 23450.8,
              market_value: 102229.7,
              frozen_amount: 0,
              source: 'relay_backup'
            },
            status: 'waiting_for_local_data',
            message: '等待本地交易软件响应，使用备用数据'
          });
        }
      } catch (error) {
        return createResponse({ error: '中转服务错误: ' + error.message }, 500);
      }
    }

    // 交易执行端点
    if (path === '/api/relay/buy' && request.method === 'POST') {
      try {
        const body = await request.json();
        console.log('前端请求买入:', body);
        
        if (localClients.size === 0) {
          return createResponse({
            success: false,
            message: '本地交易软件未连接，无法执行买入'
          }, 400);
        }

        // 向本地客户端发送买入指令
        const requestId = 'buy_' + Date.now();
        const trade_message = {
          id: requestId,
          type: 'execute_buy',
          data: body,
          timestamp: new Date().toISOString()
        };

        for (const [clientId, ws] of localClients) {
          if (ws.readyState === 1) {
            ws.send(JSON.stringify(trade_message));
          }
        }

        return createResponse({
          order_id: requestId,
          status: 'sent_to_local',
          message: '买入指令已发送到本地交易软件',
          details: body,
          relay_note: '通过云端中转服务执行交易'
        });
      } catch (error) {
        return createResponse({ error: '交易中转失败: ' + error.message }, 500);
      }
    }

    // 状态检查端点
    if (path === '/api/relay/status') {
      return createResponse({
        local_clients_connected: localClients.size,
        latest_data_types: Array.from(latestData.keys()),
        service_status: 'running',
        uptime: new Date().toISOString()
      });
    }

    // 默认响应
    return createResponse({ 
      message: '云端中转服务运行中',
      endpoints: [
        '/ws/local-client - WebSocket连接 (本地客户端)',
        '/api/relay/positions - 获取持仓',
        '/api/relay/balance - 获取余额', 
        '/api/relay/buy - 执行买入',
        '/api/relay/status - 服务状态'
      ]
    });
  },
};
