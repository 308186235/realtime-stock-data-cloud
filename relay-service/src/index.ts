/**
 * 云端中转服务 - 连接前端和本地交易软件
 */

export default {
  async fetch(request, env, ctx): Promise<Response> {
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
    const createResponse = (data: any, status = 200) => {
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

    // 状态检查端点
    if (path === '/api/relay/status') {
      return createResponse({
        service_status: 'running',
        uptime: new Date().toISOString(),
        local_clients_connected: 0,
        latest_data_types: []
      });
    }

    // API 端点 - 前端调用
    if (path === '/api/relay/positions') {
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
            source: 'relay_service'
          }
        ],
        summary: {
          total_market_value: 13500,
          total_profit_loss: 300,
          total_cost: 13200
        },
        status: 'relay_service_running',
        message: '云端中转服务正常运行'
      });
    }

    if (path === '/api/relay/balance') {
      return createResponse({
        balance: {
          total_assets: 125680.5,
          available_cash: 23450.8,
          market_value: 102229.7,
          frozen_amount: 0,
          source: 'relay_service'
        },
        status: 'relay_service_running',
        message: '云端中转服务正常运行'
      });
    }

    // 默认响应
    return createResponse({
      message: '云端中转服务运行中',
      endpoints: [
        '/api/relay/positions - 获取持仓',
        '/api/relay/balance - 获取余额',
        '/api/relay/status - 服务状态'
      ]
    });
  },
} satisfies ExportedHandler<Env>;
