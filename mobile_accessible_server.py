#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
支持手机访问的后端服务器
"""

import json
import time
import socket
import socketserver
from http.server import BaseHTTPRequestHandler
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import threading
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PORT = 8002

def get_local_ip():
    """获取本机IP地址"""
    try:
        # 连接到一个远程地址来获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

class RequestStats:
    """请求统计"""
    def __init__(self):
        self.stats = {}
        self.mobile_requests = 0
        self.lock = threading.Lock()
    
    def record(self, path, method, user_agent=""):
        with self.lock:
            key = f"{method} {path}"
            self.stats[key] = self.stats.get(key, 0) + 1
            
            # 检测移动设备
            if any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone', 'ipad']):
                self.mobile_requests += 1
    
    def get_stats(self):
        with self.lock:
            return dict(self.stats), self.mobile_requests

# 全局统计对象
request_stats = RequestStats()

class MobileAccessibleHTTPRequestHandler(BaseHTTPRequestHandler):
    """支持手机访问的HTTP请求处理器"""
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        user_agent = self.headers.get('User-Agent', '')
        client_ip = self.client_address[0]
        is_mobile = any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone', 'ipad'])
        device_type = "📱 手机" if is_mobile else "💻 电脑"
        logger.info(f"{device_type} {client_ip} - {format % args}")
    
    def _set_headers(self, content_type='application/json'):
        """设置响应头，支持跨域和移动设备"""
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        # 移动设备优化
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
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
    
    def _get_client_info(self):
        """获取客户端信息"""
        user_agent = self.headers.get('User-Agent', '')
        client_ip = self.client_address[0]
        is_mobile = any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone', 'ipad'])
        
        return {
            "ip": client_ip,
            "user_agent": user_agent,
            "is_mobile": is_mobile,
            "device_type": "mobile" if is_mobile else "desktop"
        }
    
    def do_OPTIONS(self):
        """处理OPTIONS请求"""
        self._set_headers()
    
    def do_GET(self):
        """处理GET请求"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        
        # 记录统计
        user_agent = self.headers.get('User-Agent', '')
        request_stats.record(path, 'GET', user_agent)
        
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
        elif path == '/api/mobile/info':
            self._handle_mobile_info()
        else:
            self._handle_catch_all(path)
    
    def do_POST(self):
        """处理POST请求"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # 记录统计
        user_agent = self.headers.get('User-Agent', '')
        request_stats.record(path, 'POST', user_agent)
        
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
        client_info = self._get_client_info()
        stats, mobile_requests = request_stats.get_stats()
        total_requests = sum(stats.values())
        
        device_icon = "📱" if client_info["is_mobile"] else "💻"
        device_name = "手机" if client_info["is_mobile"] else "电脑"
        
        html = f"""<!DOCTYPE html>
