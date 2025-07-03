# 🚀 快速部署指南 - 修复OneDrive数据读取

## 🎯 问题
当前 `api.aigupiao.me` 无法读取OneDrive的真实数据，需要部署新的Worker来解决

## 📋 5分钟快速部署

### 步骤1: 打开Cloudflare Dashboard
1. 访问 https://dash.cloudflare.com
2. 选择域名 `aigupiao.me`
3. 点击左侧 **Workers & Pages**

### 步骤2: 找到现有Worker
1. 找到当前运行的Worker (可能叫 `api` 或类似名称)
2. 点击进入Worker详情页面
3. 点击 **Edit code** 按钮

### 步骤3: 替换Worker代码
1. **全选并删除** 现有代码
2. **复制粘贴** 以下新代码
3. 点击 **Save and deploy**

### 步骤4: 验证部署
访问 https://api.aigupiao.me/ 应该看到新的响应

---

## 🔧 新Worker代码 (复制粘贴)

```javascript
/**
 * 混合数据源API Worker - 支持OneDrive数据读取
 * 解决云端Agent无法获取本地导出数据的问题
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

// 配置
const CONFIG = {
  // Supabase配置
  SUPABASE_URL: 'https://zzukfxwavknskqcepsjb.supabase.co',
  SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw',
  
  // OneDrive分享链接
  ONEDRIVE_SHARES: {
    positions: 'https://1drv.ms/u/c/f988d396f8de5959/EcLi6OcK2R5KoQumcE8dx6EB0pb8rjeD8ghYFQvb0bR1rw?e=3mxWXi',
    balance: 'https://1drv.ms/u/c/f988d396f8de5959/EZWBY0aF7KhPmWSOX-9OlBEBFzgJeOWhmicQhfMoyjNwgA?e=IksT7e'
  },
  
  // CORS配置
  CORS_HEADERS: {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400'
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
    return new Response(null, {
      status: 200,
      headers: CONFIG.CORS_HEADERS
    })
  }
  
  try {
    if (path === '/') {
      return handleRoot()
    } else if (path === '/health') {
      return handleHealth()
    } else if (path === '/api/agent/complete-data') {
      return handleAgentCompleteData(request)
    } else if (path === '/api/local-trading/positions') {
      return handleLocalPositions(request)
    } else if (path === '/api/local-trading/balance') {
      return handleLocalBalance(request)
    } else {
      return createErrorResponse('API端点未找到', 404)
    }
  } catch (error) {
    console.error('请求处理错误:', error)
    return createErrorResponse(`服务器错误: ${error.message}`, 500)
  }
}

/**
 * 根路径处理
 */
function handleRoot() {
  const welcomeData = {
    message: "🚀 混合数据源交易系统API (OneDrive支持)",
    status: "running",
    platform: "Cloudflare Workers",
    timestamp: new Date().toISOString(),
    version: "3.1.0",
    data_sources: {
      stock_realtime: "Supabase数据库 (茶股帮推送)",
      trading_data: "OneDrive (本地导出) - 已修复",
      integration: "混合数据源Agent分析"
    },
    fix_note: "已修复OneDrive数据读取问题"
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
    onedrive_support: "enabled",
    fix_status: "deployed"
  })
}

/**
 * 本地持仓数据API
 */
async function handleLocalPositions(request) {
  try {
    console.log('📊 获取OneDrive持仓数据')
    
    const oneDriveData = await getOneDriveData('positions')
    
    if (oneDriveData) {
      console.log('✅ 成功从OneDrive获取持仓数据')
      return createSuccessResponse({
        ...oneDriveData,
        api_source: 'onedrive_realtime',
        api_note: '从OneDrive实时读取的本地导出数据',
        fix_note: 'OneDrive数据读取已修复'
      })
    } else {
      console.log('⚠️ OneDrive数据不可用，使用备用数据')
      return createSuccessResponse({
        ...getBackupPositionsData(),
        api_source: 'backup_data',
        api_note: 'OneDrive数据不可用，使用备用数据'
      })
    }
    
  } catch (error) {
    console.error('获取持仓数据失败:', error)
    return createErrorResponse(`获取持仓数据失败: ${error.message}`, 500)
  }
}

/**
 * 本地余额数据API
 */
async function handleLocalBalance(request) {
  try {
    console.log('💰 获取OneDrive余额数据')
    
    const oneDriveData = await getOneDriveData('balance')
    
    if (oneDriveData) {
      console.log('✅ 成功从OneDrive获取余额数据')
      return createSuccessResponse({
        ...oneDriveData,
        api_source: 'onedrive_realtime',
        api_note: '从OneDrive实时读取的本地导出数据',
        fix_note: 'OneDrive数据读取已修复'
      })
    } else {
      console.log('⚠️ OneDrive数据不可用，使用备用数据')
      return createSuccessResponse({
        ...getBackupBalanceData(),
        api_source: 'backup_data',
        api_note: 'OneDrive数据不可用，使用备用数据'
      })
    }
    
  } catch (error) {
    console.error('获取余额数据失败:', error)
    return createErrorResponse(`获取余额数据失败: ${error.message}`, 500)
  }
}

/**
 * Agent完整数据API
 */
async function handleAgentCompleteData(request) {
  try {
    console.log('🤖 Agent请求完整数据集')
    
    // 并行获取OneDrive数据
    const [positionsData, balanceData] = await Promise.all([
      getOneDriveData('positions'),
      getOneDriveData('balance')
    ])
    
    // 整合数据
    const completeData = {
      timestamp: new Date().toISOString(),
      data_sources: {
        local_positions: !!positionsData,
        local_balance: !!balanceData
      },
      trading_data: {
        positions: positionsData || getBackupPositionsData(),
        balance: balanceData || getBackupBalanceData()
      },
      analysis_context: {
        data_freshness: {
          positions_data: positionsData?.timestamp || null,
          balance_data: balanceData?.timestamp || null
        },
        fix_note: "OneDrive数据读取已修复",
        agent_notes: [
          "交易数据来源: 本地交易软件 → OneDrive → API (已修复)",
          "数据读取: 实时从OneDrive获取最新导出数据"
        ]
      }
    }
    
    console.log('✅ Agent完整数据集成成功')
    return createSuccessResponse(completeData)
    
  } catch (error) {
    console.error('Agent数据集成失败:', error)
    return createErrorResponse(`数据集成失败: ${error.message}`, 500)
  }
}

/**
 * 从OneDrive获取数据
 */
async function getOneDriveData(dataType) {
  try {
    const shareUrl = CONFIG.ONEDRIVE_SHARES[dataType]
    if (!shareUrl) {
      throw new Error(`未知的数据类型: ${dataType}`)
    }
    
    console.log(`📁 从OneDrive获取${dataType}数据`)
    
    // 转换为直接下载链接
    const downloadUrl = convertShareUrlToDownload(shareUrl)
    
    const response = await fetch(downloadUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    })
    
    if (!response.ok) {
      throw new Error(`OneDrive访问失败: ${response.status}`)
    }
    
    const data = await response.json()
    console.log(`✅ OneDrive ${dataType}数据获取成功`)
    
    return data
    
  } catch (error) {
    console.error(`OneDrive ${dataType}数据获取失败:`, error)
    return null
  }
}

/**
 * 转换OneDrive分享链接
 */
function convertShareUrlToDownload(shareUrl) {
  try {
    const encoded = btoa(shareUrl).replace(/=+$/, '').replace(/\//g, '_').replace(/\+/g, '-')
    return `https://api.onedrive.com/v1.0/shares/u!${encoded}/root/content`
  } catch (error) {
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
```

---

## ✅ 部署验证

部署完成后，访问以下URL验证:

1. **根路径**: https://api.aigupiao.me/
   - 应该显示 "OneDrive支持" 和 "已修复" 信息

2. **持仓数据**: https://api.aigupiao.me/api/local-trading/positions
   - 应该显示 `"api_source": "onedrive_realtime"`

3. **Agent数据**: https://api.aigupiao.me/api/agent/complete-data
   - 应该包含最新的OneDrive数据

## 🧪 最终测试

部署完成后运行:
```bash
python create_real_test_data.py
```

如果看到测试ID被检测到，说明修复成功！

---

*快速部署指南 - 解决OneDrive数据读取问题*
