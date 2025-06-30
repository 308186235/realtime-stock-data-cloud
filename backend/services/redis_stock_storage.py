"""
Redis股票数据存储服务 - 高性能批量存储
专门优化用于处理大量实时股票数据
"""
import redis
import json
import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import asdict
import threading
from concurrent.futures import ThreadPoolExecutor
import queue
from datetime import datetime, timedelta

from services.stock_data_parser import StockData

logger = logging.getLogger(__name__)

class RedisStockStorage:
    """Redis股票数据存储服务"""
    
    def __init__(self, 
                 host: str = 'localhost',
                 port: int = 6379,
                 db: int = 2,
                 max_connections: int = 50):
        
        # Redis连接配置
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=False,  # 二进制模式提高性能
            max_connections=max_connections,
            socket_keepalive=True,
            socket_keepalive_options={},
            health_check_interval=30,
            retry_on_timeout=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # 性能配置
        self.batch_size = 1000
        self.max_queue_size = 100000
        self.pipeline_size = 500
        
        # 数据队列
        self.storage_queue = queue.Queue(maxsize=self.max_queue_size)
        
        # 统计信息
        self.stats = {
            'stored_count': 0,
            'error_count': 0,
            'queue_size': 0,
            'storage_rate': 0,
            'last_storage_time': 0,
            'redis_operations': 0
        }
        
        # 线程控制
        self.running = False
        self.storage_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # 数据保留策略
        self.retention_config = {
            'realtime_ttl': 3600,      # 实时数据保留1小时
            'minute_ttl': 86400,       # 分钟数据保留1天
            'daily_ttl': 2592000,      # 日数据保留30天
            'max_stream_length': 100000 # Stream最大长度
        }
    
    def start(self):
        """启动存储服务"""
        try:
            # 测试Redis连接
            self.redis_client.ping()
            logger.info("Redis连接成功")
            
            self.running = True
            
            # 启动存储线程
            self.storage_thread = threading.Thread(
                target=self._storage_loop,
                daemon=True,
                name="RedisStorage"
            )
            self.storage_thread.start()
            
            logger.info("Redis存储服务启动成功")
            
        except Exception as e:
            logger.error(f"启动Redis存储服务失败: {str(e)}")
            raise
    
    def stop(self):
        """停止存储服务"""
        logger.info("停止Redis存储服务...")
        
        self.running = False
        
        # 等待存储线程结束
        if self.storage_thread and self.storage_thread.is_alive():
            self.storage_thread.join(timeout=10)
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
        
        # 关闭Redis连接
        try:
            self.redis_client.close()
        except Exception:
            pass
        
        logger.info("Redis存储服务已停止")
    
    def store_stock_data(self, stock_data: StockData):
        """存储单条股票数据"""
        try:
            self.storage_queue.put_nowait(stock_data)
            self.stats['queue_size'] = self.storage_queue.qsize()
        except queue.Full:
            logger.error("存储队列已满，丢弃数据")
            self.stats['error_count'] += 1
    
    def store_stock_batch(self, stock_data_list: List[StockData]):
        """批量存储股票数据"""
        for stock_data in stock_data_list:
            self.store_stock_data(stock_data)
    
    def _storage_loop(self):
        """存储循环"""
        batch_data = []
        last_storage_time = time.time()
        
        while self.running:
            try:
                # 收集批量数据
                try:
                    stock_data = self.storage_queue.get(timeout=0.1)
                    batch_data.append(stock_data)
                    
                    # 继续收集更多数据
                    while len(batch_data) < self.batch_size:
                        try:
                            stock_data = self.storage_queue.get_nowait()
                            batch_data.append(stock_data)
                        except queue.Empty:
                            break
                            
                except queue.Empty:
                    # 检查是否需要处理现有批次
                    current_time = time.time()
                    if batch_data and (current_time - last_storage_time) > 1.0:
                        # 超过1秒，处理现有批次
                        pass
                    else:
                        continue
                
                if batch_data:
                    # 批量存储
                    self._store_batch_to_redis(batch_data)
                    
                    # 更新统计
                    self.stats['stored_count'] += len(batch_data)
                    self.stats['queue_size'] = self.storage_queue.qsize()
                    self.stats['last_storage_time'] = time.time()
                    
                    # 重置批次
                    batch_data = []
                    last_storage_time = time.time()
                
            except Exception as e:
                logger.error(f"存储循环错误: {str(e)}")
                self.stats['error_count'] += 1
                time.sleep(0.1)
    
    def _store_batch_to_redis(self, batch_data: List[StockData]):
        """批量存储到Redis"""
        try:
            start_time = time.time()
            
            # 使用pipeline提高性能
            pipe = self.redis_client.pipeline()
            operation_count = 0
            
            for i, stock_data in enumerate(batch_data):
                # 1. 存储实时数据到Hash
                self._add_realtime_data(pipe, stock_data)
                
                # 2. 存储到时间序列Stream
                self._add_to_stream(pipe, stock_data)
                
                # 3. 更新股票列表
                self._update_stock_list(pipe, stock_data)
                
                # 4. 存储市场统计
                self._update_market_stats(pipe, stock_data)
                
                operation_count += 4
                
                # 每500个操作执行一次pipeline
                if operation_count >= self.pipeline_size:
                    pipe.execute()
                    pipe = self.redis_client.pipeline()
                    operation_count = 0
            
            # 执行剩余操作
            if operation_count > 0:
                pipe.execute()
            
            # 更新性能统计
            elapsed = time.time() - start_time
            if elapsed > 0:
                self.stats['storage_rate'] = len(batch_data) / elapsed
            
            self.stats['redis_operations'] += len(batch_data) * 4
            
        except Exception as e:
            logger.error(f"批量存储到Redis失败: {str(e)}")
            self.stats['error_count'] += 1
    
    def _add_realtime_data(self, pipe, stock_data: StockData):
        """添加实时数据"""
        key = f"stock:realtime:{stock_data.stock_code}"
        
        # 存储完整股票数据
        data_dict = stock_data.to_dict()
        
        # 转换为字符串存储
        for field, value in data_dict.items():
            if isinstance(value, list):
                pipe.hset(key, field, json.dumps(value))
            else:
                pipe.hset(key, field, str(value))
        
        # 设置过期时间
        pipe.expire(key, self.retention_config['realtime_ttl'])
    
    def _add_to_stream(self, pipe, stock_data: StockData):
        """添加到时间序列流"""
        stream_key = f"stock:stream:{stock_data.stock_code}"
        
        # 准备流数据
        stream_data = {
            'timestamp': stock_data.timestamp,
            'price': stock_data.current_price,
            'volume': stock_data.volume,
            'amount': stock_data.amount,
            'change': stock_data.current_price - stock_data.last_close if stock_data.last_close > 0 else 0
        }
        
        # 添加到流
        pipe.xadd(
            stream_key,
            stream_data,
            maxlen=self.retention_config['max_stream_length']
        )
    
    def _update_stock_list(self, pipe, stock_data: StockData):
        """更新股票列表"""
        # 按市场分类存储
        market_key = f"stocks:list:{stock_data.market}"
        pipe.sadd(market_key, stock_data.stock_code)
        
        # 全局股票列表
        pipe.sadd("stocks:all", stock_data.stock_code)
        
        # 股票基本信息
        info_key = f"stock:info:{stock_data.stock_code}"
        pipe.hset(info_key, mapping={
            'code': stock_data.stock_code,
            'name': stock_data.stock_name,
            'market': stock_data.market,
            'last_update': stock_data.timestamp
        })
        pipe.expire(info_key, self.retention_config['daily_ttl'])
    
    def _update_market_stats(self, pipe, stock_data: StockData):
        """更新市场统计"""
        # 市场统计
        market_stats_key = f"market:stats:{stock_data.market}"
        
        # 使用有序集合存储价格分布
        if stock_data.current_price > 0:
            pipe.zadd(f"market:prices:{stock_data.market}", 
                     {stock_data.stock_code: stock_data.current_price})
        
        # 成交量排行
        if stock_data.volume > 0:
            pipe.zadd(f"market:volume:{stock_data.market}",
                     {stock_data.stock_code: stock_data.volume})
        
        # 成交额排行
        if stock_data.amount > 0:
            pipe.zadd(f"market:amount:{stock_data.market}",
                     {stock_data.stock_code: stock_data.amount})
    
    def get_realtime_data(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取实时数据"""
        try:
            key = f"stock:realtime:{stock_code}"
            data = self.redis_client.hgetall(key)
            
            if not data:
                return None
            
            # 转换数据类型
            result = {}
            for field, value in data.items():
                field_str = field.decode('utf-8') if isinstance(field, bytes) else field
                value_str = value.decode('utf-8') if isinstance(value, bytes) else value
                
                # 尝试转换数据类型
                if field_str in ['ask_prices', 'bid_prices', 'ask_volumes', 'bid_volumes']:
                    result[field_str] = json.loads(value_str)
                elif field_str in ['timestamp', 'open_price', 'high_price', 'low_price', 
                                  'current_price', 'last_close', 'amount', 'turnover_rate']:
                    result[field_str] = float(value_str)
                elif field_str in ['volume']:
                    result[field_str] = int(value_str)
                else:
                    result[field_str] = value_str
            
            return result
            
        except Exception as e:
            logger.error(f"获取实时数据失败: {str(e)}")
            return None
    
    def get_stock_stream(self, stock_code: str, count: int = 100) -> List[Dict[str, Any]]:
        """获取股票时间序列数据"""
        try:
            stream_key = f"stock:stream:{stock_code}"
            
            # 获取最新的数据
            result = self.redis_client.xrevrange(stream_key, count=count)
            
            stream_data = []
            for stream_id, fields in result:
                data = {}
                for field, value in fields.items():
                    field_str = field.decode('utf-8') if isinstance(field, bytes) else field
                    value_str = value.decode('utf-8') if isinstance(value, bytes) else value
                    
                    if field_str in ['timestamp', 'price', 'amount', 'change']:
                        data[field_str] = float(value_str)
                    elif field_str in ['volume']:
                        data[field_str] = int(value_str)
                    else:
                        data[field_str] = value_str
                
                data['stream_id'] = stream_id.decode('utf-8') if isinstance(stream_id, bytes) else stream_id
                stream_data.append(data)
            
            return stream_data
            
        except Exception as e:
            logger.error(f"获取股票流数据失败: {str(e)}")
            return []
    
    def get_market_top_stocks(self, market: str, metric: str = 'volume', count: int = 50) -> List[Dict[str, Any]]:
        """获取市场热门股票"""
        try:
            key = f"market:{metric}:{market}"
            
            # 获取排行榜
            result = self.redis_client.zrevrange(key, 0, count-1, withscores=True)
            
            top_stocks = []
            for stock_code, score in result:
                stock_code_str = stock_code.decode('utf-8') if isinstance(stock_code, bytes) else stock_code
                
                # 获取股票基本信息
                stock_info = self.get_realtime_data(stock_code_str)
                if stock_info:
                    stock_info[metric] = score
                    top_stocks.append(stock_info)
            
            return top_stocks
            
        except Exception as e:
            logger.error(f"获取市场热门股票失败: {str(e)}")
            return []
    
    def cleanup_expired_data(self):
        """清理过期数据"""
        try:
            # 这个方法可以定期调用来清理过期数据
            # Redis的TTL会自动处理大部分清理工作
            
            # 清理过长的Stream
            for market in ['SZ', 'SH', 'BJ']:
                stocks = self.redis_client.smembers(f"stocks:list:{market}")
                for stock_code in stocks:
                    if isinstance(stock_code, bytes):
                        stock_code = stock_code.decode('utf-8')
                    
                    stream_key = f"stock:stream:{stock_code}"
                    # 保留最近的数据
                    self.redis_client.xtrim(stream_key, maxlen=self.retention_config['max_stream_length'])
            
            logger.info("数据清理完成")
            
        except Exception as e:
            logger.error(f"数据清理失败: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取存储统计"""
        stats = self.stats.copy()
        stats['queue_size'] = self.storage_queue.qsize()
        return stats

# 全局存储实例
redis_stock_storage = RedisStockStorage()
