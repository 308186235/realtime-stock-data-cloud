#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一本地Agent服务
集成WebSocket客户端、HTTP服务器、交易API和配置管理
"""

import asyncio
import websockets
import json
import logging
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/unified_local_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 尝试导入本地交易模块
try:
    from trader_api import TraderAPI
    from trader_buy_sell import TraderBuySell
    from trader_export import TraderExport
    from trader_core import TraderCore
    LOCAL_TRADING_AVAILABLE = True
    logger.info("✅ 本地交易模块加载成功")
except ImportError as e:
    LOCAL_TRADING_AVAILABLE = False
    logger.warning(f"⚠️ 本地交易模块不可用: {e}")

class UnifiedLocalAgent:
    """统一本地Agent服务"""
    
    def __init__(self):
        self.running = False
        self.websocket_connection = None
        self.http_server = None
        self.trader_api = None
        self.config = self.load_config()
        
        # 初始化FastAPI应用
        self.app = FastAPI(title="统一本地Agent服务", version="1.0.0")
        self.setup_fastapi()
        
        # 初始化交易API
        if LOCAL_TRADING_AVAILABLE:
            try:
                self.trader_api = TraderAPI()
                logger.info("✅ 交易API初始化成功")
            except Exception as e:
                logger.error(f"❌ 交易API初始化失败: {e}")
                self.trader_api = None
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        return {
            "cloud_websocket_url": "wss://app.aigupiao.me/ws/local-agent",
            "local_http_port": 8080,
            "reconnect_interval": 5,
            "max_reconnect_attempts": 10,
            "heartbeat_interval": 30
        }
    
    def setup_fastapi(self):
        """设置FastAPI应用"""
        # CORS配置
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 添加路由
        @self.app.get("/status")
        async def get_status():
            """获取服务状态"""
            return {
                "service_running": self.running,
                "websocket_connected": self.websocket_connection is not None,
                "trader_api_available": self.trader_api is not None,
                "local_trading_available": LOCAL_TRADING_AVAILABLE,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/trade")
        async def execute_trade(command: Dict[str, Any]):
            """执行交易"""
            if not self.trader_api:
                raise HTTPException(status_code=503, detail="交易API不可用")
            
            result = await self._execute_trade_command(command)
            if not result["success"]:
                raise HTTPException(status_code=500, detail=result["message"])
            
            return result
        
        @self.app.post("/export")
        async def export_data(request: Dict[str, Any]):
            """导出数据"""
            if not self.trader_api:
                raise HTTPException(status_code=503, detail="交易API不可用")
            
            result = await self._execute_export_command(request)
            if not result["success"]:
                raise HTTPException(status_code=500, detail=result["message"])
            
            return result
        
        @self.app.get("/portfolio")
        async def get_portfolio():
            """获取投资组合"""
            if not self.trader_api:
                raise HTTPException(status_code=503, detail="交易API不可用")
            
            try:
                # 导出持仓数据
                export_result = await self._execute_export_command({"data_type": "holdings"})
                if export_result["success"]:
                    return {
                        "success": True,
                        "portfolio": export_result.get("data", {}),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    raise HTTPException(status_code=500, detail="获取投资组合失败")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"获取投资组合异常: {e}")
    
    async def start_all_services(self):
        """启动所有服务"""
        logger.info("🚀 启动统一本地Agent服务")
        self.running = True
        
        # 启动WebSocket客户端
        websocket_task = asyncio.create_task(self._websocket_client_loop())
        
        # 启动HTTP服务器
        http_task = asyncio.create_task(self._start_http_server())
        
        # 启动心跳任务
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # 等待所有任务
        await asyncio.gather(websocket_task, http_task, heartbeat_task)
    
    async def _start_http_server(self):
        """启动HTTP服务器"""
        try:
            config = uvicorn.Config(
                self.app,
                host="0.0.0.0",
                port=self.config["local_http_port"],
                log_level="info"
            )
            server = uvicorn.Server(config)
            logger.info(f"🌐 HTTP服务器启动在端口 {self.config['local_http_port']}")
            await server.serve()
        except Exception as e:
            logger.error(f"❌ HTTP服务器启动失败: {e}")
    
    async def _websocket_client_loop(self):
        """WebSocket客户端循环"""
        reconnect_attempts = 0
        
        while self.running and reconnect_attempts < self.config["max_reconnect_attempts"]:
            try:
                logger.info(f"🔗 连接云端WebSocket: {self.config['cloud_websocket_url']}")
                
                async with websockets.connect(self.config["cloud_websocket_url"]) as websocket:
                    self.websocket_connection = websocket
                    reconnect_attempts = 0  # 重置重连计数
                    
                    # 注册本地服务
                    await self._register_local_service(websocket)
                    
                    # 监听云端命令
                    async for message in websocket:
                        if not self.running:
                            break
                        
                        try:
                            command = json.loads(message)
                            await self._handle_cloud_command(websocket, command)
                        except Exception as e:
                            logger.error(f"❌ 处理云端命令失败: {e}")
            
            except Exception as e:
                logger.error(f"❌ WebSocket连接失败: {e}")
                self.websocket_connection = None
                reconnect_attempts += 1
                
                if self.running and reconnect_attempts < self.config["max_reconnect_attempts"]:
                    wait_time = min(self.config["reconnect_interval"] * reconnect_attempts, 60)
                    logger.info(f"⏳ {wait_time}秒后重连 (第{reconnect_attempts}次)")
                    await asyncio.sleep(wait_time)
        
        if reconnect_attempts >= self.config["max_reconnect_attempts"]:
            logger.error("❌ 达到最大重连次数，停止重连")
    
    async def _register_local_service(self, websocket):
        """注册本地服务"""
        register_msg = {
            "type": "register",
            "agent_type": "unified_local_agent",
            "capabilities": ["trade", "export", "portfolio", "status"],
            "config": {
                "local_trading_available": LOCAL_TRADING_AVAILABLE,
                "trader_api_available": self.trader_api is not None
            },
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(register_msg))
        logger.info("✅ 已注册到云端服务")
    
    async def _handle_cloud_command(self, websocket, command):
        """处理云端命令"""
        command_type = command.get("type")
        command_id = command.get("id")
        
        logger.info(f"📨 收到云端命令: {command_type}")
        
        try:
            result = None
            
            if command_type == "trade":
                result = await self._execute_trade_command(command.get("data", {}))
            elif command_type == "export":
                result = await self._execute_export_command(command.get("data", {}))
            elif command_type == "portfolio":
                result = await self._get_portfolio()
            elif command_type == "status":
                result = await self._get_status()
            elif command_type == "heartbeat":
                result = {"status": "alive", "timestamp": datetime.now().isoformat()}
            else:
                result = {"success": False, "message": f"未知命令类型: {command_type}"}
            
            # 发送响应
            response = {
                "type": "response",
                "command_id": command_id,
                "success": result.get("success", True),
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(response))
            logger.info(f"✅ 命令执行完成: {command_type}")
            
        except Exception as e:
            # 发送错误响应
            error_response = {
                "type": "error",
                "command_id": command_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(error_response))
            logger.error(f"❌ 执行命令失败: {e}")
    
    async def _execute_trade_command(self, data):
        """执行交易命令"""
        if not self.trader_api:
            return {"success": False, "message": "交易API不可用"}
        
        action = data.get("action")
        stock_code = data.get("stock_code")
        quantity = data.get("quantity")
        price = data.get("price")
        
        logger.info(f"💰 执行交易: {action} {stock_code} {quantity}股 @{price or '市价'}")
        
        try:
            if action.lower() == "buy":
                success = self.trader_api.buy(stock_code, quantity, price or "市价")
                action_name = "买入"
            elif action.lower() == "sell":
                success = self.trader_api.sell(stock_code, quantity, price or "市价")
                action_name = "卖出"
            else:
                return {"success": False, "message": f"不支持的交易类型: {action}"}
            
            result_message = f"{action_name}操作{'成功' if success else '失败'}"
            logger.info(f"{'✅' if success else '❌'} {result_message}")
            
            return {
                "success": success,
                "message": result_message,
                "trade_details": {
                    "action": action,
                    "stock_code": stock_code,
                    "quantity": quantity,
                    "price": price or "市价",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            error_msg = f"交易执行异常: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    async def _execute_export_command(self, data):
        """执行导出命令"""
        if not self.trader_api:
            return {"success": False, "message": "交易API不可用"}
        
        data_type = data.get("data_type", "all")
        logger.info(f"📊 执行数据导出: {data_type}")
        
        try:
            if data_type == "holdings":
                result = self.trader_api.export_holdings()
            elif data_type == "transactions":
                result = self.trader_api.export_transactions()
            elif data_type == "orders":
                result = self.trader_api.export_orders()
            elif data_type == "all":
                result = self.trader_api.export_all()
            else:
                return {"success": False, "message": f"不支持的导出类型: {data_type}"}
            
            return {
                "success": True,
                "message": f"{data_type}数据导出成功",
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"数据导出异常: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    async def _get_portfolio(self):
        """获取投资组合"""
        export_result = await self._execute_export_command({"data_type": "holdings"})
        return export_result
    
    async def _get_status(self):
        """获取状态"""
        return {
            "success": True,
            "service_running": self.running,
            "websocket_connected": self.websocket_connection is not None,
            "trader_api_available": self.trader_api is not None,
            "local_trading_available": LOCAL_TRADING_AVAILABLE,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while self.running:
            try:
                if self.websocket_connection:
                    heartbeat_msg = {
                        "type": "heartbeat",
                        "timestamp": datetime.now().isoformat(),
                        "status": "alive"
                    }
                    await self.websocket_connection.send(json.dumps(heartbeat_msg))
                
                await asyncio.sleep(self.config["heartbeat_interval"])
            except Exception as e:
                logger.error(f"❌ 心跳发送失败: {e}")
                await asyncio.sleep(5)
    
    def stop(self):
        """停止服务"""
        logger.info("🛑 停止统一本地Agent服务")
        self.running = False

async def main():
    """主函数"""
    agent = UnifiedLocalAgent()
    
    try:
        await agent.start_all_services()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止服务...")
    finally:
        agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
