# AI系统到Agent系统迁移指南

## 概述

本文档说明了如何从原有的AI交易系统迁移到新的自学习Agent系统。新系统具有更强的自主学习能力和市场适应性。

## 主要变化

### 1. 架构升级
- **原系统**:基于规则的策略优化器
- **新系统**:基于强化学习的自主Agent

### 2. 核心能力增强
- ✅ 深度强化学习(DQN,A2C)
- ✅ 经验记忆和回放
- ✅ 元学习能力
- ✅ 自适应策略选择
- ✅ 实时学习和优化

### 3. API变更
- 原API路径:`/api/ai/*`
- 新API路径:`/api/agent/*`

## 迁移步骤

### 1. 安装新依赖
```bash
pip install -r requirements.txt
```

### 2. 创建必要目录
```bash
mkdir models data logs plots
```

### 3. 更新配置
- 复制 `config/agent_config.json` 并根据需要调整参数
- 主要配置项:
  - 学习参数
  - 风险管理
  - 策略权重

### 4. 启动新系统
```bash
# 方式1:使用启动脚本
start_agent.bat

# 方式2:直接运行
python start_learning_agent.py --config config/agent_config.json
```

### 5. 前端集成
```javascript
// 更新API服务
import agentService from './services/aiService';

// 使用新的Agent API
const status = await agentService.getAgentStatus();
const decision = await agentService.getAgentDecision(marketData);
```

## API对照表

| 功能 | 原API | 新API |
|------|-------|-------|
| 获取状态 | `/api/ai/status` | `/api/agent/status` |
| 获取决策 | `/api/ai/optimize` | `/api/agent/decision` |
| 市场分析 | `/api/ai/analyze` | `/api/agent/market-analysis` |
| 风险评估 | `/api/ai/risk` | `/api/agent/risk-assessment` |
| 性能指标 | N/A | `/api/agent/performance` |
| 学习状态 | N/A | `/api/agent/learning-status` |

## 新增功能

### 1. 学习管理
- 实时学习进度监控
- 手动触发学习
- 学习参数调整

### 2. 经验管理
- 交易经验存储
- 成功/失败案例分析
- 经验回放优化

### 3. 策略融合
- 多策略权重自适应
- 市场状态策略匹配
- 策略性能评估

### 4. WebSocket支持
- 实时状态推送
- 决策通知
- 市场更新

## 注意事项

1. **数据兼容性**:新系统使用不同的数据格式,历史数据需要转换
2. **性能要求**:新系统需要更多计算资源,建议使用GPU加速
3. **学习时间**:系统需要一定时间积累经验才能达到最佳性能
4. **监控建议**:初期建议密切监控Agent决策,确保系统稳定

## 回滚方案

如需回滚到原系统:
1. 停止Agent服务
2. 恢复原 `main.py` 文件
3. 重启后端服务

## 支持

如遇到问题,请查看:
- 日志文件:`logs/agent.log`
- 性能报告:`plots/`目录
- 模型文件:`models/`目录 
