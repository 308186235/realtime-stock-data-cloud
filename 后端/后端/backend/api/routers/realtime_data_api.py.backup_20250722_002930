"""
实时数据API - 基于新的实时数据管理器
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query
from typing import List, Optional, Dict, Any
import logging
import json
import asyncio
import time

from services.realtime_data_manager import realtime_data_manager

logger = logging.getLogger(__name__)

router = APIRouter()

# WebSocket连接管理器
class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.stock_subscriptions: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket连接建立，当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # 从股票订阅中移除
        for stock_code, connections in self.stock_subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info(f"WebSocket连接断开，当前连接数: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(message)
            except Exception:
                self.active_connections.remove(connection)

manager = WebSocketManager()

@router.get("/stocks")
async def get_all_stocks():
    """获取所有股票数据"""
    try:
        stocks = realtime_data_manager.get_all_stocks()
        return {
            "success": True,
            "data": stocks,
            "count": len(stocks),
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"获取股票数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{stock_code}")
async def get_stock_data(stock_code: str):
    """获取单只股票数据"""
    try:
        stock_data = realtime_data_manager.get_stock_data(stock_code)
        if stock_data:
            return {
                "success": True,
                "data": stock_data
            }
        else:
            raise HTTPException(status_code=404, detail="股票不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats():
    """获取实时数据统计信息"""
    try:
        stats = realtime_data_manager.get_stats()
        stats['websocket_connections'] = len(manager.active_connections)
        stats['stock_subscriptions'] = len(manager.stock_subscriptions)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时数据推送"""
    await manager.connect(websocket)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # 订阅股票
                stock_code = data.get('stock_code')
                if stock_code:
                    await subscribe_stock(stock_code, websocket)
                    await websocket.send_json({
                        'type': 'subscription_confirmed',
                        'stock_code': stock_code,
                        'message': f'已订阅 {stock_code}'
                    })
            
            elif message_type == 'unsubscribe':
                # 取消订阅
                stock_code = data.get('stock_code')
                if stock_code:
                    await unsubscribe_stock(stock_code, websocket)
                    await websocket.send_json({
                        'type': 'unsubscription_confirmed',
                        'stock_code': stock_code,
                        'message': f'已取消订阅 {stock_code}'
                    })
            
            elif message_type == 'get_stock':
                # 获取股票数据
                stock_code = data.get('stock_code')
                if stock_code:
                    stock_data = realtime_data_manager.get_stock_data(stock_code)
                    await websocket.send_json({
                        'type': 'stock_data',
                        'stock_code': stock_code,
                        'data': stock_data,
                        'timestamp': time.time()
                    })
            
            elif message_type == 'ping':
                # 心跳检测
                await websocket.send_json({
                    'type': 'pong',
                    'timestamp': time.time()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket错误: {str(e)}")
        manager.disconnect(websocket)

async def subscribe_stock(stock_code: str, websocket: WebSocket):
    """订阅股票数据"""
    if stock_code not in manager.stock_subscriptions:
        manager.stock_subscriptions[stock_code] = []
    
    if websocket not in manager.stock_subscriptions[stock_code]:
        manager.stock_subscriptions[stock_code].append(websocket)
    
    # 创建回调函数
    async def stock_callback(data):
        # 发送给所有订阅该股票的WebSocket连接
        for ws in manager.stock_subscriptions.get(stock_code, []):
            try:
                await ws.send_json(data)
            except Exception:
                # 移除失效的连接
                if ws in manager.stock_subscriptions[stock_code]:
                    manager.stock_subscriptions[stock_code].remove(ws)
    
    # 注册到实时数据管理器
    realtime_data_manager.subscribe_stock(stock_code, stock_callback)
    
    # 立即发送当前数据
    current_data = realtime_data_manager.get_stock_data(stock_code)
    if current_data:
        await websocket.send_json({
            'type': 'stock_data',
            'stock_code': stock_code,
            'data': current_data,
            'timestamp': time.time()
        })

async def unsubscribe_stock(stock_code: str, websocket: WebSocket):
    """取消订阅股票数据"""
    if stock_code in manager.stock_subscriptions:
        if websocket in manager.stock_subscriptions[stock_code]:
            manager.stock_subscriptions[stock_code].remove(websocket)
        
        # 如果没有订阅者了，从实时数据管理器中取消订阅
        if not manager.stock_subscriptions[stock_code]:
            del manager.stock_subscriptions[stock_code]
            # 注意：这里需要传递正确的回调函数，暂时跳过
            # realtime_data_manager.unsubscribe_stock(stock_code, callback)

@router.get("/test")
async def test_realtime_data():
    """测试实时数据功能"""
    try:
        # 获取一些测试数据
        test_stocks = ['000001', '600000', '600519']
        results = {}
        
        for stock_code in test_stocks:
            data = realtime_data_manager.get_stock_data(stock_code)
            if data:
                results[stock_code] = data
        
        stats = realtime_data_manager.get_stats()
        
        return {
            "success": True,
            "message": "实时数据功能正常",
            "test_data": results,
            "stats": stats,
            "websocket_url": "/api/realtime-data/ws"
        }
        
    except Exception as e:
        logger.error(f"测试实时数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate_trade")
async def simulate_trade(trade_data: Dict[str, Any]):
    """模拟交易，触发价格变动"""
    try:
        stock_code = trade_data.get('stock_code')
        trade_type = trade_data.get('type', 'buy')  # buy or sell
        volume = trade_data.get('volume', 1000)
        
        if not stock_code:
            raise HTTPException(status_code=400, detail="缺少股票代码")
        
        # 获取当前股票数据
        current_data = realtime_data_manager.get_stock_data(stock_code)
        if not current_data:
            raise HTTPException(status_code=404, detail="股票不存在")
        
        # 模拟价格影响
        import random
        if trade_type == 'buy':
            price_impact = random.uniform(0.1, 0.5)  # 买入推高价格
        else:
            price_impact = random.uniform(-0.5, -0.1)  # 卖出压低价格
        
        # 这里可以直接修改股票数据来模拟交易影响
        # 实际应用中应该通过更复杂的机制来处理
        
        return {
            "success": True,
            "message": f"模拟{trade_type}交易成功",
            "stock_code": stock_code,
            "volume": volume,
            "price_impact": price_impact,
            "current_price": current_data['price']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"模拟交易失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
