#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试 - 仅限DNS模式
"""

import requests
import socket

def test_simple():
    """简化测试"""
    print("🔧 简化测试 - 仅限DNS模式")
    print("=" * 40)
    
    # 1. DNS解析
    try:
        ip = socket.gethostbyname('aigupiao.me')
        print(f"✅ DNS解析: aigupiao.me → {ip}")
    except Exception as e:
        print(f"❌ DNS解析失败: {e}")
        return
    
    # 2. 测试HTTP (不跟随重定向)
    try:
        response = requests.get("http://aigupiao.me/api/health", 
                              timeout=10, 
                              allow_redirects=False)
        print(f"📡 HTTP状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ HTTP成功: {response.json()}")
        elif response.status_code in [301, 302, 307, 308]:
            print(f"🔄 HTTP重定向到: {response.headers.get('Location', 'Unknown')}")
        else:
            print(f"⚠️ HTTP响应: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ HTTP失败: {e}")
    
    # 3. 测试HTTPS (不跟随重定向)
    try:
        response = requests.get("https://aigupiao.me/api/health", 
                              timeout=10, 
                              allow_redirects=False,
                              verify=False)
        print(f"📡 HTTPS状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ HTTPS成功: {response.json()}")
        elif response.status_code in [301, 302, 307, 308]:
            print(f"🔄 HTTPS重定向到: {response.headers.get('Location', 'Unknown')}")
        else:
            print(f"⚠️ HTTPS响应: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ HTTPS失败: {e}")
    
    print("=" * 40)
    print("💡 如果仍有重定向，请切换到'仅限DNS'模式")

if __name__ == "__main__":
    test_simple()
