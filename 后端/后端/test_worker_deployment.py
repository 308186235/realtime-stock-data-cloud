#!/usr/bin/env python3
"""
测试Worker部署状态
"""

import requests
import json
import time

def test_worker():
    """测试Worker部署"""
    worker_url = "https://trading-api.308186235.workers.dev"
    
    print("🧪 测试云端Worker部署")
    print("=" * 50)
    print(f"🎯 Worker URL: {worker_url}")
    
    # 测试端点
    endpoints = [
        "/",
        "/api/agent-analysis", 
        "/api/account-balance",
        "/api/account-positions"
    ]
    
    for endpoint in endpoints:
        url = f"{worker_url}{endpoint}"
        print(f"\n📡 测试: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ 状态: {response.status_code} OK")
                
                try:
                    data = response.json()
                    if data.get("success"):
                        print("✅ 响应格式: JSON正确")
                        if "data" in data:
                            print(f"✅ 数据字段: 存在")
                        if "timestamp" in data.get("data", {}):
                            print(f"✅ 时间戳: {data['data']['timestamp']}")
                    else:
                        print("⚠️ 响应格式: success字段为false")
                except:
                    print("⚠️ 响应格式: 非JSON格式")
                    print(f"   内容: {response.text[:100]}...")
                    
            else:
                print(f"❌ 状态: {response.status_code}")
                print(f"   响应: {response.text[:100]}...")
                
        except requests.exceptions.Timeout:
            print("⏰ 超时: 请求超时")
        except requests.exceptions.ConnectionError:
            print("🔌 连接错误: 无法连接到Worker")
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    print(f"\n{'='*50}")
    print("🎯 测试完成")

if __name__ == "__main__":
    test_worker()
