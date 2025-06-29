#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
域名访问服务器 - 支持 aigupiao.me
"""

import json
import socketserver
from http.server import BaseHTTPRequestHandler
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PORT = 8002
DOMAIN = "aigupiao.me"

class DomainAccessHTTPRequestHandler(BaseHTTPRequestHandler):
    """支持域名访问的HTTP请求处理器"""
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        host = self.headers.get('Host', 'unknown')
        user_agent = self.headers.get('User-Agent', '')
        is_mobile = any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone', 'ipad'])
        device_type = "📱 手机" if is_mobile else "💻 电脑"
        logger.info(f"{device_type} {host} - {format % args}")
    
    def _set_headers(self, content_type='application/json'):
        """设置响应头，支持域名访问"""
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        # 域名访问优化
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('X-Content-Type-Options', 'nosniff')
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
        
        # 路由分发
        if path == '/':
            self._handle_home()
        elif path == '/api/health':
            self._handle_health()
        elif path == '/test':
            self._handle_test()
        elif path == '/api/stock/quote':
            code = query.get('code', ['000001'])[0]
            self._handle_stock_quote(code)
        elif path == '/api/stats':
            self._handle_stats()
        elif path.startswith('/api/'):
            self._handle_api(path, query)
        else:
            self._handle_catch_all(path)
    
    def do_POST(self):
        """处理POST请求"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
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
        if path.startswith('/api/'):
            self._handle_api_post(path, data)
        else:
            self._handle_catch_all(path, 'POST')
    
    def _handle_home(self):
        """处理首页"""
        host = self.headers.get('Host', 'localhost')
        
        html = f"""<!DOCTYPE html>
<html><head><title>🚀 {DOMAIN} - 交易系统</title><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
.container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
.domain {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 10px 0; }}
.status {{ color: #28a745; font-weight: bold; }}
.api-list {{ list-style: none; padding: 0; }}
.api-list li {{ margin: 10px 0; padding: 10px; background: #e9ecef; border-radius: 5px; }}
.api-list a {{ text-decoration: none; color: #007bff; font-weight: bold; }}
</style></head>
<body>
<div class="container">
<h1>🚀 {DOMAIN} 交易系统</h1>
<div class="domain">
<h3>🌐 域名访问信息</h3>
<p>访问域名: <strong>{host}</strong></p>
<p>目标域名: <strong>{DOMAIN}</strong></p>
<p>服务端口: <strong>{PORT}</strong></p>
<p>访问方式: <strong>域名访问</strong></p>
</div>
<p>系统状态: <span class="status">正常运行</span></p>
<p>时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<h2>🔗 API端点测试</h2>
<ul class="api-list">
<li><a href="/api/health">/api/health</a> - 健康检查</li>
<li><a href="/test">/test</a> - 测试端点</li>
<li><a href="/api/stock/quote?code=000001">/api/stock/quote</a> - 股票报价</li>
<li><a href="/api/stats">/api/stats</a> - 系统统计</li>
</ul>

<div style="margin-top: 20px; padding: 15px; background: #d1ecf1; border-radius: 5px;">
<h4>📱 手机访问说明</h4>
<p>✅ 现在支持通过域名访问: <strong>https://{DOMAIN}</strong></p>
<p>✅ 手机和电脑都可以使用相同的域名</p>
<p>✅ 支持HTTPS安全访问</p>
</div>
</div>
</body></html>"""
        
        self._send_html_response(html)
    
    def _handle_health(self):
        """健康检查"""
        host = self.headers.get('Host', 'localhost')
        response = {
            "status": "healthy",
            "message": f"域名访问正常 - {DOMAIN}",
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0",
            "domain": DOMAIN,
            "host": host,
            "port": PORT,
            "domain_access": True,
            "mobile_support": True
        }
        self._send_json_response(response)
    
    def _handle_test(self):
        """处理测试请求"""
        host = self.headers.get('Host', 'localhost')
        response = {
            "status": "ok",
            "message": f"域名测试成功 - {DOMAIN}",
            "timestamp": datetime.now().isoformat(),
            "domain": DOMAIN,
            "host": host,
            "note": "域名访问正常工作"
        }
        self._send_json_response(response)
    
    def _handle_stock_quote(self, code):
        """股票报价模拟"""
        import random
        host = self.headers.get('Host', 'localhost')
        response = {
            "code": code,
            "name": f"股票{code}",
            "price": round(random.uniform(10, 100), 2),
            "change": round(random.uniform(-5, 5), 2),
            "timestamp": datetime.now().isoformat(),
            "domain": DOMAIN,
            "host": host,
            "access_method": "domain"
        }
        self._send_json_response(response)
    
    def _handle_stats(self):
        """系统统计"""
        host = self.headers.get('Host', 'localhost')
        response = {
            "domain": DOMAIN,
            "host": host,
            "port": PORT,
            "access_method": "domain",
            "timestamp": datetime.now().isoformat(),
            "message": "通过域名访问的系统统计"
        }
        self._send_json_response(response)
    
    def _handle_api(self, path, query):
        """处理API请求"""
        host = self.headers.get('Host', 'localhost')
        response = {
            "api": path,
            "method": "GET",
            "query": query,
            "domain": DOMAIN,
            "host": host,
            "timestamp": datetime.now().isoformat(),
            "message": "API通过域名访问正常"
        }
        self._send_json_response(response)
    
    def _handle_api_post(self, path, data):
        """处理API POST请求"""
        host = self.headers.get('Host', 'localhost')
        response = {
            "api": path,
            "method": "POST",
            "data": data,
            "domain": DOMAIN,
            "host": host,
            "timestamp": datetime.now().isoformat(),
            "message": "POST API通过域名访问正常"
        }
        self._send_json_response(response)
    
    def _handle_catch_all(self, path, method='GET'):
        """捕获所有其他请求"""
        host = self.headers.get('Host', 'localhost')
        response = {
            "path": path,
            "method": method,
            "domain": DOMAIN,
            "host": host,
            "timestamp": datetime.now().isoformat(),
            "message": f"请求已被域名服务器处理"
        }
        self._send_json_response(response)

def run_server():
    """启动服务器"""
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), DomainAccessHTTPRequestHandler) as httpd:
            logger.info("=" * 60)
            logger.info(f"🌐 域名访问服务器启动成功!")
            logger.info("=" * 60)
            logger.info(f"📍 本机访问: http://localhost:{PORT}")
            logger.info(f"🌐 域名访问: https://{DOMAIN}")
            logger.info(f"📱 手机访问: https://{DOMAIN} (通过域名)")
            logger.info(f"🔗 ngrok访问: https://5db1-116-169-10-245.ngrok-free.app")
            logger.info("=" * 60)
            logger.info("💡 域名访问说明:")
            logger.info(f"  1. 前端配置已更新为使用 https://{DOMAIN}")
            logger.info(f"  2. 手机可直接访问 https://{DOMAIN}")
            logger.info(f"  3. 支持HTTPS和跨域访问")
            logger.info("=" * 60)
            httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 服务器已停止")
    except Exception as e:
        logger.error(f"❌ 服务器错误: {e}")

if __name__ == "__main__":
    run_server()
