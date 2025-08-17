use anyhow::{Result, anyhow};
use crate::models::CryptoPrice;
use crate::exchanges::Exchange;
use tokio::sync::mpsc;
use tokio_tungstenite::{connect_async, tungstenite::Message};
use futures_util::{SinkExt, StreamExt};
use serde_json::{json, Value};
use tracing::{info, error, warn, debug};
use chrono::Utc;

pub struct CoinbaseExchange {
    ws_url: String,
    symbols: Vec<String>,
}

impl CoinbaseExchange {
    pub fn new() -> Self {
        Self {
            ws_url: "wss://ws-feed.exchange.coinbase.com".to_string(),
            symbols: vec![
                "BTC-USD".to_string(),
                "ETH-USD".to_string(),
                "ADA-USD".to_string(),
            ],
        }
    }

    fn parse_ticker_data(&self, data: &Value) -> Result<Option<CryptoPrice>> {
        // Coinbase WebSocket ticker数据格式
        if let Some(msg_type) = data.get("type").and_then(|v| v.as_str()) {
            if msg_type == "ticker" {
                if let (Some(symbol), Some(price_str)) = 
                    (data.get("product_id").and_then(|v| v.as_str()),
                     data.get("price").and_then(|v| v.as_str())) {
                    
                    let price = price_str.parse::<f64>()
                        .map_err(|e| anyhow!("Failed to parse price: {}", e))?;

                    // 获取24小时价格变化
                    let change_24h = if let Some(open_str) = data.get("open_24h").and_then(|v| v.as_str()) {
                        if let Ok(open_price) = open_str.parse::<f64>() {
                            if open_price > 0.0 {
                                ((price - open_price) / open_price) * 100.0
                            } else {
                                0.0
                            }
                        } else {
                            0.0
                        }
                    } else {
                        0.0
                    };

                    // 获取24小时交易量
                    let volume_24h = data.get("volume_24h")
                        .and_then(|v| v.as_str())
                        .and_then(|s| s.parse::<f64>().ok())
                        .unwrap_or(0.0);

                    // 数据验证
                    if price <= 0.0 {
                        warn!("⚠️ Coinbase {}: 价格数据异常 ${}", symbol, price);
                        return Ok(None);
                    }

                    if change_24h.abs() > 50.0 {
                        warn!("⚠️ Coinbase {}: 24h变化异常 {:.2}%", symbol, change_24h);
                    }

                    let crypto_price = CryptoPrice::new(
                        symbol.to_string(),
                        price,
                        if change_24h.abs() > 50.0 { 0.0 } else { change_24h },
                        volume_24h,
                        "coinbase".to_string(),
                    );

                    info!("📊 Coinbase {}: ${:.2} ({:+.2}%) Vol: {:.0}", 
                        symbol, price, crypto_price.change_24h, volume_24h);

                    return Ok(Some(crypto_price));
                }
            }
        }
        Ok(None)
    }
}

#[async_trait::async_trait]
impl Exchange for CoinbaseExchange {
    async fn connect(&self, sender: mpsc::Sender<CryptoPrice>) -> Result<()> {
        info!("🔗 连接Coinbase WebSocket: {}", self.ws_url);

        let (ws_stream, _) = connect_async(&self.ws_url).await
            .map_err(|e| anyhow!("Failed to connect to Coinbase WebSocket: {}", e))?;

        let (mut ws_sender, mut ws_receiver) = ws_stream.split();

        // 订阅ticker数据
        let subscribe_msg = json!({
            "type": "subscribe",
            "product_ids": self.symbols,
            "channels": ["ticker"]
        });

        ws_sender.send(Message::Text(subscribe_msg.to_string())).await
            .map_err(|e| anyhow!("Failed to send subscribe message: {}", e))?;

        info!("✅ Coinbase WebSocket连接成功，已订阅 {} 个交易对", self.symbols.len());

        // 处理消息
        while let Some(msg) = ws_receiver.next().await {
            match msg {
                Ok(Message::Text(text)) => {
                    match serde_json::from_str::<Value>(&text) {
                        Ok(data) => {
                            // 跳过订阅确认消息
                            if let Some(msg_type) = data.get("type").and_then(|v| v.as_str()) {
                                if msg_type == "subscriptions" {
                                    debug!("Coinbase订阅确认: {}", text);
                                    continue;
                                }
                            }

                            // 处理ticker数据
                            match self.parse_ticker_data(&data) {
                                Ok(Some(price)) => {
                                    if let Err(e) = sender.send(price).await {
                                        error!("Failed to send Coinbase price data: {}", e);
                                        break;
                                    }
                                }
                                Ok(None) => {
                                    // 正常情况，可能是其他类型的消息
                                }
                                Err(e) => {
                                    error!("❌ Coinbase数据解析错误: {}", e);
                                }
                            }
                        }
                        Err(e) => {
                            error!("❌ Coinbase JSON解析错误: {}", e);
                        }
                    }
                }
                Ok(Message::Ping(payload)) => {
                    if let Err(e) = ws_sender.send(Message::Pong(payload)).await {
                        error!("Failed to send pong to Coinbase: {}", e);
                        break;
                    }
                }
                Ok(Message::Close(_)) => {
                    warn!("Coinbase WebSocket连接关闭");
                    break;
                }
                Err(e) => {
                    error!("❌ Coinbase WebSocket错误: {}", e);
                    break;
                }
                _ => {}
            }
        }

        warn!("Coinbase WebSocket连接断开");
        Ok(())
    }

    fn name(&self) -> &str {
        "Coinbase"
    }
}
