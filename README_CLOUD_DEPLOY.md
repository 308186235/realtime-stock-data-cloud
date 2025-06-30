# 🌐 云端实时股票数据服务部署指南

## 📋 项目概述

基于 **QT_wat5QfcJ6N9pDZM5** API的云端实时股票数据推送服务，支持WebSocket实时连接，24/7运行。

### ✨ 主要功能
- 🔄 实时股票数据推送 (3秒间隔)
- 🌐 WebSocket连接支持
- 📊 多股票订阅管理
- 📈 实时数据监控面板
- ☁️ 云端部署优化

---

## 🚀 快速部署

### 方法1: Railway部署 (推荐)

1. **Fork此仓库到您的GitHub**

2. **访问 [Railway](https://railway.app)**
   ```
   https://railway.app
   ```

3. **连接GitHub仓库**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择您fork的仓库

4. **配置环境变量**
   ```bash
   MARKET_DATA_API_KEY=QT_wat5QfcJ6N9pDZM5
   ENVIRONMENT=production
   REALTIME_DATA_ENABLED=true
   ```

5. **部署完成**
   - Railway会自动检测并部署
   - 获得类似 `https://your-app.railway.app` 的域名

### 方法2: Render部署

1. **访问 [Render](https://render.com)**

2. **创建新的Web Service**
   - 连接GitHub仓库
   - 选择分支: `main`

3. **配置部署设置**
   ```yaml
   Build Command: pip install -r requirements_cloud.txt
   Start Command: python cloud_app.py
   ```

4. **设置环境变量**
   ```bash
   MARKET_DATA_API_KEY=QT_wat5QfcJ6N9pDZM5
   ENVIRONMENT=production
   REALTIME_DATA_ENABLED=true
   PORT=10000
   ```

---

## 🔧 本地测试

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# 2. 安装依赖
pip install -r requirements_cloud.txt

# 3. 启动服务
python cloud_app.py

# 4. 访问测试页面
http://localhost:8002
```

---

## 📊 API端点

### 🌐 主要端点
```
GET  /                          # 服务首页
GET  /api/health               # 健康检查
GET  /api/realtime/test        # API测试
GET  /api/realtime/stats       # 服务统计
GET  /api/realtime/stocks      # 支持的股票列表
WS   /api/realtime/ws          # WebSocket连接
```

### 📈 WebSocket消息格式

**订阅股票**
```json
{
  "type": "subscribe",
  "stock_code": "000001"
}
```

**接收数据**
```json
{
  "type": "stock_data",
  "stock_code": "000001",
  "data": {
    "price": 12.45,
    "change": 0.15,
    "change_percent": 1.22,
    "volume": 1500000,
    "timestamp": 1672531200
  }
}
```

---

## 🎯 支持的股票

```
000001 - 平安银行    600000 - 浦发银行    600519 - 贵州茅台
000858 - 五粮液      002415 - 海康威视    600036 - 招商银行
300059 - 东方财富    002594 - 比亚迪      300750 - 宁德时代
000002 - 万科A       601318 - 中国平安    002304 - 洋河股份
300014 - 亿纬锂能    000725 - 京东方A
```

---

## 🔍 部署验证

部署完成后，访问以下链接验证：

1. **服务首页**: `https://your-app.platform.com/`
2. **健康检查**: `https://your-app.platform.com/api/health`
3. **API测试**: `https://your-app.platform.com/api/realtime/test`
4. **监控面板**: `https://your-app.platform.com/static/cloud_test.html`

### ✅ 预期结果
```json
{
  "status": "healthy",
  "service": "cloud-realtime-stock-service",
  "api_key": "QT_wat5QfcJ6N9pDZM5",
  "uptime": 3600.5,
  "active_connections": 0
}
```

---

## 🕘 交易时间说明

- **交易时间**: 周一至周五 9:00-15:00
- **数据推送**: 交易时间内推送真实数据
- **非交易时间**: 推送模拟数据用于测试

---

## 🛠️ 故障排查

### 常见问题

**1. 部署失败**
```bash
# 检查requirements_cloud.txt是否存在
# 确认Python版本 >= 3.8
# 检查环境变量配置
```

**2. WebSocket连接失败**
```bash
# 确认平台支持WebSocket
# 检查防火墙设置
# 验证域名和端口
```

**3. 无数据推送**
```bash
# 检查API Key配置
# 确认在交易时间内测试
# 查看服务日志
```

### 📋 调试命令
```bash
# 查看服务状态
curl https://your-app.platform.com/api/health

# 测试API
curl https://your-app.platform.com/api/realtime/test

# 查看统计信息
curl https://your-app.platform.com/api/realtime/stats
```

---

## 📞 技术支持

### 🔧 环境变量说明
```bash
MARKET_DATA_API_KEY=QT_wat5QfcJ6N9pDZM5  # 必需
ENVIRONMENT=production                    # 必需
REALTIME_DATA_ENABLED=true               # 必需
PORT=8002                                # 可选，平台会自动设置
HOST=0.0.0.0                            # 可选，默认0.0.0.0
```

### 📊 性能优化
- 免费版Railway: 512MB RAM, 1GB存储
- 免费版Render: 512MB RAM, 限制运行时间
- 建议升级到付费版以获得更好性能

---

## 🎉 部署成功后

1. **保存部署URL** - 记录您的应用域名
2. **测试所有功能** - 验证API和WebSocket
3. **监控运行状态** - 定期检查服务健康
4. **配置域名** - 可选择绑定自定义域名

---

## 📝 更新日志

- **v1.0.0** - 初始版本，支持基础实时数据推送
- **v1.0.1** - 优化云端部署配置
- **v1.0.2** - 添加监控面板和统计功能

---

## 📄 许可证

MIT License - 可自由使用和修改

---

**🚀 现在就开始部署您的云端实时股票数据服务吧！**
