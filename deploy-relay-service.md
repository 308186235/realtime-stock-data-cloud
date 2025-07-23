# 云端中转服务部署指南

## 🏗️ 架构说明

```
前端App → 云端Agent → 云端中转服务 ← WebSocket ← 本地客户端 → 本地交易软件
```

## 📋 部署步骤

### 1. 部署云端中转服务

```bash
# 创建新的Cloudflare Worker项目
wrangler init relay-service

# 复制cloud-relay-service.js内容到src/index.js
cp cloud-relay-service.js relay-service/src/index.js

# 部署到Cloudflare
cd relay-service
wrangler deploy --env production
```

### 2. 配置域名

在Cloudflare Dashboard中设置:
- 域名:`relay.aigupiao.me`
- 指向:刚部署的relay-service Worker

### 3. 修改主Worker

修改 `ultra-simple-worker.js` 中的本地交易API端点:

```javascript
// 将现有的本地调用改为中转服务调用
const relayResponse = await fetch('https://relay.aigupiao.me/api/relay/positions', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
    'User-Agent': 'CloudAgent/1.0'
  },
  timeout: 15000
});
```

### 4. 运行本地客户端

在您的本地电脑上:

```bash
# 安装依赖
pip install websockets requests asyncio

# 运行本地中转客户端
python local-relay-client.py
```

## 🔧 配置说明

### 本地客户端配置

编辑 `local-relay-client.py`:

```python
# 云端中转服务WebSocket地址
self.ws_url = "wss://relay.aigupiao.me/ws/local-client"

# 本地交易软件API地址
self.local_api_base = "http://localhost:8000"
```

### 前端配置

修改 `agentDataService.js`:

```javascript
// 持仓信息端点
url: `${this.apiBaseUrl}/api/local-trading/positions`

// 账户余额端点  
url: `${this.apiBaseUrl}/api/local-trading/balance`
```

## 🚀 工作流程

### 数据获取流程

1. **前端请求** → `api.aigupiao.me/api/local-trading/positions`
2. **主Worker** → `relay.aigupiao.me/api/relay/positions`
3. **中转服务** → 通过WebSocket请求本地客户端
4. **本地客户端** → 调用 `localhost:8000/api/positions`
5. **本地交易软件** → 返回真实数据
6. **数据回传** → 原路返回到前端

### 交易执行流程

1. **前端发起交易** → `api.aigupiao.me/api/local-trading/buy`
2. **主Worker** → `relay.aigupiao.me/api/relay/buy`
3. **中转服务** → 通过WebSocket发送交易指令
4. **本地客户端** → 调用 `localhost:8000/api/buy`
5. **本地交易软件** → 执行真实交易
6. **结果回传** → 原路返回交易结果

## 📊 监控和状态

### 检查中转服务状态

```bash
curl https://relay.aigupiao.me/api/relay/status
```

### 检查本地连接

本地客户端会显示连接状态:
- ✅ 成功连接到云端中转服务
- 📡 调用本地API成功
- 📤 自动发送数据到云端

## 🔍 故障排除

### 常见问题

1. **WebSocket连接失败**
   - 检查防火墙设置
   - 确认域名解析正确

2. **本地API调用失败**
   - 确认本地交易软件运行在8000端口
   - 检查API端点是否正确

3. **数据不同步**
   - 检查本地客户端是否正常运行
   - 查看WebSocket连接状态

### 日志查看

- **云端中转服务**:Cloudflare Dashboard → Workers → Logs
- **本地客户端**:控制台输出
- **本地交易软件**:软件自身日志

## 🎯 优势

1. **真实数据**:直接从本地交易软件获取
2. **实时同步**:WebSocket保持连接
3. **故障恢复**:自动重连机制
4. **安全性**:本地数据不暴露到公网
5. **扩展性**:支持多个本地客户端

## 📝 下一步

1. 部署云端中转服务
2. 运行本地客户端
3. 测试数据同步
4. 验证交易执行
5. 监控系统状态

这个方案解决了云端无法直接访问本地网络的问题,通过WebSocket建立稳定的双向通信通道。
