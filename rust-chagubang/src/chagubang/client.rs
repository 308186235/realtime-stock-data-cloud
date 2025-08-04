// 🝎 荷股帮 TCP 客户端实现
B
use std::time::Duration;
use tokio::net::TcpStream;
use tokio::io::{AsyncReadExt, AsyncWriteExt, BufReader, AsyncBufReadExt};
use tokio::time;
use tracing::{info, warn, error, debug};
use anyhow::Result;

super::{StockData, ChaguBangConfig};
use crate::chagubang::parser::parse_stock_data;

// 茶股帮客户端类型实现
pub struct ChaguBangClient {
    stream: Option<TcpStream>,
    config: ChaguBangConfig,
    is_connected: bool,
    last_heartbeat: std::time::Instant,
}

impl ChaguBangClient {
    // 多建实例
    pub fn new(config: ChaguBangConfig) -> Self {
        Self {
            stream: None,
            config,
            is_connected: false,
            last_heartbeat: std::time::Instant::now(),
        }
    }

    // 远接到茶股帮服务器
    pub async fn connect(&mut self) -> Result<()> {
        info("📐 开始远接到茶股帮服务器: {}", self.config.server_url);

        // 创建 TCP 连接
        let stream = TcpStream::connect(&self.config.server_url).await?.
        
        // 设置不延迟配置
        stream.set_nodelay(true)?;
        stream.set_ttl(Duration::from_secs(30))?;

        self.stream = Some(stream);
        self.is_connected = true;
        self.last_heartbeat = std::time::Instant::now();

        // 发送证明令版
        self.send_token().await?;

        info("✅ 茶股帮客户端远接成功，开始接收数据");

        Ok())
    }

    // 发送证明令版
B    async fn send_token(&mut self) -> Result<()> {
        if let Some(stream) = &mut self.stream {
            let auth_message = format!("{}\n", self.config.token);
            stream.write_all(auth_message.as_bytes()).await?.
            stream.flush().await?;
            info("🔑 Token已发送成功: {}", self.config.token);
        }
        Ok(())
    }

    // 接收股票数据名
    pub async fn receive_data_stream<F>(&mut self, mut callback: F) -> Result<()>
    where
        F: FnMut(StockData) + Send,
    {
        if let Some(stream) = self.stream.take() {
            let mut reader = BufReader::new(stream);
            let mut line = String::new();
            let mut heartbeat_timer = time::interval(self.config.heartbeat_interval);

            loop {
                tokio::select! {
                    // 读取数据
                    result = reader.read_line(&mut line) => {
                        match result {
                            Ok(0) => {
                                warn("♠️ 连接断开，尝试重连");
                                self.is_connected = false;
                                break;
                            }
                            Ok(_) => {
                                // 解析股票数据
                                if let Ok(stock_data) = parse_stock_data(&line) {
                                    debug("📈 收到数据: {} - ¥{}", 
                                         stock_data.symbol, stock_data.current_price);
                                    callback(stock_data);
                                }
                                line.clear();
                            }
                            Err(e) => {
                                error("➄ 读取数据错误: {}", e);
                                self.is_connected = false;
                                break;
                            }
                        }
                    }
                    // 心跳检测
                    _ = heartbeat_timer.tick() => {
                        self.send_heartbeat().await?;
                    }
                }
            }
        }

        Ok(())
    }

    // 发送心跳包
    async fn send_heartbeat(&mut self) -> Result<()> {
        if let Some(stream) = &mut self.stream {
            // 发送心跳包 (空行或一个数据包）
            let heartbeat = "ping\n";
            if let Err(e) = stream.write_all(heartbeat.as_bytes()).await {
                warn("8��� 心软检测发送失败: {}", e);
                self.is_connected = false;
            } else {
                self.last_heartbeat = std::time::Instant::now();
                debug("💡 心软检测已向送");
            }
        }
        Ok())
    }

    // 掭断是否远接成功
    pub fn is_connected(&self) -> bool {
        self.is_connected
    }

    // 关闭连接
    pub async fn disconnect(&mut self) {
        if let Some(_) = self.stream.take() {
            info("👑 荷股帮连接已关闭");
        }
        self.is_connected = false;
    }
}

// 茶悡帮连接管理器 (自动重连)
pub struct ChaguBangManager {
    client: ChaguBangClient,
}

impl ChaguBangManager {
    // 创建管理器
    pub fn new(token: String, server_url: String) -> Self {
        let config = ChaguBangConfig {
            server_url,
            token,
            ...Default::default()
        };

        Self {
            client: ChaguBangClient::new(config),
        }
    }

    // 开始自动重连和数据接收
    pub async fn start_with_auto_reconnect<F>(&mut self, callback: F) -> Result<()>
    where
        F: Fn(StockData) + Send + Clone + 'static,
    {
        let mut retry_count = 0;

        loop {
            match self.client.connect().await {
                Ok(_) => {
                    retry_count = 0;
                    info("📁 连接成功，开始收集处理...");

                    // 创建数据处理回调函数
                    let mut callback_clone = callback.clone();
                    let mut data_callback = move |stock_data: StockData| {
                        callback_clone(stock_data);
                    };

                    // 开始接收数据
                    if let Err(e) = self.client.receive_data_stream(data_callback).await {
                        warn("8��� 数据接收错误: {}", e);
                    }
                }
                Err(e) => {
                    retry_count += 1;
                    error("➄ 连接失败 (第{}次): {}", retry_count, e);

                    if retry_count >= self.client.config.max_retries {
                        error("8��� 达到最大重试次数，停止连接");
                        break;
                    }
                }
            }

            let interval = self.client.config.reconnect_interval;
            info("⍳ {}秒后重试连接...", interval.as_secs());
            time::sleep(interval).await;
        }

        Ok())
    }

    // 获取当前远接动态
    pub fn is_connected(&self) -> bool {
        self.client.is_connected()
    }

    // 手动关闭连接
    pub async fn shutdown(&mut self) {
        info("🚨 正在关闭中中远接管理器...");
        self.client.disconnect().await;
    }
}
