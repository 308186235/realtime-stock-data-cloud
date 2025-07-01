// Cloudflare Pages Functions - 数据同步处理器
export async function onRequest(context) {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  if (context.request.method === 'OPTIONS') {
    return new Response('', { headers: corsHeaders });
  }

  try {
    const action = new URL(context.request.url).searchParams.get('action') || 'sync';
    
    switch (action) {
      case 'sync':
        return await handleDataSync(context);
      case 'push':
        return await handlePushData(context);
      case 'monitor':
        return await handleHealthMonitor(context);
      default:
        return new Response(JSON.stringify({
          error: '不支持的操作',
          available_actions: ['sync', 'push', 'monitor']
        }), { status: 400, headers: corsHeaders });
    }
  } catch (error) {
    console.error('Data Sync Error:', error);
    return new Response(JSON.stringify({
      error: '数据同步服务错误',
      message: error.message
    }), { status: 500, headers: corsHeaders });
  }
}

// 处理数据同步
async function handleDataSync(context) {
  const supabaseUrl = 'https://zzukfxwavknskqcepsjb.supabase.co';
  const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw';
  
  try {
    // 获取实时股票数据
    const stockResponse = await fetch('https://realtime-stock-api.pages.dev/api/quotes?symbols=sz000001,sh600519,sz300750,sh688599,sz002415');
    const stockData = await stockResponse.json();
    
    if (!stockData.success) {
      throw new Error('获取股票数据失败');
    }
    
    const syncResults = [];
    
    // 同步每只股票数据到数据库
    for (const stock of stockData.data) {
      try {
        const dbData = {
          symbol: stock.stock_code,
          stock_name: stock.stock_name,
          current_price: stock.current_price,
          yesterday_close: stock.yesterday_close,
          today_open: stock.today_open,
          high_price: stock.high_price,
          low_price: stock.low_price,
          volume: stock.volume,
          amount: stock.amount,
          turnover_rate: stock.turnover_rate,
          pe_ratio: stock.pe_ratio,
          pb_ratio: stock.pb_ratio,
          market_cap: stock.market_cap,
          change_amount: stock.change,
          change_percent: stock.change_percent,
          bid_price_1: stock.bid_price_1,
          bid_price_2: stock.bid_price_2,
          bid_price_3: stock.bid_price_3,
          bid_price_4: stock.bid_price_4,
          bid_price_5: stock.bid_price_5,
          ask_price_1: stock.ask_price_1,
          ask_price_2: stock.ask_price_2,
          ask_price_3: stock.ask_price_3,
          ask_price_4: stock.ask_price_4,
          ask_price_5: stock.ask_price_5,
          bid_volume_1: stock.bid_volume_1,
          bid_volume_2: stock.bid_volume_2,
          bid_volume_3: stock.bid_volume_3,
          bid_volume_4: stock.bid_volume_4,
          bid_volume_5: stock.bid_volume_5,
          ask_volume_1: stock.ask_volume_1,
          ask_volume_2: stock.ask_volume_2,
          ask_volume_3: stock.ask_volume_3,
          ask_volume_4: stock.ask_volume_4,
          ask_volume_5: stock.ask_volume_5,
          amplitude: stock.amplitude,
          volume_ratio: stock.volume_ratio,
          limit_up: stock.limit_up,
          limit_down: stock.limit_down,
          data_source: stock.data_source,
          data_quality_score: stock.data_quality_score,
          market_status: stock.data_status,
          trading_date: stock.data_timestamp ? new Date(stock.data_timestamp).toISOString().split('T')[0] : null,
          data_timestamp: stock.data_timestamp,
          updated_at: new Date().toISOString()
        };
        
        // 插入或更新数据库
        const response = await fetch(`${supabaseUrl}/rest/v1/real_time_stock_data`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${supabaseKey}`,
            'apikey': supabaseKey,
            'Prefer': 'resolution=merge-duplicates'
          },
          body: JSON.stringify(dbData)
        });
        
        if (response.ok) {
          syncResults.push({
            symbol: stock.stock_code,
            status: 'success',
            message: '数据同步成功'
          });
        } else {
          const error = await response.text();
          syncResults.push({
            symbol: stock.stock_code,
            status: 'error',
            message: `数据库写入失败: ${error}`
          });
        }
        
      } catch (error) {
        syncResults.push({
          symbol: stock.stock_code,
          status: 'error',
          message: error.message
        });
      }
    }
    
    // 记录数据质量监控
    await recordDataQuality(supabaseUrl, supabaseKey, stockData.data_quality);
    
    return new Response(JSON.stringify({
      success: true,
      message: '数据同步完成',
      sync_results: syncResults,
      total_processed: stockData.data.length,
      successful: syncResults.filter(r => r.status === 'success').length,
      failed: syncResults.filter(r => r.status === 'error').length,
      data_quality: stockData.data_quality,
      timestamp: new Date().toISOString()
    }), {
      headers: {
        ...corsHeaders,
        'Cache-Control': 'no-cache'
      }
    });
    
  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: '数据同步失败',
      message: error.message,
      timestamp: new Date().toISOString()
    }), {
      status: 500,
      headers: corsHeaders
    });
  }
}

// 处理推送数据接收
async function handlePushData(context) {
  if (context.request.method !== 'POST') {
    return new Response(JSON.stringify({
      error: '仅支持POST请求'
    }), { status: 405, headers: corsHeaders });
  }
  
  try {
    const pushData = await context.request.json();
    const supabaseUrl = 'https://zzukfxwavknskqcepsjb.supabase.co';
    const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw';
    
    // 记录推送日志
    const logData = {
      symbol: pushData.symbol,
      price: pushData.price,
      volume: pushData.volume,
      push_timestamp: new Date(pushData.timestamp * 1000).toISOString(),
      api_key_used: pushData.api_key_used || 'unknown',
      batch_id: pushData.batch_id || null,
      processed: false
    };
    
    const response = await fetch(`${supabaseUrl}/rest/v1/stock_push_logs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${supabaseKey}`,
        'apikey': supabaseKey
      },
      body: JSON.stringify(logData)
    });
    
    if (response.ok) {
      return new Response(JSON.stringify({
        success: true,
        message: '推送数据已记录',
        data: logData
      }), { headers: corsHeaders });
    } else {
      throw new Error('数据库写入失败');
    }
    
  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: '推送数据处理失败',
      message: error.message
    }), { status: 500, headers: corsHeaders });
  }
}

// 记录数据质量监控
async function recordDataQuality(supabaseUrl, supabaseKey, qualityData) {
  try {
    const monitorData = {
      check_type: 'api_data_quality',
      check_result: qualityData,
      issues_found: qualityData.total_warnings || 0,
      critical_issues: qualityData.critical_issues?.length || 0,
      overall_score: qualityData.overall_score || 0,
      recommendations: qualityData.recommendations || []
    };
    
    await fetch(`${supabaseUrl}/rest/v1/data_quality_monitor`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${supabaseKey}`,
        'apikey': supabaseKey
      },
      body: JSON.stringify(monitorData)
    });
  } catch (error) {
    console.error('记录数据质量监控失败:', error);
  }
}

