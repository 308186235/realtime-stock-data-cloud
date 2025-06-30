# Cloudflare Worker KV 设置指南

## 🎯 创建KV命名空间

### 1. 在Cloudflare Dashboard中：
1. 进入 **Workers & Pages**
2. 点击 **KV**
3. 点击 **Create a namespace**
4. 创建以下命名空间：

| 命名空间名称 | 用途 | TTL |
|-------------|------|-----|
| `STOCK_CACHE` | 实时股票价格缓存 | 3秒 |
| `MARKET_DATA` | 市场指数数据缓存 | 30秒 |
| `USER_SESSIONS` | 用户会话缓存 | 1小时 |
| `API_CACHE` | API响应缓存 | 5分钟 |

### 2. 绑定到Worker：
在 `wrangler.toml` 中添加：

```toml
[[kv_namespaces]]
binding = "STOCK_CACHE"
id = "你的KV命名空间ID"
preview_id = "预览环境ID"

[[kv_namespaces]]
binding = "MARKET_DATA"
id = "你的KV命名空间ID"
preview_id = "预览环境ID"

[[kv_namespaces]]
binding = "USER_SESSIONS"
id = "你的KV命名空间ID"
preview_id = "预览环境ID"

[[kv_namespaces]]
binding = "API_CACHE"
id = "你的KV命名空间ID"
preview_id = "预览环境ID"
```

## 📊 KV数据结构设计

### 实时股票数据 (STOCK_CACHE)
```javascript
// Key: stock:{code}
// Value: 
{
  "code": "600000",
  "name": "浦发银行",
  "price": 11.23,
  "change": 0.67,
  "change_pct": 6.34,
  "volume": 1500000,
  "timestamp": "2025-06-30T15:30:00Z"
}
```

### 市场指数数据 (MARKET_DATA)
```javascript
// Key: index:{code}
// Value:
{
  "code": "000001",
  "name": "上证指数",
  "price": 3200.45,
  "change": 1.23,
  "change_pct": 0.38,
  "timestamp": "2025-06-30T15:30:00Z"
}
```

### 用户会话 (USER_SESSIONS)
```javascript
// Key: session:{user_id}
// Value:
{
  "user_id": "uuid",
  "username": "user123",
  "permissions": ["read", "trade"],
  "last_active": "2025-06-30T15:30:00Z"
}
```

### API缓存 (API_CACHE)
```javascript
// Key: api:{endpoint}:{params_hash}
// Value:
{
  "data": {...},
  "cached_at": "2025-06-30T15:30:00Z",
  "expires_at": "2025-06-30T15:35:00Z"
}
```

## 🔧 Worker KV操作示例

### 写入数据
```javascript
// 缓存股票价格 (3秒过期)
await STOCK_CACHE.put(
  `stock:${stockCode}`, 
  JSON.stringify(stockData),
  { expirationTtl: 3 }
);

// 缓存市场数据 (30秒过期)
await MARKET_DATA.put(
  `index:${indexCode}`,
  JSON.stringify(indexData),
  { expirationTtl: 30 }
);
```

### 读取数据
```javascript
// 读取股票价格
const stockData = await STOCK_CACHE.get(`stock:${stockCode}`);
if (stockData) {
  return JSON.parse(stockData);
}

// 批量读取多只股票
const stockCodes = ['600000', '000001', '000002'];
const promises = stockCodes.map(code => 
  STOCK_CACHE.get(`stock:${code}`)
);
const results = await Promise.all(promises);
```

### 删除数据
```javascript
// 删除过期数据
await STOCK_CACHE.delete(`stock:${stockCode}`);

// 清空用户会话
await USER_SESSIONS.delete(`session:${userId}`);
```

## 📈 性能优化策略

### 1. 批量操作
```javascript
// 批量写入股票数据
const writePromises = stockList.map(stock => 
  STOCK_CACHE.put(
    `stock:${stock.code}`,
    JSON.stringify(stock),
    { expirationTtl: 3 }
  )
);
await Promise.all(writePromises);
```

### 2. 缓存穿透保护
```javascript
async function getStockPrice(stockCode) {
  // 先查KV缓存
  let data = await STOCK_CACHE.get(`stock:${stockCode}`);
  if (data) return JSON.parse(data);
  
  // 缓存未命中，查数据库
  data = await fetchFromSupabase(stockCode);
  if (data) {
    // 写入缓存
    await STOCK_CACHE.put(
      `stock:${stockCode}`,
      JSON.stringify(data),
      { expirationTtl: 3 }
    );
  }
  
  return data;
}
```

### 3. 缓存预热
```javascript
// 预热热门股票数据
const hotStocks = ['600000', '000001', '600519', '000858'];
for (const code of hotStocks) {
  const data = await fetchStockData(code);
  await STOCK_CACHE.put(`stock:${code}`, JSON.stringify(data), {
    expirationTtl: 3
  });
}
```

## 🚨 注意事项

1. **KV限制**：
   - 免费层：每天100,000次读取 + 1,000次写入
   - 单个值最大25MB
   - 键名最大512字节

2. **TTL设置**：
   - 实时数据：3秒
   - 市场数据：30秒  
   - 用户会话：1小时
   - API缓存：5分钟

3. **错误处理**：
   - KV操作可能失败，需要降级到数据库
   - 设置合理的超时时间
   - 记录操作日志

4. **数据一致性**：
   - KV是最终一致性，不是强一致性
   - 关键数据仍需要数据库确认
   - 定期清理过期数据
