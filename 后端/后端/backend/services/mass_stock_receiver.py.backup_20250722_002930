"""
大规模股票数据接收器 - 支持5000支股票每3秒推送
性能目标: 1667 TPS (5000股票/3秒)
"""
import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from collections import deque
import threading
from concurrent.futures import ThreadPoolExecutor
import queue
import redis.asyncio as redis
from datetime import datetime
import aiohttp
import websockets
import uvloop  # 高性能事件循环

logger = logging.getLogger(__name__)

@dataclass
class StockTick:
    """股票tick数据"""
    code: str
    price: float
    volume: int
    timestamp: float
    change: float = 0.0
    change_percent: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'code': self.code,
            'price': self.price,
            'volume': self.volume,
            'timestamp': self.timestamp,
            'change': self.change,
            'change_percent': self.change_percent
        }

class MassStockReceiver:
    """大规模股票数据接收器"""
    
    def __init__(self):
        # 性能配置
        self.target_stocks = 5000  # 目标股票数量
        self.push_interval = 3.0   # 推送间隔
        self.batch_size = 1000     # 批处理大小
        self.buffer_size = 100000  # 缓冲区大小
        
        # 数据存储
        self.stock_buffer = deque(maxlen=self.buffer_size)
        self.latest_data: Dict[str, StockTick] = {}
        
        # 性能监控
        self.stats = {
            'received_count': 0,
            'processed_count': 0,
            'error_count': 0,
            'receive_rate': 0,
            'process_rate': 0,
            'buffer_usage': 0,
            'last_receive_time': 0,
            'cycle_count': 0
        }
        
        # 异步组件
        self.redis_client: Optional[redis.Redis] = None
        self.running = False
        self.receive_task: Optional[asyncio.Task] = None
        self.process_task: Optional[asyncio.Task] = None
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=20)
        
        # 数据队列 - 使用多个队列提高并发
        self.data_queues = [queue.Queue(maxsize=10000) for _ in range(10)]
        self.queue_index = 0
        
        # 回调函数
        self.data_callbacks: List[Callable] = []
    
    async def initialize(self):
        """初始化接收器"""
        try:
            # 设置高性能事件循环
            if hasattr(uvloop, 'install'):
                uvloop.install()
            
            # 初始化Redis连接池
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=1,  # 使用专用数据库
                decode_responses=False,  # 二进制模式提高性能
                max_connections=50,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            await self.redis_client.ping()
            logger.info("Redis连接池初始化成功")
            
            # 启动接收和处理任务
            self.running = True
            self.receive_task = asyncio.create_task(self._receive_loop())
            self.process_task = asyncio.create_task(self._process_loop())
            
            # 启动性能监控
            asyncio.create_task(self._monitor_performance())
            
            logger.info(f"大规模股票接收器初始化完成 - 目标: {self.target_stocks}支股票")
            
        except Exception as e:
            logger.error(f"接收器初始化失败: {str(e)}")
            raise
    
    async def shutdown(self):
        """关闭接收器"""
        self.running = False
        
        if self.receive_task:
            self.receive_task.cancel()
        if self.process_task:
            self.process_task.cancel()
            
        if self.redis_client:
            await self.redis_client.close()
            
        self.executor.shutdown(wait=True)
        logger.info("大规模股票接收器已关闭")
    
    def add_data_callback(self, callback: Callable):
        """添加数据处理回调"""
        self.data_callbacks.append(callback)
    
    async def receive_stock_batch(self, stock_data_list: List[Dict]):
        """接收股票数据批次 - 主要接口"""
        try:
            start_time = time.time()
            
            # 快速解析和验证数据
            valid_ticks = []
            current_timestamp = time.time()
            
            for data in stock_data_list:
                try:
                    tick = StockTick(
                        code=data['code'],
                        price=float(data['price']),
                        volume=int(data.get('volume', 0)),
                        timestamp=current_timestamp,
                        change=float(data.get('change', 0)),
                        change_percent=float(data.get('change_percent', 0))
                    )
                    valid_ticks.append(tick)
                except (KeyError, ValueError, TypeError) as e:
                    logger.debug(f"数据解析错误: {data}, 错误: {str(e)}")
                    self.stats['error_count'] += 1
            
            if valid_ticks:
                # 添加到缓冲区
                self.stock_buffer.extend(valid_ticks)
                
                # 更新最新数据
                for tick in valid_ticks:
                    self.latest_data[tick.code] = tick
                
                # 更新统计
                self.stats['received_count'] += len(valid_ticks)
                self.stats['buffer_usage'] = len(self.stock_buffer)
                self.stats['last_receive_time'] = time.time()
                
                # 计算接收速率
                elapsed = time.time() - start_time
                self.stats['receive_rate'] = len(valid_ticks) / elapsed if elapsed > 0 else 0
                
                logger.debug(f"接收批次: {len(valid_ticks)}支股票, 用时: {elapsed:.3f}秒")
            
        except Exception as e:
            logger.error(f"接收股票批次失败: {str(e)}")
            self.stats['error_count'] += 1
    
    async def _receive_loop(self):
        """接收循环 - 模拟外部数据源"""
        while self.running:
            try:
                # 模拟接收5000支股票数据
                await self._simulate_receive_5000_stocks()
                
                # 等待下一个周期
                await asyncio.sleep(self.push_interval)
                self.stats['cycle_count'] += 1
                
            except Exception as e:
                logger.error(f"接收循环错误: {str(e)}")
                await asyncio.sleep(1)
    
    async def _simulate_receive_5000_stocks(self):
        """模拟接收5000支股票数据"""
        try:
            start_time = time.time()
            
            # 生成5000支股票的模拟数据
            stock_data_batch = []
            base_codes = ['000001', '000002', '600000', '600036', '002415']
            
            for i in range(self.target_stocks):
                # 生成股票代码
                if i < 1000:
                    code = f"000{i:03d}"
                elif i < 2000:
                    code = f"002{i-1000:03d}"
                elif i < 3000:
                    code = f"300{i-2000:03d}"
                elif i < 4000:
                    code = f"600{i-3000:03d}"
                else:
                    code = f"688{i-4000:03d}"
                
                # 生成随机价格数据
                import random
                base_price = 10 + (i % 100)
                price_change = random.uniform(-0.5, 0.5)
                current_price = base_price + price_change
                
                stock_data = {
                    'code': code,
                    'price': round(current_price, 2),
                    'volume': random.randint(1000, 100000),
                    'change': round(price_change, 2),
                    'change_percent': round((price_change / base_price) * 100, 2)
                }
                stock_data_batch.append(stock_data)
            
            # 批量处理数据
            await self.receive_stock_batch(stock_data_batch)
            
            elapsed = time.time() - start_time
            logger.info(f"模拟接收{self.target_stocks}支股票数据完成, 用时: {elapsed:.3f}秒")
            
        except Exception as e:
            logger.error(f"模拟接收失败: {str(e)}")
    
    async def _process_loop(self):
        """数据处理循环"""
        while self.running:
            try:
                if self.stock_buffer:
                    # 批量处理数据
                    batch_data = []
                    batch_count = min(len(self.stock_buffer), self.batch_size)
                    
                    for _ in range(batch_count):
                        if self.stock_buffer:
                            batch_data.append(self.stock_buffer.popleft())
                    
                    if batch_data:
                        await self._process_batch(batch_data)
                        self.stats['processed_count'] += len(batch_data)
                
                # 短暂休息避免CPU占用过高
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"处理循环错误: {str(e)}")
                await asyncio.sleep(1)
    
    async def _process_batch(self, batch_data: List[StockTick]):
        """批量处理数据"""
        try:
            start_time = time.time()
            
            # 并行处理任务
            tasks = []
            
            # 1. 存储到Redis
            tasks.append(self._store_to_redis(batch_data))
            
            # 2. 调用回调函数
            for callback in self.data_callbacks:
                tasks.append(self._call_callback(callback, batch_data))
            
            # 3. 可选：存储到数据库
            # tasks.append(self._store_to_database(batch_data))
            
            # 并行执行
            await asyncio.gather(*tasks, return_exceptions=True)
            
            elapsed = time.time() - start_time
            self.stats['process_rate'] = len(batch_data) / elapsed if elapsed > 0 else 0
            
        except Exception as e:
            logger.error(f"批量处理失败: {str(e)}")
    
    async def _store_to_redis(self, batch_data: List[StockTick]):
        """存储到Redis"""
        try:
            if not self.redis_client:
                return
            
            # 使用pipeline提高性能
            pipe = self.redis_client.pipeline()
            
            for tick in batch_data:
                # 存储最新价格
                key = f"stock:latest:{tick.code}"
                pipe.hset(key, mapping={
                    'price': tick.price,
                    'volume': tick.volume,
                    'change': tick.change,
                    'change_percent': tick.change_percent,
                    'timestamp': tick.timestamp
                })
                pipe.expire(key, 3600)  # 1小时过期
                
                # 存储到时间序列
                ts_key = f"stock:ts:{tick.code}"
                pipe.zadd(ts_key, {json.dumps(tick.to_dict()): tick.timestamp})
                pipe.zremrangebyrank(ts_key, 0, -101)  # 只保留最近100条
            
            await pipe.execute()
            
        except Exception as e:
            logger.error(f"Redis存储失败: {str(e)}")
    
    async def _call_callback(self, callback: Callable, batch_data: List[StockTick]):
        """调用回调函数"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(batch_data)
            else:
                # 在线程池中执行同步回调
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(self.executor, callback, batch_data)
                
        except Exception as e:
            logger.error(f"回调函数执行失败: {str(e)}")
    
    async def get_latest_data(self, stock_codes: List[str] = None) -> Dict[str, Dict]:
        """获取最新数据"""
        try:
            if stock_codes is None:
                # 返回所有股票的最新数据
                return {code: tick.to_dict() for code, tick in self.latest_data.items()}
            else:
                # 返回指定股票的最新数据
                result = {}
                for code in stock_codes:
                    if code in self.latest_data:
                        result[code] = self.latest_data[code].to_dict()
                return result
                
        except Exception as e:
            logger.error(f"获取最新数据失败: {str(e)}")
            return {}
    
    async def _monitor_performance(self):
        """性能监控"""
        while self.running:
            try:
                await asyncio.sleep(10)  # 每10秒监控一次
                
                # 计算性能指标
                total_target_per_cycle = self.target_stocks
                actual_receive_rate = self.stats['receive_rate']
                actual_process_rate = self.stats['process_rate']
                
                logger.info(
                    f"性能监控 - "
                    f"周期: {self.stats['cycle_count']}, "
                    f"接收: {self.stats['received_count']}, "
                    f"处理: {self.stats['processed_count']}, "
                    f"接收速率: {actual_receive_rate:.0f}/s, "
                    f"处理速率: {actual_process_rate:.0f}/s, "
                    f"缓冲区: {self.stats['buffer_usage']}, "
                    f"错误: {self.stats['error_count']}"
                )
                
                # 性能告警
                if actual_receive_rate < 1000:
                    logger.warning("接收速率过低！")
                
                if self.stats['buffer_usage'] > self.buffer_size * 0.8:
                    logger.warning("缓冲区使用率过高！")
                
                if self.stats['error_count'] > 100:
                    logger.warning("错误数量过多！")
                
            except Exception as e:
                logger.error(f"性能监控错误: {str(e)}")
    
    def get_performance_stats(self) -> Dict:
        """获取性能统计"""
        stats = self.stats.copy()
        stats['target_stocks'] = self.target_stocks
        stats['push_interval'] = self.push_interval
        stats['target_tps'] = self.target_stocks / self.push_interval
        return stats

# 全局接收器实例
mass_stock_receiver = MassStockReceiver()

# 使用示例
async def example_usage():
    """使用示例"""
    
    # 初始化接收器
    await mass_stock_receiver.initialize()
    
    # 添加数据处理回调
    async def data_handler(batch_data: List[StockTick]):
        print(f"处理了 {len(batch_data)} 条股票数据")
    
    mass_stock_receiver.add_data_callback(data_handler)
    
    # 运行一段时间
    await asyncio.sleep(30)
    
    # 获取性能统计
    stats = mass_stock_receiver.get_performance_stats()
    print(f"性能统计: {stats}")
    
    # 关闭接收器
    await mass_stock_receiver.shutdown()

if __name__ == "__main__":
    asyncio.run(example_usage())
