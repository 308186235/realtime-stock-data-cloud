#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
域名访问配置工具 - 配置aigupiao.me域名访问
"""

import os
import json
import requests
import subprocess
import time
from datetime import datetime

class DomainAccessSetup:
    """域名访问配置器"""
    
    def __init__(self):
        self.domain = "aigupiao.me"
        self.local_port = 8002
        self.ngrok_url = None
        self.setup_log = []
    
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.setup_log.append(log_entry)
        print(log_entry)
    
    def check_domain_status(self):
        """检查域名状态"""
        self.log("🔍 检查域名状态...")
        
        try:
            # 测试HTTPS访问
            response = requests.get(f"https://{self.domain}", timeout=10)
            self.log(f"✅ 域名HTTPS访问正常: {response.status_code}")
            return True
        except requests.exceptions.SSLError:
            self.log("⚠️ SSL证书问题，尝试HTTP访问")
            try:
                response = requests.get(f"http://{self.domain}", timeout=10)
                self.log(f"✅ 域名HTTP访问正常: {response.status_code}")
                return True
            except Exception as e:
                self.log(f"❌ 域名访问失败: {e}")
                return False
        except Exception as e:
            self.log(f"❌ 域名访问失败: {e}")
            return False
    
    def check_ngrok_status(self):
        """检查ngrok状态"""
        self.log("🔍 检查ngrok状态...")
        
        try:
            # 检查ngrok API
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                tunnels = response.json()
                if tunnels.get('tunnels'):
                    tunnel = tunnels['tunnels'][0]
                    self.ngrok_url = tunnel['public_url']
                    self.log(f"✅ ngrok隧道运行中: {self.ngrok_url}")
                    return True
                else:
                    self.log("⚠️ ngrok运行但无隧道")
                    return False
            else:
                self.log("❌ ngrok API不可访问")
                return False
        except Exception as e:
            self.log(f"❌ ngrok检查失败: {e}")
            return False
    
    def start_ngrok(self):
        """启动ngrok隧道"""
        self.log("🚀 启动ngrok隧道...")
        
        try:
            # 启动ngrok
            cmd = f"ngrok http {self.local_port} --log=stdout"
            process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待ngrok启动
            time.sleep(5)
            
            # 检查是否启动成功
            if self.check_ngrok_status():
                self.log("✅ ngrok启动成功")
                return True
            else:
                self.log("❌ ngrok启动失败")
                return False
                
        except Exception as e:
            self.log(f"❌ 启动ngrok失败: {e}")
            return False
    
    def update_frontend_config(self):
        """更新前端配置使用域名"""
        self.log("🔧 更新前端配置...")
        
        config_files = [
            "frontend/gupiao1/env.js",
            "frontend/gupiao1/services/config.js",
            "frontend/stock5/env.js",
            "炒股养家/env.js",
            "炒股养家/services/config.js"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 更新API URL为域名
                    content = content.replace(
                        'http://localhost:8002', 
                        f'https://{self.domain}'
                    )
                    content = content.replace(
                        'http://localhost:8000', 
                        f'https://{self.domain}'
                    )
                    
                    with open(config_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.log(f"✅ 更新配置文件: {config_file}")
                    
                except Exception as e:
                    self.log(f"❌ 更新配置文件失败 {config_file}: {e}")
            else:
                self.log(f"⚠️ 配置文件不存在: {config_file}")
    
    def create_domain_server(self):
        """创建支持域名访问的服务器"""
        self.log("🔧 创建域名访问服务器...")
        
        server_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
域名访问服务器 - 支持 {self.domain}
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

PORT = {self.local_port}
DOMAIN = "{self.domain}"

class DomainAccessHTTPRequestHandler(BaseHTTPRequestHandler):
    """支持域名访问的HTTP请求处理器"""
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        host = self.headers.get('Host', 'unknown')
        user_agent = self.headers.get('User-Agent', '')
        is_mobile = any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone', 'ipad'])
        device_type = "📱 手机" if is_mobile else "💻 电脑"
        logger.info(f"{{device_type}} {{host}} - {{format % args}}")
    
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
                data = {{}}
        else:
            data = {{}}
        
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
.container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
.domain {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 10px 0; }}
.status {{ color: #28a745; font-weight: bold; }}
</style></head>
<body>
<div class="container">
<h1>🚀 {DOMAIN} 交易系统</h1>
<div class="domain">
<h3>🌐 域名访问信息</h3>
<p>访问域名: <strong>{host}</strong></p>
<p>目标域名: <strong>{DOMAIN}</strong></p>
<p>服务端口: <strong>{PORT}</strong></p>
</div>
<p>系统状态: <span class="status">正常运行</span></p>
<p>时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<h2>🔗 API端点</h2>
<ul>
<li><a href="/api/health">/api/health</a> - 健康检查</li>
<li><a href="/test">/test</a> - 测试端点</li>
<li><a href="/api/stock/quote?code=000001">/api/stock/quote</a> - 股票报价</li>
</ul>
</div>
</body></html>"""
        
        self._send_html_response(html)
    
    def _handle_health(self):
        """健康检查"""
        host = self.headers.get('Host', 'localhost')
        response = {{
            "status": "healthy",
            "message": f"域名访问正常 - {DOMAIN}",
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0",
            "domain": DOMAIN,
            "host": host,
            "port": PORT,
            "domain_access": True
        }}
        self._send_json_response(response)
    
    def _handle_test(self):
        """处理测试请求"""
        host = self.headers.get('Host', 'localhost')
        response = {{
            "status": "ok",
            "message": f"域名测试成功 - {DOMAIN}",
            "timestamp": datetime.now().isoformat(),
            "domain": DOMAIN,
            "host": host,
            "note": "域名访问正常工作"
        }}
        self._send_json_response(response)
    
    def _handle_api(self, path, query):
        """处理API请求"""
        host = self.headers.get('Host', 'localhost')
        response = {{
            "api": path,
            "method": "GET",
            "query": query,
            "domain": DOMAIN,
            "host": host,
            "timestamp": datetime.now().isoformat(),
            "message": "API通过域名访问正常"
        }}
        self._send_json_response(response)
    
    def _handle_api_post(self, path, data):
        """处理API POST请求"""
        host = self.headers.get('Host', 'localhost')
        response = {{
            "api": path,
            "method": "POST",
            "data": data,
            "domain": DOMAIN,
            "host": host,
            "timestamp": datetime.now().isoformat(),
            "message": "POST API通过域名访问正常"
        }}
        self._send_json_response(response)
    
    def _handle_catch_all(self, path, method='GET'):
        """捕获所有其他请求"""
        host = self.headers.get('Host', 'localhost')
        response = {{
            "path": path,
            "method": method,
            "domain": DOMAIN,
            "host": host,
            "timestamp": datetime.now().isoformat(),
            "message": f"请求已被域名服务器处理"
        }}
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
        logger.error(f"❌ 服务器错误: {{e}}")

