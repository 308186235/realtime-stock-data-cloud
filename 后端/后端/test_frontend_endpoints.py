#!/usr/bin/env python3
"""
测试前端需要的所有API端点
"""

import requests
import json
import time

def test_frontend_endpoints():
    """测试前端调用的所有端点"""
    base_url = "https://api.aigupiao.me"
    
    # 前端实际调用的端点
    endpoints = [
        # 基础端点
        {"path": "/", "name": "根路径", "critical": True},
        {"path": "/health", "name": "健康检查", "critical": True},
        
        # Agent相关
        {"path": "/api/agent-analysis", "name": "Agent分析", "critical": True},
        {"path": "/api/agent/status", "name": "Agent状态", "critical": False},
        
        # 账户相关
        {"path": "/api/account-balance", "name": "账户余额", "critical": True},
        {"path": "/api/account-positions", "name": "账户持仓", "critical": True},
        
        # 市场相关
        {"path": "/api/market-data", "name": "市场数据", "critical": True},
        {"path": "/api/market/status", "name": "市场状态", "critical": False},
        
        # 交易相关
        {"path": "/api/brokers", "name": "券商列表", "critical": True},
        {"path": "/api/realtime/quotes", "name": "实时行情", "critical": True},
    ]
    
    print("🧪 测试前端需要的API端点")
    print("=" * 60)
    print(f"🎯 基础URL: {base_url}")
    print("=" * 60)
    
    passed = 0
    critical_passed = 0
    total = len(endpoints)
    critical_total = sum(1 for ep in endpoints if ep["critical"])
    
    for i, endpoint in enumerate(endpoints, 1):
        path = endpoint["path"]
        name = endpoint["name"]
        critical = endpoint["critical"]
        url = f"{base_url}{path}"
        
        status_icon = "🔥" if critical else "📋"
        print(f"\n{status_icon} 测试 {i}/{total}: {name}")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if data.get("success"):
                        print("   ✅ 通过: 响应正常")
                        passed += 1
                        if critical:
                            critical_passed += 1
                        
                        # 显示关键信息
                        if "data" in data:
                            data_info = data["data"]
                            if isinstance(data_info, dict):
                                if "balance" in data_info:
                                    print(f"   💰 余额: {data_info['balance'].get('total_assets', 'N/A')}")
                                elif "positions" in data_info:
                                    positions = data_info["positions"]
                                    print(f"   📊 持仓: {len(positions) if isinstance(positions, list) else 'N/A'} 只")
                                elif "market_sentiment" in data_info:
                                    print(f"   📈 市场情绪: {data_info['market_sentiment']}")
                                elif "brokers" in data_info:
                                    brokers = data_info["brokers"]
                                    print(f"   🏦 券商: {len(brokers) if isinstance(brokers, list) else 'N/A'} 家")
                        
                    else:
                        print(f"   ❌ 失败: {data.get('error', '未知错误')}")
                        
                except json.JSONDecodeError:
                    print("   ❌ 失败: 响应非JSON格式")
                    print(f"   内容: {response.text[:100]}...")
                    
            else:
                print(f"   ❌ 失败: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("   ⏰ 失败: 请求超时")
        except requests.exceptions.ConnectionError:
            print("   🔌 失败: 连接错误")
        except Exception as e:
            print(f"   ❌ 失败: {e}")
    
    # 测试交易端点
    print(f"\n🔥 测试交易端点...")
    
    trading_tests = [
        {
            "name": "买入交易",
            "url": f"{base_url}/api/trading/buy",
            "data": {"code": "000001", "quantity": 100, "price": 13.50},
            "critical": True
        },
        {
            "name": "卖出交易", 
            "url": f"{base_url}/api/trading/sell",
            "data": {"code": "000001", "quantity": 100, "price": 13.80},
            "critical": True
        }
    ]
    
    for test in trading_tests:
        print(f"\n🔥 测试: {test['name']}")
        
        try:
            response = requests.post(
                test['url'],
                json=test['data'],
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success"):
                        print("   ✅ 通过: 交易请求成功")
                        passed += 1
                        critical_passed += 1
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
    critical_total += len(trading_tests)
    
    # 测试结果
    print(f"\n{'='*60}")
    print(f"🎯 测试完成")
    print(f"📊 总体结果: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    print(f"🔥 关键功能: {critical_passed}/{critical_total} 通过 ({critical_passed/critical_total*100:.1f}%)")
    
    if critical_passed == critical_total:
        print("🎉 所有关键功能正常!前端可以正常使用!")
    elif critical_passed >= critical_total * 0.8:
        print("✅ 大部分关键功能正常,系统基本可用")
    else:
        print("⚠️ 多个关键功能失败,需要进一步修复")
    
    return passed, total, critical_passed, critical_total

if __name__ == "__main__":
    test_frontend_endpoints()
