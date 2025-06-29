# 🎨 Render混合架构部署指南

## 📋 部署步骤

### 第一步：准备GitHub仓库

1. **提交代码到GitHub**
```bash
git add .
git commit -m "添加Render部署配置"
git push origin main
```

### 第二步：在Render创建服务

1. **访问 [render.com](https://render.com)**
2. **点击 "Get Started for Free"**
3. **使用GitHub账号登录**
4. **点击 "New +" → "Web Service"**
5. **选择您的GitHub仓库**
6. **配置服务**：
   - **Name**: `trading-backend-api`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `python backend/app.py`
   - **Plan**: `Free`

### 第三步：环境变量配置

在Render服务设置中添加环境变量：

| 变量名 | 值 |
|--------|-----|
| `PYTHONPATH` | `/opt/render/project/src` |
| `PORT` | `10000` |
| `ENVIRONMENT` | `production` |
| `DATABASE_URL` | `sqlite:///./data/trading.db` |
| `CORS_ORIGINS` | `*` |

### 第四步：等待部署完成

- ⏳ 首次部署需要5-10分钟
- 🔄 Render会自动构建和启动服务
- ✅ 部署成功后会显示服务URL

### 第五步：获取服务URL

部署完成后，您会得到类似这样的URL：
```
https://trading-backend-api-xxxx.onrender.com
```

### 第六步：配置本地客户端

1. **编辑 `local_hybrid_client.py`**
2. **更新第222行的URL**：
```python
# 将这行
RENDER_URL = "https://your-app-name.onrender.com"

# 改为您的实际URL
RENDER_URL = "https://trading-backend-api-xxxx.onrender.com"
```

### 第七步：运行本地客户端

```bash
python local_hybrid_client.py
```

## 🏗️ 架构说明

```
📱 移动应用
    ↓ HTTPS API调用
🌐 Render云端服务 (https://your-app.onrender.com)
    ↓ WebSocket连接
🖥️ 本地客户端 (local_hybrid_client.py)
    ↓ 直接调用
💼 本地交易软件 (买卖/导出/查询)
```

## ✅ 验证部署

### 1. 检查云端API
```bash
curl https://your-app.onrender.com/api/health
```
应该返回：
```json
{"status": "healthy", "timestamp": "..."}
```

### 2. 检查本地客户端
运行本地客户端后，应该看到：
```
✅ 本地交易模块加载成功
🔗 连接到Render服务: wss://your-app.onrender.com/ws
✅ 已注册到云端服务
```

### 3. 测试移动应用
- 更新移动应用的API地址为Render URL
- 测试登录、查询等功能
- 交易操作会通过本地客户端执行

## 🔧 故障排除

### 问题1：部署失败
**解决方案**：
- 检查 `backend/requirements.txt` 是否存在
- 确认 `backend/app.py` 文件路径正确
- 查看Render部署日志

### 问题2：本地客户端连接失败
**解决方案**：
- 确认Render服务已启动
- 检查URL是否正确
- 确认网络连接正常

### 问题3：交易软件无法操作
**解决方案**：
- 确认交易软件已打开
- 检查 `trader_buy_sell.py` 等模块是否存在
- 查看本地客户端日志

### 问题4：冷启动慢
**原因**：Render免费版有冷启动延迟
**解决方案**：
- 第一次访问可能需要等待30秒
- 可以设置定时ping保持服务活跃
- 考虑升级到付费版本

## 📊 监控和维护

### 1. 服务监控
- Render控制台可查看服务状态
- 查看部署日志和运行日志
- 监控资源使用情况

### 2. 本地客户端监控
- 查看 `local_agent.log` 日志文件
- 监控连接状态和命令执行
- 设置自动重启机制

### 3. 定期维护
- 定期检查服务健康状态
- 更新依赖包版本
- 备份重要数据

## 💡 优化建议

### 1. 性能优化
- 使用Redis缓存频繁查询的数据
- 优化数据库查询
- 压缩API响应

### 2. 安全优化
- 添加API认证
- 限制CORS来源
- 使用HTTPS

### 3. 可靠性优化
- 添加健康检查
- 实现自动重连机制
- 设置错误报警

## 🎯 下一步

1. **测试完整流程**
2. **优化移动应用配置**
3. **添加监控和日志**
4. **考虑数据备份策略**

---

## 📞 支持

如果遇到问题：
1. 查看Render部署日志
2. 检查本地客户端日志
3. 确认网络连接状态
4. 验证交易软件状态
