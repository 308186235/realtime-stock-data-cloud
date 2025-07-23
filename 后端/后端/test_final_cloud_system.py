#!/usr/bin/env python3
"""
测试最终云端系统
"""

import requests
import json
import time

def test_cloud_agent_system():
    """测试云端Agent系统"""
    base_url = "https://api.aigupiao.me"
    
    print("🚀 测试云端Agent系统")
    print("=" * 50)
    print(f"🎯 云端API: {base_url}")
    print("=" * 50)
    
    # 测试端点
    test_cases = [
        {
            "name": "系统状态",
            "method": "GET",
            "url": f"{base_url}/",
            "expected": "success"
        },
        {
            "name": "健康检查",
            "method": "GET", 
            "url": f"{base_url}/health",
            "expected": "healthy"
        },
        {
            "name": "Agent分析",
            "method": "GET",
            "url": f"{base_url}/api/agent-analysis",
            "expected": "analysis_data"
        },
        {
            "name": "账户余额",
            "method": "GET",
            "url": f"{base_url}/api/account-balance",
            "expected": "balance_data"
        },
        {
            "name": "账户持仓",
            "method": "GET",
            "url": f"{base_url}/api/account-positions",
            "expected": "positions_data"
        },
        {
            "name": "市场数据",
            "method": "GET",
            "url": f"{base_url}/api/market-data",
            "expected": "market_data"
        },
        {
            "name": "买入交易",
            "method": "POST",
            "url": f"{base_url}/api/trading/buy",
            "data": {"code": "000001", "quantity": 100, "price": 13.50},
            "expected": "order_data"
        },
        {
            "name": "卖出交易",
            "method": "POST",
            "url": f"{base_url}/api/trading/sell",
            "data": {"code": "000001", "quantity": 100, "price": 13.80},
            "expected": "order_data"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📋 测试 {i}/{total}: {test['name']}")
        
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=10)
            else:
                response = requests.post(
                    test['url'], 
                    json=test.get('data', {}),
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if data.get("success"):
                        # 验证特定字段
                        if test['expected'] == "success":
                            print("✅ 通过: 系统正常运行")
                        elif test['expected'] == "healthy":
                            if "status" in data.get("data", {}):
                                print("✅ 通过: 健康检查正常")
                            else:
                                print("⚠️ 警告: 缺少状态字段")
                        elif test['expected'] == "analysis_data":
                            if "market_sentiment" in data.get("data", {}):
                                print("✅ 通过: Agent分析数据完整")
                            else:
                                print("⚠️ 警告: 分析数据不完整")
                        elif test['expected'] == "balance_data":
                            if "balance" in data.get("data", {}):
                                print("✅ 通过: 余额数据正常")
                            else:
                                print("⚠️ 警告: 余额数据缺失")
                        elif test['expected'] == "positions_data":
                            if "positions" in data.get("data", {}):
                                print("✅ 通过: 持仓数据正常")
                            else:
                                print("⚠️ 警告: 持仓数据缺失")
                        elif test['expected'] == "market_data":
                            if "market_status" in data.get("data", {}):
                                print("✅ 通过: 市场数据正常")
                            else:
                                print("⚠️ 警告: 市场数据缺失")
                        elif test['expected'] == "order_data":
                            if "order_id" in data.get("data", {}):
                                print("✅ 通过: 交易订单创建成功")
                            else:
                                print("⚠️ 警告: 订单数据缺失")
                        
                        passed += 1
                        
                    else:
                        print(f"❌ 失败: success字段为false")
                        print(f"   错误: {data.get('error', '未知错误')}")
                        
                except json.JSONDecodeError:
                    print("❌ 失败: 响应非JSON格式")
                    print(f"   内容: {response.text[:100]}...")
                    
            else:
                print(f"❌ 失败: HTTP {response.status_code}")
                print(f"   响应: {response.text[:100]}...")
                
        except requests.exceptions.Timeout:
            print("⏰ 失败: 请求超时")
        except requests.exceptions.ConnectionError:
            print("🔌 失败: 连接错误")
        except Exception as e:
            print(f"❌ 失败: {e}")
    
    # 测试结果
    print(f"\n{'='*50}")
    print(f"🎯 测试完成")
    print(f"📊 结果: {passed}/{total} 通过")
    print(f"📈 通过率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过!云端Agent系统运行正常!")
    elif passed >= total * 0.8:
        print("✅ 大部分测试通过,系统基本正常")
    else:
        print("⚠️ 多个测试失败,需要进一步检查")
    
    return passed, total

if __name__ == "__main__":
    test_cloud_agent_system()
