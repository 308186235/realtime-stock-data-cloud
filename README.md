# 智能交易Agent系统

这是一个基于深度强化学习的自主交易Agent系统,具有自学习,自适应和自优化能力。系统通过不断从市场中学习,自动调整交易策略以适应不同的市场环境。

## 🚀 核心特性

### 1. 自主学习能力
- **深度强化学习**:采用DQN和A2C算法,从交易经验中学习最优策略
- **经验记忆回放**:存储和分析历史交易,从成功和失败中学习
- **元学习**:不仅学习交易策略,还学习如何更有效地学习
- **在线学习**:实时更新模型,持续优化决策能力

### 2. 智能决策系统
- **多策略融合**:整合趋势跟踪,均值回归,突破等多种策略
- **自适应权重**:根据市场状态动态调整策略权重
- **置信度评估**:为每个决策提供置信度评分
- **风险感知**:内置风险管理,自动控制仓位和止损

### 3. 市场分析能力
- **多时间框架分析**:从1分钟到日线的全方位市场扫描
- **市场状态识别**:自动识别牛市,熊市,震荡等市场状态
- **技术指标集成**:RSI,MACD,布林带等经典指标
- **模式识别**:头肩顶,双顶双底等形态识别

### 4. 实时监控与控制
- **Web控制台**:直观的Agent状态监控和控制界面
- **WebSocket推送**:实时推送决策和市场更新
- **性能追踪**:详细的交易记录和性能分析
- **参数调优**:支持在线调整学习参数

## 📋 系统架构

```
交易Agent系统
├── 核心Agent (agent_system.py)
│   ├── 市场分析器 (market_analyzer.py)
│   ├── 决策引擎 (decision_engine.py)
│   ├── 风险管理器 (risk_manager.py)
│   └── 策略融合器 (strategy_fusion.py)
├── 学习模块
│   ├── 学习管理器 (learning_manager.py)
│   ├── 强化学习 (reinforcement_learning.py)
│   ├── 经验记忆 (experience_memory.py)
│   └── 元学习 (meta_learning.py)
└── API接口
    ├── REST API (agent_api.py)
    └── WebSocket (实时推送)
```

## 🛠️ 安装与使用

### 环境要求
- Python 3.8+
- TensorFlow 2.8+
- 4GB+ RAM (建议8GB)
- GPU支持(可选,但推荐)

### 快速开始

1. **克隆项目**
```bash
git clone <repository-url>
cd 交易2
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置系统**
编辑 `config/agent_config.json` 根据需要调整参数

4. **启动Agent**
```bash
# Windows
start_agent.bat

# Linux/Mac
python start_learning_agent.py
```

5. **访问控制台**
打开浏览器访问 `http://localhost:8000/api/docs` 查看API文档

## 📊 性能指标

系统会自动跟踪以下性能指标:
- **胜率**:成功交易占比
- **收益率**:总体和年化收益
- **夏普比率**:风险调整后收益
- **最大回撤**:最大亏损幅度
- **盈亏比**:平均盈利/平均亏损

## 🔧 配置说明

主要配置项(`config/agent_config.json`):

```json
{
  "learning": {
    "learning_rate": 0.001,      // 学习率
    "exploration_rate": 0.2,     // 探索率
    "batch_size": 64            // 批次大小
  },
  "risk_management": {
    "max_position_size": 0.2,    // 最大仓位
    "stop_loss_percentage": 0.05 // 止损百分比
  }
}
```

## 📚 API文档

### REST API端点

- `GET /api/agent/status` - 获取Agent状态
- `POST /api/agent/decision` - 获取交易决策
- `GET /api/agent/market-analysis` - 获取市场分析
- `GET /api/agent/performance` - 获取性能指标
- `POST /api/agent/learn` - 触发学习过程

### WebSocket连接

```javascript
const ws = new WebSocket('ws://localhost:8000/api/agent/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // 处理实时数据
};
```

## 🎯 使用场景

1. **自动交易**:完全自主的交易决策和执行
2. **交易辅助**:为人工交易提供决策建议
3. **策略研究**:测试和优化交易策略
4. **风险管理**:实时监控和控制交易风险

## ⚠️ 风险提示

- 交易有风险,使用本系统需谨慎
- 建议先在模拟环境中测试
- 定期监控系统表现
- 设置合理的风险限制

## 🤝 贡献

欢迎提交Issue和Pull Request来改进系统。

## 📄 许可证

本项目采用MIT许可证。

---

## 原股票交易回测系统

以下是原有的股票交易策略回测系统文档...

[原有内容保留]
