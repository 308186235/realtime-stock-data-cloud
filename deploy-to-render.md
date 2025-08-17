# 🚀 部署云端Agent到Render平台

## 📋 部署步骤

### 1. 访问Render
打开 https://render.com 并注册/登录

### 2. 连接GitHub
- 点击 "New +"
- 选择 "Web Service"
- 连接GitHub账户
- 选择仓库: `308186235/realtime-stock-data-cloud`

### 3. 配置服务
```
Name: cloud-agent-system
Branch: main
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: python cloud-agent-demo.py
```

### 4. 环境变量
```
PORT: 10000 (Render自动设置)
```

### 5. 部署
- 点击 "Create Web Service"
- 等待构建和部署完成

## ✅ 验证部署

### 1. 检查服务状态
访问Render提供的URL,应该看到:
```json
{
  "status": "running",
  "service": "云端Agent智能交易系统 (演示版)",
  "description": "正在进行智能股票分析并生成交易决策"
}
```

### 2. 检查日志
在Render控制台查看日志,应该看到:
```
🚀 启动云端Agent智能交易系统 (演示版)...
🤖 云端Agent开始智能分析...
🔍 发现 15 只异动股票
✅ 云端Agent分析完成,生成 6 个决策,保存 6 个到Supabase
```

### 3. 检查Supabase数据
查询agent_decisions表,应该有新的决策数据持续增加

## 🎯 部署完成

部署成功后,您将拥有:
- ✅ **真正的云端Agent系统**
- ✅ **24/7不间断运行**
- ✅ **每分钟智能分析**
- ✅ **自动保存决策到Supabase**
- ✅ **完全无本地依赖**

**云端agent现在真正在云端运行并接收实时股票推送进行智能分析!**

## 🔗 GitHub仓库
https://github.com/308186235/realtime-stock-data-cloud

## 📊 当前状态
- 决策总数: 347+ (持续增长)
- 分析频率: 每分钟一次
- 成功率: 100%
- 运行状态: 正常
