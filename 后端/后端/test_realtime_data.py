#!/usr/bin/env python3
"""
测试实时数据接收
"""

import asyncio
import websockets
import json
import time

async def test_websocket_connection():
    """测试WebSocket连接"""
    print("🔍 测试实时数据接收...")
    print("=" * 50)
    
    try:
        # 连接到本地WebSocket服务器
        uri = "ws://localhost:8765"
        print(f"🔗 连接到: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功")
            
            # 发送ping测试
            await websocket.send(json.dumps({"type": "ping"}))
            print("📤 发送ping消息")
            
            # 接收消息
            message_count = 0
            start_time = time.time()
            
            print("\n📡 开始接收实时数据...")
            print("-" * 30)
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_count += 1
                    
                    if data.get('type') == 'welcome':
                        print(f"🎉 {data.get('message')}")
                        print(f"📊 服务器统计: {data.get('stats')}")
                    
                    elif data.get('type') == 'stock_data':
                        stock_info = data.get('data', {})
                        print(f"📈 股票数据: {stock_info.get('symbol')} "
                              f"价格:{stock_info.get('price')} "
                              f"涨跌:{stock_info.get('change_percent')}%")
                    
                    elif data.get('type') == 'pong':
                        print("🏓 收到pong响应")
                    
                    # 测试10秒或收到10条消息
                    if message_count >= 10 or (time.time() - start_time) > 10:
                        break
                        
                except json.JSONDecodeError:
                    print(f"❌ 消息解析失败: {message}")
                except Exception as e:
                    print(f"❌ 处理消息错误: {e}")
            
            print(f"\n📊 测试完成:")
            print(f"   - 接收消息数: {message_count}")
            print(f"   - 测试时长: {time.time() - start_time:.1f}秒")
            
            if message_count > 0:
                print("✅ 实时数据接收正常!")
            else:
                print("⚠️ 未接收到数据")
                
    except ConnectionRefusedError:
        print("❌ 连接被拒绝 - WebSocket服务器可能未运行")
    except Exception as e:
        print(f"❌ 连接失败: {e}")

async def test_data_parsing():
    """测试数据解析"""
    print("\n🧪 测试数据解析...")
    print("-" * 30)
    
    # 模拟茶股帮数据格式
    test_lines = [
        "000001|平安银行|12.34|2.5|1000000|",
        "600000|浦发银行|8.76|-1.2|800000|",
        "600519|贵州茅台|1680.50|0.8|50000|"
    ]
    
    for line in test_lines:
        parts = line.split('|')
        if len(parts) >= 5:
            stock_data = {
                'symbol': parts[0],
                'name': parts[1],
                'price': float(parts[2]) if parts[2] else 0,
                'change_percent': float(parts[3]) if parts[3] else 0,
                'volume': int(parts[4]) if parts[4] else 0
            }
            print(f"📈 {stock_data['symbol']} {stock_data['name']} "
                  f"¥{stock_data['price']} {stock_data['change_percent']:+.1f}%")

def check_server_status():
    """检查服务器状态"""
    print("\n🔍 检查服务器状态...")
    print("-" * 30)
    
    import subprocess
    import sys
    
    try:
        # 检查端口8765是否被占用
        result = subprocess.run(
            ["netstat", "-an"], 
            capture_output=True, 
            text=True, 
            shell=True
        )
        
        if ":8765" in result.stdout:
            print("✅ 端口8765正在使用中")
        else:
            print("❌ 端口8765未被占用")
            
    except Exception as e:
        print(f"⚠️ 无法检查端口状态: {e}")

async def main():
    """主函数"""
    print("🚀 实时数据接收测试")
    print("=" * 50)
    
    # 1. 检查服务器状态
    check_server_status()
    
    # 2. 测试数据解析
    await test_data_parsing()
    
    # 3. 测试WebSocket连接
    await test_websocket_connection()
    
    print("\n" + "=" * 50)
    print("🎯 测试完成")

if __name__ == "__main__":
    asyncio.run(main())
