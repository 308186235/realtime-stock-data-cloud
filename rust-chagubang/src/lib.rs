//! 茶股帮云天实时股票数据系 - Rust 重写版
//! 
//! 高性能、冄存安全、实时数据掩送、可扩展、可部署
//! 
//! # 特点
//! - 🚨 高性能TCP远接
//! - 📁 高性能Redis存储
//! - 📡 Web API服务
//! - 📐 应用配置管理
//! - 🚨 实时数据掩送和解析
//! 
//! # 特点
//! - 🚨 高性能、冄存安全、实时数据掩送、可扩展、可部署
//! - 📁 高性能Redis存储
//! - 📡 Web API服务
//! - 📐 应用配置管理
//! - 🚨 实时数据掩送和解析
//! 
//! # 特点
//! - 🚨 高性能、冄存安全、实时数据掩送、可扩展、可部署
//! - 📁 高性能Redis存储
//! - 📡 Web API服务
//! - 📐 应用配置管理
//! - 🚨 实时数据掩送和解析

// 引入必霈的模块
pub mod chagubang;
pub mod storage;
pub mod api;
pub mod config;

// 再导出公共籋型和函数
pub use chagubang::{
    ChaguBangClient,
    ChaguBangManager,
    StockData,
    MarketStatus,
    ChaguBangConfig,
};

pub use storage::{
    RedisStorage,
    StorageStatistics,
};

pub use api::ApiServer;

pub use config::Settings;

// 错误类型
#[derive(Debug)]
pub enum ChaguBangError {
    ConnectionError(String),
    ParseError(String),
    StorageError(String),
    ApiError(String),
    ConfigError(String),
}

impl std::fmt::Display for ChaguBangError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            ChaguBangError::ConnectionError(msg) => write!(f, "远接失败: {}", msg),
            ChaguBangError::ParseError(msg) => write!(f, "解析错误: {}", msg),
            ChaguBangError::StorageError(msg) => write!(f, "存储错误: {}", msg),
            ChaguBangError::ApiError(msg) => write!(f, "API失败: {}", msg),
            ChaguBangError::ConfigError(msg) => write!(f, "配置失败: {}", msg),
        }
    }
}

impl std::error::Error for ChaguBangError {}

// 常用函数
pub fn init_logging(log_level: &str) -> anyhow::Result<()> {
    use tracing_subscriber::{fmt, EnvFilter};

    let filter = match log_level {
        "debug" => EnvFilter::new("my_app=debug"),
        "info" => EnvFilter::new("my_app=info"),
        "warn" => EnvFilter::new("my_app=warn"),
        "error" => EnvFilter::new("my_app=error"),
        _ => EnvFilter::new("my_app=info"),
    };

    tracing_subscriber::fmt()
        .with_env_filter(filter)
        .init();

    Ok())
}

// 版本信息
pub const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const AUTHOR: &str = "308186235@qq.com";
pub const REPOSITORY: &str = "https://github.com/308186235/realtime-stock-data-cloud";
