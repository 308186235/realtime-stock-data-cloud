#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地混合架构客户端
连接Render云端API，执行本地交易操作
"""

import asyncio
import websockets
import json
import requests
import time
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('local_agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LocalTradingClient:
    """本地交易客户端"""
    
    def __init__(self, render_url):
        self.render_url = render_url
        self.api_url = render_url
        self.ws_url = render_url.replace('https://', 'wss://') + '/ws'
        self.running = False
        
        # 导入本地交易模块
        try:
            from trader_buy_sell import buy_stock, sell_stock
            from trader_export import export_holdings, export_trades  
            from trader_core import get_account_balance
            
            self.buy_stock = buy_stock
            self.sell_stock = sell_stock
            self.export_holdings = export_holdings
            self.export_trades = export_trades
            self.get_account_balance = get_account_balance
            
            logger.info("✅ 本地交易模块加载成功")
        except Exception as e:
            logger.error(f"❌ 本地交易模块加载失败: {e}")
            logger.error("❌ 本地交易模块不可用，系统拒绝使用模拟交易")
            self._setup_real_only_functions()

    def _setup_real_only_functions(self):
        """设置真实交易函数 - 禁用模拟交易"""
        def require_real_trading(operation_name):
            def real_function(*args, **kwargs):
                error_msg = f"""
                ❌ 错误：{operation_name}操作需要真实交易接口

                请配置以下真实交易系统之一：
                1. working-trader-FIXED本地交易模块
                2. 券商API接口
                3. 第三方交易平台API

                系统拒绝执行模拟交易操作！
                """
                logger.error(error_msg)
                raise ValueError(error_msg)
            return real_function

        self.buy_stock = require_real_trading("买入")
        self.sell_stock = require_real_trading("卖出")
        self.export_holdings = require_real_trading("导出持仓")
        self.get_account_balance = require_real_trading("获取余额")
    
    async def connect_and_run(self):
        """连接并运行客户端"""
        self.running = True
        
        while self.running:
            try:
                logger.info(f"🔗 连接到Render服务: {self.ws_url}")
                
                # 检查服务是否可用
                if not await self._check_service_health():
                    logger.warning("⚠️ 服务健康检查失败，等待重试...")
                    await asyncio.sleep(30)
                    continue
                
                async with websockets.connect(
                    self.ws_url,
                    ping_interval=30,
                    ping_timeout=10
                ) as websocket:
                    
                    # 注册客户端
                    await self._register_client(websocket)
                    
                    # 开始心跳任务
                    heartbeat_task = asyncio.create_task(
                        self._send_heartbeat(websocket)
                    )
                    
                    # 监听消息
                    try:
                        async for message in websocket:
                            await self._handle_message(websocket, message)
                    finally:
                        heartbeat_task.cancel()
                        
            except websockets.exceptions.ConnectionClosed:
                logger.warning("⚠️ 连接断开，准备重连...")
            except Exception as e:
                logger.error(f"❌ 连接异常: {e}")
            
            if self.running:
                logger.info("⏳ 10秒后重新连接...")
                await asyncio.sleep(10)
    
    async def _check_service_health(self):
        """检查服务健康状态"""
        try:
            response = requests.get(f"{self.api_url}/api/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    async def _register_client(self, websocket):
        """注册客户端"""
        register_msg = {
            "type": "register",
            "client_type": "local_trading_agent",
            "capabilities": ["buy", "sell", "export", "balance"],
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(register_msg))
        logger.info("✅ 已注册到云端服务")
    
    async def _send_heartbeat(self, websocket):
        """发送心跳"""
        while True:
            try:
                heartbeat = {
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat(),
                    "status": "running"
                }
                await websocket.send(json.dumps(heartbeat))
                await asyncio.sleep(30)
            except:
                break
    
    async def _handle_message(self, websocket, message):
        """处理消息"""
        try:
            data = json.loads(message)
            command_type = data.get("type")
            command_id = data.get("id")
            
            logger.info(f"📨 收到命令: {command_type}")
            
            result = None
            
            if command_type == "buy_stock":
                params = data["data"]
                result = self.buy_stock(
                    params["code"], 
                    params["price"], 
                    params["quantity"]
                )
            elif command_type == "sell_stock":
                params = data["data"]
                result = self.sell_stock(
                    params["code"],
                    params["price"], 
                    params["quantity"]
                )
            elif command_type == "export_holdings":
                result = self.export_holdings()
            elif command_type == "get_balance":
                result = self.get_account_balance()
            
            # 发送结果
            response = {
                "type": "command_result",
                "command_id": command_id,
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(response))
            logger.info(f"✅ 命令执行完成: {command_type}")
            
        except Exception as e:
            logger.error(f"❌ 处理消息失败: {e}")
            
            if "command_id" in locals():
                error_response = {
                    "type": "command_error",
                    "command_id": command_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(error_response))

def main():
    """主函数"""
    # Render服务URL - 部署后需要更新
    RENDER_URL = "https://your-app-name.onrender.com"
    
    print("🌐 本地交易代理客户端")
    print("=" * 50)
    print(f"🔗 连接地址: {RENDER_URL}")
    print("📱 移动应用API: 使用相同地址")
    print("🖥️ 本地交易: 通过此客户端执行")
    print("=" * 50)
    
    # 创建客户端
    client = LocalTradingClient(RENDER_URL)
    
    try:
        # 运行客户端
        asyncio.run(client.connect_and_run())
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出程序")
        client.running = False

if __name__ == "__main__":
    main()
