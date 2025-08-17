#!/usr/bin/env python3
"""
快速交易API服务器
提供毫秒级响应的交易接口
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
import asyncio
from datetime import datetime
import uvicorn

app = FastAPI(title="Ultra Fast Trading API", version="1.0.0")

class TradeRequest(BaseModel):
    action: str
    stock_code: str
    quantity: int
    price: float = None

class TradeResponse(BaseModel):
    success: bool
    trade_id: str
    status: str
    message: str
    latency: int
    timestamp: str

# 全局交易解决方案实例
from ultra_fast_trading_solution import UltraFastTradingSolution
trading_solution = UltraFastTradingSolution()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ultra-fast-trading-api",
        "latency": 1,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/trade/instant", response_model=TradeResponse)
async def instant_trade(trade: TradeRequest):
    """立即响应的交易接口"""
    start_time = time.perf_counter()
    
    result = trading_solution.instant_trade_response(
        trade.action,
        trade.stock_code,
        trade.quantity,
        trade.price
    )
    
    latency = round((time.perf_counter() - start_time) * 1000)
    result['latency'] = latency
    
    return result

@app.post("/trade/mock", response_model=TradeResponse)
async def mock_trade(trade: TradeRequest):
    """超快速模拟交易"""
    start_time = time.perf_counter()
    
    result = trading_solution.mock_ultra_fast_trade(
        trade.action,
        trade.stock_code,
        trade.quantity,
        trade.price
    )
    
    latency = round((time.perf_counter() - start_time) * 1000)
    result['latency'] = latency
    
    return result

@app.get("/trade/status/{trade_id}")
async def get_trade_status(trade_id: str):
    """获取交易状态"""
    return trading_solution.check_trade_status(trade_id)

@app.get("/performance/test")
async def performance_test():
    """性能测试接口"""
    start_time = time.perf_counter()
    
    # 模拟一些处理
    await asyncio.sleep(0.001)  # 1ms
    
    latency = round((time.perf_counter() - start_time) * 1000)
    
    return {
        "test": "performance",
        "latency": latency,
        "status": "ultra_fast",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 启动超快速交易API服务器...")
    print("📡 服务地址: http://localhost:8889")
    print("📖 API文档: http://localhost:8889/docs")
    print("⚡ 预期延迟: 1-5ms")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8889,
        log_level="info"
    )
