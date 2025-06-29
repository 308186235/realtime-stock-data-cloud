#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP优化的强健服务器 - 处理所有请求类型
"""

import json
import time
import socketserver
from http.server import BaseHTTPRequestHandler
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import threading
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PORT = 8002  # 使用新端口避免冲突

class RequestStats:
    """请求统计"""
    def __init__(self):
        self.stats = {}
        self.lock = threading.Lock()
    
    def record(self, path, method):
        with self.lock:
            key = f"{method} {path}"
            self.stats[key] = self.stats.get(key, 0) + 1
    
    def get_stats(self):
        with self.lock:
            return dict(self.stats)

# 全局统计对象
request_stats = RequestStats()

class RobustHTTPRequestHandler(BaseHTTPRequestHandler):
    """强健的HTTP请求处理器"""
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        logger.info(f"{self.address_string()} - {format % args}")
    
    def _set_headers(self, content_type='application/json'):
        """设置响应头"""
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()
    
    def _send_json_response(self, data):
        """发送JSON响应"""
        self._set_headers()
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def _send_html_response(self, html):
        """发送HTML响应"""
        self._set_headers('text/html; charset=utf-8')
        self.wfile.write(html.encode('utf-8'))
    
    def do_OPTIONS(self):
        """处理OPTIONS请求"""
        self._set_headers()
    
    def do_GET(self):
        """处理GET请求"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        
        # 记录统计
        request_stats.record(path, 'GET')
        
        # 路由分发
        if path == '/':
            self._handle_home()
        elif path == '/api/health':
            self._handle_health()
        elif path == '/test':
            self._handle_test()
        elif path == '/api/stats':
            self._handle_stats()
        elif path == '/api/test/ping':
            self._handle_ping()
        elif path == '/api/test/echo':
            message = query.get('message', ['Hello'])[0]
            self._handle_echo(message)
        elif path == '/api/stock/quote':
            code = query.get('code', ['000001'])[0]
            self._handle_stock_quote(code)
        elif path == '/api/t-trading/summary':
            self._handle_trading_summary()
        else:
            self._handle_catch_all(path)
    
    def do_POST(self):
        """处理POST请求"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # 记录统计
        request_stats.record(path, 'POST')
        
        # 读取POST数据
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}
        
        # 路由分发
        if path == '/api/test/echo':
            self._handle_echo_post(data)
        elif path == '/api/trade/buy':
            self._handle_trade_buy(data)
        elif path == '/api/trade/sell':
            self._handle_trade_sell(data)
        else:
            self._handle_catch_all(path, 'POST')
    
    def _handle_home(self):
        """处理首页"""
        stats = request_stats.get_stats()
        total_requests = sum(stats.values())
        
        html = f"""<!DOCTYPE html>
