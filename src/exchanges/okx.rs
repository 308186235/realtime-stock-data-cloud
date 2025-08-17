use anyhow::Result;
use crate::models::CryptoPrice;
use crate::exchanges::Exchange;
use tokio::sync::mpsc;
use tokio_tungstenite::{connect_async, tungstenite::Message};
use futures_util::{SinkExt, StreamExt};
use serde_json::{json, Value};
use tracing::{info, error, warn};

pub struct OkxExchange;

impl OkxExchange {
    pub fn new() -> Self {
        Self
    }
}

#[async_trait::async_trait]
impl Exchange for OkxExchange {
    async fn connect(&self, sender: mpsc::Sender<CryptoPrice>) -> Result<()> {
        let url = "wss://ws.okx.com:8443/ws/v5/public";

        info!("🔗 连接到OKX WebSocket: {}", url);

        let (ws_stream, _) = connect_async(url).await?;
        let (mut write, mut read) = ws_stream.split();

        // 订阅ticker数据
        let subscribe_msg = json!({
            "op": "subscribe",
            "args": [
                {"channel": "tickers", "instId": "BTC-USDT"},
                {"channel": "tickers", "instId": "ETH-USDT"},
                {"channel": "tickers", "instId": "ADA-USDT"},
                {"channel": "tickers", "instId": "DOT-USDT"},
                {"channel": "tickers", "instId": "BNB-USDT"}
            ]
        });

        write.send(Message::Text(subscribe_msg.to_string())).await?;
        info!("✅ OKX WebSocket连接成功，已订阅ticker数据");

        while let Some(msg) = read.next().await {
            match msg {
                Ok(Message::Text(text)) => {
                    // 🔧 处理订阅确认消息
                    if text.contains("\"event\":\"subscribe\"") {
                        info!("📡 OKX订阅确认: {}", text);
                        continue;
                    }

                    if let Ok(data) = serde_json::from_str::<Value>(&text) {
                        if let Some(price_data) = self.parse_ticker(&data) {
                            if let Err(e) = sender.send(price_data).await {
                                error!("❌ OKX数据发送失败: {}", e);
                                break;
                            }
                        }
                    }
                }
                Ok(Message::Ping(payload)) => {
                    // 🔧 处理ping消息
                    if let Err(e) = write.send(Message::Pong(payload)).await {
                        error!("❌ OKX Pong发送失败: {}", e);
                        break;
                    }
                }
                Ok(Message::Close(_)) => {
                    warn!("⚠️ OKX WebSocket连接关闭");
                    break;
                }
                Err(e) => {
                    error!("❌ OKX WebSocket错误: {}", e);
                    break;
                }
                _ => {}
            }
        }

        Ok(())
    }

    fn name(&self) -> &str {
        "OKX"
    }
}

impl OkxExchange {
    fn parse_ticker(&self, data: &Value) -> Option<CryptoPrice> {
        // 🔧 修复：正确解析OKX数据格式
        // OKX数据格式: {"arg":{"channel":"tickers","instId":"BTC-USDT"},"data":[{...}]}
        if let Some(data_array) = data.get("data").and_then(|d| d.as_array()) {
            if data_array.is_empty() {
                return None;
            }

            let ticker = &data_array[0];
            let inst_id = ticker.get("instId")?.as_str()?;
            let price = ticker.get("last")?.as_str()?.parse::<f64>().ok()?;
            
            // 🔧 修复：OKX使用open24h字段计算百分比变化
            let open24h = ticker.get("open24h")?.as_str()?.parse::<f64>().ok()?;
            let change_percent = if open24h > 0.0 {
                ((price - open24h) / open24h) * 100.0
            } else {
                0.0
            };
            
            let volume = ticker.get("vol24h")?.as_str()?.parse::<f64>().ok()?;

            let symbol_clean = match inst_id {
                "BTC-USDT" => "BTCUSDT",
                "ETH-USDT" => "ETHUSDT", 
                "ADA-USDT" => "ADAUSDT",
                "DOT-USDT" => "DOTUSDT",
                "BNB-USDT" => "BNBUSDT",
                _ => return None,
            };

            info!("📊 OKX {} - Price: ${:.2} ({:+.2}%) Volume: {:.0}",
                  symbol_clean, price, change_percent, volume);

            Some(CryptoPrice::new(
                symbol_clean.to_string(),
                price,
                change_percent,
                volume,
                "OKX".to_string(),
            ))
        } else {
            None
        }
    }
}
