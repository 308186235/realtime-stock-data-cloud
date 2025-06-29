#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动Cloudflare快速隧道并获取URL
"""

import subprocess
import time
import re
import threading

class QuickTunnel:
    def __init__(self):
        self.tunnel_url = None
        self.process = None
        
    def start_tunnel(self):
        """启动快速隧道"""
        print("🚀 启动Cloudflare快速隧道...")
        
        try:
            self.process = subprocess.Popen(
                ["cloudflared.exe", "tunnel", "--url", "http://localhost:8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            print("⏳ 等待隧道启动...")
            
            # 读取输出获取URL
            def read_output():
                while True:
                    if self.process.poll() is not None:
                        break
                    
                    line = self.process.stdout.readline()
                    if line:
                        print(line.strip())
                        
                        # 查找URL
                        if 'trycloudflare.com' in line:
                            url_match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                            if url_match:
                                self.tunnel_url = url_match.group(0)
                                print(f"\n🎉 隧道启动成功!")
                                print(f"🌐 访问地址: {self.tunnel_url}")
                                print(f"📱 API测试: {self.tunnel_url}/api/auth/test")
                                break
            
            # 启动读取线程
            thread = threading.Thread(target=read_output)
            thread.daemon = True
            thread.start()
            
            # 等待URL获取
            timeout = 30
            start_time = time.time()
            
            while not self.tunnel_url and time.time() - start_time < timeout:
                if self.process.poll() is not None:
                    print("❌ 隧道进程意外退出")
                    return None
                time.sleep(1)
            
            if self.tunnel_url:
                return self.tunnel_url
            else:
                print("❌ 获取隧道URL超时")
                return None
                
        except Exception as e:
            print(f"❌ 启动隧道失败: {e}")
            return None
    
    def test_tunnel(self):
        """测试隧道连接"""
        if not self.tunnel_url:
            return False
            
        print(f"\n🧪 测试隧道连接...")
        
        import requests
        try:
            test_url = f"{self.tunnel_url}/api/auth/test"
            response = requests.get(test_url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ 隧道测试成功!")
                print(f"📱 手机可访问: {test_url}")
                return True
            else:
                print(f"❌ 隧道测试失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 隧道测试失败: {e}")
            return False
    
    def stop_tunnel(self):
        """停止隧道"""
        if self.process:
            self.process.terminate()
            print("👋 隧道已停止")

if __name__ == "__main__":
    tunnel = QuickTunnel()
    
    try:
        url = tunnel.start_tunnel()
        if url:
            tunnel.test_tunnel()
            
            print("\n💡 提示:")
            print("  - 隧道将持续运行")
            print("  - 按Ctrl+C停止隧道")
            print("  - 这个URL可以立即使用")
            
            # 保持运行
            while True:
                time.sleep(1)
        else:
            print("❌ 隧道启动失败")
            
    except KeyboardInterrupt:
        print("\n停止隧道...")
        tunnel.stop_tunnel()
    except Exception as e:
        print(f"❌ 错误: {e}")
        tunnel.stop_tunnel()
