#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实云端到本地交易系统
直接使用真实的交易模块,不使用任何模拟数据
"""

import asyncio
import json
import logging
import time
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/real_trading_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 确保日志目录存在
os.makedirs('logs', exist_ok=True)

# 数据模型
class TradeRequest(BaseModel):
    action: str  # buy/sell
    stock_code: str
    quantity: int
    price: Optional[str] = "市价"

class ExportRequest(BaseModel):
    data_type: str = "all"  # all/holdings/transactions/orders

class RealTradingSystem:
    """真实交易系统"""
    
    def __init__(self):
        self.trader_api = None
        self.trade_history = []
        self.system_stats = {
            "trades_executed": 0,
            "exports_completed": 0,
            "errors_count": 0,
            "start_time": datetime.now().isoformat()
        }
        
        # 初始化真实交易API
        self.init_real_trader_api()
        
        # 创建FastAPI应用
        self.app = self.create_fastapi_app()
    
    def init_real_trader_api(self):
        """初始化真实交易API"""
        try:
            # 导入真实的交易模块
            import trader_buy_sell
            import trader_export_original
            import trader_core

            # 创建简单的API包装器
            class SimpleTraderAPI:
                def __init__(self):
                    self.version = "1.0.0"

                def get_status(self):
                    """获取交易软件状态"""
                    try:
                        # 检查交易软件是否运行
                        import win32gui
                        def enum_windows_proc(hwnd, windows):
                            if win32gui.IsWindowVisible(hwnd):
                                window_text = win32gui.GetWindowText(hwnd)
                                if "东吴证券" in window_text or "网上交易" in window_text:
                                    windows.append((hwnd, window_text))
                            return True

                        windows = []
                        win32gui.EnumWindows(enum_windows_proc, windows)

                        return {
                            'trading_software_active': len(windows) > 0,
                            'window_title': windows[0][1] if windows else '',
                            'current_window': windows[0][1] if windows else 'None'
                        }
                    except Exception as e:
                        logger.error(f"获取状态失败: {e}")
                        return {'trading_software_active': False}

                def buy(self, stock_code, quantity, price):
                    """执行买入"""
                    try:
                        return trader_buy_sell.buy_stock(stock_code, quantity, price)
                    except Exception as e:
                        logger.error(f"买入失败: {e}")
                        return False

                def sell(self, stock_code, quantity, price):
                    """执行卖出"""
                    try:
                        return trader_buy_sell.sell_stock(stock_code, quantity, price)
                    except Exception as e:
                        logger.error(f"卖出失败: {e}")
                        return False

                def export_positions(self):
                    """导出持仓"""
                    try:
                        return trader_export_original.export_holdings()
                    except Exception as e:
                        logger.error(f"导出持仓失败: {e}")
                        return False

                def export_trades(self):
                    """导出成交"""
                    try:
                        return trader_export_original.export_transactions()
                    except Exception as e:
                        logger.error(f"导出成交失败: {e}")
                        return False

                def export_orders(self):
                    """导出委托"""
                    try:
                        return trader_export_original.export_orders()
                    except Exception as e:
                        logger.error(f"导出委托失败: {e}")
                        return False

                def export_all(self):
                    """导出所有数据"""
                    return {
                        'holdings': self.export_positions(),
                        'transactions': self.export_trades(),
                        'orders': self.export_orders()
                    }

                def get_files(self):
                    """获取导出的文件数据"""
                    try:
                        import trader_core
                        return trader_core.read_exported_files()
                    except Exception as e:
                        logger.error(f"读取文件失败: {e}")
                        return {}

            self.trader_api = SimpleTraderAPI()
            logger.info("✅ 真实交易API初始化成功")
            logger.info(f"✅ TraderAPI版本: {self.trader_api.version}")

            # 测试交易软件连接
            status = self.trader_api.get_status()
            if status.get('trading_software_active'):
                logger.info("✅ 交易软件连接正常")
                logger.info(f"✅ 窗口标题: {status.get('window_title')}")
            else:
                logger.warning("⚠️ 交易软件未激活,请确保东吴证券软件正在运行")

        except ImportError as e:
            logger.error(f"❌ 无法导入交易模块: {e}")
            logger.error("请确保trader_buy_sell.py, trader_export_original.py, trader_core.py等文件存在")
            raise Exception("交易模块导入失败")
        except Exception as e:
            logger.error(f"❌ 交易API初始化失败: {e}")
            raise Exception(f"交易API初始化失败: {e}")
    
    def create_fastapi_app(self):
        """创建FastAPI应用"""
        app = FastAPI(
            title="真实本地交易系统",
            description="云端Agent调用本地电脑真实交易",
            version="1.0.0"
        )
        
        # 添加CORS支持
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 添加路由
        self.setup_routes(app)
        
        return app
    
    def setup_routes(self, app):
        """设置API路由"""
        
        @app.get("/")
        async def root():
            """根路径"""
            return {
                "service": "真实本地交易系统",
                "version": "1.0.0",
                "mode": "REAL_TRADING",
                "timestamp": datetime.now().isoformat(),
                "stats": self.system_stats,
                "trading_software_status": self.get_trading_software_status(),
                "endpoints": {
                    "status": "GET /status",
                    "trade": "POST /trade",
                    "export": "POST /export",
                    "history": "GET /history",
                    "health": "GET /health"
                }
            }
        
        @app.get("/status")
        async def get_status():
            """获取系统状态"""
            status = self.trader_api.get_status()
            return {
                "service_running": True,
                "trader_api_available": True,
                "trading_software_active": status.get('trading_software_active', False),
                "mode": "REAL_TRADING",
                "last_heartbeat": datetime.now().isoformat(),
                "stats": self.system_stats
            }
        
        @app.post("/trade")
        async def execute_trade(request: TradeRequest):
            """执行真实交易"""
            result = await self.execute_real_trade(
                action=request.action,
                stock_code=request.stock_code,
                quantity=request.quantity,
                price=request.price
            )
            
            if not result["success"]:
                raise HTTPException(status_code=500, detail=result["message"])
            
            return result
        
        @app.post("/export")
        async def export_data(request: ExportRequest):
            """导出真实数据"""
            result = await self.export_real_data(request.data_type)
            
            if not result["success"]:
                raise HTTPException(status_code=500, detail=result["message"])
            
            return result
        
        @app.get("/history")
        async def get_trade_history(limit: int = 20):
            """获取交易历史"""
            return {
                "success": True,
                "trades": self.trade_history[-limit:],
                "total": len(self.trade_history)
            }
        
        @app.get("/health")
        async def health_check():
            """健康检查"""
            return {
                "status": "healthy",
                "mode": "REAL_TRADING",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_trading_software_status(self):
        """获取交易软件状态"""
        try:
            status = self.trader_api.get_status()
            return {
                "active": status.get('trading_software_active', False),
                "window_title": status.get('window_title', ''),
                "caps_lock": status.get('caps_lock_on', False)
            }
        except Exception as e:
            logger.error(f"获取交易软件状态失败: {e}")
            return {"active": False, "error": str(e)}
    
    async def execute_real_trade(self, action: str, stock_code: str, quantity: int, price: str = "市价") -> Dict[str, Any]:
        """执行真实交易"""
        logger.info(f"💰 执行真实交易: {action} {stock_code} {quantity}股 @{price}")
        
        try:
            # 检查交易软件状态
            status = self.trader_api.get_status()
            if not status.get('trading_software_active'):
                return {
                    "success": False,
                    "message": "交易软件未激活,请确保东吴证券软件正在运行并已登录"
                }
            
            # 记录交易开始
            trade_record = {
                "id": f"trade_{int(time.time())}_{len(self.trade_history)}",
                "action": action,
                "stock_code": stock_code,
                "quantity": quantity,
                "price": price,
                "timestamp": datetime.now().isoformat(),
                "mode": "REAL_TRADING"
            }
            
            # 执行真实交易
            if action.lower() == "buy":
                logger.info(f"🔵 执行买入: {stock_code} {quantity}股 @{price}")
                success = self.trader_api.buy(stock_code, quantity, price)
                operation = "买入"
            elif action.lower() == "sell":
                logger.info(f"🔴 执行卖出: {stock_code} {quantity}股 @{price}")
                success = self.trader_api.sell(stock_code, quantity, price)
                operation = "卖出"
            else:
                return {"success": False, "message": f"不支持的交易类型: {action}"}
            
            # 更新交易记录
            trade_record["success"] = success
            trade_record["message"] = f"真实{operation}操作{'成功' if success else '失败'}"
            
            # 记录到历史
            self.trade_history.append(trade_record)
            self.system_stats["trades_executed"] += 1
            
            # 限制历史记录长度
            if len(self.trade_history) > 1000:
                self.trade_history = self.trade_history[-1000:]
            
            if success:
                logger.info(f"✅ 交易成功: {operation} {stock_code}")
            else:
                logger.error(f"❌ 交易失败: {operation} {stock_code}")
            
            return {
                "success": success,
                "message": trade_record["message"],
                "trade_id": trade_record["id"],
                "trade_details": trade_record
            }
            
        except Exception as e:
            error_msg = f"交易执行异常: {e}"
            logger.error(f"❌ {error_msg}")
            self.system_stats["errors_count"] += 1
            return {"success": False, "message": error_msg}
    
    async def export_real_data(self, data_type: str = "all") -> Dict[str, Any]:
        """导出真实数据"""
        logger.info(f"📊 导出真实数据: {data_type}")
        
        try:
            # 检查交易软件状态
            status = self.trader_api.get_status()
            if not status.get('trading_software_active'):
                return {
                    "success": False,
                    "message": "交易软件未激活,请确保东吴证券软件正在运行并已登录"
                }
            
            # 执行真实数据导出
            if data_type == "holdings":
                logger.info("📈 导出持仓数据...")
                success = self.trader_api.export_positions()
                data = self.trader_api.get_files().get("holdings", []) if success else []
                
            elif data_type == "transactions":
                logger.info("📋 导出成交数据...")
                success = self.trader_api.export_trades()
                data = self.trader_api.get_files().get("transactions", []) if success else []
                
            elif data_type == "orders":
                logger.info("📝 导出委托数据...")
                success = self.trader_api.export_orders()
                data = self.trader_api.get_files().get("orders", []) if success else []
                
            else:  # all
                logger.info("📊 导出所有数据...")
                results = self.trader_api.export_all()
                success = any(results.values())
                data = self.trader_api.get_files() if success else {}
            
            # 更新统计
            if success:
                self.system_stats["exports_completed"] += 1
                logger.info(f"✅ 数据导出成功: {data_type}")
            else:
                logger.error(f"❌ 数据导出失败: {data_type}")
                self.system_stats["errors_count"] += 1
            
            return {
                "success": success,
                "message": f"真实数据导出{'成功' if success else '失败'}",
                "data": data,
                "data_type": data_type,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"数据导出异常: {e}"
            logger.error(f"❌ {error_msg}")
            self.system_stats["errors_count"] += 1
            return {"success": False, "message": error_msg}
    
    async def start_system(self):
        """启动系统"""
        logger.info("🚀 启动真实本地交易系统")
        logger.info("⚠️ 注意: 这是真实交易模式,所有操作都会影响实际账户")
        
        # 检查交易软件状态
        software_status = self.get_trading_software_status()
        if software_status.get("active"):
            logger.info("✅ 交易软件已激活")
        else:
            logger.warning("⚠️ 交易软件未激活,请启动东吴证券软件并登录")
        
        # 启动HTTP服务器
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=8889,  # 使用不同端口避免冲突
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        logger.info("📍 真实交易系统服务地址:")
        logger.info("  - HTTP API: http://localhost:8889")
        logger.info("  - API文档: http://localhost:8889/docs")
        logger.info("  - 模式: 真实交易模式")
        
        await server.serve()

# 全局系统实例
real_trading_system = RealTradingSystem()

def main():
    """主函数"""
    try:
        print("⚠️ 警告: 这是真实交易模式!")
        print("所有交易操作都会影响您的实际账户!")
        print("请确保:")
        print("1. 东吴证券软件已启动并登录")
        print("2. 您了解交易风险")
        print("3. 在收盘时间进行测试")
        
        confirm = input("\n确认继续? (输入 'YES' 继续): ")
        if confirm != "YES":
            print("已取消启动")
            return
        
        asyncio.run(real_trading_system.start_system())
    except KeyboardInterrupt:
        logger.info("👋 系统已停止")
    except Exception as e:
        logger.error(f"❌ 系统启动失败: {e}")

if __name__ == "__main__":
    main()