<html><head><title>🚀 强健交易系统</title><meta charset="utf-8">
<style>
body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
.container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
.status {{ color: #28a745; font-weight: bold; }}
.stats {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
.api-list {{ list-style: none; padding: 0; }}
.api-list li {{ margin: 10px 0; padding: 10px; background: #e9ecef; border-radius: 5px; }}
.api-list a {{ text-decoration: none; color: #007bff; font-weight: bold; }}
.api-list a:hover {{ color: #0056b3; }}
</style></head>
<body>
<div class="container">
<h1>🚀 强健交易系统</h1>
<p>系统状态: <span class="status">正常运行</span></p>
<p>时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<p>端口: {PORT}</p>

<div class="stats">
<h3>📊 请求统计</h3>
<p>总请求数: <strong>{total_requests}</strong></p>
<details>
<summary>详细统计</summary>
<ul>
{''.join([f'<li>{k}: {v}</li>' for k, v in sorted(stats.items(), key=lambda x: x[1], reverse=True)])}
</ul>
</details>
</div>

<h2>🔗 可用API</h2>
<ul class="api-list">
<li><a href="/api/health">/api/health</a> - 健康检查</li>
<li><a href="/test">/test</a> - 测试端点</li>
<li><a href="/api/stats">/api/stats</a> - 请求统计</li>
<li><a href="/api/test/ping">/api/test/ping</a> - Ping测试</li>
<li><a href="/api/test/echo?message=Hello">/api/test/echo</a> - Echo测试</li>
<li><a href="/api/stock/quote?code=000001">/api/stock/quote</a> - 股票报价</li>
<li><a href="/api/t-trading/summary">/api/t-trading/summary</a> - T+0交易摘要</li>
</ul>
</div>
</body></html>"""
        
        self._send_html_response(html)
    
    def _handle_health(self):
        """健康检查"""
        response = {
            "status": "healthy",
            "message": "强健交易系统运行正常",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "port": PORT,
            "total_requests": sum(request_stats.get_stats().values())
        }
        self._send_json_response(response)
    
    def _handle_test(self):
        """处理测试请求 - 解决垃圾请求问题"""
        response = {
            "status": "ok",
            "message": "测试端点正常 - MCP修复成功",
            "timestamp": datetime.now().isoformat(),
            "note": "此端点已通过MCP自动修复"
        }
        self._send_json_response(response)
    
    def _handle_stats(self):
        """请求统计"""
        stats = request_stats.get_stats()
        response = {
            "total_requests": sum(stats.values()),
            "request_breakdown": stats,
            "timestamp": datetime.now().isoformat()
        }
        self._send_json_response(response)
    
    def _handle_ping(self):
        """Ping测试"""
        response = {
            "message": "pong",
            "timestamp": datetime.now().isoformat(),
            "server": "robust_server"
        }
        self._send_json_response(response)
    
    def _handle_echo(self, message):
        """Echo测试"""
        response = {
            "echo": message,
            "timestamp": datetime.now().isoformat(),
            "method": "GET"
        }
        self._send_json_response(response)
    
    def _handle_echo_post(self, data):
        """Echo POST测试"""
        response = {
            "echo": data,
            "timestamp": datetime.now().isoformat(),
            "method": "POST"
        }
        self._send_json_response(response)
    
    def _handle_stock_quote(self, code):
        """股票报价模拟"""
        import random
        response = {
            "code": code,
            "name": f"股票{code}",
            "price": round(random.uniform(10, 100), 2),
            "change": round(random.uniform(-5, 5), 2),
            "timestamp": datetime.now().isoformat()
        }
        self._send_json_response(response)
    
    def _handle_trading_summary(self):
        """T+0交易摘要"""
        response = {
            "summary": "T+0交易摘要",
            "total_trades": 0,
            "profit_loss": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        self._send_json_response(response)
    
    def _handle_trade_buy(self, data):
        """买入交易"""
        response = {
            "action": "buy",
            "data": data,
            "status": "simulated",
            "timestamp": datetime.now().isoformat()
        }
        self._send_json_response(response)
    
    def _handle_trade_sell(self, data):
        """卖出交易"""
        response = {
            "action": "sell",
            "data": data,
            "status": "simulated",
            "timestamp": datetime.now().isoformat()
        }
        self._send_json_response(response)
    
    def _handle_catch_all(self, path, method='GET'):
        """捕获所有其他请求"""
        response = {
            "message": f"端点 {method} {path} 已被捕获",
            "status": "handled",
            "timestamp": datetime.now().isoformat(),
            "note": "此请求已被强健服务器处理"
        }
        self._send_json_response(response)

def run_server():
    """启动服务器"""
    try:
        with socketserver.TCPServer(("", PORT), RobustHTTPRequestHandler) as httpd:
            logger.info(f"🚀 强健服务器启动在 http://localhost:{PORT}")
            logger.info("✅ 所有请求都将被正确处理")
            logger.info("📊 访问 /api/stats 查看请求统计")
            httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 服务器已停止")
    except Exception as e:
        logger.error(f"❌ 服务器错误: {e}")

if __name__ == "__main__":
    run_server()
