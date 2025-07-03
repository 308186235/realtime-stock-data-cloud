# 移动前端访问后端配置检查

## 🔍 **当前配置状态**

### ✅ **已正确配置的部分**:

1. **环境配置文件** (`env.js`)
   - 开发环境: `http://localhost:8000`
   - 生产环境: `https://api.aigupiao.me`
   - WebSocket: `wss://api.aigupiao.me/ws`

2. **服务配置** (`services/config.js`)
   - API基础URL已更新为您的域名

3. **请求工具** (`auto-trader/request.js`)
   - 已更新为使用正确的API地址

4. **Agent服务** (`services/agentTradingService.js`)
   - 所有API调用都使用环境配置

### ⚠️ **需要检查的部分**:

1. **后端CORS配置**
   - 需要确保后端允许来自 `https://app.aigupiao.me` 的请求
   - 检查 `backend/app.py` 中的CORS设置

2. **SSL证书**
   - 确保 Cloudflare SSL 配置正确
   - 验证 HTTPS 证书有效

3. **防火墙设置**
   - 确保服务器防火墙允许HTTPS (443端口)
   - 确保WebSocket连接不被阻止

## 🧪 **网络连接测试工具**

我已经为您创建了一个网络连接测试页面:

### 访问方式:
1. 打开应用
2. 进入"设置"页面
3. 点击"网络连接测试"

### 测试功能:
- ✅ API连接测试
- ✅ WebSocket连接测试  
- ✅ Agent服务测试
- ✅ 详细日志记录
- ✅ 响应时间监控

## 🔧 **可能的问题和解决方案**

### 1. **API连接失败**

**可能原因**:
- 后端服务未启动
- CORS配置不正确
- SSL证书问题
- 防火墙阻止

**解决方案**:
```bash
# 检查后端服务状态
curl -I https://aigupiao.me/api/health

# 检查CORS设置
curl -H "Origin: https://aigupiao.me" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     https://aigupiao.me/api/health
```

### 2. **WebSocket连接失败**

**可能原因**:
- Cloudflare WebSocket支持未启用
- 后端WebSocket服务未运行
- 网络代理阻止WebSocket

**解决方案**:
1. 在Cloudflare控制台启用WebSocket支持
2. 检查后端WebSocket服务
3. 测试WebSocket连接:
```bash
wscat -c wss://aigupiao.me/ws
```

### 3. **移动端特殊问题**

**可能原因**:
- 移动网络限制
- App权限设置
- 证书信任问题

**解决方案**:
1. 检查App网络权限
2. 在移动设备上信任SSL证书
3. 尝试不同网络环境(WiFi/4G/5G)

## 📱 **移动端配置检查**

### uni-app配置 (`manifest.json`)
```json
{
  "mp-weixin": {
    "setting": {
      "urlCheck": false  // 已配置,允许访问外部域名
    }
  }
}
```

### 网络安全配置
- ✅ 已配置允许HTTPS请求
- ✅ 已配置WebSocket支持
- ✅ 已关闭URL检查限制

## 🚀 **测试步骤**

### 1. 基础连通性测试
```bash
# 测试域名解析
nslookup aigupiao.me

# 测试HTTPS连接
curl -I https://aigupiao.me

# 测试API端点
curl https://aigupiao.me/api/health
```

### 2. 移动端测试
1. 使用网络测试工具进行全面检测
2. 查看详细日志了解具体错误
3. 在不同网络环境下测试

### 3. 功能测试
1. 测试Agent分析控制台功能
2. 验证实时数据更新
3. 检查WebSocket实时通信

## 📊 **预期测试结果**

### 成功状态:
- ✅ API连接: 成功 (响应时间 < 1000ms)
- ✅ WebSocket连接: 成功
- ✅ Agent服务: 成功

### 失败处理:
- ❌ 详细错误日志
- 🔧 具体解决建议
- 📞 技术支持联系方式

## 🆘 **故障排除联系**

如果测试失败,请提供以下信息:
1. 网络测试页面的详细日志
2. 使用的网络环境(WiFi/移动网络)
3. 设备型号和系统版本
4. 具体的错误信息

## 📝 **更新记录**

- 2024-01-15: 创建网络测试工具
- 2024-01-15: 更新所有配置文件为 aigupiao.me 域名
- 2024-01-15: 添加CORS配置建议

---

**下一步**: 请使用网络测试工具检查连接状态,如有问题请查看详细日志进行排查。
