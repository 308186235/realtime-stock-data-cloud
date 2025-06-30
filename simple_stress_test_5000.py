"""
简化版5000支股票每3秒推送压力测试 - 不依赖Redis
"""
import asyncio
import time
import json
import logging
import statistics
from typing import List, Dict, Set
import random
from dataclasses import dataclass
from collections import deque, defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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

class SimpleStockReceiver:
    """简化股票数据接收器"""
    
    def __init__(self):
        self.target_stocks = 5000
        self.push_interval = 3.0
        self.batch_size = 1000
        self.buffer_size = 100000
        
        # 数据存储
        self.stock_buffer = deque(maxlen=self.buffer_size)
        self.latest_data: Dict[str, StockTick] = {}
        
        # 性能统计
        self.stats = {
            'received_count': 0,
            'processed_count': 0,
            'error_count': 0,
            'receive_rate': 0,
            'process_rate': 0,
            'buffer_usage': 0,
            'cycle_count': 0
        }
        
        self.running = False
        self.data_callbacks = []
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    async def initialize(self):
        """初始化"""
        self.running = True
        # 启动处理任务
        asyncio.create_task(self._process_loop())
        logger.info("简化股票接收器初始化完成")
    
    async def shutdown(self):
        """关闭"""
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("简化股票接收器已关闭")
    
    def add_data_callback(self, callback):
        """添加数据回调"""
        self.data_callbacks.append(callback)
    
    async def receive_stock_batch(self, stock_data_list: List[Dict]):
        """接收股票数据批次"""
        try:
            start_time = time.time()
            
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
                except Exception as e:
                    self.stats['error_count'] += 1
            
            if valid_ticks:
                self.stock_buffer.extend(valid_ticks)
                
                for tick in valid_ticks:
                    self.latest_data[tick.code] = tick
                
                self.stats['received_count'] += len(valid_ticks)
                self.stats['buffer_usage'] = len(self.stock_buffer)
                
                elapsed = time.time() - start_time
                self.stats['receive_rate'] = len(valid_ticks) / elapsed if elapsed > 0 else 0
            
        except Exception as e:
            logger.error(f"接收失败: {str(e)}")
            self.stats['error_count'] += 1
    
    async def _process_loop(self):
        """处理循环"""
        while self.running:
            try:
                if self.stock_buffer:
                    batch_data = []
                    batch_count = min(len(self.stock_buffer), self.batch_size)
                    
                    for _ in range(batch_count):
                        if self.stock_buffer:
                            batch_data.append(self.stock_buffer.popleft())
                    
                    if batch_data:
                        await self._process_batch(batch_data)
                        self.stats['processed_count'] += len(batch_data)
                
                await asyncio.sleep(0.01)  # 避免CPU占用过高
                
            except Exception as e:
                logger.error(f"处理循环错误: {str(e)}")
    
    async def _process_batch(self, batch_data: List[StockTick]):
        """处理批次数据"""
        try:
            start_time = time.time()
            
            # 调用回调函数
            for callback in self.data_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(batch_data)
                    else:
                        callback(batch_data)
                except Exception as e:
                    logger.error(f"回调执行失败: {str(e)}")
            
            elapsed = time.time() - start_time
            self.stats['process_rate'] = len(batch_data) / elapsed if elapsed > 0 else 0
            
        except Exception as e:
            logger.error(f"批量处理失败: {str(e)}")
    
    def get_performance_stats(self) -> Dict:
        """获取性能统计"""
        return self.stats.copy()

class SimpleWebSocketManager:
    """简化WebSocket管理器"""
    
    def __init__(self):
        self.connections: Dict[str, Dict] = {}
        self.stock_subscribers: Dict[str, Set[str]] = defaultdict(set)
        
        self.stats = {
            'active_connections': 0,
            'total_connections': 0,
            'total_messages_sent': 0,
            'total_messages_failed': 0,
            'push_rate': 0,
            'stock_subscriptions': 0
        }
        
        self.push_queue = asyncio.Queue(maxsize=100000)
        self.running = False
    
    async def start(self):
        """启动"""
        self.running = True
        asyncio.create_task(self._push_loop())
        logger.info("简化WebSocket管理器已启动")
    
    async def stop(self):
        """停止"""
        self.running = False
        logger.info("简化WebSocket管理器已停止")
    
    async def push_stock_data(self, stock_code: str, data: Dict):
        """推送股票数据"""
        try:
            message = {
                'type': 'stock_data',
                'stock_code': stock_code,
                'data': data,
                'timestamp': time.time()
            }
            
            await self.push_queue.put((stock_code, message))
            
        except Exception as e:
            logger.error(f"推送失败: {str(e)}")
    
    async def _push_loop(self):
        """推送循环"""
        while self.running:
            try:
                batch_messages = []
                
                try:
                    stock_code, message = await asyncio.wait_for(
                        self.push_queue.get(), timeout=1.0
                    )
                    batch_messages.append((stock_code, message))
                    
                    # 收集更多消息
                    for _ in range(999):
                        try:
                            stock_code, message = self.push_queue.get_nowait()
                            batch_messages.append((stock_code, message))
                        except asyncio.QueueEmpty:
                            break
                            
                except asyncio.TimeoutError:
                    continue
                
                if batch_messages:
                    await self._process_push_batch(batch_messages)
                
            except Exception as e:
                logger.error(f"推送循环错误: {str(e)}")
    
    async def _process_push_batch(self, batch_messages: List[tuple]):
        """处理推送批次"""
        try:
            start_time = time.time()
            
            # 模拟推送处理
            self.stats['total_messages_sent'] += len(batch_messages)
            
            elapsed = time.time() - start_time
            self.stats['push_rate'] = len(batch_messages) / elapsed if elapsed > 0 else 0
            
        except Exception as e:
            logger.error(f"处理推送批次失败: {str(e)}")
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return self.stats.copy()

