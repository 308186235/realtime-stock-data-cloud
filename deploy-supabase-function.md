# 🚀 Supabase Edge Function 部署指南

## 📋 部署步骤

### 1. 安装Supabase CLI
```bash
npm install -g supabase
```

### 2. 登录Supabase
```bash
supabase login
```

### 3. 初始化项目
```bash
supabase init
```

### 4. 创建Edge Function
```bash
supabase functions new chagubang-sync
```

### 5. 复制代码
将 `supabase-edge-function.js` 的内容复制到:
```
supabase/functions/chagubang-sync/index.ts
```

### 6. 部署Function
```bash
supabase functions deploy chagubang-sync --project-ref zzukfxwavknskqcepsjb
```

### 7. 设置环境变量
```bash
supabase secrets set SUPABASE_URL=https://zzukfxwavknskqcepsjb.supabase.co
supabase secrets set SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🔄 调用Edge Function

### 手动触发
```bash
curl -X POST https://zzukfxwavknskqcepsjb.supabase.co/functions/v1/chagubang-sync \
  -H "Authorization: Bearer YOUR_ANON_KEY"
```

### 定时触发 (Cloudflare Workers)
```javascript
// 在Cloudflare Workers中定时调用
export default {
  async scheduled(event, env, ctx) {
    const response = await fetch(
      'https://zzukfxwavknskqcepsjb.supabase.co/functions/v1/chagubang-sync',
      {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer ' + env.SUPABASE_ANON_KEY
        }
      }
    )
    
    const result = await response.json()
    console.log('茶股帮数据同步结果:', result)
  }
}
```

## 🎯 最终架构

```
茶股帮TCP服务器 → Supabase Edge Function → Supabase数据库 → Cloudflare Workers Agent
```

**优势**:
- ✅ 无中间服务器
- ✅ 直接数据库连接
- ✅ 最小延迟
- ✅ 云端原生
- ✅ 自动扩展

## 📊 监控和调试

### 查看Function日志
```bash
supabase functions logs chagubang-sync
```

### 测试Function
```bash
supabase functions serve chagubang-sync
```

## 🔧 配置Cron定时任务

在Cloudflare Workers中设置定时触发:
```javascript
// wrangler.toml
[triggers]
crons = ["*/3 * * * *"]  # 每3分钟执行一次
```

这样就实现了:
**茶股帮 → Supabase Edge Function → 数据库 → Cloudflare Workers**

完全云端,无本地依赖!
