# 股票交易回测系统 API 集成说明

## 简介

本文档说明了股票交易回测系统的前后端 API 集成方案。该系统使用简化版 API 服务器(`simple_api_server.py`)提供与原系统相同的 API 路由,以确保前端能够正常工作,同时逐步解决完整后端的问题。

## 系统架构

系统由以下主要组件组成:

1. **前端**:
   - 使用 Vue.js 框架构建的 Web 应用
   - 包含交易界面,回测配置,结果展示等功能
   - 统一通过服务层调用后端 API

2. **简化版 API 服务器**:
   - 使用 FastAPI 框架
   - 提供与原系统相同的 API 路由
   - 使用模拟数据响应请求

3. **测试脚本**:
   - `test_full_api_flow.py` 验证整个前后端交互流程
   - 覆盖认证流程,回测执行,结果获取等核心流程

## API 端点

系统支持以下主要 API 端点:

### 认证 API

- **登录**: `POST /api/auth/token`
  - 请求: `{ "username": "用户名", "password": "密码" }`
  - 响应: `{ "access_token": "令牌", "token_type": "bearer", "username": "用户名", "expires_at": "过期时间" }`

- **获取用户信息**: `GET /api/auth/me`
  - 请求头: `Authorization: Bearer <token>`
  - 响应: `{ "username": "用户名", "role": "角色", "is_active": true }`

### 回测 API

- **执行回测**: `POST /api/backtesting/run`
  - 请求: 包含策略配置,交易品种,日期范围等参数
  - 响应: 回测结果,包括ID,指标数据,图表数据,交易记录等

- **获取回测结果**: `GET /api/backtesting/results/{backtest_id}`
  - 响应: 指定ID的回测详细结果

- **保存回测**: `POST /api/backtesting/save`
  - 请求: `{ "backtest_id": "回测ID", "name": "回测名称" }`
  - 响应: `{ "status": "success", "message": "回测结果已保存" }`

- **获取回测历史**: `GET /api/backtesting/history`
  - 响应: 所有已保存回测的列表

### 辅助 API

- **获取技术指标**: `GET /api/backtesting/indicators`
  - 响应: 可用技术指标列表

- **获取基准指数**: `GET /api/backtesting/benchmarks`
  - 响应: 可用基准指数列表

## 认证流程

1. 前端调用登录API获取令牌
2. 将令牌存储在localStorage中
3. 后续API请求在请求头中添加令牌
4. 令牌过期时重新登录

## 回测流程

1. 配置回测参数(策略,品种,时间范围等)
2. 调用回测执行API运行回测
3. 获取回测结果和指标
4. 可选择保存回测结果
5. 查看历史回测记录

## 测试方法

使用提供的批处理脚本可以快速测试API集成:

```
run_api_test.bat
```

该脚本将:
1. 启动简化版API服务器
2. 运行完整的API流程测试
3. 展示测试结果
4. 停止服务器

## 故障排除

如果遇到API连接问题,请检查:

1. API服务器是否正常运行(http://localhost:8000/api/docs)
2. 网络连接是否正常
3. 请求格式是否符合API要求(特别是请求体格式)
4. 认证令牌是否有效

## 开发注意事项

1. 前端代码中的API路径应与后端路由保持一致
2. 更改API请求/响应格式时,需同时更新前后端代码
3. 使用简化版API服务器进行开发和测试,确保前端正常工作
4. 完整后端开发完成后,前端无需修改即可无缝切换 
