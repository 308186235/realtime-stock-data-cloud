#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端口代理服务器 - 将80端口请求转发到8003端口
解决域名访问问题
"""

import http.server
import socketserver
import urllib.request
import urllib.parse
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置
PROXY_PORT = 8082        # 代理服务器端口 (可用端口)
TARGET_PORT = 8003       # 目标API服务器端口
TARGET_HOST = "localhost"

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    """代理请求处理器"""
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        user_agent = self.headers.get('User-Agent', '')
        host = self.headers.get('Host', 'unknown')
        
        # 检测设备类型
        is_app = any(app in user_agent.lower() for app in ['uni-app', 'hbuilderx', 'plus', 'android', 'ios'])
        is_mobile = any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone', 'ipad'])
        
        if is_app:
            device_type = "📱 APP"
        elif is_mobile:
            device_type = "📱 手机"
        else:
            device_type = "💻 电脑"
            
        logger.info(f"🔄 代理 {device_type} {host} - {format % args}")
    
    def _proxy_request(self, method='GET', data=None):
        """代理请求到目标服务器"""
        target_url = f"http://{TARGET_HOST}:{TARGET_PORT}{self.path}"
        
        try:
            # 准备请求
            headers = {}
            for key, value in self.headers.items():
                if key.lower() not in ['host', 'connection']:
                    headers[key] = value
            
            # 创建请求
            if data:
                req = urllib.request.Request(target_url, data=data, headers=headers, method=method)
            else:
                req = urllib.request.Request(target_url, headers=headers, method=method)
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=30) as response:
                # 获取响应数据
                response_data = response.read()
                
                # 设置响应头
                self.send_response(response.getcode())
                
                # 复制响应头
                for key, value in response.headers.items():
                    if key.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(key, value)
                
                # 添加CORS头
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
                
                self.end_headers()
                
                # 发送响应数据
                self.wfile.write(response_data)
                
                logger.info(f"✅ 代理成功: {method} {self.path} -> {response.getcode()}")
                
        except urllib.error.HTTPError as e:
            logger.error(f"❌ HTTP错误: {method} {self.path} -> {e.code} {e.reason}")
            self.send_error(e.code, e.reason)
            
        except urllib.error.URLError as e:
            logger.error(f"❌ 连接错误: {method} {self.path} -> {e.reason}")
            self._send_error_response(502, f"无法连接到API服务器: {e.reason}")
            
        except Exception as e:
            logger.error(f"❌ 代理错误: {method} {self.path} -> {e}")
            self._send_error_response(500, f"代理服务器内部错误: {e}")
    
    def _send_error_response(self, code, message):
        """发送错误响应"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = {
            "status": "error",
            "code": code,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "proxy_info": {
                "proxy_port": PROXY_PORT,
                "target_port": TARGET_PORT,
                "target_host": TARGET_HOST
            }
        }
        
        self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_GET(self):
        """处理GET请求"""
        self._proxy_request('GET')
    
    def do_POST(self):
        """处理POST请求"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else None
        self._proxy_request('POST', post_data)
    
    def do_PUT(self):
        """处理PUT请求"""
        content_length = int(self.headers.get('Content-Length', 0))
        put_data = self.rfile.read(content_length) if content_length > 0 else None
        self._proxy_request('PUT', put_data)
    
    def do_DELETE(self):
        """处理DELETE请求"""
        self._proxy_request('DELETE')
    
    def do_OPTIONS(self):
        """处理OPTIONS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()

def check_target_server():
    """检查目标服务器是否运行"""
    try:
        test_url = f"http://{TARGET_HOST}:{TARGET_PORT}/api/health"
        with urllib.request.urlopen(test_url, timeout=5) as response:
            if response.getcode() == 200:
                logger.info(f"✅ 目标API服务器运行正常: {TARGET_HOST}:{TARGET_PORT}")
                return True
    except Exception as e:
        logger.error(f"❌ 目标API服务器不可用: {TARGET_HOST}:{TARGET_PORT} - {e}")
        return False
    
    return False

def run_proxy():
    """启动代理服务器"""
    # 检查目标服务器
    if not check_target_server():
        logger.error("⚠️  目标API服务器不可用,但代理服务器仍将启动")
        logger.info("💡 请确保API服务器在8003端口运行")
    
    try:
        with socketserver.TCPServer(("0.0.0.0", PROXY_PORT), ProxyHandler) as httpd:
            logger.info("=" * 60)
            logger.info("🔄 端口代理服务器启动成功!")
            logger.info("=" * 60)
            logger.info(f"📍 代理端口: {PROXY_PORT} (HTTP标准端口)")
            logger.info(f"🎯 目标服务器: {TARGET_HOST}:{TARGET_PORT}")
            logger.info(f"🌐 域名访问: https://aigupiao.me")
            logger.info(f"📱 本地访问: http://localhost:{PROXY_PORT}")
            logger.info("=" * 60)
            logger.info("🔄 所有请求将被转发到API服务器")
            logger.info("📊 实时监控代理请求")
            logger.info("=" * 60)
            
            httpd.serve_forever()
            
    except PermissionError:
        logger.error("❌ 权限错误: 无法绑定到端口80")
        logger.info("💡 解决方案:")
        logger.info("   1. 以管理员身份运行")
        logger.info("   2. 或者修改PROXY_PORT为其他端口(如8080)")
        
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error(f"❌ 端口{PROXY_PORT}已被占用")
            logger.info("💡 请检查是否有其他服务使用此端口")
        else:
            logger.error(f"❌ 网络错误: {e}")
            
    except KeyboardInterrupt:
        logger.info("🛑 代理服务器已停止")
        
    except Exception as e:
        logger.error(f"❌ 代理服务器错误: {e}")

if __name__ == "__main__":
    run_proxy()
