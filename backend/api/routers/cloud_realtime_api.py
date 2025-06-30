"""
云端实时股票数据API
专为云端部署优化的实时数据推送服务
API Key: QT_wat5QfcJ6N9pDZM5
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query, Body
from typing import Dict, List, Any, Optional
import asyncio
import json
import time
import logging
import random
from datetime import datetime, timedelta
from collections import defaultdict, deque
import os

logger = logging.getLogger(__name__)

router = APIRouter()

class CloudRealtimeManager:
    """云端实时数据管理器"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, List[str]] = defaultdict(list)  # stock_code -> [connection_ids]
        self.stock_data: Dict[str, Dict] = {}
        self.push_task: Optional[asyncio.Task] = None
        self.running = False
        
        # 配置
        self.config = {
            'api_key': 'QT_wat5QfcJ6N9pDZM5',
            'push_interval': 3,
            'max_connections': 100,
            'heartbeat_interval': 30
        }
        
        # 统计信息
        self.stats = {
            'start_time': time.time(),
            'total_connections': 0,
            'active_connections': 0,
            'total_messages': 0,
            'total_subscriptions': 0,
            'data_points_sent': 0
        }
        
        # 监控的股票列表
        self.monitor_stocks = [
            '000001', '600000', '600519', '000858', '002415',
            '600036', '300059', '002594', '300750', '000002',
            '601318', '600036', '002304', '300014', '000725'
        ]
        
        # 初始化模拟数据
        self._init_mock_data()
    
    def _init_mock_data(self):
        """初始化模拟股票数据"""
        stock_names = {
            '000001': '平安银行', '600000': '浦发银行', '600519': '贵州茅台',
            '000858': '五粮液', '002415': '海康威视', '600036': '招商银行',
            '300059': '东方财富', '002594': '比亚迪', '300750': '宁德时代',
            '000002': '万科A', '601318': '中国平安', '002304': '洋河股份',
            '300014': '亿纬锂能', '000725': '京东方A'
        }
        
        base_prices = {
            '000001': 12.50, '600000': 10.80, '600519': 1680.00,
            '000858': 128.50, '002415': 39.20, '600036': 42.80,
            '300059': 18.90, '002594': 245.60, '300750': 185.30,
            '000002': 18.45, '601318': 45.20, '002304': 98.70,
            '300014': 78.90, '000725': 4.25
        }
        
        for stock_code in self.monitor_stocks:
            base_price = base_prices.get(stock_code, 20.00)
            last_close = base_price * random.uniform(0.95, 1.05)
            current_price = last_close * random.uniform(0.98, 1.02)
            
            self.stock_data[stock_code] = {
                'code': stock_code,
                'name': stock_names.get(stock_code, f'股票{stock_code}'),
                'price': round(current_price, 2),
                'last_close': round(last_close, 2),
                'change': round(current_price - last_close, 2),
                'change_percent': round((current_price - last_close) / last_close * 100, 2),
                'volume': random.randint(1000000, 50000000),
                'amount': random.randint(100000000, 2000000000),
                'open': round(last_close * random.uniform(0.99, 1.01), 2),
                'high': round(current_price * random.uniform(1.0, 1.03), 2),
                'low': round(current_price * random.uniform(0.97, 1.0), 2),
                'timestamp': time.time()
            }
    
    def is_market_time(self) -> bool:
        """检查是否在交易时间"""
        now = datetime.now()
        hour = now.hour
        day = now.weekday()  # 0=周一, 6=周日
        
        # 工作日 9:00-15:00
        return day < 5 and 9 <= hour < 15
    
    async def add_connection(self, connection_id: str, websocket: WebSocket):
        """添加WebSocket连接"""
        if len(self.connections) >= self.config['max_connections']:
            raise HTTPException(status_code=429, detail="连接数量已达上限")
        
        self.connections[connection_id] = websocket
        self.stats['total_connections'] += 1
        self.stats['active_connections'] = len(self.connections)
        
        logger.info(f"新连接: {connection_id}, 当前活跃连接: {self.stats['active_connections']}")
        
        # 发送欢迎消息
        await self.send_to_connection(connection_id, {
            'type': 'welcome',
            'connection_id': connection_id,
            'api_key': self.config['api_key'],
            'market_time': self.is_market_time(),
            'available_stocks': self.monitor_stocks,
            'timestamp': time.time()
        })
    
    async def remove_connection(self, connection_id: str):
        """移除WebSocket连接"""
        if connection_id in self.connections:
            del self.connections[connection_id]
            
            # 清理订阅
            for stock_code, subscribers in self.subscriptions.items():
                if connection_id in subscribers:
                    subscribers.remove(connection_id)
            
            self.stats['active_connections'] = len(self.connections)
            logger.info(f"连接断开: {connection_id}, 当前活跃连接: {self.stats['active_connections']}")
    
    async def send_to_connection(self, connection_id: str, message: Dict):
        """发送消息到指定连接"""
        if connection_id in self.connections:
            try:
                await self.connections[connection_id].send_text(json.dumps(message))
                self.stats['total_messages'] += 1
                return True
            except Exception as e:
                logger.error(f"发送消息失败 {connection_id}: {str(e)}")
                await self.remove_connection(connection_id)
                return False
        return False
    
    async def subscribe_stock(self, connection_id: str, stock_code: str):
        """订阅股票"""
        if stock_code not in self.monitor_stocks:
            await self.send_to_connection(connection_id, {
                'type': 'error',
                'message': f'不支持的股票代码: {stock_code}',
                'timestamp': time.time()
            })
            return False
        
        if connection_id not in self.subscriptions[stock_code]:
            self.subscriptions[stock_code].append(connection_id)
            self.stats['total_subscriptions'] += 1
            
            # 发送订阅确认
            await self.send_to_connection(connection_id, {
                'type': 'subscription_confirmed',
                'stock_code': stock_code,
                'timestamp': time.time()
            })
            
            # 立即发送当前数据
            if stock_code in self.stock_data:
                await self.send_to_connection(connection_id, {
                    'type': 'stock_data',
                    'stock_code': stock_code,
                    'data': self.stock_data[stock_code],
                    'timestamp': time.time()
                })
            
            logger.info(f"订阅成功: {connection_id} -> {stock_code}")
            return True
        
        return False
    
    async def unsubscribe_stock(self, connection_id: str, stock_code: str):
        """取消订阅股票"""
        if connection_id in self.subscriptions[stock_code]:
            self.subscriptions[stock_code].remove(connection_id)
            
            await self.send_to_connection(connection_id, {
                'type': 'unsubscription_confirmed',
                'stock_code': stock_code,
                'timestamp': time.time()
            })
            
            logger.info(f"取消订阅: {connection_id} -> {stock_code}")
            return True
        
        return False
    
    def update_stock_data(self):
        """更新股票数据"""
        for stock_code, data in self.stock_data.items():
            # 模拟价格变动
            change_percent = random.uniform(-0.02, 0.02)  # -2% 到 +2%
            new_price = data['price'] * (1 + change_percent)
            
            # 更新数据
            data['price'] = round(new_price, 2)
            data['change'] = round(new_price - data['last_close'], 2)
            data['change_percent'] = round((new_price - data['last_close']) / data['last_close'] * 100, 2)
            data['volume'] += random.randint(10000, 100000)
            data['amount'] += random.randint(1000000, 10000000)
            data['high'] = max(data['high'], new_price)
            data['low'] = min(data['low'], new_price)
            data['timestamp'] = time.time()
    
    async def broadcast_data(self):
        """广播数据到订阅者"""
        while self.running:
            try:
                # 更新股票数据
                self.update_stock_data()
                
                # 广播到订阅者
                for stock_code, subscribers in self.subscriptions.items():
                    if subscribers and stock_code in self.stock_data:
                        message = {
                            'type': 'stock_data',
                            'stock_code': stock_code,
                            'data': self.stock_data[stock_code],
                            'timestamp': time.time()
                        }
                        
                        # 发送给所有订阅者
                        for connection_id in subscribers[:]:  # 使用切片避免修改时的问题
                            success = await self.send_to_connection(connection_id, message)
                            if success:
                                self.stats['data_points_sent'] += 1
                
                # 等待下次推送
                await asyncio.sleep(self.config['push_interval'])
                
            except Exception as e:
                logger.error(f"广播数据错误: {str(e)}")
                await asyncio.sleep(1)
    
    async def start(self):
        """启动服务"""
        if not self.running:
            self.running = True
            self.stats['start_time'] = time.time()
            self.push_task = asyncio.create_task(self.broadcast_data())
            logger.info("云端实时数据服务已启动")
    
    async def stop(self):
        """停止服务"""
        self.running = False
        if self.push_task:
            self.push_task.cancel()
            try:
                await self.push_task
            except asyncio.CancelledError:
                pass
        logger.info("云端实时数据服务已停止")

