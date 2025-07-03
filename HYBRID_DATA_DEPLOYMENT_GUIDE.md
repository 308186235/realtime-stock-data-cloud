# 混合数据源系统部署指南

## 🎯 系统架构概述

### 数据流架构
```
茶股帮实时推送 → Supabase数据库 → 股票实时数据
                                    ↓
本地交易软件 → OneDrive → 本地交易数据 → 混合数据API → Agent分析
                                    ↑
                              Cloudflare Worker
```

### 数据源说明
1. **股票实时数据**: 茶股帮推送 → Supabase数据库存储
2. **本地交易数据**: 交易软件导出 → OneDrive同步
3. **Agent分析**: 整合两种数据源进行智能分析

## 📋 部署步骤

### 第一步: 部署混合数据API Worker

#### 1.1 准备Worker代码
- 文件: `hybrid-data-api-worker.js`
- 功能: 整合Supabase + OneDrive数据源

#### 1.2 配置Cloudflare Worker
```bash
# 登录Cloudflare Dashboard
# 进入 Workers & Pages
# 创建新Worker: hybrid-trading-api
# 复制 hybrid-data-api-worker.js 代码
# 部署Worker
```

#### 1.3 配置自定义域名
```bash
# 在Worker设置中添加自定义域名
# 推荐域名: api.aigupiao.me
# 或子域名: hybrid-api.aigupiao.me
```

### 第二步: 验证数据源连接

#### 2.1 测试Supabase连接
```bash
# 运行测试脚本
python test_hybrid_data_api.py

# 检查股票实时数据端点
curl "https://api.aigupiao.me/api/stock/realtime?codes=000001,600036"
```

#### 2.2 测试OneDrive连接
```bash
# 检查本地交易数据端点
curl "https://api.aigupiao.me/api/local-trading/positions"
curl "https://api.aigupiao.me/api/local-trading/balance"
```

#### 2.3 测试混合数据API
```bash
# 检查Agent完整数据端点
curl "https://api.aigupiao.me/api/agent/complete-data?stocks=000001,600036,000002"
```

### 第三步: 配置前端应用

#### 3.1 更新API地址
```javascript
// 在前端配置中更新API基础地址
const API_BASE = 'https://api.aigupiao.me'

// 更新API端点
const ENDPOINTS = {
  agentData: '/api/agent/complete-data',
  stockRealtime: '/api/stock/realtime',
  localPositions: '/api/local-trading/positions',
  localBalance: '/api/local-trading/balance'
}
```

#### 3.2 更新Agent分析页面
```javascript
// 使用新的混合数据API
async function getAgentData() {
  const response = await fetch(`${API_BASE}/api/agent/complete-data?stocks=000001,600036,000002`)
  const data = await response.json()
  return data.data
}
```

## 🔧 API端点说明

### 核心端点

#### 1. Agent完整数据 (推荐)
```
GET /api/agent/complete-data?stocks=000001,600036,000002
```
**功能**: 获取股票实时数据 + 本地交易数据的完整集合
**返回**: 
```json
{
  "success": true,
  "data": {
    "stock_data": { /* 股票实时数据 */ },
    "trading_data": {
      "positions": { /* 本地持仓数据 */ },
      "balance": { /* 本地余额数据 */ }
    },
    "analysis_context": { /* 分析上下文 */ }
  }
}
```

#### 2. 股票实时数据
```
GET /api/stock/realtime?codes=000001,600036
```
**功能**: 获取Supabase中的股票实时数据
**数据源**: 茶股帮推送 → Supabase数据库

#### 3. 本地交易数据
```
GET /api/local-trading/positions  # 持仓数据
GET /api/local-trading/balance    # 余额数据
```
**功能**: 获取OneDrive中的本地导出数据
**数据源**: 本地交易软件 → OneDrive

#### 4. 数据源状态
```
GET /api/data-sources/status
```
**功能**: 检查所有数据源的连接状态

## 🧪 测试和验证

### 自动化测试
```bash
# 运行混合数据API测试
python test_hybrid_data_api.py

# 运行Agent分析演示
python agent_data_analysis_demo.py
```

### 手动测试
```bash
# 1. 基础连接测试
curl "https://api.aigupiao.me/"
curl "https://api.aigupiao.me/health"

# 2. 数据源状态测试
curl "https://api.aigupiao.me/api/data-sources/status"

# 3. 完整数据测试
curl "https://api.aigupiao.me/api/agent/complete-data"
```

## 📊 数据流验证

### 验证股票数据流
1. **茶股帮推送** → 检查是否有新的股票数据推送
2. **Supabase存储** → 验证数据库中是否有最新数据
3. **API读取** → 确认API能正确读取数据库数据

### 验证交易数据流
1. **本地导出** → 运行 `complete_trading_integration.py`
2. **OneDrive同步** → 检查OneDrive中的文件更新
3. **API读取** → 确认API能正确读取OneDrive数据

### 验证Agent数据流
1. **混合数据获取** → 调用 `/api/agent/complete-data`
2. **数据整合** → 验证返回数据包含股票+交易数据
3. **分析处理** → 运行Agent分析演示

## 🔍 故障排除

### 常见问题

#### 1. Supabase连接失败
```bash
# 检查配置
- SUPABASE_URL 是否正确
- SUPABASE_ANON_KEY 是否有效
- 网络连接是否正常
```

#### 2. OneDrive数据读取失败
```bash
# 检查配置
- OneDrive分享链接是否有效
- 文件是否存在于OneDrive
- 分享权限是否正确设置
```

#### 3. API响应慢或超时
```bash
# 优化建议
- 启用Cloudflare缓存
- 减少请求的股票数量
- 检查数据源响应时间
```

### 日志和监控
```bash
# Cloudflare Worker日志
- 在Cloudflare Dashboard查看Worker日志
- 监控API请求量和响应时间
- 检查错误率和失败原因
```

## 🎯 部署检查清单

### 部署前检查
- [ ] Supabase数据库有股票数据
- [ ] OneDrive有本地交易数据
- [ ] Cloudflare Worker代码准备就绪

### 部署后验证
- [ ] 所有API端点响应正常
- [ ] 数据源状态检查通过
- [ ] Agent完整数据获取成功
- [ ] 前端应用能正确调用API

### 功能验证
- [ ] 股票实时数据更新正常
- [ ] 本地交易数据同步正常
- [ ] Agent分析功能工作正常
- [ ] 错误处理和备用数据机制正常

## 🚀 上线准备

### 生产环境配置
1. **域名配置**: 确保 api.aigupiao.me 正确解析
2. **SSL证书**: Cloudflare自动提供SSL
3. **缓存策略**: 配置合适的缓存TTL
4. **监控告警**: 设置API监控和告警

### 性能优化
1. **缓存机制**: 股票数据30秒缓存，交易数据10秒缓存
2. **并发处理**: 并行获取多个数据源
3. **错误恢复**: 数据源失败时使用备用数据

---

## 📞 技术支持

### 快速诊断
```bash
# 运行完整测试
python test_hybrid_data_api.py

# 检查数据源状态
curl "https://api.aigupiao.me/api/data-sources/status"
```

### 联系方式
- 系统状态: 通过API健康检查端点
- 错误日志: Cloudflare Worker Dashboard
- 数据验证: 运行测试脚本

---

*部署指南版本: v1.0*  
*最后更新: 2025-01-03*  
*状态: 生产就绪*
