"""
简化版实时股票数据API路由 - 不依赖Redis
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query, Body
from typing import Optional, List, Dict, Any
import asyncio
import json
import logging
import time
import random
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

router = APIRouter()

# 模拟数据存储
class SimpleStockStorage:
    def __init__(self):
        self.stock_data: Dict[str, Dict] = {}
        self.stock_streams: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.market_stats = {
            'SZ': {'volume_top': [], 'amount_top': []},
            'SH': {'volume_top': [], 'amount_top': []},
            'BJ': {'volume_top': [], 'amount_top': []}
        }
        
        # 生成一些模拟数据
        self._generate_mock_data()
    
    def _generate_mock_data(self):
        """生成模拟数据"""
        stock_codes = [
            '000001', '000002', '000858', '002415', '002594',
            '600000', '600036', '600519', '600887', '601318',
            '833171', '833519', '835185', '871981', '873169'
        ]
        
        for code in stock_codes:
            market = 'BJ' if code.startswith('8') else ('SH' if code.startswith('6') else 'SZ')
            base_price = 10 + (hash(code) % 100)
            
            stock_data = {
                'stock_code': code,
                'stock_name': f'股票{code}',
                'current_price': round(base_price + random.uniform(-2, 2), 2),
                'open_price': round(base_price + random.uniform(-1, 1), 2),
                'high_price': round(base_price + random.uniform(0, 3), 2),
                'low_price': round(base_price + random.uniform(-3, 0), 2),
                'last_close': base_price,
                'volume': random.randint(10000, 1000000),
                'amount': random.randint(10000000, 1000000000),
                'turnover_rate': round(random.uniform(0.1, 5.0), 2),
                'market': market,
                'timestamp': time.time(),
                'ask_prices': [base_price + i * 0.01 for i in range(1, 6)],
                'bid_prices': [base_price - i * 0.01 for i in range(1, 6)],
                'ask_volumes': [random.randint(100, 10000) for _ in range(5)],
                'bid_volumes': [random.randint(100, 10000) for _ in range(5)]
            }
            
            # 计算涨跌
            change = stock_data['current_price'] - stock_data['last_close']
            change_percent = (change / stock_data['last_close']) * 100 if stock_data['last_close'] > 0 else 0
            stock_data['change'] = round(change, 2)
            stock_data['change_percent'] = round(change_percent, 2)
            
            self.stock_data[code] = stock_data
            
            # 添加到流数据
            self.stock_streams[code].append({
                'timestamp': stock_data['timestamp'],
                'price': stock_data['current_price'],
                'volume': stock_data['volume'],
                'amount': stock_data['amount']
            })
    
    def get_stock_data(self, stock_code: str) -> Optional[Dict]:
        return self.stock_data.get(stock_code)
    
    def get_stock_stream(self, stock_code: str, count: int = 100) -> List[Dict]:
        stream_data = list(self.stock_streams[stock_code])
        return stream_data[-count:] if len(stream_data) > count else stream_data
    
    def get_market_top_stocks(self, market: str, metric: str = 'volume', count: int = 50) -> List[Dict]:
        market_stocks = [data for data in self.stock_data.values() if data['market'] == market]
        sorted_stocks = sorted(market_stocks, key=lambda x: x.get(metric, 0), reverse=True)
        return sorted_stocks[:count]
    
    def update_stock_data(self, stock_code: str, updates: Dict):
        if stock_code in self.stock_data:
            self.stock_data[stock_code].update(updates)
            self.stock_data[stock_code]['timestamp'] = time.time()

# 全局存储实例
simple_storage = SimpleStockStorage()

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.stock_subscriptions: Dict[str, List[WebSocket]] = defaultdict(list)
        self.market_subscriptions: Dict[str, List[WebSocket]] = defaultdict(list)
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket连接建立，当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # 清理订阅
        for connections in self.stock_subscriptions.values():
            if websocket in connections:
                connections.remove(websocket)
        
        for connections in self.market_subscriptions.values():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info(f"WebSocket连接断开，当前连接数: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")

manager = ConnectionManager()

# 模拟实时数据推送任务
async def simulate_realtime_data():
    """模拟实时数据推送"""
    while True:
        try:
            # 随机更新一些股票数据
            stock_codes = list(simple_storage.stock_data.keys())
            update_codes = random.sample(stock_codes, min(10, len(stock_codes)))
            
            for stock_code in update_codes:
                current_data = simple_storage.stock_data[stock_code]
                base_price = current_data['current_price']
                
                # 随机价格变动
                price_change = random.uniform(-0.5, 0.5)
                new_price = max(0.01, base_price + price_change)
                
                updates = {
                    'current_price': round(new_price, 2),
                    'volume': current_data['volume'] + random.randint(100, 10000),
                    'amount': current_data['amount'] + random.randint(100000, 10000000)
                }
                
                # 重新计算涨跌
                change = new_price - current_data['last_close']
                change_percent = (change / current_data['last_close']) * 100 if current_data['last_close'] > 0 else 0
                updates['change'] = round(change, 2)
                updates['change_percent'] = round(change_percent, 2)
                
                simple_storage.update_stock_data(stock_code, updates)
                
                # 推送给订阅者
                if stock_code in manager.stock_subscriptions:
                    message = {
                        'type': 'stock_data',
                        'stock_code': stock_code,
                        'data': simple_storage.get_stock_data(stock_code),
                        'timestamp': time.time()
                    }
                    
                    for websocket in manager.stock_subscriptions[stock_code]:
                        try:
                            await websocket.send_json(message)
                        except Exception:
                            pass
            
            await asyncio.sleep(3)  # 3秒推送一次
            
        except Exception as e:
            logger.error(f"模拟数据推送错误: {str(e)}")
            await asyncio.sleep(1)

# 模拟数据推送任务将在应用启动时启动
_simulation_task = None

async def start_simulation():
    """启动模拟数据推送"""
    global _simulation_task
    if _simulation_task is None:
        _simulation_task = asyncio.create_task(simulate_realtime_data())

async def stop_simulation():
    """停止模拟数据推送"""
    global _simulation_task
    if _simulation_task:
        _simulation_task.cancel()
        _simulation_task = None

# ==================== API端点 ====================

@router.get("/status")
async def get_service_status():
    """获取服务状态"""
    return {
        "success": True,
        "data": {
            "status": "running",
            "is_connected": True,
            "stock_count": len(simple_storage.stock_data),
            "connection_count": len(manager.active_connections),
            "timestamp": time.time()
        }
    }

@router.get("/config")
async def get_service_config():
    """获取服务配置"""
    return {
        "success": True,
        "data": {
            "api_key": "QT_wat5QfcJ6N9pDZM5",
            "mode": "simulation",
            "push_interval": 3,
            "stock_count": len(simple_storage.stock_data)
        }
    }

@router.post("/start")
async def start_service(config: Dict[str, Any] = Body(...)):
    """启动服务（模拟）"""
    return {
        "success": True,
        "message": "模拟服务已启动",
        "config": config
    }

@router.post("/stop")
async def stop_service():
    """停止服务（模拟）"""
    return {
        "success": True,
        "message": "模拟服务已停止"
    }

@router.get("/stock/{stock_code}")
async def get_stock_realtime_data(stock_code: str):
    """获取股票实时数据"""
    data = simple_storage.get_stock_data(stock_code)
    
    if data:
        return {
            "success": True,
            "data": data
        }
    else:
        raise HTTPException(status_code=404, detail="股票数据不存在")

@router.get("/stock/{stock_code}/stream")
async def get_stock_stream_data(stock_code: str, count: int = Query(100, ge=1, le=1000)):
    """获取股票时间序列数据"""
    data = simple_storage.get_stock_stream(stock_code, count)
    
    return {
        "success": True,
        "data": data,
        "count": len(data)
    }

@router.get("/market/{market}/summary")
async def get_market_summary(market: str):
    """获取市场概况"""
    if market not in ['SZ', 'SH', 'BJ']:
        raise HTTPException(status_code=400, detail="无效的市场代码，支持: SZ, SH, BJ")
    
    top_volume = simple_storage.get_market_top_stocks(market, 'volume', 20)
    top_amount = simple_storage.get_market_top_stocks(market, 'amount', 20)
    
    return {
        "success": True,
        "data": {
            'market': market,
            'top_volume': top_volume,
            'top_amount': top_amount,
            'timestamp': time.time()
        }
    }

@router.get("/market/{market}/top")
async def get_market_top_stocks(
    market: str,
    metric: str = Query("volume", regex="^(volume|amount)$"),
    count: int = Query(50, ge=1, le=200)
):
    """获取市场热门股票"""
    if market not in ['SZ', 'SH', 'BJ']:
        raise HTTPException(status_code=400, detail="无效的市场代码，支持: SZ, SH, BJ")
    
    data = simple_storage.get_market_top_stocks(market, metric, count)
    
    return {
        "success": True,
        "data": data,
        "count": len(data)
    }

@router.get("/test/generate")
async def generate_test_data(count: int = Query(10, ge=1, le=100)):
    """生成测试数据"""
    test_stocks = []
    stock_codes = list(simple_storage.stock_data.keys())
    selected_codes = random.sample(stock_codes, min(count, len(stock_codes)))
    
    for stock_code in selected_codes:
        data = simple_storage.get_stock_data(stock_code)
        if data:
            test_stocks.append(data)
    
    return {
        "success": True,
        "data": test_stocks,
        "count": len(test_stocks)
    }

@router.post("/test/start")
async def start_test_service():
    """启动测试服务"""
    return {
        "success": True,
        "message": "测试服务启动成功",
        "note": "使用模拟数据进行测试"
    }

# ==================== WebSocket端点 ====================

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时数据推送"""
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get('type')
            
            if message_type == 'subscribe_stock':
                stock_code = data.get('stock_code')
                if stock_code:
                    manager.stock_subscriptions[stock_code].append(websocket)
                    await websocket.send_json({
                        'type': 'subscription_confirmed',
                        'stock_code': stock_code
                    })
            
            elif message_type == 'unsubscribe_stock':
                stock_code = data.get('stock_code')
                if stock_code and websocket in manager.stock_subscriptions[stock_code]:
                    manager.stock_subscriptions[stock_code].remove(websocket)
                    await websocket.send_json({
                        'type': 'unsubscription_confirmed',
                        'stock_code': stock_code
                    })
            
            elif message_type == 'subscribe_market':
                market = data.get('market')
                if market:
                    manager.market_subscriptions[market].append(websocket)
                    await websocket.send_json({
                        'type': 'market_subscription_confirmed',
                        'market': market
                    })
            
            elif message_type == 'ping':
                await websocket.send_json({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket错误: {str(e)}")
        manager.disconnect(websocket)