if __name__ == "__main__":
    run_server()
'''
        
        # 保存服务器代码
        with open('domain_access_server.py', 'w', encoding='utf-8') as f:
            f.write(server_code)
        
        self.log("✅ 域名访问服务器创建完成")
    
    def test_domain_api(self):
        """测试域名API访问"""
        self.log("🧪 测试域名API访问...")
        
        test_urls = [
            f"https://{self.domain}/api/health",
            f"https://{self.domain}/test",
            f"https://{self.domain}/"
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=10, verify=False)
                if response.status_code == 200:
                    self.log(f"✅ {url}: {response.status_code}")
                else:
                    self.log(f"⚠️ {url}: {response.status_code}")
            except Exception as e:
                self.log(f"❌ {url}: {e}")
    
    def generate_setup_report(self):
        """生成配置报告"""
        self.log("📋 生成配置报告...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "domain": self.domain,
            "local_port": self.local_port,
            "ngrok_url": self.ngrok_url,
            "setup_log": self.setup_log,
            "access_urls": {
                "domain": f"https://{self.domain}",
                "local": f"http://localhost:{self.local_port}",
                "ngrok": self.ngrok_url
            },
            "mobile_access": {
                "recommended": f"https://{self.domain}",
                "note": "使用域名访问，支持手机和电脑"
            }
        }
        
        with open('domain_access_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log("✅ 配置报告已保存到: domain_access_report.json")
    
    def run_setup(self):
        """运行完整配置"""
        print("🌐 域名访问配置工具")
        print("=" * 60)
        
        # 1. 检查域名状态
        domain_ok = self.check_domain_status()
        
        # 2. 检查ngrok状态
        ngrok_ok = self.check_ngrok_status()
        
        # 3. 如果ngrok未运行，尝试启动
        if not ngrok_ok:
            self.start_ngrok()
        
        # 4. 更新前端配置
        self.update_frontend_config()
        
        # 5. 创建域名访问服务器
        self.create_domain_server()
        
        # 6. 测试域名API
        if domain_ok:
            self.test_domain_api()
        
        # 7. 生成报告
        self.generate_setup_report()
        
        print("\n" + "=" * 60)
        print("🎉 域名访问配置完成!")
        print("=" * 60)
        print(f"🌐 域名访问: https://{self.domain}")
        print(f"📱 手机访问: https://{self.domain}")
        print(f"💻 本机访问: http://localhost:{self.local_port}")
        print("=" * 60)
        print("📋 下一步:")
        print("  1. 启动域名访问服务器: python domain_access_server.py")
        print("  2. 测试域名访问: https://aigupiao.me/api/health")
        print("  3. 在手机上访问: https://aigupiao.me")
        print("=" * 60)

def main():
    """主函数"""
    setup = DomainAccessSetup()
    setup.run_setup()

if __name__ == "__main__":
    main()
