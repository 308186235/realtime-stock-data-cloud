import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

Deno.serve(async (req) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // 茶股帮配置
    const CHAGUBANG_CONFIG = {
      host: 'l1.chagubang.com',
      port: 6380,
      token: 'QT_wat5QfcJ6N9pDZM5'
    }

    // Supabase配置
    const supabaseUrl = Deno.env.get('SUPABASE_URL')
    const supabaseKey = Deno.env.get('SUPABASE_ANON_KEY')
    const supabase = createClient(supabaseUrl, supabaseKey)

    console.log('🔗 开始连接茶股帮...')

    // 连接茶股帮 (使用Deno的TCP连接)
    const conn = await Deno.connect({
      hostname: CHAGUBANG_CONFIG.host,
      port: CHAGUBANG_CONFIG.port,
    })

    console.log('✅ 茶股帮连接成功')

    // 发送token
    const encoder = new TextEncoder()
    await conn.write(encoder.encode(CHAGUBANG_CONFIG.token))

    console.log('📤 Token发送成功，开始接收数据...')

    // 接收数据
    const decoder = new TextDecoder()
    const buffer = new Uint8Array(4096)
    let dataBuffer = ''
    let processedCount = 0
    const maxProcessTime = 10000 // 10秒处理时间

    const startTime = Date.now()

    while (Date.now() - startTime < maxProcessTime) {
      try {
        const bytesRead = await conn.read(buffer)
        if (bytesRead === null) break

        const chunk = decoder.decode(buffer.subarray(0, bytesRead))
        dataBuffer += chunk

        // 处理完整的行
        while (dataBuffer.includes('\n')) {
          const lineEnd = dataBuffer.indexOf('\n')
          const line = dataBuffer.substring(0, lineEnd).trim()
          dataBuffer = dataBuffer.substring(lineEnd + 1)

          if (line) {
            const stockData = parseStockData(line)
            if (stockData) {
              // 保存到Supabase
              const { error } = await supabase
                .from('stock_quotes')
                .upsert([stockData])

              if (!error) {
                processedCount++
              } else {
                console.error('保存数据失败:', error)
              }
            }
          }
        }

        // 限制处理数量
        if (processedCount >= 100) break

      } catch (error) {
        console.error('接收数据错误:', error)
        break
      }
    }

    conn.close()

    console.log(`✅ 处理完成，保存了 ${processedCount} 条数据`)

    return new Response(
      JSON.stringify({
        success: true,
        message: '茶股帮数据同步完成',
        processed_count: processedCount,
        timestamp: new Date().toISOString()
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      },
    )

  } catch (error) {
    console.error('Edge Function错误:', error)

    return new Response(
      JSON.stringify({
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500,
      },
    )
  }
})

// 解析股票数据
function parseStockData(line) {
  try {
    const parts = line.split('|')
    
    if (parts.length >= 10) {
      return {
        symbol: parts[0],
        name: parts[1] || '',
        price: parseFloat(parts[2]) || 0,
        change_percent: parseFloat(parts[3]) || 0,
        volume: parseInt(parts[4]) || 0,
        amount: parseFloat(parts[5]) || 0,
        high: parseFloat(parts[6]) || 0,
        low: parseFloat(parts[7]) || 0,
        open: parseFloat(parts[8]) || 0,
        prev_close: parseFloat(parts[9]) || 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    }
  } catch (error) {
    console.debug('解析数据失败:', error)
  }
  
  return null
}
