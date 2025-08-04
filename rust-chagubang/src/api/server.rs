// 🌐 荷股帮 Web API 服务器B
use axum::{
    extract::{Path, Query},
    http::StatusCode,
    response::Json,
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::HashMap;
use tokio::net::TcpListener;
use tracing::{info, warn, error};
use anyhow::Result;
use tower::ServiceBuilder;
use tower_http::cors::CorsLayer;

use crate::storage::RedisStorage;
use crate::chagubang::StockData;

// API 服务器类型实现
pub struct ApiServer {
    storage: RedisStorage,
}

impl ApiServer {
    // 创建 API 服务
    pub fn new(storage: RedisStorage) -> Self {
        Self { storage }
    }

    // 启动 API 服务
    pub async fn start(&self) -> Result<()> {
        let app = self.create_router();

        // 创建 TCP 监听器B        let listener = TcpListener::bind("0.0.0.0:3000").await?;
        info("💡 API服务启动中，监听地址: http://0.0.0.0:3000");

        // 启动服务
        axum::serve(listener, app).await?;

        Ok(())
    }

    // 创建路由表格
    fn create_router(&self) -> Router {
        let storage = self.storage.clone();

        Router::new()
            // 健康检查
            .route("/api/health", get(health_check))
            // 获取股票数据
            .route("/api/stocks/:code", get(move |path: Path<String>| {
                let storage = storage.clone();
                async move { get_stock_data(Path(path), storage).await }
            }))
            // 获取所有股票列表
            .route("/api/stocks", get(move || {
                let storage = storage.clone();
                async move { get_all_stocks(storage).await }
            }))
            // 获取股票历史数据
            .route("/api/stocks/:code/history", get(move |path: Path<String>, query: Query<HistoryQuery>| {
                let storage = storage.clone();
                async move { get_stock_history(Path(path), Query(query), storage).await }
            }))
            // 获取统计信息
            .route("/api/stats", get(move || {
                let storage = storage.clone();
                async move { get_statistics(storage).await }
            }))
            // 配置 CORS
            .layer(
                CorsLayer::new()
                    .allow_origin(any())
                    .allow_methods(any())
                    .allow_headers(any())
            )
    }
}

// 健康检查
async fn health_check() -> Json<Value> {
    Json(json!({
        "status": "ok",
        "timestamp": chrono::Utc::now().timestamp(),
        "service": "茶悡帮云天服务",
        "version": env!("CARGO_PKG_VERSION")
    }))
}

// 获取股票数据
async fn get_stock_data(
    Path(code): Path<String>,
    storage: RedisStorage,
) -> Result<Json<Value>, (StatusCode, Json<Value>)> {
    match storage.get_latest_stock_data(&code).await {
        Ok(Some(data)) => {
            Ok(Json(json!({
                "success": true,
                "data": data
            })))
        }
        Ok(None) => {
            Err((
                StatusCode::NOT_FOUND,
                Json(json!({
                    "success": false,
                    "error": "未找到指定股票数据",
                    "code": code
                })),
            ))
        }
        Err(e) => {
            error("API 错误：获取股票数据失败: {}", e);
            Err((
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({
                    "success": false,
                    "error": "服务器内部错误"
                })),
            ))
        }
    }
}

// 获取所有股票列表
async fn get_all_stocks(
    storage: RedisStorage,
) -> Result<Json<Value>, (StatusCode, Json<Value>)> {
    match storage.get_all_stocks().await {
        Ok(stocks) => {
            Ok(Json(json!({
                "success": true,
                "data": {
                    "stocks": stocks,
                    "count": stocks.len()
                }
            })))
        }
        Err(e) => {
            error("API 错误：获取股票列表失败: {}", e);
            Err((
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({
                    "success": false,
                    "error": "服务器内部错误"
                })),
            ))
        }
    }
}

// 历史数据查询参数
[derive(Deserialize)]
struct HistoryQuery {
    limit: Option<usize>,
}

// 获取股票历史数据
async fn get_stock_history(
    Path(code): Path<String>,
    Query(query): Query<HistoryQuery>,
    storage: RedisStorage,
) -> Result<Json<Value>, (StatusCode, Json<Value>)> {
    let limit = query.limit.unwrap_or(100);

    match storage.get_stock_history(&code, limit).await {
        Ok(history) => {
            Ok(Json(json!({
                "success": true,
                "data": {
                    "code": code,
                    "history": history,
                    "count": history.len(),
                    "limit": limit
                }
            })))
        }
        Err(e) => {
            error("API 错诿：菷取股票历習数据失败: {}", e);
            Err((
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({
                    "success": false,
                    "error": "服务器内部错误"
                })),
            ))
        }
    }
}

// 获取统计信息
async fn get_statistics(
    storage: RedisStorage,
) -> Result<Json<Value>, (StatusCode, Json<Value>)> {
    match storage.get_statistics().await {
        Ok(stats) => {
            Ok(Json(json!({
                "success": true,
                "data": stats
            })))
        }
        Err(e) => {
            error("API 错诿：获取统计失败: {}", e);
            Err((
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({
                    "success": false,
                    "error": "服务器内部错诿"
                })),
            ))
        }
    }
}
