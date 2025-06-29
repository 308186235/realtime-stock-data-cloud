"""
简单HTTP测试服务器
使用Python内置的http.server模块
"""

import http.server
import socketserver
import json
import random
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# 端口设置
PORT = 9000

# 股票测试数据
stock_data = {
    "sh600000": {
        "code": "sh600000",
        "name": "浦发银行",
        "currentPrice": 10.56,
        "open": 10.33,
        "high": 10.86,
        "low": 10.21,
        "volume": 12345678,
        "turnoverRate": 2.45,
        "priceChange": 0.23,
        "priceChangePercent": 2.15
    },
    "sh601398": {
        "code": "sh601398",
        "name": "工商银行",
        "currentPrice": 5.67,
        "open": 5.79,
        "high": 5.82,
        "low": 5.65,
        "volume": 23456789,
        "turnoverRate": 1.82,
        "priceChange": -0.12,
        "priceChangePercent": -2.13
    }
}

# 处理请求的类
class TestHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        """处理OPTIONS请求,用于CORS"""
        self._set_headers()
    
    def do_GET(self):
        """处理GET请求"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        
        # 提取查询参数
        code = query.get('code', [''])[0]
        message = query.get('message', ['Hello'])[0]
        seconds = query.get('seconds', ['1'])[0]
        
        try:
            seconds = int(seconds)
        except ValueError:
            seconds = 1
        
        # 路由分发
        if path == '/api/health':
            self._handle_health()
        elif path == '/':
            self._handle_home()
        elif path == '/api/test':
            self._handle_test()
        elif path == '/api/test/ping':
            self._handle_ping()
        elif path == '/api/test/echo':
            self._handle_echo(message)
        elif path == '/api/test/delay':
            self._handle_delay(seconds)
        elif path == '/api/test/stock':
            self._handle_stock(code)
        elif path == '/api/stock/quote':
            self._handle_quote(code)
        elif path == '/api/t-trading/summary':
            self._handle_trading_summary()
        else:
            self._handle_not_found()
    
    def do_POST(self):
        """处理POST请求"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            data = {}
        
        path = self.path
        
        # 路由分发
        if path == '/api/test/echo':
            self._handle_echo_post(data)
        elif path == '/api/t-trading/evaluate-opportunity':
            self._handle_evaluate_opportunity(data)
        elif path == '/api/t-trading/record-trade':
            self._handle_record_trade(data)
        else:
            self._handle_not_found()
    
    def _handle_health(self):
        """处理健康检查请求"""
        self._set_headers()
        response = {
            "status": "healthy",
            "message": "交易系统运行正常",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def _handle_home(self):
        """处理首页请求"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        html = """<!DOCTYPE html>
<html><head><title>交易系统</title><meta charset="utf-8"></head>
<body><h1>🚀 交易系统运行中</h1><p>系统状态: <span style="color: green;">正常</span></p>
<p>时间: {}</p><h2>可用API:</h2><ul>
<li><a href="/api/health">/api/health</a> - 健康检查</li>
<li><a href="/api/test/ping">/api/test/ping</a> - Ping测试</li>
<li><a href="/api/stock/quote?code=000001">/api/stock/quote</a> - 股票报价</li>
<li><a href="/api/t-trading/summary">/api/t-trading/summary</a> - T+0交易摘要</li>
</ul></body></html>""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        self.wfile.write(html.encode('utf-8'))

    def _handle_test(self):
        """处理基础连接测试请求"""
        self._set_headers()
        response = {
            "status": "success",
            "message": "连接测试成功",
            "timestamp": time.time(),
            "server": "交易系统后端",
            "version": "1.0.0"
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def _handle_ping(self):
        """处理ping请求"""
        self._set_headers()
        response = {
            "message": "pong",
            "timestamp": time.time()
        }
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_echo(self, message):
        """处理echo GET请求"""
        self._set_headers()
        response = {
            "message": message,
            "timestamp": time.time()
        }
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_echo_post(self, data):
        """处理echo POST请求"""
        self._set_headers()
        response = {
            "data": data,
            "timestamp": time.time()
        }
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_delay(self, seconds):
        """处理延迟请求"""
        if seconds > 10:
            seconds = 10  # 限制最大延迟
        
        time.sleep(seconds)
        
        self._set_headers()
        response = {
            "message": f"Delayed response after {seconds} seconds",
            "timestamp": time.time()
        }
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_stock(self, code):
        """处理股票数据请求"""
        if not code or code not in stock_data:
            self._set_headers(404)
            response = {
                "error": f"股票代码 {code} 不存在",
                "timestamp": time.time()
            }
        else:
            self._set_headers()
            response = {
                "data": stock_data[code],
                "timestamp": time.time()
            }
        
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_quote(self, code):
        """处理股票行情请求"""
        if not code or code not in stock_data:
            self._set_headers(404)
            response = {
                "code": 404,
                "message": f"股票代码 {code} 不存在"
            }
        else:
            self._set_headers()
            response = {
                "code": 200,
                "data": stock_data[code]
            }
        
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_evaluate_opportunity(self, data):
        """处理交易机会评估请求"""
        if "code" not in data:
            self._set_headers(400)
            response = {
                "code": 400,
                "message": "缺少股票代码"
            }
        else:
            code = data.get("code")
            if code not in stock_data:
                # 如果股票代码不存在,使用请求数据创建临时数据
                stock_data[code] = {
                    "code": code,
                    "name": data.get("name", "未知股票"),
                    "currentPrice": data.get("current_price", 10.0),
                    "open": data.get("open_price", 9.8),
                    "high": data.get("intraday_high", 10.5),
                    "low": data.get("intraday_low", 9.5),
                    "volume": random.randint(1000000, 5000000),
                    "turnoverRate": random.uniform(1.0, 3.0),
                    "priceChange": random.uniform(-0.5, 0.5),
                    "priceChangePercent": random.uniform(-5, 5)
                }
            
            stock = stock_data[code]
            has_opportunity = stock["priceChangePercent"] > 0 or random.random() > 0.5
            
            self._set_headers()
            response = {
                "code": 200,
                "data": {
                    "has_opportunity": has_opportunity,
                    "mode": "positive" if has_opportunity else "negative",
                    "suggested_quantity": random.randint(100, 500) // 100 * 100,
                    "ai_confidence": random.uniform(0.6, 0.95),
                    "expected_cost_impact": {
                        "reduction_percentage": random.uniform(0.3, 1.2)
                    },
                    "message": "AI分析显示该股票当前走势强劲,建议买入" if has_opportunity else "AI分析显示该股票当前走势疲软,建议观望",
                    "evaluation_method": "ai",
                    "volatility": random.uniform(0.01, 0.05)
                }
            }
        
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_record_trade(self, data):
        """处理记录交易请求"""
        self._set_headers()
        response = {
            "code": 200,
            "data": {
                "trade_id": f"TR{int(time.time())}",
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "message": "交易记录成功"
            }
        }
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_trading_summary(self):
        """处理交易摘要请求"""
        self._set_headers()
        response = {
            "code": 200,
            "data": {
                "is_trading_day": True,
                "total_trades": random.randint(5, 20),
                "success_rate": random.uniform(0.6, 0.9),
                "total_profit": random.uniform(500, 2000),
                "active_positions": random.randint(1, 5)
            }
        }
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_not_found(self):
        """处理未找到的路由"""
        self._set_headers(404)
        response = {
            "error": "Not Found",
            "message": f"路径 {self.path} 不存在",
            "timestamp": time.time()
        }
        self.wfile.write(json.dumps(response).encode())

def run_server():
    """运行HTTP服务器"""
    handler = TestHandler

    try:
        # 允许地址重用
        socketserver.TCPServer.allow_reuse_address = True

        with socketserver.TCPServer(("localhost", PORT), handler) as httpd:
            print(f"服务器启动在 http://localhost:{PORT}")
            print("按 Ctrl+C 停止服务器")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 10013:
            print(f"端口 {PORT} 被占用或权限不足，尝试其他端口...")
            # 尝试其他端口
            for port in range(PORT + 1, PORT + 10):
                try:
                    with socketserver.TCPServer(("localhost", port), handler) as httpd:
                        print(f"服务器启动在 http://localhost:{port}")
                        print("按 Ctrl+C 停止服务器")
                        httpd.serve_forever()
                        break
                except OSError:
                    continue
            else:
                print("无法找到可用端口")
        else:
            print(f"启动服务器失败: {e}")
    except KeyboardInterrupt:
        print("\n服务器已关闭")

if __name__ == "__main__":
    run_server() 
 
