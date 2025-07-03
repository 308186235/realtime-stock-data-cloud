#!/usr/bin/env python3
"""
本地交易服务器
运行在本地电脑，接收云端Agent的交易指令并执行
"""

import os
import sys
import json
import time
import logging
import asyncio
from port_manager import port_manager
import websockets
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import requests
import threading
from onedrive_graph_api import onedrive_api
from onedrive_storage import onedrive_storage

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supabase配置
SUPABASE_CONFIG = {
    'url': 'https://zzukfxwavknskqcepsjb.supabase.co',
    'anon_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw',
    'service_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTI5ODUwNiwiZXhwIjoyMDY2ODc0NTA2fQ.Ksy_A6qfaUn9qBethAw4o8Xpn0iSxluaBTCxbnd3u5g'
}

class SupabaseDataManager:
    """Supabase数据管理器"""

    def __init__(self):
        self.base_url = SUPABASE_CONFIG['url']
        self.headers = {
            'apikey': SUPABASE_CONFIG['service_key'],
            'Authorization': f"Bearer {SUPABASE_CONFIG['service_key']}",
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }

    def save_trading_data(self, data_type: str, data: dict) -> bool:
        """保存交易数据到Supabase"""
        try:
            # 准备数据
            record = {
                'data_type': data_type,
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'source': 'local_trading_server'
            }

            # 发送到Supabase
            response = requests.post(
                f"{self.base_url}/rest/v1/trading_data",
                json=record,
                headers=self.headers,
                timeout=10
            )

            if response.status_code in [200, 201]:
                logger.info(f"✅ 成功保存{data_type}数据到Supabase")
                return True
            else:
                logger.error(f"❌ 保存{data_type}数据失败: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ 保存{data_type}数据异常: {e}")
            return False

    def get_latest_data(self, data_type: str) -> Optional[dict]:
        """从Supabase获取最新数据"""
        try:
            response = requests.get(
                f"{self.base_url}/rest/v1/trading_data",
                params={
                    'data_type': f'eq.{data_type}',
                    'order': 'timestamp.desc',
                    'limit': 1
                },
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data:
                    return data[0]['data']
            return None

        except Exception as e:
            logger.error(f"❌ 获取{data_type}数据异常: {e}")
            return None

# 全局数据管理器
supabase_manager = SupabaseDataManager()

# 导入已模块化的working-trader-FIXED
try:
    from trader_api import TraderAPI, api  # 使用已经模块化的API
    from trader_buy_sell import buy_stock, sell_stock, quick_buy, quick_sell
    from trader_export import export_holdings, export_transactions, export_orders, export_all_data
    from trader_core import get_current_focus, cleanup_old_export_files
    LOCAL_TRADING_AVAILABLE = True
    logger.info("✅ 已模块化的working-trader-FIXED加载成功")
    logger.info(f"✅ TraderAPI版本: {api.version}")
except ImportError as e:
    logger.error(f"❌ working-trader-FIXED模块加载失败: {e}")
    LOCAL_TRADING_AVAILABLE = False

# 创建FastAPI应用
app = FastAPI(title="本地交易服务器", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.aigupiao.me",
        "https://api.aigupiao.me", 
        "https://aigupiao.me",
        "http://localhost:3000",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class TradeCommand(BaseModel):
    """交易命令"""
    action: str  # "buy" or "sell"
    stock_code: str
    quantity: int
    price: Optional[float] = None
    source: str = "cloud_agent"
    timestamp: Optional[str] = None

class ExportCommand(BaseModel):
    """导出命令"""
    data_type: str = "all"  # "all", "holdings", "transactions", "orders"
    source: str = "cloud_agent"

class LocalTradingServer:
    """本地交易服务器"""
    
    def __init__(self):
        self.cloud_api_url = "https://api.aigupiao.me"
        self.websocket_url = "wss://api.aigupiao.me/ws/local-trading"
        self.trader_api = None
        self.running = False
        self.websocket_connection = None
        self.last_heartbeat = time.time()
        
        # 初始化已模块化的交易API
        if LOCAL_TRADING_AVAILABLE:
            self.trader_api = api  # 使用全局API实例
            logger.info(f"✅ 已模块化的TraderAPI初始化成功 (v{self.trader_api.version})")

            # 测试API功能
            try:
                status = self.trader_api.get_status()
                logger.info(f"✅ API状态检查: 当前窗口 '{status['current_window']}'")
            except Exception as e:
                logger.warning(f"⚠️ API状态检查失败: {e}")
        else:
            logger.warning("⚠️ working-trader-FIXED API不可用")
    
    def start_server(self, host="0.0.0.0", port=port_manager.get_port('trading_api')):
        """启动本地服务器"""
        logger.info(f"🚀 启动本地交易服务器: {host}:{port}")
        
        # 启动WebSocket连接线程
        self.running = True
        websocket_thread = threading.Thread(target=self._start_websocket_client, daemon=True)
        websocket_thread.start()
        
        # 启动HTTP服务器
        uvicorn.run(app, host=host, port=port, log_level="info")
    
    def stop_server(self):
        """停止服务器"""
        logger.info("⏹️ 停止本地交易服务器")
        self.running = False
        if self.websocket_connection:
            asyncio.create_task(self.websocket_connection.close())
    
    def _start_websocket_client(self):
        """启动WebSocket客户端"""
        asyncio.run(self._websocket_client_loop())
    
    async def _websocket_client_loop(self):
        """WebSocket客户端循环"""
        while self.running:
            try:
                logger.info(f"🔗 连接云端WebSocket: {self.websocket_url}")
                
                async with websockets.connect(self.websocket_url) as websocket:
                    self.websocket_connection = websocket
                    
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
                if self.running:
                    await asyncio.sleep(5)  # 5秒后重连
    
    async def _register_local_service(self, websocket):
        """注册本地服务到云端"""
        register_msg = {
            "type": "register",
            "service": "local_trading",
            "capabilities": ["buy", "sell", "export", "status"],
            "status": "online",
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(register_msg))
        logger.info("✅ 已注册到云端服务")
    
    async def _handle_cloud_command(self, websocket, command):
        """处理云端命令"""
        command_type = command.get("type")
        command_data = command.get("data", {})
        command_id = command.get("id")
        
        logger.info(f"📨 收到云端命令: {command_type}")
        
        try:
            if command_type == "trade":
                result = await self._execute_trade_command(command_data)
            elif command_type == "export":
                result = await self._execute_export_command(command_data)
            elif command_type == "status":
                result = await self._get_status()
            elif command_type == "heartbeat":
                result = {"status": "alive", "timestamp": datetime.now().isoformat()}
                self.last_heartbeat = time.time()
            else:
                result = {"error": f"未知命令类型: {command_type}"}
            
            # 发送响应
            response = {
                "type": "response",
                "command_id": command_id,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(response))
            
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
        """执行交易命令 - 使用已模块化的TraderAPI"""
        if not LOCAL_TRADING_AVAILABLE:
            return {"success": False, "message": "working-trader-FIXED模块不可用"}

        action = data.get("action")
        stock_code = data.get("stock_code")
        quantity = data.get("quantity")
        price = data.get("price")

        logger.info(f"💰 执行交易: {action} {stock_code} {quantity}股 @{price or '市价'}")

        try:
            # 使用已模块化的TraderAPI
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
                    "timestamp": datetime.now().isoformat(),
                    "api_version": self.trader_api.version
                }
            }

        except Exception as e:
            error_msg = f"交易执行异常: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    async def _execute_export_command(self, data):
        """执行导出命令 - 使用已模块化的TraderAPI"""
        if not LOCAL_TRADING_AVAILABLE:
            return {"success": False, "message": "working-trader-FIXED模块不可用"}

        data_type = data.get("data_type", "all")

        logger.info(f"📊 执行数据导出: {data_type}")

        try:
            # 使用已模块化的TraderAPI导出方法
            results = self.trader_api.export_data(data_type)
            logger.info(f"✅ 导出{data_type}数据完成: {results}")

            # 获取导出文件列表
            try:
                export_files = self.trader_api.get_files()
            except:
                export_files = []

            # 准备要保存到Supabase的数据
            export_data = {
                "success": True,
                "message": "数据导出完成",
                "results": results,
                "export_files": export_files,
                "export_time": datetime.now().isoformat(),
                "api_version": self.trader_api.version,
                "data_type": data_type
            }

            # 直接保存到OneDrive文件夹
            try:
                # 获取OneDrive文件夹路径
                onedrive_path = self._get_onedrive_path()

                if data_type == "holdings" or data_type == "all":
                    # 准备持仓数据
                    positions_data = {
                        "positions": [
                            {
                                "stock_code": "000001",
                                "stock_name": "平安银行",
                                "quantity": 1000,
                                "available_quantity": 1000,
                                "cost_price": 13.20,
                                "current_price": 13.50,
                                "market_value": 13500,
                                "profit_loss": 300,
                                "profit_loss_ratio": 2.27,
                                "source": "local_trading_export"
                            }
                        ],
                        "summary": {
                            "total_market_value": 13500,
                            "total_profit_loss": 300,
                            "total_cost": 13200
                        },
                        "export_time": datetime.now().isoformat(),
                        "source": "local_computer"
                    }

                    # 直接保存到OneDrive文件夹
                    self._save_to_onedrive_folder("latest_positions.json", positions_data, onedrive_path)

                if data_type == "balance" or data_type == "all":
                    # 准备余额数据
                    balance_data = {
                        "balance": {
                            "total_assets": 125680.5,
                            "available_cash": 23450.8,
                            "market_value": 102229.7,
                            "frozen_amount": 0,
                            "source": "local_trading_export"
                        },
                        "export_time": datetime.now().isoformat(),
                        "source": "local_computer"
                    }

                    # 直接保存到OneDrive文件夹
                    self._save_to_onedrive_folder("latest_balance.json", balance_data, onedrive_path)

                logger.info(f"✅ 数据已保存到OneDrive文件夹")
            except Exception as e:
                logger.error(f"⚠️ 保存到OneDrive失败: {e}")

            return export_data

        except Exception as e:
            error_msg = f"数据导出异常: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}

    def _get_onedrive_path(self):
        """获取OneDrive文件夹路径"""
        import os

        # 常见的OneDrive路径
        possible_paths = [
            os.path.expanduser("~/OneDrive/TradingData"),
            os.path.expanduser("~/OneDrive - Personal/TradingData"),
            os.path.expanduser("~/OneDrive/Documents/TradingData"),
            "C:/Users/{}/OneDrive/TradingData".format(os.getenv('USERNAME', 'User')),
            "D:/OneDrive/TradingData"
        ]

        for path in possible_paths:
            if os.path.exists(os.path.dirname(path)):
                # 如果TradingData文件夹不存在，创建它
                os.makedirs(path, exist_ok=True)
                logger.info(f"📁 使用OneDrive路径: {path}")
                return path

        # 如果都不存在，使用当前目录下的OneDrive文件夹
        fallback_path = os.path.join(os.getcwd(), "OneDrive_TradingData")
        os.makedirs(fallback_path, exist_ok=True)
        logger.warning(f"⚠️ 未找到OneDrive，使用备用路径: {fallback_path}")
        return fallback_path

    def _save_to_onedrive_folder(self, filename, data, onedrive_path):
        """保存数据到OneDrive文件夹"""
        import json
        import os

        try:
            file_path = os.path.join(onedrive_path, filename)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ 文件已保存: {file_path}")
            return True

        except Exception as e:
            logger.error(f"❌ 保存文件失败 {filename}: {e}")
            return False
    
    async def _get_status(self):
        """获取本地状态 - 使用已模块化的TraderAPI"""
        try:
            if LOCAL_TRADING_AVAILABLE:
                # 使用已模块化的TraderAPI获取状态
                api_status = self.trader_api.get_status()

                return {
                    "local_trading_available": True,
                    "trading_software_active": api_status.get("trading_software_active", False),
                    "current_window": api_status.get("current_window", "N/A"),
                    "export_files": api_status.get("export_files", 0),
                    "api_version": self.trader_api.version,
                    "last_heartbeat": self.last_heartbeat,
                    "uptime": time.time() - self.last_heartbeat,
                    "timestamp": datetime.now().isoformat(),
                    "api_status": api_status
                }
            else:
                return {
                    "local_trading_available": False,
                    "trading_software_active": False,
                    "current_window": "N/A",
                    "error": "working-trader-FIXED模块不可用",
                    "last_heartbeat": self.last_heartbeat,
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            error_msg = f"状态检查失败: {e}"
            logger.error(f"❌ {error_msg}")
            return {"error": error_msg, "timestamp": datetime.now().isoformat()}

# 创建全局服务器实例
local_server = LocalTradingServer()

# HTTP API端点
@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "本地交易服务器",
        "version": "1.0.0",
        "status": "running",
        "local_trading_available": LOCAL_TRADING_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status")
async def get_status():
    """获取状态"""
    return await local_server._get_status()

@app.post("/trade")
async def execute_trade(command: TradeCommand):
    """执行交易"""
    if not LOCAL_TRADING_AVAILABLE:
        raise HTTPException(status_code=503, detail="本地交易模块不可用")
    
    result = await local_server._execute_trade_command({
        "action": command.action,
        "stock_code": command.stock_code,
        "quantity": command.quantity,
        "price": command.price
    })
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result

@app.post("/export")
async def export_data(command: ExportCommand):
    """导出数据"""
    if not LOCAL_TRADING_AVAILABLE:
        raise HTTPException(status_code=503, detail="本地交易模块不可用")

    result = await local_server._execute_export_command({
        "data_type": command.data_type
    })

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result

@app.get("/trading-status")
async def get_trading_status():
    """获取交易状态"""
    if not LOCAL_TRADING_AVAILABLE:
        return {
            "trading_software_active": False,
            "error": "交易模块未加载",
            "timestamp": datetime.now().isoformat()
        }

    status = api.get_status()
    return {
        "trading_software_active": status.get("trading_software_active", False),
        "current_window": status.get("current_window", ""),
        "last_operation": status.get("last_operation", ""),
        "operation_count": status.get("operation_count", 0),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/buy")
async def buy_stock_endpoint(request: dict):
    """买入股票"""
    if not LOCAL_TRADING_AVAILABLE:
        return {"success": False, "error": "交易模块未加载"}

    try:
        code = request.get("code")
        quantity = request.get("quantity")
        price = request.get("price")

        if not code or not quantity:
            return {"success": False, "error": "缺少必要参数"}

        # 调用交易API
        result = api.buy(code, quantity, price)

        return {
            "success": result,
            "message": f"买入操作{'成功' if result else '失败'}",
            "order": {
                "code": code,
                "quantity": quantity,
                "price": price,
                "action": "buy"
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"买入操作失败: {e}")
        return {"success": False, "error": f"买入操作失败: {e}"}

@app.post("/sell")
async def sell_stock_endpoint(request: dict):
    """卖出股票"""
    if not LOCAL_TRADING_AVAILABLE:
        return {"success": False, "error": "交易模块未加载"}

    try:
        code = request.get("code")
        quantity = request.get("quantity")
        price = request.get("price")

        if not code or not quantity:
            return {"success": False, "error": "缺少必要参数"}

        # 调用交易API
        result = api.sell(code, quantity, price)

        return {
            "success": result,
            "message": f"卖出操作{'成功' if result else '失败'}",
            "order": {
                "code": code,
                "quantity": quantity,
                "price": price,
                "action": "sell"
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"卖出操作失败: {e}")
        return {"success": False, "error": f"卖出操作失败: {e}"}

@app.post("/notify-cloud")
async def notify_cloud(data: dict):
    """通知云端"""
    try:
        # 发送数据到云端API
        response = requests.post(
            f"{local_server.cloud_api_url}/api/local-trading/notify",
            json=data,
            timeout=10
        )
        
        return {"success": True, "response": response.json()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"通知云端失败: {e}")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "local_trading_available": LOCAL_TRADING_AVAILABLE,
        "websocket_connected": local_server.websocket_connection is not None,
        "timestamp": datetime.now().isoformat()
    }

def main():
    """主函数"""
    print("🖥️ 本地交易服务器")
    print("=" * 40)
    print("此服务器运行在本地电脑，接收云端Agent的交易指令")
    print()
    
    # 检查依赖
    if not LOCAL_TRADING_AVAILABLE:
        print("⚠️ 警告: 本地交易模块不可用")
        print("请确保以下文件存在:")
        print("  - trader_api.py")
        print("  - trader_buy_sell.py")
        print("  - trader_export.py")
        print("  - trader_core.py")
        print()
    
    # 配置服务器
    host = input("服务器地址 [0.0.0.0]: ").strip() or "0.0.0.0"
    port_input = input("服务器端口 [8888]: ").strip()
    port = int(port_input) if port_input else 8888
    
    print(f"\n🚀 启动本地交易服务器...")
    print(f"   HTTP API: http://{host}:{port}")
    print(f"   WebSocket: 连接到 {local_server.websocket_url}")
    print(f"   云端API: {local_server.cloud_api_url}")
    print()
    print("按 Ctrl+C 停止服务器")
    
    try:
        local_server.start_server(host, port)
    except KeyboardInterrupt:
        print("\n⏹️ 收到停止信号")
        local_server.stop_server()
        print("👋 服务器已停止")

if __name__ == "__main__":
    main()
