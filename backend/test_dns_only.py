#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试仅限DNS模式
"""

import requests
import time
import socket

def test_dns_only_mode():
    """测试仅限DNS模式"""
    print("🔧 测试仅限DNS模式")
    print("=" * 50)
    
    # 1. 检查DNS解析
    print("1. 检查DNS解析...")
    try:
        ip = socket.gethostbyname('aigupiao.me')
        print(f"✅ aigupiao.me 解析到: {ip}")
    except Exception as e:
        print(f"❌ DNS解析失败: {e}")
    
    print()
    
    # 2. 测试HTTP访问
    print("2. 测试HTTP访问...")
    try:
        response = requests.get("http://aigupiao.me/api/health", timeout=15)
        print(f"📡 HTTP状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ HTTP访问成功: {response.json()}")
        else:
            print(f"⚠️ HTTP响应: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ HTTP访问失败: {e}")
    
    print()
    
    # 3. 测试HTTPS访问
    print("3. 测试HTTPS访问...")
    try:
        response = requests.get("https://aigupiao.me/api/health", timeout=15, verify=False)
        print(f"📡 HTTPS状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ HTTPS访问成功: {response.json()}")
        else:
            print(f"⚠️ HTTPS响应: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ HTTPS访问失败: {e}")
    
    print()
    
    # 4. 测试前端页面
    print("4. 测试前端页面...")
    try:
        response = requests.get("https://aigupiao.me/", timeout=15, verify=False)
        print(f"📡 前端页面状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ 前端页面访问成功")
            if "股票交易" in response.text or "trading" in response.text.lower():
                print(f"✅ 页面内容正确")
        else:
            print(f"⚠️ 前端响应: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ 前端访问失败: {e}")
    
    print()
    print("=" * 50)
    print("📋 测试完成！")
    print("💡 如果仍有问题，可能需要等待DNS传播（2-10分钟）")

if __name__ == "__main__":
    test_dns_only_mode()
