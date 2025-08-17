# 🚀 超高性能虚拟币实时价格监控系统 v3.0.0

一个基于Rust构建的超高性能虚拟币实时价格监控系统，支持多个主流交易所的实时数据收集、处理和存储。

## ✨ 特性

- 🔥 **超高性能**: SIMD + MessagePack + 无锁结构 + 并行处理
- 📊 **多交易所支持**: Binance, Bybit, OKX, Kraken, Coinbase
- ⚡ **实时数据**: WebSocket连接实时获取价格数据
- 💾 **高效存储**: Redis缓存 + ClickHouse数据库
- 🔧 **高并发**: 多线程处理，支持大量并发连接
- 📈 **数据完整性**: 完整的价格、涨跌幅、成交量数据

## 🏗️ 系统架构

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│   交易所APIs    │───▶│  数据处理器   │───▶│  存储系统   │
│  (WebSocket)    │    │   (Rust)     │    │Redis+ClickH │
└─────────────────┘    └──────────────┘    └─────────────┘
```

## 🚀 快速开始

### 环境要求

- Rust 1.70+
- Redis 6.0+
- ClickHouse 21.0+

### 安装依赖

```bash
# 安装Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 安装Redis
sudo apt install redis-server

# 安装ClickHouse
curl https://clickhouse.com/ | sh
```

### 编译运行

```bash
# 克隆项目
git clone https://github.com/your-username/crypto-monitor-rust.git
cd crypto-monitor-rust

# 编译
cargo build --release

# 运行
./target/release/crypto-monitor-rust
```

## 📊 支持的交易所

| 交易所 | 状态 | 支持币种 |
|--------|------|----------|
| Binance | ✅ | BTC, ETH, ADA, DOT, BNB |
| Bybit | ✅ | BTC, ETH, ADA, DOT, BNB |
| OKX | ✅ | BTC, ETH, ADA, DOT, BNB |
| Kraken | ✅ | BTC, ETH, ADA, DOT |
| Coinbase | ✅ | BTC, ETH, ADA |

## 🔧 配置

系统配置在代码中硬编码，主要参数：

- **批量处理大小**: 2000条
- **工作线程数**: 8个
- **缓冲区大小**: 10000条
- **Redis连接池**: 20个连接

## 📈 性能指标

- **数据处理速度**: 每秒处理数万条价格更新
- **延迟**: 毫秒级数据处理延迟
- **并发连接**: 支持5个交易所同时连接
- **存储效率**: 批量写入优化，高效存储

## 🗄️ 数据存储

### Redis缓存
- 实时价格数据缓存
- 高速读写访问
- MessagePack序列化

### ClickHouse数据库
- 历史数据持久化
- 高性能分析查询
- 时间序列优化

## 📝 日志系统

系统提供详细的日志记录：

```
2025-08-17T06:14:36.399368Z  INFO 🚀 启动超高性能虚拟币实时价格监控系统 v3.0.0
2025-08-17T06:14:36.399458Z  INFO ⚡ 性能优化: SIMD + MessagePack + 无锁结构 + 并行处理
2025-08-17T06:14:36.724106Z  INFO 📊 OKX BNBUSDT - Price: $851.30 (+2.44%) Volume: 7180
```

## 🛠️ 开发

### 项目结构

```
src/
├── exchanges/          # 交易所连接器
│   ├── binance.rs     # Binance交易所
│   ├── bybit.rs       # Bybit交易所
│   ├── okx.rs         # OKX交易所
│   ├── kraken.rs      # Kraken交易所
│   ├── coinbase.rs    # Coinbase交易所
│   └── mod.rs         # 交易所模块定义
├── models/            # 数据模型
├── queue/             # 队列处理
├── storage/           # 存储模块
└── main.rs           # 主程序入口
```

### 添加新交易所

1. 在`src/exchanges/`目录下创建新的交易所文件
2. 实现`Exchange` trait
3. 在`mod.rs`中注册新交易所
4. 在`main.rs`中添加连接逻辑

## 📊 监控指标

系统实时显示以下监控指标：

- 数据接收速度
- 存储性能
- 队列状态
- 连接状态
- 错误统计

## 🔒 安全性

- WebSocket连接自动重连
- 错误处理和恢复
- 数据完整性验证
- 连接池管理

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 联系

如有问题，请提交Issue或联系维护者。

---

⭐ 如果这个项目对你有帮助，请给个Star！
