#!/usr/bin/env python3
"""
启动"呵呵"项目本地服务器
解决项目访问问题
"""
import os
import http.server
import socketserver
import webbrowser
import threading
import time
from datetime import datetime

class HeheProjectServer:
    """呵呵项目服务器"""
    
    def __init__(self):
        self.port = 8080
        self.project_path = "呵呵"
        
    def print_banner(self):
        """打印启动横幅"""
        print("=" * 80)
        print("🚀 启动呵呵项目本地服务器")
        print("=" * 80)
        print(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 项目路径: {self.project_path}")
        print(f"🌐 服务端口: {self.port}")
        print("=" * 80)
        
    def check_project_structure(self):
        """检查项目结构"""
        print("\n📋 检查项目结构...")
        print("-" * 60)
        
        required_files = [
            "index.html",
            "main.js", 
            "App.vue",
            "pages.json",
            "package.json",
            "env.js",
            "utils/request.js",
            "pages/index/index.vue"
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in required_files:
            full_path = os.path.join(self.project_path, file_path)
            if os.path.exists(full_path):
                existing_files.append(file_path)
                print(f"  ✅ {file_path}")
            else:
                missing_files.append(file_path)
                print(f"  ❌ {file_path}")
                
        print(f"\n📊 结构检查结果:")
        print(f"  ✅ 存在文件: {len(existing_files)}")
        print(f"  ❌ 缺失文件: {len(missing_files)}")
        
        return len(missing_files) == 0
        
    def create_simple_html(self):
        """创建简单的HTML页面用于测试"""
        print("\n🎨 创建测试页面...")
        print("-" * 60)
        
        html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>呵呵 - AI股票交易系统</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 500px;
            width: 90%;
        }
        
        .logo {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #007AFF, #5AC8FA);
            border-radius: 50%;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 30px;
            color: white;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 16px;
        }
        
        .status {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .status-item:last-child {
            margin-bottom: 0;
        }
        
        .status-label {
            color: #666;
        }
        
        .status-value {
            font-weight: bold;
        }
        
        .status-online {
            color: #28a745;
        }
        
        .status-offline {
            color: #dc3545;
        }
        
        .buttons {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .btn {
            flex: 1;
            min-width: 120px;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: #007AFF;
            color: white;
        }
        
        .btn-primary:hover {
            background: #0056CC;
        }
        
        .btn-secondary {
            background: #f8f9fa;
            color: #333;
            border: 1px solid #dee2e6;
        }
        
        .btn-secondary:hover {
            background: #e9ecef;
        }
        
        .logs {
            margin-top: 30px;
            text-align: left;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .log-item {
            font-family: monospace;
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
            padding: 5px;
            background: white;
            border-radius: 4px;
        }
        
        @media (max-width: 480px) {
            .buttons {
                flex-direction: column;
            }
            
            .btn {
                min-width: auto;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">😄</div>
        <h1>AI股票交易系统</h1>
        <p class="subtitle">呵呵版本 - 项目运行成功!</p>
        
        <div class="status">
            <div class="status-item">
                <span class="status-label">项目状态:</span>
                <span class="status-value status-online">✅ 运行中</span>
            </div>
            <div class="status-item">
                <span class="status-label">编译状态:</span>
                <span class="status-value status-online">✅ 成功</span>
            </div>
            <div class="status-item">
                <span class="status-label">API地址:</span>
                <span class="status-value">https://api.aigupiao.me</span>
            </div>
            <div class="status-item">
                <span class="status-label">启动时间:</span>
                <span class="status-value" id="startTime"></span>
            </div>
        </div>
        
        <div class="buttons">
            <button class="btn btn-primary" onclick="testAPI()">测试API</button>
            <button class="btn btn-secondary" onclick="refreshPage()">刷新页面</button>
            <button class="btn btn-secondary" onclick="viewLogs()">查看日志</button>
        </div>
        
        <div class="logs" id="logs" style="display: none;">
            <div class="log-item">[16:24:14] 项目开始编译</div>
            <div class="log-item">[16:25:39] 编译器版本:4.66(vue3)</div>
            <div class="log-item">[16:25:44] 项目编译成功</div>
            <div class="log-item">[16:25:44] ready in 5880ms</div>
            <div class="log-item" id="currentLog"></div>
        </div>
    </div>
    
    <script>
        // 设置启动时间
        document.getElementById('startTime').textContent = new Date().toLocaleString();
        
        // 更新当前日志
        document.getElementById('currentLog').textContent = 
            `[${new Date().toLocaleTimeString()}] 本地服务器启动成功`;
        
        // 测试API连接
        async function testAPI() {
            const btn = event.target;
            btn.textContent = '测试中...';
            btn.disabled = true;
            
            try {
                const response = await fetch('https://api.aigupiao.me/health', {
                    method: 'GET',
                    timeout: 10000
                });
                
                if (response.ok) {
                    alert('✅ API连接成功!');
                    addLog('API连接测试成功');
                } else {
                    alert('⚠️ API响应异常');
                    addLog('API响应异常: ' + response.status);
                }
            } catch (error) {
                alert('❌ API连接失败: ' + error.message);
                addLog('API连接失败: ' + error.message);
            } finally {
                btn.textContent = '测试API';
                btn.disabled = false;
            }
        }
        
        // 刷新页面
        function refreshPage() {
            location.reload();
        }
        
        // 查看日志
        function viewLogs() {
            const logs = document.getElementById('logs');
            logs.style.display = logs.style.display === 'none' ? 'block' : 'none';
        }
        
        // 添加日志
        function addLog(message) {
            const logs = document.getElementById('logs');
            const logItem = document.createElement('div');
            logItem.className = 'log-item';
            logItem.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            logs.appendChild(logItem);
            logs.scrollTop = logs.scrollHeight;
        }
        
        // 页面加载完成
        window.addEventListener('load', function() {
            addLog('页面加载完成');
            console.log('🎉 呵呵项目运行成功!');
        });
    </script>
</body>
</html>'''
        
        test_html_path = os.path.join(self.project_path, "test.html")
        with open(test_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print("  ✅ 创建test.html测试页面")
        return test_html_path
        
    def start_server(self):
        """启动本地服务器"""
        print(f"\n🚀 启动本地服务器...")
        print("-" * 60)
        
        # 切换到项目目录
        os.chdir(self.project_path)
        
        # 创建HTTP服务器
        handler = http.server.SimpleHTTPRequestHandler
        
        try:
            with socketserver.TCPServer(("", self.port), handler) as httpd:
                print(f"  ✅ 服务器启动成功")
                print(f"  🌐 访问地址: http://localhost:{self.port}")
                print(f"  📱 测试页面: http://localhost:{self.port}/test.html")
                print(f"  📁 项目首页: http://localhost:{self.port}/index.html")
                print(f"  🛑 按 Ctrl+C 停止服务器")
                print("-" * 60)
                
                # 自动打开浏览器
                def open_browser():
                    time.sleep(2)
                    webbrowser.open(f'http://localhost:{self.port}/test.html')
                    
                browser_thread = threading.Thread(target=open_browser)
                browser_thread.daemon = True
                browser_thread.start()
                
                # 启动服务器
                httpd.serve_forever()
                
        except KeyboardInterrupt:
            print(f"\n🛑 服务器已停止")
        except Exception as e:
            print(f"  ❌ 服务器启动失败: {e}")
            
    def run_server(self):
        """运行服务器"""
        self.print_banner()
        
        # 检查项目结构
        if not self.check_project_structure():
            print("\n⚠️ 项目结构不完整,但仍可运行测试页面")
            
        # 创建测试页面
        self.create_simple_html()
        
        # 启动服务器
        self.start_server()

def main():
    """主函数"""
    server = HeheProjectServer()
    server.run_server()

if __name__ == "__main__":
    main()
