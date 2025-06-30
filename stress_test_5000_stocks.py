"""
5000支股票每3秒推送的压力测试
"""
import asyncio
import time
import json
import logging
import statistics
from typing import List, Dict
import sys
import os
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import random

# 添加backend目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.mass_stock_receiver import mass_stock_receiver, StockTick
from backend.services.websocket_manager_optimized import optimized_websocket_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StockDataGenerator:
    """股票数据生成器"""
    
    def __init__(self, stock_count: int = 5000):
        self.stock_count = stock_count
        self.stock_codes = self._generate_stock_codes()
        self.base_prices = {code: random.uniform(5, 200) for code in self.stock_codes}
        
    def _generate_stock_codes(self) -> List[str]:
        """生成股票代码"""
        codes = []
        
        # 深圳主板 000xxx
        for i in range(1000):
            codes.append(f"000{i:03d}")
            
        # 深圳中小板 002xxx  
        for i in range(1000):
            codes.append(f"002{i:03d}")
            
        # 深圳创业板 300xxx
        for i in range(1000):
            codes.append(f"300{i:03d}")
            
        # 上海主板 600xxx
        for i in range(1000):
            codes.append(f"600{i:03d}")
            
        # 上海科创板 688xxx
        for i in range(1000):
            codes.append(f"688{i:03d}")
        
        return codes[:self.stock_count]
    
    def generate_batch(self) -> List[Dict]:
        """生成一批股票数据"""
        batch_data = []
        current_time = time.time()
        
        for code in self.stock_codes:
            base_price = self.base_prices[code]
            
            # 生成价格波动
            change_percent = random.uniform(-10, 10)  # -10% 到 +10%
            change = base_price * (change_percent / 100)
            current_price = base_price + change
            
            # 更新基础价格
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
        """记录周期性能"""
        self.metrics['cycles_completed'] += 1
        self.metrics['total_stocks_processed'] += stocks_count
        self.metrics['cycle_times'].append(cycle_time)
        
        self.metrics['min_cycle_time'] = min(self.metrics['min_cycle_time'], cycle_time)
        self.metrics['max_cycle_time'] = max(self.metrics['max_cycle_time'], cycle_time)
        
        if self.metrics['cycle_times']:
            self.metrics['average_cycle_time'] = statistics.mean(self.metrics['cycle_times'])
        
        # 计算TPS
        if self.metrics['start_time'] > 0:
            elapsed = time.time() - self.metrics['start_time']
            self.metrics['throughput_tps'] = self.metrics['total_stocks_processed'] / elapsed
    
    def record_error(self):
        """记录错误"""
        self.metrics['errors'] += 1
    
    def start_monitoring(self):
        """开始监控"""
        self.metrics['start_time'] = time.time()
    
    def get_report(self) -> Dict:
        """获取性能报告"""
        return self.metrics.copy()

