// Cloudflare Pages Functions - 数据监控仪表板
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

  const url = new URL(context.request.url);
  const action = url.searchParams.get('action') || 'overview';

  try {
    switch (action) {
      case 'overview':
        return await getSystemOverview(context);
      case 'stocks':
        return await getStockData(context);
      case 'quality':
        return await getDataQuality(context);
      case 'health':
        return await getSystemHealth(context);
      case 'logs':
        return await getPushLogs(context);
      default:
        return new Response(JSON.stringify({
          error: '不支持的操作',
          available_actions: ['overview', 'stocks', 'quality', 'health', 'logs']
        }), { status: 400, headers: corsHeaders });
    }
  } catch (error) {
    console.error('Dashboard Error:', error);
    return new Response(JSON.stringify({
      error: '仪表板服务错误',
      message: error.message
    }), { status: 500, headers: corsHeaders });
  }
}

// 获取系统概览
async function getSystemOverview(context) {
  const supabaseUrl = 'https://zzukfxwavknskqcepsjb.supabase.co';
  const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw';
  
  try {
    const headers = {
      'Authorization': `Bearer ${supabaseKey}`,
      'apikey': supabaseKey
    };

    // 并行获取各种统计数据
    const [stocksRes, pushLogsRes, realTimeRes, qualityRes] = await Promise.all([
      fetch(`${supabaseUrl}/rest/v1/stocks?select=count`, { headers }),
      fetch(`${supabaseUrl}/rest/v1/stock_push_logs?select=count`, { headers }),
      fetch(`${supabaseUrl}/rest/v1/real_time_stock_data?select=count`, { headers }),
      fetch(`${supabaseUrl}/rest/v1/data_quality_monitor?select=*&order=created_at.desc&limit=1`, { headers })
    ]);

    const stocksCount = stocksRes.ok ? (await stocksRes.json()).length : 0;
    const pushLogsCount = pushLogsRes.ok ? (await pushLogsRes.json()).length : 0;
    const realTimeCount = realTimeRes.ok ? (await realTimeRes.json()).length : 0;
    const latestQuality = qualityRes.ok ? await qualityRes.json() : [];

    // 获取API健康状态
    let apiStatus = 'unknown';
    try {
      const apiRes = await fetch('https://realtime-stock-api.pages.dev/api/health');
      apiStatus = apiRes.ok ? 'healthy' : 'unhealthy';
    } catch {
      apiStatus = 'error';
    }

    const overview = {
      system_status: {
        api_status: apiStatus,
        database_status: stocksRes.ok ? 'healthy' : 'error',
        last_update: new Date().toISOString()
      },
      data_statistics: {
        total_stocks: stocksCount,
        push_logs_count: pushLogsCount,
        real_time_records: realTimeCount,
        data_quality_score: latestQuality[0]?.overall_score || 0
      },
      recent_activity: {
        last_quality_check: latestQuality[0]?.created_at || null,
        quality_issues: latestQuality[0]?.issues_found || 0,
        critical_issues: latestQuality[0]?.critical_issues || 0
      }
    };

    return new Response(JSON.stringify({
      success: true,
      data: overview,
      timestamp: new Date().toISOString()
    }), { headers: corsHeaders });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: '获取系统概览失败',
      message: error.message
    }), { status: 500, headers: corsHeaders });
  }
}

// 获取股票数据
async function getStockData(context) {
  const supabaseUrl = 'https://zzukfxwavknskqcepsjb.supabase.co';
  const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw';
  
  try {
    const headers = {
      'Authorization': `Bearer ${supabaseKey}`,
      'apikey': supabaseKey
    };

    // 获取股票基础信息
    const stocksRes = await fetch(`${supabaseUrl}/rest/v1/stocks?select=*&order=created_at.desc`, { headers });
    const stocks = stocksRes.ok ? await stocksRes.json() : [];

    // 获取最新实时数据
    const realTimeRes = await fetch(`${supabaseUrl}/rest/v1/real_time_stock_data?select=*&order=updated_at.desc&limit=20`, { headers });
    const realTimeData = realTimeRes.ok ? await realTimeRes.json() : [];

    // 获取推送统计
    const pushStatsRes = await fetch(`${supabaseUrl}/rest/v1/stock_push_logs?select=symbol,count&group=symbol&order=count.desc&limit=10`, { headers });
    const pushStats = pushStatsRes.ok ? await pushStatsRes.json() : [];

    return new Response(JSON.stringify({
      success: true,
      data: {
        stocks: stocks,
        real_time_data: realTimeData,
        push_statistics: pushStats,
        summary: {
          total_stocks: stocks.length,
          active_stocks: stocks.filter(s => s.is_active).length,
          markets: [...new Set(stocks.map(s => s.market))],
          sectors: [...new Set(stocks.map(s => s.sector))]
        }
      },
      timestamp: new Date().toISOString()
    }), { headers: corsHeaders });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: '获取股票数据失败',
      message: error.message
    }), { status: 500, headers: corsHeaders });
  }
}

