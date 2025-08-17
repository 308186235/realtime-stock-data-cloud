import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Trading Backend API",
    description="Google Cloud hosted trading system API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Trading Backend API is running on Google Cloud",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server": "gcp-vm"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "server": "google-cloud",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running"
    }

# Account endpoints
@app.get("/api/account/balance")
async def get_account_balance():
    return {
        "total_assets": 100000.00,
        "available_cash": 50000.00,
        "market_value": 50000.00,
        "profit_loss": 5000.00,
        "profit_loss_rate": 5.26,
        "server": "google-cloud",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/account/positions")
async def get_positions():
    return {
        "positions": [
            {
                "symbol": "000001",
                "name": "平安银行",
                "quantity": 1000,
                "avg_price": 12.50,
                "current_price": 13.15,
                "market_value": 13150.00,
                "profit_loss": 650.00,
                "profit_loss_rate": 5.20
            },
            {
                "symbol": "600000", 
                "name": "浦发银行",
                "quantity": 2000,
                "avg_price": 8.80,
                "current_price": 9.20,
                "market_value": 18400.00,
                "profit_loss": 800.00,
                "profit_loss_rate": 4.55
            }
        ],
        "server": "google-cloud",
        "timestamp": datetime.now().isoformat()
    }

# Trading endpoints
@app.get("/api/trading/orders")
async def get_orders():
    return {
        "orders": [
            {
                "order_id": "GCP20250629001",
                "symbol": "000001",
                "name": "平安银行",
                "type": "buy",
                "quantity": 1000,
                "price": 12.50,
                "status": "filled",
                "time": "2025-06-29 09:30:00"
            }
        ],
        "server": "google-cloud",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/trading/order")
async def place_order(order_data: dict):
    return {
        "status": "success",
        "message": "订单已提交到Google Cloud处理",
        "order_id": f"GCP{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "order_data": order_data,
        "server": "google-cloud",
        "timestamp": datetime.now().isoformat()
    }

# Agent analysis endpoints
@app.get("/api/agent/analysis")
async def get_agent_analysis():
    return {
        "analysis": {
            "market_trend": "上涨",
            "confidence": 0.75,
            "recommendation": "适度买入",
            "key_factors": [
                "技术指标向好",
                "成交量放大", 
                "资金流入明显"
            ]
        },
        "learning_progress": {
            "accuracy": 0.68,
            "total_trades": 156,
            "win_rate": 0.64,
            "status": "学习中"
        },
        "server": "google-cloud",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/agent/trade")
async def execute_agent_trade(trade_data: dict):
    return {
        "status": "success",
        "message": "AI交易指令已在Google Cloud执行",
        "order_id": f"AI-GCP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "trade_data": trade_data,
        "server": "google-cloud",
        "timestamp": datetime.now().isoformat()
    }

# Stock data endpoints
@app.get("/api/stocks/{symbol}")
async def get_stock_data(symbol: str):
    return {
        "symbol": symbol,
        "name": "示例股票",
        "price": 12.50,
        "change": 0.15,
        "change_percent": 1.22,
        "volume": 1000000,
        "server": "google-cloud",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8000))
    logger.info(f"Starting Trading Backend API on Google Cloud VM, port {PORT}")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        access_log=True
    )
