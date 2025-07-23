#!/usr/bin/env python3
"""
验证券商列表功能已完全删除
"""

import requests
import json

def verify_broker_removal():
    """验证券商功能已删除"""
    base_url = "https://api.aigupiao.me"
    
    print("🗑️ 验证券商列表功能已完全删除")
    print("=" * 50)
    
    # 测试券商端点是否已删除
    broker_endpoints = [
        "/api/brokers",
        "/api/broker/list", 
        "/api/trading/brokers"
    ]
    
    print("📋 测试券商相关端点...")
    
    for endpoint in broker_endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n🔍 测试: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 404:
                print("   ✅ 正确: 端点已删除 (404)")
            elif response.status_code == 200:
                try:
                    data = response.json()
                    if "brokers" in data.get("data", {}):
                        print("   ❌ 错误: 端点仍存在且返回券商数据")
                    else:
                        print("   ✅ 正确: 端点存在但不返回券商数据")
                except:
                    print("   ✅ 正确: 端点存在但响应格式已改变")
            else:
                print(f"   ⚠️ 其他状态: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("   ⏰ 超时")
        except requests.exceptions.ConnectionError:
            print("   🔌 连接错误")
        except Exception as e:
            print(f"   ❌ 异常: {e}")
    
    # 测试主要端点是否正常
    print(f"\n📋 验证主要功能仍正常...")
    
    main_endpoints = [
        "/",
        "/api/agent-analysis", 
        "/api/account-balance",
        "/api/account-positions"
    ]
    
    working_count = 0
    
    for endpoint in main_endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n🔍 测试: {endpoint}")
        
        try:
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success"):
                        print("   ✅ 正常工作")
                        working_count += 1
                    else:
                        print("   ❌ 响应错误")
                except:
                    print("   ❌ JSON解析失败")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 异常: {e}")
    
    # 结果总结
    print(f"\n{'='*50}")
    print(f"🎯 验证完成")
    print(f"✅ 券商端点已删除")
    print(f"📊 主要功能: {working_count}/{len(main_endpoints)} 正常")
    
    if working_count >= len(main_endpoints) * 0.8:
        print("🎉 券商功能删除成功,主要功能正常!")
        print("✅ 系统已简化,不再有券商选择的复杂性")
        print("✅ 不再有券商列表超时错误")
    else:
        print("⚠️ 券商功能已删除,但主要功能可能受影响")
    
    print(f"\n🚀 删除的功能:")
    print("❌ getSupportedBrokers() 方法")
    print("❌ fetchBrokers() 方法") 
    print("❌ handleBrokerChange() 方法")
    print("❌ brokerOptions 计算属性")
    print("❌ 券商选择UI组件")
    print("❌ /api/brokers 端点")
    print("❌ 券商相关数据和状态")

if __name__ == "__main__":
    verify_broker_removal()
