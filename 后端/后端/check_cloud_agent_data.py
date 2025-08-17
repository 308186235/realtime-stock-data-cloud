#!/usr/bin/env python3
"""
检查云端Agent是否接收到本地数据
"""

import requests
import json
import time

def check_cloud_agent_data():
    """检查云端Agent是否接收到本地数据"""
    print("🔍 检查云端Agent是否接收到本地数据")
    print("=" * 60)
    
    # 1. 检查WebSocket状态
    print("\n📊 1. 检查WebSocket状态")
    print("-" * 40)
    
    try:
        response = requests.get("https://api.aigupiao.me/api/websocket/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ WebSocket状态API正常")
            
            ws_data = data.get("data", {})
            print(f"📊 WebSocket状态: {ws_data.get('websocket_status')}")
            print(f"🔗 连接的本地客户端: {ws_data.get('local_clients_connected', 0)}")
            print(f"📋 可用数据类型: {ws_data.get('latest_data_types', [])}")
            print(f"🕐 最后数据更新: {ws_data.get('last_data_update')}")
            
            if ws_data.get('local_clients_connected', 0) > 0:
                print("🎉 本地客户端已连接!")
            else:
                print("⚠️ 没有本地客户端连接")
                
            if 'positions' in ws_data.get('latest_data_types', []):
                print("🎉 云端已接收到持仓数据!")
            else:
                print("⚠️ 云端未接收到持仓数据")
                
            if 'balance' in ws_data.get('latest_data_types', []):
                print("🎉 云端已接收到余额数据!")
            else:
                print("⚠️ 云端未接收到余额数据")
        else:
            print(f"❌ WebSocket状态API错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ WebSocket状态检查异常: {e}")
    
    # 2. 检查持仓数据
    print(f"\n📊 2. 检查持仓数据")
    print("-" * 40)
    
    try:
        response = requests.get("https://api.aigupiao.me/api/local-trading/positions", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 持仓API调用成功")
            
            if data.get("success"):
                positions_data = data.get("data", {})
                
                # 检查数据源
                source = positions_data.get("source", "unknown")
                print(f"📊 数据源: {source}")
                
                # 检查连接状态
                connection_status = positions_data.get("connection_status")
                if connection_status:
                    print(f"🔗 连接状态: {connection_status}")
                
                # 检查WebSocket信息
                websocket_note = positions_data.get("websocket_note")
                if websocket_note:
                    print(f"🌐 WebSocket备注: {websocket_note}")
                
                connected_clients = positions_data.get("connected_clients")
                if connected_clients is not None:
                    print(f"👥 连接的客户端: {connected_clients}")
                
                # 检查持仓信息
                positions = positions_data.get("positions", [])
                print(f"📈 持仓数量: {len(positions)}")
                
                if positions:
                    for i, pos in enumerate(positions[:3]):  # 显示前3个
                        print(f"   📊 {i+1}. {pos.get('stock_name', 'N/A')} ({pos.get('stock_code', 'N/A')})")
                        print(f"      数量: {pos.get('quantity', 0)}, 价格: {pos.get('current_price', 0)}")
                
                # 检查汇总信息
                summary = positions_data.get("summary", {})
                if summary:
                    print(f"💰 总市值: {summary.get('total_market_value', 0)}")
                    print(f"💹 总盈亏: {summary.get('total_profit_loss', 0)}")
                
                # 检查最后更新时间
                last_update = positions_data.get("last_update")
                if last_update:
                    print(f"🕐 最后更新: {last_update}")
                
                # 判断数据来源
                if source == "local_computer_via_websocket":
                    print("🎉 成功!云端Agent通过WebSocket接收到本地真实数据!")
                elif source == "backup_data":
                    print("⚠️ 使用备用数据,本地数据未传输成功")
                else:
                    print(f"❓ 未知数据源: {source}")
                    
            else:
                print(f"❌ 持仓API失败: {data.get('error', '未知错误')}")
        else:
            print(f"❌ 持仓API HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 持仓数据检查异常: {e}")
    
    # 3. 检查余额数据
    print(f"\n📊 3. 检查余额数据")
    print("-" * 40)
    
    try:
        response = requests.get("https://api.aigupiao.me/api/local-trading/balance", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 余额API调用成功")
            
            if data.get("success"):
                balance_data = data.get("data", {})
                
                # 检查数据源
                source = balance_data.get("source", "unknown")
                print(f"📊 数据源: {source}")
                
                # 检查余额信息
                balance = balance_data.get("balance", {})
                if balance:
                    print(f"💰 总资产: {balance.get('total_assets', 0)}")
                    print(f"💵 可用资金: {balance.get('available_cash', 0)}")
                    print(f"📈 市值: {balance.get('market_value', 0)}")
                    print(f"🔒 冻结金额: {balance.get('frozen_amount', 0)}")
                
                # 检查最后更新时间
                last_update = balance_data.get("last_update")
                if last_update:
                    print(f"🕐 最后更新: {last_update}")
                
                # 判断数据来源
                if source == "local_computer_via_websocket":
                    print("🎉 成功!云端Agent通过WebSocket接收到本地真实余额!")
                elif source == "backup_data":
                    print("⚠️ 使用备用数据,本地余额未传输成功")
                else:
                    print(f"❓ 未知数据源: {source}")
                    
            else:
                print(f"❌ 余额API失败: {data.get('error', '未知错误')}")
        else:
            print(f"❌ 余额API HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 余额数据检查异常: {e}")
    
    # 4. 总结
    print(f"\n{'='*60}")
    print(f"🎯 数据传输状态总结")
    print(f"{'='*60}")
    
    # 再次检查WebSocket状态进行总结
    try:
        response = requests.get("https://api.aigupiao.me/api/websocket/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            ws_data = data.get("data", {})
            
            clients = ws_data.get('local_clients_connected', 0)
            data_types = ws_data.get('latest_data_types', [])
            
            if clients > 0:
                print("✅ 本地客户端已连接到云端")
            else:
                print("❌ 本地客户端未连接到云端")
            
            if 'positions' in data_types and 'balance' in data_types:
                print("✅ 云端已接收到完整的本地数据")
            elif 'positions' in data_types or 'balance' in data_types:
                print("⚠️ 云端部分接收到本地数据")
            else:
                print("❌ 云端未接收到本地数据")
                
            print(f"📊 数据类型: {data_types}")
            
    except:
        print("❌ 无法获取最终状态")

if __name__ == "__main__":
    check_cloud_agent_data()