class StockDataGenerator:
    """股票数据生成器"""
    
    def __init__(self, stock_count: int = 5000):
        self.stock_count = stock_count
        self.stock_codes = self._generate_stock_codes()
        self.base_prices = {code: random.uniform(5, 200) for code in self.stock_codes}
        
    def _generate_stock_codes(self) -> List[str]:
        """生成股票代码"""
        codes = []
        
        for i in range(1000):
            codes.append(f"000{i:03d}")
        for i in range(1000):
            codes.append(f"002{i:03d}")
        for i in range(1000):
            codes.append(f"300{i:03d}")
        for i in range(1000):
            codes.append(f"600{i:03d}")
        for i in range(1000):
            codes.append(f"688{i:03d}")
        
        return codes[:self.stock_count]
    
    def generate_batch(self) -> List[Dict]:
        """生成一批股票数据"""
        batch_data = []
        current_time = time.time()
        
        for code in self.stock_codes:
            base_price = self.base_prices[code]
            
            change_percent = random.uniform(-5, 5)
            change = base_price * (change_percent / 100)
            current_price = base_price + change
            
            self.base_prices[code] = current_price
            
            stock_data = {
                'code': code,
                'price': round(current_price, 2),
                'volume': random.randint(100, 1000000),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'timestamp': current_time
            }
            
            batch_data.append(stock_data)
        
        return batch_data

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {
            'cycles_completed': 0,
            'total_stocks_processed': 0,
            'average_cycle_time': 0,
            'min_cycle_time': float('inf'),
            'max_cycle_time': 0,
            'cycle_times': [],
            'errors': 0,
            'start_time': 0,
            'throughput_tps': 0
        }
        
    def record_cycle(self, cycle_time: float, stocks_count: int):
        """记录周期"""
        self.metrics['cycles_completed'] += 1
        self.metrics['total_stocks_processed'] += stocks_count
        self.metrics['cycle_times'].append(cycle_time)
        
        self.metrics['min_cycle_time'] = min(self.metrics['min_cycle_time'], cycle_time)
        self.metrics['max_cycle_time'] = max(self.metrics['max_cycle_time'], cycle_time)
        
        if self.metrics['cycle_times']:
            self.metrics['average_cycle_time'] = statistics.mean(self.metrics['cycle_times'])
        
        if self.metrics['start_time'] > 0:
            elapsed = time.time() - self.metrics['start_time']
            self.metrics['throughput_tps'] = self.metrics['total_stocks_processed'] / elapsed
    
    def start_monitoring(self):
        """开始监控"""
        self.metrics['start_time'] = time.time()
    
    def get_report(self) -> Dict:
        """获取报告"""
        return self.metrics.copy()

