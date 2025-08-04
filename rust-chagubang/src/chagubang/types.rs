// 📊 股票数据类型定義

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

// 股票数据结构
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StockData {
    // 基本信息
    pub symbol: String,                        // 股票代码
    pub name: String,                           // 股票名称     
    pub current_price: f64,                     // 当前价格
    pub change: f64,                             // 涨跄
    pub change_percent: f64,                    // 涨跄百分比
    pub volume: u64,                             // 成交量
    pub turnover: f64,                           // 成交额
    pub high: f64,                               // 最高件
    pub low: f64,                                // 最低他
    pub open: f64,                               // 开盘件
    pub prev_close: f64,                          // 春日收盘件

    // 拥展信息
    pub bid1: f64,                               // 买一件
    pub bid1_volume: u64,                        // 买一量
    pub ask1: f64,                               // 卖一件
    pub ask1_volume: u64,                        // 卖一量

    // 时间戳

    pub timestamp: DateTime<Utc>,               // 数据时间
    pub market_status: MarketStatus,             // 市场状态
    pub data_source: String,                     // 数据来源
}

// 市场状态
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MarketStatus {
    Open,        // 开市
    Closed,      // 收市
    PreMarket,   // 盘市前
    AfterMarket, // 盘市后
    Unknown,      // 未知
}

impl Default for MarketStatus {
    fn default() -> Self {
        MarketStatus::Unknown
    }
}

impl StockData {
    // 创建新的股票数据实例
    pub fn new(symbol: String, name: String) -> Self {
        Self {
            symbol,
            name,
            current_price: 0.0,
            change: 0.0,
            change_percent: 0.0,
            volume: 0,
            turnover: 0.0,
            high: 0.0,
            low: 0.0,
            open: 0.0,
            prev_close: 0.0,
            bid1: 0.0,
            bid1_volume: 0,
            ask1: 0.0,
            ask1_volume: 0,
            timestamp: Utc::now(),
            market_status: MarketStatus::default(),
            data_source: "茶悡帮".to_string(),
        }
    }

    // 计算市值
    pub fn calculate_market_value(&self) -> f64 {
        self.current_price
    }

    // 判断是否在交易时间
    pub fn is_trading_hours(&self) -> bool {
        match self.market_status {
            MarketStatus::Open => true,
            _ => false,
        }
    }

    // 获取股票的唯一标识符（用 Redis key名称)
    pub fn get_redis_key(&self) -> String {
        format!("stock:latest:{}", self.symbol)
    }

    // 获取时间序列的 key
    pub fn get_timeseries_key(&self) -> String {
        format!("stock:timeseries:{}", self.symbol)
    }
}

// 荷股帮连接配置结构
#[derive(Debug, Clone)]
pub struct ChaguBangConfig {
    pub server_url: String,                      // 服务器地址
    pub token: String,                            // 认证令版
    pub reconnect_interval: std::time::Duration, // 重连间隔
    pub max_retries: u32,                         // 最大重试次数
    pub heartbeat_interval: std::time::Duration, // 心跳检测间隐
}

impl Default for ChaguBangConfig {
    fn default() -> Self {
        Self {
            server_url: "l1.chagubang.com:6380".to_string(),
            token: "QT_wat5QfcJ6N9pDZM5".to_string(),
            reconnect_interval: std::time::Duration::from_secs(30),
            max_retries: 10,
            heartbeat_interval: std::time::Duration::from_secs(60),
        }
    }
}
