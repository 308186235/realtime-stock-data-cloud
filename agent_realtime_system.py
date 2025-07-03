#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent实时数据接收系统 - 完整集成版本
修复Agent无法接收实时推送的问题
"""

import asyncio
import socket
import json
import time
import threading
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional
import queue
import traceback

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent_realtime.log', mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 茶股帮配置
CHAGUBANG_CONFIG = {
    'host': 'l1.chagubang.com',
    'port': 6380,
    'token': 'QT_wat5QfcJ6N9pDZM5',
    'reconnect_interval': 5,
    'max_reconnect_attempts': 10,
    'socket_timeout': 30,
    'buffer_size': 65536
}

class StockDataProcessor:
    """股票数据处理器"""
    
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
        
    def parse_chagubang_data(self, raw_data: str) -> Optional[Dict[str, Any]]:
        """解析茶股帮数据格式"""
        try:
            # 茶股帮数据格式: symbol$name$timestamp$open$high$low$current$volume$amount$买一价$买二价$买三价$买四价$买五价$买一量$买二量$买三量$买四量$买五量$卖一价$卖二价$卖三价$卖四价$卖五价$卖一量$卖二量$卖三量$卖四量$卖五量$涨跌幅$昨收价$52周最高$52周最低
            parts = raw_data.strip().split('$')
            if len(parts) < 10:  # 至少需要前10个字段
                return None

            symbol = parts[0].strip()
            name = parts[1].strip()

            # 跳过空的股票代码或名称
            if not symbol or not name or symbol.startswith('0000'):
                return None

            try:
                # 解析价格数据 (索引从0开始)
                timestamp = parts[2] if len(parts) > 2 else ""
                open_price = float(parts[3]) if len(parts) > 3 and parts[3] else 0.0
                high_price = float(parts[4]) if len(parts) > 4 and parts[4] else 0.0
                low_price = float(parts[5]) if len(parts) > 5 and parts[5] else 0.0
                current_price = float(parts[6]) if len(parts) > 6 and parts[6] else 0.0
                volume = float(parts[7]) if len(parts) > 7 and parts[7] else 0.0
                amount = float(parts[8]) if len(parts) > 8 and parts[8] else 0.0

                # 获取涨跌幅 (如果有的话，通常在第29个位置)
                change_percent = 0.0
                if len(parts) > 29 and parts[29]:
                    try:
                        change_percent = float(parts[29])
                    except:
                        # 如果没有涨跌幅数据，根据昨收价计算
                        if len(parts) > 30 and parts[30]:
                            try:
                                yesterday_close = float(parts[30])
                                if yesterday_close > 0:
                                    change_percent = ((current_price - yesterday_close) / yesterday_close * 100)
                            except:
                                pass

                # 如果还是没有涨跌幅，用开盘价估算
                if change_percent == 0.0 and open_price > 0:
                    change_percent = ((current_price - open_price) / open_price * 100)

            except (ValueError, ZeroDivisionError, IndexError):
                current_price = 0.0
                volume = 0.0
                amount = 0.0
                change_percent = 0.0
                open_price = 0.0
                high_price = 0.0
                low_price = 0.0

            # 只处理有效的股票数据
            if current_price <= 0:
                return None

            self.processed_count += 1

            return {
                'symbol': symbol,
                'name': name,
                'price': current_price,
                'change_percent': change_percent,
                'volume': volume,
                'amount': amount,
                'open_price': open_price,
                'high_price': high_price,
                'low_price': low_price,
                'timestamp': datetime.now().isoformat(),
                'raw_data': raw_data[:200]  # 只保存前200个字符
            }

        except Exception as e:
            self.error_count += 1
            logger.debug(f"解析数据失败: {e}, 原始数据: {raw_data[:100]}")
            return None

class AgentAnalysisEngine:
    """Agent分析引擎"""
    
    def __init__(self):
        self.stock_data = {}  # 最新股票数据
        self.price_history = defaultdict(lambda: deque(maxlen=100))
        self.analysis_results = {
            'market_sentiment': 'neutral',
            'confidence_score': 75,
            'recommendations': [],
            'market_stats': {},
            'last_analysis': None
        }
        
    def update_stock_data(self, stock_data: Dict[str, Any]):
        """更新股票数据"""
        symbol = stock_data['symbol']
        self.stock_data[symbol] = stock_data
        
        # 更新价格历史
        self.price_history[symbol].append({
            'price': stock_data['price'],
            'timestamp': stock_data['timestamp'],
            'change_percent': stock_data['change_percent']
        })
        
    def analyze_market(self) -> Dict[str, Any]:
        """分析市场并生成Agent建议"""
        if not self.stock_data:
            return self.analysis_results
            
        try:
            # 统计市场数据
            total_stocks = len(self.stock_data)
            rising_stocks = sum(1 for data in self.stock_data.values() if data['change_percent'] > 0)
            falling_stocks = sum(1 for data in self.stock_data.values() if data['change_percent'] < 0)
            
            # 计算市场情绪
            if rising_stocks > falling_stocks * 1.2:
                sentiment = 'bullish'
                confidence = min(90, 60 + (rising_stocks - falling_stocks) / total_stocks * 100)
            elif falling_stocks > rising_stocks * 1.2:
                sentiment = 'bearish'
                confidence = min(90, 60 + (falling_stocks - rising_stocks) / total_stocks * 100)
            else:
                sentiment = 'neutral'
                confidence = 75
                
            # 生成推荐股票
            recommendations = self._generate_recommendations()
            
            # 更新分析结果
            self.analysis_results.update({
                'market_sentiment': sentiment,
                'confidence_score': int(confidence),
                'recommendations': recommendations,
                'market_stats': {
                    'total_stocks': total_stocks,
                    'rising_stocks': rising_stocks,
                    'falling_stocks': falling_stocks,
                    'neutral_stocks': total_stocks - rising_stocks - falling_stocks
                },
                'last_analysis': datetime.now().isoformat()
            })
            
            return self.analysis_results
            
        except Exception as e:
            logger.error(f"市场分析失败: {e}")
            return self.analysis_results
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """生成股票推荐"""
        recommendations = []
        
        try:
            # 选择涨幅较大的股票作为买入推荐
            rising_stocks = [data for data in self.stock_data.values() 
                           if data['change_percent'] > 1 and data['price'] > 0]
            rising_stocks.sort(key=lambda x: x['change_percent'], reverse=True)
            
            for stock in rising_stocks[:2]:
                recommendations.append({
                    'stock_code': stock['symbol'],
                    'stock_name': stock['name'],
                    'action': 'buy',
                    'current_price': stock['price'],
                    'target_price': round(stock['price'] * 1.05, 2),
                    'reason': f"技术指标向好，涨幅{stock['change_percent']:.2f}%，成交活跃",
                    'confidence': min(85, 60 + stock['change_percent'] * 2)
                })
            
            # 选择跌幅较大的股票作为卖出建议
            falling_stocks = [data for data in self.stock_data.values() 
                            if data['change_percent'] < -2 and data['price'] > 0]
            falling_stocks.sort(key=lambda x: x['change_percent'])
            
            for stock in falling_stocks[:1]:
                recommendations.append({
                    'stock_code': stock['symbol'],
                    'stock_name': stock['name'],
                    'action': 'sell',
                    'current_price': stock['price'],
                    'target_price': round(stock['price'] * 0.95, 2),
                    'reason': f"技术指标走弱，跌幅{stock['change_percent']:.2f}%，建议减仓",
                    'confidence': min(80, 60 + abs(stock['change_percent']) * 1.5)
                })
                
        except Exception as e:
            logger.error(f"生成推荐失败: {e}")
            
        return recommendations

class AgentRealtimeSystem:
    """Agent实时数据接收系统"""
    
    def __init__(self):
        self.running = False
        self.socket = None
        self.data_processor = StockDataProcessor()
        self.analysis_engine = AgentAnalysisEngine()
        
        # 数据队列
        self.data_queue = queue.Queue(maxsize=10000)
        
        # 统计信息
        self.stats = {
            'start_time': None,
            'received_count': 0,
            'processed_count': 0,
            'error_count': 0,
            'last_receive_time': None,
            'connection_status': 'disconnected'
        }
        
        # 线程
        self.receive_thread = None
        self.process_thread = None
        self.analysis_thread = None
        
    def start(self):
        """启动Agent实时数据系统"""
        if self.running:
            logger.warning("Agent实时数据系统已在运行")
            return True
            
        logger.info("🚀 启动Agent实时数据接收系统...")
        
        try:
            self.running = True
            self.stats['start_time'] = time.time()
            
            # 启动数据接收线程
            self.receive_thread = threading.Thread(
                target=self._receive_loop,
                daemon=True,
                name="AgentDataReceiver"
            )
            self.receive_thread.start()
            
            # 启动数据处理线程
            self.process_thread = threading.Thread(
                target=self._process_loop,
                daemon=True,
                name="AgentDataProcessor"
            )
            self.process_thread.start()
            
            # 启动分析线程
            self.analysis_thread = threading.Thread(
                target=self._analysis_loop,
                daemon=True,
                name="AgentAnalyzer"
            )
            self.analysis_thread.start()
            
            logger.info("✅ Agent实时数据系统启动成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 启动Agent实时数据系统失败: {e}")
            self.running = False
            return False
    
    def stop(self):
        """停止Agent实时数据系统"""
        logger.info("⏹️ 停止Agent实时数据系统...")
        
        self.running = False
        
        # 关闭socket连接
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            
        # 等待线程结束
        for thread in [self.receive_thread, self.process_thread, self.analysis_thread]:
            if thread and thread.is_alive():
                thread.join(timeout=5)
                
        logger.info("✅ Agent实时数据系统已停止")
    
    def _connect_to_chagubang(self) -> bool:
        """连接到茶股帮服务器"""
        try:
            logger.info(f"🔗 连接茶股帮: {CHAGUBANG_CONFIG['host']}:{CHAGUBANG_CONFIG['port']}")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(CHAGUBANG_CONFIG['socket_timeout'])
            self.socket.connect((CHAGUBANG_CONFIG['host'], CHAGUBANG_CONFIG['port']))
            
            # 发送认证token
            self.socket.send(CHAGUBANG_CONFIG['token'].encode('utf-8'))
            
            self.stats['connection_status'] = 'connected'
            logger.info("✅ 茶股帮连接成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 茶股帮连接失败: {e}")
            self.stats['connection_status'] = 'disconnected'
            return False
    
    def _receive_loop(self):
        """数据接收循环"""
        reconnect_count = 0
        
        while self.running:
            try:
                # 尝试连接
                if not self._connect_to_chagubang():
                    reconnect_count += 1
                    if reconnect_count >= CHAGUBANG_CONFIG['max_reconnect_attempts']:
                        logger.error("达到最大重连次数，停止接收")
                        break
                        
                    wait_time = min(reconnect_count * CHAGUBANG_CONFIG['reconnect_interval'], 60)
                    logger.info(f"等待 {wait_time} 秒后重连...")
                    time.sleep(wait_time)
                    continue
                
                reconnect_count = 0  # 重置重连计数
                buffer = ""
                
                # 数据接收循环
                while self.running:
                    try:
                        data = self.socket.recv(CHAGUBANG_CONFIG['buffer_size'])
                        if not data:
                            logger.warning("连接断开")
                            break
                            
                        # 解码数据
                        decoded_data = data.decode('utf-8', errors='ignore')
                        buffer += decoded_data
                        
                        # 按行处理数据
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            line = line.strip()
                            
                            if line:
                                try:
                                    self.data_queue.put_nowait(line)
                                    self.stats['received_count'] += 1
                                    self.stats['last_receive_time'] = time.time()
                                except queue.Full:
                                    logger.warning("数据队列已满，丢弃数据")
                                    self.stats['error_count'] += 1
                                    
                    except socket.timeout:
                        continue
                    except Exception as e:
                        logger.error(f"接收数据错误: {e}")
                        break
                        
            except Exception as e:
                logger.error(f"接收循环错误: {e}")
                time.sleep(5)
                
        self.stats['connection_status'] = 'disconnected'
    
    def _process_loop(self):
        """数据处理循环"""
        while self.running:
            try:
                # 从队列获取数据
                raw_data = self.data_queue.get(timeout=1)
                
                # 解析股票数据
                stock_data = self.data_processor.parse_chagubang_data(raw_data)
                if stock_data:
                    # 更新到分析引擎
                    self.analysis_engine.update_stock_data(stock_data)
                    self.stats['processed_count'] += 1
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"数据处理错误: {e}")
                self.stats['error_count'] += 1
    
    def _analysis_loop(self):
        """分析循环"""
        last_analysis_time = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # 每10秒进行一次分析
                if current_time - last_analysis_time >= 10:
                    self.analysis_engine.analyze_market()
                    last_analysis_time = current_time
                    
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"分析循环错误: {e}")
                time.sleep(5)
    
    def get_agent_analysis(self) -> Dict[str, Any]:
        """获取Agent分析结果"""
        return {
            'success': True,
            'data': {
                'timestamp': datetime.now().isoformat(),
                **self.analysis_engine.analysis_results
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        elapsed = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
        receive_rate = self.stats['received_count'] / elapsed if elapsed > 0 else 0
        
        return {
            'running': self.running,
            'connection_status': self.stats['connection_status'],
            'received_count': self.stats['received_count'],
            'processed_count': self.stats['processed_count'],
            'error_count': self.stats['error_count'],
            'receive_rate': round(receive_rate, 2),
            'queue_size': self.data_queue.qsize(),
            'stock_count': len(self.analysis_engine.stock_data),
            'last_receive_time': self.stats['last_receive_time'],
            'uptime': round(elapsed, 2)
        }
    
    def print_status(self):
        """打印系统状态"""
        status = self.get_system_status()
        analysis = self.get_agent_analysis()
        
        print(f"\n📊 Agent实时数据系统状态:")
        print(f"   运行状态: {'✅ 运行中' if status['running'] else '❌ 已停止'}")
        print(f"   连接状态: {'✅ 已连接' if status['connection_status'] == 'connected' else '❌ 未连接'}")
        print(f"   接收数据: {status['received_count']} 条")
        print(f"   处理数据: {status['processed_count']} 条")
        print(f"   错误次数: {status['error_count']} 次")
        print(f"   接收速率: {status['receive_rate']} 条/秒")
        print(f"   股票数量: {status['stock_count']} 只")
        print(f"   运行时间: {status['uptime']} 秒")
        
        if analysis['data']['recommendations']:
            print(f"\n🤖 Agent分析结果:")
            print(f"   市场情绪: {analysis['data']['market_sentiment']}")
            print(f"   信心分数: {analysis['data']['confidence_score']}%")
            print(f"   推荐股票: {len(analysis['data']['recommendations'])} 只")
            
            for i, rec in enumerate(analysis['data']['recommendations'][:3], 1):
                action_emoji = "🚀" if rec['action'] == 'buy' else "⚠️"
                print(f"   {i}. {action_emoji} {rec['action'].upper()}: {rec['stock_name']} ({rec['stock_code']})")
                print(f"      当前价: ¥{rec['current_price']}, 目标价: ¥{rec['target_price']}")
                print(f"      理由: {rec['reason']}")

# 全局实例
agent_system = None

def get_agent_system():
    """获取Agent系统实例"""
    global agent_system
    if agent_system is None:
        agent_system = AgentRealtimeSystem()
    return agent_system

def main():
    """主函数 - 测试运行"""
    print("🤖 Agent实时数据接收系统测试")
    print("=" * 60)
    
    system = get_agent_system()
    
    try:
        # 启动系统
        if system.start():
            print("✅ 系统启动成功，开始接收实时数据...")
            
            # 运行60秒测试
            for i in range(12):  # 12次，每次5秒
                time.sleep(5)
                system.print_status()
                print("-" * 40)
                
        else:
            print("❌ 系统启动失败")
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
    finally:
        system.stop()
        print("👋 测试完成")

if __name__ == "__main__":
    main()
