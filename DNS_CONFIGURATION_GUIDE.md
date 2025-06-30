# Cloudflare DNS配置指南

## 🌐 子域名DNS记录配置

### A记录 (指向Cloudflare Pages)
```
类型    名称    内容                代理状态
A       app     104.21.x.x         已代理  
A       api     104.21.x.x         已代理
A       mobile  104.21.x.x         已代理
A       admin   104.21.x.x         已代理
A       ws      104.21.x.x         已代理
A       docs    104.21.x.x         已代理
```

### CNAME记录 (别名指向)
```
类型     名称        内容                代理状态
CNAME    www         aigupiao.me        已代理
CNAME    data        api.aigupiao.me    已代理
CNAME    status      app.aigupiao.me    已代理
```

## 🔧 Cloudflare Pages项目配置

### 1. app.aigupiao.me
- 构建命令: `echo "Static deployment"`
- 构建输出目录: `subdomains/app`
- 自定义域名: `app.aigupiao.me`

### 2. api.aigupiao.me  
- 部署到: Railway/Render/Cloudflare Workers
- 自定义域名: `api.aigupiao.me`

### 3. mobile.aigupiao.me
- 构建命令: `echo "Mobile deployment"`
- 构建输出目录: `subdomains/mobile`
- 自定义域名: `mobile.aigupiao.me`

## 📋 配置步骤

1. 登录Cloudflare Dashboard
2. 选择域名: aigupiao.me
3. 进入DNS设置
4. 添加上述DNS记录
5. 进入Pages设置
6. 为每个子域名创建独立的Pages项目
7. 配置自定义域名

## 🔒 SSL证书

Cloudflare会自动为所有子域名提供SSL证书，包括通配符证书 *.aigupiao.me
