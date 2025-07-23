#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
混合架构 - 云端API + 本地交易代理
"""

import asyncio
import websockets
import json
import requests
from datetime import datetime
import logging

class LocalTradingAgent:
    """本地交易代理 - 负责与交易软件交互"""
    
    def __init__(self, cloud_api_url, websocket_url):
        self.cloud_api_url = cloud_api_url
        self.websocket_url = websocket_url
        self.websocket = None
        self.running = False
        
        # 导入本地交易模块
        from trader_buy_sell import buy_stock, sell_stock
        from trader_export import export_holdings, export_trades
        from trader_core import get_account_balance
        
        self.buy_stock = buy_stock
        self.sell_stock = sell_stock
        self.export_holdings = export_holdings
        self.export_trades = export_trades
        self.get_account_balance = get_account_balance
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def connect_to_cloud(self):
        """连接到云端服务"""
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            self.logger.info(f"✅ 已连接到云端服务: {self.websocket_url}")
            
            # 发送注册消息
            register_msg = {
                "type": "register",
                "agent_type": "local_trading",
                "capabilities": [
                    "buy_stock",
                    "sell_stock", 
                    "export_data",
                    "get_balance"
                ],
                "timestamp": datetime.now().isoformat()
            }
            await self.websocket.send(json.dumps(register_msg))
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 连接云端服务失败: {e}")
            return False
    
    async def listen_for_commands(self):
        """监听云端命令"""
        try:
            async for message in self.websocket:
                try:
                    command = json.loads(message)
                    await self.handle_command(command)
                except json.JSONDecodeError:
                    self.logger.error(f"❌ 无效的JSON消息: {message}")
                except Exception as e:
                    self.logger.error(f"❌ 处理命令失败: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("⚠️ 与云端服务连接断开")
        except Exception as e:
            self.logger.error(f"❌ 监听命令失败: {e}")
    
    async def handle_command(self, command):
        """处理云端命令"""
        command_type = command.get("type")
        command_id = command.get("id")
        
        self.logger.info(f"📨 收到命令: {command_type}")
        
        try:
            result = None
            
            if command_type == "buy_stock":
                # 执行买入操作
                code = command["data"]["code"]
                price = command["data"]["price"]
                quantity = command["data"]["quantity"]
                result = self.buy_stock(code, price, quantity)
                
            elif command_type == "sell_stock":
                # 执行卖出操作
                code = command["data"]["code"]
                price = command["data"]["price"]
                quantity = command["data"]["quantity"]
                result = self.sell_stock(code, price, quantity)
                
            elif command_type == "export_holdings":
                # 导出持仓数据
                result = self.export_holdings()
                
            elif command_type == "export_trades":
                # 导出成交数据
                result = self.export_trades()
                
            elif command_type == "get_balance":
                # 获取账户余额
                result = self.get_account_balance()
                
            elif command_type == "ping":
                # 心跳检测
                result = {"status": "alive", "timestamp": datetime.now().isoformat()}
            
            # 发送执行结果回云端
            response = {
                "type": "command_result",
                "command_id": command_id,
                "success": result is not False,
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket.send(json.dumps(response))
            self.logger.info(f"✅ 命令执行完成: {command_type}")
            
        except Exception as e:
            # 发送错误信息
            error_response = {
                "type": "command_error",
                "command_id": command_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            await self.websocket.send(json.dumps(error_response))
            self.logger.error(f"❌ 命令执行失败: {e}")
    
    async def send_heartbeat(self):
        """发送心跳"""
        while self.running:
            try:
                if self.websocket:
                    heartbeat = {
                        "type": "heartbeat",
                        "timestamp": datetime.now().isoformat(),
                        "status": "running"
                    }
                    await self.websocket.send(json.dumps(heartbeat))
                    
                await asyncio.sleep(30)  # 每30秒发送一次心跳
                
            except Exception as e:
                self.logger.error(f"❌ 心跳发送失败: {e}")
                break
    
    async def run(self):
        """运行本地代理"""
        self.running = True
        self.logger.info("🚀 启动本地交易代理...")
        
        while self.running:
            try:
                # 连接到云端
                if await self.connect_to_cloud():
                    # 启动心跳任务
                    heartbeat_task = asyncio.create_task(self.send_heartbeat())
                    
                    # 监听命令
                    await self.listen_for_commands()
                    
                    # 取消心跳任务
                    heartbeat_task.cancel()
                
                # 连接断开,等待重连
                self.logger.info("⏳ 5秒后重新连接...")
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                self.logger.info("👋 用户中断,退出程序")
                break
            except Exception as e:
                self.logger.error(f"❌ 运行异常: {e}")
                await asyncio.sleep(5)
        
        self.running = False

class CloudAPIClient:
    """云端API客户端"""
    
    def __init__(self, api_url):
        self.api_url = api_url
    
    def send_trading_command(self, command_type, data):
        """发送交易命令到云端"""
        try:
            response = requests.post(
                f"{self.api_url}/api/trading/command",
                json={
                    "type": command_type,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                },
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def main():
    """主函数"""
    # 配置
    CLOUD_API_URL = "https://your-app.railway.app"  # 云端API地址
    WEBSOCKET_URL = "wss://your-app.railway.app/ws/trading"  # WebSocket地址
    
    # 创建本地代理
    agent = LocalTradingAgent(CLOUD_API_URL, WEBSOCKET_URL)
    
    # 运行
    asyncio.run(agent.run())

if __name__ == "__main__":
    main()
