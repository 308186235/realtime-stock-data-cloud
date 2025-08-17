# 文件操作最佳实践:
# 1. 始终使用 with 语句打开文件
# 2. 避免在循环中重复打开同一文件
# 3. 大文件处理时考虑分块读取
# 4. 异常情况下确保文件正确关闭

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的前端服务器启动器
"""

import http.server
import socketserver
import webbrowser
import os
import threading
import time

PORT = 9000

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP请求处理器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="frontend", **kwargs)
    
    def end_headers(self):
        # 添加CORS头
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        # 自定义日志格式
        print(f"[前端服务器] {self.address_string()} - {format % args}")

def start_server():
    """启动前端服务器"""
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print("=" * 60)
            print("🌐 前端服务器启动成功!")
            print("=" * 60)
            print(f"📍 服务地址: http://localhost:{PORT}")
            print(f"📄 测试页面: http://localhost:{PORT}/simple_frontend.html")
            print(f"🔗 后端API: http://localhost:8002")
            print("=" * 60)
            print("💡 提示:")
            print("  - 前端会自动连接到后端API")
            print("  - 可以测试所有API端点")
            print("  - 按 Ctrl+C 停止服务器")
            print("=" * 60)
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 前端服务器已停止")
    except Exception as e:
        print(f"❌ 启动前端服务器失败: {e}")

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)  # 等待服务器启动
    url = f"http://localhost:{PORT}/simple_frontend.html"
    print(f"🌐 正在打开浏览器: {url}")
    webbrowser.open(url)

def main():
    """主函数"""
    # 检查前端文件是否存在
    frontend_file = "frontend/simple_frontend.html"
    if not os.path.exists(frontend_file):
        print(f"❌ 前端文件不存在: {frontend_file}")
        return
    
    # 在后台线程中打开浏览器
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
