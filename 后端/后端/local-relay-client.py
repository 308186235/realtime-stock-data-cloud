#!/usr/bin/env python3
"""
本地中转客户端 - 连接本地交易软件和云端中转服务
运行在您的本地电脑上
"""

import asyncio
import websockets
import json
import requests
import time
from datetime import datetime

class LocalRelayClient:
    def __init__(self):
        self.ws_url = "wss://relay.aigupiao.me/ws/local-client"  # 云端中转服务WebSocket
        self.local_api_base = "http://localhost:8000"  # 您的本地交易软件API
        self.websocket = None
        self.running = False
        
    async def connect_to_cloud(self):
        """连接到云端中转服务"""
        try:
            print(f"🔗 连接云端中转服务: {self.ws_url}")
            self.websocket = await websockets.connect(self.ws_url)
            print("✅ 成功连接到云端中转服务")
            return True
        except Exception as e:
            print(f"❌ 连接云端中转服务失败: {e}")
            return False
    
    def call_local_api(self, endpoint, method='GET', data=None):
        """调用本地交易软件API"""
        try:
            url = f"{self.local_api_base}{endpoint}"
            print(f"📡 调用本地API: {method} {url}")
            
            if method == 'GET':
                response = requests.get(url, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=10)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 本地API调用成功")
                return result
            else:
                print(f"❌ 本地API调用失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 本地API调用异常: {e}")
            return None
    
    async def handle_cloud_message(self, message_str):
        """处理来自云端的消息"""
        try:
            message = json.loads(message_str)
            request_type = message.get('type')
            request_id = message.get('id')
            
            print(f"📨 收到云端请求: {request_type} (ID: {request_id})")
            
            response_data = None
            
            if request_type == 'get_positions':
                # 获取持仓信息
                local_data = self.call_local_api('/api/positions')
                if local_data:
                    response_data = {
                        'id': request_id,
                        'type': 'positions',
                        'data': local_data,
                        'timestamp': datetime.now().isoformat()
                    }
            
            elif request_type == 'get_balance':
                # 获取账户余额
                local_data = self.call_local_api('/api/balance')
                if local_data:
                    response_data = {
                        'id': request_id,
                        'type': 'balance',
                        'data': local_data,
                        'timestamp': datetime.now().isoformat()
                    }
            
            elif request_type == 'execute_buy':
                # 执行买入
                trade_data = message.get('data', {})
                local_result = self.call_local_api('/api/buy', 'POST', trade_data)
                if local_result:
                    response_data = {
                        'id': request_id,
                        'type': 'buy_result',
                        'data': local_result,
                        'timestamp': datetime.now().isoformat()
                    }
            
            elif request_type == 'execute_sell':
                # 执行卖出
                trade_data = message.get('data', {})
                local_result = self.call_local_api('/api/sell', 'POST', trade_data)
                if local_result:
                    response_data = {
                        'id': request_id,
                        'type': 'sell_result',
                        'data': local_result,
                        'timestamp': datetime.now().isoformat()
                    }
            
            # 发送响应到云端
            if response_data:
                await self.websocket.send(json.dumps(response_data))
                print(f"📤 已发送响应到云端: {request_type}")
            else:
                print(f"⚠️ 无法处理请求: {request_type}")
                
        except Exception as e:
            print(f"❌ 处理云端消息失败: {e}")
    
    async def send_periodic_data(self):
        """定期发送数据到云端 (可选)"""
        while self.running:
            try:
                # 每30秒发送一次最新数据
                await asyncio.sleep(30)
                
                if not self.websocket:
                    continue
                
                # 获取并发送持仓数据
                positions_data = self.call_local_api('/api/positions')
                if positions_data:
                    message = {
                        'type': 'positions',
                        'data': positions_data,
                        'timestamp': datetime.now().isoformat(),
                        'auto_update': True
                    }
                    await self.websocket.send(json.dumps(message))
                    print("📤 自动发送持仓数据到云端")
                
                # 获取并发送余额数据
                balance_data = self.call_local_api('/api/balance')
                if balance_data:
                    message = {
                        'type': 'balance',
                        'data': balance_data,
                        'timestamp': datetime.now().isoformat(),
                        'auto_update': True
                    }
                    await self.websocket.send(json.dumps(message))
                    print("📤 自动发送余额数据到云端")
                    
            except Exception as e:
                print(f"❌ 定期发送数据失败: {e}")
    
    async def run(self):
        """运行本地中转客户端"""
        print("🚀 启动本地中转客户端")
        print(f"💻 本地API: {self.local_api_base}")
        print(f"☁️ 云端中转: {self.ws_url}")
        print("=" * 50)
        
        while True:
            try:
                # 连接到云端中转服务
                if await self.connect_to_cloud():
                    self.running = True
                    
                    # 启动定期数据发送任务
                    periodic_task = asyncio.create_task(self.send_periodic_data())
                    
                    # 监听云端消息
                    async for message in self.websocket:
                        await self.handle_cloud_message(message)
                        
                else:
                    print("⏰ 5秒后重试连接...")
                    await asyncio.sleep(5)
                    
            except websockets.exceptions.ConnectionClosed:
                print("🔌 与云端中转服务连接断开")
                self.running = False
                if 'periodic_task' in locals():
                    periodic_task.cancel()
                    
            except Exception as e:
                print(f"❌ 运行异常: {e}")
                self.running = False
                
            print("⏰ 10秒后重新连接...")
            await asyncio.sleep(10)

def main():
    """主函数"""
    print("🏠 本地中转客户端")
    print("连接本地交易软件和云端中转服务")
    print("=" * 50)
    
    # 检查本地交易软件是否运行
    try:
        response = requests.get("http://localhost:8000/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ 本地交易软件API正常运行")
        else:
            print("⚠️ 本地交易软件API响应异常")
    except:
        print("❌ 本地交易软件API未运行 (http://localhost:8000)")
        print("💡 请先启动您的本地交易软件API服务")
        return
    
    # 启动中转客户端
    client = LocalRelayClient()
    asyncio.run(client.run())

if __name__ == "__main__":
    main()
