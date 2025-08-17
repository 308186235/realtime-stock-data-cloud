
# 循环安全检查
import time
import signal
import threading

class LoopSafetyManager:
    """循环安全管理器"""
    
    def __init__(self, max_iterations=None, timeout=None):
        self.max_iterations = max_iterations
        self.timeout = timeout
        self.start_time = None
        self.iteration_count = 0
        self.should_stop = False
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.should_stop = True
    
    def check_loop_safety(self):
        """检查循环安全性"""
        if self.should_stop:
            raise KeyboardInterrupt("收到停止信号")
        
        if self.start_time is None:
            self.start_time = time.time()
        
        self.iteration_count += 1
        
        # 检查最大迭代次数
        if self.max_iterations and self.iteration_count > self.max_iterations:
            raise RuntimeError(f"超过最大迭代次数: {self.max_iterations}")
        
        # 检查超时
        if self.timeout:
            elapsed = time.time() - self.start_time
            if elapsed > self.timeout:
                raise TimeoutError(f"循环超时: {elapsed:.1f}s")
        
        # 定期让出CPU
        if self.iteration_count % 1000 == 0:
            time.sleep(0.001)


# 内存优化
import gc
import sys
from backend.config.performance_config import perf_config

def optimize_memory():
    """内存优化"""
    # 强制垃圾回收
    gc.collect()
    
    # 检查内存使用
    import psutil
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    if memory_mb > perf_config.MEMORY_CONFIG['cleanup_threshold_mb']:
        # 清理缓存
        if hasattr(sys.modules[__name__], '_cache'):
            sys.modules[__name__]._cache.clear()
        
        # 再次垃圾回收
        gc.collect()
        
        logger.info(f"内存优化完成,当前使用: {memory_mb:.1f}MB")

#!/usr/bin/env python3
"""
超高性能5000+股票推送接收器
专门解决100M数据堆积和服务端断开连接问题
"""

import asyncio
import redis
import time
import threading
import queue
import psutil
import logging
from typing import Dict, Any
from collections import deque
import gc

