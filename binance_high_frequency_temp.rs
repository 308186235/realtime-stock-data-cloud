use anyhow::Result;
use crate::models::CryptoPrice;
use crate::exchanges::Exchange;
use tokio::sync::mpsc;
use tokio_tungstenite::{connect_async, tungstenite::Message};
use futures_util::{SinkExt, StreamExt};
use serde_json::Value;
use tracing::{info, error, warn};
use std::time::Duration;

pub struct BinanceExchange;

impl BinanceExchange {
    pub fn new() -> Self {
        Self
    }

    // 🚀 高频组合流策略：使用实时交易数据流
    async fn connect_high_frequency_streams(&self, sender: mpsc::Sender<CryptoPrice>) -> Result<()> {
        // 🎯 构建高频数据流组合 - 基于深度研究报告的最佳实践
        let symbols = vec!["btcusdt", "ethusdt", "adausdt", "dotusdt", "bnbusdt"];
        let mut streams = Vec::new();
        
        for symbol in &symbols {
            // 实时交易流 - 每笔交易都推送 (20-50条/秒)
            streams.push(format!("{}@trade", symbol));
            // 聚合交易流 - 高频聚合数据 (10-30条/秒)  
            streams.push(format!("{}@aggTrade", symbol));
            // 最佳买卖价流 - 实时订单簿顶层 (5-20条/秒)
            streams.push(format!("{}@bookTicker", symbol));
        }
        
        let stream_names = streams.join("/");
        let url = format!("wss://stream.binance.com:9443/stream?streams={}", stream_names);
        
        info!("🚀 Binance高频组合流连接: {} 个数据流", streams.len());
        info!("🔗 预期频率: 50-100条/秒 (每个交易对15-20条/秒)");
        info!("🌐 连接URL: {}", url);

        loop {
            match connect_async(&url).await {
                Ok((ws_stream, _)) => {
                    let (mut write, mut read) = ws_stream.split();
                    info!("✅ Binance高频组合流连接成功，开始接收高频数据...");

                    // 心跳保持连接 - 20秒间隔（符合Binance最新规范）
                    let write_clone = std::sync::Arc::new(tokio::sync::Mutex::new(write));
                    let write_for_heartbeat = write_clone.clone();
                    
                    let heartbeat_handle = tokio::spawn(async move {
                        let mut interval = tokio::time::interval(Duration::from_secs(20));
                        loop {
                            interval.tick().await;
                            let mut write_guard = write_for_heartbeat.lock().await;
                            if let Err(e) = write_guard.send(Message::Ping(vec![])).await {
                                error!("❌ Binance心跳发送失败: {}", e);
                                break;
                            }
                        }
                    });

                    while let Some(msg) = read.next().await {
                        match msg {
                            Ok(Message::Text(text)) => {
                                if let Ok(data) = serde_json::from_str::<Value>(&text) {
                                    // 解析组合流数据
                                    if let Some(price_data) = self.parse_combined_stream(&data) {
                                        if let Err(e) = sender.send(price_data).await {
                                            error!("❌ Binance发送数据失败: {}", e);
                                            break;
                                        }
                                    }
                                }
                            }
                            Ok(Message::Pong(_)) => {
                                // 心跳响应
                            }
                            Ok(Message::Close(_)) => {
                                warn!("⚠️ Binance连接关闭，重连中...");
                                break;
                            }
                            Err(e) => {
                                error!("❌ Binance WebSocket错误: {}", e);
                                break;
                            }
                            _ => {}
                        }
                    }

                    heartbeat_handle.abort();
                }
                Err(e) => {
                    error!("❌ Binance连接失败: {}，3秒后重试", e);
                    tokio::time::sleep(Duration::from_secs(3)).await;
                }
            }
        }
    }

    // 🎯 解析组合流数据 - 支持多种高频数据类型
    fn parse_combined_stream(&self, data: &Value) -> Option<CryptoPrice> {
        // 组合流格式: {"stream": "btcusdt@trade", "data": {...}}
        let stream = data.get("stream")?.as_str()?;
        let stream_data = data.get("data")?;
        
        if stream.contains("@trade") {
            // 实时交易数据 - 最高频
            return self.parse_trade_data(stream_data, stream);
        } else if stream.contains("@aggTrade") {
            // 聚合交易数据 - 高频
            return self.parse_agg_trade_data(stream_data, stream);
        } else if stream.contains("@bookTicker") {
            // 最佳买卖价数据 - 中高频
            return self.parse_book_ticker_data(stream_data, stream);
        }
        
        None
    }

