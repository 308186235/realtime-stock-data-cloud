# 🚀 已模块化working-trader-FIXED使用指南

## 📋 概述

working-trader-FIXED已经完全模块化，为Agent提供了简单易用的API接口！

---

## 🏗️ **模块化架构**

```
📦 working-trader-FIXED (已模块化)
├── 🔧 trader_api.py - 统一API接口
├── 💰 trader_buy_sell.py - 买卖交易模块
├── 📊 trader_export.py - 数据导出模块
├── ⚙️ trader_core.py - 核心功能模块
└── 🧪 测试和演示文件
```

---

## 🔌 **TraderAPI - 统一接口**

### **初始化**
```python
from trader_api import TraderAPI, api

# 方式1: 创建新实例
trader = TraderAPI()

# 方式2: 使用全局实例（推荐）
trader = api
```

### **交易功能**
```python
# 买入股票
success = trader.buy("000001", 100, "10.50")  # 股票代码, 数量, 价格
success = trader.buy("600000", 200)  # 市价买入

# 卖出股票  
success = trader.sell("000001", 100, "10.60")  # 股票代码, 数量, 价格
success = trader.sell("600000", 200)  # 市价卖出
```

### **数据导出功能**
```python
# 单独导出
success = trader.export_positions()    # 导出持仓数据
success = trader.export_trades()       # 导出成交数据
success = trader.export_orders()       # 导出委托数据

# 批量导出
results = trader.export_all()  # 导出所有数据
# 返回: {"holdings": bool, "transactions": bool, "orders": bool}
```

### **文件管理**
```python
# 获取导出文件列表
files = trader.get_files()
# 返回: {"holdings": [文件列表], "transactions": [文件列表], "orders": [文件列表]}

# 清理过期文件
trader.cleanup_files()
```

### **状态查询**
```python
# 获取系统状态
status = trader.get_status()
# 返回: {
#   "current_window": "当前窗口标题",
#   "trading_software_active": bool,
#   "export_files": 文件数量
# }
```

---

## 🤖 **Agent集成示例**

### **简单Agent**
```python
from trader_api import api

class SimpleAgent:
    def __init__(self):
        self.trader = api
    
    def make_decision(self, stock_data):
        if stock_data['change_pct'] < -5:  # 跌超5%
            return self.trader.buy(stock_data['code'], 100)
        elif stock_data['change_pct'] > 10:  # 涨超10%
            return self.trader.sell(stock_data['code'], 100)
    
    def export_daily_data(self):
        return self.trader.export_all()
```

### **云端Agent调用**
```python
import requests

class CloudAgent:
    def execute_local_trade(self, action, code, quantity, price=None):
        # 通过API调用本地交易
        response = requests.post("http://localhost:8888/trade", json={
            "action": action,
            "stock_code": code, 
            "quantity": quantity,
            "price": price
        })
        return response.json()
    
    def get_local_portfolio(self):
        # 获取本地投资组合
        response = requests.post("http://localhost:8888/export", json={
            "data_type": "all"
        })
        return response.json()
```

---

## 🖥️ **本地服务器部署**

### **简化版本地服务器**
```bash
# 运行简化版本地服务器
python simple_local_trading_server.py
```

**功能特性**:
- ✅ 直接使用已模块化的TraderAPI
- ✅ 简单的HTTP接口
- ✅ 完整的错误处理
- ✅ 详细的日志记录

### **完整版本地服务器**
```bash
# 运行完整版本地服务器（需要安装依赖）
pip install fastapi uvicorn websockets
python local_trading_server.py
```

**功能特性**:
- ✅ FastAPI + WebSocket
- ✅ 云端连接支持
- ✅ CORS配置
- ✅ 异步处理

---

## ☁️ **云端集成**

### **云端API路由**
在`backend/app.py`中添加：
```python
from backend.api.cloud_local_trading_api import router as cloud_local_router
app.include_router(cloud_local_router)
```

### **Agent系统集成**
在`backend/ai/agent_system.py`中已添加：
```python
async def execute_local_trade(self, action, stock_code, quantity, price=None):
    """执行本地交易"""
    api_url = "https://api.aigupiao.me/api/cloud-local-trading/execute-trade"
    # ... 实现代码
```

