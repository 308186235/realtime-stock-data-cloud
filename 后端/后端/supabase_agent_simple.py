#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于Supabase的Agent智能交易系统 - 简化版本
不依赖复杂的技术分析库,使用基础计算
"""

import socket
import time
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supabase配置
SUPABASE_CONFIG = {
    'url': 'https://process.env.SUPABASE_URL',
    'key': 'process.env.SUPABASE_ANON_KEY
}

# 茶股帮配置
CHAGUBANG_CONFIG = {
    'host': 'l1.chagubang.com',
    'port': 6380,
    'token': 'process.env.STOCK_API_KEY'
}

# 交易配置
TRADING_CONFIG = {
    'enable_beijing_exchange': False,  # 北交所开关,默认关闭
    'trading_start_time': "09:10",     # 交易开始时间
    'trading_end_time': "15:00",       # 交易结束时间
    'reconnect_interval': 30,          # 重连间隔(秒)
    'max_reconnect_attempts': 10,      # 最大重连次数
    'analysis_interval': 40            # Agent分析间隔(秒)
}

class SupabaseClient:
    """简化的Supabase客户端"""
    
    def __init__(self):
        self.base_url = SUPABASE_CONFIG['url']
        self.headers = {
            'apikey': SUPABASE_CONFIG['key'],
            'Authorization': f"Bearer {SUPABASE_CONFIG['key']}",
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    
    def insert(self, table: str, data: Dict) -> bool:
        """插入数据"""
        try:
            url = f"{self.base_url}/rest/v1/{table}"
            response = requests.post(url, headers=self.headers, json=data)
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"插入数据失败: {e}")
            return False
    
    def select(self, table: str, filters: Dict = None, limit: int = None) -> List[Dict]:
        """查询数据"""
        try:
            url = f"{self.base_url}/rest/v1/{table}"
            params = {}

            if filters:
                for key, value in filters.items():
                    params[key] = f"eq.{value}"

            if limit:
                params['limit'] = limit

            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            logger.error(f"查询数据失败: {e}")
            return []

    def delete(self, table: str, filters: Dict) -> bool:
        """删除数据"""
        try:
            url = f"{self.base_url}/rest/v1/{table}"
            params = {}

            if filters:
                for key, value in filters.items():
                    params[key] = f"eq.{value}"

            response = requests.delete(url, headers=self.headers, params=params)
            return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"删除数据失败: {e}")
            return False

class SimpleTechnicalAnalyzer:
    """简化的技术分析器"""
    
    @staticmethod
    def calculate_ma(prices: List[float], period: int) -> float:
        """计算移动平均线"""
        if len(prices) < period:
            return 0.0
        return sum(prices[-period:]) / period
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """计算RSI指标"""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return 50.0
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def analyze_trend(prices: List[float]) -> str:
        """分析价格趋势"""
        if len(prices) < 3:
            return 'UNKNOWN'
        
        recent_prices = prices[-3:]
        if recent_prices[-1] > recent_prices[-2] > recent_prices[-3]:
            return 'STRONG_UP'
        elif recent_prices[-1] > recent_prices[-2]:
            return 'UP'
        elif recent_prices[-1] < recent_prices[-2] < recent_prices[-3]:
            return 'STRONG_DOWN'
        elif recent_prices[-1] < recent_prices[-2]:
            return 'DOWN'
        else:
            return 'SIDEWAYS'

class SupabaseAgentSystem:
    """基于Supabase的Agent系统 - 简化版"""
    
    def __init__(self):
        self.supabase = SupabaseClient()
        self.analyzer = SimpleTechnicalAnalyzer()
        self.stock_data = {}
        self.price_history = {}  # 存储价格历史用于技术分析
        self.reconnect_count = 0
        self.load_trading_config()  # 启动时加载配置

    def update_trading_config(self, enable_beijing: bool = None):
        """更新交易配置"""
        if enable_beijing is not None:
            TRADING_CONFIG['enable_beijing_exchange'] = enable_beijing
            status = "开启" if enable_beijing else "关闭"
            logger.info(f"🔧 北交所交易权限已{status}")

            # 保存配置到数据库
            config_data = {
                'config_key': 'enable_beijing_exchange',
                'config_value': str(enable_beijing).lower(),
                'updated_at': datetime.now().isoformat()
            }
            self.supabase.insert('trading_config', config_data)

    def load_trading_config(self):
        """从数据库加载交易配置"""
        try:
            configs = self.supabase.select('trading_config', limit=10)
            for config in configs:
                key = config.get('config_key')
                value = config.get('config_value')

                if key == 'enable_beijing_exchange':
                    TRADING_CONFIG['enable_beijing_exchange'] = value.lower() == 'true'

            logger.info(f"📋 配置加载完成,北交所权限: {'开启' if TRADING_CONFIG['enable_beijing_exchange'] else '关闭'}")
        except Exception as e:
            logger.warning(f"配置加载失败,使用默认配置: {e}")

    def is_trading_time(self):
        """检查是否在交易时间内"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        # 检查是否是工作日
        if now.weekday() >= 5:  # 周六日
            return False

        # 检查时间范围
        start_time = TRADING_CONFIG['trading_start_time']
        end_time = TRADING_CONFIG['trading_end_time']

        return start_time <= current_time <= end_time
        
    def start_realtime_system(self):
        """启动实时数据接收和分析系统"""
        logger.info("🚀 启动基于Supabase的Agent实时系统...")
        
        try:
            # 连接茶股帮
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((CHAGUBANG_CONFIG['host'], CHAGUBANG_CONFIG['port']))
            sock.send(CHAGUBANG_CONFIG['token'].encode('utf-8'))
            
            logger.info("✅ 茶股帮连接成功,开始接收数据...")
            
            data_buffer = ""
            processed_count = 0
            saved_count = 0
            last_analysis_time = 0
            
            while True:
                try:
                    data = sock.recv(8192)
                    if data:
                        decoded_data = data.decode('utf-8', errors='ignore')
                        data_buffer += decoded_data
                        
                        # 处理数据
                        if len(data_buffer) > 50000:
                            records = self._extract_stock_records(data_buffer)
                            
                            for record in records:
                                stock_info = self._parse_stock_data(record)
                                if stock_info:
                                    processed_count += 1
                                    
                                    # 更新内存中的股票数据
                                    symbol = stock_info['symbol']
                                    self.stock_data[symbol] = stock_info
                                    
                                    # 更新价格历史
                                    if symbol not in self.price_history:
                                        self.price_history[symbol] = []
                                    self.price_history[symbol].append(stock_info['price'])
                                    # 只保留最近100个价格点
                                    if len(self.price_history[symbol]) > 100:
                                        self.price_history[symbol] = self.price_history[symbol][-100:]
                                    
                                    # 每10条数据保存一次到Supabase
                                    if processed_count % 10 == 0:
                                        if self._save_to_supabase(stock_info):
                                            saved_count += 1
                                    
                                    # 每处理100条数据显示进度
                                    if processed_count % 100 == 0:
                                        logger.info(f"📊 已处理 {processed_count} 条数据,保存 {saved_count} 条,股票池: {len(self.stock_data)} 只")
                            
                            data_buffer = data_buffer[-10000:]  # 保留最后10KB
                        
                        # 每30秒进行一次Agent分析
                        current_time = time.time()
                        if current_time - last_analysis_time >= 30:
                            self._perform_agent_analysis()
                            last_analysis_time = current_time
                            
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"数据处理错误: {e}")
                    break
            
            sock.close()
            
        except Exception as e:
            logger.error(f"实时系统启动失败: {e}")
    
    def _extract_stock_records(self, data_stream: str) -> List[str]:
        """从数据流中提取股票记录"""
        import re
        pattern = r'(S[HZ]\d{6}\$[^S]*?)(?=S[HZ]\d{6}\$|$)'
        return re.findall(pattern, data_stream)
    
    def _parse_stock_data(self, raw_data: str) -> Optional[Dict]:
        """解析股票数据"""
        try:
            parts = raw_data.strip().split('$')
            if len(parts) < 10:
                return None
            
            symbol = parts[0].strip()
            name = parts[1].strip()
            
            # 跳过指数数据
            if symbol.startswith('SH0000') or symbol.startswith('SZ0000') or symbol.startswith('SZ399'):
                return None
            
            if not symbol or not name or len(symbol) < 6:
                return None
            
            current_price = float(parts[6]) if parts[6] else 0.0
            volume = float(parts[7]) if len(parts) > 7 and parts[7] else 0.0
            amount = float(parts[8]) if len(parts) > 8 and parts[8] else 0.0
            
            change_percent = 0.0
            if len(parts) > 29 and parts[29]:
                try:
                    change_percent = float(parts[29])
                except:
                    pass
            
            if current_price <= 0:
                return None
            
            return {
                'symbol': symbol,
                'name': name,
                'price': current_price,
                'change_percent': change_percent,
                'volume': volume,
                'amount': amount,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return None
    
    def _save_to_supabase(self, stock_info: Dict) -> bool:
        """保存数据到Supabase"""
        try:
            # 保存到stock_quotes表
            quote_data = {
                'symbol': stock_info['symbol'],
                'trade_time': stock_info['timestamp'],
                'price': stock_info['price'],
                'change_percent': stock_info['change_percent'],
                'volume': stock_info['volume'],
                'amount': stock_info['amount']
            }
            
            return self.supabase.insert('stock_quotes', quote_data)
            
        except Exception as e:
            logger.error(f"保存到Supabase失败: {e}")
            return False
    
    def _clean_stock_data(self, stock: Dict) -> tuple[bool, str]:
        """数据清洗:过滤不符合条件的股票"""
        try:
            symbol = stock.get('symbol', '')
            name = stock.get('name', '')
            price = stock.get('price', 0)
            volume = stock.get('volume', 0)
            amount = stock.get('amount', 0)
            change_percent = stock.get('change_percent', 0)

            # 1. 过滤停牌股票(成交量为0或极小)
            if volume <= 100:
                return False, "停牌/成交量过小"

            # 2. 过滤ST股票
            if 'ST' in name or '*ST' in name or 'S*ST' in name:
                return False, "ST股票"

            # 3. 过滤新股(上市不足30天,简化判断:股票代码后3位大于800的新股)
            if symbol.startswith('SZ30') or symbol.startswith('SH68'):
                code_num = symbol[-3:]
                if code_num.isdigit() and int(code_num) > 800:
                    return False, "新股"

            # 4. 过滤价格异常股票
            if price <= 0 or price > 1000:  # 价格异常
                return False, "价格异常"

            # 5. 过滤涨跌停股票(避免追高杀跌)
            if abs(change_percent) >= 9.8:  # 接近涨跌停
                return False, "涨跌停"

            # 6. 过滤成交额过小的股票(流动性不足)
            if amount < 10000000:  # 成交额小于1000万
                return False, "成交额过小"

            # 7. 北交所股票处理(根据配置决定是否过滤)
            is_beijing_stock = symbol.startswith('BJ') or any(symbol.endswith(x) for x in ['43', '83', '87'])
            if is_beijing_stock and not TRADING_CONFIG['enable_beijing_exchange']:
                return False, "北交所股票(未开启)"

            return True, "通过"

        except Exception as e:
            logger.error(f"数据清洗错误: {e}")
            return False, f"错误: {e}"

    def _perform_agent_analysis(self):
        """执行Agent智能分析"""
        if not self.stock_data:
            return

        logger.info("🤖 开始Agent智能分析...")

        # 数据清洗:过滤符合条件的股票
        cleaned_stocks = {}
        filter_stats = {}

        for symbol, stock in self.stock_data.items():
            is_valid, reason = self._clean_stock_data(stock)
            if is_valid:
                cleaned_stocks[symbol] = stock
            else:
                filter_stats[reason] = filter_stats.get(reason, 0) + 1

        logger.info(f"📊 数据清洗完成:{len(self.stock_data)} -> {len(cleaned_stocks)} 只股票")
        if filter_stats:
            filter_info = ", ".join([f"{reason}: {count}只" for reason, count in filter_stats.items()])
            logger.info(f"🔍 过滤详情:{filter_info}")

        # 选择表现突出的股票进行深度分析
        rising_stocks = [
            stock for stock in cleaned_stocks.values()
            if stock['change_percent'] > 3
        ]

        falling_stocks = [
            stock for stock in cleaned_stocks.values()
            if stock['change_percent'] < -3
        ]
        
        decisions_made = 0
        
        # 分析涨幅较大的股票
        for stock in sorted(rising_stocks, key=lambda x: x['change_percent'], reverse=True)[:5]:
            decision = self._analyze_single_stock(stock, 'rising')
            if decision and self._save_decision_to_supabase(decision):
                decisions_made += 1
        
        # 分析跌幅较大的股票
        for stock in sorted(falling_stocks, key=lambda x: x['change_percent'])[:3]:
            decision = self._analyze_single_stock(stock, 'falling')
            if decision and self._save_decision_to_supabase(decision):
                decisions_made += 1
        
        logger.info(f"✅ Agent分析完成,生成 {decisions_made} 个决策,分析了 {len(rising_stocks) + len(falling_stocks)} 只异动股票")
    
    def _analyze_single_stock(self, stock: Dict, trend_type: str) -> Optional[Dict]:
        """分析单只股票"""
        symbol = stock['symbol']
        
        # 获取价格历史进行技术分析
        prices = self.price_history.get(symbol, [])
        
        # 计算技术指标
        technical_signals = {}
        if len(prices) >= 5:
            technical_signals['ma5'] = self.analyzer.calculate_ma(prices, 5)
            technical_signals['ma20'] = self.analyzer.calculate_ma(prices, 20) if len(prices) >= 20 else 0
            technical_signals['rsi'] = self.analyzer.calculate_rsi(prices)
            technical_signals['trend'] = self.analyzer.analyze_trend(prices)
        
        # 生成决策
        if trend_type == 'rising':
            action = 'BUY'
            base_confidence = 60 + min(30, stock['change_percent'] * 2)
            
            # 技术指标加分
            if technical_signals.get('rsi', 50) < 70:  # 未超买
                base_confidence += 5
            if technical_signals.get('trend') in ['UP', 'STRONG_UP']:
                base_confidence += 10
            
            confidence = min(95, base_confidence)
            reason = f"强势上涨{stock['change_percent']:.2f}%"
            
            if technical_signals:
                reason += f",RSI:{technical_signals.get('rsi', 0):.1f}"
                
        else:
            action = 'SELL'
            base_confidence = 60 + min(25, abs(stock['change_percent']) * 1.5)
            
            # 技术指标加分
            if technical_signals.get('rsi', 50) > 30:  # 未超卖
                base_confidence += 5
            if technical_signals.get('trend') in ['DOWN', 'STRONG_DOWN']:
                base_confidence += 10
            
            confidence = min(90, base_confidence)
            reason = f"大幅下跌{stock['change_percent']:.2f}%"
            
            if technical_signals:
                reason += f",RSI:{technical_signals.get('rsi', 0):.1f}"
        
        return {
            'symbol': symbol,
            'action': action,
            'price': stock['price'],
            'confidence': int(confidence),
            'reason': reason,
            'technical_signals': technical_signals,
            'timestamp': datetime.now().isoformat()
        }
    
    def _save_decision_to_supabase(self, decision: Dict) -> bool:
        """保存Agent决策到Supabase"""
        try:
            decision_data = {
                'symbol': decision['symbol'],
                'decision_time': decision['timestamp'],
                'action': decision['action'],
                'price': decision['price'],
                'confidence': decision['confidence'],
                'reason': decision['reason'],
                'technical_signals': decision['technical_signals']
            }
            
            return self.supabase.insert('agent_decisions', decision_data)
            
        except Exception as e:
            logger.error(f"保存决策失败: {e}")
            return False
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict]:
        """获取最近的Agent决策"""
        return self.supabase.select('agent_decisions', limit=limit)
    
    def get_dashboard_data(self) -> Dict:
        """获取仪表板数据"""
        recent_decisions = self.get_recent_decisions(10)
        
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'total_stocks_monitored': len(self.stock_data),
            'recent_decisions': recent_decisions,
            'market_summary': {
                'rising_stocks': len([s for s in self.stock_data.values() if s['change_percent'] > 0]),
                'falling_stocks': len([s for s in self.stock_data.values() if s['change_percent'] < 0]),
                'active_stocks': len([s for s in self.stock_data.values() if abs(s['change_percent']) > 1])
            }
        }
        
        return dashboard

