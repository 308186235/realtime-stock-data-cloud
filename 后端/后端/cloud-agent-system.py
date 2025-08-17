#!/usr/bin/env python3
"""
真正的云端Agent智能交易系统
部署到Railway平台,完全云端运行
"""

import os
import socket
import json
import time
import requests
import logging
from datetime import datetime
import threading
from typing import Dict, List, Optional
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supabase配置
SUPABASE_CONFIG = {
    'url': 'https://process.env.SUPABASE_URL',
    'anon_key': 'process.env.SUPABASE_ANON_KEY
}

# 茶股帮配置
CHAGUBANG_CONFIG = {
    'host': 'l1.chagubang.com',
    'port': 6380,
    'token': 'process.env.STOCK_API_KEY'
}

class CloudAgentSystem:
    def __init__(self):
        self.running = False
        self.socket = None
        self.stock_pool = {}
        self.stats = {
            'received': 0,
            'processed': 0,
            'decisions': 0,
            'errors': 0,
            'start_time': time.time()
        }
        
    def connect_to_chagubang(self):
        """连接茶股帮"""
        try:
            logger.info(f"🔗 连接茶股帮: {CHAGUBANG_CONFIG['host']}:{CHAGUBANG_CONFIG['port']}")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((CHAGUBANG_CONFIG['host'], CHAGUBANG_CONFIG['port']))
            
            # 发送token
            self.socket.send(CHAGUBANG_CONFIG['token'].encode('utf-8'))
            
            logger.info("✅ 茶股帮连接成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 茶股帮连接失败: {e}")
            return False
    
    def save_decision_to_supabase(self, decision_data):
        """保存Agent决策到Supabase"""
        try:
            headers = {
                'apikey': SUPABASE_CONFIG['anon_key'],
                'Authorization': f"Bearer {SUPABASE_CONFIG['anon_key']}",
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }
            
            response = requests.post(
                f"{SUPABASE_CONFIG['url']}/rest/v1/agent_decisions",
                headers=headers,
                json=decision_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                self.stats['decisions'] += 1
                return True
            else:
                logger.error(f"❌ Supabase保存失败: {response.status_code}")
                self.stats['errors'] += 1
                return False
                
        except Exception as e:
            logger.error(f"❌ Supabase保存错误: {e}")
            self.stats['errors'] += 1
            return False
    
    def parse_stock_data(self, line):
        """解析股票数据"""
        try:
            # 茶股帮数据格式可能是JSON或分隔符格式
            if line.startswith('{'):
                # JSON格式
                data = json.loads(line)
                return {
                    'symbol': data.get('symbol', ''),
                    'name': data.get('name', ''),
                    'price': float(data.get('price', 0)),
                    'change_percent': float(data.get('change_percent', 0)),
                    'volume': int(data.get('volume', 0)),
                    'amount': float(data.get('amount', 0)),
                    'high': float(data.get('high', 0)),
                    'low': float(data.get('low', 0)),
                    'open': float(data.get('open', 0)),
                    'prev_close': float(data.get('prev_close', 0))
                }
            else:
                # 分隔符格式
                parts = line.split('|')
                if len(parts) >= 10:
                    return {
                        'symbol': parts[0],
                        'name': parts[1] or '',
                        'price': float(parts[2]) if parts[2] else 0,
                        'change_percent': float(parts[3]) if parts[3] else 0,
                        'volume': int(parts[4]) if parts[4] else 0,
                        'amount': float(parts[5]) if parts[5] else 0,
                        'high': float(parts[6]) if parts[6] else 0,
                        'low': float(parts[7]) if parts[7] else 0,
                        'open': float(parts[8]) if parts[8] else 0,
                        'prev_close': float(parts[9]) if parts[9] else 0
                    }
        except Exception as e:
            logger.debug(f"解析数据失败: {e}")
        
        return None
    
    def clean_stock_data(self, stocks):
        """数据清洗"""
        cleaned = {}
        filter_stats = {
            '涨跌停': 0,
            '北交所股票': 0,
            '价格异常': 0,
            '新股': 0,
            '成交额过小': 0
        }
        
        for symbol, stock in stocks.items():
            # 过滤涨跌停
            if abs(stock['change_percent']) >= 9.8:
                filter_stats['涨跌停'] += 1
                continue
                
            # 过滤北交所股票
            if symbol.startswith('BJ') or symbol.startswith('8') or symbol.startswith('4'):
                filter_stats['北交所股票'] += 1
                continue
                
            # 过滤价格异常
            if stock['price'] <= 0 or stock['price'] > 1000:
                filter_stats['价格异常'] += 1
                continue
                
            # 过滤新股(简单判断)
            if stock['volume'] < 1000:
                filter_stats['新股'] += 1
                continue
                
            # 过滤成交额过小
            if stock['amount'] < 10000:
                filter_stats['成交额过小'] += 1
                continue
                
            cleaned[symbol] = stock
        
        logger.info(f"📊 数据清洗完成:{len(stocks)} -> {len(cleaned)} 只股票")
        logger.info(f"🔍 过滤详情:{', '.join([f'{k}: {v}只' for k, v in filter_stats.items() if v > 0])}")
        
        return cleaned
    
    def agent_analysis(self, stocks):
        """Agent智能分析"""
        decisions = []
        
        # 筛选异动股票
        abnormal_stocks = []
        for symbol, stock in stocks.items():
            if abs(stock['change_percent']) > 3 or stock['volume'] > 1000000:
                abnormal_stocks.append((symbol, stock))
        
        logger.info(f"🔍 发现 {len(abnormal_stocks)} 只异动股票")
        
        # 对异动股票进行分析
        for symbol, stock in abnormal_stocks[:100]:  # 限制分析数量
            try:
                # Agent智能分析逻辑
                action = self.analyze_stock_action(stock)
                confidence = self.calculate_confidence(stock)
                reason = self.generate_reason(stock, action)
                
                if action != 'hold':  # 只保存非持有决策
                    decision = {
                        'symbol': symbol,
                        'stock_name': stock['name'],
                        'action': action,
                        'current_price': stock['price'],
                        'change_percent': stock['change_percent'],
                        'volume': stock['volume'],
                        'confidence': confidence,
                        'reason': reason,
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                    decisions.append(decision)
                    
            except Exception as e:
                logger.error(f"分析股票 {symbol} 失败: {e}")
        
        return decisions
    
    def analyze_stock_action(self, stock):
        """分析股票操作"""
        change_percent = stock['change_percent']
        volume = stock['volume']
        price = stock['price']
        
        # 简单的分析逻辑
        if change_percent > 7 and volume > 2000000:
            return 'sell'  # 高涨幅高成交量,可能见顶
        elif change_percent < -5 and volume > 1000000 and price > 5:
            return 'buy'   # 大跌有成交量,可能反弹
        elif change_percent > 3 and change_percent < 6 and volume > 500000:
            return 'buy'   # 温和上涨有成交量
        else:
            return 'hold'
    
    def calculate_confidence(self, stock):
        """计算置信度"""
        base_confidence = 0.5
        
        # 根据成交量调整
        if stock['volume'] > 2000000:
            base_confidence += 0.2
        elif stock['volume'] > 1000000:
            base_confidence += 0.1
            
        # 根据涨跌幅调整
        if abs(stock['change_percent']) > 5:
            base_confidence += 0.1
            
        # 添加随机因子
        base_confidence += random.uniform(-0.1, 0.1)
        
        return min(max(base_confidence, 0.1), 0.9)
    
    def generate_reason(self, stock, action):
        """生成决策原因"""
        change_percent = stock['change_percent']
        volume = stock['volume']
        
        if action == 'buy':
            if change_percent < 0:
                return f"大跌{abs(change_percent):.1f}%且成交量{volume//10000:.0f}万手,可能反弹"
            else:
                return f"温和上涨{change_percent:.1f}%且成交量{volume//10000:.0f}万手,趋势向好"
        elif action == 'sell':
            return f"高涨{change_percent:.1f}%且成交量{volume//10000:.0f}万手,可能见顶"
        else:
            return "观望"
    
    def data_collection_loop(self):
        """数据收集循环"""
        buffer = ""
        last_analysis_time = time.time()
        
        while self.running:
            try:
                data = self.socket.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    logger.warning("⚠️ 连接断开")
                    break
                
                buffer += data
                self.stats['received'] += 1
                
                # 处理完整的行
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    
                    if line:
                        stock_data = self.parse_stock_data(line)
                        if stock_data and stock_data['symbol']:
                            self.stock_pool[stock_data['symbol']] = stock_data
                            self.stats['processed'] += 1
                
                # 每30秒进行一次Agent分析
                current_time = time.time()
                if current_time - last_analysis_time >= 30:
                    self.perform_agent_analysis()
                    last_analysis_time = current_time
                
                # 每100条数据打印统计
                if self.stats['received'] % 100 == 0:
                    self.print_stats()
                    
            except Exception as e:
                logger.error(f"❌ 数据接收错误: {e}")
                break
    
    def perform_agent_analysis(self):
        """执行Agent分析"""
        if not self.stock_pool:
            return
            
        logger.info("🤖 开始Agent智能分析...")
        
        # 数据清洗
        cleaned_stocks = self.clean_stock_data(self.stock_pool)
        
        # Agent分析
        decisions = self.agent_analysis(cleaned_stocks)
        
        # 保存决策到Supabase
        saved_count = 0
        for decision in decisions:
            if self.save_decision_to_supabase(decision):
                saved_count += 1
        
        logger.info(f"✅ Agent分析完成,生成 {len(decisions)} 个决策,保存 {saved_count} 个到Supabase")
    
    def print_stats(self):
        """打印统计信息"""
        uptime = time.time() - self.stats['start_time']
        rate = self.stats['received'] / uptime if uptime > 0 else 0
        
        logger.info(f"📊 已处理 {self.stats['received']} 条数据,股票池: {len(self.stock_pool)} 只,"
                   f"决策: {self.stats['decisions']} 个,错误: {self.stats['errors']} 个,"
                   f"速率: {rate:.1f}/秒")
    
    def start(self):
        """启动云端Agent系统"""
        logger.info("🚀 启动云端Agent智能交易系统...")
        
        if not self.connect_to_chagubang():
            return False
        
        self.running = True
        
        # 启动数据收集线程
        collection_thread = threading.Thread(target=self.data_collection_loop)
        collection_thread.start()
        
        logger.info("✅ 云端Agent系统启动成功")
        logger.info("📡 开始接收茶股帮数据并进行智能分析...")
        
        try:
            # 主线程保持运行
            while self.running:
                time.sleep(60)  # 每分钟打印一次状态
                self.print_stats()
                
        except KeyboardInterrupt:
            logger.info("\n⏹️ 收到停止信号")
        finally:
            self.stop()
            collection_thread.join(timeout=10)
    
    def stop(self):
        """停止系统"""
        logger.info("⏹️ 停止云端Agent系统...")
        self.running = False
        
        if self.socket:
            self.socket.close()
        
        self.print_stats()
        logger.info("✅ 云端Agent系统已停止")

def main():
    """主函数"""
    # 从环境变量获取配置(Railway部署时使用)
    port = int(os.environ.get('PORT', 8080))
    
    # 启动HTTP服务器(Railway需要)
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'running',
                'service': '云端Agent智能交易系统',
                'timestamp': datetime.now().isoformat()
            }).encode())
    
    # 启动HTTP服务器
    def start_http_server():
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        logger.info(f"🌐 HTTP服务器启动在端口 {port}")
        server.serve_forever()
    
    http_thread = threading.Thread(target=start_http_server)
    http_thread.daemon = True
    http_thread.start()
    
    # 启动Agent系统
    agent = CloudAgentSystem()
    agent.start()

if __name__ == "__main__":
    main()
