# GitHub上传指南

## 📁 需要上传的文件

将以下文件上传到GitHub仓库：

### 根目录文件：
```
trading-system-api/
├── package.json
├── vercel.json  
├── README.md
└── api/
    ├── index.js
    ├── health.js
    └── account/
        ├── balance.js
        └── positions.js
```

## 🚀 上传步骤

### 方法1：网页上传（推荐）
1. 在GitHub仓库页面点击"uploading an existing file"
2. 拖拽文件到页面中
3. 填写提交信息："Initial commit - Trading API"
4. 点击"Commit changes"

### 方法2：Git命令行
```bash
git clone https://github.com/YOUR_USERNAME/trading-system-api.git
cd trading-system-api
# 复制文件到此目录
git add .
git commit -m "Initial commit - Trading API"
git push origin main
```

## 📋 文件内容

### package.json
```json
{
  "name": "trading-system-api",
  "version": "1.0.0",
  "description": "Trading System API on Vercel",
  "main": "api/index.js",
  "scripts": {
    "dev": "vercel dev",
    "deploy": "vercel --prod"
  },
  "keywords": ["trading", "api", "vercel"],
  "author": "Trading System",
  "license": "MIT"
}
```

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/**/*.js",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    }
  ]
}
```

## ✅ 完成后

1. GitHub仓库创建完成
2. 代码上传成功
3. 准备部署到Vercel（或其他平台）
