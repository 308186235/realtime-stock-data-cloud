#!/usr/bin/env python3
"""
云端Agent智能交易系统 - 演示版
可以在任何云平台部署，模拟真实的Agent分析
"""

import os
import json
import time
import requests
import logging
from datetime import datetime
import threading
from typing import Dict, List
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supabase配置
SUPABASE_CONFIG = {
    'url': 'https://zzukfxwavknskqcepsjb.supabase.co',
    'anon_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw'
}

class CloudAgentDemo:
    def __init__(self):
        self.running = False
        self.stats = {
            'decisions': 0,
            'analysis_rounds': 0,
            'errors': 0,
            'start_time': time.time()
        }
        
    def generate_mock_stock_data(self):
        """生成模拟股票数据"""
        stocks = []
        stock_codes = [
            'SZ000001', 'SZ000002', 'SZ000858', 'SZ002415', 'SZ002594',
            'SH600000', 'SH600036', 'SH600519', 'SH600887', 'SH601318',
            'SZ300059', 'SZ300274', 'SZ300750', 'SZ300896', 'SZ301318'
        ]
        
        for code in stock_codes:
            stock = {
                'symbol': code,
                'name': f'股票{code[-3:]}',
                'price': round(random.uniform(5, 100), 2),
                'change_percent': round(random.uniform(-8, 8), 2),
                'volume': random.randint(100000, 5000000),
                'amount': round(random.uniform(1000000, 100000000), 2),
                'high': 0,
                'low': 0,
                'open': 0,
                'prev_close': 0
            }
            stocks.append(stock)
        
        return stocks
    
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
    
    def agent_analysis(self, stocks):
        """Agent智能分析"""
        decisions = []
        
        # 筛选异动股票
        abnormal_stocks = []
        for stock in stocks:
            if abs(stock['change_percent']) > 3 or stock['volume'] > 1000000:
                abnormal_stocks.append(stock)
        
        logger.info(f"🔍 发现 {len(abnormal_stocks)} 只异动股票")
        
        # 对异动股票进行分析
        for stock in abnormal_stocks:
            try:
                # Agent智能分析逻辑
                action = self.analyze_stock_action(stock)
                confidence = self.calculate_confidence(stock)
                reason = self.generate_reason(stock, action)
                
                if action != 'hold':  # 只保存非持有决策
                    decision = {
                        'symbol': stock['symbol'],
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
                logger.error(f"分析股票 {stock['symbol']} 失败: {e}")
        
        return decisions
    
    def analyze_stock_action(self, stock):
        """分析股票操作"""
        change_percent = stock['change_percent']
        volume = stock['volume']
        price = stock['price']
        
        # 智能分析逻辑
        if change_percent > 6 and volume > 2000000:
            return 'sell'  # 高涨幅高成交量，可能见顶
        elif change_percent < -4 and volume > 1000000 and price > 5:
            return 'buy'   # 大跌有成交量，可能反弹
        elif change_percent > 2 and change_percent < 5 and volume > 800000:
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
            base_confidence += 0.15
            
        # 添加随机因子
        base_confidence += random.uniform(-0.1, 0.1)
        
        return min(max(base_confidence, 0.1), 0.9)
    
    def generate_reason(self, stock, action):
        """生成决策原因"""
        change_percent = stock['change_percent']
        volume = stock['volume']
        
        if action == 'buy':
            if change_percent < 0:
                return f"大跌{abs(change_percent):.1f}%且成交量{volume//10000:.0f}万手，云端Agent判断可能反弹"
            else:
                return f"温和上涨{change_percent:.1f}%且成交量{volume//10000:.0f}万手，云端Agent判断趋势向好"
        elif action == 'sell':
            return f"高涨{change_percent:.1f}%且成交量{volume//10000:.0f}万手，云端Agent判断可能见顶"
        else:
            return "云端Agent建议观望"
    
    def perform_agent_analysis(self):
        """执行Agent分析"""
        logger.info("🤖 云端Agent开始智能分析...")
        
        # 生成模拟股票数据
        stocks = self.generate_mock_stock_data()
        
        # Agent分析
        decisions = self.agent_analysis(stocks)
        
        # 保存决策到Supabase
        saved_count = 0
        for decision in decisions:
            if self.save_decision_to_supabase(decision):
                saved_count += 1
        
        self.stats['analysis_rounds'] += 1
        
        logger.info(f"✅ 云端Agent分析完成，生成 {len(decisions)} 个决策，保存 {saved_count} 个到Supabase")
    
    def print_stats(self):
        """打印统计信息"""
        uptime = time.time() - self.stats['start_time']
        
        logger.info(f"📊 云端Agent运行状态: 分析轮次 {self.stats['analysis_rounds']}，"
                   f"决策总数 {self.stats['decisions']}，错误 {self.stats['errors']}，"
                   f"运行时间 {uptime:.0f}秒")
    
    def analysis_loop(self):
        """分析循环"""
        while self.running:
            try:
                self.perform_agent_analysis()
                time.sleep(60)  # 每分钟分析一次
            except Exception as e:
                logger.error(f"❌ 分析循环错误: {e}")
                time.sleep(30)
    
    def start(self):
        """启动云端Agent系统"""
        logger.info("🚀 启动云端Agent智能交易系统 (演示版)...")
        
        self.running = True
        
        # 启动分析线程
        analysis_thread = threading.Thread(target=self.analysis_loop)
        analysis_thread.start()
        
        logger.info("✅ 云端Agent系统启动成功")
        logger.info("📡 开始模拟股票数据分析...")
        
        try:
            # 主线程保持运行
            while self.running:
                time.sleep(60)  # 每分钟打印一次状态
                self.print_stats()
                
        except KeyboardInterrupt:
            logger.info("\n⏹️ 收到停止信号")
        finally:
            self.stop()
            analysis_thread.join(timeout=10)
    
    def stop(self):
        """停止系统"""
        logger.info("⏹️ 停止云端Agent系统...")
        self.running = False
        self.print_stats()
        logger.info("✅ 云端Agent系统已停止")

def main():
    """主函数"""
    # 从环境变量获取配置
    port = int(os.environ.get('PORT', 8080))
    
    # 启动HTTP服务器
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response_data = {
                'status': 'running',
                'service': '云端Agent智能交易系统 (演示版)',
                'description': '正在进行智能股票分析并生成交易决策',
                'features': [
                    '实时股票数据分析',
                    '智能交易决策生成',
                    '置信度计算',
                    '决策原因生成',
                    'Supabase数据存储'
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response_data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    # 启动HTTP服务器
    def start_http_server():
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        logger.info(f"🌐 HTTP服务器启动在端口 {port}")
        server.serve_forever()
    
    http_thread = threading.Thread(target=start_http_server)
    http_thread.daemon = True
    http_thread.start()
    
    # 启动Agent系统
    agent = CloudAgentDemo()
    agent.start()

if __name__ == "__main__":
    main()
