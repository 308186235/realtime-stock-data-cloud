# Netlify 部署指南

## 📁 文件夹结构

请确保您的文件夹结构如下：

```
netlify-trading/
├── netlify.toml
├── package.json
├── public/
│   └── index.html
└── netlify/
    └── functions/
        ├── health.js
        ├── account-balance.js
        ├── account-positions.js
        └── agent-analysis.js
```

## 🚀 部署步骤

### 步骤1：准备文件
1. 创建一个名为 `netlify-trading` 的文件夹
2. 将所有文件按照上述结构放入文件夹
3. 确保所有文件都在正确位置

### 步骤2：上传到Netlify
1. 在Netlify控制台点击 "Add new project"
2. 选择 "Deploy manually"
3. 拖拽整个 `netlify-trading` 文件夹到上传区域
4. 等待部署完成

### 步骤3：测试API
部署成功后，您的API将在以下地址可用：
- 主页：https://your-site-name.netlify.app/
- 健康检查：https://your-site-name.netlify.app/api/health
- 账户余额：https://your-site-name.netlify.app/api/account-balance
- 持仓信息：https://your-site-name.netlify.app/api/account-positions
- AI分析：https://your-site-name.netlify.app/api/agent-analysis

## ✅ 成功标志

部署成功后，您应该看到：
1. 绿色的 "Published" 状态
2. 可以访问的网站URL
3. 所有API端点都能正常返回JSON数据

## 🔧 如果遇到问题

1. 检查文件结构是否正确
2. 确保所有文件都已上传
3. 查看Netlify的部署日志
4. 检查函数是否正确部署到 /.netlify/functions/ 路径下
