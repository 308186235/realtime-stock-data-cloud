#!/usr/bin/env python3
"""
测试交易API Worker
"""

import requests
import json
import time

# API基础URL
API_BASE = "https://trading-api.308186235.workers.dev"

def test_api():
    """测试API功能"""
    print("🧪 测试交易API Worker")
    print("=" * 50)
    
    # 测试健康检查
    print("\n1. 测试健康检查...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
    
    # 测试根路径
    print("\n2. 测试根路径...")
    try:
        response = requests.get(f"{API_BASE}/", timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"❌ 根路径测试失败: {e}")
    
    # 测试股票列表API
    print("\n3. 测试股票列表API...")
    try:
        response = requests.get(f"{API_BASE}/api/stock/list", timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"❌ 股票列表API失败: {e}")
    
    # 测试股票信息API
    print("\n4. 测试股票信息API...")
    try:
        response = requests.get(f"{API_BASE}/api/stock/info/000001", timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"❌ 股票信息API失败: {e}")
    
    # 测试买入订单API
    print("\n5. 测试买入订单API...")
    try:
        buy_data = {
            "stockCode": "000001",
            "quantity": 100,
            "price": 10.50
        }
        response = requests.post(f"{API_BASE}/api/trading/buy", 
                               json=buy_data, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"❌ 买入订单API失败: {e}")
    
    # 测试余额查询API
    print("\n6. 测试余额查询API...")
    try:
        response = requests.get(f"{API_BASE}/api/trading/balance", timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"❌ 余额查询API失败: {e}")
    
    # 测试数据导出API
    print("\n7. 测试数据导出API...")
    try:
        export_data = {
            "type": "holdings",
            "startDate": "2025-01-01",
            "endDate": "2025-07-02"
        }
        response = requests.post(f"{API_BASE}/api/data/export", 
                               json=export_data, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"❌ 数据导出API失败: {e}")
    
    print("\n✅ API测试完成!")
    print(f"🌐 Worker URL: {API_BASE}")
    print("📝 可以在Cloudflare Dashboard中查看日志和监控")

if __name__ == "__main__":
    test_api()
