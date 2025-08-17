use clickhouse::{Client, Row};
use anyhow::Result;
use crate::models::CryptoPrice;
use tracing::{info, warn};

pub struct ClickHouseStorage {
    client: Client,
}

impl ClickHouseStorage {
    pub fn new(url: &str) -> Self {
        let client = Client::default().with_url(url);
        Self { client }
    }

    pub async fn init(&self) -> Result<()> {
        let create_table_sql = r#"
            CREATE TABLE IF NOT EXISTS crypto_prices (
                id String,
                symbol String,
                price Float64,
                change_24h Float64,
                volume_24h Float64,
                exchange String,
                timestamp DateTime64(3),
                source String DEFAULT 'websocket'
            ) ENGINE = MergeTree()
            PARTITION BY toYYYYMM(timestamp)
            ORDER BY (exchange, symbol, timestamp)
            SETTINGS index_granularity = 8192
        "#;

        self.client.query(create_table_sql).execute().await?;
        info!("ClickHouse table crypto_prices initialized");
        Ok(())
    }

    pub async fn insert_prices_batch(&self, prices: &[CryptoPrice]) -> Result<()> {
        if prices.is_empty() {
            return Ok(());
        }

        // 使用简单的SQL插入而不是批量插入
        for price in prices {
            let sql = format!(
                "INSERT INTO crypto_prices (id, symbol, price, change_24h, volume_24h, exchange, timestamp, source) VALUES ('{}', '{}', {}, {}, {}, '{}', '{}', '{}')",
                price.id,
                price.symbol,
                price.price,
                price.change_24h,
                price.volume_24h,
                price.exchange,
                price.timestamp.format("%Y-%m-%d %H:%M:%S%.3f"),
                price.source
            );
            
            if let Err(e) = self.client.query(&sql).execute().await {
                warn!("Failed to insert single price: {}", e);
            }
        }

        info!("Inserted {} crypto prices to ClickHouse", prices.len());
        Ok(())
    }

    pub async fn get_price_count(&self) -> Result<u64> {
        let query = "SELECT COUNT(*) FROM crypto_prices";
        let result = self.client.query(query).fetch_one::<u64>().await?;
        Ok(result)
    }
}
