//! 🚀 超高性能交易所连接模块

pub mod binance;
pub mod bybit;
pub mod okx;
pub mod kraken;
pub mod coinbase;

use anyhow::Result;
use tokio::sync::mpsc;
use flume::Sender;
use crate::models::CryptoPrice;
use async_trait::async_trait;

#[async_trait]
pub trait Exchange {
    async fn connect(&self, sender: mpsc::Sender<CryptoPrice>) -> Result<()>;
    
    /// 🚀 新增：支持高性能flume通道
    async fn connect_flume(&self, sender: Sender<CryptoPrice>) -> Result<()> {
        // 默认实现：创建一个桥接器
        let (tx, mut rx) = mpsc::channel(1000);
        
        // 启动桥接任务
        let sender_clone = sender.clone();
        tokio::spawn(async move {
            while let Some(price) = rx.recv().await {
                if let Err(_) = sender_clone.send_async(price).await {
                    break; // 接收端已关闭
                }
            }
        });
        
        // 使用原有的connect方法
        self.connect(tx).await
    }
    
    fn name(&self) -> &str;
}
