# 交易系统 Vercel 部署指南

## 🚀 快速部署

### 第1步：准备代码
```bash
# 进入项目目录
cd vercel-trading

# 安装依赖（可选，Vercel会自动安装）
npm install
```

### 第2步：部署到Vercel
```bash
# 方法1：使用Vercel CLI
npm install -g vercel
vercel login
vercel --prod

# 方法2：GitHub集成
# 1. 将代码推送到GitHub
# 2. 在Vercel.com连接GitHub仓库
# 3. 自动部署
```

### 第3步：配置域名
```bash
# 在Vercel Dashboard中：
# 1. 进入项目设置
# 2. 添加自定义域名：api.aigupiao.me
# 3. 配置DNS记录
```

## 📋 API端点

### 健康检查
- `GET /api/health` - 服务状态检查

### 账户相关
- `GET /api/account/balance` - 获取账户余额
- `GET /api/account/positions` - 获取持仓信息

### 交易相关  
- `GET /api/trading/orders` - 获取订单列表
- `POST /api/trading/orders` - 提交新订单

### AI分析
- `GET /api/agent/analysis` - 获取AI分析结果

## 🌐 访问地址

部署成功后，您的API将在以下地址可用：
- Vercel默认域名：`https://your-project.vercel.app`
- 自定义域名：`https://api.aigupiao.me`

## 📱 移动端集成

在您的移动应用中使用：
```javascript
const API_BASE = 'https://api.aigupiao.me';

// 获取账户余额
const balance = await fetch(`${API_BASE}/api/account/balance`);

// 获取AI分析
const analysis = await fetch(`${API_BASE}/api/agent/analysis`);
```

## 🔧 本地开发

```bash
# 启动开发服务器
npm run dev

# 访问 http://localhost:3000/api/health
```

## 📊 优势

- ✅ **零成本**：100万请求/月免费
- ✅ **全球CDN**：访问速度快
- ✅ **自动扩展**：无需担心并发
- ✅ **简单部署**：一键发布
- ✅ **HTTPS**：自动SSL证书
