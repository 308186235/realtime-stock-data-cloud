# 🌐 域名连接问题解决方案

## 📋 问题现状
- **域名**: `aigupiao.me`
- **错误**: "当前无法使用此页面" / "服务器拒绝了连接"
- **原因**: Cloudflare配置或后端服务器问题

## 🔧 解决步骤

### 1. 检查本地API服务器状态
```bash
# 检查8003端口是否在运行
netstat -an | findstr :8003

# 测试本地API
curl http://localhost:8003/api/health
```

### 2. Cloudflare配置检查
需要在Cloudflare控制台配置：

#### A. DNS设置
- **类型**: A记录
- **名称**: @ (根域名)
- **内容**: 您的服务器公网IP
- **代理状态**: 🟠 已代理 (启用)

#### B. SSL/TLS设置
- **加密模式**: 完全(严格) 或 灵活
- **边缘证书**: 启用
- **源服务器证书**: 配置(如果使用完全模式)

#### C. 防火墙规则
- 允许来自Cloudflare的请求
- 检查是否有阻止规则

### 3. 服务器端口配置

#### 方案A: 使用标准端口 (推荐)
```python
# 修改 app_api_server.py
PORT = 80  # HTTP标准端口
# 或
PORT = 443  # HTTPS标准端口 (需要SSL证书)
```

#### 方案B: 使用自定义端口 + 反向代理
```nginx
# nginx配置示例
server {
    listen 80;
    server_name aigupiao.me;
    
    location / {
        proxy_pass http://localhost:8003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. 临时解决方案 - 使用IP直接访问
如果域名暂时无法使用，可以：
```
# 直接使用服务器IP + 端口
http://您的服务器IP:8003
```

## 🚀 快速修复方案

### 方案1: 修改为标准端口
```python
# 在 app_api_server.py 中修改
PORT = 80  # 使用HTTP标准端口
```

### 方案2: 创建简单的端口转发
```python
# 创建一个80端口的转发服务器
import http.server
import socketserver
from urllib.request import urlopen
from urllib.parse import urlparse

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # 转发到8003端口
        target_url = f"http://localhost:8003{self.path}"
        try:
            response = urlopen(target_url)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.read())
        except Exception as e:
            self.send_error(502, f"Bad Gateway: {e}")

# 在80端口启动代理
with socketserver.TCPServer(("", 80), ProxyHandler) as httpd:
    print("代理服务器运行在端口80")
    httpd.serve_forever()
```

## 📱 APP配置更新

确保APP配置正确指向域名：

```javascript
// env.js 生产环境配置
[ENV_TYPE.PROD]: {
  apiBaseUrl: 'https://aigupiao.me',  // 使用HTTPS
  wsUrl: 'wss://aigupiao.me/ws',      // WebSocket使用WSS
  // ...
}
```

## 🔍 调试命令

```bash
# 1. 检查域名解析
nslookup aigupiao.me

# 2. 检查端口连通性
telnet aigupiao.me 80
telnet aigupiao.me 443

# 3. 检查HTTP响应
curl -I https://aigupiao.me

# 4. 检查本地服务器
curl http://localhost:8003/api/health
```

## ⚡ 立即可用的解决方案

1. **修改API服务器端口为80**
2. **或者配置Cloudflare的源服务器端口**
3. **或者使用nginx反向代理**

选择最适合您当前环境的方案！