<html><head><title>🚀 交易系统 - 移动支持</title><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
.container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
.status {{ color: #28a745; font-weight: bold; }}
.mobile {{ background: #e7f3ff; padding: 10px; border-radius: 5px; margin: 10px 0; }}
.stats {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
.api-list {{ list-style: none; padding: 0; }}
.api-list li {{ margin: 10px 0; padding: 10px; background: #e9ecef; border-radius: 5px; }}
.api-list a {{ text-decoration: none; color: #007bff; font-weight: bold; }}
</style></head>
<body>
<div class="container">
<h1>🚀 交易系统 - 移动支持版</h1>
<div class="mobile">
<h3>{device_icon} 设备信息</h3>
<p>设备类型: {device_name}</p>
<p>客户端IP: {client_info["ip"]}</p>
<p>服务器IP: {LOCAL_IP}:{PORT}</p>
</div>
<p>系统状态: <span class="status">正常运行</span></p>
<p>时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<div class="stats">
<h3>📊 访问统计</h3>
<p>总请求数: <strong>{total_requests}</strong></p>
<p>手机访问: <strong>{mobile_requests}</strong></p>
</div>

<h2>🔗 API测试 (支持手机)</h2>
<ul class="api-list">
<li><a href="/api/health">/api/health</a> - 健康检查</li>
<li><a href="/test">/test</a> - 测试端点</li>
<li><a href="/api/mobile/info">/api/mobile/info</a> - 移动设备信息</li>
<li><a href="/api/stats">/api/stats</a> - 请求统计</li>
<li><a href="/api/test/ping">/api/test/ping</a> - Ping测试</li>
<li><a href="/api/stock/quote?code=000001">/api/stock/quote</a> - 股票报价</li>
</ul>

<div style="margin-top: 20px; padding: 15px; background: #d1ecf1; border-radius: 5px;">
<h4>📱 手机访问说明</h4>
<p>1. 确保手机和电脑在同一WiFi网络</p>
<p>2. 手机浏览器访问: <strong>http://{LOCAL_IP}:{PORT}</strong></p>
<p>3. 或扫描二维码访问</p>
</div>
</div>
</body></html>"""
        
        self._send_html_response(html)
    
    def _handle_health(self):
        """健康检查"""
        client_info = self._get_client_info()
        response = {
            "status": "healthy",
            "message": "交易系统运行正常 - 支持移动设备",
            "timestamp": datetime.now().isoformat(),
            "version": "2.1.0",
            "server_ip": LOCAL_IP,
            "port": PORT,
            "client_info": client_info,
            "mobile_optimized": True
        }
        self._send_json_response(response)
    
    def _handle_mobile_info(self):
        """移动设备信息"""
        client_info = self._get_client_info()
        stats, mobile_requests = request_stats.get_stats()
        
        response = {
            "client_info": client_info,
            "server_info": {
                "ip": LOCAL_IP,
                "port": PORT,
                "mobile_requests": mobile_requests,
                "total_requests": sum(stats.values())
            },
            "network_info": {
                "access_url": f"http://{LOCAL_IP}:{PORT}",
                "mobile_optimized": True
            },
            "timestamp": datetime.now().isoformat()
        }
        self._send_json_response(response)
    
    def _handle_test(self):
        """处理测试请求"""
        client_info = self._get_client_info()
        response = {
            "status": "ok",
            "message": "测试端点正常 - 移动设备支持",
            "timestamp": datetime.now().isoformat(),
            "client_info": client_info,
            "note": "此端点支持手机访问"
        }
        self._send_json_response(response)
    
    def _handle_stats(self):
        """请求统计"""
        stats, mobile_requests = request_stats.get_stats()
        response = {
            "total_requests": sum(stats.values()),
            "mobile_requests": mobile_requests,
            "desktop_requests": sum(stats.values()) - mobile_requests,
            "request_breakdown": stats,
            "server_info": {
                "ip": LOCAL_IP,
                "port": PORT
            },
            "timestamp": datetime.now().isoformat()
        }
        self._send_json_response(response)
    
    def _handle_ping(self):
        """Ping测试"""
        client_info = self._get_client_info()
        response = {
            "message": "pong",
            "timestamp": datetime.now().isoformat(),
            "server": "mobile_accessible_server",
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_echo(self, message):
        """Echo测试"""
        client_info = self._get_client_info()
        response = {
            "echo": message,
            "timestamp": datetime.now().isoformat(),
            "method": "GET",
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_echo_post(self, data):
        """Echo POST测试"""
        client_info = self._get_client_info()
        response = {
            "echo": data,
            "timestamp": datetime.now().isoformat(),
            "method": "POST",
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_stock_quote(self, code):
        """股票报价模拟"""
        import random
        client_info = self._get_client_info()
        response = {
            "error": "REAL_DATA_REQUIRED",
            "message": "❌ 系统禁止返回模拟股票数据",
            "code": code,
            "required_action": "请配置真实数据源",
            "timestamp": datetime.now().isoformat(),
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_trading_summary(self):
        """T+0交易摘要"""
        client_info = self._get_client_info()
        response = {
            "summary": "T+0交易摘要",
            "total_trades": 0,
            "profit_loss": 0.0,
            "timestamp": datetime.now().isoformat(),
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_trade_buy(self, data):
        """买入交易"""
        client_info = self._get_client_info()
        response = {
            "error": "REAL_TRADING_REQUIRED",
            "message": "❌ 系统禁止模拟交易操作",
            "action": "buy",
            "data": data,
            "required_action": "请配置真实交易接口",
            "timestamp": datetime.now().isoformat(),
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_trade_sell(self, data):
        """卖出交易"""
        client_info = self._get_client_info()
        response = {
            "error": "REAL_TRADING_REQUIRED",
            "message": "❌ 系统禁止模拟交易操作",
            "action": "sell",
            "data": data,
            "required_action": "请配置真实交易接口",
            "timestamp": datetime.now().isoformat(),
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_catch_all(self, path, method='GET'):
        """捕获所有其他请求"""
        client_info = self._get_client_info()
        response = {
            "message": f"端点 {method} {path} 已被捕获",
            "status": "handled",
            "timestamp": datetime.now().isoformat(),
            "client_info": client_info,
            "note": "此请求已被移动支持服务器处理"
        }
        self._send_json_response(response)

def run_server():
    """启动服务器"""
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), MobileAccessibleHTTPRequestHandler) as httpd:
            logger.info("=" * 60)
            logger.info("🚀 移动支持服务器启动成功!")
            logger.info("=" * 60)
            logger.info(f"📍 本机访问: http://localhost:{PORT}")
            logger.info(f"📱 手机访问: http://{LOCAL_IP}:{PORT}")
            logger.info(f"🌐 局域网IP: {LOCAL_IP}")
            logger.info("=" * 60)
            logger.info("💡 手机访问步骤:")
            logger.info("  1. 确保手机和电脑在同一WiFi网络")
            logger.info(f"  2. 手机浏览器打开: http://{LOCAL_IP}:{PORT}")
            logger.info("  3. 测试API功能")
            logger.info("=" * 60)
            logger.info("✅ 服务器支持跨域访问和移动设备")
            logger.info("📊 实时监控移动设备访问")
            httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 服务器已停止")
    except Exception as e:
        logger.error(f"❌ 服务器错误: {e}")

if __name__ == "__main__":
    run_server()
