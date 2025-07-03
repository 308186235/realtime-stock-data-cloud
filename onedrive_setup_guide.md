# OneDrive存储方案设置指南

## 🎯 方案概述

这个方案非常简单直接：
1. **本地服务器**：直接将交易数据保存到OneDrive文件夹
2. **云端Worker**：通过Microsoft Graph API直接读取OneDrive文件

## 📋 设置步骤

### 1. 本地OneDrive设置

#### 1.1 安装OneDrive客户端
- 确保您的电脑已安装OneDrive客户端
- 登录您的Microsoft账户
- 确保OneDrive正在同步

#### 1.2 创建交易数据文件夹
在您的OneDrive中创建文件夹：
```
OneDrive/
└── TradingData/
    ├── latest_positions.json  (持仓数据)
    └── latest_balance.json    (余额数据)
```

### 2. Azure应用注册

#### 2.1 访问Azure Portal
1. 打开 https://portal.azure.com
2. 登录您的Microsoft账户

#### 2.2 注册应用
1. 进入 **Azure Active Directory** > **应用注册**
2. 点击 **新注册**
3. 填写应用信息：
   - **名称**：TradingDataAPI
   - **支持的账户类型**：任何组织目录中的帐户和个人Microsoft帐户
   - **重定向URI**：留空

#### 2.3 配置API权限
1. 在应用页面，点击 **API权限**
2. 点击 **添加权限** > **Microsoft Graph** > **应用程序权限**
3. 搜索并添加：`Files.ReadWrite.All`
4. 点击 **授予管理员同意**

#### 2.4 创建客户端密码
1. 点击 **证书和密码**
2. 点击 **新客户端密码**
3. 设置描述和过期时间
4. **复制并保存客户端密码**（只显示一次）

#### 2.5 获取应用信息
在 **概述** 页面复制：
- **应用程序(客户端)ID**
- **目录(租户)ID**

### 3. 配置Worker

#### 3.1 修改Worker代码
在 `ultra-simple-worker.js` 中找到这部分：

```javascript
// Microsoft Graph API配置
const graphConfig = {
  clientId: 'YOUR_CLIENT_ID',        // 替换为您的客户端ID
  clientSecret: 'YOUR_CLIENT_SECRET', // 替换为您的客户端密码
  tenantId: 'common'                 // 或者您的租户ID
};
```

替换为您的实际值。

#### 3.2 部署Worker
```bash
wrangler deploy --env production
```

### 4. 测试方案

#### 4.1 测试本地保存
1. 运行本地交易服务器
2. 调用导出API：
```bash
curl -X POST http://localhost:8888/export -H "Content-Type: application/json" -d '{"data_type":"holdings"}'
```
3. 检查OneDrive/TradingData文件夹是否有新文件

#### 4.2 测试云端读取
```bash
curl https://api.aigupiao.me/api/local-trading/positions
```

## 🔧 工作原理

### 数据流程
```
本地交易软件 → 本地服务器 → OneDrive文件夹 → OneDrive云同步 → Microsoft Graph API → 云端Worker → 前端应用
```

### 文件结构
```json
{
  "data_type": "positions",
  "timestamp": "2025-07-03T02:30:00.000Z",
  "source": "local_computer",
  "data": {
    "positions": [...],
    "summary": {...}
  }
}
```

## 🎯 优势

1. **✅ 简单直接** - 本地直接保存文件，云端直接读取
2. **✅ 实时同步** - OneDrive自动同步
3. **✅ 无需复杂配置** - 不需要WebSocket或数据库
4. **✅ 可靠性高** - 利用OneDrive的稳定性
5. **✅ 易于调试** - 可以直接查看OneDrive文件

## 🔍 故障排除

### 常见问题

1. **文件未同步**
   - 检查OneDrive客户端是否正常运行
   - 确认网络连接正常

2. **Graph API权限错误**
   - 确认已授予管理员同意
   - 检查客户端ID和密码是否正确

3. **文件不存在错误**
   - 确认本地服务器已生成文件
   - 检查文件路径是否正确

### 调试方法

1. **检查本地文件**
   ```bash
   ls -la ~/OneDrive/TradingData/
   ```

2. **测试Graph API**
   ```bash
   curl -X GET "https://graph.microsoft.com/v1.0/me/drive/root:/TradingData:/children" \
        -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

## 📝 注意事项

1. **安全性**：客户端密码要妥善保管
2. **权限**：确保应用有足够的OneDrive访问权限
3. **同步延迟**：OneDrive同步可能有几秒延迟
4. **文件大小**：单个文件建议不超过10MB

这个方案非常适合您的需求，既简单又可靠！
