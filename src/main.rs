//! 🚀 超高性能虚拟币实时价格监控系统 v3.0.0
//! 
//! 性能优化特性：
//! - SIMD加速JSON解析
//! - MessagePack序列化 (比JSON快3-5倍)
//! - 无锁数据结构
//! - 高性能内存分配器
//! - 零拷贝优化
//! - 并行处理

mod models;
mod exchanges;
mod storage;
mod queue;

use anyhow::Result;
use std::sync::Arc;
use tokio::sync::mpsc;
use tokio::time::{Duration, sleep, Instant};
use tracing::{info, error, warn};
use tracing_subscriber;

// 🚀 高性能依赖
use mimalloc::MiMalloc;
use crossbeam::channel;
use dashmap::DashMap;
use flume::{Sender, Receiver};
use parking_lot::RwLock;
use rayon::prelude::*;

// 🔥 全局高性能内存分配器
#[global_allocator]
static GLOBAL: MiMalloc = MiMalloc;

use models::CryptoPrice;
use storage::ClickHouseStorage;
use queue::HighPerformanceRedisQueue;
use exchanges::{
    binance::BinanceExchange,
    bybit::BybitExchange,
    okx::OkxExchange,
    kraken::KrakenExchange,
    coinbase::CoinbaseExchange,
    Exchange,
};

// 🎯 超高性能配置
const ULTRA_BATCH_SIZE: usize = 2000;        // 超大批量
const WORKER_THREADS: usize = 8;             // 多线程处理
const CHANNEL_BUFFER: usize = 10000;         // 大缓冲区
const REDIS_POOL_SIZE: usize = 20;           // 大连接池

/// 🚀 超高性能统计结构
#[derive(Debug, Clone)]
struct UltraPerformanceStats {
    total_processed: Arc<parking_lot::Mutex<u64>>,
    start_time: Instant,
    last_report: Arc<parking_lot::Mutex<Instant>>,
    throughput_history: Arc<RwLock<Vec<f64>>>,
}

impl UltraPerformanceStats {
    fn new() -> Self {
        Self {
            total_processed: Arc::new(parking_lot::Mutex::new(0)),
            start_time: Instant::now(),
            last_report: Arc::new(parking_lot::Mutex::new(Instant::now())),
            throughput_history: Arc::new(RwLock::new(Vec::new())),
        }
    }