def main():
    """主函数"""
    print("🤖 基于Supabase的Agent智能交易系统 (简化版)")
    print("=" * 60)
    
    agent_system = SupabaseAgentSystem()
    
    print("请选择操作:")
    print("1. 启动实时Agent系统")
    print("2. 查看Agent仪表板")
    print("3. 查看最近决策")
    print("4. 测试Supabase连接")
    
    choice = input("请输入选择 (1-4): ").strip()
    
    if choice == '1':
        print("🚀 启动实时Agent系统...")
        print("系统将接收茶股帮实时数据并保存到Supabase")
        print("按 Ctrl+C 停止系统")
        agent_system.start_realtime_system()
        
    elif choice == '2':
        dashboard = agent_system.get_dashboard_data()
        print(f"\n📊 Agent仪表板 ({dashboard['timestamp']})")
        print(f"监控股票数量: {dashboard['total_stocks_monitored']}")
        print(f"上涨股票: {dashboard['market_summary']['rising_stocks']}")
        print(f"下跌股票: {dashboard['market_summary']['falling_stocks']}")
        print(f"活跃股票: {dashboard['market_summary']['active_stocks']}")
        
    elif choice == '3':
        decisions = agent_system.get_recent_decisions(5)
        print(f"\n🎯 最近5个Agent决策:")
        if decisions:
            for i, decision in enumerate(decisions, 1):
                print(f"{i}. {decision.get('action', 'N/A')}: {decision.get('symbol', 'N/A')} - {decision.get('reason', 'N/A')}")
                print(f"   信心度: {decision.get('confidence', 0)}%, 时间: {decision.get('decision_time', 'N/A')}")
        else:
            print("暂无决策记录")
            
    elif choice == '4':
        print("🔗 测试Supabase连接...")
        test_data = {
            'symbol': 'TEST001',
            'trade_time': datetime.now().isoformat(),
            'price': 10.0,
            'change_percent': 1.5,
            'volume': 1000,
            'amount': 10000
        }
        
        if agent_system.supabase.insert('stock_quotes', test_data):
            print("✅ Supabase连接测试成功!")
        else:
            print("❌ Supabase连接测试失败")
    
    else:
        print("无效选择")

if __name__ == "__main__":
    main()
