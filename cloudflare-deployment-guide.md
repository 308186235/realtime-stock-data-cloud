# Cloudflare全栈部署指南

## 🎯 部署目标
将整个股票交易系统部署到Cloudflare，实现：
- 后端API: Cloudflare Workers
- 前端应用: Cloudflare Pages
- 数据库: Supabase (已配置)
- 域名: aigupiao.me及子域名

## 📋 部署清单

### ✅ 已完成
- [x] DNS记录配置完成
- [x] 前端API配置指向api.aigupiao.me
- [x] Cloudflare Workers代码准备完成
- [x] Supabase数据库配置完成

### 🔄 待完成
- [ ] 部署Cloudflare Workers API
- [ ] 部署Cloudflare Pages前端
- [ ] 配置Workers路由
- [ ] 配置Pages自定义域名
- [ ] 测试所有功能

## 🚀 部署步骤

### 步骤1: 部署Cloudflare Workers API

#### 方法A: 使用Wrangler CLI (推荐)
```bash
# 1. 登录Cloudflare
wrangler login

# 2. 创建KV命名空间
wrangler kv:namespace create "TRADING_KV"

# 3. 更新wrangler.toml中的KV ID

# 4. 部署Worker
wrangler publish
```

#### 方法B: 使用Cloudflare Dashboard
1. 访问 https://dash.cloudflare.com
2. 进入 Workers & Pages
3. 创建新的Worker
4. 复制 `cloudflare-api/src/index.js` 的内容
5. 保存并部署

### 步骤2: 配置Workers路由
1. 在Cloudflare Dashboard中
2. 进入 Workers & Pages > 你的Worker
3. 添加路由: `api.aigupiao.me/*`
4. 选择区域: `aigupiao.me`

### 步骤3: 创建KV存储
1. 在Workers & Pages中
2. 进入KV存储
3. 创建命名空间: `TRADING_KV`
4. 在Worker设置中绑定KV

### 步骤4: 部署前端到Cloudflare Pages

#### 方法A: 连接GitHub仓库
1. 在Cloudflare Dashboard中
2. 进入 Workers & Pages
3. 创建Pages项目
4. 连接GitHub仓库
5. 设置构建配置:
   - 构建命令: (留空或自定义)
   - 构建输出目录: `炒股养家`
   - 根目录: `/`

#### 方法B: 直接上传
1. 压缩 `炒股养家` 目录
2. 在Pages中选择直接上传
3. 上传压缩文件

### 步骤5: 配置Pages自定义域名
1. 在Pages项目设置中
2. 添加自定义域名:
   - `app.aigupiao.me`
   - `mobile.aigupiao.me`
   - `admin.aigupiao.me`
3. 等待SSL证书生成

## 🔧 配置文件说明

### wrangler.toml 配置
```toml
name = "aigupiao-trading-api"
main = "src/index.js"
compatibility_date = "2024-01-01"

[env.production]
name = "aigupiao-trading-api"
routes = [
  { pattern = "api.aigupiao.me/*", zone_name = "aigupiao.me" }
]

[[kv_namespaces]]
binding = "TRADING_KV"
id = "你的KV命名空间ID"
```

### 环境变量设置
在Worker设置中添加：
- `SUPABASE_URL`: https://zzukfxwavknskqcepsjb.supabase.co
- `SUPABASE_ANON_KEY`: (你的匿名密钥)
- `STOCK_API_KEY`: QT_wat5QfcJ6N9pDZM5

## 🌐 域名配置验证

访问以下URL验证部署：

### API端点测试
- https://api.aigupiao.me/api/health
- https://api.aigupiao.me/api/agent/status
- https://api.aigupiao.me/api/trading/balance

### 前端页面测试
- https://app.aigupiao.me (主应用)
- https://mobile.aigupiao.me (移动端)
- https://admin.aigupiao.me (管理后台)
- https://aigupiao.me (重定向到app)

## 🔍 故障排除

### 常见问题

1. **Worker部署失败**
   - 检查代码语法
   - 确认KV绑定正确
   - 查看Worker日志

2. **路由不工作**
   - 确认DNS记录正确
   - 检查路由配置
   - 等待DNS传播

3. **CORS错误**
   - 检查CORS头部设置
   - 确认API域名配置

4. **前端无法访问API**
   - 检查env.js配置
   - 确认API URL正确
   - 测试API端点

## 📱 移动端特殊配置

对于uni-app移动端，需要：
1. 配置域名白名单
2. 更新manifest.json
3. 重新打包应用

## 🎉 部署完成检查

部署完成后，确认以下功能正常：
- [ ] API健康检查通过
- [ ] Agent状态查询正常
- [ ] 股票数据获取正常
- [ ] 前端页面加载正常
- [ ] 移动端访问正常
- [ ] 管理后台功能正常

## 📞 技术支持

如遇问题，可以：
1. 查看Cloudflare Dashboard日志
2. 检查浏览器开发者工具
3. 测试API端点响应
4. 验证DNS解析结果
