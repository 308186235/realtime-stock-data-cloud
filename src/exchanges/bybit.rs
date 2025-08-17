use super::Exchange;
use crate::models::{CryptoPrice, BybitResponse};
use anyhow::Result;
use futures_util::{SinkExt, StreamExt};
use serde_json::json;
use tokio::sync::mpsc;
use tokio_tungstenite::{connect_async, tungstenite::Message};
use tracing::{info, error, warn};
use url::Url;

pub struct BybitExchange {
    symbols: Vec<String>,
}

impl BybitExchange {
    pub fn new() -> Self {
        Self {
            symbols: vec![
                "BTCUSDT".to_string(),
                "ETHUSDT".to_string(),
                "ADAUSDT".to_string(),
                "DOTUSDT".to_string(),
                "BNBUSDT".to_string(),
            ],
        }
    }
}

#[async_trait::async_trait]
impl Exchange for BybitExchange {
    async fn connect(&self, sender: mpsc::Sender<CryptoPrice>) -> Result<()> {
        let url = Url::parse("wss://stream.bybit.com/v5/public/spot")?;

        loop {
            match self.connect_websocket(&url, &sender).await {
                Ok(_) => {
                    warn!("Bybit WebSocket connection closed, reconnecting...");
                }
                Err(e) => {
                    error!("Bybit WebSocket error: {}, reconnecting in 5 seconds...", e);
                    tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
                }
            }
        }
    }

    fn name(&self) -> &str {
        "Bybit"
    }
}

impl BybitExchange {
    async fn connect_websocket(&self, url: &Url, sender: &mpsc::Sender<CryptoPrice>) -> Result<()> {
        info!("Connecting to Bybit WebSocket: {}", url);

        let (ws_stream, _) = connect_async(url).await?;
        let (mut write, mut read) = ws_stream.split();

        for symbol in &self.symbols {
            let subscribe_msg = json!({
                "op": "subscribe",
                "args": [format!("tickers.{}", symbol)]
            });

            write.send(Message::Text(subscribe_msg.to_string())).await?;
            info!("Subscribed to Bybit ticker for {}", symbol);
        }

        while let Some(msg) = read.next().await {
            match msg? {
                Message::Text(text) => {
                    if let Err(e) = self.handle_message(&text, sender).await {
                        error!("Error handling Bybit message: {}", e);
                    }
                }
                Message::Ping(payload) => {
                    write.send(Message::Pong(payload)).await?;
                }
                Message::Close(_) => {
                    warn!("Bybit WebSocket connection closed");
                    break;
                }
                _ => {}
            }
        }

        Ok(())
    }

    async fn handle_message(&self, text: &str, sender: &mpsc::Sender<CryptoPrice>) -> Result<()> {
        if text.contains("\"success\":true") || text.contains("\"op\":\"ping\"") {
            return Ok(());
        }

        match serde_json::from_str::<BybitResponse>(text) {
            Ok(response) => {
                let price = response.data.lastPrice.parse::<f64>()?;
                let change_24h = response.data.price24hPcnt.parse::<f64>()? * 100.0;
                let volume_24h = response.data.volume24h.parse::<f64>()?;

                let crypto_price = CryptoPrice::new(
                    response.data.symbol,
                    price,
                    change_24h,
                    volume_24h,
                    "Bybit".to_string(),
                );

                info!(
                    "Bybit {} - Price: ${:.2} ({:+.2}%) Volume: {:.0}",
                    crypto_price.symbol,
                    crypto_price.price,
                    crypto_price.change_24h,
                    crypto_price.volume_24h
                );

                if let Err(e) = sender.send(crypto_price).await {
                    error!("Failed to send crypto price to channel: {}", e);
                }
            }
            Err(e) => {
                if text.contains("\"topic\":\"tickers.") {
                    error!("Failed to parse Bybit response: {} - Text: {}", e, text);
                }
            }
        }

        Ok(())
    }
}
