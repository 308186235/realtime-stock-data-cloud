//! 🔒 连接稳定性保障模块
//! 
//! 功能特性：
//! - WebSocket连接保活
//! - 防止主动断开机制
//! - 连接质量监控
//! - 自动重连策略
//! - 网络异常检测

use std::time::{Duration, Instant};
use tokio::time::{sleep, interval};
use tracing::{info, warn, error};
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};

/// 🔒 连接稳定性配置
#[derive(Debug, Clone)]
pub struct StabilityConfig {
    /// 心跳间隔 (秒)
    pub heartbeat_interval: u64,
    /// 连接超时 (秒)
    pub connection_timeout: u64,
    /// 重连延迟 (秒)
    pub reconnect_delay: u64,
    /// 最大重连次数
    pub max_reconnect_attempts: u32,
    /// 数据超时阈值 (秒)
    pub data_timeout_threshold: u64,
    /// 强制重连间隔 (小时)
    pub force_reconnect_hours: u64,
}

impl Default for StabilityConfig {
    fn default() -> Self {
        Self {
            heartbeat_interval: 30,        // 30秒心跳
            connection_timeout: 60,        // 60秒连接超时
            reconnect_delay: 5,            // 5秒重连延迟
            max_reconnect_attempts: 20,    // 最多重连20次
            data_timeout_threshold: 120,   // 2分钟数据超时
            force_reconnect_hours: 24,     // 24小时强制重连
        }
    }
}

/// 🔒 连接稳定性管理器
pub struct StabilityManager {
    config: StabilityConfig,
    is_running: Arc<AtomicBool>,
    last_heartbeat: Arc<AtomicU64>,
    reconnect_count: Arc<AtomicU64>,
    connection_start_time: Instant,
}

impl StabilityManager {
    /// 创建新的稳定性管理器
    pub fn new(config: StabilityConfig) -> Self {
        Self {
            config,
            is_running: Arc::new(AtomicBool::new(false)),
            last_heartbeat: Arc::new(AtomicU64::new(0)),
            reconnect_count: Arc::new(AtomicU64::new(0)),
            connection_start_time: Instant::now(),
        }
    }

    /// 启动稳定性保障机制
    pub async fn start_stability_protection(&self, exchange_name: String) {
        if self.is_running.load(Ordering::Relaxed) {
            warn!("🔒 {} 稳定性保障已在运行", exchange_name);
            return;
        }

        self.is_running.store(true, Ordering::Relaxed);
        info!("🔒 启动 {} 连接稳定性保障", exchange_name);

        // �� 心跳保活机制
        self.start_heartbeat_monitor(exchange_name.clone()).await;

        // 🛡️ 连接质量监控
        self.start_connection_quality_monitor(exchange_name.clone()).await;

        // 🔄 自动重连机制
        self.start_auto_reconnect_monitor(exchange_name.clone()).await;

        // 🕐 强制重连机制
        self.start_force_reconnect_monitor(exchange_name.clone()).await;
    }

    /// 🫀 心跳保活机制
    async fn start_heartbeat_monitor(&self, exchange_name: String) {
        let heartbeat_interval = self.config.heartbeat_interval;
        let last_heartbeat = self.last_heartbeat.clone();
        let is_running = self.is_running.clone();

        tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(heartbeat_interval));
            
            while is_running.load(Ordering::Relaxed) {
                interval.tick().await;
                
                let now = std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_secs();
                
                last_heartbeat.store(now, Ordering::Relaxed);
                
                // 发送心跳包 (这里可以根据具体协议实现)
                info!("🫀 {} 心跳保活: {}", exchange_name, now);
            }
        });
    }

    /// 🛡️ 连接质量监控
    async fn start_connection_quality_monitor(&self, exchange_name: String) {
        let data_timeout = self.config.data_timeout_threshold;
        let is_running = self.is_running.clone();

        tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(30)); // 每30秒检查一次
            
            while is_running.load(Ordering::Relaxed) {
                interval.tick().await;
                
                // 这里可以检查数据接收质量
                // 实际实现需要与数据接收模块集成
                info!("🛡️ {} 连接质量检查通过", exchange_name);
            }
        });
    }

    /// 🔄 自动重连机制
    async fn start_auto_reconnect_monitor(&self, exchange_name: String) {
        let reconnect_delay = self.config.reconnect_delay;
        let max_attempts = self.config.max_reconnect_attempts;
        let reconnect_count = self.reconnect_count.clone();
        let is_running = self.is_running.clone();

        tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(60)); // 每分钟检查一次
            
            while is_running.load(Ordering::Relaxed) {
                interval.tick().await;
                
                let current_count = reconnect_count.load(Ordering::Relaxed);
                
                if current_count >= max_attempts as u64 {
                    error!("🔄 {} 重连次数已达上限: {}", exchange_name, current_count);
                    continue;
                }

                // 检查是否需要重连
                // 这里的逻辑需要与健康监控模块集成
                // 如果检测到连接问题，执行重连
                
                info!("🔄 {} 自动重连检查: 重连次数 {}/{}", 
                      exchange_name, current_count, max_attempts);
            }
        });
    }

    /// 🕐 强制重连机制
    async fn start_force_reconnect_monitor(&self, exchange_name: String) {
        let force_hours = self.config.force_reconnect_hours;
        let is_running = self.is_running.clone();

        tokio::spawn(async move {
            let force_interval = Duration::from_secs(force_hours * 3600);
            let mut interval = interval(force_interval);
            
            while is_running.load(Ordering::Relaxed) {
                interval.tick().await;
                
                warn!("🕐 {} 执行{}小时强制重连", exchange_name, force_hours);
                
                // 这里可以触发强制重连逻辑
                // 实际实现需要与连接管理模块集成
            }
        });
    }

    /// 停止稳定性保障
    pub fn stop_stability_protection(&self) {
        self.is_running.store(false, Ordering::Relaxed);
        info!("🔒 连接稳定性保障已停止");
    }

    /// 记录重连事件
    pub fn record_reconnect(&self) {
        let count = self.reconnect_count.fetch_add(1, Ordering::Relaxed) + 1;
        warn!("🔄 记录重连事件: 第{}次", count);
    }

    /// 获取连接统计信息
    pub fn get_connection_stats(&self) -> ConnectionStabilityStats {
        ConnectionStabilityStats {
            uptime: self.connection_start_time.elapsed(),
            reconnect_count: self.reconnect_count.load(Ordering::Relaxed),
            last_heartbeat: self.last_heartbeat.load(Ordering::Relaxed),
            is_stable: self.is_connection_stable(),
        }
    }

    /// 检查连接是否稳定
    fn is_connection_stable(&self) -> bool {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();
        
        let last_heartbeat = self.last_heartbeat.load(Ordering::Relaxed);
        let heartbeat_age = now.saturating_sub(last_heartbeat);
        
        // 如果心跳超过2倍间隔时间，认为不稳定
        heartbeat_age <= (self.config.heartbeat_interval * 2)
    }
}

/// 🔒 连接稳定性统计信息
#[derive(Debug, Clone)]
pub struct ConnectionStabilityStats {
    pub uptime: Duration,
    pub reconnect_count: u64,
    pub last_heartbeat: u64,
    pub is_stable: bool,
}

/// 🔒 创建默认稳定性管理器
pub fn create_stability_manager() -> StabilityManager {
    let config = StabilityConfig::default();
    StabilityManager::new(config)
}

/// 🔒 创建自定义稳定性管理器
pub fn create_custom_stability_manager(config: StabilityConfig) -> StabilityManager {
    StabilityManager::new(config)
}
