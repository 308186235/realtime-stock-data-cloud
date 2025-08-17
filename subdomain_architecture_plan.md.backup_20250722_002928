# AI股票交易系统 - 子域名架构规划

## 🎯 核心子域名架构

### **主要服务域名**
```
app.aigupiao.me          - 主前端应用 (Vue/React/uni-app)
api.aigupiao.me          - 后端API服务 (FastAPI/Express)
ws.aigupiao.me           - WebSocket实时数据
admin.aigupiao.me        - 管理后台
mobile.aigupiao.me       - 移动端H5应用
```

### **数据与分析服务**
```
data.aigupiao.me         - 数据服务API
analytics.aigupiao.me    - 数据分析平台
ai.aigupiao.me           - AI分析引擎
backtest.aigupiao.me     - 回测系统
```

### **支持服务**
```
docs.aigupiao.me         - API文档 & 用户手册
status.aigupiao.me       - 系统状态监控
cdn.aigupiao.me          - 静态资源CDN
files.aigupiao.me        - 文件上传/下载
```

### **环境分离**
```
test.aigupiao.me         - 测试环境
dev.aigupiao.me          - 开发环境
staging.aigupiao.me      - 预发布环境
```

## 🔧 Cloudflare DNS配置

### **A记录配置**
```
类型    名称        内容                    代理状态
A       app         104.21.x.x             已代理
A       api         104.21.x.x             已代理
A       ws          104.21.x.x             已代理
A       admin       104.21.x.x             已代理
A       mobile      104.21.x.x             已代理
```

### **CNAME记录配置**
```
类型     名称        内容                    代理状态
CNAME    data        api.aigupiao.me        已代理
CNAME    analytics   app.aigupiao.me        已代理
CNAME    docs        app.aigupiao.me        已代理
CNAME    status      app.aigupiao.me        已代理
```

### **通配符SSL证书**
```
证书类型: 通配符证书
覆盖范围: *.aigupiao.me
自动续期: 已启用
```

## 🚀 部署架构方案

### **方案1: Cloudflare Pages + Workers**
```
app.aigupiao.me      → Cloudflare Pages (前端)
api.aigupiao.me      → Cloudflare Workers (轻量API)
ws.aigupiao.me       → Cloudflare Durable Objects (WebSocket)
admin.aigupiao.me    → Cloudflare Pages (管理后台)
```

### **方案2: 混合云架构**
```
app.aigupiao.me      → Vercel/Netlify (前端)
api.aigupiao.me      → Railway/Render (后端API)
ws.aigupiao.me       → 专用WebSocket服务
data.aigupiao.me     → 数据库服务
```

### **方案3: 容器化部署**
```
app.aigupiao.me      → Docker容器 (前端)
api.aigupiao.me      → Docker容器 (后端)
ws.aigupiao.me       → Docker容器 (WebSocket)
所有服务通过Docker Compose编排
```

## 📱 移动端策略

### **响应式 vs 独立移动端**
```
app.aigupiao.me      - 响应式设计，支持桌面和移动端
mobile.aigupiao.me   - 专门为移动端优化的轻量版本
```

### **PWA支持**
```
app.aigupiao.me/manifest.json    - PWA配置
app.aigupiao.me/sw.js            - Service Worker
支持离线使用和推送通知
```

## 🔒 安全配置

### **CORS配置**
```javascript
// API服务CORS设置
const corsOptions = {
  origin: [
    'https://app.aigupiao.me',
    'https://admin.aigupiao.me', 
    'https://mobile.aigupiao.me'
  ],
  credentials: true
}
```

### **CSP策略**
```
Content-Security-Policy: 
  default-src 'self' *.aigupiao.me;
  script-src 'self' 'unsafe-inline' *.aigupiao.me;
  style-src 'self' 'unsafe-inline' *.aigupiao.me;
```

## 🚀 立即实施步骤

### **第1步: 配置子域名DNS**
1. 登录Cloudflare Dashboard
2. 进入DNS设置
3. 添加子域名记录：
   ```
   A    app     104.21.x.x    已代理
   A    api     104.21.x.x    已代理
   ```

### **第2步: 部署前端到app子域名**
```bash
# 创建app子域名的部署
git clone https://github.com/308186235/Bei-fen.git app-frontend
cd app-frontend
# 配置Cloudflare Pages指向app.aigupiao.me
```

### **第3步: 配置API子域名**
```bash
# 部署后端API到api.aigupiao.me
# 可以使用Railway、Render或Cloudflare Workers
```

### **第4步: 更新前端配置**
```javascript
// 更新API基础URL
const API_BASE_URL = 'https://api.aigupiao.me'
const WS_URL = 'wss://ws.aigupiao.me'
```

## 📋 迁移计划

### **当前状态**
```
aigupiao.me          - 主域名，显示完整应用
bei-fen.pages.dev    - Cloudflare Pages默认域名
```

### **目标状态**
```
aigupiao.me          - 重定向到app.aigupiao.me或显示landing页面
app.aigupiao.me      - 主前端应用
api.aigupiao.me      - 后端API服务
```

### **迁移步骤**
1. **保持现有服务运行**
2. **逐步添加子域名服务**
3. **测试所有功能正常**
4. **更新DNS指向**
5. **设置重定向规则**

## 🎯 推荐优先级

### **第一阶段 (立即实施)**
- ✅ app.aigupiao.me - 主前端应用
- ✅ api.aigupiao.me - 后端API

### **第二阶段 (1-2周内)**
- 📱 mobile.aigupiao.me - 移动端优化
- 📊 ws.aigupiao.me - 实时数据

### **第三阶段 (1个月内)**
- 🔧 admin.aigupiao.me - 管理后台
- 📈 analytics.aigupiao.me - 数据分析

## 💡 额外建议

### **SEO优化**
```
aigupiao.me          - Landing页面，介绍产品
app.aigupiao.me      - 应用入口，需要登录
```

### **监控和日志**
```
status.aigupiao.me   - 系统状态页面
logs.aigupiao.me     - 日志查看(内部使用)
```

### **开发工具**
```
dev.aigupiao.me      - 开发环境
test.aigupiao.me     - 测试环境
docs.aigupiao.me     - API文档
```

这样的架构可以支持你未来的所有扩展需求！你觉得这个规划如何？我们可以立即开始实施第一阶段。
