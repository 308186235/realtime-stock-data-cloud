#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Agent是否能接收到茶股帮实时数据
"""

import socket
import time
import threading
from datetime import datetime
from collections import defaultdict

# 茶股帮配置
CHAGUBANG_HOST = 'l1.chagubang.com'
CHAGUBANG_PORT = 6380
TOKEN = "QT_wat5QfcJ6N9pDZM5"

class AgentRealtimeTest:
    def __init__(self):
        self.socket = None
        self.running = False
        self.received_data = []
        self.stock_count = defaultdict(int)
        self.stats = {
            'total_received': 0,
            'valid_parsed': 0,
            'unique_stocks': 0,
            'start_time': None,
            'last_data_time': None
        }
        
    def connect_to_chagubang(self):
        """连接茶股帮"""
        try:
            print(f"🔗 正在连接茶股帮: {CHAGUBANG_HOST}:{CHAGUBANG_PORT}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((CHAGUBANG_HOST, CHAGUBANG_PORT))
            
            print(f"📤 发送Token: {TOKEN}")
            self.socket.send(TOKEN.encode('utf-8'))
            
            print("✅ 茶股帮连接成功!")
            return True
            
        except Exception as e:
            print(f"❌ 茶股帮连接失败: {e}")
            return False
    
    def parse_stock_data(self, raw_data):
        """解析股票数据"""
        try:
            parts = raw_data.strip().split(',')
            if len(parts) >= 4:
                symbol = parts[0].strip()
                name = parts[1].strip() if len(parts) > 1 else ""
                
                try:
                    price = float(parts[2]) if parts[2] else 0.0
                except:
                    price = 0.0
                    
                try:
                    change_percent = float(parts[3]) if parts[3] else 0.0
                except:
                    change_percent = 0.0
                
                return {
                    'symbol': symbol,
                    'name': name,
                    'price': price,
                    'change_percent': change_percent,
                    'timestamp': datetime.now().isoformat(),
                    'raw': raw_data
                }
        except:
            pass
        return None
    
    def process_realtime_data(self):
        """处理实时数据"""
        buffer = ""
        
        while self.running:
            try:
                # 接收数据
                self.socket.settimeout(2)
                data = self.socket.recv(4096).decode('utf-8', errors='ignore')
                
                if not data:
                    print("⚠️ 没有接收到数据")
                    continue
                
                buffer += data
                
                # 按行处理
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    
                    if line:
                        self.stats['total_received'] += 1
                        self.stats['last_data_time'] = datetime.now()
                        
                        # 解析数据
                        parsed = self.parse_stock_data(line)
                        if parsed:
                            self.stats['valid_parsed'] += 1
                            self.received_data.append(parsed)
                            self.stock_count[parsed['symbol']] += 1
                            
                            # 保留最近1000条数据
                            if len(self.received_data) > 1000:
                                self.received_data = self.received_data[-1000:]
                        
                        # 每100条数据显示一次进度
                        if self.stats['total_received'] % 100 == 0:
                            self.show_progress()
                            
            except socket.timeout:
                continue
            except Exception as e:
                print(f"❌ 数据处理错误: {e}")
                break
    
    def show_progress(self):
        """显示进度"""
        elapsed = time.time() - self.stats['start_time']
        rate = self.stats['total_received'] / elapsed if elapsed > 0 else 0
        unique_stocks = len(self.stock_count)
        
        print(f"📊 接收: {self.stats['total_received']} | "
              f"解析: {self.stats['valid_parsed']} | "
              f"股票: {unique_stocks} | "
              f"速率: {rate:.1f}/秒")
        
        # 显示最新的几只股票
        if self.received_data:
            latest = self.received_data[-3:]
            print("📈 最新数据:")
            for data in latest:
                print(f"   {data['symbol']} {data['name']}: ¥{data['price']} ({data['change_percent']:+.2f}%)")
    
    def show_sample_data(self):
        """显示样本数据"""
        if not self.received_data:
            print("❌ 没有接收到任何数据")
            return
        
        print(f"\n📊 Agent接收到的实时数据样本 (共{len(self.received_data)}条):")
        print("-" * 80)
        
        # 显示前10条数据
        for i, data in enumerate(self.received_data[:10], 1):
            print(f"{i:2d}. {data['symbol']:8s} {data['name']:12s} "
                  f"¥{data['price']:8.2f} {data['change_percent']:+6.2f}% "
                  f"{data['timestamp']}")
        
        if len(self.received_data) > 10:
            print(f"... 还有 {len(self.received_data) - 10} 条数据")
        
        # 统计信息
        print(f"\n📈 数据统计:")
        print(f"   总接收: {self.stats['total_received']} 条")
        print(f"   有效解析: {self.stats['valid_parsed']} 条")
        print(f"   不同股票: {len(self.stock_count)} 只")
        print(f"   解析成功率: {(self.stats['valid_parsed']/self.stats['total_received']*100) if self.stats['total_received'] > 0 else 0:.1f}%")
        
        # 显示更新最频繁的股票
        if self.stock_count:
            top_stocks = sorted(self.stock_count.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"\n🔥 更新最频繁的股票:")
            for symbol, count in top_stocks:
                print(f"   {symbol}: {count} 次更新")
    
    def test_agent_analysis(self):
        """测试Agent分析功能"""
        if not self.received_data:
            print("❌ 没有数据进行Agent分析")
            return
        
        print(f"\n🤖 Agent分析测试:")
        print("-" * 50)
        
        # 简单的市场分析
        rising_stocks = [d for d in self.received_data if d['change_percent'] > 0]
        falling_stocks = [d for d in self.received_data if d['change_percent'] < 0]
        
        print(f"📊 市场概况:")
        print(f"   上涨股票: {len(rising_stocks)} 只")
        print(f"   下跌股票: {len(falling_stocks)} 只")
        print(f"   平盘股票: {len(self.received_data) - len(rising_stocks) - len(falling_stocks)} 只")
        
        # 市场情绪
        if len(rising_stocks) > len(falling_stocks):
            sentiment = "乐观"
        elif len(falling_stocks) > len(rising_stocks):
            sentiment = "悲观"
        else:
            sentiment = "中性"
        
        print(f"   市场情绪: {sentiment}")
        
        # 推荐股票
        if rising_stocks:
            top_gainers = sorted(rising_stocks, key=lambda x: x['change_percent'], reverse=True)[:3]
            print(f"\n🚀 Agent推荐 - 涨幅领先:")
            for i, stock in enumerate(top_gainers, 1):
                print(f"   {i}. {stock['name']} ({stock['symbol']}): +{stock['change_percent']:.2f}%")
        
        if falling_stocks:
            top_losers = sorted(falling_stocks, key=lambda x: x['change_percent'])[:3]
            print(f"\n⚠️  Agent警告 - 跌幅较大:")
            for i, stock in enumerate(top_losers, 1):
                print(f"   {i}. {stock['name']} ({stock['symbol']}): {stock['change_percent']:.2f}%")
    
    def run_test(self, duration=60):
        """运行测试"""
        print("🧪 Agent实时数据接收测试")
        print("=" * 60)
        print(f"测试时长: {duration} 秒")
        print("测试目标: 验证Agent能否接收茶股帮实时数据")
        print()
        
        # 连接茶股帮
        if not self.connect_to_chagubang():
            return False
        
        self.running = True
        self.stats['start_time'] = time.time()
        
        # 启动数据处理线程
        data_thread = threading.Thread(target=self.process_realtime_data)
        data_thread.start()
        
        print(f"⏱️  开始接收数据，运行 {duration} 秒...")
        
        try:
            # 等待指定时间
            time.sleep(duration)
        except KeyboardInterrupt:
            print("\n⏹️ 用户中断测试")
        
        # 停止测试
        self.running = False
        
        # 等待线程结束
        data_thread.join(timeout=5)
        
        # 关闭连接
        if self.socket:
            self.socket.close()
        
        # 显示结果
        print(f"\n🏁 测试完成!")
        self.show_sample_data()
        self.test_agent_analysis()
        
        # 判断测试结果
        success = (self.stats['total_received'] > 0 and 
                  self.stats['valid_parsed'] > 0 and 
                  len(self.stock_count) > 100)
        
        print(f"\n🎯 测试结果:")
        if success:
            print("✅ Agent可以成功接收茶股帮实时数据!")
            print("✅ 数据解析正常")
            print("✅ 可以进行智能分析")
            print("✅ 数据覆盖面广")
        else:
            print("❌ Agent接收实时数据存在问题")
            if self.stats['total_received'] == 0:
                print("❌ 没有接收到任何数据")
            elif self.stats['valid_parsed'] == 0:
                print("❌ 数据解析失败")
            elif len(self.stock_count) < 100:
                print("❌ 数据覆盖面不足")
        
        return success

def main():
    """主函数"""
    tester = AgentRealtimeTest()
    
    # 运行60秒测试
    success = tester.run_test(duration=60)
    
    if success:
        print("\n🎉 结论: Agent完全可以接收实时数据!")
        print("💡 Agent可以基于实时数据进行智能分析和交易决策")
    else:
        print("\n❌ 结论: Agent接收实时数据存在问题")
        print("💡 需要检查网络连接或数据源配置")

if __name__ == "__main__":
    main()
