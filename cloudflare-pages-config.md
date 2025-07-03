# Cloudflare Pages配置

## 构建设置
- 构建命令: `npm run build`
- 构建输出目录: `dist`
- 根目录: `/`

## 环境变量
- NODE_ENV: production
- API_BASE_URL: https://api.aigupiao.me
- WS_URL: wss://api.aigupiao.me/ws

## 自定义域名
- app.aigupiao.me
- mobile.aigupiao.me
- admin.aigupiao.me

## 重定向规则
/api/* https://api.aigupiao.me/api/:splat 200
/* /index.html 200