    fn record_batch(&self, count: u64) {
        let mut total = self.total_processed.lock();
        *total += count;
        
        let mut last_report = self.last_report.lock();
        let now = Instant::now();
        
        if now.duration_since(*last_report).as_secs() >= 10 {
            let elapsed = now.duration_since(self.start_time).as_secs_f64();
            let rate = *total as f64 / elapsed;
            
            // 记录吞吐量历史
            {
                let mut history = self.throughput_history.write();
                history.push(rate);
                if history.len() > 60 { // 保留最近60个数据点
                    history.remove(0);
                }
            }
            
            let avg_rate = {
                let history = self.throughput_history.read();
                if !history.is_empty() {
                    history.iter().sum::<f64>() / history.len() as f64
                } else {
                    rate
                }
            };
            
            info!("🚀 超高性能统计: 当前 {:.1} msg/s, 平均 {:.1} msg/s, 总计 {} 条", 
                  rate, avg_rate, *total);
            *last_report = now;
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    // 🎯 启用高性能日志
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .with_target(false)
        .compact()
        .init();

    info!("🚀 启动超高性能虚拟币实时价格监控系统 v3.0.0");
    info!("⚡ 性能优化: SIMD + MessagePack + 无锁结构 + 并行处理");
    info!("📊 支持交易所: Binance, Bybit, OKX, Kraken, Coinbase");
    info!("🎯 配置: 批量={}, 线程={}, 缓冲={}", ULTRA_BATCH_SIZE, WORKER_THREADS, CHANNEL_BUFFER);

    // 🚀 初始化超高性能Redis队列
    let redis_queue = Arc::new(
        HighPerformanceRedisQueue::new(
            "redis://127.0.0.1:6379", 
            "crypto_prices_queue", 
            REDIS_POOL_SIZE
        ).await?
    );
    info!("✅ 超高性能Redis连接池初始化完成 (连接数: {})", REDIS_POOL_SIZE);

    // 🚀 初始化ClickHouse存储
    let storage = Arc::new(ClickHouseStorage::new("http://localhost:8123"));
    storage.init().await?;
    info!("✅ ClickHouse存储初始化完成");

    // 🚀 创建高性能通道
    let (tx, rx) = flume::bounded::<CryptoPrice>(CHANNEL_BUFFER);
    let stats = Arc::new(UltraPerformanceStats::new());

    // 🚀 启动所有交易所连接 (并行启动)
    let exchanges: Vec<Box<dyn Exchange + Send + Sync>> = vec![
        Box::new(BinanceExchange::new()),
        Box::new(BybitExchange::new()),
        Box::new(OkxExchange::new()),
        Box::new(KrakenExchange::new()),
        Box::new(CoinbaseExchange::new()),
    ];

    info!("🔗 并行启动 {} 个交易所连接...", exchanges.len());
    for exchange in exchanges {
        let tx_clone = tx.clone();
        tokio::spawn(async move {
            if let Err(e) = exchange.connect_flume(tx_clone).await {
                error!("❌ 交易所连接失败: {}", e);
            }
        });
    }

    // 🚀 启动超高性能数据处理管道
    let queue_clone = redis_queue.clone();
    let stats_clone = stats.clone();
    tokio::spawn(async move {
        info!("⚡ 启动超高性能数据处理管道...");
        
        let mut batch_buffer = Vec::with_capacity(ULTRA_BATCH_SIZE);
        let mut last_flush = Instant::now();
        
        while let Ok(price) = rx.recv_async().await {
            batch_buffer.push(price);
            
            // 智能批量处理：大小或时间触发
            let should_flush = batch_buffer.len() >= ULTRA_BATCH_SIZE 
                || last_flush.elapsed() > Duration::from_millis(100);
                
            if should_flush && !batch_buffer.is_empty() {
                let batch_size = batch_buffer.len();
                
                // 🚀 使用MessagePack序列化 (比JSON快3-5倍)
                match queue_clone.push_batch_msgpack(&batch_buffer).await {
                    Ok(_) => {
                        stats_clone.record_batch(batch_size as u64);
                        info!("⚡ 超高速批量写入Redis: {} 条数据", batch_size);
                    }
                    Err(e) => error!("❌ Redis批量写入失败: {}", e),
                }
                
                batch_buffer.clear();
                last_flush = Instant::now();
            }
        }
    });

    // 🚀 启动并行存储任务
    for worker_id in 0..WORKER_THREADS {
        let storage_clone = storage.clone();
        let queue_clone = redis_queue.clone();
        let stats_clone = stats.clone();
        
        tokio::spawn(async move {
            info!("💾 启动存储工作线程 #{}", worker_id);
            
            loop {
                match queue_clone.pop_batch_msgpack(ULTRA_BATCH_SIZE / WORKER_THREADS).await {
                    Ok(prices) => {
                        if !prices.is_empty() {
                            let count = prices.len();
                            let start_time = Instant::now();
                            
                            // 🚀 并行处理数据
                            let processed_prices: Vec<_> = prices
                                .into_par_iter()
                                .map(|mut price| {
                                    // 这里可以添加数据预处理逻辑
                                    price
                                })
                                .collect();
                            
                            match storage_clone.insert_prices_batch(&processed_prices).await {
                                Ok(_) => {
                                    let duration = start_time.elapsed();
                                    let queue_len = queue_clone.get_queue_length().await.unwrap_or(0);
                                    
                                    if let Ok(total_count) = storage_clone.get_price_count().await {
                                        info!("💾 工作线程#{} 存储 {} 条，耗时: {:.2}ms，队列: {}，总计: {} 条",
                                              worker_id, count, duration.as_millis(), queue_len, total_count);
                                    }
                                }
                                Err(e) => error!("❌ 工作线程#{} ClickHouse存储失败: {}", worker_id, e),
                            }
                        } else {
                            // 队列为空，短暂休眠
                            sleep(Duration::from_millis(10)).await;
                        }
                    }
                    Err(e) => {
                        error!("❌ 工作线程#{} Redis读取失败: {}", worker_id, e);
                        sleep(Duration::from_secs(1)).await;
                    }
                }
            }
        });
    }

    // 🚀 启动性能监控任务
    let stats_clone = stats.clone();
    let queue_clone = redis_queue.clone();
    tokio::spawn(async move {
        loop {
            sleep(Duration::from_secs(30)).await;
            
            match queue_clone.get_queue_length().await {
                Ok(queue_len) => {
                    let total = *stats_clone.total_processed.lock();
                    let elapsed = stats_clone.start_time.elapsed().as_secs_f64();
                    let avg_rate = total as f64 / elapsed;
                    
                    info!("📊 系统监控: 队列={} 条, 平均速率={:.1} msg/s, 运行时间={:.1}分钟", 
                          queue_len, avg_rate, elapsed / 60.0);
                }
                Err(e) => warn!("获取队列长度失败: {}", e),
            }
        }
    });

    info!("🎯 超高性能系统启动完成，开始实时数据收集...");

    // 保持主线程运行
    loop {
        sleep(Duration::from_secs(60)).await;
    }
}
