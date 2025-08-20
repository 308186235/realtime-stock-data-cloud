use anyhow::{Result, anyhow};
use crate::models::CryptoPrice;
use crate::exchanges::Exchange;
use tokio::sync::mpsc;
use tokio_tungstenite::{connect_async, tungstenite::Message};
use futures_util::{SinkExt, StreamExt};
use serde_json::{json, Value};
use tracing::{info, error, warn, debug};
use chrono::Utc;

pub struct KrakenExchange {
    ws_url: String,
    symbols: Vec<String>,
}

impl KrakenExchange {
    pub fn new() -> Self {
        Self {
            ws_url: "wss://ws.kraken.com/".to_string(),
            symbols: vec![
                "BTC/USD".to_string(),
                "ETH/USD".to_string(),
                "ADA/USD".to_string(),
                "DOT/USD".to_string(),
            ],
        }
    }

    fn parse_ticker_data(&self, data: &Value) -> Result<Option<CryptoPrice>> {
        // Kraken WebSocket ticker数据格式: [channelID, data, channelName, pair]
        if let Some(array) = data.as_array() {
            if array.len() >= 4 {
                if let (Some(ticker_data), Some(channel_name), Some(symbol)) =
                    (array[1].as_object(), array[2].as_str(), array[3].as_str()) {

                    if channel_name == "ticker" {
                        // 获取最新价格 (c: [price, lot_volume])
                        if let Some(close_data) = ticker_data.get("c").and_then(|v| v.as_array()) {
                            if let Some(price_str) = close_data.get(0).and_then(|v| v.as_str()) {
                                let price = price_str.parse::<f64>()
                                    .map_err(|e| anyhow!("Failed to parse price: {}", e))?;

                                // 获取24小时交易量 (v: [today, 24hr])
                                let volume_24h = ticker_data.get("v")
                                    .and_then(|v| v.as_array())
                                    .and_then(|arr| arr.get(1))
                                    .and_then(|v| v.as_str())
                                    .and_then(|s| s.parse::<f64>().ok())
                                    .unwrap_or(0.0);

                                // 计算24小时价格变化 (o: opening price)
                                let change_24h = if let Some(open_str) = ticker_data.get("o").and_then(|v| v.as_str()) {
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

                                // 数据验证
                                if price <= 0.0 {
                                    warn!("⚠️ Kraken {}: 价格数据异常 ${}", symbol, price);
                                    return Ok(None);
                                }

                                if change_24h.abs() > 50.0 {
                                    warn!("⚠️ Kraken {}: 24h变化异常 {:.2}%", symbol, change_24h);
                                }

                                let crypto_price = CryptoPrice::new(
                                    symbol.to_string(),
                                    price,
                                    change_24h,
                                    volume_24h,
                                    "Kraken".to_string(),
                                );

                                info!("📊 Kraken {}: ${:.2} ({:+.2}%) Vol: {:.0}",
                                    symbol, price, crypto_price.change_24h, volume_24h);

                                return Ok(Some(crypto_price));
                            }
                        }
                    }
                }
            }
        }
        Ok(None)
    }
}

#[async_trait::async_trait]
impl Exchange for KrakenExchange {
    async fn connect(&self, sender: mpsc::Sender<CryptoPrice>) -> Result<()> {
        info!("🔗 连接Kraken WebSocket: {}", self.ws_url);

        // 🚀 添加重连逻辑
        loop {
            match self.connect_with_retry(&sender).await {
                Ok(_) => {
                    warn!("⚠️ Kraken连接正常结束，5秒后重连...");
                }
                Err(e) => {
                    error!("❌ Kraken连接失败: {}，5秒后重试", e);
                }
            }
            tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
        }
    }

    fn name(&self) -> &str {
        "Kraken"
    }
}

impl KrakenExchange {
    async fn connect_with_retry(&self, sender: &mpsc::Sender<CryptoPrice>) -> Result<()> {
        let (ws_stream, _) = connect_async(&self.ws_url).await
            .map_err(|e| anyhow!("Failed to connect to Kraken WebSocket: {}", e))?;

        let (mut ws_sender, mut ws_receiver) = ws_stream.split();

        // 🚀 优化订阅消息 - 订阅更高频的数据流
        let subscribe_msg = json!({
            "event": "subscribe",
            "pair": self.symbols,
            "subscription": {
                "name": "ticker"
            }
        });

        ws_sender.send(Message::Text(subscribe_msg.to_string())).await
            .map_err(|e| anyhow!("Failed to send subscribe message: {}", e))?;

        info!("✅ Kraken WebSocket连接成功，已订阅 {} 个交易对", self.symbols.len());

        // 🚀 添加心跳计时器
        let mut last_heartbeat = tokio::time::Instant::now();
        let heartbeat_interval = tokio::time::Duration::from_secs(30);

        // 处理消息
        while let Some(msg) = ws_receiver.next().await {
            match msg {
                Ok(Message::Text(text)) => {
                    // 更新心跳时间
                    last_heartbeat = tokio::time::Instant::now();

                    match serde_json::from_str::<Value>(&text) {
                        Ok(data) => {
                            // 跳过订阅确认消息
                            if let Some(event) = data.get("event").and_then(|v| v.as_str()) {
                                if event == "subscriptionStatus" {
                                    info!("📡 Kraken订阅确认: {}", text);
                                    continue;
                                }
                                if event == "systemStatus" {
                                    info!("📡 Kraken系统状态: {}", text);
                                    continue;
                                }
                                if event == "heartbeat" {
                                    debug!("💓 Kraken心跳: {}", text);
                                    continue;
                                }
                            }

                            // 处理ticker数据
                            match self.parse_ticker_data(&data) {
                                Ok(Some(price)) => {
                                    if let Err(e) = sender.send(price).await {
                                        error!("Failed to send Kraken price data: {}", e);
                                        break;
                                    }
                                }
                                Ok(None) => {
                                    // 正常情况，可能是其他类型的消息
                                }
                                Err(e) => {
                                    error!("❌ Kraken数据解析错误: {}", e);
                                }
                            }
                        }
                        Err(e) => {
                            error!("❌ Kraken JSON解析错误: {}", e);
                        }
                    }
                }
                Ok(Message::Ping(payload)) => {
                    // 🚀 处理ping消息
                    if let Err(e) = ws_sender.send(Message::Pong(payload)).await {
                        error!("Failed to send pong to Kraken: {}", e);
                        break;
                    }
                    debug!("💓 Kraken Ping/Pong处理成功");
                }
                Ok(Message::Close(_)) => {
                    warn!("⚠️ Kraken WebSocket连接关闭");
                    break;
                }
                Err(e) => {
                    error!("❌ Kraken WebSocket错误: {}", e);
                    break;
                }
                _ => {}
            }

            // 🚀 检查心跳超时
            if last_heartbeat.elapsed() > heartbeat_interval * 2 {
                warn!("⚠️ Kraken心跳超时，重新连接...");
                break;
            }
        }

        warn!("Kraken WebSocket连接断开");
        Ok(())
    }
}
