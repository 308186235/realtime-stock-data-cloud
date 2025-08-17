use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use clickhouse::Row;

#[derive(Debug, Clone, Serialize, Deserialize, Row)]
pub struct CryptoPrice {
    pub id: String,
    pub symbol: String,
    pub price: f64,
    pub change_24h: f64,
    pub volume_24h: f64,
    pub exchange: String,
    pub timestamp: DateTime<Utc>,
    pub source: String,
}

impl CryptoPrice {
    pub fn new(
        symbol: String,
        price: f64,
        change_24h: f64,
        volume_24h: f64,
        exchange: String,
    ) -> Self {
        Self {
            id: uuid::Uuid::new_v4().to_string(),
            symbol,
            price,
            change_24h,
            volume_24h,
            exchange,
            timestamp: Utc::now(),
            source: "websocket".to_string(),
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct BybitTickerData {
    pub symbol: String,
    pub lastPrice: String,
    pub price24hPcnt: String,
    pub volume24h: String,
}

#[derive(Debug, Deserialize)]
pub struct BybitResponse {
    pub topic: String,
    pub data: BybitTickerData,
}
