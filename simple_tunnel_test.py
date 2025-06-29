#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的隧道测试工具
"""

import subprocess
import time
import requests
import threading

def test_localhost_run():
    """测试localhost.run"""
    print("🌐 测试localhost.run...")
    print("💡 这需要SSH客户端，如果没有会失败")
    
    try:
        # 尝试SSH隧道
        cmd = ['ssh', '-R', '80:localhost:8000', 'ssh.localhost.run']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("⏳ 启动SSH隧道...")
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ SSH隧道可能已启动")
            print("🔍 请查看SSH输出获取访问地址")
            return True
        else:
            print("❌ SSH隧道启动失败")
            return False
            
    except FileNotFoundError:
        print("❌ SSH客户端未找到")
        return False

def test_simple_http_server():
    """测试简单HTTP服务器"""
    print("\n🌐 测试Python内置HTTP服务器...")
    
    try:
        # 启动简单HTTP服务器
        cmd = ['python', '-m', 'http.server', '9999']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("⏳ 启动HTTP服务器在端口9999...")
        time.sleep(3)
        
        # 测试本地访问
        try:
            response = requests.get('http://localhost:9999', timeout=5)
            if response.status_code == 200:
                print("✅ HTTP服务器启动成功")
                print("🌐 本地访问: http://localhost:9999")
                
                # 停止服务器
                process.terminate()
                return True
        except:
            pass
        
        process.terminate()
        print("❌ HTTP服务器测试失败")
        return False
        
    except Exception as e:
        print(f"❌ HTTP服务器启动失败: {e}")
        return False

def check_current_tunnels():
    """检查当前运行的隧道"""
    print("\n🔍 检查当前运行的隧道...")
    
    # 检查ngrok
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=3)
        if response.status_code == 200:
            tunnels = response.json().get('tunnels', [])
            if tunnels:
                tunnel = tunnels[0]
                url = tunnel['public_url']
                print(f"✅ ngrok隧道运行中: {url}")
                
                # 测试连接
                try:
                    test_response = requests.get(f"{url}/api/auth/test", timeout=10)
                    if test_response.status_code == 200:
                        print("✅ ngrok连接测试成功")
                        print(f"📱 推荐使用: {url}")
                        return url
                    else:
                        print("⚠️ ngrok连接测试失败")
                except:
                    print("⚠️ ngrok连接测试失败")
            else:
                print("❌ ngrok无活跃隧道")
        else:
            print("❌ ngrok API不可访问")
    except:
        print("❌ ngrok未运行")
    
    return None

def main():
    """主函数"""
    print("🚀 免费隧道方案测试")
    print("=" * 40)
    
    # 1. 检查当前隧道
    current_url = check_current_tunnels()
    if current_url:
        print(f"\n🎉 发现可用隧道: {current_url}")
        print("💡 建议继续使用当前隧道")
        return
    
    # 2. 测试localhost.run
    if test_localhost_run():
        print("💡 localhost.run可用，请查看SSH输出")
        return
    
    # 3. 测试简单HTTP服务器
    test_simple_http_server()
    
    print("\n💡 建议:")
    print("1. 继续使用ngrok（如果已启动）")
    print("2. 尝试Cloudflare Tunnel")
    print("3. 或者配置路由器端口转发")

if __name__ == "__main__":
    main()
