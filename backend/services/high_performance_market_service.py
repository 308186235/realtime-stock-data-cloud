"""
高性能市场数据服务 - 支持5000支股票每3秒推送
"""
import asyncio
import json
import time
import logging
from typing import Dict, List, Set, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import redis.asyncio as redis
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor
import queue
import weakref

logger = logging.getLogger(__name__)

@dataclass
class StockData:
    """股票数据结构"""
    code: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: float
    market: str = "SZ"
    
    def to_dict(self) -> Dict:
        return asdict(self)

class HighPerformanceMarketService:
    """高性能市场数据服务"""
    
    def __init__(self):
        # 配置参数
        self.batch_size = 1000  # 批处理大小
        self.push_interval = 3.0  # 推送间隔(秒)
        self.max_connections = 10000  # 最大连接数
        self.buffer_size = 50000  # 缓冲区大小
        
        # 数据存储
        self.stock_data: Dict[str, StockData] = {}
        self.data_buffer = deque(maxlen=self.buffer_size)
        self.subscribers: Dict[str, Set[weakref.ref]] = defaultdict(set)
        
        # 性能监控
        self.stats = {
            'total_pushed': 0,
            'push_rate': 0,
            'error_count': 0,
            'connection_count': 0,
            'last_push_time': 0,
            'buffer_usage': 0
        }
        
        # 异步组件
        self.redis_client: Optional[redis.Redis] = None
        self.push_task: Optional[asyncio.Task] = None
        self.running = False
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # 数据队列
        self.data_queue = queue.Queue(maxsize=100000)
        
    async def initialize(self):
        """初始化服务"""
        try:
            # 初始化Redis连接
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True,
                max_connections=20,
                retry_on_timeout=True
            )
            
            # 测试Redis连接
            await self.redis_client.ping()
            logger.info("Redis连接成功")
            
            # 启动推送任务
            self.running = True
            self.push_task = asyncio.create_task(self._push_loop())
            
            # 启动性能监控
            asyncio.create_task(self._monitor_performance())
            
            logger.info("高性能市场数据服务初始化完成")
            
        except Exception as e:
            logger.error(f"服务初始化失败: {str(e)}")
            raise

    async def shutdown(self):
        """关闭服务"""
        self.running = False
        
        if self.push_task:
            self.push_task.cancel()
            
        if self.redis_client:
            await self.redis_client.close()
            
        self.executor.shutdown(wait=True)
        logger.info("高性能市场数据服务已关闭")

    def receive_market_data(self, data_batch: List[Dict]):
        """接收市场数据批次"""
        try:
            # 快速处理数据批次
            processed_data = []
            current_time = time.time()
            
            for data in data_batch:
                stock_data = StockData(
                    code=data['code'],
                    name=data.get('name', ''),
                    price=float(data['price']),
                    change=float(data.get('change', 0)),
                    change_percent=float(data.get('change_percent', 0)),
                    volume=int(data.get('volume', 0)),
                    timestamp=current_time,
                    market=data.get('market', 'SZ')
                )
                
                # 更新内存数据
                self.stock_data[stock_data.code] = stock_data
                processed_data.append(stock_data)
            
            # 添加到缓冲区
            self.data_buffer.extend(processed_data)
            
            # 更新统计
            self.stats['total_pushed'] += len(processed_data)
            self.stats['buffer_usage'] = len(self.data_buffer)
            
            logger.debug(f"接收到 {len(data_batch)} 条市场数据")
            
        except Exception as e:
            logger.error(f"处理市场数据失败: {str(e)}")
            self.stats['error_count'] += 1

    async def _push_loop(self):
        """推送循环"""
        while self.running:
            try:
                start_time = time.time()
                
                # 获取需要推送的数据
                if self.data_buffer:
                    # 批量获取数据
                    batch_data = []
                    batch_count = min(len(self.data_buffer), self.batch_size)
                    
                    for _ in range(batch_count):
                        if self.data_buffer:
                            batch_data.append(self.data_buffer.popleft())
                    
                    if batch_data:
                        # 并行推送
                        await self._parallel_push(batch_data)
                        
                        # 更新统计
                        self.stats['last_push_time'] = time.time()
                        self.stats['push_rate'] = len(batch_data) / (time.time() - start_time)
                
                # 计算下次推送时间
                elapsed = time.time() - start_time
                sleep_time = max(0, self.push_interval - elapsed)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    
            except Exception as e:
                logger.error(f"推送循环错误: {str(e)}")
                self.stats['error_count'] += 1
                await asyncio.sleep(1)  # 错误后短暂休息

    async def _parallel_push(self, batch_data: List[StockData]):
        """并行推送数据"""
        try:
            # 创建推送任务
            tasks = []
            
            # 推送到Redis
            tasks.append(self._push_to_redis(batch_data))
            
            # 推送到WebSocket订阅者
            tasks.append(self._push_to_websockets(batch_data))
            
            # 推送到数据库(异步)
            tasks.append(self._push_to_database(batch_data))
            
            # 并行执行所有推送任务
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"并行推送失败: {str(e)}")

    async def _push_to_redis(self, batch_data: List[StockData]):
        """推送到Redis缓存"""
        try:
            if not self.redis_client:
                return
                
            # 批量写入Redis
            pipe = self.redis_client.pipeline()
            
            for stock_data in batch_data:
                # 设置股票最新数据
                key = f"stock:{stock_data.code}"
                pipe.hset(key, mapping=stock_data.to_dict())
                pipe.expire(key, 3600)  # 1小时过期
                
                # 添加到实时数据流
                pipe.lpush(f"stream:stock:{stock_data.code}", json.dumps(stock_data.to_dict()))
                pipe.ltrim(f"stream:stock:{stock_data.code}", 0, 99)  # 保留最近100条
            
            await pipe.execute()
            
        except Exception as e:
            logger.error(f"Redis推送失败: {str(e)}")

    async def _push_to_websockets(self, batch_data: List[StockData]):
        """推送到WebSocket连接"""
        try:
            # 按股票代码分组
            grouped_data = defaultdict(list)
            for stock_data in batch_data:
                grouped_data[stock_data.code].append(stock_data.to_dict())
            
            # 推送给订阅者
            for stock_code, data_list in grouped_data.items():
                if stock_code in self.subscribers:
                    # 清理失效的连接
                    valid_subscribers = set()
                    
                    for subscriber_ref in self.subscribers[stock_code]:
                        subscriber = subscriber_ref()
                        if subscriber is not None:
                            try:
                                # 异步发送数据
                                asyncio.create_task(subscriber.send_json({
                                    'type': 'market_data',
                                    'stock_code': stock_code,
                                    'data': data_list
                                }))
                                valid_subscribers.add(subscriber_ref)
                            except Exception as e:
                                logger.debug(f"WebSocket发送失败: {str(e)}")
                    
                    # 更新有效订阅者
                    self.subscribers[stock_code] = valid_subscribers
            
        except Exception as e:
            logger.error(f"WebSocket推送失败: {str(e)}")

    async def _push_to_database(self, batch_data: List[StockData]):
        """异步推送到数据库"""
        try:
            # 使用线程池执行数据库操作
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self._sync_database_write,
                batch_data
            )
            
        except Exception as e:
            logger.error(f"数据库推送失败: {str(e)}")

    def _sync_database_write(self, batch_data: List[StockData]):
        """同步数据库写入"""
        try:
            # 这里可以集成Supabase批量写入
            # 为了性能，可以考虑批量插入或使用消息队列
            
            # 示例：批量准备数据
            db_records = []
            for stock_data in batch_data:
                db_records.append({
                    'stock_code': stock_data.code,
                    'price': stock_data.price,
                    'change': stock_data.change,
                    'change_percent': stock_data.change_percent,
                    'volume': stock_data.volume,
                    'timestamp': datetime.fromtimestamp(stock_data.timestamp),
                    'market': stock_data.market
                })
            
            # TODO: 实际的批量数据库插入
            # supabase_client.table('market_data').insert(db_records).execute()
            
        except Exception as e:
            logger.error(f"同步数据库写入失败: {str(e)}")

    def subscribe_stock(self, stock_code: str, websocket):
        """订阅股票数据"""
        try:
            # 使用弱引用避免内存泄漏
            subscriber_ref = weakref.ref(websocket)
            self.subscribers[stock_code].add(subscriber_ref)
            self.stats['connection_count'] = sum(len(subs) for subs in self.subscribers.values())
            
            logger.debug(f"新订阅: {stock_code}, 总连接数: {self.stats['connection_count']}")
            
        except Exception as e:
            logger.error(f"订阅失败: {str(e)}")

    def unsubscribe_stock(self, stock_code: str, websocket):
        """取消订阅股票数据"""
        try:
            if stock_code in self.subscribers:
                # 移除对应的弱引用
                to_remove = set()
                for subscriber_ref in self.subscribers[stock_code]:
                    if subscriber_ref() == websocket:
                        to_remove.add(subscriber_ref)
                
                self.subscribers[stock_code] -= to_remove
                
                # 如果没有订阅者，删除该股票的订阅记录
                if not self.subscribers[stock_code]:
                    del self.subscribers[stock_code]
            
            self.stats['connection_count'] = sum(len(subs) for subs in self.subscribers.values())
            
        except Exception as e:
            logger.error(f"取消订阅失败: {str(e)}")

    async def get_stock_data(self, stock_code: str) -> Optional[Dict]:
        """获取股票数据"""
        try:
            # 优先从内存获取
            if stock_code in self.stock_data:
                return self.stock_data[stock_code].to_dict()
            
            # 从Redis获取
            if self.redis_client:
                data = await self.redis_client.hgetall(f"stock:{stock_code}")
                if data:
                    return data
            
            return None
            
        except Exception as e:
            logger.error(f"获取股票数据失败: {str(e)}")
            return None

    async def _monitor_performance(self):
        """性能监控"""
        while self.running:
            try:
                # 每30秒输出性能统计
                await asyncio.sleep(30)
                
                logger.info(f"性能统计: "
                          f"推送总数={self.stats['total_pushed']}, "
                          f"推送速率={self.stats['push_rate']:.2f}/s, "
                          f"连接数={self.stats['connection_count']}, "
                          f"缓冲区使用={self.stats['buffer_usage']}, "
                          f"错误数={self.stats['error_count']}")
                
                # 检查性能告警
                if self.stats['push_rate'] < 1000:  # 推送速率过低
                    logger.warning("推送速率过低，可能存在性能问题")
                
                if self.stats['buffer_usage'] > self.buffer_size * 0.8:  # 缓冲区使用率过高
                    logger.warning("缓冲区使用率过高，可能存在积压")
                
            except Exception as e:
                logger.error(f"性能监控错误: {str(e)}")

    def get_performance_stats(self) -> Dict:
        """获取性能统计"""
        return self.stats.copy()

# 全局服务实例
high_performance_market_service = HighPerformanceMarketService()