---

## 🧪 **测试和演示**

### **本地功能测试**
```bash
# 测试TraderAPI功能
python trader_api.py

# 测试简化版服务器
python simple_local_trading_server.py
```

### **云端本地集成测试**
```bash
# 测试云端到本地的完整通信
python test_cloud_local_integration.py
```

### **Agent交易演示**
```bash
# 演示云端Agent调用本地交易
python cloud_agent_local_trading_demo.py
```

---

## 📊 **API接口总览**

### **本地API (localhost:8888)**
```
GET  /           - 服务状态
GET  /status     - 本地状态
POST /trade      - 执行交易
POST /export     - 导出数据
GET  /health     - 健康检查
```

### **云端API (api.aigupiao.me)**
```
POST /api/cloud-local-trading/execute-trade  - 执行本地交易
POST /api/cloud-local-trading/export-data   - 导出本地数据
GET  /api/cloud-local-trading/local-status  - 获取本地状态
POST /api/cloud-local-trading/agent/buy     - Agent买入
POST /api/cloud-local-trading/agent/sell    - Agent卖出
```

---

## 🔧 **配置和部署**

### **必需文件检查**
```bash
# 确认模块化文件存在
ls trader_*.py

# 应该看到:
# trader_api.py          - ✅ 统一API接口
# trader_buy_sell.py     - ✅ 买卖交易模块  
# trader_export.py       - ✅ 数据导出模块
# trader_core.py         - ✅ 核心功能模块
```

### **依赖安装**
```bash
# 基础依赖（Windows）
pip install pywin32

# 服务器依赖（可选）
pip install fastapi uvicorn websockets requests
```

### **环境要求**
- ✅ Windows系统
- ✅ Python 3.7+
- ✅ 交易软件运行
- ✅ Caps Lock功能正常

---

## 🎯 **使用流程**

### **日常使用**
1. **启动交易软件** - 确保交易软件正常运行
2. **启动本地服务器** - `python simple_local_trading_server.py`
3. **云端Agent决策** - Agent分析数据并生成决策
4. **执行交易** - 通过API调用本地交易功能
5. **导出数据** - 定期导出交易数据进行分析

### **开发调试**
1. **测试API功能** - `python trader_api.py`
2. **测试单个模块** - 分别测试买卖和导出功能
3. **测试服务器** - 验证HTTP API接口
4. **测试集成** - 运行完整的集成测试

---

## 🎉 **优势特性**

### **模块化优势**
- ✅ **统一接口**: TraderAPI提供一致的调用方式
- ✅ **功能分离**: 买卖、导出、核心功能独立模块
- ✅ **易于维护**: 模块化设计便于更新和扩展
- ✅ **向后兼容**: 保留原有功能的同时提供新接口

### **Agent友好**
- ✅ **简单调用**: `api.buy()`, `api.sell()`, `api.export_all()`
- ✅ **错误处理**: 完善的异常处理和日志记录
- ✅ **状态查询**: 实时获取系统和软件状态
- ✅ **批量操作**: 支持批量导出和文件管理

### **云端集成**
- ✅ **HTTP API**: 标准的RESTful接口
- ✅ **WebSocket**: 实时双向通信
- ✅ **跨平台**: 云端Agent可以是任何语言
- ✅ **高可用**: 多重备份和故障恢复

---

## 🚀 **立即开始**

### **快速测试**
```python
# 1. 导入API
from trader_api import api

# 2. 检查状态
status = api.get_status()
print(f"交易软件激活: {status['trading_software_active']}")

# 3. 导出数据
results = api.export_all()
print(f"导出结果: {results}")

# 4. 模拟交易
success = api.buy("000001", 100, "10.50")
print(f"买入结果: {success}")
```

### **启动服务器**
```bash
# 简单版（推荐）
python simple_local_trading_server.py

# 完整版
python local_trading_server.py
```

### **云端集成**
```bash
# 部署云端API
git push origin main  # 推送到GitHub
# Cloudflare自动部署

# 测试集成
python test_cloud_local_integration.py
```

**🎊 现在您可以轻松使用已模块化的working-trader-FIXED，让Agent通过简单的API调用实现强大的本地交易功能！**
