#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试ngrok公网连接
"""

import requests
import json

def test_ngrok_connection():
    """测试ngrok公网连接"""
    ngrok_url = "https://5db1-116-169-10-245.ngrok-free.app"
    
    print("🧪 测试ngrok公网连接")
    print("=" * 50)
    print(f"🌐 公网地址: {ngrok_url}")
    print()
    
    # 测试根路径
    try:
        print("📡 测试根路径...")
        response = requests.get(f"{ngrok_url}/", timeout=10)
        print(f"✅ 状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 响应: {data['message']}")
            print(f"✅ 版本: {data['version']}")
        else:
            print(f"⚠️ 响应内容: {response.text[:200]}")
    except Exception as e:
        print(f"❌ 根路径测试失败: {e}")
    
    print()
    
    # 测试健康检查
    try:
        print("🏥 测试健康检查...")
        response = requests.get(f"{ngrok_url}/api/health", timeout=10)
        print(f"✅ 状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务状态: {data['status']}")
            print(f"✅ 服务名称: {data['service']}")
        else:
            print(f"⚠️ 响应内容: {response.text[:200]}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
    
    print()
    
    # 测试系统状态
    try:
        print("📊 测试系统状态...")
        response = requests.get(f"{ngrok_url}/api/v1/agent-trading/system-status", timeout=10)
        print(f"✅ 状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ AI服务: {data['data']['ai_service']}")
                print(f"✅ 交易服务: {data['data']['trading_service']}")
                print(f"✅ 数据服务: {data['data']['data_service']}")
            else:
                print(f"⚠️ 系统状态异常")
        else:
            print(f"⚠️ 响应内容: {response.text[:200]}")
    except Exception as e:
        print(f"❌ 系统状态测试失败: {e}")
    
    print()
    print("🎉 ngrok连接测试完成！")
    print()
    print("📋 下一步操作：")
    print("1. 登录Cloudflare控制台")
    print("2. 更新DNS记录")
    print("3. 测试域名访问")

if __name__ == "__main__":
    test_ngrok_connection()