    // 解析实时交易数据 - 每笔交易都推送
    fn parse_trade_data(&self, data: &Value, stream: &str) -> Option<CryptoPrice> {
        let symbol = data.get("s")?.as_str()?;
        let price = data.get("p")?.as_str()?.parse::<f64>().ok()?;
        let quantity = data.get("q")?.as_str()?.parse::<f64>().ok()?;
        let trade_time = data.get("T")?.as_u64()?;
        let is_buyer_maker = data.get("m")?.as_bool().unwrap_or(false);
        
        let symbol_clean = self.normalize_symbol(symbol)?;
        
        info!("🔥 Binance Trade {} - Price: ${:.2} Qty: {:.2} {}",
              symbol_clean, price, quantity, 
              if is_buyer_maker { "📉" } else { "📈" });

        Some(CryptoPrice::new(
            symbol_clean.to_string(),
            price,
            0.0, // 交易数据没有变化百分比
            quantity,
            "Binance".to_string(),
        ))
    }

    // 解析聚合交易数据 - 聚合多笔交易
    fn parse_agg_trade_data(&self, data: &Value, stream: &str) -> Option<CryptoPrice> {
        let symbol = data.get("s")?.as_str()?;
        let price = data.get("p")?.as_str()?.parse::<f64>().ok()?;
        let quantity = data.get("q")?.as_str()?.parse::<f64>().ok()?;
        let first_trade_id = data.get("f")?.as_u64()?;
        let last_trade_id = data.get("l")?.as_u64()?;
        let trade_count = last_trade_id - first_trade_id + 1;
        
        let symbol_clean = self.normalize_symbol(symbol)?;
        
        info!("⚡ Binance AggTrade {} - Price: ${:.2} Qty: {:.2} Trades: {}",
              symbol_clean, price, quantity, trade_count);

        Some(CryptoPrice::new(
            symbol_clean.to_string(),
            price,
            0.0,
            quantity,
            "Binance".to_string(),
        ))
    }

    // 解析最佳买卖价数据 - 订单簿顶层
    fn parse_book_ticker_data(&self, data: &Value, stream: &str) -> Option<CryptoPrice> {
        let symbol = data.get("s")?.as_str()?;
        let best_bid = data.get("b")?.as_str()?.parse::<f64>().ok()?;
        let best_ask = data.get("a")?.as_str()?.parse::<f64>().ok()?;
        let bid_qty = data.get("B")?.as_str()?.parse::<f64>().ok()?;
        let ask_qty = data.get("A")?.as_str()?.parse::<f64>().ok()?;
        
        let mid_price = (best_bid + best_ask) / 2.0;
        let spread = best_ask - best_bid;
        let spread_percent = (spread / mid_price) * 100.0;
        
        let symbol_clean = self.normalize_symbol(symbol)?;
        
        info!("📊 Binance BookTicker {} - Mid: ${:.2} Spread: {:.4}% Bid: {:.2} Ask: {:.2}",
              symbol_clean, mid_price, spread_percent, best_bid, best_ask);

        Some(CryptoPrice::new(
            symbol_clean.to_string(),
            mid_price,
            0.0,
            spread, // 使用价差作为volume指标
            "Binance".to_string(),
        ))
    }

    // 标准化交易对名称
    fn normalize_symbol(&self, symbol: &str) -> Option<&str> {
        match symbol.to_uppercase().as_str() {
            "BTCUSDT" => Some("BTCUSDT"),
            "ETHUSDT" => Some("ETHUSDT"),
            "ADAUSDT" => Some("ADAUSDT"),
            "DOTUSDT" => Some("DOTUSDT"),
            "BNBUSDT" => Some("BNBUSDT"),
            _ => None,
        }
    }

    // 兼容旧ticker格式（备用）
    fn parse_ticker(&self, data: &Value) -> Option<CryptoPrice> {
        let symbol = data.get("s")?.as_str()?;
        let price = data.get("c")?.as_str()?.parse::<f64>().ok()?;
        let change_percent = data.get("P")?.as_str()?.parse::<f64>().ok()?;
        let volume = data.get("v")?.as_str()?.parse::<f64>().ok()?;

        let symbol_clean = self.normalize_symbol(symbol)?;

        info!("📈 Binance Ticker {} - Price: ${:.2} ({:+.2}%) Volume: {:.0}",
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

#[async_trait::async_trait]
impl Exchange for BinanceExchange {
    async fn connect(&self, sender: mpsc::Sender<CryptoPrice>) -> Result<()> {
        info!("🚀 启动Binance高频数据流策略...");
        info!("📊 预期数据频率: 50-100条/秒 (比@ticker提升50-100倍)");
        
        // 使用高频组合流
        self.connect_high_frequency_streams(sender).await
    }

    fn name(&self) -> &str {
        "Binance"
    }
}
