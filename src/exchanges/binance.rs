//! 🚀 Binance交易所连接器 - 基于Exa深度研究的真正高频版本

use anyhow::Result;
use crate::models::CryptoPrice;
use crate::exchanges::Exchange;
use tokio::sync::mpsc;
use tokio_tungstenite::{connect_async, tungstenite::Message};
use futures_util::{SinkExt, StreamExt};
use serde_json::Value;
use tracing::{info, error, warn, debug};
use std::time::{Duration, Instant};
use async_trait::async_trait;

pub struct BinanceExchange;

impl BinanceExchange {
    pub fn new() -> Self {
        Self
    }

    /// 🔥 基于Exa研究的真正高频Binance连接实现
    async fn connect_binance_websocket(&self, sender: mpsc::Sender<CryptoPrice>) -> Result<()> {
        info!("🚀 启动基于Exa研究的真正高频Binance连接");
        info!("�� 预期性能: 每个交易对40-50条/秒, 总计200-250条/秒");

        // 🔥 使用多个独立的高频连接而不是组合流
        let symbols = vec!["btcusdt", "ethusdt", "adausdt", "dotusdt", "bnbusdt"];
        let mut handles = vec![];

        for symbol in symbols {
            let sender_clone = sender.clone();
            let symbol_clone = symbol.to_string();

            // 为每个交易对创建独立的高频连接
            let handle = tokio::spawn(async move {
                Self::connect_symbol_high_frequency(symbol_clone, sender_clone).await
            });
            handles.push(handle);
        }

        // 等待所有连接
        for handle in handles {
            if let Err(e) = handle.await {
                error!("❌ Binance高频连接错误: {}", e);
            }
        }

        Ok(())
    }

    /// 🎯 为单个交易对创建真正的高频连接
    async fn connect_symbol_high_frequency(symbol: String, sender: mpsc::Sender<CryptoPrice>) -> Result<()> {
        let mut reconnect_count = 0;

        loop {
            // 🔥 使用真正的高频流 - 基于Exa研究
            let streams = vec![
                format!("{}@trade", symbol),        // 实时交易流
                format!("{}@aggTrade", symbol),     // 聚合交易流  
                format!("{}@bookTicker", symbol),   // 最佳买卖价
                format!("{}@depth@100ms", symbol),  // 100ms深度流
            ];

            // 🌐 使用组合流URL但限制为单个交易对的多个流
            let streams_str = streams.join("/");
            let url = format!("wss://stream.binance.com:9443/stream?streams={}", streams_str);

            info!("🔗 {}高频连接: {}", symbol.to_uppercase(), url);

            match connect_async(&url).await {
                Ok((ws_stream, _)) => {
                    let (mut write, mut read) = ws_stream.split();
                    info!("✅ {}高频连接成功，开始接收数据...", symbol.to_uppercase());

                    let mut last_ping = Instant::now();
                    let mut last_data = Instant::now();
                    let mut message_count = 0u64;
                    let mut last_report = Instant::now();

                    // 🔥 24小时自动重连定时器
                    let connection_start = Instant::now();
                    let max_connection_time = Duration::from_secs(23 * 3600);

                    while let Some(message) = read.next().await {
                        // 🔄 24小时强制重连
                        if connection_start.elapsed() > max_connection_time {
                            info!("🔄 {}24小时连接时间到，主动重连...", symbol.to_uppercase());
                            break;
                        }

                        // 🔄 30秒无数据检测
                        if last_data.elapsed() > Duration::from_secs(30) {
                            warn!("⚠️ {}30秒无数据，重连...", symbol.to_uppercase());
                            break;
                        }

                        match message {
                            Ok(Message::Text(text)) => {
                                last_data = Instant::now();
                                message_count += 1;

                                match serde_json::from_str::<Value>(&text) {
                                    Ok(data) => {
                                        // 🔥 处理组合流数据
                                        if let Some(stream_data) = Self::parse_combined_stream(&data) {
                                            if sender.send(stream_data).await.is_err() {
                                                warn!("⚠️ {}数据发送失败", symbol.to_uppercase());
                                                break;
                                            }
                                        }
                                    }
                                    Err(e) => {
                                        debug!("🔍 {}JSON解析错误: {}", symbol.to_uppercase(), e);
                                    }
                                }

                                // 每5秒报告一次性能
                                if last_report.elapsed() >= Duration::from_secs(5) {
                                    let rate = message_count as f64 / last_report.elapsed().as_secs_f64();
                                    info!("📊 {}性能: {:.1} 条/秒, 总计: {} 条", 
                                          symbol.to_uppercase(), rate, message_count);
                                    last_report = Instant::now();
                                    message_count = 0;
                                }
                            }
                            Ok(Message::Ping(payload)) => {
                                last_ping = Instant::now();
                                if let Err(e) = write.send(Message::Pong(payload)).await {
                                    error!("❌ {}pong回复失败: {}", symbol.to_uppercase(), e);
                                    break;
                                }
                                debug!("�� {}ping收到并回复pong", symbol.to_uppercase());
                            }
                            Ok(Message::Close(close_frame)) => {
                                warn!("🔌 {}连接被服务器关闭: {:?}", symbol.to_uppercase(), close_frame);
                                break;
                            }
                            Err(e) => {
                                error!("❌ {}消息错误: {}", symbol.to_uppercase(), e);
                                break;
                            }
                            _ => {}
                        }

                        // 🔄 60秒无ping检测
                        if last_ping.elapsed() > Duration::from_secs(60) {
                            warn!("⚠️ {}60秒无ping，重连...", symbol.to_uppercase());
                            break;
                        }
                    }

                    info!("📊 {}连接结束，总共处理了 {} 条消息", symbol.to_uppercase(), message_count);
                }
                Err(e) => {
                    error!("❌ {}连接失败: {}", symbol.to_uppercase(), e);
                    reconnect_count += 1;

                    // 🔄 指数退避重连
                    let backoff = std::cmp::min(60, 2_u64.pow(std::cmp::min(reconnect_count, 6)));
                    warn!("🔄 {}{}秒后重试... (第{}次)", symbol.to_uppercase(), backoff, reconnect_count);
                    tokio::time::sleep(Duration::from_secs(backoff)).await;
                }
            }
        }
    }

