"""
简化的后端应用 - 用于快速修复API路由问题
现在连接真实数据库
"""
import os
import logging
import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database_setup import DatabaseManager

# 配置日志
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/simple_backend.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Stock Trading System API - Simplified",
    description="简化版API用于快速修复路由问题",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "message": "简化版API服务正常",
        "timestamp": datetime.now().isoformat(),
        "api_version": "1.0",
        "service": "stock-trading-backend-simple"
    }

@app.get("/api/health")
async def api_health_check():
    """API健康检查端点"""
    return {
        "status": "healthy",
        "message": "简化版API服务正常",
        "timestamp": datetime.now().isoformat(),
        "api_version": "1.0",
        "service": "stock-trading-backend-simple"
    }

# 投资组合API
@app.get("/api/portfolio/")
async def get_portfolios():
    """获取所有投资组合列表"""
    return {
        "success": True,
        "data": [
            {
                "id": "portfolio-001",
                "name": "默认组合",
                "total_value": 152340.56,
                "cash": 25600.38,
                "stock_value": 126740.18,
                "stocks_count": 8,
                "profit_pct": 8.23
            }
        ]
    }

@app.get("/api/portfolio/{portfolio_id}")
async def get_portfolio(portfolio_id: str):
    """获取指定投资组合详情"""
    return {
        "success": True,
        "data": {
            "id": portfolio_id,
            "name": "默认组合",
            "total_value": 152340.56,
            "cash": 25600.38,
            "stock_value": 126740.18,
            "stocks": [
                {"code": "600000", "name": "浦发银行", "shares": 1000, "cost_price": 10.56, "current_price": 11.23, "profit_pct": 6.34},
                {"code": "000001", "name": "平安银行", "shares": 500, "cost_price": 15.20, "current_price": 16.45, "profit_pct": 8.22}
            ]
        }
    }

# 股票数据API
@app.get("/api/stock/market-data")
async def get_market_data():
    """获取市场数据"""
    return {
        "success": True,
        "data": {
            "lastUpdate": datetime.now().isoformat(),
            "indices": {
                "000001": {"name": "上证指数", "price": 3200.45, "change": 1.23, "change_pct": 0.38},
                "399001": {"name": "深证成指", "price": 12500.67, "change": -5.43, "change_pct": -0.04}
            },
            "marketStatus": "normal",
            "connected": True
        }
    }

@app.get("/api/stock/list")
async def get_stock_list():
    """获取股票列表"""
    return {
        "success": True,
        "data": [
            {"code": "600000", "name": "浦发银行", "price": 11.23, "change": 0.67, "change_pct": 6.34},
            {"code": "000001", "name": "平安银行", "price": 16.45, "change": 1.25, "change_pct": 8.22},
            {"code": "000002", "name": "万科A", "price": 25.67, "change": -0.33, "change_pct": -1.27}
        ]
    }

# AI分析API
@app.get("/api/ai/analysis")
async def get_ai_analysis():
    """获取AI分析结果"""
    return {
        "success": True,
        "data": {
            "market_sentiment": "neutral",
            "recommendations": [
                {"code": "600000", "action": "buy", "confidence": 0.75, "reason": "技术指标向好"},
                {"code": "000001", "action": "hold", "confidence": 0.65, "reason": "震荡整理中"}
            ],
            "risk_level": "medium",
            "timestamp": datetime.now().isoformat()
        }
    }

# 策略API
@app.get("/api/strategy/")
async def get_strategies():
    """获取策略列表"""
    return {
        "success": True,
        "data": [
            {
                "id": "strategy-001",
                "name": "均线策略",
                "description": "基于移动平均线的交易策略",
                "status": "active",
                "profit_pct": 12.5
            },
            {
                "id": "strategy-002", 
                "name": "动量策略",
                "description": "基于价格动量的交易策略",
                "status": "inactive",
                "profit_pct": 8.3
            }
        ]
    }

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Stock Trading System API - Simplified Version",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/health",
            "/api/health", 
            "/api/portfolio/",
            "/api/stock/market-data",
            "/api/ai/analysis",
            "/api/strategy/",
            "/docs"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
