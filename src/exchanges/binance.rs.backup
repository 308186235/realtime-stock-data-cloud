use anyhow::Result;
use crate::models::CryptoPrice;
use crate::exchanges::Exchange;
use tokio::sync::mpsc;
use tokio_tungstenite::{connect_async, tungstenite::Message};
use futures_util::{SinkExt, StreamExt};
use serde_json::{json, Value};
use chrono::Utc;
use tracing::{info, error, warn};

pub struct BinanceExchange;

impl BinanceExchange {
    pub fn new() -> Self {
        Self
    }
}

#[async_trait::async_trait]
impl Exchange for BinanceExchange {
    async fn connect(&self, sender: mpsc::Sender<CryptoPrice>) -> Result<()> {
        let url = "wss://stream.binance.com:9443/ws/btcusdt@ticker/ethusdt@ticker/adausdt@ticker/dotusdt@ticker/bnbusdt@ticker";
        
        info!("Connecting to Binance WebSocket: {}", url);
        
        let (ws_stream, _) = connect_async(url).await?;
        let (mut write, mut read) = ws_stream.split();
        
        info!("Connected to Binance WebSocket");
        
        while let Some(msg) = read.next().await {
            match msg {
                Ok(Message::Text(text)) => {
                    if let Ok(data) = serde_json::from_str::<Value>(&text) {
                        if let Some(price_data) = self.parse_ticker(&data) {
                            if let Err(e) = sender.send(price_data).await {
                                error!("Failed to send Binance price data: {}", e);
                                break;
                            }
                        }
                    }
                }
                Ok(Message::Close(_)) => {
                    warn!("Binance WebSocket connection closed");
                    break;
                }
                Err(e) => {
                    error!("Binance WebSocket error: {}", e);
                    break;
                }
                _ => {}
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