    /// 🎯 解析组合流数据 - 基于Exa研究的正确实现
    fn parse_combined_stream(data: &Value) -> Option<CryptoPrice> {
        // 检查是否是组合流格式
        if let (Some(stream), Some(data_obj)) = (data.get("stream"), data.get("data")) {
            let stream_name = stream.as_str()?;

            // 🔥 解析不同类型的高频数据流
            if stream_name.contains("@trade") {
                return Self::parse_trade_data(data_obj);
            } else if stream_name.contains("@aggTrade") {
                return Self::parse_agg_trade_data(data_obj);
            } else if stream_name.contains("@bookTicker") {
                return Self::parse_book_ticker_data(data_obj);
            } else if stream_name.contains("@depth") {
                return Self::parse_depth_data(data_obj);
            }
        }
        None
    }

    /// 🎯 解析交易数据
    fn parse_trade_data(data: &Value) -> Option<CryptoPrice> {
        let symbol = data.get("s")?.as_str()?.to_string();
        let price = data.get("p")?.as_str()?.parse::<f64>().ok()?;
        let quantity = data.get("q")?.as_str()?.parse::<f64>().ok()?;

        info!("📊 Binance {} Trade - Price: ${:.2} Qty: {:.4}", symbol, price, quantity);

        Some(CryptoPrice::new(
            symbol,
            price,
            0.0, // 交易数据没有变化百分比
            quantity,
            "Binance".to_string(),
        ))
    }

    /// �� 解析聚合交易数据
    fn parse_agg_trade_data(data: &Value) -> Option<CryptoPrice> {
        let symbol = data.get("s")?.as_str()?.to_string();
        let price = data.get("p")?.as_str()?.parse::<f64>().ok()?;
        let quantity = data.get("q")?.as_str()?.parse::<f64>().ok()?;

        info!("📊 Binance {} AggTrade - Price: ${:.2} Qty: {:.4}", symbol, price, quantity);

        Some(CryptoPrice::new(
            symbol,
            price,
            0.0,
            quantity,
            "Binance".to_string(),
        ))
    }

    /// 🎯 解析最佳买卖价数据
    fn parse_book_ticker_data(data: &Value) -> Option<CryptoPrice> {
        let symbol = data.get("s")?.as_str()?.to_string();
        let bid_price = data.get("b")?.as_str()?.parse::<f64>().ok()?;
        let ask_price = data.get("a")?.as_str()?.parse::<f64>().ok()?;
        let mid_price = (bid_price + ask_price) / 2.0;

        info!("📊 Binance {} BookTicker - Bid: ${:.2} Ask: ${:.2} Mid: ${:.2}", 
              symbol, bid_price, ask_price, mid_price);

        Some(CryptoPrice::new(
            symbol,
            mid_price,
            0.0,
            0.0,
            "Binance".to_string(),
        ))
    }

    /// 🎯 解析深度数据
    fn parse_depth_data(data: &Value) -> Option<CryptoPrice> {
        let symbol = data.get("s")?.as_str()?.to_string();

        // 获取最佳买卖价
        if let (Some(bids), Some(asks)) = (data.get("b"), data.get("a")) {
            if let (Some(bid_array), Some(ask_array)) = (bids.as_array(), asks.as_array()) {
                if let (Some(best_bid), Some(best_ask)) = (bid_array.first(), ask_array.first()) {
                    if let (Some(bid_price_str), Some(ask_price_str)) =
                        (best_bid.get(0).and_then(|v| v.as_str()),
                         best_ask.get(0).and_then(|v| v.as_str())) {

                        let bid_price = bid_price_str.parse::<f64>().ok()?;
                        let ask_price = ask_price_str.parse::<f64>().ok()?;
                        let mid_price = (bid_price + ask_price) / 2.0;

                        info!("📊 Binance {} Depth - Bid: ${:.2} Ask: ${:.2} Mid: ${:.2}", 
                              symbol, bid_price, ask_price, mid_price);

                        return Some(CryptoPrice::new(
                            symbol,
                            mid_price,
                            0.0,
                            0.0,
                            "Binance".to_string(),
                        ));
                    }
                }
            }
        }
        None
    }
}

#[async_trait]
impl Exchange for BinanceExchange {
    async fn connect(&self, sender: mpsc::Sender<CryptoPrice>) -> Result<()> {
        self.connect_binance_websocket(sender).await
    }

    fn name(&self) -> &str {
        "Binance"
    }
}