// 处理系统健康监控
async function handleHealthMonitor(context) {
  const supabaseUrl = 'https://zzukfxwavknskqcepsjb.supabase.co';
  const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw';
  
  const healthChecks = [];
  
  // 检查API健康状态
  try {
    const apiResponse = await fetch('https://realtime-stock-api.pages.dev/api/health');
    const apiHealth = await apiResponse.json();
    healthChecks.push({
      component: 'stock_api',
      status: apiResponse.ok ? 'healthy' : 'unhealthy',
      metrics: apiHealth,
      error_count: 0
    });
  } catch (error) {
    healthChecks.push({
      component: 'stock_api',
      status: 'error',
      metrics: {},
      error_count: 1,
      last_error: error.message
    });
  }
  
  // 检查数据库连接
  try {
    const dbResponse = await fetch(`${supabaseUrl}/rest/v1/stocks?select=count&apikey=${supabaseKey}`);
    healthChecks.push({
      component: 'database',
      status: dbResponse.ok ? 'healthy' : 'unhealthy',
      metrics: { response_time: Date.now() },
      error_count: 0
    });
  } catch (error) {
    healthChecks.push({
      component: 'database',
      status: 'error',
      metrics: {},
      error_count: 1,
      last_error: error.message
    });
  }
  
  // 记录健康监控数据
  for (const check of healthChecks) {
    try {
      await fetch(`${supabaseUrl}/rest/v1/system_health_monitor`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${supabaseKey}`,
          'apikey': supabaseKey
        },
        body: JSON.stringify(check)
      });
    } catch (error) {
      console.error('记录健康监控失败:', error);
    }
  }
  
  return new Response(JSON.stringify({
    success: true,
    health_status: healthChecks,
    overall_status: healthChecks.every(c => c.status === 'healthy') ? 'healthy' : 'degraded',
    timestamp: new Date().toISOString()
  }), { headers: corsHeaders });
}
