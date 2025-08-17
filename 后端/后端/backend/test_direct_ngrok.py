#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试ngrok地址
"""

import requests
import socket

def test_direct_ngrok():
    """直接测试ngrok"""
    print("🔧 直接测试ngrok地址")
    print("=" * 40)
    
    ngrok_url = "https://5db1-116-169-10-245.ngrok-free.app"
    
    # 1. 测试ngrok健康检查
    try:
        response = requests.get(f"{ngrok_url}/api/health", 
                              timeout=10,
                              headers={'ngrok-skip-browser-warning': 'true'})
        print(f"✅ ngrok健康检查: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ 响应: {response.json()}")
        else:
            print(f"⚠️ 响应: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ ngrok健康检查失败: {e}")
    
    # 2. 测试ngrok前端
    try:
        response = requests.get(f"{ngrok_url}/", 
                              timeout=10,
                              headers={'ngrok-skip-browser-warning': 'true'})
        print(f"✅ ngrok前端: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ 前端页面正常")
        else:
            print(f"⚠️ 前端响应: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ ngrok前端失败: {e}")
    
    print()
    
    # 3. 测试域名解析
    try:
        ip = socket.gethostbyname('aigupiao.me')
        print(f"📡 aigupiao.me 解析到: {ip}")
        
        # 检查是否解析到ngrok
        ngrok_host = "5db1-116-169-10-245.ngrok-free.app"
        ngrok_ip = socket.gethostbyname(ngrok_host)
        print(f"📡 {ngrok_host} 解析到: {ngrok_ip}")
        
        if ip == ngrok_ip:
            print("✅ 域名正确解析到ngrok服务器")
        else:
            print("⚠️ 域名没有解析到ngrok服务器")
            print("💡 可能需要等待DNS传播(5-10分钟)")
            
    except Exception as e:
        print(f"❌ DNS解析失败: {e}")
    
    print()
    
    # 4. 测试域名访问(带ngrok头)
    try:
        response = requests.get("https://aigupiao.me/api/health", 
                              timeout=10,
                              headers={'ngrok-skip-browser-warning': 'true'},
                              allow_redirects=False)
        print(f"📡 域名访问状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ 域名访问成功: {response.json()}")
        elif response.status_code in [301, 302, 307, 308]:
            print(f"🔄 域名重定向到: {response.headers.get('Location', 'Unknown')}")
        else:
            print(f"⚠️ 域名响应: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ 域名访问失败: {e}")
    
    print("=" * 40)
    print("📋 测试完成!")

if __name__ == "__main__":
    test_direct_ngrok()
