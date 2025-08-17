#!/usr/bin/env python3
"""
测试WebSocket连接
"""

import asyncio
import websockets
import json
import time

async def test_websocket_connection():
    """测试WebSocket连接"""
    print("🔧 测试WebSocket连接")
    print("=" * 50)
    
    websocket_url = "wss://api.aigupiao.me/ws/local-trading"
    
    try:
        print(f"🔗 连接到: {websocket_url}")
        
        async with websockets.connect(websocket_url) as websocket:
            print("✅ WebSocket连接成功!")
            
            # 发送注册消息
            register_message = {
                "type": "register",
                "service": "local_trading",
                "version": "1.0.0",
                "timestamp": time.time()
            }
            
            await websocket.send(json.dumps(register_message))
            print("📤 发送注册消息")
            
            # 等待响应
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                print(f"📥 收到响应: {response}")
            except asyncio.TimeoutError:
                print("⏰ 等待响应超时")
            
            # 发送测试数据
            test_data = {
                "type": "positions",
                "data": {
                    "positions": [
                        {
                            "stock_code": "000001",
                            "stock_name": "平安银行",
                            "quantity": 1000,
                            "current_price": 13.50,
                            "market_value": 13500
                        }
                    ],
                    "summary": {
                        "total_market_value": 13500
                    }
                },
                "timestamp": time.time()
            }
            
            await websocket.send(json.dumps(test_data))
            print("📤 发送测试持仓数据")
            
            # 等待确认
            try:
                ack = await asyncio.wait_for(websocket.recv(), timeout=10)
                print(f"📥 收到确认: {ack}")
            except asyncio.TimeoutError:
                print("⏰ 等待确认超时")
            
            # 发送余额数据
            balance_data = {
                "type": "balance",
                "data": {
                    "balance": {
                        "total_assets": 125680.5,
                        "available_cash": 23450.8,
                        "market_value": 102229.7,
                        "frozen_amount": 0
                    }
                },
                "timestamp": time.time()
            }
            
            await websocket.send(json.dumps(balance_data))
            print("📤 发送测试余额数据")
            
            # 等待确认
            try:
                ack = await asyncio.wait_for(websocket.recv(), timeout=10)
                print(f"📥 收到确认: {ack}")
            except asyncio.TimeoutError:
                print("⏰ 等待确认超时")
            
            print("✅ WebSocket测试完成")
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ WebSocket连接失败: HTTP {e.status_code}")
        if e.status_code == 426:
            print("   💡 可能需要正确的WebSocket升级头")
    except Exception as e:
        print(f"❌ WebSocket连接异常: {e}")

async def test_websocket_status():
    """测试WebSocket状态API"""
    print("\n🔧 测试WebSocket状态API")
    print("-" * 30)
    
    import requests
    
    try:
        response = requests.get("https://api.aigupiao.me/api/websocket/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ WebSocket状态API正常")
            print(f"📊 状态: {data}")
        else:
            print(f"❌ WebSocket状态API错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ WebSocket状态API异常: {e}")

async def main():
    """主函数"""
    await test_websocket_status()
    await test_websocket_connection()

if __name__ == "__main__":
    asyncio.run(main())
