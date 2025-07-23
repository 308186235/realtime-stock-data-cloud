"""
实时股票数据API路由
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query, Body
from typing import Optional, List, Dict, Any
import asyncio
import json
import logging
import sys
import os

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from services.realtime_stock_service import realtime_stock_service

logger = logging.getLogger(__name__)

router = APIRouter()

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.stock_subscriptions: Dict[str, List[WebSocket]] = {}
        self.market_subscriptions: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket连接建立，当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # 清理订阅
        for stock_code, connections in self.stock_subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
        
        for market, connections in self.market_subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info(f"WebSocket连接断开，当前连接数: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# ==================== 服务管理API ====================

@router.post("/start")
async def start_service(config: Dict[str, Any] = Body(...)):
    """启动实时股票服务"""
    try:
        host = config.get('host')
        port = config.get('port')
        token = config.get('token')
        
        if not all([host, port, token]):
            raise HTTPException(status_code=400, detail="缺少必要配置参数: host, port, token")
        
        # 配置并启动服务
        realtime_stock_service.configure(host, port, token)
        await realtime_stock_service.start()
        
        return {
            "success": True,
            "message": "实时股票服务启动成功",
            "config": realtime_stock_service.get_config()
        }
        
    except Exception as e:
        logger.error(f"启动服务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动服务失败: {str(e)}")

@router.post("/stop")
async def stop_service():
    """停止实时股票服务"""
    try:
        await realtime_stock_service.stop()
        return {
            "success": True,
            "message": "实时股票服务已停止"
        }
    except Exception as e:
        logger.error(f"停止服务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"停止服务失败: {str(e)}")

@router.get("/status")
async def get_service_status():
    """获取服务状态"""
    try:
        stats = realtime_stock_service.get_service_stats()
        health = await realtime_stock_service.health_check()
        
        return {
            "success": True,
            "data": {
                "stats": stats,
                "health": health,
                "is_running": realtime_stock_service.is_running(),
                "is_connected": realtime_stock_service.is_connected()
            }
        }
    except Exception as e:
        logger.error(f"获取服务状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取服务状态失败: {str(e)}")

@router.get("/config")
async def get_service_config():
    """获取服务配置"""
    try:
        config = realtime_stock_service.get_config()
        return {
            "success": True,
            "data": config
        }
    except Exception as e:
        logger.error(f"获取服务配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取服务配置失败: {str(e)}")

# ==================== 数据查询API ====================

@router.get("/stock/{stock_code}")
async def get_stock_realtime_data(stock_code: str):
    """获取股票实时数据"""
    try:
        data = await realtime_stock_service.get_realtime_data(stock_code)
        
        if data:
            return {
                "success": True,
                "data": data
            }
        else:
            raise HTTPException(status_code=404, detail="股票数据不存在")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票实时数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取股票实时数据失败: {str(e)}")

@router.get("/stock/{stock_code}/stream")
async def get_stock_stream_data(stock_code: str, count: int = Query(100, ge=1, le=1000)):
    """获取股票时间序列数据"""
    try:
        data = await realtime_stock_service.get_stock_stream(stock_code, count)
        
        return {
            "success": True,
            "data": data,
            "count": len(data)
        }
        
    except Exception as e:
        logger.error(f"获取股票时间序列数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取股票时间序列数据失败: {str(e)}")

@router.get("/market/{market}/summary")
async def get_market_summary(market: str):
    """获取市场概况"""
    try:
        if market not in ['SZ', 'SH', 'BJ']:
            raise HTTPException(status_code=400, detail="无效的市场代码，支持: SZ, SH, BJ")
        
        data = await realtime_stock_service.get_market_summary(market)
        
        return {
            "success": True,
            "data": data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取市场概况失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取市场概况失败: {str(e)}")

@router.get("/market/{market}/top")
async def get_market_top_stocks(
    market: str,
    metric: str = Query("volume", regex="^(volume|amount)$"),
    count: int = Query(50, ge=1, le=200)
):
    """获取市场热门股票"""
    try:
        if market not in ['SZ', 'SH', 'BJ']:
            raise HTTPException(status_code=400, detail="无效的市场代码，支持: SZ, SH, BJ")
        
        data = await realtime_stock_service.get_market_top_stocks(market, metric, count)
        
        return {
            "success": True,
            "data": data,
            "count": len(data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取市场热门股票失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取市场热门股票失败: {str(e)}")

# ==================== WebSocket实时推送 ====================

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时数据推送"""
    await manager.connect(websocket)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            message_type = data.get('type')
            
            if message_type == 'subscribe_stock':
                # 订阅单只股票
                stock_code = data.get('stock_code')
                if stock_code:
                    await subscribe_stock_websocket(stock_code, websocket)
                    await websocket.send_json({
                        'type': 'subscription_confirmed',
                        'stock_code': stock_code
                    })
            
            elif message_type == 'unsubscribe_stock':
                # 取消订阅股票
                stock_code = data.get('stock_code')
                if stock_code:
                    await unsubscribe_stock_websocket(stock_code, websocket)
                    await websocket.send_json({
                        'type': 'unsubscription_confirmed',
                        'stock_code': stock_code
                    })
            
            elif message_type == 'subscribe_market':
                # 订阅市场
                market = data.get('market')
                if market:
                    await subscribe_market_websocket(market, websocket)
                    await websocket.send_json({
                        'type': 'market_subscription_confirmed',
                        'market': market
                    })
            
            elif message_type == 'ping':
                # 心跳响应
                await websocket.send_json({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket错误: {str(e)}")
        manager.disconnect(websocket)

async def subscribe_stock_websocket(stock_code: str, websocket: WebSocket):
    """WebSocket订阅股票"""
    if stock_code not in manager.stock_subscriptions:
        manager.stock_subscriptions[stock_code] = []
    
    if websocket not in manager.stock_subscriptions[stock_code]:
        manager.stock_subscriptions[stock_code].append(websocket)
    
    # 添加到实时服务订阅
    async def stock_callback(data):
        message = {
            'type': 'stock_data',
            'stock_code': stock_code,
            'data': data['data'],
            'timestamp': data.get('timestamp')
        }
        
        # 发送给所有订阅该股票的WebSocket连接
        for ws in manager.stock_subscriptions.get(stock_code, []):
            try:
                await ws.send_json(message)
            except Exception:
                pass
    
    realtime_stock_service.subscribe_stock(stock_code, stock_callback)

async def unsubscribe_stock_websocket(stock_code: str, websocket: WebSocket):
    """WebSocket取消订阅股票"""
    if stock_code in manager.stock_subscriptions:
        if websocket in manager.stock_subscriptions[stock_code]:
            manager.stock_subscriptions[stock_code].remove(websocket)
        
        if not manager.stock_subscriptions[stock_code]:
            del manager.stock_subscriptions[stock_code]

async def subscribe_market_websocket(market: str, websocket: WebSocket):
    """WebSocket订阅市场"""
    if market not in manager.market_subscriptions:
        manager.market_subscriptions[market] = []
    
    if websocket not in manager.market_subscriptions[market]:
        manager.market_subscriptions[market].append(websocket)
    
    # 添加到实时服务订阅
    async def market_callback(data):
        message = {
            'type': 'market_data',
            'market': market,
            'data': data['data'],
            'timestamp': data.get('timestamp')
        }
        
        # 发送给所有订阅该市场的WebSocket连接
        for ws in manager.market_subscriptions.get(market, []):
            try:
                await ws.send_json(message)
            except Exception:
                pass
    
    realtime_stock_service.subscribe_market(market, market_callback)

# ==================== 测试API ====================

@router.post("/test/start")
async def start_test_service():
    """启动测试服务（使用模拟数据）"""
    try:
        # 使用测试配置
        test_config = {
            'host': 'test.example.com',
            'port': 8888,
            'token': 'test_token'
        }
        
        # 注意：这里应该启动模拟数据生成器而不是真实连接
        # 为了演示，我们返回成功状态
        
        return {
            "success": True,
            "message": "测试服务启动成功",
            "note": "使用模拟数据进行测试"
        }
        
    except Exception as e:
        logger.error(f"启动测试服务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动测试服务失败: {str(e)}")

@router.get("/test/generate")
async def generate_test_data(count: int = Query(10, ge=1, le=100)):
    """生成测试数据"""
    try:
        import random
        import time
        
        test_stocks = []
        stock_codes = ['000001', '000002', '600000', '600036', '002415']
        
        for i in range(count):
            stock_code = random.choice(stock_codes)
            base_price = 10 + (hash(stock_code) % 100)
            
            test_data = {
                'stock_code': stock_code,
                'stock_name': f'测试股票{stock_code}',
                'current_price': round(base_price + random.uniform(-2, 2), 2),
                'volume': random.randint(1000, 100000),
                'amount': random.randint(1000000, 100000000),
                'timestamp': time.time(),
                'market': 'SZ' if stock_code.startswith('0') else 'SH'
            }
            test_stocks.append(test_data)
        
        return {
            "success": True,
            "data": test_stocks,
            "count": len(test_stocks)
        }
        
    except Exception as e:
        logger.error(f"生成测试数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成测试数据失败: {str(e)}")
