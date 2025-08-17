"""
简化版测试服务器
仅包含测试端点,用于前后端通信测试
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
import logging
import time
import random
from datetime import datetime
from typing import Dict, Any, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="通信测试服务",
    description="简化版测试服务器,用于前后端通信测试",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储连接的WebSocket客户端
websocket_connections = {}

# 活跃的订阅
active_subscriptions = {}

# 测试数据
test_data = {
    "echo": {
        "message": "Hello from backend!"
    },
    "stock": {
        "sh600000": {
            "code": "sh600000",
            "name": "浦发银行",
            "price": 10.56,
            "change": 0.23,
            "change_percent": 2.15,
            "volume": 12345678,
            "amount": 123456789.12,
            "market_cap": 300000000000,
            "pe_ratio": 12.34,
            "industry": "银行"
        },
        "sh601398": {
            "code": "sh601398",
            "name": "工商银行",
            "price": 5.67,
            "change": -0.12,
            "change_percent": -2.13,
            "volume": 23456789,
            "amount": 234567890.12,
            "market_cap": 2000000000000,
            "pe_ratio": 6.78,
            "industry": "银行"
        }
    }
}

# 测试数据生成器
async def generate_price_updates():
    """模拟股票价格更新"""
    logger.info("开始生成股票价格更新")
    while True:
        # 修改所有股票价格
        for code in test_data["stock"]:
            stock = test_data["stock"][code]
            # 随机价格变动 ±0.5%
            change = random.uniform(-0.005, 0.005) * stock["price"]
            stock["price"] = round(stock["price"] + change, 2)
            stock["change"] = round(stock["change"] + change, 2)
            stock["change_percent"] = round(stock["change"] / (stock["price"] - stock["change"]) * 100, 2)
            stock["timestamp"] = datetime.now().isoformat()
            
            # 推送到已订阅的客户端
            for client_id, subscriptions in active_subscriptions.items():
                if client_id in websocket_connections and "quote" in subscriptions:
                    if "code" not in subscriptions["quote"] or subscriptions["quote"]["code"] == code:
                        try:
                            message = {
                                "type": "quote",
                                "data": stock
                            }
                            await websocket_connections[client_id].send_text(json.dumps(message))
                        except Exception as e:
                            logger.error(f"发送WebSocket消息失败: {str(e)}")
        
        # 等待1秒
        await asyncio.sleep(1)

# 启动后台任务
background_task = None

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    global background_task
    logger.info("测试服务启动")
    background_task = asyncio.create_task(generate_price_updates())

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    if background_task:
        background_task.cancel()
    logger.info("测试服务关闭")

# ---------- API测试端点 ----------

@app.get("/api/test/ping")
async def ping():
    """简单的ping测试"""
    return {"message": "pong", "timestamp": time.time()}

@app.get("/api/test/echo")
async def echo(message: str = "Hello"):
    """回显消息"""
    return {"message": message, "timestamp": time.time()}

@app.post("/api/test/echo")
async def echo_post(data: Dict[str, Any]):
    """POST回显数据"""
    return {"data": data, "timestamp": time.time()}

@app.get("/api/test/delay")
async def delay(seconds: int = 1):
    """测试延迟响应"""
    if seconds > 10:
        seconds = 10  # 限制最大延迟
    await asyncio.sleep(seconds)
    return {"message": f"Delayed response after {seconds} seconds", "timestamp": time.time()}

@app.get("/api/test/error")
async def error(status_code: int = 500, message: str = "测试错误"):
    """测试错误响应"""
    raise HTTPException(status_code=status_code, detail=message)

@app.get("/api/test/stock")
async def get_stock(code: str):
    """获取股票数据"""
    if code not in test_data["stock"]:
        raise HTTPException(status_code=404, detail=f"股票代码 {code} 不存在")
    return {"data": test_data["stock"][code], "timestamp": time.time()}

@app.post("/api/test/evaluate")
async def evaluate_stock(data: Dict[str, Any]):
    """评估股票交易机会"""
    # 简单的模拟逻辑
    if "code" not in data:
        raise HTTPException(status_code=400, detail="缺少股票代码")
    
    code = data["code"]
    if code not in test_data["stock"]:
        raise HTTPException(status_code=404, detail=f"股票代码 {code} 不存在")
    
    stock = test_data["stock"][code]
    
    # 简单模拟的评估逻辑
    has_opportunity = stock["change_percent"] > 0
    
    return {
        "code": 200,
        "data": {
            "has_opportunity": has_opportunity,
            "mode": "positive" if has_opportunity else "negative",
            "suggested_quantity": 100,
            "expected_cost_impact": {
                "reduction_percentage": 0.8 if has_opportunity else 0.2
            },
            "message": "价格呈上升趋势,建议买入" if has_opportunity else "价格呈下降趋势,建议观望",
            "evaluation_method": "test"
        }
    }

# ---------- 模拟真实API端点 ----------

@app.get("/api/stock/quote")
async def stock_quote(code: str):
    """模拟股票行情接口"""
    if code not in test_data["stock"]:
        raise HTTPException(status_code=404, detail=f"股票代码 {code} 不存在")
    
    stock = test_data["stock"][code]
    return {
        "code": 200,
        "data": {
            "code": stock["code"],
            "name": stock["name"],
            "currentPrice": stock["price"],
            "open": stock["price"] - stock["change"],
            "high": stock["price"] * 1.01,
            "low": stock["price"] * 0.99,
            "volume": stock["volume"],
            "turnoverRate": random.uniform(1.0, 3.0),
            "lastUpdated": datetime.now().isoformat()
        }
    }

@app.post("/api/t-trading/evaluate-opportunity")
async def evaluate_opportunity(data: Dict[str, Any]):
    """模拟交易机会评估接口"""
    if "code" not in data:
        raise HTTPException(status_code=400, detail="缺少股票代码")
    
    code = data.get("code")
    if code not in test_data["stock"]:
        # 如果股票代码不存在,创建一个临时数据
        test_data["stock"][code] = {
            "code": code,
            "name": data.get("name", "未知股票"),
            "price": data.get("current_price", 10.0),
            "change": random.uniform(-0.5, 0.5),
            "change_percent": random.uniform(-5, 5),
            "volume": random.randint(1000000, 5000000),
            "amount": random.randint(10000000, 50000000),
            "market_cap": random.randint(1000000000, 5000000000),
            "pe_ratio": random.uniform(5, 20),
            "industry": "未知行业"
        }
        
    stock = test_data["stock"][code]
    has_opportunity = stock["change_percent"] > 0 or random.random() > 0.5
    
    return {
        "code": 200,
        "data": {
            "has_opportunity": has_opportunity,
            "mode": "positive" if has_opportunity else "negative",
            "suggested_quantity": random.randint(100, 500) // 100 * 100,
            "ai_confidence": random.uniform(0.6, 0.95),
            "expected_cost_impact": {
                "reduction_percentage": random.uniform(0.3, 1.2)
            },
            "message": "AI分析显示该股票当前走势强劲,建议买入" if has_opportunity else "AI分析显示该股票当前走势疲软,建议观望",
            "evaluation_method": "ai",
            "volatility": random.uniform(0.01, 0.05)
        }
    }

@app.post("/api/t-trading/record-trade")
async def record_trade(data: Dict[str, Any]):
    """模拟记录交易接口"""
    return {
        "code": 200,
        "data": {
            "trade_id": f"TR{int(time.time())}",
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "message": "交易记录成功"
        }
    }

@app.get("/api/t-trading/summary")
async def trading_summary():
    """模拟交易摘要接口"""
    return {
        "code": 200,
        "data": {
            "is_trading_day": True,
            "total_trades": random.randint(5, 20),
            "success_rate": random.uniform(0.6, 0.9),
            "total_profit": random.uniform(500, 2000),
            "active_positions": random.randint(1, 5)
        }
    }

# ---------- WebSocket测试端点 ----------

@app.websocket("/api/test/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket测试端点"""
    await websocket.accept()
    logger.info("WebSocket客户端连接")
    
    # 生成客户端ID
    client_id = str(id(websocket))
    websocket_connections[client_id] = websocket
    active_subscriptions[client_id] = {}
    
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"收到WebSocket消息: {data}")
            try:
                message = json.loads(data)
                message_type = message.get("type", "")
                
                # 处理不同类型的消息
                if message_type == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": time.time()
                    }))
                    logger.info("响应ping消息")
                
                elif message_type == "subscribe":
                    channel = message.get("channel", "")
                    params = message.get("params", {})
                    
                    if channel:
                        # 保存订阅
                        active_subscriptions[client_id][channel] = params
                        await websocket.send_text(json.dumps({
                            "type": "subscription",
                            "status": "success",
                            "channel": channel,
                            "params": params
                        }))
                        logger.info(f"客户端订阅: {channel}, 参数: {params}")
                
                elif message_type == "unsubscribe":
                    channel = message.get("channel", "")
                    
                    if channel and channel in active_subscriptions[client_id]:
                        # 删除订阅
                        del active_subscriptions[client_id][channel]
                        await websocket.send_text(json.dumps({
                            "type": "unsubscription",
                            "status": "success",
                            "channel": channel
                        }))
                        logger.info(f"客户端取消订阅: {channel}")
                
                else:
                    # 未知消息类型
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "error": f"未知消息类型: {message_type}"
                    }))
                    logger.warning(f"未知消息类型: {message_type}")
            
            except json.JSONDecodeError:
                # 无效的JSON
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": "无效的JSON数据"
                }))
                logger.error("无效的JSON数据")
            
            except Exception as e:
                # 其他错误
                logger.error(f"处理WebSocket消息时出错: {str(e)}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": f"处理消息时出错: {str(e)}"
                }))
    
    except WebSocketDisconnect:
        # 客户端断开连接
        if client_id in websocket_connections:
            del websocket_connections[client_id]
        if client_id in active_subscriptions:
            del active_subscriptions[client_id]
        logger.info(f"客户端 {client_id} 断开连接")
    
    except Exception as e:
        # 其他错误
        logger.error(f"WebSocket连接错误: {str(e)}")
        if client_id in websocket_connections:
            del websocket_connections[client_id]
        if client_id in active_subscriptions:
            del active_subscriptions[client_id]

if __name__ == "__main__":
    uvicorn.run("simple_test_server:app", host="0.0.0.0", port=8000, reload=True) 
 
