use anyhow::Result;
use crate::models::CryptoPrice;
use crate::exchanges::Exchange;
use tokio::sync::mpsc;
use tokio_tungstenite::{connect_async, tungstenite::Message};
use futures_util::{SinkExt, StreamExt};
use serde_json::{json, Value};
use chrono::Utc;
use tracing::{info, error, warn};
use std::sync::Arc;

pub struct BinanceExchange;

impl BinanceExchange {
    pub fn new() -> Self {
        Self
    }

    // 🚀 多连接策略：每个交易对独立连接
    async fn connect_symbol(&self, symbol: &str, sender: mpsc::Sender<CryptoPrice>) -> Result<()> {
        let url = format!("wss://stream.binance.com:9443/ws/{}@ticker", symbol.to_lowercase());
        
        info!("🔗 Binance独立连接 {}: {}", symbol, url);

        loop {
            match connect_async(&url).await {
                Ok((ws_stream, _)) => {
                    let (mut write, mut read) = ws_stream.split();
                    info!("✅ Binance {} 连接成功", symbol);

                    while let Some(msg) = read.next().await {
                        match msg {
                            Ok(Message::Text(text)) => {
                                if let Ok(data) = serde_json::from_str::<Value>(&text) {
                                    if let Some(price_data) = self.parse_ticker(&data) {
                                        if let Err(e) = sender.send(price_data).await {
                                            error!("❌ Binance {} 发送数据失败: {}", symbol, e);
                                            break;
                                        }
                                    }
                                }
                            }
                            Ok(Message::Close(_)) => {
                                warn!("⚠️ Binance {} 连接关闭，重连中...", symbol);
                                break;
                            }
                            Err(e) => {
                                error!("❌ Binance {} WebSocket错误: {}", symbol, e);
                                break;
                            }
                            _ => {}
                        }
                    }
                }
                Err(e) => {
                    error!("❌ Binance {} 连接失败: {}，5秒后重试", symbol, e);
                    tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
                }
            }
        }
    }
}

#[async_trait::async_trait]
impl Exchange for BinanceExchange {
    async fn connect(&self, sender: mpsc::Sender<CryptoPrice>) -> Result<()> {
        info!("🚀 启动Binance多连接策略...");
        
        // 🎯 为每个交易对创建独立连接
        let symbols = vec!["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "BNBUSDT"];
        let mut handles = Vec::new();

        for symbol in symbols {
            let sender_clone = sender.clone();
            let symbol_owned = symbol.to_string();
            let exchange_clone = BinanceExchange::new();
            
            let handle = tokio::spawn(async move {
                exchange_clone.connect_symbol(&symbol_owned, sender_clone).await
            });
            
            handles.push(handle);
            info!("🔗 启动Binance {} 独立连接", symbol);
        }

        // 等待所有连接
        for handle in handles {
            if let Err(e) = handle.await {
                error!("❌ Binance连接任务失败: {}", e);
            }
        }

        Ok(())
    }

    fn name(&self) -> &str {
        "Binance"
    }
}

impl BinanceExchange {
    fn parse_ticker(&self, data: &Value) -> Option<CryptoPrice> {
        let symbol = data.get("s")?.as_str()?;
        let price = data.get("c")?.as_str()?.parse::<f64>().ok()?;
        let change_percent = data.get("P")?.as_str()?.parse::<f64>().ok()?;
        let volume = data.get("v")?.as_str()?.parse::<f64>().ok()?;

        let symbol_clean = match symbol {
            "BTCUSDT" => "BTCUSDT",
            "ETHUSDT" => "ETHUSDT",
            "ADAUSDT" => "ADAUSDT",
            "DOTUSDT" => "DOTUSDT",
            "BNBUSDT" => "BNBUSDT",
            _ => return None,
        };

        info!("Binance {} - Price: ${:.2} ({:+.2}%) Volume: {:.0}",
              symbol_clean, price, change_percent, volume);

        Some(CryptoPrice::new(
            symbol_clean.to_string(),
            price,
            change_percent,
            volume,
            "Binance".to_string(),
        ))
    }
}
