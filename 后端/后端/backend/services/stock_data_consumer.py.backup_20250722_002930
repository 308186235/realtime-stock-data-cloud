"""
股票数据消费者 - 从Redis消费数据并推送给前端
"""
import asyncio
import json
import time
import logging
from typing import Dict, List, Set, Optional, Callable
import redis
import threading
from collections import defaultdict, deque
from dataclasses import asdict

from services.redis_stock_storage import redis_stock_storage
from services.stock_data_parser import parse_stock_batch, StockData

logger = logging.getLogger(__name__)

class StockDataConsumer:
    """股票数据消费者"""
    
    def __init__(self):
        # Redis连接
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=2,
            decode_responses=False,
            max_connections=20
        )
        
        # 订阅管理
        self.subscribers: Dict[str, Set[Callable]] = defaultdict(set)  # stock_code -> callbacks
        self.market_subscribers: Dict[str, Set[Callable]] = defaultdict(set)  # market -> callbacks
        self.all_subscribers: Set[Callable] = set()  # 全市场订阅
        
        # 性能配置
        self.batch_size = 100
        self.push_interval = 0.1  # 100ms推送间隔
        self.max_cache_size = 10000
        
        # 数据缓存
        self.data_cache: Dict[str, StockData] = {}
        self.cache_timestamps: Dict[str, float] = {}
        
        # 统计信息
        self.stats = {
            'consumed_count': 0,
            'pushed_count': 0,
            'subscriber_count': 0,
            'cache_hit_count': 0,
            'cache_miss_count': 0,
            'error_count': 0,
            'last_consume_time': 0,
            'consume_rate': 0
        }
        
        # 运行控制
        self.running = False
        self.consume_task: Optional[asyncio.Task] = None
        self.push_task: Optional[asyncio.Task] = None
        
        # 推送队列
        self.push_queue = asyncio.Queue(maxsize=50000)
    
    async def start(self):
        """启动消费者"""
        try:
            # 测试Redis连接
            self.redis_client.ping()
            logger.info("数据消费者Redis连接成功")
            
            self.running = True
            
            # 启动消费任务
            self.consume_task = asyncio.create_task(self._consume_loop())
            
            # 启动推送任务
            self.push_task = asyncio.create_task(self._push_loop())
            
            logger.info("股票数据消费者启动成功")
            
        except Exception as e:
            logger.error(f"启动数据消费者失败: {str(e)}")
            raise
    
    async def stop(self):
        """停止消费者"""
        logger.info("停止股票数据消费者...")
        
        self.running = False
        
        # 取消任务
        if self.consume_task:
            self.consume_task.cancel()
        if self.push_task:
            self.push_task.cancel()
        
        # 关闭Redis连接
        try:
            self.redis_client.close()
        except Exception:
            pass
        
        logger.info("股票数据消费者已停止")
    
    def subscribe_stock(self, stock_code: str, callback: Callable):
        """订阅单只股票"""
        self.subscribers[stock_code].add(callback)
        self._update_subscriber_count()
        logger.debug(f"新增股票订阅: {stock_code}")
    
    def unsubscribe_stock(self, stock_code: str, callback: Callable):
        """取消订阅单只股票"""
        self.subscribers[stock_code].discard(callback)
        if not self.subscribers[stock_code]:
            del self.subscribers[stock_code]
        self._update_subscriber_count()
        logger.debug(f"取消股票订阅: {stock_code}")
    
    def subscribe_market(self, market: str, callback: Callable):
        """订阅整个市场"""
        self.market_subscribers[market].add(callback)
        self._update_subscriber_count()
        logger.debug(f"新增市场订阅: {market}")
    
    def unsubscribe_market(self, market: str, callback: Callable):
        """取消订阅市场"""
        self.market_subscribers[market].discard(callback)
        if not self.market_subscribers[market]:
            del self.market_subscribers[market]
        self._update_subscriber_count()
        logger.debug(f"取消市场订阅: {market}")
    
    def subscribe_all(self, callback: Callable):
        """订阅所有股票"""
        self.all_subscribers.add(callback)
        self._update_subscriber_count()
        logger.debug("新增全市场订阅")
    
    def unsubscribe_all(self, callback: Callable):
        """取消订阅所有股票"""
        self.all_subscribers.discard(callback)
        self._update_subscriber_count()
        logger.debug("取消全市场订阅")
    
    def _update_subscriber_count(self):
        """更新订阅者数量统计"""
        total_count = (
            sum(len(subs) for subs in self.subscribers.values()) +
            sum(len(subs) for subs in self.market_subscribers.values()) +
            len(self.all_subscribers)
        )
        self.stats['subscriber_count'] = total_count
    
    async def _consume_loop(self):
        """消费循环"""
        last_stream_id = '0'  # 从头开始读取
        
        while self.running:
            try:
                # 从Redis Stream读取原始数据
                result = self.redis_client.xread(
                    {'stock:realtime:raw': last_stream_id},
                    count=self.batch_size,
                    block=100  # 100ms阻塞
                )
                
                if result:
                    stream_name, messages = result[0]
                    
                    if messages:
                        # 处理消息批次
                        await self._process_message_batch(messages)
                        
                        # 更新最后读取的ID
                        last_stream_id = messages[-1][0].decode('utf-8')
                        
                        # 更新统计
                        self.stats['consumed_count'] += len(messages)
                        self.stats['last_consume_time'] = time.time()
                
            except Exception as e:
                logger.error(f"消费循环错误: {str(e)}")
                self.stats['error_count'] += 1
                await asyncio.sleep(1)
    
    async def _process_message_batch(self, messages: List):
        """处理消息批次"""
        try:
            start_time = time.time()
            
            # 准备批量解析的数据
            raw_data_list = []
            for message_id, fields in messages:
                raw_data = fields.get(b'data', b'')
                timestamp = float(fields.get(b'timestamp', time.time()))
                
                raw_data_list.append({
                    'data': raw_data,
                    'timestamp': timestamp
                })
            
            # 批量解析股票数据
            parsed_stocks = parse_stock_batch(raw_data_list)
            
            if parsed_stocks:
                # 更新缓存
                self._update_cache(parsed_stocks)
                
                # 添加到推送队列
                for stock_data in parsed_stocks:
                    try:
                        await self.push_queue.put_nowait(stock_data)
                    except asyncio.QueueFull:
                        logger.warning("推送队列已满，丢弃数据")
                        break
            
            # 更新性能统计
            elapsed = time.time() - start_time
            if elapsed > 0:
                self.stats['consume_rate'] = len(messages) / elapsed
            
        except Exception as e:
            logger.error(f"处理消息批次失败: {str(e)}")
            self.stats['error_count'] += 1
    
    def _update_cache(self, stock_data_list: List[StockData]):
        """更新数据缓存"""
        current_time = time.time()
        
        for stock_data in stock_data_list:
            # 更新缓存
            self.data_cache[stock_data.stock_code] = stock_data
            self.cache_timestamps[stock_data.stock_code] = current_time
        
        # 清理过期缓存
        if len(self.data_cache) > self.max_cache_size:
            self._cleanup_cache()
    
    def _cleanup_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_codes = []
        
        for stock_code, timestamp in self.cache_timestamps.items():
            if current_time - timestamp > 300:  # 5分钟过期
                expired_codes.append(stock_code)
        
        for stock_code in expired_codes:
            self.data_cache.pop(stock_code, None)
            self.cache_timestamps.pop(stock_code, None)
    
    async def _push_loop(self):
        """推送循环"""
        batch_data = []
        last_push_time = time.time()
        
        while self.running:
            try:
                # 收集批量数据
                try:
                    stock_data = await asyncio.wait_for(
                        self.push_queue.get(), timeout=self.push_interval
                    )
                    batch_data.append(stock_data)
                    
                    # 继续收集更多数据
                    while len(batch_data) < self.batch_size:
                        try:
                            stock_data = self.push_queue.get_nowait()
                            batch_data.append(stock_data)
                        except asyncio.QueueEmpty:
                            break
                            
                except asyncio.TimeoutError:
                    # 超时，检查是否需要推送现有数据
                    current_time = time.time()
                    if batch_data and (current_time - last_push_time) > self.push_interval:
                        pass  # 继续处理现有批次
                    else:
                        continue
                
                if batch_data:
                    # 推送数据
                    await self._push_to_subscribers(batch_data)
                    
                    # 更新统计
                    self.stats['pushed_count'] += len(batch_data)
                    
                    # 重置批次
                    batch_data = []
                    last_push_time = time.time()
                
            except Exception as e:
                logger.error(f"推送循环错误: {str(e)}")
                self.stats['error_count'] += 1
                await asyncio.sleep(0.1)
    
    async def _push_to_subscribers(self, stock_data_list: List[StockData]):
        """推送给订阅者"""
        try:
            # 按股票代码分组
            stock_groups = defaultdict(list)
            market_groups = defaultdict(list)
            
            for stock_data in stock_data_list:
                stock_groups[stock_data.stock_code].append(stock_data)
                market_groups[stock_data.market].append(stock_data)
            
            # 推送给股票订阅者
            for stock_code, data_list in stock_groups.items():
                if stock_code in self.subscribers:
                    await self._notify_callbacks(
                        self.subscribers[stock_code],
                        {
                            'type': 'stock_data',
                            'stock_code': stock_code,
                            'data': [data.to_dict() for data in data_list]
                        }
                    )
            
            # 推送给市场订阅者
            for market, data_list in market_groups.items():
                if market in self.market_subscribers:
                    await self._notify_callbacks(
                        self.market_subscribers[market],
                        {
                            'type': 'market_data',
                            'market': market,
                            'data': [data.to_dict() for data in data_list]
                        }
                    )
            
            # 推送给全市场订阅者
            if self.all_subscribers:
                await self._notify_callbacks(
                    self.all_subscribers,
                    {
                        'type': 'all_market_data',
                        'data': [data.to_dict() for data in stock_data_list]
                    }
                )
            
        except Exception as e:
            logger.error(f"推送给订阅者失败: {str(e)}")
            self.stats['error_count'] += 1
    
    async def _notify_callbacks(self, callbacks: Set[Callable], data: Dict):
        """通知回调函数"""
        for callback in callbacks.copy():  # 复制集合避免并发修改
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"回调函数执行失败: {str(e)}")
                # 移除失效的回调
                callbacks.discard(callback)
    
    async def get_latest_data(self, stock_code: str) -> Optional[Dict]:
        """获取最新数据"""
        try:
            # 先从缓存获取
            if stock_code in self.data_cache:
                self.stats['cache_hit_count'] += 1
                return self.data_cache[stock_code].to_dict()
            
            # 从Redis获取
            self.stats['cache_miss_count'] += 1
            data = redis_stock_storage.get_realtime_data(stock_code)
            
            if data:
                # 更新缓存
                # 注意：这里需要将Redis数据转换为StockData对象
                # 为简化，直接返回Redis数据
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"获取最新数据失败: {str(e)}")
            return None
    
    async def get_market_summary(self, market: str) -> Dict:
        """获取市场概况"""
        try:
            # 获取热门股票
            top_volume = redis_stock_storage.get_market_top_stocks(market, 'volume', 20)
            top_amount = redis_stock_storage.get_market_top_stocks(market, 'amount', 20)
            
            return {
                'market': market,
                'top_volume': top_volume,
                'top_amount': top_amount,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"获取市场概况失败: {str(e)}")
            return {}
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = self.stats.copy()
        stats['cache_size'] = len(self.data_cache)
        stats['push_queue_size'] = self.push_queue.qsize()
        return stats

# 全局消费者实例
stock_data_consumer = StockDataConsumer()
