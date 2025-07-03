/**
 * 简单测试Worker
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400',
    };
    
    // Handle preflight requests
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 200,
        headers: corsHeaders
      });
    }
    
    // Create response helper
    function createResponse(data, status = 200) {
      return new Response(JSON.stringify(data), {
        status,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }
    
    // Routes
    if (path === '/') {
      return createResponse({
        message: '🚀 AI股票交易后端API',
        version: '1.0.0',
        status: 'running',
        timestamp: new Date().toISOString()
      });
    }
    
    if (path === '/api/health') {
      return createResponse({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '1.0.0'
      });
    }
    
    if (path === '/api/agent-analysis') {
      return createResponse({
        success: true,
        data: [
          {
            name: '平安银行',
            code: '000001',
            price: '13.20',
            change: '+2.27%',
            trend: 'up',
            recommendation: 'buy',
            confidence: 0.75
          },
          {
            name: '万科A',
            code: '000002',
            price: '8.45',
            change: '-1.15%',
            trend: 'down',
            recommendation: 'hold',
            confidence: 0.60
          }
        ],
        timestamp: new Date().toISOString()
      });
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
          }
        },
        timestamp: new Date().toISOString()
      });
    }
    
    if (path === '/api/account-positions') {
      return createResponse({
        success: true,
        data: [
          {
            code: '000001',
            name: '平安银行',
            quantity: 1000,
            cost_price: 12.50,
            current_price: 13.20,
            market_value: 13200.00,
            profit_loss: 700.00,
            profit_loss_ratio: 0.056
          }
        ],
        timestamp: new Date().toISOString()
      });
    }
    
    // 404 for unknown paths
    return createResponse({
      success: false,
      error: 'API端点未找到',
      timestamp: new Date().toISOString()
    }, 404);
}
