#!/usr/bin/env python3
"""
最终云端系统测试
"""

import requests
import json
import time

def test_cloud_system():
    """测试云端系统"""
    base_url = "https://api.aigupiao.me"
    
    print("🚀 最终云端系统测试")
    print("=" * 50)
    print(f"🎯 云端API: {base_url}")
    print("=" * 50)
    
    # 基础测试
    basic_tests = [
        {
            "name": "系统状态",
            "url": f"{base_url}/",
            "method": "GET"
        },
        {
            "name": "Agent分析",
            "url": f"{base_url}/api/agent-analysis",
            "method": "GET"
        },
        {
            "name": "账户余额",
            "url": f"{base_url}/api/account-balance",
            "method": "GET"
        }
    ]
    
    passed = 0
    total = len(basic_tests)
    
    for i, test in enumerate(basic_tests, 1):
        print(f"\n📋 测试 {i}/{total}: {test['name']}")
        
        try:
            response = requests.get(test['url'], timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if data.get("success"):
                        print("✅ 通过: 响应正常")
                        
                        # 显示关键数据
                        if "message" in data:
                            print(f"   消息: {data['message']}")
                        
                        if "data" in data:
                            data_info = data["data"]
                            if isinstance(data_info, dict):
                                if "timestamp" in data_info:
                                    print(f"   时间: {data_info['timestamp']}")
                                if "market_sentiment" in data_info:
                                    print(f"   市场情绪: {data_info['market_sentiment']}")
                                if "balance" in data_info:
                                    balance = data_info["balance"]
                                    if "total_assets" in balance:
                                        print(f"   总资产: {balance['total_assets']}")
                        
                        passed += 1
                        
                    else:
                        print(f"❌ 失败: {data.get('error', '未知错误')}")
                        
                except json.JSONDecodeError:
                    print("❌ 失败: 响应非JSON格式")
                    print(f"   内容: {response.text[:100]}...")
                    
            else:
                print(f"❌ 失败: HTTP {response.status_code}")
                
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
        print("🎉 所有测试通过！云端系统运行正常！")
        print("\n✅ 前端现在可以正常连接云端API了！")
        print("✅ 不再需要本地服务器！")
        print("✅ 完全基于云端的Agent系统！")
    elif passed >= total * 0.8:
        print("✅ 大部分测试通过，系统基本正常")
    else:
        print("⚠️ 多个测试失败，需要进一步检查")
    
    return passed, total

if __name__ == "__main__":
    test_cloud_system()
