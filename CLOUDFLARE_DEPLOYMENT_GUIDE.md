# Cloudflare部署指南

## 🌐 域名架构

### 主要域名
- **主域名**: aigupiao.me
- **API服务**: api.aigupiao.me (Cloudflare Workers)
- **前端应用**: app.aigupiao.me (Cloudflare Pages)
- **移动端**: mobile.aigupiao.me (Cloudflare Pages)
- **管理后台**: admin.aigupiao.me (Cloudflare Pages)

## 🚀 部署步骤

### 1. Cloudflare Workers (API服务)
```bash
# 安装Wrangler CLI
npm install -g wrangler

# 登录Cloudflare
wrangler login

# 部署API服务
wrangler publish
```

### 2. Cloudflare Pages (前端应用)
1. 连接GitHub仓库到Cloudflare Pages
2. 设置构建命令: `npm run build`
3. 设置输出目录: `dist`
4. 配置自定义域名: app.aigupiao.me

### 3. DNS配置
在Cloudflare DNS中添加：
- A记录: aigupiao.me → Cloudflare IP
- CNAME记录: api → aigupiao.me
- CNAME记录: app → aigupiao.me
- CNAME记录: mobile → aigupiao.me
- CNAME记录: admin → aigupiao.me

## 🔧 环境变量

### Cloudflare Workers
- ENVIRONMENT: production
- API_BASE_URL: https://api.aigupiao.me

### Cloudflare Pages
- NODE_ENV: production
- API_BASE_URL: https://api.aigupiao.me
- WS_URL: wss://api.aigupiao.me/ws

## 📱 移动应用配置

更新移动应用中的API地址：
```javascript
const API_CONFIG = {
  baseURL: 'https://api.aigupiao.me',
  wsURL: 'wss://api.aigupiao.me/ws'
};
```

## 🔍 验证部署

1. 访问 https://app.aigupiao.me 检查前端
2. 访问 https://api.aigupiao.me/health 检查API
3. 测试WebSocket连接: wss://api.aigupiao.me/ws

## ⚠️ 注意事项

- 所有Netlify配置已移除
- 使用Cloudflare的全球CDN加速
- 支持自动HTTPS和SSL证书
- WebSocket连接通过Cloudflare Workers
