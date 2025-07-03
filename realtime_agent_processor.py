#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时Agent数据处理器 - 内存模式
直接处理茶股帮实时数据，提供给Agent分析
"""

import socket
import json
import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
import queue

# 茶股帮配置
CHAGUBANG_HOST = 'l1.chagubang.com'
CHAGUBANG_PORT = 6380
TOKEN = "QT_wat5QfcJ6N9pDZM5"

class RealtimeAgentProcessor:
    def __init__(self):
        self.socket = None
        self.running = False
        
        # 内存数据存储
        self.stock_data = {}  # 最新股票数据
        self.price_history = defaultdict(lambda: deque(maxlen=100))  # 价格历史
        self.volume_history = defaultdict(lambda: deque(maxlen=100))  # 成交量历史
        
        # 统计信息
        self.stats = {
            'received': 0,
            'processed': 0,
            'errors': 0,
            'start_time': time.time(),
            'last_update': None
        }
        
        # Agent分析数据
        self.agent_analysis = {
            'market_sentiment': 'neutral',
            'confidence_score': 75,
            'recommendations': [],
            'market_data': {},
            'last_analysis': None
        }
        
        # Agent虚拟账户
        self.agent_account = {
            'account_info': {
                'account_id': 'AGENT_VIRTUAL_001',
                'account_name': 'Agent虚拟交易账户',
                'account_type': 'virtual',
                'data_source': 'realtime_memory'
            },
            'balance': {
                'total_assets': 125680.50,
                'available_cash': 23450.80,
                'market_value': 101029.70,
                'total_profit_loss': 8650.30,
                'profit_loss_percent': 7.38
            },
            'positions': [
                {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'quantity': 1000,
                    'cost_price': 12.50,
                    'current_price': 13.20,
                    'market_value': 13200.00,
                    'profit_loss': 700.00,
                    'profit_loss_percent': 5.60
                },
                {
                    'stock_code': '000002',
                    'stock_name': '万科A',
                    'quantity': 2000,
                    'cost_price': 18.75,
                    'current_price': 19.40,
                    'market_value': 38800.00,
                    'profit_loss': 1300.00,
                    'profit_loss_percent': 3.47
                },
                {
                    'stock_code': '600036',
                    'stock_name': '招商银行',
                    'quantity': 1500,
                    'cost_price': 48.50,
                    'current_price': 49.05,
                    'market_value': 73575.00,
                    'profit_loss': 825.00,
                    'profit_loss_percent': 1.13
                }
            ],
            'today_trading': {
                'buy_amount': 5000.00,
                'sell_amount': 3000.00,
                'net_amount': 2000.00,
                'transaction_count': 3
            }
        }
    
    def connect_to_chagubang(self):
        """连接到茶股帮服务器"""
        try:
            print(f"🔗 连接茶股帮服务器: {CHAGUBANG_HOST}:{CHAGUBANG_PORT}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((CHAGUBANG_HOST, CHAGUBANG_PORT))
            
            # 发送token
            self.socket.send(TOKEN.encode('utf-8'))
            print("✅ 茶股帮连接成功")
            return True
            
        except Exception as e:
            print(f"❌ 茶股帮连接失败: {e}")
            return False
    
    def parse_stock_data(self, data_str):
        """解析股票数据"""
        try:
            parts = data_str.strip().split(',')
            if len(parts) < 4:
                return None
                
            symbol = parts[0].strip()
            name = parts[1].strip() if len(parts) > 1 else ""
            
            try:
                price = float(parts[2]) if len(parts) > 2 and parts[2] else 0.0
            except:
                price = 0.0
                
            try:
                change_percent = float(parts[3]) if len(parts) > 3 and parts[3] else 0.0
            except:
                change_percent = 0.0
                
            try:
                volume = int(parts[4]) if len(parts) > 4 and parts[4] else 0
            except:
                volume = 0
            
            return {
                'symbol': symbol,
                'name': name,
                'price': price,
                'change_percent': change_percent,
                'volume': volume,
                'timestamp': datetime.now().isoformat(),
                'raw_data': data_str
            }
            
        except Exception as e:
            return None
    
    def update_stock_data(self, stock_data):
        """更新股票数据到内存"""
        symbol = stock_data['symbol']
        
        # 更新最新数据
        self.stock_data[symbol] = stock_data
        
        # 更新价格历史
        self.price_history[symbol].append({
            'price': stock_data['price'],
            'timestamp': stock_data['timestamp']
        })
        
        # 更新成交量历史
        self.volume_history[symbol].append({
            'volume': stock_data['volume'],
            'timestamp': stock_data['timestamp']
        })
        
        # 更新持仓的当前价格
        for position in self.agent_account['positions']:
            if position['stock_code'] == symbol:
                position['current_price'] = stock_data['price']
                position['market_value'] = position['quantity'] * stock_data['price']
                position['profit_loss'] = position['market_value'] - (position['quantity'] * position['cost_price'])
                position['profit_loss_percent'] = (position['profit_loss'] / (position['quantity'] * position['cost_price'])) * 100
    
    def analyze_market(self):
        """Agent市场分析"""
        if not self.stock_data:
            return
        
        # 统计涨跌股票数量
        rising_stocks = sum(1 for data in self.stock_data.values() if data['change_percent'] > 0)
        falling_stocks = sum(1 for data in self.stock_data.values() if data['change_percent'] < 0)
        total_stocks = len(self.stock_data)
        
        # 计算市场情绪
        if rising_stocks > falling_stocks * 1.2:
            sentiment = 'bullish'
            confidence = min(85, 60 + (rising_stocks - falling_stocks) / total_stocks * 100)
        elif falling_stocks > rising_stocks * 1.2:
            sentiment = 'bearish'
            confidence = min(85, 60 + (falling_stocks - rising_stocks) / total_stocks * 100)
        else:
            sentiment = 'neutral'
            confidence = 75
        
        # 生成推荐股票
        recommendations = []
        
        # 选择涨幅较大的股票作为买入推荐
        rising_stocks_data = [data for data in self.stock_data.values() if data['change_percent'] > 2]
        rising_stocks_data.sort(key=lambda x: x['change_percent'], reverse=True)
        
        for i, stock in enumerate(rising_stocks_data[:2]):
            recommendations.append({
                'stock_code': stock['symbol'],
                'stock_name': stock['name'],
                'action': 'buy',
                'current_price': stock['price'],
                'target_price': stock['price'] * 1.05,
                'reason': f"技术指标向好，当前涨幅{stock['change_percent']:.2f}%"
            })
        
        # 选择跌幅较大的股票作为卖出建议
        falling_stocks_data = [data for data in self.stock_data.values() if data['change_percent'] < -2]
        falling_stocks_data.sort(key=lambda x: x['change_percent'])
        
        for i, stock in enumerate(falling_stocks_data[:1]):
            recommendations.append({
                'stock_code': stock['symbol'],
                'stock_name': stock['name'],
                'action': 'sell',
                'current_price': stock['price'],
                'target_price': stock['price'] * 0.95,
                'reason': f"技术指标走弱，当前跌幅{stock['change_percent']:.2f}%"
            })
        
        # 更新Agent分析
        self.agent_analysis.update({
            'market_sentiment': sentiment,
            'confidence_score': int(confidence),
            'recommendations': recommendations,
            'market_data': {
                'total_stocks': total_stocks,
                'rising_stocks': rising_stocks,
                'falling_stocks': falling_stocks,
                'neutral_stocks': total_stocks - rising_stocks - falling_stocks
            },
            'last_analysis': datetime.now().isoformat()
        })
    
    def receive_data(self):
        """接收数据主循环"""
        buffer = ""
        
        while self.running:
            try:
                data = self.socket.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    print("⚠️ 连接断开")
                    break
                
                buffer += data
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    
                    if line:
                        self.stats['received'] += 1
                        
                        # 解析股票数据
                        stock_data = self.parse_stock_data(line)
                        if stock_data:
                            # 更新到内存
                            self.update_stock_data(stock_data)
                            self.stats['processed'] += 1
                            self.stats['last_update'] = datetime.now().isoformat()
                        
                        # 每1000条数据进行一次市场分析
                        if self.stats['processed'] % 1000 == 0:
                            self.analyze_market()
                            self.print_stats()
                            
            except Exception as e:
                self.stats['errors'] += 1
                print(f"❌ 接收数据错误: {e}")
                break
    
    def print_stats(self):
        """打印统计信息"""
        elapsed = time.time() - self.stats['start_time']
        rate = self.stats['received'] / elapsed if elapsed > 0 else 0
        
        print(f"📊 统计: 接收{self.stats['received']} 处理{self.stats['processed']} "
              f"错误{self.stats['errors']} 速率{rate:.1f}/秒 股票{len(self.stock_data)}只")
        
        if self.agent_analysis['recommendations']:
            print(f"🤖 Agent推荐: {len(self.agent_analysis['recommendations'])}只股票")
            for rec in self.agent_analysis['recommendations'][:2]:
                print(f"   {rec['action'].upper()}: {rec['stock_name']} ({rec['stock_code']}) - {rec['reason']}")
    
    def get_agent_analysis(self):
        """获取Agent分析数据"""
        return {
            'success': True,
            'data': {
                'timestamp': datetime.now().isoformat(),
                **self.agent_analysis
            }
        }
    
    def get_agent_account(self):
        """获取Agent账户数据"""
        return {
            'success': True,
            'data': self.agent_account
        }
    
    def start(self, duration=None):
        """开始处理"""
        print("🚀 启动实时Agent数据处理器...")
        
        if not self.connect_to_chagubang():
            return False
        
        self.running = True
        self.stats['start_time'] = time.time()
        
        # 启动数据接收线程
        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.start()
        
        try:
            if duration:
                time.sleep(duration)
                self.stop()
            else:
                # 持续运行
                while self.running:
                    time.sleep(10)
                    self.analyze_market()
                    
        except KeyboardInterrupt:
            print("\n⏹️ 用户中断")
            self.stop()
        
        receive_thread.join(timeout=5)
        return True
    
    def stop(self):
        """停止处理"""
        print("⏹️ 停止数据处理...")
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

# 全局处理器实例
processor = None

def get_processor():
    """获取处理器实例"""
    global processor
    if processor is None:
        processor = RealtimeAgentProcessor()
    return processor

def main():
    """主函数"""
    print("🤖 实时Agent数据处理器 - 内存模式")
    print("=" * 50)
    print("功能:")
    print("- 接收茶股帮实时数据")
    print("- 内存存储和处理")
    print("- Agent智能分析")
    print("- 虚拟账户管理")
    print("- API数据提供")
    
    processor = get_processor()
    
    try:
        # 运行5分钟测试
        processor.start(duration=300)
        
        # 显示最终结果
        print("\n📊 最终统计:")
        processor.print_stats()
        
        print("\n🤖 Agent分析结果:")
        analysis = processor.get_agent_analysis()
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        processor.stop()

if __name__ == "__main__":
    main()
