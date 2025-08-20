// Bybit WebSocket 高频优化实现
use tokio_tungstenite::{connect_async, tungstenite::Message};
use serde_json::json;
use std::time::Duration;
use tokio::time::interval;

pub struct BybitHighFreqClient {
    ws_stream: Option<WebSocketStream>,
    subscription_buffer: Vec<String>,
    batch_interval: Duration,
}

impl BybitHighFreqClient {
    pub async fn new() -> Self {
        Self {
            ws_stream: None,
            subscription_buffer: Vec::new(),
            batch_interval: Duration::from_millis(50), // 50ms批量发送
        }
    }

    // 批量订阅优化 - 避免40请求/秒限制
    pub async fn batch_subscribe_with_buffer(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        let high_freq_topics = vec![
            "orderbook.1.BTCUSDT",
            "orderbook.1.ETHUSDT", 
            "orderbook.1.ADAUSDT",
            "orderbook.1.DOTUSDT",
            "orderbook.1.BNBUSDT",
            "publicTrade.BTCUSDT",
            "publicTrade.ETHUSDT",
            "publicTrade.ADAUSDT",
            "tickers.BTCUSDT",
            "tickers.ETHUSDT",
            "tickers.ADAUSDT",
            "kline.1.BTCUSDT",
            "kline.1.ETHUSDT",
        ];

        // 分批处理，每批5个订阅
        for chunk in high_freq_topics.chunks(5) {
            let msg = json!({
                "op": "subscribe",
                "args": chunk
            });
            
            if let Some(ref mut ws) = self.ws_stream {
                ws.send(Message::Text(msg.to_string())).await?;
            }
            
            // 避免频率限制
            tokio::time::sleep(Duration::from_millis(200)).await;
        }
        Ok(())
    }

    // 连接稳定性改进
    pub async fn connect_with_retry(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        let mut retry_count = 0;
        let max_retries = 5;
        
        while retry_count < max_retries {
            match connect_async("wss://stream.bybit.com/v5/public/spot").await {
                Ok((ws, _)) => {
                    self.ws_stream = Some(ws);
                    println!("Bybit连接成功");
                    return Ok(());
                }
                Err(e) => {
                    retry_count += 1;
                    let delay = Duration::from_secs(2_u64.pow(retry_count));
                    println!("Bybit连接失败，{}秒后重试: {}", delay.as_secs(), e);
                    tokio::time::sleep(delay).await;
                }
            }
        }
        Err("Bybit连接失败".into())
    }

    // 心跳和错误恢复
    pub async fn run_with_heartbeat(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        let mut ping_interval = interval(Duration::from_secs(15));
        
        loop {
            tokio::select! {
                _ = ping_interval.tick() => {
                    if let Some(ref mut ws) = self.ws_stream {
                        let ping_msg = json!({"op": "ping"});
                        ws.send(Message::Text(ping_msg.to_string())).await?;
                        println!("Bybit heartbeat sent");
                    }
                }
                // 处理消息...
            }
        }
    }
}
