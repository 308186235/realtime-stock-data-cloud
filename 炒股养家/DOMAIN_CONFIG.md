# 域名配置说明

## 域名信息
- **主域名**: `aigupiao.me`
- **HTTPS**: 通过 Cloudflare 提供
- **协议**: HTTPS/WSS

## 配置文件更新

### 1. 环境配置 (`env.js`)
```javascript
// 生产环境
[ENV_TYPE.PROD]: {
  // API基础URL
  apiBaseUrl: 'https://api.aigupiao.me',

  // WebSocket地址
  wsUrl: 'wss://api.aigupiao.me/ws',

  // 其他配置...
}
```

### 2. 服务配置 (`services/config.js`)
```javascript
// API基础URL,根据环境设置
const baseUrl = process.env.NODE_ENV === 'development'
  ? 'http://localhost:8000'  // 开发环境
  : 'https://api.aigupiao.me';   // 生产环境
```

### 3. Agent分析控制台环境信息
生产环境显示:
- **API端点**: `https://aigupiao.me/api`
- **数据源**: 实时股票数据源
- **风险级别**: 高风险

### 4. WebSocket连接
所有WebSocket连接已更新为:
- 开发环境: `ws://localhost:8000/ws`
- 生产环境: `wss://aigupiao.me/ws`

## 更新的文件列表

1. `env.js` - 主环境配置文件
2. `services/config.js` - 服务配置文件
3. `pages/ai-analysis/index.vue` - Agent分析控制台页面
4. `auto-trader/index/index.vue` - 自动交易页面
5. `auto-trader/index/index.fixed.vue` - 修复版自动交易页面

## Cloudflare 配置建议

### SSL/TLS 设置
- 加密模式: **完全(严格)**
- 最低 TLS 版本: **1.2**
- 启用 **HSTS**

### WebSocket 支持
- 确保 Cloudflare 的 WebSocket 支持已启用
- 在 **Network** 标签页中启用 **WebSockets**

### 缓存规则
建议为 API 路径设置缓存规则:
```
/api/* - 不缓存 (Bypass Cache)
/ws - 不缓存 (Bypass Cache)
```

### 页面规则
可以设置页面规则优化性能:
```
aigupiao.me/api/* - 缓存级别: 绕过
aigupiao.me/* - 缓存级别: 标准
```

## 部署检查清单

- [ ] 确认域名 DNS 指向正确
- [ ] 验证 HTTPS 证书有效
- [ ] 测试 API 端点连接
- [ ] 验证 WebSocket 连接
- [ ] 检查 CORS 设置
- [ ] 测试前端页面加载
- [ ] 验证 Agent 功能正常

## 环境切换

### 开发环境
```bash
NODE_ENV=development
```
- API: `http://localhost:8000`
- WebSocket: `ws://localhost:8000/ws`

### 生产环境
```bash
NODE_ENV=production
```
- API: `https://aigupiao.me`
- WebSocket: `wss://aigupiao.me/ws`

## 故障排除

### 常见问题

1. **API 连接失败**
   - 检查 Cloudflare SSL 设置
   - 验证后端服务是否运行
   - 检查防火墙设置

2. **WebSocket 连接失败**
   - 确认 Cloudflare WebSocket 支持已启用
   - 检查后端 WebSocket 服务
   - 验证 WSS 证书

3. **CORS 错误**
   - 检查后端 CORS 配置
   - 验证 Cloudflare 设置
   - 确认域名配置正确

### 调试命令

```bash
# 测试 API 连接
curl -I https://aigupiao.me/api/health

# 测试 WebSocket (使用 wscat)
wscat -c wss://aigupiao.me/ws

# 检查 DNS 解析
nslookup aigupiao.me

# 检查 SSL 证书
openssl s_client -connect aigupiao.me:443
```

## 更新日期
2024-01-15

## 联系信息
如有问题,请检查配置文件或联系开发团队。
