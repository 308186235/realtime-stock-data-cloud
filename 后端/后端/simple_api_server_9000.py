#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的API服务器 - 运行在9000端口,支持Cloudflare Tunnel
"""

import json
import socketserver
from http.server import BaseHTTPRequestHandler
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import logging
import random

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PORT = 9000
DOMAIN = "aigupiao.me"

class SimpleAPIRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            query_params = parse_qs(parsed_path.query)
            
            logger.info(f"GET {path} from {self.client_address[0]}")
            
            # 设置CORS头
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            # 路由处理
            if path == '/':
                response = {
                    "message": "AI股票交易系统API",
                    "status": "running",
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0.0",
                    "domain": DOMAIN,
                    "port": PORT
                }
            elif path == '/api/health':
                response = {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "service": "ai-stock-trading-api",
                    "domain": DOMAIN
                }
            elif path == '/api/agent/status':
                response = {
                    "agent_status": "running",
                    "learning_progress": None  # 需要真实数据,
                    "active_strategies": 3,
                    "last_update": datetime.now().isoformat(),
                    "performance": {
                        "win_rate": None  # 需要真实数据,
                        "total_trades": None  # 需要真实数据,
                        "profit_rate": None  # 需要真实数据
                    }
                }
            elif path == '/api/trading/summary':
                response = {
                    "total_balance": round(random.uniform(100000, 500000), 2),
                    "available_cash": round(random.uniform(20000, 100000), 2),
                    "market_value": round(random.uniform(80000, 400000), 2),
                    "today_profit": round(random.uniform(-5000, 8000), 2),
                    "total_profit": round(random.uniform(-10000, 50000), 2),
                    "positions": random.randint(3, 8),
                    "timestamp": datetime.now().isoformat()
                }
            elif path == '/api/stock/quote':
                # 获取股票代码参数
                symbol = query_params.get('symbol', ['000001'])[0]
                response = {
                    "symbol": symbol,
                    "name": "平安银行" if symbol == "000001" else f"股票{symbol}",
                    "price": None  # 需要真实数据,
                    "change": None  # 需要真实数据,
                    "change_percent": round(random.uniform(-5, 8), 2),
                    "volume": None  # 需要真实数据,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                response = {
                    "error": "API endpoint not found",
                    "path": path,
                    "available_endpoints": [
                        "/",
                        "/api/health",
                        "/api/agent/status",
                        "/api/trading/summary",
                        "/api/stock/quote?symbol=000001"
                    ]
                }
            
            # 发送响应
            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"GET请求处理错误: {e}")
            self.send_error(500, f"Internal Server Error: {e}")
    
    def do_POST(self):
        """处理POST请求"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            logger.info(f"POST {path} from {self.client_address[0]}")
            
            # 设置CORS头
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            # 解析POST数据
            try:
                request_data = json.loads(post_data.decode('utf-8')) if post_data else {}
            except:
                request_data = {}
            
            # 路由处理
            if path == '/api/agent/start':
                response = {
                    "status": "success",
                    "message": "Agent已启动",
                    "agent_id": f"agent_{random.randint(1000, 9999)}",
                    "timestamp": datetime.now().isoformat()
                }
            elif path == '/api/agent/stop':
                response = {
                    "status": "success",
                    "message": "Agent已停止",
                    "timestamp": datetime.now().isoformat()
                }
            elif path == '/api/trading/buy':
                symbol = request_data.get('symbol', '000001')
                quantity = request_data.get('quantity', 100)
                response = {
                    "status": "success",
                    "message": f"买入订单已提交",
                    "order_id": f"order_{random.randint(10000, 99999)}",
                    "symbol": symbol,
                    "quantity": quantity,
                    "price": None  # 需要真实数据,
                    "timestamp": datetime.now().isoformat()
                }
            elif path == '/api/trading/sell':
                symbol = request_data.get('symbol', '000001')
                quantity = request_data.get('quantity', 100)
                response = {
                    "status": "success",
                    "message": f"卖出订单已提交",
                    "order_id": f"order_{random.randint(10000, 99999)}",
                    "symbol": symbol,
                    "quantity": quantity,
                    "price": None  # 需要真实数据,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                response = {
                    "error": "API endpoint not found",
                    "path": path,
                    "method": "POST"
                }
            
            # 发送响应
            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"POST请求处理错误: {e}")
            self.send_error(500, f"Internal Server Error: {e}")
    
    def do_OPTIONS(self):
        """处理OPTIONS请求(CORS预检)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def log_message(self, format, *args):
        """重写日志方法,避免重复日志"""
        pass

def run_server():
    """启动API服务器"""
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), SimpleAPIRequestHandler) as httpd:
            logger.info("=" * 60)
            logger.info("🚀 AI股票交易API服务器启动成功!")
            logger.info("=" * 60)
            logger.info(f"📍 本机访问: http://localhost:{PORT}")
            logger.info(f"🌐 域名访问: https://{DOMAIN}")
            logger.info(f"📱 手机访问: https://{DOMAIN} (通过Cloudflare Tunnel)")
            logger.info("=" * 60)
            logger.info("📋 API端点:")
            logger.info("  GET  / - 服务器信息")
            logger.info("  GET  /api/health - 健康检查")
            logger.info("  GET  /api/agent/status - Agent状态")
            logger.info("  POST /api/agent/start - 启动Agent")
            logger.info("  POST /api/agent/stop - 停止Agent")
            logger.info("  GET  /api/trading/summary - 交易摘要")
            logger.info("  GET  /api/stock/quote?symbol=000001 - 股票报价")
            logger.info("  POST /api/trading/buy - 买入交易")
            logger.info("  POST /api/trading/sell - 卖出交易")
            logger.info("=" * 60)
            logger.info("💡 Cloudflare Tunnel已配置,外网可通过域名访问")
            logger.info("🔄 所有请求支持CORS跨域访问")
            logger.info("=" * 60)
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        logger.info("🛑 API服务器已停止")
    except Exception as e:
        logger.error(f"❌ API服务器错误: {e}")

if __name__ == "__main__":
    run_server()