// 获取数据质量信息
async function getDataQuality(context) {
  const supabaseUrl = 'https://zzukfxwavknskqcepsjb.supabase.co';
  const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw';
  
  try {
    const headers = {
      'Authorization': `Bearer ${supabaseKey}`,
      'apikey': supabaseKey
    };

    // 获取最近的数据质量检查
    const qualityRes = await fetch(`${supabaseUrl}/rest/v1/data_quality_monitor?select=*&order=created_at.desc&limit=10`, { headers });
    const qualityData = qualityRes.ok ? await qualityRes.json() : [];

    // 计算质量趋势
    const qualityTrend = qualityData.map(q => ({
      timestamp: q.created_at,
      score: q.overall_score,
      issues: q.issues_found,
      critical: q.critical_issues
    }));

    // 获取当前API数据质量
    let currentQuality = null;
    try {
      const apiRes = await fetch('https://realtime-stock-api.pages.dev/api/quotes?symbols=sz000001');
      if (apiRes.ok) {
        const apiData = await apiRes.json();
        currentQuality = apiData.data_quality;
      }
    } catch (error) {
      console.error('获取当前API质量失败:', error);
    }

    return new Response(JSON.stringify({
      success: true,
      data: {
        current_quality: currentQuality,
        quality_history: qualityData,
        quality_trend: qualityTrend,
        summary: {
          latest_score: qualityData[0]?.overall_score || 0,
          average_score: qualityData.length > 0 ? 
            Math.round(qualityData.reduce((sum, q) => sum + q.overall_score, 0) / qualityData.length) : 0,
          total_checks: qualityData.length,
          issues_trend: qualityTrend.slice(0, 5).map(t => t.issues)
        }
      },
      timestamp: new Date().toISOString()
    }), { headers: corsHeaders });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: '获取数据质量信息失败',
      message: error.message
    }), { status: 500, headers: corsHeaders });
  }
}

// 获取系统健康状态
async function getSystemHealth(context) {
  const supabaseUrl = 'https://zzukfxwavknskqcepsjb.supabase.co';
  const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw';
  
  try {
    const headers = {
      'Authorization': `Bearer ${supabaseKey}`,
      'apikey': supabaseKey
    };

    // 获取系统健康监控数据
    const healthRes = await fetch(`${supabaseUrl}/rest/v1/system_health_monitor?select=*&order=created_at.desc&limit=20`, { headers });
    const healthData = healthRes.ok ? await healthRes.json() : [];

    // 实时健康检查
    const healthChecks = [];
    
    // 检查API
    try {
      const apiRes = await fetch('https://realtime-stock-api.pages.dev/api/health');
      healthChecks.push({
        component: 'stock_api',
        status: apiRes.ok ? 'healthy' : 'unhealthy',
        response_time: Date.now(),
        last_check: new Date().toISOString()
      });
    } catch (error) {
      healthChecks.push({
        component: 'stock_api',
        status: 'error',
        error: error.message,
        last_check: new Date().toISOString()
      });
    }

    // 检查数据库
    try {
      const dbRes = await fetch(`${supabaseUrl}/rest/v1/stocks?select=count&limit=1`, { headers });
      healthChecks.push({
        component: 'database',
        status: dbRes.ok ? 'healthy' : 'unhealthy',
        response_time: Date.now(),
        last_check: new Date().toISOString()
      });
    } catch (error) {
      healthChecks.push({
        component: 'database',
        status: 'error',
        error: error.message,
        last_check: new Date().toISOString()
      });
    }

    // 分析健康趋势
    const componentHealth = {};
    healthData.forEach(h => {
      if (!componentHealth[h.component]) {
        componentHealth[h.component] = [];
      }
      componentHealth[h.component].push({
        status: h.status,
        timestamp: h.created_at,
        error_count: h.error_count
      });
    });

    return new Response(JSON.stringify({
      success: true,
      data: {
        current_health: healthChecks,
        health_history: healthData,
        component_trends: componentHealth,
        overall_status: healthChecks.every(c => c.status === 'healthy') ? 'healthy' : 'degraded'
      },
      timestamp: new Date().toISOString()
    }), { headers: corsHeaders });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: '获取系统健康状态失败',
      message: error.message
    }), { status: 500, headers: corsHeaders });
  }
}

// 获取推送日志
async function getPushLogs(context) {
  const supabaseUrl = 'https://zzukfxwavknskqcepsjb.supabase.co';
  const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw';
  
  try {
    const headers = {
      'Authorization': `Bearer ${supabaseKey}`,
      'apikey': supabaseKey
    };

    const url = new URL(context.request.url);
    const limit = url.searchParams.get('limit') || '50';
    const symbol = url.searchParams.get('symbol');

    let query = `${supabaseUrl}/rest/v1/stock_push_logs?select=*&order=created_at.desc&limit=${limit}`;
    if (symbol) {
      query += `&symbol=eq.${symbol}`;
    }

    const logsRes = await fetch(query, { headers });
    const logs = logsRes.ok ? await logsRes.json() : [];

    // 统计信息
    const stats = {
      total_logs: logs.length,
      processed_count: logs.filter(l => l.processed).length,
      error_count: logs.filter(l => l.error_message).length,
      unique_symbols: [...new Set(logs.map(l => l.symbol))].length,
      latest_push: logs[0]?.push_timestamp || null
    };

    return new Response(JSON.stringify({
      success: true,
      data: {
        logs: logs,
        statistics: stats
      },
      timestamp: new Date().toISOString()
    }), { headers: corsHeaders });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: '获取推送日志失败',
      message: error.message
    }), { status: 500, headers: corsHeaders });
  }
}
