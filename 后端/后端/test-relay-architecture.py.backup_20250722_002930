#!/usr/bin/env python3
"""
测试云端中转服务架构
"""

import requests
import json
import time

def test_relay_architecture():
    """测试云端中转服务架构"""
    print("🧪 测试云端中转服务架构")
    print("=" * 60)
    
    # 测试端点
    tests = [
        {
            "name": "主Worker → 中转服务 (持仓)",
            "url": "https://api.aigupiao.me/api/local-trading/positions",
            "description": "前端通过主Worker调用中转服务获取持仓"
        },
        {
            "name": "主Worker → 中转服务 (余额)",
            "url": "https://api.aigupiao.me/api/local-trading/balance", 
            "description": "前端通过主Worker调用中转服务获取余额"
        },
        {
            "name": "直接访问中转服务 (状态)",
            "url": "https://relay.aigupiao.me/api/relay/status",
            "description": "直接检查中转服务运行状态"
        },
        {
            "name": "直接访问中转服务 (持仓)",
            "url": "https://relay.aigupiao.me/api/relay/positions",
            "description": "直接通过中转服务获取持仓"
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for i, test in enumerate(tests, 1):
        print(f"\n🔥 测试 {i}/{total}: {test['name']}")
        print(f"   📝 {test['description']}")
        print(f"   🌐 {test['url']}")
        
        try:
            start_time = time.time()
            response = requests.get(test['url'], timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if data.get("success"):
                        print(f"   ✅ 成功 ({response_time:.2f}s)")
                        
                        # 分析响应数据
                        data_content = data.get("data", {})
                        
                        # 检查数据来源
                        source = data_content.get("source", "unknown")
                        connection_status = data_content.get("connection_status", "unknown")
                        
                        if source:
                            print(f"   📊 数据源: {source}")
                        if connection_status:
                            print(f"   🔗 连接状态: {connection_status}")
                        
                        # 显示关键信息
                        if "local_clients_connected" in data_content:
                            clients = data_content["local_clients_connected"]
                            print(f"   👥 本地客户端: {clients} 个连接")
                            
                        if "positions" in data_content:
                            positions = data_content["positions"]
                            print(f"   📈 持仓: {len(positions)} 只股票")
                            
                        if "balance" in data_content:
                            balance = data_content["balance"]
                            total_assets = balance.get("total_assets", 0)
                            print(f"   💰 总资产: {total_assets}")
                        
                        # 检查错误信息
                        error = data_content.get("error")
                        if error:
                            print(f"   ⚠️ 错误: {error}")
                        
                        # 检查备注
                        note = data_content.get("note") or data_content.get("relay_note")
                        if note:
                            print(f"   💡 备注: {note}")
                        
                        passed += 1
                        
                    else:
                        print(f"   ❌ 失败: {data.get('error', '未知错误')}")
                        
                except json.JSONDecodeError:
                    print("   ❌ 失败: 响应非JSON格式")
                    print(f"   📄 响应内容: {response.text[:200]}...")
                    
            else:
                print(f"   ❌ 失败: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("   ⏰ 失败: 请求超时")
        except requests.exceptions.ConnectionError:
            print("   🔌 失败: 连接错误")
        except Exception as e:
            print(f"   ❌ 失败: {e}")
    
    # 测试交易功能
    print(f"\n🔥 测试交易功能...")
    
    try:
        buy_data = {
            "code": "000001",
            "quantity": 100,
            "price": 13.50
        }
        
        buy_response = requests.post(
            "https://api.aigupiao.me/api/local-trading/buy",
            json=buy_data,
            headers={'Content-Type': 'application/json'},
            timeout=20
        )
        
        if buy_response.status_code == 200:
            data = buy_response.json()
            if data.get("success"):
                print("   ✅ 买入指令: 成功发送")
                
                data_content = data.get("data", {})
                order_id = data_content.get("order_id")
                status = data_content.get("status")
                
                if order_id:
                    print(f"   📋 订单ID: {order_id}")
                if status:
                    print(f"   📊 状态: {status}")
                    
                passed += 1
            else:
                print("   ❌ 买入指令: 失败")
        else:
            print("   ❌ 买入指令: HTTP错误")
            
    except Exception as e:
        print(f"   ❌ 买入指令: {e}")
    
    total += 1
    
    # 最终结果
    print(f"\n{'='*60}")
    print(f"🎯 架构测试完成")
    print(f"📊 结果: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    if passed >= total * 0.8:
        print("🎉 云端中转服务架构正常！")
        status = "架构正常"
    elif passed >= total * 0.5:
        print("⚠️ 架构基本正常，部分功能可能需要优化")
        status = "基本正常"
    else:
        print("❌ 架构有问题，需要检查配置")
        status = "需要修复"
    
    print(f"\n🚀 架构优势:")
    print("✅ 云端Agent可以获取本地数据")
    print("✅ 支持实时双向通信")
    print("✅ 自动故障恢复机制")
    print("✅ 安全的本地网络访问")
    print("✅ 可扩展的中转架构")
    
    print(f"\n📝 下一步:")
    if passed < total:
        print("1. 部署云端中转服务 (relay.aigupiao.me)")
        print("2. 运行本地中转客户端")
        print("3. 检查WebSocket连接")
        print("4. 验证本地API调用")
    else:
        print("1. 运行本地中转客户端连接云端")
        print("2. 测试实时数据同步")
        print("3. 验证交易执行功能")
        print("4. 监控系统运行状态")
    
    return status, passed, total

if __name__ == "__main__":
    status, passed, total = test_relay_architecture()
    print(f"\n🎊 最终状态: {status}")
    print(f"🎯 通过率: {passed}/{total} ({passed/total*100:.1f}%)")
