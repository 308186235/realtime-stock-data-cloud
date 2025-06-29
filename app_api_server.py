#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APP专用API服务器 - 支持手机APP连接
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

PORT = 8003
DOMAIN = "aigupiao.me"

class AppAPIRequestHandler(BaseHTTPRequestHandler):
    """APP专用API请求处理器"""
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        user_agent = self.headers.get('User-Agent', '')
        host = self.headers.get('Host', 'unknown')
        
        # 检测APP请求
        is_app = any(app in user_agent.lower() for app in ['uni-app', 'hbuilderx', 'plus', 'android', 'ios'])
        is_mobile = any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone', 'ipad'])
        
        if is_app:
            device_type = "📱 APP"
        elif is_mobile:
            device_type = "📱 手机"
        else:
            device_type = "💻 电脑"
            
        logger.info(f"{device_type} {host} - {format % args}")
    
    def _set_headers(self, content_type='application/json'):
        """设置响应头，专门优化APP访问"""
        self.send_response(200)
        self.send_header('Content-type', content_type)
        # APP专用CORS配置
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, X-Custom-Header')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        # APP优化头
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('X-API-Version', '1.0')
        self.send_header('X-Server-Type', 'APP-API')
        self.end_headers()
    
    def _send_json_response(self, data):
        """发送JSON响应"""
        self._set_headers()
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def _get_client_info(self):
        """获取客户端信息"""
        user_agent = self.headers.get('User-Agent', '')
        host = self.headers.get('Host', 'unknown')
        
        is_app = any(app in user_agent.lower() for app in ['uni-app', 'hbuilderx', 'plus'])
        is_mobile = any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone', 'ipad'])
        
        return {
            "host": host,
            "user_agent": user_agent,
            "is_app": is_app,
            "is_mobile": is_mobile,
            "device_type": "app" if is_app else ("mobile" if is_mobile else "desktop")
        }
    
    def do_OPTIONS(self):
        """处理OPTIONS预检请求"""
        self._set_headers()
    
    def do_GET(self):
        """处理GET请求"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        
        # APP API路由
        if path == '/api/health':
            self._handle_health()
        elif path == '/api/agent/status':
            self._handle_agent_status()
        elif path == '/api/agent/start':
            self._handle_agent_start()
        elif path == '/api/agent/stop':
            self._handle_agent_stop()
        elif path == '/api/trading/summary':
            self._handle_trading_summary()
        elif path == '/api/trading/balance':
            self._handle_trading_balance()
        elif path == '/api/stock/quote':
            code = query.get('code', ['000001'])[0]
            self._handle_stock_quote(code)
        elif path == '/api/stock/list':
            self._handle_stock_list()
        elif path == '/test':
            self._handle_test()
        elif path == '/':
            self._handle_app_home()
        else:
            self._handle_not_found(path)
    
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
        
        # APP API POST路由
        if path == '/api/trading/buy':
            self._handle_trading_buy(data)
        elif path == '/api/trading/sell':
            self._handle_trading_sell(data)
        elif path == '/api/agent/config':
            self._handle_agent_config(data)
        elif path == '/api/user/login':
            self._handle_user_login(data)
        else:
            self._handle_not_found(path, 'POST')
    
    def _handle_app_home(self):
        """APP首页信息"""
        client_info = self._get_client_info()
        
        response = {
            "app_name": "Agent智能分析控制台",
            "version": "1.0.0",
            "status": "running",
            "domain": DOMAIN,
            "client_info": client_info,
            "timestamp": datetime.now().isoformat(),
            "message": "APP API服务正常运行"
        }
        self._send_json_response(response)
    
    def _handle_health(self):
        """健康检查"""
        client_info = self._get_client_info()
        
        response = {
            "status": "healthy",
            "message": "APP API服务正常",
            "domain": DOMAIN,
            "port": PORT,
            "client_info": client_info,
            "timestamp": datetime.now().isoformat(),
            "api_version": "1.0",
            "app_support": True
        }
        self._send_json_response(response)
    
    def _handle_agent_status(self):
        """Agent状态"""
        client_info = self._get_client_info()
        
        response = {
            "agent_status": "running",
            "strategy": "趋势跟踪,量价分析",
            "runtime": "03:45:21",
            "trades_count": 12,
            "current_balance": 131.99,
            "profit_loss": "+5.67%",
            "last_update": datetime.now().isoformat(),
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_agent_start(self):
        """启动Agent"""
        client_info = self._get_client_info()
        
        response = {
            "status": "success",
            "message": "Agent已启动",
            "agent_id": "agent_001",
            "start_time": datetime.now().isoformat(),
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_agent_stop(self):
        """停止Agent"""
        client_info = self._get_client_info()
        
        response = {
            "status": "success",
            "message": "Agent已停止",
            "stop_time": datetime.now().isoformat(),
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_trading_summary(self):
        """交易摘要"""
        client_info = self._get_client_info()
        
        response = {
            "total_trades": 12,
            "successful_trades": 8,
            "failed_trades": 4,
            "success_rate": "66.7%",
            "total_profit": 131.99,
            "today_profit": 25.67,
            "account_balance": 10000.00,
            "available_funds": 8500.00,
            "timestamp": datetime.now().isoformat(),
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_trading_balance(self):
        """账户余额"""
        client_info = self._get_client_info()
        
        response = {
            "total_balance": 10000.00,
            "available_balance": 8500.00,
            "frozen_balance": 1500.00,
            "today_profit": 131.99,
            "total_profit": 567.89,
            "currency": "CNY",
            "timestamp": datetime.now().isoformat(),
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_stock_quote(self, code):
        """股票报价"""
        client_info = self._get_client_info()
        
        response = {
            "code": code,
            "name": f"股票{code}",
            "current_price": round(random.uniform(10, 100), 2),
            "change": round(random.uniform(-5, 5), 2),
            "change_percent": f"{round(random.uniform(-10, 10), 2)}%",
            "volume": random.randint(1000000, 10000000),
            "turnover": round(random.uniform(100000000, 1000000000), 2),
            "timestamp": datetime.now().isoformat(),
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_stock_list(self):
        """股票列表"""
        client_info = self._get_client_info()
        
        stocks = []
        for i in range(10):
            code = f"00000{i+1}"
            stocks.append({
                "code": code,
                "name": f"股票{code}",
                "price": round(random.uniform(10, 100), 2),
                "change": round(random.uniform(-5, 5), 2)
            })
        
        response = {
            "stocks": stocks,
            "total": len(stocks),
            "timestamp": datetime.now().isoformat(),
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_trading_buy(self, data):
        """买入交易"""
        client_info = self._get_client_info()
        
        response = {
            "status": "success",
            "message": "买入订单已提交",
            "order_id": f"BUY_{int(datetime.now().timestamp())}",
            "stock_code": data.get("stock_code", "000001"),
            "quantity": data.get("quantity", 100),
            "price": data.get("price", 50.00),
            "timestamp": datetime.now().isoformat(),
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_trading_sell(self, data):
        """卖出交易"""
        client_info = self._get_client_info()
        
        response = {
            "status": "success",
            "message": "卖出订单已提交",
            "order_id": f"SELL_{int(datetime.now().timestamp())}",
            "stock_code": data.get("stock_code", "000001"),
            "quantity": data.get("quantity", 100),
            "price": data.get("price", 50.00),
            "timestamp": datetime.now().isoformat(),
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_agent_config(self, data):
        """Agent配置"""
        client_info = self._get_client_info()
        
        response = {
            "status": "success",
            "message": "Agent配置已更新",
            "config": data,
            "timestamp": datetime.now().isoformat(),
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_user_login(self, data):
        """用户登录"""
        client_info = self._get_client_info()
        
        response = {
            "status": "success",
            "message": "登录成功",
            "token": "app_token_123456",
            "user_id": "user_001",
            "username": data.get("username", "demo_user"),
            "timestamp": datetime.now().isoformat(),
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_test(self):
        """测试端点"""
        client_info = self._get_client_info()
        
        response = {
            "status": "ok",
            "message": "APP API测试成功",
            "domain": DOMAIN,
            "timestamp": datetime.now().isoformat(),
            "client_info": client_info
        }
        self._send_json_response(response)
    
    def _handle_not_found(self, path, method='GET'):
        """处理未找到的路径"""
        client_info = self._get_client_info()
        
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "error",
            "message": f"API端点未找到: {method} {path}",
            "code": 404,
            "timestamp": datetime.now().isoformat(),
            "client_info": client_info
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

def run_server():
    """启动APP API服务器"""
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), AppAPIRequestHandler) as httpd:
            logger.info("=" * 60)
            logger.info("📱 APP专用API服务器启动成功!")
            logger.info("=" * 60)
            logger.info(f"📍 本机访问: http://localhost:{PORT}")
            logger.info(f"🌐 域名访问: https://{DOMAIN}")
            logger.info(f"📱 APP访问: https://{DOMAIN} (专用API)")
            logger.info("=" * 60)
            logger.info("📋 APP API端点:")
            logger.info("  /api/health - 健康检查")
            logger.info("  /api/agent/status - Agent状态")
            logger.info("  /api/agent/start - 启动Agent")
            logger.info("  /api/agent/stop - 停止Agent")
            logger.info("  /api/trading/summary - 交易摘要")
            logger.info("  /api/trading/balance - 账户余额")
            logger.info("  /api/stock/quote - 股票报价")
            logger.info("  /api/trading/buy - 买入交易")
            logger.info("  /api/trading/sell - 卖出交易")
            logger.info("=" * 60)
            logger.info("✅ 专门优化APP连接和响应")
            logger.info("📊 实时监控APP请求")
            httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 APP API服务器已停止")
    except Exception as e:
        logger.error(f"❌ 服务器错误: {e}")

if __name__ == "__main__":
    run_server()
