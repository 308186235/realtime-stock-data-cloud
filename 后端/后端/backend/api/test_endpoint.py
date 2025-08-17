"""
测试API端点模块
提供用于前后端通信测试的各种API端点
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from typing import Dict, Any, List, Optional
import asyncio
import json
import time
import logging
from datetime import datetime

# 创建路由器
router = APIRouter(prefix="/api/test", tags=["测试"])

# 日志配置
logger = logging.getLogger(__name__)

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
    import random
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

@router.on_event("startup")
async def startup_event():
    global background_task
    background_task = asyncio.create_task(generate_price_updates())

@router.on_event("shutdown")
async def shutdown_event():
    if background_task:
        background_task.cancel()

@router.get("/ping")
async def ping():
    """简单的ping测试"""
    return {"message": "pong", "timestamp": time.time()}

@router.get("/echo")
async def echo(message: str = "Hello"):
    """回显消息"""
    return {"message": message, "timestamp": time.time()}

@router.post("/echo")
async def echo_post(data: Dict[str, Any]):
    """POST回显数据"""
    return {"data": data, "timestamp": time.time()}

@router.get("/delay")
async def delay(seconds: int = 1):
    """测试延迟响应"""
    if seconds > 10:
        seconds = 10  # 限制最大延迟
    await asyncio.sleep(seconds)
    return {"message": f"Delayed response after {seconds} seconds", "timestamp": time.time()}

@router.get("/error")
async def error(status_code: int = 500, message: str = "测试错误"):
    """测试错误响应"""
    raise HTTPException(status_code=status_code, detail=message)

@router.get("/stock")
async def get_stock(code: str):
    """获取股票数据"""
    if code not in test_data["stock"]:
        raise HTTPException(status_code=404, detail=f"股票代码 {code} 不存在")
    return {"data": test_data["stock"][code], "timestamp": time.time()}

@router.post("/evaluate")
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

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket测试端点"""
    await websocket.accept()
    
    # 生成客户端ID
    client_id = str(id(websocket))
    websocket_connections[client_id] = websocket
    active_subscriptions[client_id] = {}
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                message_type = message.get("type", "")
                
                # 处理不同类型的消息
                if message_type == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": time.time()
                    }))
                
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
                
                else:
                    # 未知消息类型
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "error": f"未知消息类型: {message_type}"
                    }))
            
            except json.JSONDecodeError:
                # 无效的JSON
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": "无效的JSON数据"
                }))
            
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
 
