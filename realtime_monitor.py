"""
实时股票数据监控工具
持续监控QT_wat5QfcJ6N9pDZM5数据推送状态
"""
import asyncio
import websockets
import json
import time
import logging
from datetime import datetime
from collections import defaultdict, deque
import signal
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealtimeMonitor:
    """实时数据监控器"""
    
    def __init__(self):
        self.websocket_url = 'ws://localhost:8001/api/realtime-data/ws'
        self.api_key = "QT_wat5QfcJ6N9pDZM5"
        
        # 监控统计
        self.stats = {
            'start_time': None,
            'total_received': 0,
            'stocks_received': defaultdict(int),
            'last_received_time': None,
            'connection_count': 0,
            'error_count': 0
        }
        
        # 最近数据缓存 (保留最近100条)
        self.recent_data = deque(maxlen=100)
        
        # 监控的股票列表
        self.monitor_stocks = [
            '000001',  # 平安银行
            '600000',  # 浦发银行
            '600519',  # 贵州茅台
            '000858',  # 五粮液
            '002415',  # 海康威视
            '600036',  # 招商银行
            '300059',  # 东方财富
            '002594',  # 比亚迪
            '300750'   # 宁德时代
        ]
        
        self.running = False
        
    def is_market_time(self) -> bool:
        """检查是否在交易时间"""
        now = datetime.now()
        current_time = now.time()
        
        # 交易时间：9:00-15:00
        market_start = datetime.strptime("09:00", "%H:%M").time()
        market_end = datetime.strptime("15:00", "%H:%M").time()
        
        # 检查是否为工作日
        is_weekday = now.weekday() < 5
        
        return is_weekday and market_start <= current_time <= market_end
    
    def print_status(self):
        """打印当前状态"""
        if not self.stats['start_time']:
            return
            
        now = datetime.now()
        uptime = now - self.stats['start_time']
        
        # 清屏并打印状态
        print("\033[2J\033[H")  # 清屏
        print("🚀 实时股票数据监控器")
        print("=" * 60)
        print(f"📅 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  运行时间: {uptime}")
        print(f"🔑 API Key: {self.api_key}")
        print(f"📊 交易时间: {'✅ 是' if self.is_market_time() else '❌ 否'}")
        print("=" * 60)
        
        # 连接状态
        print(f"🔗 连接状态: {'✅ 已连接' if self.running else '❌ 未连接'}")
        print(f"📈 总接收数据: {self.stats['total_received']} 条")
        print(f"🔄 连接次数: {self.stats['connection_count']}")
        print(f"❌ 错误次数: {self.stats['error_count']}")
        
        if self.stats['last_received_time']:
            last_time = datetime.fromtimestamp(self.stats['last_received_time'])
            time_diff = (now - last_time).total_seconds()
            print(f"⏰ 最后接收: {last_time.strftime('%H:%M:%S')} ({time_diff:.1f}秒前)")
        
        print("=" * 60)
        
        # 股票数据统计
        print("📊 股票数据统计:")
        if self.stats['stocks_received']:
            for stock_code in self.monitor_stocks:
                count = self.stats['stocks_received'].get(stock_code, 0)
                print(f"   {stock_code}: {count:>4} 条")
        else:
            print("   暂无数据")
        
        print("=" * 60)
        
        # 最近数据
        print("📋 最近接收的数据 (最新5条):")
        if self.recent_data:
            for item in list(self.recent_data)[-5:]:
                timestamp = datetime.fromtimestamp(item['timestamp']).strftime('%H:%M:%S')
                print(f"   {timestamp} | {item['stock_code']} | ¥{item['price']:.2f} | {item['change']:+.2f}%")
        else:
            print("   暂无数据")
        
        print("=" * 60)
        print("💡 按 Ctrl+C 停止监控")
    
    async def connect_and_monitor(self):
        """连接并开始监控"""
        while self.running:
            try:
                self.stats['connection_count'] += 1
                logger.info(f"🔗 尝试连接WebSocket... (第{self.stats['connection_count']}次)")
                
                async with websockets.connect(self.websocket_url) as websocket:
                    logger.info("✅ WebSocket连接成功")
                    
                    # 订阅监控的股票
                    for stock_code in self.monitor_stocks:
                        await websocket.send(json.dumps({
                            'type': 'subscribe',
                            'stock_code': stock_code
                        }))
                        logger.info(f"📈 订阅股票: {stock_code}")
                        await asyncio.sleep(0.1)  # 避免发送过快
                    
                    # 监听数据
                    while self.running:
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=10)
                            await self.process_message(message)
                            
                        except asyncio.TimeoutError:
                            # 发送心跳
                            await websocket.send(json.dumps({'type': 'ping'}))
                            continue
                            
            except websockets.exceptions.ConnectionClosed:
                logger.warning("⚠️ WebSocket连接断开，尝试重连...")
                self.stats['error_count'] += 1
                await asyncio.sleep(5)  # 等待5秒后重连
                
            except Exception as e:
                logger.error(f"❌ 连接错误: {str(e)}")
                self.stats['error_count'] += 1
                await asyncio.sleep(10)  # 等待10秒后重连
    
    async def process_message(self, message: str):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'stock_data':
                # 处理股票数据
                stock_code = data.get('stock_code')
                stock_data = data.get('data', {})
                
                self.stats['total_received'] += 1
                self.stats['stocks_received'][stock_code] += 1
                self.stats['last_received_time'] = time.time()
                
                # 保存到最近数据
                self.recent_data.append({
                    'timestamp': time.time(),
                    'stock_code': stock_code,
                    'price': stock_data.get('price', 0),
                    'change': stock_data.get('change_percent', 0)
                })
                
            elif message_type == 'subscription_confirmed':
                logger.info(f"✅ 订阅确认: {data.get('stock_code')}")
                
            elif message_type == 'pong':
                logger.debug("💓 心跳响应")
                
        except json.JSONDecodeError:
            logger.error(f"❌ 消息解析失败: {message}")
        except Exception as e:
            logger.error(f"❌ 处理消息失败: {str(e)}")
    
    async def status_updater(self):
        """状态更新器"""
        while self.running:
            self.print_status()
            await asyncio.sleep(2)  # 每2秒更新一次状态
    
    async def start_monitoring(self):
        """开始监控"""
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        logger.info("🚀 启动实时数据监控...")
        
        # 创建监控任务
        tasks = [
            asyncio.create_task(self.connect_and_monitor()),
            asyncio.create_task(self.status_updater())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("⏹️ 监控被用户中断")
        finally:
            self.running = False
            for task in tasks:
                task.cancel()
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        logger.info("🛑 停止监控...")

def signal_handler(signum, frame):
    """信号处理器"""
    print("\n⏹️ 接收到停止信号，正在退出...")
    sys.exit(0)

async def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    monitor = RealtimeMonitor()
    
    print("🚀 实时股票数据监控器")
    print("API Key: QT_wat5QfcJ6N9pDZM5")
    print("=" * 60)
    
    # 检查交易时间
    if not monitor.is_market_time():
        print("⏰ 当前非交易时间 (9:00-15:00)")
        print("💡 在非交易时间可能无法接收到真实数据推送")
        
        choice = input("是否继续监控? (y/N): ").strip().lower()
        if choice != 'y':
            print("❌ 监控已取消")
            return
    
    print("🔄 开始监控，按 Ctrl+C 停止...")
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n⏹️ 监控已停止")
    except Exception as e:
        print(f"\n❌ 监控过程中发生错误: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 再见！")
    except Exception as e:
        print(f"❌ 程序错误: {str(e)}")
