#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试服务器 - 简单的HTTP服务器用于测试Cloudflare Tunnel
"""

import http.server
import socketserver
import json
from datetime import datetime

PORT = 9000

class TestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "message": "Test server is working!",
                "path": self.path,
                "client": self.client_address[0]
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
            print(f"Health check from {self.client_address[0]}")
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Test Server</title>
                <meta charset="utf-8">
            </head>
            <body>
                <h1>🚀 Test Server Working!</h1>
                <p><strong>Time:</strong> {datetime.now().isoformat()}</p>
                <p><strong>Path:</strong> {self.path}</p>
                <p><strong>Client:</strong> {self.client_address[0]}</p>
                <p><strong>Port:</strong> {PORT}</p>
                <hr>
                <p><a href="/api/health">Health Check API</a></p>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode('utf-8'))
            print(f"Request from {self.client_address[0]} for {self.path}")

if __name__ == "__main__":
    print(f"🚀 Starting test server on port {PORT}")
    print(f"📍 Local: http://localhost:{PORT}")
    print(f"🔗 Health: http://localhost:{PORT}/api/health")
    print("Press Ctrl+C to stop")
    
    with socketserver.TCPServer(("", PORT), TestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
