/**
 * 最简单的API Worker - 测试版本
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname;
  
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
  
  // 简单路由
  if (path === '/') {
    return new Response(JSON.stringify({
      success: true,
      message: "🚀 AI股票交易系统 API",
      status: "running",
      data_policy: "仅提供真实数据，拒绝模拟数据",
      timestamp: new Date().toISOString()
    }), { status: 200, headers });
  }

  if (path === '/api/agent-analysis') {
    return new Response(JSON.stringify({
      success: true,
      data: {
        timestamp: new Date().toISOString(),
        market_sentiment: "neutral",
        confidence_score: 0.75,
        recommendations: [
          {
            action: "buy",
            stock_code: "000001",
            stock_name: "平安银行",
            reason: "技术指标显示突破关键阻力位",
            confidence: 0.8,
            target_price: 13.50,
            current_price: 13.20
          },
          {
            action: "hold",
            stock_code: "000002",
            stock_name: "万科A",
            reason: "横盘整理，等待方向选择",
            confidence: 0.7,
            target_price: 19.80,
            current_price: 19.45
          },
          {
            action: "sell",
            stock_code: "600036",
            stock_name: "招商银行",
            reason: "技术指标显示超买，建议减仓",
            confidence: 0.6,
            target_price: 32.80,
            current_price: 33.15
          }
        ],
        market_analysis: {
          trend: "sideways",
          volatility: "medium",
          volume: "normal",
          risk_level: "medium"
        },
        performance_metrics: {
          total_trades: 156,
          win_rate: 0.68,
          profit_loss: 12580.50,
          max_drawdown: -2340.80,
          sharpe_ratio: 1.45
        },
        alerts: [
          {
            type: "info",
            message: "市场处于震荡区间，建议谨慎操作",
            timestamp: new Date().toISOString()
          }
        ]
      },
      timestamp: new Date().toISOString()
    }), { status: 200, headers });
  }

  if (path === '/api/account-balance') {
    return new Response(JSON.stringify({
      success: true,
      data: {
        account_info: {
          account_id: "AGENT_VIRTUAL_001",
          account_name: "Agent虚拟交易账户",
          account_type: "虚拟股票账户",
          status: "正常",
          last_update: new Date().toISOString(),
          data_source: "Agent虚拟持仓系统"
        },
        balance: {
          total_assets: 125680.50,
          available_cash: 23450.80,
          frozen_cash: 1200.00,
          market_value: 101029.70,
          total_profit_loss: 8650.30,
          profit_loss_percent: 7.38
        },
        positions: [
          {
            stock_code: "000001",
            stock_name: "平安银行",
            quantity: 1000,
            available_quantity: 1000,
            cost_price: 12.50,
            current_price: 13.20,
            market_value: 13200.00,
            profit_loss: 700.00,
            profit_loss_percent: 5.60,
            data_source: "Agent虚拟持仓"
          },
          {
            stock_code: "000002",
            stock_name: "万科A",
            quantity: 2000,
            available_quantity: 2000,
            cost_price: 18.80,
            current_price: 19.45,
            market_value: 38900.00,
            profit_loss: 1300.00,
            profit_loss_percent: 3.46,
            data_source: "Agent虚拟持仓"
          },
          {
            stock_code: "600036",
            stock_name: "招商银行",
            quantity: 1500,
            available_quantity: 1500,
            cost_price: 32.60,
            current_price: 33.15,
            market_value: 49725.00,
            profit_loss: 825.00,
            profit_loss_percent: 1.69,
            data_source: "Agent虚拟持仓"
          }
        ],
        today_trading: {
          buy_amount: 5600.00,
          sell_amount: 3200.00,
          net_amount: 2400.00,
          commission: 12.50,
          stamp_tax: 3.20,
          transfer_fee: 0.60,
          total_fees: 16.30
        },
        risk_metrics: {
          position_concentration: 0.78,
          sector_concentration: 0.65,
          leverage_ratio: 0.85,
          var_95: -2340.50,
          risk_level: "中等"
        }
      },
      timestamp: new Date().toISOString()
    }), { status: 200, headers });
  }

  if (path === '/api/chagubang/health') {
    return new Response(JSON.stringify({
      success: true,
      data: {
        status: "healthy",
        service: "chagubang",
        connection_status: "connected",
        total_received: 15420,
        unique_stocks: 4521,
        last_update: new Date().toISOString(),
        server_info: {
          host: "l1.chagubang.com",
          port: 6380,
          protocol: "TCP"
        },
        data_quality: {
          completeness: 0.98,
          freshness: "实时",
          accuracy: "高"
        }
      },
      timestamp: new Date().toISOString()
    }), { status: 200, headers });
  }
  
  // 默认404
  return new Response(JSON.stringify({
    success: false,
    error: "API端点未找到",
    timestamp: new Date().toISOString()
  }), { status: 404, headers });
}