# 全局管理器实例
cloud_manager = CloudRealtimeManager()

@router.on_event("startup")
async def startup_event():
    """启动事件"""
    await cloud_manager.start()

@router.on_event("shutdown") 
async def shutdown_event():
    """关闭事件"""
    await cloud_manager.stop()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点"""
    await websocket.accept()
    
    connection_id = f"conn_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
    
    try:
        await cloud_manager.add_connection(connection_id, websocket)
        
        while True:
            try:
                # 接收消息
                data = await websocket.receive_text()
                message = json.loads(data)
                
                message_type = message.get('type')
                
                if message_type == 'subscribe':
                    stock_code = message.get('stock_code')
                    if stock_code:
                        await cloud_manager.subscribe_stock(connection_id, stock_code)
                
                elif message_type == 'unsubscribe':
                    stock_code = message.get('stock_code')
                    if stock_code:
                        await cloud_manager.unsubscribe_stock(connection_id, stock_code)
                
                elif message_type == 'ping':
                    await cloud_manager.send_to_connection(connection_id, {
                        'type': 'pong',
                        'timestamp': time.time()
                    })
                
                elif message_type == 'get_stats':
                    await cloud_manager.send_to_connection(connection_id, {
                        'type': 'stats',
                        'data': cloud_manager.stats,
                        'timestamp': time.time()
                    })
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await cloud_manager.send_to_connection(connection_id, {
                    'type': 'error',
                    'message': '消息格式错误',
                    'timestamp': time.time()
                })
            except Exception as e:
                logger.error(f"WebSocket消息处理错误: {str(e)}")
                break
    
    except Exception as e:
        logger.error(f"WebSocket连接错误: {str(e)}")
    finally:
        await cloud_manager.remove_connection(connection_id)

@router.get("/test")
async def test_cloud_service():
    """测试云端服务"""
    return {
        "success": True,
        "message": "云端实时股票数据服务正常运行",
        "api_key": cloud_manager.config['api_key'],
        "service": "Cloud Realtime Stock Data",
        "version": "1.0.0",
        "market_time": cloud_manager.is_market_time(),
        "stats": cloud_manager.stats,
        "available_stocks": cloud_manager.monitor_stocks,
        "timestamp": time.time()
    }

@router.get("/health")
async def health_check():
    """健康检查"""
    uptime = time.time() - cloud_manager.stats['start_time']
    
    return {
        "status": "healthy",
        "service": "cloud-realtime-stock-data",
        "api_key": cloud_manager.config['api_key'],
        "uptime_seconds": round(uptime, 2),
        "active_connections": cloud_manager.stats['active_connections'],
        "total_messages": cloud_manager.stats['total_messages'],
        "market_time": cloud_manager.is_market_time(),
        "timestamp": time.time()
    }

@router.get("/stats")
async def get_service_stats():
    """获取服务统计"""
    uptime = time.time() - cloud_manager.stats['start_time']
    
    return {
        "success": True,
        "stats": {
            **cloud_manager.stats,
            "uptime_seconds": round(uptime, 2),
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "market_time": cloud_manager.is_market_time(),
            "subscriptions_by_stock": {
                stock: len(subscribers) 
                for stock, subscribers in cloud_manager.subscriptions.items()
            }
        },
        "timestamp": time.time()
    }

@router.get("/stocks")
async def get_available_stocks():
    """获取可用股票列表"""
    return {
        "success": True,
        "stocks": cloud_manager.monitor_stocks,
        "count": len(cloud_manager.monitor_stocks),
        "timestamp": time.time()
    }

@router.get("/stocks/{stock_code}")
async def get_stock_data(stock_code: str):
    """获取指定股票数据"""
    if stock_code not in cloud_manager.stock_data:
        raise HTTPException(status_code=404, detail="股票代码不存在")
    
    return {
        "success": True,
        "stock_code": stock_code,
        "data": cloud_manager.stock_data[stock_code],
        "timestamp": time.time()
    }
