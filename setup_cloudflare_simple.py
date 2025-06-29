#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare Tunnel 简化设置工具
"""

import subprocess
import time
import requests
import re

class CloudflareTunnelSetup:
    def __init__(self):
        self.local_port = 8000
        self.tunnel_url = None
        
    def log(self, message, level="INFO"):
        """日志输出"""
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m", 
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "RESET": "\033[0m"
        }
        color = colors.get(level, colors["INFO"])
        print(f"{color}{message}{colors['RESET']}")
    
    def start_quick_tunnel(self):
        """启动快速隧道（无需登录）"""
        self.log("🚀 启动Cloudflare快速隧道...")
        
        try:
            # 使用 --url 参数创建临时隧道
            cmd = ['cloudflared.exe', 'tunnel', '--url', f'http://localhost:{self.local_port}']
            
            process = subprocess.Popen(cmd, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     text=True,
                                     bufsize=1,
                                     universal_newlines=True)
            
            self.log("⏳ 等待隧道启动...")
            
            # 读取输出获取URL
            timeout = 30
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if process.poll() is not None:
                    # 进程已结束
                    stdout, stderr = process.communicate()
                    self.log(f"❌ 隧道启动失败", "ERROR")
                    self.log(f"错误信息: {stderr}", "ERROR")
                    return None
                
                # 尝试读取一行输出
                try:
                    line = process.stdout.readline()
                    if line:
                        print(line.strip())
                        # 查找URL
                        if 'trycloudflare.com' in line or 'https://' in line:
                            # 提取URL
                            url_match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                            if url_match:
                                self.tunnel_url = url_match.group(0)
                                self.log(f"✅ 隧道启动成功!", "SUCCESS")
                                self.log(f"🌐 访问地址: {self.tunnel_url}", "SUCCESS")
                                return self.tunnel_url
                except:
                    pass
                
                time.sleep(0.5)
            
            self.log("❌ 隧道启动超时", "ERROR")
            process.terminate()
            return None
            
        except Exception as e:
            self.log(f"❌ 启动失败: {e}", "ERROR")
            return None
    
    def test_tunnel(self):
        """测试隧道连接"""
        if not self.tunnel_url:
            return False
            
        self.log("🧪 测试隧道连接...")
        
        try:
            test_url = f"{self.tunnel_url}/api/auth/test"
            response = requests.get(test_url, timeout=10)
            
            if response.status_code == 200:
                self.log("✅ 隧道连接测试成功!", "SUCCESS")
                self.log(f"📱 手机可访问: {test_url}", "SUCCESS")
                return True
            else:
                self.log(f"❌ 隧道测试失败: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ 隧道测试失败: {e}", "ERROR")
            return False
    
    def update_frontend_config(self):
        """更新前端配置"""
        if not self.tunnel_url:
            return False
            
        self.log("📝 更新前端配置...")
        
        try:
            # 读取当前配置
            with open('炒股养家/env.js', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换开发环境URL
            content = re.sub(
                r"apiBaseUrl: '[^']*'",
                f"apiBaseUrl: '{self.tunnel_url}'",
                content
            )
            
            # 替换WebSocket URL
            ws_url = self.tunnel_url.replace('https://', 'wss://')
            content = re.sub(
                r"wsUrl: '[^']*'",
                f"wsUrl: '{ws_url}/ws'",
                content
            )
            
            # 写回文件
            with open('炒股养家/env.js', 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log("✅ 前端配置更新完成", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ 配置更新失败: {e}", "ERROR")
            return False
    
    def run_setup(self):
        """运行完整设置"""
        self.log("🌟 Cloudflare Tunnel 免费设置")
        self.log("=" * 40)
        
        # 启动隧道
        tunnel_url = self.start_quick_tunnel()
        if not tunnel_url:
            return False
        
        # 测试连接
        if not self.test_tunnel():
            return False
        
        # 更新前端配置
        if not self.update_frontend_config():
            return False
        
        self.log("\n🎉 设置完成!", "SUCCESS")
        self.log(f"🌐 访问地址: {tunnel_url}")
        self.log(f"📱 API测试: {tunnel_url}/api/auth/test")
        self.log("\n💡 提示:")
        self.log("  - 隧道将持续运行直到程序关闭")
        self.log("  - 每次重启URL会变化")
        self.log("  - 按Ctrl+C停止隧道")
        
        return True

if __name__ == "__main__":
    setup = CloudflareTunnelSetup()
    
    if setup.run_setup():
        try:
            print("\n⏳ 隧道运行中，按Ctrl+C停止...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 隧道已停止")
    else:
        print("\n❌ 设置失败")
