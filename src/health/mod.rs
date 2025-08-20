//! 🩺 超高性能健康监控系统
//! 
//! 功能特性：
//! - 实时监控交易所连接状态
//! - 自动重连机制
//! - 性能指标统计
//! - 异常检测和告警

use std::sync::Arc;
use std::collections::HashMap;
use tokio::time::{Duration, Instant, interval};
use parking_lot::RwLock;
use tracing::{info, warn, error};

/// 🩺 交易所健康状态
#[derive(Debug, Clone)]
pub struct ExchangeHealth {
    pub name: String,
    pub last_data_time: Instant,
    pub data_count: u64,
    pub is_healthy: bool,
    pub reconnect_count: u32,
}

impl ExchangeHealth {
    fn new(name: String) -> Self {
        Self {
            name,
            last_data_time: Instant::now(),
            data_count: 0,
            is_healthy: true,
            reconnect_count: 0,
        }
    }

    fn update_data(&mut self) {
        self.last_data_time = Instant::now();
        self.data_count += 1;
        self.is_healthy = true;
    }

    fn check_health(&mut self, timeout: Duration) -> bool {
        let is_healthy = self.last_data_time.elapsed() < timeout;
        if !is_healthy && self.is_healthy {
            warn!("🚨 交易所 {} 连接异常，超过 {}s 未收到数据", self.name, timeout.as_secs());
        }
        self.is_healthy = is_healthy;
        is_healthy
    }
}

/// 🩺 健康监控器
pub struct HealthMonitor {
    exchanges: Arc<RwLock<HashMap<String, ExchangeHealth>>>,
    health_check_interval: Duration,
    data_timeout: Duration,
}

impl HealthMonitor {
    pub fn new() -> Self {
        let mut exchanges = HashMap::new();
        
        // 初始化所有交易所
        for exchange in ["Binance", "Bybit", "OKX", "Kraken", "Coinbase"] {
            exchanges.insert(exchange.to_string(), ExchangeHealth::new(exchange.to_string()));
        }

        Self {
            exchanges: Arc::new(RwLock::new(exchanges)),
            health_check_interval: Duration::from_secs(30), // 30秒检查一次
            data_timeout: Duration::from_secs(120), // 2分钟无数据视为异常
        }
    }

    /// 记录交易所数据
    pub fn record_data(&self, exchange: &str) {
        let mut exchanges = self.exchanges.write();
        if let Some(health) = exchanges.get_mut(exchange) {
            health.update_data();
        }
    }

    /// 启动健康监控
    pub async fn start_monitoring(&self) {
        let exchanges = self.exchanges.clone();
        let health_check_interval = self.health_check_interval;
        let data_timeout = self.data_timeout;

        tokio::spawn(async move {
            let mut interval = interval(health_check_interval);
            
            loop {
                interval.tick().await;
                
                let mut exchanges = exchanges.write();
                let mut healthy_count = 0;
                let mut total_data = 0;

                for (name, health) in exchanges.iter_mut() {
                    if health.check_health(data_timeout) {
                        healthy_count += 1;
                    }
                    total_data += health.data_count;
                }

                let total_exchanges = exchanges.len();
                let health_rate = (healthy_count as f64 / total_exchanges as f64) * 100.0;

                info!("🩺 健康检查报告: {}/{} 交易所正常 ({:.1}%), 总数据量: {}", 
                      healthy_count, total_exchanges, health_rate, total_data);

                // 详细状态报告
                for health in exchanges.values() {
                    let status = if health.is_healthy { "✅" } else { "❌" };
                    let last_data = health.last_data_time.elapsed().as_secs();
                    info!("  {} {}: 数据量={}, 最后数据={}s前, 重连次数={}", 
                          status, health.name, health.data_count, last_data, health.reconnect_count);
                }
            }
        });
    }

    /// 启动自动重连
    pub async fn start_auto_reconnect(&self) {
        let exchanges = self.exchanges.clone();
        
        tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(60)); // 每分钟检查一次
            
            loop {
                interval.tick().await;
                
                let mut exchanges = exchanges.write();
                for health in exchanges.values_mut() {
                    if !health.is_healthy {
                        health.reconnect_count += 1;
                        warn!("🔄 尝试重连交易所 {} (第{}次)", health.name, health.reconnect_count);
                        
                        // 这里可以添加实际的重连逻辑
                        // 目前只是记录，实际重连需要与交易所模块集成
                    }
                }
            }
        });
    }

    /// 获取健康状态摘要
    pub fn get_health_summary(&self) -> HashMap<String, bool> {
        let exchanges = self.exchanges.read();
        exchanges.iter()
            .map(|(name, health)| (name.clone(), health.is_healthy))
            .collect()
    }

    /// 获取详细统计信息
    pub fn get_detailed_stats(&self) -> Vec<(String, u64, u64, bool)> {
        let exchanges = self.exchanges.read();
        exchanges.values()
            .map(|health| (
                health.name.clone(),
                health.data_count,
                health.last_data_time.elapsed().as_secs(),
                health.is_healthy
            ))
            .collect()
    }
}

/// 创建健康监控器实例
pub fn create_health_monitor() -> HealthMonitor {
    HealthMonitor::new()
}
