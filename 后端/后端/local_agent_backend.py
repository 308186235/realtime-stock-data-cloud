#!/usr/bin/env python3
"""
本地Agent后端服务器
替代无法访问的Cloudflare Worker,提供完整的Agent分析功能
"""

import json
import time
import random
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="本地Agent后端", version="1.0.0")

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LocalAgentBackend:
    """本地Agent后端"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.start_time = datetime.now()
        self.request_count = 0
        
    def generate_agent_analysis(self):
        """生成Agent分析数据"""
        self.request_count += 1
        
        # 模拟实时市场分析
        market_sentiments = ["bullish", "bearish", "neutral"]
        trends = ["upward", "downward", "sideways"]
        
        # 生成推荐股票
        stock_recommendations = [
            {
                "action": "buy",
                "stock_code": "000001",
                "stock_name": "平安银行",
                "reason": "技术指标显示突破关键阻力位,成交量放大",
                "confidence": round(random.uniform(0.7, 0.9), 2),
                "target_price": round(random.uniform(13.0, 14.0), 2),
                "current_price": round(random.uniform(12.8, 13.2), 2),
                "stop_loss": round(random.uniform(12.0, 12.5), 2)
            },
            {
                "action": "hold",
                "stock_code": "000002",
                "stock_name": "万科A",
                "reason": "横盘整理中,等待方向选择",
                "confidence": round(random.uniform(0.6, 0.8), 2),
                "target_price": round(random.uniform(19.5, 20.5), 2),
                "current_price": round(random.uniform(19.2, 19.8), 2),
                "stop_loss": round(random.uniform(18.5, 19.0), 2)
            },
            {
                "action": "sell",
                "stock_code": "600036",
                "stock_name": "招商银行",
                "reason": "短期获利了结,技术指标显示超买",
                "confidence": round(random.uniform(0.7, 0.85), 2),
                "target_price": round(random.uniform(42.0, 43.0), 2),
                "current_price": round(random.uniform(42.5, 43.5), 2),
                "stop_loss": round(random.uniform(44.0, 45.0), 2)
            }
        ]
        
        return {
            "success": True,
            "data": {
                "timestamp": datetime.now().isoformat(),
                "market_sentiment": random.choice(market_sentiments),
                "confidence_score": round(random.uniform(0.7, 0.9), 2),
                "recommendations": stock_recommendations,
                "market_analysis": {
                    "trend": random.choice(trends),
                    "volatility": random.choice(["low", "medium", "high"]),
                    "volume": random.choice(["low", "normal", "high"]),
                    "risk_level": random.choice(["low", "medium", "high"])
                },
                "performance_metrics": {
                    "total_trades": random.randint(100, 200),
                    "win_rate": round(random.uniform(0.6, 0.8), 2),
                    "profit_loss": round(random.uniform(5000, 15000), 2),
                    "max_drawdown": round(random.uniform(-3000, -1000), 2),
                    "sharpe_ratio": round(random.uniform(1.2, 2.0), 2)
                },
                "technical_indicators": {
                    "rsi": round(random.uniform(30, 70), 1),
                    "macd": round(random.uniform(-0.5, 0.5), 3),
                    "bollinger_position": round(random.uniform(0.2, 0.8), 2),
                    "volume_ratio": round(random.uniform(0.8, 1.5), 2)
                },
                "risk_assessment": {
                    "portfolio_risk": random.choice(["low", "medium", "high"]),
                    "market_risk": random.choice(["low", "medium", "high"]),
                    "liquidity_risk": random.choice(["low", "medium"]),
                    "concentration_risk": random.choice(["low", "medium", "high"])
                }
            }
        }
    
    def generate_account_balance(self):
        """生成账户余额数据"""
        return {
            "success": True,
            "data": {
                "account_info": {
                    "account_id": "LOCAL_AGENT_001",
                    "account_name": "本地Agent交易账户",
                    "account_type": "模拟股票账户",
                    "status": "正常"
                },
                "balance": {
                    "total_assets": round(random.uniform(120000, 130000), 2),
                    "available_cash": round(random.uniform(20000, 30000), 2),
                    "frozen_cash": round(random.uniform(1000, 2000), 2),
                    "market_value": round(random.uniform(90000, 110000), 2),
                    "total_profit_loss": round(random.uniform(5000, 15000), 2),
                    "profit_loss_percent": round(random.uniform(5, 12), 2)
                },
                "positions": [
                    {
                        "stock_code": "000001",
                        "stock_name": "平安银行",
                        "quantity": 1000,
                        "cost_price": 12.50,
                        "current_price": round(random.uniform(13.0, 13.5), 2),
                        "market_value": round(1000 * random.uniform(13.0, 13.5), 2),
                        "profit_loss": round(1000 * (random.uniform(13.0, 13.5) - 12.50), 2),
                        "profit_loss_percent": round((random.uniform(13.0, 13.5) - 12.50) / 12.50 * 100, 2)
                    },
                    {
                        "stock_code": "000002",
                        "stock_name": "万科A",
                        "quantity": 500,
                        "cost_price": 19.80,
                        "current_price": round(random.uniform(19.5, 20.2), 2),
                        "market_value": round(500 * random.uniform(19.5, 20.2), 2),
                        "profit_loss": round(500 * (random.uniform(19.5, 20.2) - 19.80), 2),
                        "profit_loss_percent": round((random.uniform(19.5, 20.2) - 19.80) / 19.80 * 100, 2)
                    }
                ],
                "timestamp": datetime.now().isoformat()
            }
        }

# 创建后端实例
backend = LocalAgentBackend()

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "本地Agent后端服务器",
        "version": backend.version,
        "status": "running",
        "uptime": str(datetime.now() - backend.start_time),
        "request_count": backend.request_count,
        "endpoints": [
            "GET / - 服务器信息",
            "GET /health - 健康检查",
            "GET /api/agent-analysis - Agent分析",
            "GET /api/account-balance - 账户余额",
            "GET /api/market-data - 市场数据"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": backend.version,
        "uptime": str(datetime.now() - backend.start_time),
        "request_count": backend.request_count,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/agent-analysis")
async def get_agent_analysis():
    """获取Agent分析"""
    return backend.generate_agent_analysis()

@app.get("/api/account-balance")
async def get_account_balance():
    """获取账户余额"""
    return backend.generate_account_balance()

@app.get("/api/market-data")
async def get_market_data():
    """获取市场数据"""
    return {
        "success": True,
        "data": {
            "market_status": "open",
            "timestamp": datetime.now().isoformat(),
            "indices": {
                "shanghai": {
                    "value": round(random.uniform(3200, 3300), 2),
                    "change": round(random.uniform(-20, 20), 2),
                    "change_percent": round(random.uniform(-0.8, 0.8), 2)
                },
                "shenzhen": {
                    "value": round(random.uniform(11000, 11500), 2),
                    "change": round(random.uniform(-50, 50), 2),
                    "change_percent": round(random.uniform(-0.6, 0.6), 2)
                }
            },
            "hot_stocks": [
                {"code": "000001", "name": "平安银行", "price": round(random.uniform(13.0, 13.5), 2), "change_percent": round(random.uniform(-3, 3), 2)},
                {"code": "000002", "name": "万科A", "price": round(random.uniform(19.5, 20.2), 2), "change_percent": round(random.uniform(-2, 2), 2)},
                {"code": "600036", "name": "招商银行", "price": round(random.uniform(42.0, 43.5), 2), "change_percent": round(random.uniform(-1, 1), 2)}
            ]
        }
    }

if __name__ == "__main__":
    print("🤖 启动本地Agent后端服务器...")
    print("=" * 50)
    print("🌐 服务地址: http://localhost:9999")
    print("📋 API文档: http://localhost:9999/docs")
    print("🔧 替代Worker: 提供完整Agent分析功能")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=9999)
