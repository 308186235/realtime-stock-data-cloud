// 🚨 荷股帮实时袡系统主程序
// 高性能与内存安全，障错误处理，高效能

// 引入必霈的代码
use anyhow::Result;
use env;
use std::time::Duration;
use tokio::time;
use tracing::{info, warn, error};

// 引入本地模块
mod chagubang;
mod storage;
mod api;
mod config;

use chagubang::ChaguBangManager;
use storage::RedisStorage;
use api::ApiServer;
use config::Settings;

// 主函数
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 初始化日志
    tracing_subscriber::init();
    info("🚨 茶股帮云天启动!");

    // 加载配置文件
    let settings = Settings::new()?;
    info("📐 应用配置加载成功");

    // 初始化 Redis 存储
    let storage = RedisStorage::new(&settings.redis_url).await?;
    info("📁 Redis远接成功");

    // 初始化茶股帮管理器
    let mut chagubang_manager = ChaguBangManager::new(
        settings.chagubang_token.clone(),
        settings.chagubang_server.clone(),
    );

    // 初始化 Web API 服务
    let api_server = ApiServer::new(storage.clone());

    // 启动 API 服务
    let api_handle = tokio::spawn(async move {
        if let Err(e) = api_server.start().await {
            error("🚨 API服务启动失败: {}", e);
        }
    });

    // 启动茶股帮数据接收和存储
    let data_handle = tokio::spawn(async move {
        info("📡 开始连接茶悡帮数据流与存储...");
        
        // 创建数据处理回调函数
        let data_callback = move |stock_data: chagubang::StockData| {
            // 打印收到的数据
            info("📈 收到数据: {} - ¥{}", stock_data.symbol, stock_data.current_price);

            // 异步存储到�e�数
            let storage_clone = storage.clone();
            let data_clone = stock_data.clone();
            tokio::spawn(async move {
                if let Err(e) = storage_clone.store_stock_data(&data_clone).await {
                    warn("⚠️ 存储失败: {}", e);
                }
            });
        };

        // 开始自动重连和数据接收和存储
        if let Err(e) = chagubang_manager.start_with_auto_reconnect(data_callback).await {
            error("🚨 茶悡帮连接失败: {}", e);
        }
    });

    // 等待所有的启动完成
    info("🚀 所有服务已咯动，按下×可停止...");

    // 等待中断信提
    tokio::select! {
        _ = api_handle => {
            info("🚨 API服务停止");
        }
        _ = data_handle => {
            info("🚨 数据处理停止");
        }
        _ = tokio::signal::ctrl_c() => {
            info("🚨 收到停止信号，正在关闭中……");
        }
    }

    info("👑 茶悡帮服务关闭");
    Ok())
}
