"""
实时数据管理器 - 统一管理实时股票数据推送
支持真实数据源和模拟数据源的切换
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
import json

from config.settings import (
    MARKET_DATA_API_KEY, MARKET_DATA_HOST, MARKET_DATA_PORT, MARKET_DATA_TOKEN,
    REALTIME_DATA_ENABLED, REALTIME_PUSH_INTERVAL
)

logger = logging.getLogger(__name__)

@dataclass
class StockQuote:
    """股票行情数据结构"""
    code: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    amount: float
    open_price: float
    high_price: float
    low_price: float
    last_close: float
    timestamp: float

class RealtimeDataManager:
    """实时数据管理器"""
    
    def __init__(self):
        self.running = False
        self.subscribers: Dict[str, List[Callable]] = {}  # 订阅者管理
        self.stock_data: Dict[str, StockQuote] = {}  # 股票数据缓存
        self.push_task: Optional[asyncio.Task] = None
        
        # 配置
        self.config = {
            'api_key': MARKET_DATA_API_KEY,
            'host': MARKET_DATA_HOST,
            'port': MARKET_DATA_PORT,
            'token': MARKET_DATA_TOKEN,
            'enabled': REALTIME_DATA_ENABLED,
            'push_interval': REALTIME_PUSH_INTERVAL
        }
        
        # 统计信息
        self.stats = {
            'start_time': 0,
            'total_pushed': 0,
            'subscriber_count': 0,
            'stock_count': 0,
            'error_count': 0
        }
        
        # 初始化模拟数据
        self._init_mock_data()
    
    def _init_mock_data(self):
        """初始化模拟股票数据"""
        mock_stocks = [
            {'code': '000001', 'name': '平安银行', 'base_price': 12.50},
            {'code': '000002', 'name': '万科A', 'base_price': 18.30},
            {'code': '600000', 'name': '浦发银行', 'base_price': 10.80},
            {'code': '600036', 'name': '招商银行', 'base_price': 35.60},
            {'code': '600519', 'name': '贵州茅台', 'base_price': 1680.00},
            {'code': '000858', 'name': '五粮液', 'base_price': 128.50},
            {'code': '002415', 'name': '海康威视', 'base_price': 39.20},
            {'code': '300059', 'name': '东方财富', 'base_price': 15.40},
            {'code': '002594', 'name': '比亚迪', 'base_price': 245.80},
            {'code': '300750', 'name': '宁德时代', 'base_price': 185.60}
        ]
        
        current_time = time.time()
        
        for stock in mock_stocks:
            base_price = stock['base_price']
            # 模拟价格波动 (-3% 到 +3%)
            import random
            change_percent = random.uniform(-3.0, 3.0)
            current_price = base_price * (1 + change_percent / 100)
            change = current_price - base_price
            
            quote = StockQuote(
                code=stock['code'],
                name=stock['name'],
                price=round(current_price, 2),
                change=round(change, 2),
                change_percent=round(change_percent, 2),
                volume=random.randint(1000000, 50000000),
                amount=round(current_price * random.randint(1000000, 50000000), 2),
                open_price=round(base_price * random.uniform(0.98, 1.02), 2),
                high_price=round(current_price * random.uniform(1.0, 1.05), 2),
                low_price=round(current_price * random.uniform(0.95, 1.0), 2),
                last_close=base_price,
                timestamp=current_time
            )
            
            self.stock_data[stock['code']] = quote
    
    async def start(self):
        """启动实时数据管理器"""
        if self.running:
            logger.warning("实时数据管理器已在运行")
            return
        
        logger.info("启动实时数据管理器...")
        self.running = True
        self.stats['start_time'] = time.time()
        
        # 检查是否有真实数据源配置
        if self.config['host'] and self.config['port'] and self.config['token']:
            logger.info("尝试连接真实数据源...")
            try:
                await self._start_real_data_source()
            except Exception as e:
                logger.warning(f"真实数据源连接失败，使用模拟数据: {str(e)}")
                await self._start_mock_data_source()
        else:
            logger.info("使用模拟数据源...")
            await self._start_mock_data_source()
        
        logger.info("实时数据管理器启动成功")
    
    async def stop(self):
        """停止实时数据管理器"""
        logger.info("停止实时数据管理器...")
        self.running = False
        
        if self.push_task:
            self.push_task.cancel()
            try:
                await self.push_task
            except asyncio.CancelledError:
                pass
        
        logger.info("实时数据管理器已停止")
    
    async def _start_real_data_source(self):
        """启动真实数据源"""
        # 这里应该集成真实的股票数据接收器
        # 由于缺少实际的服务器配置，暂时抛出异常
        raise NotImplementedError("真实数据源需要配置服务器地址和认证信息")
    
    async def _start_mock_data_source(self):
        """启动模拟数据源"""
        logger.info("启动模拟数据推送...")
        self.push_task = asyncio.create_task(self._mock_data_push_loop())
    
    async def _mock_data_push_loop(self):
        """模拟数据推送循环"""
        import random
        
        while self.running:
            try:
                current_time = time.time()
                
                # 更新所有股票数据
                for code, quote in self.stock_data.items():
                    # 模拟价格变动 (-0.5% 到 +0.5%)
                    price_change_percent = random.uniform(-0.5, 0.5)
                    new_price = quote.price * (1 + price_change_percent / 100)
                    
                    # 更新数据
                    quote.price = round(new_price, 2)
                    quote.change = round(new_price - quote.last_close, 2)
                    quote.change_percent = round((quote.change / quote.last_close) * 100, 2)
                    quote.volume += random.randint(1000, 10000)
                    quote.amount += round(new_price * random.randint(1000, 10000), 2)
                    quote.timestamp = current_time
                    
                    # 更新高低价
                    if new_price > quote.high_price:
                        quote.high_price = new_price
                    if new_price < quote.low_price:
                        quote.low_price = new_price
                
                # 推送数据给订阅者
                await self._push_to_subscribers()
                
                # 更新统计
                self.stats['total_pushed'] += 1
                self.stats['stock_count'] = len(self.stock_data)
                
                # 等待下次推送
                await asyncio.sleep(self.config['push_interval'])
                
            except Exception as e:
                logger.error(f"模拟数据推送错误: {str(e)}")
                self.stats['error_count'] += 1
                await asyncio.sleep(1)
    
    async def _push_to_subscribers(self):
        """推送数据给所有订阅者"""
        if not self.subscribers:
            return
        
        for stock_code, callbacks in self.subscribers.items():
            if stock_code in self.stock_data:
                quote = self.stock_data[stock_code]
                data = {
                    'type': 'stock_data',
                    'stock_code': stock_code,
                    'data': {
                        'code': quote.code,
                        'name': quote.name,
                        'price': quote.price,
                        'change': quote.change,
                        'change_percent': quote.change_percent,
                        'volume': quote.volume,
                        'amount': quote.amount,
                        'open': quote.open_price,
                        'high': quote.high_price,
                        'low': quote.low_price,
                        'last_close': quote.last_close
                    },
                    'timestamp': quote.timestamp
                }
                
                # 调用所有回调函数
                for callback in callbacks[:]:  # 使用切片避免修改时的问题
                    try:
                        await callback(data)
                    except Exception as e:
                        logger.error(f"推送数据到订阅者失败: {str(e)}")
                        # 移除失效的回调
                        if callback in callbacks:
                            callbacks.remove(callback)
    
    def subscribe_stock(self, stock_code: str, callback: Callable):
        """订阅股票数据"""
        if stock_code not in self.subscribers:
            self.subscribers[stock_code] = []
        
        if callback not in self.subscribers[stock_code]:
            self.subscribers[stock_code].append(callback)
            logger.info(f"订阅股票: {stock_code}")
            
        self.stats['subscriber_count'] = sum(len(callbacks) for callbacks in self.subscribers.values())
    
    def unsubscribe_stock(self, stock_code: str, callback: Callable):
        """取消订阅股票数据"""
        if stock_code in self.subscribers and callback in self.subscribers[stock_code]:
            self.subscribers[stock_code].remove(callback)
            logger.info(f"取消订阅股票: {stock_code}")
            
            # 如果没有订阅者了，删除该股票的订阅列表
            if not self.subscribers[stock_code]:
                del self.subscribers[stock_code]
                
        self.stats['subscriber_count'] = sum(len(callbacks) for callbacks in self.subscribers.values())
    
    def get_stock_data(self, stock_code: str) -> Optional[Dict]:
        """获取股票数据"""
        if stock_code in self.stock_data:
            quote = self.stock_data[stock_code]
            return {
                'code': quote.code,
                'name': quote.name,
                'price': quote.price,
                'change': quote.change,
                'change_percent': quote.change_percent,
                'volume': quote.volume,
                'amount': quote.amount,
                'open': quote.open_price,
                'high': quote.high_price,
                'low': quote.low_price,
                'last_close': quote.last_close,
                'timestamp': quote.timestamp
            }
        return None
    
    def get_all_stocks(self) -> List[Dict]:
        """获取所有股票数据"""
        return [self.get_stock_data(code) for code in self.stock_data.keys()]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = self.stats.copy()
        if self.stats['start_time'] > 0:
            stats['uptime_seconds'] = int(time.time() - self.stats['start_time'])
        return stats

# 全局实例
realtime_data_manager = RealtimeDataManager()
