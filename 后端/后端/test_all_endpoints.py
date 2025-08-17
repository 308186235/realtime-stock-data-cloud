#!/usr/bin/env python3
"""
测试所有API端点
"""

import requests
import json

def test_all_endpoints():
    """测试所有端点"""
    base_url = "https://api.aigupiao.me"
    
    # 前端正在调用的所有端点
    endpoints = [
        # 基础端点
        {"path": "/", "name": "根路径"},
        {"path": "/health", "name": "健康检查"},
        {"path": "/api/health", "name": "API健康检查"},
        
        # Agent相关
        {"path": "/api/agent-analysis", "name": "Agent分析"},
        {"path": "/api/agent/status", "name": "Agent状态"},
        {"path": "/api/agent/analysis", "name": "Agent分析(备用)"},
        
        # 账户相关
        {"path": "/api/account-balance", "name": "账户余额"},
        {"path": "/api/account-positions", "name": "账户持仓"},
        {"path": "/api/account/balance", "name": "账户余额(备用)"},
        {"path": "/api/account/positions", "name": "账户持仓(备用)"},
        
        # 市场相关
        {"path": "/api/market-data", "name": "市场数据"},
        {"path": "/api/market/status", "name": "市场状态"},
    ]
    
    print("🧪 测试所有API端点")
    print("=" * 50)
    print(f"🎯 基础URL: {base_url}")
    print("=" * 50)
    
    passed = 0
    total = len(endpoints)
    
    for i, endpoint in enumerate(endpoints, 1):
        path = endpoint["path"]
        name = endpoint["name"]
        url = f"{base_url}{path}"
        
        print(f"\n📋 测试 {i}/{total}: {name}")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if data.get("success"):
                        print("   ✅ 通过: 响应正常")
                        passed += 1
                        
                        # 显示关键信息
                        if "message" in data:
                            print(f"   📝 消息: {data['message'][:50]}...")
                        if "data" in data and isinstance(data["data"], dict):
                            if "timestamp" in data["data"]:
                                print(f"   ⏰ 时间: {data['data']['timestamp']}")
                        
                    else:
                        print(f"   ❌ 失败: {data.get('error', '未知错误')}")
                        
                except json.JSONDecodeError:
                    print("   ❌ 失败: 响应非JSON格式")
                    
            else:
                print(f"   ❌ 失败: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("   ⏰ 失败: 请求超时")
        except requests.exceptions.ConnectionError:
            print("   🔌 失败: 连接错误")
        except Exception as e:
            print(f"   ❌ 失败: {e}")
    
    # 测试交易端点
    print(f"\n📋 测试交易端点...")
    
    trading_tests = [
        {
            "name": "买入交易",
            "url": f"{base_url}/api/trading/buy",
            "method": "POST",
            "data": {"code": "000001", "quantity": 100, "price": 13.50}
        },
        {
            "name": "卖出交易", 
            "url": f"{base_url}/api/trading/sell",
            "method": "POST",
            "data": {"code": "000001", "quantity": 100, "price": 13.80}
        }
    ]
    
    for test in trading_tests:
        print(f"\n📋 测试: {test['name']}")
        
        try:
            response = requests.post(
                test['url'],
                json=test['data'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success"):
                        print("   ✅ 通过: 交易请求成功")
                        passed += 1
                        if "data" in data and "order_id" in data["data"]:
                            print(f"   📝 订单ID: {data['data']['order_id']}")
                    else:
                        print(f"   ❌ 失败: {data.get('error', '未知错误')}")
                except json.JSONDecodeError:
                    print("   ❌ 失败: 响应非JSON格式")
            else:
                print(f"   ❌ 失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 失败: {e}")
    
    total += len(trading_tests)
    
    # 测试结果
    print(f"\n{'='*50}")
    print(f"🎯 测试完成")
    print(f"📊 结果: {passed}/{total} 通过")
    print(f"📈 通过率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有端点测试通过!Worker完全正常!")
    elif passed >= total * 0.8:
        print("✅ 大部分端点正常,系统基本可用")
    else:
        print("⚠️ 多个端点失败,需要进一步修复")
    
    return passed, total

if __name__ == "__main__":
    test_all_endpoints()
