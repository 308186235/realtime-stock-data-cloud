#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试530错误修复
"""

import requests
import time

def test_with_different_methods():
    """使用不同方法测试访问"""
    print("🔧 测试530错误修复")
    print("=" * 50)
    
    # 测试ngrok直接访问
    print("1. 测试ngrok直接访问...")
    try:
        response = requests.get("https://5db1-116-169-10-245.ngrok-free.app/api/health", timeout=10)
        print(f"✅ ngrok直接访问: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ ngrok服务正常: {response.json()}")
    except Exception as e:
        print(f"❌ ngrok访问失败: {e}")
    
    print()
    
    # 测试域名访问(HTTP)
    print("2. 测试HTTP访问...")
    try:
        response = requests.get("http://aigupiao.me/api/health", timeout=15, allow_redirects=True)
        print(f"📡 HTTP状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ HTTP访问成功: {response.json()}")
        else:
            print(f"⚠️ HTTP响应: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ HTTP访问失败: {e}")
    
    print()
    
    # 测试域名访问(HTTPS)
    print("3. 测试HTTPS访问...")
    try:
        response = requests.get("https://aigupiao.me/api/health", timeout=15, allow_redirects=True)
        print(f"📡 HTTPS状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ HTTPS访问成功: {response.json()}")
        elif response.status_code == 530:
            print(f"❌ 530错误 - Cloudflare无法连接到源服务器")
            print("💡 可能原因:")
            print("   - CNAME记录内容不正确")
            print("   - 代理状态配置问题")
            print("   - ngrok地址已变化")
        else:
            print(f"⚠️ HTTPS响应: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ HTTPS访问失败: {e}")
    
    print()
    
    # 测试不同的User-Agent
    print("4. 测试不同User-Agent...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get("https://aigupiao.me/api/health", headers=headers, timeout=15)
        print(f"📡 自定义UA状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ 自定义UA成功: {response.json()}")
    except Exception as e:
        print(f"❌ 自定义UA失败: {e}")
    
    print()
    print("=" * 50)
    print("📋 修复建议:")
    print("1. 确认Cloudflare CNAME记录内容为: 5db1-116-169-10-245.ngrok-free.app")
    print("2. 确认代理状态为'已代理'(橙色云朵)")
    print("3. 如果仍有问题,尝试'仅限DNS'模式")
    print("4. 检查ngrok是否仍在运行")

def check_ngrok_status():
    """检查ngrok状态"""
    print("\n🔍 检查ngrok状态...")
    try:
        # 检查ngrok API
        response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            tunnels = response.json().get('tunnels', [])
            if tunnels:
                tunnel = tunnels[0]
                print(f"✅ ngrok隧道活跃")
                print(f"📡 公网地址: {tunnel['public_url']}")
                print(f"🔗 本地地址: {tunnel['config']['addr']}")
                return tunnel['public_url']
            else:
                print("❌ 没有活跃的ngrok隧道")
        else:
            print("❌ 无法获取ngrok状态")
    except Exception as e:
        print(f"❌ ngrok API访问失败: {e}")
    
    return None

if __name__ == "__main__":
    # 检查ngrok状态
    ngrok_url = check_ngrok_status()
    
    # 运行测试
    test_with_different_methods()
    
    if ngrok_url:
        print(f"\n🔧 当前ngrok地址: {ngrok_url}")
        print("💡 请确认Cloudflare DNS记录使用此地址")
