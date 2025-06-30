"""
实时股票数据连接测试工具
用于测试QT_wat5QfcJ6N9pDZM5数据源的连接和推送功能
"""
import asyncio
import socket
import struct
import time
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
import websockets

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('realtime_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealtimeDataTester:
    """实时数据连接测试器"""
    
    def __init__(self):
        self.api_key = "QT_wat5QfcJ6N9pDZM5"
        self.test_results = {
            'connection_test': False,
            'data_reception': False,
            'websocket_test': False,
            'backend_api_test': False,
            'total_received': 0,
            'test_start_time': None,
            'test_duration': 0,
            'errors': []
        }
        
        # 测试配置
        self.config = {
            'test_duration_minutes': 5,  # 测试5分钟
            'expected_push_interval': 3,  # 期望3秒推送间隔
            'backend_url': 'http://localhost:8001',
            'websocket_url': 'ws://localhost:8001/api/realtime-data/ws'
        }
        
        self.received_data = []
        self.is_testing = False
        
    def is_market_time(self) -> bool:
        """检查是否在交易时间"""
        now = datetime.now()
        current_time = now.time()
        
        # 交易时间：9:00-15:00 (包含9:00-9:30预热时间)
        market_start = datetime.strptime("09:00", "%H:%M").time()
        market_end = datetime.strptime("15:00", "%H:%M").time()
        
        # 检查是否为工作日
        is_weekday = now.weekday() < 5  # 0-4为周一到周五
        
        return is_weekday and market_start <= current_time <= market_end
    
    def get_time_until_market_open(self) -> Optional[timedelta]:
        """获取距离开盘的时间"""
        now = datetime.now()
        
        # 如果已经是交易时间，返回None
        if self.is_market_time():
            return None
        
        # 计算下一个交易日的9:00
        next_market_day = now
        
        # 如果是周末，跳到下周一
        if now.weekday() >= 5:  # 周六或周日
            days_until_monday = 7 - now.weekday()
            next_market_day = now + timedelta(days=days_until_monday)
        # 如果是工作日但已过15:00，跳到明天
        elif now.time() > datetime.strptime("15:00", "%H:%M").time():
            next_market_day = now + timedelta(days=1)
            # 如果明天是周六，跳到下周一
            if next_market_day.weekday() >= 5:
                days_until_monday = 7 - next_market_day.weekday()
                next_market_day = next_market_day + timedelta(days=days_until_monday)
        
        # 设置为9:00
        market_open = next_market_day.replace(hour=9, minute=0, second=0, microsecond=0)
        
        return market_open - now
    
    async def test_backend_api(self) -> bool:
        """测试后端API连接"""
        logger.info("🔗 测试后端API连接...")
        
        try:
            # 测试健康检查
            response = requests.get(f"{self.config['backend_url']}/api/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ 后端API连接正常")
                
                # 测试实时数据API
                response = requests.get(f"{self.config['backend_url']}/api/realtime-data/test", timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ 实时数据API测试成功: {result.get('message', '')}")
                    self.test_results['backend_api_test'] = True
                    return True
                else:
                    logger.error(f"❌ 实时数据API测试失败: {response.status_code}")
                    
            else:
                logger.error(f"❌ 后端API连接失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ 后端API测试异常: {str(e)}")
            self.test_results['errors'].append(f"Backend API: {str(e)}")
        
        return False
    
    async def test_websocket_connection(self) -> bool:
        """测试WebSocket连接"""
        logger.info("🔌 测试WebSocket连接...")
        
        try:
            async with websockets.connect(self.config['websocket_url']) as websocket:
                logger.info("✅ WebSocket连接成功")
                
                # 发送心跳测试
                await websocket.send(json.dumps({
                    'type': 'ping'
                }))
                
                # 等待响应
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(response)
                
                if data.get('type') == 'pong':
                    logger.info("✅ WebSocket心跳测试成功")
                    self.test_results['websocket_test'] = True
                    return True
                else:
                    logger.warning(f"⚠️ WebSocket响应异常: {data}")
                    
        except asyncio.TimeoutError:
            logger.error("❌ WebSocket连接超时")
            self.test_results['errors'].append("WebSocket timeout")
        except Exception as e:
            logger.error(f"❌ WebSocket连接失败: {str(e)}")
            self.test_results['errors'].append(f"WebSocket: {str(e)}")
        
        return False
    
    async def test_realtime_data_reception(self) -> bool:
        """测试实时数据接收"""
        logger.info("📊 测试实时数据接收...")
        
        try:
            async with websockets.connect(self.config['websocket_url']) as websocket:
                # 订阅测试股票
                test_stocks = ['000001', '600000', '600519']
                
                for stock_code in test_stocks:
                    await websocket.send(json.dumps({
                        'type': 'subscribe',
                        'stock_code': stock_code
                    }))
                    logger.info(f"📈 订阅股票: {stock_code}")
                
                # 监听数据
                start_time = time.time()
                received_count = 0
                
                while time.time() - start_time < 30:  # 测试30秒
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5)
                        data = json.loads(message)
                        
                        if data.get('type') == 'stock_data':
                            received_count += 1
                            stock_code = data.get('stock_code')
                            stock_data = data.get('data', {})
                            price = stock_data.get('price', 0)
                            
                            logger.info(f"📊 收到数据: {stock_code} - 价格: {price}")
                            self.received_data.append({
                                'timestamp': time.time(),
                                'stock_code': stock_code,
                                'price': price,
                                'data': stock_data
                            })
                        
                        elif data.get('type') == 'subscription_confirmed':
                            logger.info(f"✅ 订阅确认: {data.get('stock_code')}")
                            
                    except asyncio.TimeoutError:
                        logger.warning("⏰ 等待数据超时，继续监听...")
                        continue
                
                self.test_results['total_received'] = received_count
                
                if received_count > 0:
                    logger.info(f"✅ 成功接收到 {received_count} 条实时数据")
                    self.test_results['data_reception'] = True
                    return True
                else:
                    logger.warning("⚠️ 未接收到任何实时数据")
                    
        except Exception as e:
            logger.error(f"❌ 实时数据接收测试失败: {str(e)}")
            self.test_results['errors'].append(f"Data reception: {str(e)}")
        
        return False
    
    def analyze_data_quality(self):
        """分析接收到的数据质量"""
        if not self.received_data:
            logger.warning("⚠️ 没有数据可分析")
            return
        
        logger.info("📈 分析数据质量...")
        
        # 按股票分组
        stock_data = {}
        for item in self.received_data:
            stock_code = item['stock_code']
            if stock_code not in stock_data:
                stock_data[stock_code] = []
            stock_data[stock_code].append(item)
        
        # 分析每只股票的数据
        for stock_code, data_list in stock_data.items():
            data_count = len(data_list)
            
            # 计算时间间隔
            if len(data_list) > 1:
                timestamps = [item['timestamp'] for item in data_list]
                intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
                avg_interval = sum(intervals) / len(intervals)
                
                logger.info(f"📊 {stock_code}: {data_count}条数据, 平均间隔: {avg_interval:.1f}秒")
            else:
                logger.info(f"📊 {stock_code}: {data_count}条数据")
    
    async def run_comprehensive_test(self):
        """运行综合测试"""
        logger.info("🚀 开始实时数据连接综合测试")
        logger.info("=" * 60)
        
        self.test_results['test_start_time'] = datetime.now()
        
        # 检查市场时间
        if not self.is_market_time():
            time_until_open = self.get_time_until_market_open()
            if time_until_open:
                logger.warning(f"⏰ 当前非交易时间，距离下次开盘还有: {time_until_open}")
                logger.info("💡 建议在9:00-15:00之间进行测试以获得真实数据")
            else:
                logger.info("✅ 当前在交易时间范围内")
        else:
            logger.info("✅ 当前在交易时间，可以测试真实数据推送")
        
        # 1. 测试后端API
        await self.test_backend_api()
        
        # 2. 测试WebSocket连接
        await self.test_websocket_connection()
        
        # 3. 测试实时数据接收
        await self.test_realtime_data_reception()
        
        # 4. 分析数据质量
        self.analyze_data_quality()
        
        # 生成测试报告
        self.generate_test_report()
    
    def generate_test_report(self):
        """生成测试报告"""
        logger.info("\n" + "=" * 60)
        logger.info("📋 测试报告")
        logger.info("=" * 60)
        
        test_time = datetime.now() - self.test_results['test_start_time']
        self.test_results['test_duration'] = test_time.total_seconds()
        
        # 测试结果统计
        passed_tests = sum([
            self.test_results['backend_api_test'],
            self.test_results['websocket_test'],
            self.test_results['data_reception']
        ])
        
        logger.info(f"⏱️  测试时长: {test_time}")
        logger.info(f"✅ 通过测试: {passed_tests}/3")
        logger.info(f"📊 接收数据: {self.test_results['total_received']}条")
        
        # 详细结果
        status_map = {True: "✅ 通过", False: "❌ 失败"}
        logger.info(f"🔗 后端API测试: {status_map[self.test_results['backend_api_test']]}")
        logger.info(f"🔌 WebSocket测试: {status_map[self.test_results['websocket_test']]}")
        logger.info(f"📊 数据接收测试: {status_map[self.test_results['data_reception']]}")
        
        # 错误信息
        if self.test_results['errors']:
            logger.info("\n❌ 错误信息:")
            for error in self.test_results['errors']:
                logger.info(f"   - {error}")
        
        # 建议
        logger.info("\n💡 建议:")
        if not self.test_results['backend_api_test']:
            logger.info("   - 检查后端服务是否正常运行")
        if not self.test_results['websocket_test']:
            logger.info("   - 检查WebSocket服务配置")
        if not self.test_results['data_reception']:
            logger.info("   - 检查实时数据源配置 (HOST, PORT, TOKEN)")
            logger.info("   - 确认在交易时间内测试")
        
        logger.info("=" * 60)

async def main():
    """主函数"""
    tester = RealtimeDataTester()
    
    print("🚀 实时股票数据连接测试工具")
    print("API Key: QT_wat5QfcJ6N9pDZM5")
    print("=" * 60)
    
    # 检查当前时间
    if not tester.is_market_time():
        time_until_open = tester.get_time_until_market_open()
        if time_until_open:
            print(f"⏰ 当前非交易时间")
            print(f"📅 距离下次开盘: {time_until_open}")
            print("💡 建议在9:00-15:00之间测试以获得真实数据推送")
            
            choice = input("\n是否继续测试? (y/N): ").strip().lower()
            if choice != 'y':
                print("❌ 测试已取消")
                return
    
    try:
        await tester.run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