class StressTest:
    """压力测试类"""
    
    def __init__(self):
        self.stock_count = 5000
        self.push_interval = 3.0  # 3秒间隔
        self.test_duration = 300  # 5分钟测试
        
        self.data_generator = StockDataGenerator(self.stock_count)
        self.performance_monitor = PerformanceMonitor()
        
        self.running = False
        
    async def run_stress_test(self):
        """运行压力测试"""
        logger.info(f"开始5000支股票压力测试")
        logger.info(f"配置: {self.stock_count}支股票, {self.push_interval}秒间隔, {self.test_duration}秒测试时长")
        
        try:
            # 初始化服务
            await self._initialize_services()
            
            # 开始监控
            self.performance_monitor.start_monitoring()
            self.running = True
            
            # 启动测试任务
            test_task = asyncio.create_task(self._test_loop())
            monitor_task = asyncio.create_task(self._monitor_loop())
            
            # 运行指定时长
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
            await self._cleanup_services()
    
    async def _initialize_services(self):
        """初始化服务"""
        logger.info("初始化服务...")
        
        # 初始化股票接收器
        await mass_stock_receiver.initialize()
        
        # 初始化WebSocket管理器
        await optimized_websocket_manager.start()
        
        # 添加数据处理回调
        async def data_callback(batch_data: List[StockTick]):
            # 模拟推送到WebSocket客户端
            for tick in batch_data:
                await optimized_websocket_manager.push_stock_data(
                    tick.code, 
                    tick.to_dict()
                )
        
        mass_stock_receiver.add_data_callback(data_callback)
        
        logger.info("服务初始化完成")
    
    async def _cleanup_services(self):
        """清理服务"""
        logger.info("清理服务...")
        
        try:
            await mass_stock_receiver.shutdown()
            await optimized_websocket_manager.stop()
        except Exception as e:
            logger.error(f"清理服务失败: {str(e)}")
        
        logger.info("服务清理完成")
    
    async def _test_loop(self):
        """测试循环"""
        cycle_count = 0
        
        while self.running:
            try:
                cycle_start = time.time()
                
                # 生成股票数据
                stock_data_batch = self.data_generator.generate_batch()
                
                # 发送到接收器
                await mass_stock_receiver.receive_stock_batch(stock_data_batch)
                
                cycle_end = time.time()
                cycle_time = cycle_end - cycle_start
                
                # 记录性能
                self.performance_monitor.record_cycle(cycle_time, len(stock_data_batch))
                
                cycle_count += 1
                logger.debug(f"周期 {cycle_count}: 处理 {len(stock_data_batch)} 支股票, 用时 {cycle_time:.3f}秒")
                
                # 等待下一个周期
                sleep_time = max(0, self.push_interval - cycle_time)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                else:
                    logger.warning(f"周期 {cycle_count}: 处理时间超过间隔 ({cycle_time:.3f}s > {self.push_interval}s)")
                
            except Exception as e:
                logger.error(f"测试循环错误: {str(e)}")
                self.performance_monitor.record_error()
                await asyncio.sleep(1)
    
    async def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                await asyncio.sleep(30)  # 每30秒输出一次统计
                
                # 获取性能统计
                receiver_stats = mass_stock_receiver.get_performance_stats()
                websocket_stats = optimized_websocket_manager.get_stats()
                monitor_stats = self.performance_monitor.get_report()
                
                logger.info("=== 性能统计 ===")
                logger.info(f"接收器 - 周期: {receiver_stats['cycle_count']}, "
                          f"接收: {receiver_stats['received_count']}, "
                          f"处理: {receiver_stats['processed_count']}, "
                          f"接收速率: {receiver_stats['receive_rate']:.0f}/s")
                
                logger.info(f"WebSocket - 连接: {websocket_stats['active_connections']}, "
                          f"发送: {websocket_stats['total_messages_sent']}, "
                          f"失败: {websocket_stats['total_messages_failed']}, "
                          f"推送速率: {websocket_stats['push_rate']:.0f}/s")
                
                logger.info(f"监控器 - 周期: {monitor_stats['cycles_completed']}, "
                          f"平均周期时间: {monitor_stats['average_cycle_time']:.3f}s, "
                          f"TPS: {monitor_stats['throughput_tps']:.0f}, "
                          f"错误: {monitor_stats['errors']}")
                
            except Exception as e:
                logger.error(f"监控循环错误: {str(e)}")
    
    async def _generate_report(self):
        """生成测试报告"""
        logger.info("生成压力测试报告...")
        
        # 获取最终统计
        receiver_stats = mass_stock_receiver.get_performance_stats()
        websocket_stats = optimized_websocket_manager.get_stats()
        monitor_stats = self.performance_monitor.get_report()
        
        print("\n" + "="*80)
        print("🚀 5000支股票每3秒推送 - 压力测试报告")
        print("="*80)
        
        print(f"📊 测试配置:")
        print(f"   - 股票数量: {self.stock_count}")
        print(f"   - 推送间隔: {self.push_interval}秒")
        print(f"   - 测试时长: {self.test_duration}秒")
        print(f"   - 目标TPS: {self.stock_count / self.push_interval:.0f}")
        
        print(f"\n📈 接收器性能:")
        print(f"   - 完成周期: {receiver_stats['cycle_count']}")
        print(f"   - 接收总数: {receiver_stats['received_count']}")
        print(f"   - 处理总数: {receiver_stats['processed_count']}")
        print(f"   - 接收速率: {receiver_stats['receive_rate']:.0f} 股票/秒")
        print(f"   - 处理速率: {receiver_stats['process_rate']:.0f} 股票/秒")
        print(f"   - 缓冲区使用: {receiver_stats['buffer_usage']}")
        print(f"   - 错误数量: {receiver_stats['error_count']}")
        
        print(f"\n🌐 WebSocket性能:")
        print(f"   - 活跃连接: {websocket_stats['active_connections']}")
        print(f"   - 总连接数: {websocket_stats['total_connections']}")
        print(f"   - 发送消息: {websocket_stats['total_messages_sent']}")
        print(f"   - 失败消息: {websocket_stats['total_messages_failed']}")
        print(f"   - 推送速率: {websocket_stats['push_rate']:.0f} 消息/秒")
        print(f"   - 股票订阅: {websocket_stats['stock_subscriptions']}")
        
        print(f"\n⏱️ 周期性能:")
        print(f"   - 完成周期: {monitor_stats['cycles_completed']}")
        print(f"   - 平均周期时间: {monitor_stats['average_cycle_time']:.3f}秒")
        print(f"   - 最快周期: {monitor_stats['min_cycle_time']:.3f}秒")
        print(f"   - 最慢周期: {monitor_stats['max_cycle_time']:.3f}秒")
        print(f"   - 实际TPS: {monitor_stats['throughput_tps']:.0f}")
        print(f"   - 错误数量: {monitor_stats['errors']}")
        
        # 性能评估
        target_tps = self.stock_count / self.push_interval
        actual_tps = monitor_stats['throughput_tps']
        performance_ratio = (actual_tps / target_tps) * 100 if target_tps > 0 else 0
        
        print(f"\n🎯 性能评估:")
        print(f"   - 目标TPS: {target_tps:.0f}")
        print(f"   - 实际TPS: {actual_tps:.0f}")
        print(f"   - 性能达成率: {performance_ratio:.1f}%")
        
        if performance_ratio >= 95:
            print(f"   - 评级: ✅ 优秀 (≥95%)")
        elif performance_ratio >= 80:
            print(f"   - 评级: ✅ 良好 (≥80%)")
        elif performance_ratio >= 60:
            print(f"   - 评级: ⚠️ 一般 (≥60%)")
        else:
            print(f"   - 评级: ❌ 需要优化 (<60%)")
        
        print("\n💡 优化建议:")
        if monitor_stats['average_cycle_time'] > self.push_interval:
            print("   - 周期处理时间过长，建议增加并行处理")
        if receiver_stats['buffer_usage'] > 50000:
            print("   - 缓冲区使用率高，建议增加处理速度")
        if websocket_stats['total_messages_failed'] > 0:
            print("   - 存在消息发送失败，建议检查网络和连接管理")
        if monitor_stats['errors'] > 0:
            print("   - 存在处理错误，建议检查错误日志")
        
        print("="*80)

async def main():
    """主函数"""
    stress_test = StressTest()
    
    try:
        await stress_test.run_stress_test()
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 设置事件循环策略
    if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