# 配置最小化日志,避免影响性能
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltraHighPerformanceReceiver:
    def __init__(self):
        # 性能优化配置
        self.max_memory_mb = 80  # 最大内存使用80MB,远低于100MB限制
        self.max_queue_size = 50000  # 最大队列大小
        self.redis_batch_size = 2000  # Redis批量大小
        self.memory_check_interval = 1  # 每秒检查内存
        
        # Redis连接池 - 高性能配置
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=3,  # 专用数据库
            decode_responses=False,  # 二进制模式
            max_connections=100,  # 增加连接数
            socket_keepalive=True,
            socket_keepalive_options={},
            health_check_interval=30,
            retry_on_timeout=True,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        
        # 超高速队列
        self.raw_data_queue = deque(maxlen=self.max_queue_size)
        self.processing_queue = queue.Queue(maxsize=10000)
        
        # 运行状态
        self.running = False
        self.threads = []
        
        # 性能统计 - 最小化
        self.stats = {
            'received': 0,
            'stored': 0,
            'memory_mb': 0,
            'queue_size': 0,
            'last_check': 0
        }
        
        # 内存监控
        self.process = psutil.Process()
        
    def start(self):
        """启动超高性能接收器"""
        logger.warning("🚀 启动5000+股票超高性能接收器...")
        
        self.running = True
        
        # 启动线程
        self.threads = [
            threading.Thread(target=self._receive_loop, daemon=True),
            threading.Thread(target=self._redis_store_loop, daemon=True),
            threading.Thread(target=self._memory_monitor_loop, daemon=True)
        ]
        
        for thread in self.threads:
            thread.start()
        
        logger.warning("✅ 超高性能接收器启动完成")
    
    def stop(self):
        """停止接收器"""
        self.running = False
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
    
    def receive_data(self, raw_data: bytes):
        """接收原始数据 - 超高速处理"""
        try:
            # 立即放入队列,绝对不做任何处理!
            self.raw_data_queue.append({
                'data': raw_data,
                'timestamp': time.time(),
                'size': len(raw_data)
            })
            
            # 最小化统计更新
            self.stats['received'] += 1
            
        except Exception:
            # 静默处理错误,不影响性能
            pass
    
    def _receive_loop(self):
        """接收循环 - 专门处理队列到Redis"""
        batch_data = []
        last_store_time = time.time()
        
        while self.running:
            try:
                # 快速收集数据
                while len(batch_data) < self.redis_batch_size and self.raw_data_queue:
                    try:
                        data_item = self.raw_data_queue.popleft()
                        batch_data.append(data_item)
                    except IndexError:
                        break
                
                # 批量存储到Redis
                if batch_data and (len(batch_data) >= self.redis_batch_size or 
                                 time.time() - last_store_time > 0.5):
                    self._store_batch_to_redis(batch_data)
                    batch_data = []
                    last_store_time = time.time()
                
                # 短暂休息,避免CPU占用过高
                time.sleep(0.001)  # 1毫秒
                
            except Exception:
                # 静默处理,不影响性能
                pass
    
    def _store_batch_to_redis(self, batch_data: list):
        """批量存储到Redis - 超高性能"""
        try:
            # 使用pipeline最大化性能
            pipe = self.redis_client.pipeline()
            
            for i, data_item in enumerate(batch_data):
                # 直接存储原始数据,不做任何解析
                pipe.lpush('stock:raw:queue', data_item['data'])
                
                # 每1000条执行一次,避免pipeline过大
                if (i + 1) % 1000 == 0:
                    pipe.execute()
                    pipe = self.redis_client.pipeline()
            
            # 执行剩余命令
            if len(batch_data) % 1000 != 0:
                pipe.execute()
            
            # 限制队列长度,防止内存溢出
            self.redis_client.ltrim('stock:raw:queue', 0, 100000)
            
            self.stats['stored'] += len(batch_data)
            
        except Exception:
            # 静默处理Redis错误
            pass
    
    def _redis_store_loop(self):
        """Redis存储循环"""
        while self.running:
            try:
                # 检查Redis连接
                self.redis_client.ping()
                
                # 清理过期数据
                if self.stats['stored'] % 10000 == 0:
                    self._cleanup_redis_data()
                
                time.sleep(5)  # 5秒检查一次
                
            except Exception:
                # Redis连接问题,尝试重连
                try:
                    self.redis_client = redis.Redis(
                        host='localhost',
                        port=6379,
                        db=3,
                        decode_responses=False,
                        max_connections=100
                    )
                except Exception:
                    pass
                
                time.sleep(1)
    
    def _memory_monitor_loop(self):
        """内存监控循环 - 防止超过100M"""
        while self.running:
            try:
                # 获取内存使用
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                self.stats['memory_mb'] = memory_mb
                self.stats['queue_size'] = len(self.raw_data_queue)
                self.stats['last_check'] = time.time()
                
                # 内存超过70MB时开始清理
                if memory_mb > 70:
                    self._emergency_cleanup()
                
                # 内存超过80MB时强制清理
                if memory_mb > 80:
                    self._force_cleanup()
                
                time.sleep(self.memory_check_interval)
                
            except Exception:
                pass
    
    def _emergency_cleanup(self):
        """紧急清理 - 防止达到100M限制"""
        try:
            # 清理队列中的旧数据
            if len(self.raw_data_queue) > 25000:
                # 保留最新的一半数据
                new_queue = deque(maxlen=self.max_queue_size)
                for _ in range(len(self.raw_data_queue) // 2):
                    if self.raw_data_queue:
                        new_queue.append(self.raw_data_queue.pop())
                self.raw_data_queue = new_queue
            
            # 强制垃圾回收
            gc.collect()
            
        except Exception:
            pass
    
    def _force_cleanup(self):
        """强制清理 - 最后手段"""
        try:
            # 清空队列
            self.raw_data_queue.clear()
            
            # 强制垃圾回收
            gc.collect()
            
            # 记录警告(但不影响性能)
            if time.time() - self.stats.get('last_warning', 0) > 60:
                logger.warning("⚠️ 内存使用过高,执行强制清理")
                self.stats['last_warning'] = time.time()
            
        except Exception:
            pass
    
    def _cleanup_redis_data(self):
        """清理Redis数据"""
        try:
            # 保持Redis队列在合理大小
            self.redis_client.ltrim('stock:raw:queue', 0, 50000)
            
        except Exception:
            pass
    
    def get_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        return {
            'received_count': self.stats['received'],
            'stored_count': self.stats['stored'],
            'memory_mb': self.stats['memory_mb'],
            'queue_size': self.stats['queue_size'],
            'memory_usage_percent': (self.stats['memory_mb'] / 100) * 100,
            'is_running': self.running,
            'last_check': self.stats['last_check']
        }
    
    def is_healthy(self) -> bool:
        """检查系统健康状态"""
        return (
            self.running and
            self.stats['memory_mb'] < 80 and
            len(self.raw_data_queue) < self.max_queue_size * 0.8
        )

# 全局实例
ultra_receiver = UltraHighPerformanceReceiver()

def start_ultra_receiver():
    """启动超高性能接收器"""
    ultra_receiver.start()
    return ultra_receiver

def stop_ultra_receiver():
    """停止超高性能接收器"""
    ultra_receiver.stop()

def receive_stock_data(raw_data: bytes):
    """接收股票数据的入口函数"""
    ultra_receiver.receive_data(raw_data)

def get_receiver_stats():
    """获取接收器统计"""
    return ultra_receiver.get_stats()

class DataAccumulationMonitor:
    """数据堆积监控器 - 防止超过100M导致服务端断开连接"""

    def __init__(self, receiver: UltraHighPerformanceReceiver):
        self.receiver = receiver
        self.max_data_size_mb = 90  # 90MB警戒线
        self.critical_size_mb = 95  # 95MB危险线
        self.monitoring = False
        self.monitor_thread = None

        # 统计信息
        self.total_data_size = 0
        self.data_rate_mb_per_sec = 0
        self.last_size_check = 0

    def start_monitoring(self):
        """开始监控数据堆积"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.warning("🔍 数据堆积监控器启动")

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)

    def _monitor_loop(self):
        """监控循环"""
        last_check_time = time.time()
        last_data_size = 0

        while self.monitoring:
            try:
                current_time = time.time()

                # 计算当前数据大小
                current_data_size = self._calculate_total_data_size()

                # 计算数据增长率
                time_diff = current_time - last_check_time
                if time_diff > 0:
                    size_diff = current_data_size - last_data_size
                    self.data_rate_mb_per_sec = size_diff / time_diff

                # 检查是否接近100M限制
                if current_data_size > self.critical_size_mb:
                    self._handle_critical_accumulation()
                elif current_data_size > self.max_data_size_mb:
                    self._handle_warning_accumulation()

                # 更新统计
                self.total_data_size = current_data_size
                self.last_size_check = current_time

                last_check_time = current_time
                last_data_size = current_data_size

                time.sleep(0.5)  # 500ms检查一次

            except Exception:
                pass

    def _calculate_total_data_size(self) -> float:
        """计算总数据大小(MB)"""
        try:
            # 内存中的数据
            memory_mb = self.receiver.stats['memory_mb']

            # Redis中的数据大小估算
            redis_size_mb = 0
            try:
                redis_info = self.receiver.redis_client.info('memory')
                redis_size_mb = redis_info.get('used_memory', 0) / 1024 / 1024
            except Exception:
                pass

            return memory_mb + redis_size_mb * 0.1  # Redis只算10%,因为是共享的

        except Exception:
            return 0

    def _handle_warning_accumulation(self):
        """处理警告级别的数据堆积"""
        try:
            # 加速数据处理
            self.receiver._emergency_cleanup()

            # 减少批量大小,加快处理速度
            self.receiver.redis_batch_size = min(1000, self.receiver.redis_batch_size)

        except Exception:
            pass

    def _handle_critical_accumulation(self):
        """处理危险级别的数据堆积"""
        try:
            # 强制清理
            self.receiver._force_cleanup()

            # 进一步减少批量大小
            self.receiver.redis_batch_size = 500

            # 清理Redis数据
            self.receiver._cleanup_redis_data()

        except Exception:
            pass

if __name__ == '__main__':
    # 测试运行
    receiver = start_ultra_receiver()

    # 启动数据堆积监控
    monitor = DataAccumulationMonitor(receiver)
    monitor.start_monitoring()

    try:
        # 模拟接收5000+股票数据
        import random

        print("🚀 开始5000+股票数据接收测试...")

        for i in range(200000):  # 模拟20万条数据
            # 模拟不同股票的数据
            stock_codes = [f'sz{j:06d}' for j in range(5000)]
            stock_code = random.choice(stock_codes)

            # 模拟股票数据
            test_data = f"{stock_code}$股票{i}$12.30$1000000${random.random()}".encode('utf-8')
            receive_stock_data(test_data)

            if i % 20000 == 0:
                stats = get_receiver_stats()
                print(f"📊 进度: {i}, 内存: {stats['memory_mb']:.2f}MB, 队列: {stats['queue_size']}, 数据率: {monitor.data_rate_mb_per_sec:.2f}MB/s")

        # 等待处理完成
        print("⏳ 等待数据处理完成...")
        time.sleep(10)

        final_stats = get_receiver_stats()
        print(f"🎉 测试完成: {final_stats}")

    except KeyboardInterrupt:
        print("⏹️ 测试被中断")
    finally:
        monitor.stop_monitoring()
        stop_ultra_receiver()