class SimpleStressTest:
    """简化压力测试"""
    
    def __init__(self):
        self.stock_count = 5000
        self.push_interval = 3.0
        self.test_duration = 60  # 1分钟测试
        
        self.data_generator = StockDataGenerator(self.stock_count)
        self.performance_monitor = PerformanceMonitor()
        self.stock_receiver = SimpleStockReceiver()
        self.websocket_manager = SimpleWebSocketManager()
        
        self.running = False
        
    async def run_stress_test(self):
        """运行压力测试"""
        logger.info(f"开始5000支股票简化压力测试")
        logger.info(f"配置: {self.stock_count}支股票, {self.push_interval}秒间隔, {self.test_duration}秒测试")
        
        try:
            # 初始化服务
            await self.stock_receiver.initialize()
            await self.websocket_manager.start()
            
            # 添加回调
            async def data_callback(batch_data: List[StockTick]):
                for tick in batch_data:
                    await self.websocket_manager.push_stock_data(tick.code, tick.to_dict())
            
            self.stock_receiver.add_data_callback(data_callback)
            
            # 开始监控
            self.performance_monitor.start_monitoring()
            self.running = True
            
            # 启动测试
            test_task = asyncio.create_task(self._test_loop())
            monitor_task = asyncio.create_task(self._monitor_loop())
            
            # 运行测试
            await asyncio.sleep(self.test_duration)
            
            # 停止测试
            self.running = False
            test_task.cancel()
            monitor_task.cancel()
            
            # 生成报告
            await self._generate_report()
            
        except Exception as e:
            logger.error(f"压力测试失败: {str(e)}")
            raise
        finally:
            await self.stock_receiver.shutdown()
            await self.websocket_manager.stop()
    
    async def _test_loop(self):
        """测试循环"""
        cycle_count = 0
        
        while self.running:
            try:
                cycle_start = time.time()
                
                # 生成数据
                stock_data_batch = self.data_generator.generate_batch()
                
                # 发送数据
                await self.stock_receiver.receive_stock_batch(stock_data_batch)
                
                cycle_end = time.time()
                cycle_time = cycle_end - cycle_start
                
                # 记录性能
                self.performance_monitor.record_cycle(cycle_time, len(stock_data_batch))
                
                cycle_count += 1
                logger.debug(f"周期 {cycle_count}: {len(stock_data_batch)} 支股票, {cycle_time:.3f}秒")
                
                # 等待下一周期
                sleep_time = max(0, self.push_interval - cycle_time)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                else:
                    logger.warning(f"周期 {cycle_count}: 处理超时 ({cycle_time:.3f}s > {self.push_interval}s)")
                
            except Exception as e:
                logger.error(f"测试循环错误: {str(e)}")
                await asyncio.sleep(1)
    
    async def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                await asyncio.sleep(15)  # 每15秒输出统计
                
                receiver_stats = self.stock_receiver.get_performance_stats()
                websocket_stats = self.websocket_manager.get_stats()
                monitor_stats = self.performance_monitor.get_report()
                
                logger.info(f"接收器 - 接收: {receiver_stats['received_count']}, "
                          f"处理: {receiver_stats['processed_count']}, "
                          f"速率: {receiver_stats['receive_rate']:.0f}/s")
                
                logger.info(f"WebSocket - 发送: {websocket_stats['total_messages_sent']}, "
                          f"速率: {websocket_stats['push_rate']:.0f}/s")
                
                logger.info(f"监控 - 周期: {monitor_stats['cycles_completed']}, "
                          f"TPS: {monitor_stats['throughput_tps']:.0f}")
                
            except Exception as e:
                logger.error(f"监控错误: {str(e)}")
    
    async def _generate_report(self):
        """生成报告"""
        receiver_stats = self.stock_receiver.get_performance_stats()
        websocket_stats = self.websocket_manager.get_stats()
        monitor_stats = self.performance_monitor.get_report()
        
        print("\n" + "="*80)
        print("🚀 5000支股票每3秒推送 - 简化压力测试报告")
        print("="*80)
        
        print(f"📊 测试配置:")
        print(f"   - 股票数量: {self.stock_count}")
        print(f"   - 推送间隔: {self.push_interval}秒")
        print(f"   - 测试时长: {self.test_duration}秒")
        print(f"   - 目标TPS: {self.stock_count / self.push_interval:.0f}")
        
        print(f"\n📈 性能结果:")
        print(f"   - 完成周期: {monitor_stats['cycles_completed']}")
        print(f"   - 处理股票: {monitor_stats['total_stocks_processed']}")
        print(f"   - 平均周期时间: {monitor_stats['average_cycle_time']:.3f}秒")
        print(f"   - 最快周期: {monitor_stats['min_cycle_time']:.3f}秒")
        print(f"   - 最慢周期: {monitor_stats['max_cycle_time']:.3f}秒")
        print(f"   - 实际TPS: {monitor_stats['throughput_tps']:.0f}")
        
        print(f"\n📊 接收器统计:")
        print(f"   - 接收总数: {receiver_stats['received_count']}")
        print(f"   - 处理总数: {receiver_stats['processed_count']}")
        print(f"   - 接收速率: {receiver_stats['receive_rate']:.0f}/s")
        print(f"   - 处理速率: {receiver_stats['process_rate']:.0f}/s")
        
        print(f"\n🌐 WebSocket统计:")
        print(f"   - 发送消息: {websocket_stats['total_messages_sent']}")
        print(f"   - 推送速率: {websocket_stats['push_rate']:.0f}/s")
        
        # 性能评估
        target_tps = self.stock_count / self.push_interval
        actual_tps = monitor_stats['throughput_tps']
        performance_ratio = (actual_tps / target_tps) * 100 if target_tps > 0 else 0
        
        print(f"\n🎯 性能评估:")
        print(f"   - 目标TPS: {target_tps:.0f}")
        print(f"   - 实际TPS: {actual_tps:.0f}")
        print(f"   - 达成率: {performance_ratio:.1f}%")
        
        if performance_ratio >= 95:
            print(f"   - 评级: ✅ 优秀")
        elif performance_ratio >= 80:
            print(f"   - 评级: ✅ 良好")
        elif performance_ratio >= 60:
            print(f"   - 评级: ⚠️ 一般")
        else:
            print(f"   - 评级: ❌ 需要优化")
        
        print("="*80)

async def main():
    """主函数"""
    stress_test = SimpleStressTest()
    
    try:
        await stress_test.run_stress_test()
    except KeyboardInterrupt:
        logger.info("测试被中断")
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
