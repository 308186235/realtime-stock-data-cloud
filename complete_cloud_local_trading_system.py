#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的云端到本地交易系统
集成所有现有组件，提供完整的云端Agent调用本地电脑交易功能
"""

import asyncio
import json
import logging
import time
import requests
import websockets
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import threading
import os
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/complete_trading_system.log'),
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
    price: Optional[float] = None
    agent_id: Optional[str] = None

class ExportRequest(BaseModel):
    data_type: str = "all"  # all/holdings/transactions/orders

class AgentDecision(BaseModel):
    action: str
    stock_code: str
    stock_name: str
    quantity: int
    price: Optional[float]
    confidence: float
    reason: str
    timestamp: str

class SystemStatus(BaseModel):
    service_running: bool
    trader_api_available: bool
    websocket_connected: bool
    cloud_connected: bool
    last_heartbeat: str
    mode: str  # real/simulation

class CompleteLocalTradingSystem:
    """完整的本地交易系统"""
    
    def __init__(self):
        self.trader_api = None
        self.websocket_connection = None
        self.cloud_api_url = "https://app.aigupiao.me/api"
        self.running = False
        self.trade_history = []
        self.decision_history = []
        self.system_stats = {
            "trades_executed": 0,
            "decisions_made": 0,
            "errors_count": 0,
            "start_time": datetime.now().isoformat()
        }
        
        # 初始化交易API
        self.init_trader_api()
        
        # 创建FastAPI应用
        self.app = self.create_fastapi_app()
    
    def init_trader_api(self):
        """初始化交易API"""
        try:
            # 尝试导入现有的交易模块
            from trader_api import TraderAPI
            self.trader_api = TraderAPI()
            logger.info("✅ 真实交易API初始化成功")
            self.mode = "real"
        except Exception as e:
            logger.warning(f"⚠️ 真实交易API初始化失败: {e}")
            logger.info("💡 使用模拟交易模式")
            self.trader_api = None
            self.mode = "simulation"
    
    def create_fastapi_app(self):
        """创建FastAPI应用"""
        app = FastAPI(
            title="完整本地交易系统",
            description="云端Agent调用本地电脑交易的完整解决方案",
            version="2.0.0"
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
                "service": "完整本地交易系统",
                "version": "2.0.0",
                "status": "运行中",
                "mode": self.mode,
                "timestamp": datetime.now().isoformat(),
                "stats": self.system_stats,
                "endpoints": {
                    "status": "GET /status",
                    "trade": "POST /trade",
                    "export": "POST /export",
                    "decisions": "GET /decisions",
                    "history": "GET /history",
                    "health": "GET /health"
                }
            }
        
        @app.get("/status")
        async def get_status():
            """获取系统状态"""
            return SystemStatus(
                service_running=True,
                trader_api_available=self.trader_api is not None,
                websocket_connected=self.websocket_connection is not None,
                cloud_connected=await self.check_cloud_connection(),
                last_heartbeat=datetime.now().isoformat(),
                mode=self.mode
            ).dict()
        
        @app.post("/trade")
        async def execute_trade(request: TradeRequest):
            """执行交易"""
            result = await self.execute_trade_internal(
                action=request.action,
                stock_code=request.stock_code,
                quantity=request.quantity,
                price=request.price,
                agent_id=request.agent_id
            )
            
            if not result["success"]:
                raise HTTPException(status_code=500, detail=result["message"])
            
            return result
        
        @app.post("/export")
        async def export_data(request: ExportRequest):
            """导出数据"""
            result = await self.export_data_internal(request.data_type)
            
            if not result["success"]:
                raise HTTPException(status_code=500, detail=result["message"])
            
            return result
        
        @app.post("/agent-decision")
        async def process_agent_decision(decision: AgentDecision):
            """处理Agent决策"""
            result = await self.process_agent_decision_internal(decision)
            return result
        
        @app.get("/decisions")
        async def get_decisions(limit: int = 10):
            """获取最近的决策"""
            return {
                "success": True,
                "decisions": self.decision_history[-limit:],
                "total": len(self.decision_history)
            }
        
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
                "timestamp": datetime.now().isoformat(),
                "uptime": (datetime.now() - datetime.fromisoformat(self.system_stats["start_time"])).total_seconds()
            }
        
        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket端点"""
            await self.handle_websocket_connection(websocket)
    
    async def execute_trade_internal(self, action: str, stock_code: str, quantity: int, 
                                   price: Optional[float] = None, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """内部交易执行方法"""
        logger.info(f"💰 执行交易: {action} {stock_code} {quantity}股 @{price or '市价'} (Agent: {agent_id or 'Unknown'})")
        
        try:
            trade_record = {
                "id": f"trade_{int(time.time())}_{len(self.trade_history)}",
                "action": action,
                "stock_code": stock_code,
                "quantity": quantity,
                "price": price or "市价",
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat(),
                "mode": self.mode
            }
            
            if self.trader_api and self.mode == "real":
                # 使用真实交易API
                if action.lower() == "buy":
                    success = self.trader_api.buy(stock_code, quantity, price or "市价")
                elif action.lower() == "sell":
                    success = self.trader_api.sell(stock_code, quantity, price or "市价")
                else:
                    return {"success": False, "message": f"不支持的交易类型: {action}"}
                
                trade_record["success"] = success
                trade_record["message"] = f"真实{action}操作{'成功' if success else '失败'}"
                
            else:
                # 模拟交易
                success = True  # 模拟总是成功
                trade_record["success"] = success
                trade_record["message"] = f"模拟{action}操作成功"
                logger.info("🎭 模拟交易执行")
            
            # 记录交易历史
            self.trade_history.append(trade_record)
            self.system_stats["trades_executed"] += 1
            
            # 限制历史记录长度
            if len(self.trade_history) > 1000:
                self.trade_history = self.trade_history[-1000:]
            
            # 通知云端
            await self.notify_cloud_trade_result(trade_record)
            
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
    
    async def export_data_internal(self, data_type: str = "all") -> Dict[str, Any]:
        """内部数据导出方法"""
        logger.info(f"📊 导出数据: {data_type}")
        
        try:
            if self.trader_api and self.mode == "real":
                # 使用真实导出API
                if data_type == "holdings":
                    success = self.trader_api.export_positions()
                    data = self.trader_api.get_files()["holdings"] if success else []
                elif data_type == "transactions":
                    success = self.trader_api.export_trades()
                    data = self.trader_api.get_files()["transactions"] if success else []
                elif data_type == "orders":
                    success = self.trader_api.export_orders()
                    data = self.trader_api.get_files()["orders"] if success else []
                else:
                    success = self.trader_api.export_all()
                    data = self.trader_api.get_files() if success else {}
                
                return {
                    "success": success,
                    "message": f"真实数据导出{'成功' if success else '失败'}",
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # 模拟数据
                mock_data = self.generate_mock_data(data_type)
                
                return {
                    "success": True,
                    "message": "模拟数据导出成功",
                    "data": mock_data,
                    "timestamp": datetime.now().isoformat(),
                    "mode": "simulation"
                }
                
        except Exception as e:
            error_msg = f"数据导出异常: {e}"
            logger.error(f"❌ {error_msg}")
            self.system_stats["errors_count"] += 1
            return {"success": False, "message": error_msg}
    
    def generate_mock_data(self, data_type: str) -> Dict[str, Any]:
        """生成模拟数据"""
        if data_type == "holdings":
            return [
                {"stock_code": "000001", "stock_name": "平安银行", "quantity": 100, "cost_price": 12.5, "current_price": 12.8},
                {"stock_code": "000002", "stock_name": "万科A", "quantity": 200, "cost_price": 18.3, "current_price": 18.1},
                {"stock_code": "BJ430001", "stock_name": "北交所测试", "quantity": 100, "cost_price": 15.2, "current_price": 15.8}
            ]
        elif data_type == "transactions":
            return [
                {"date": "2024-01-15", "stock_code": "000001", "action": "buy", "quantity": 100, "price": 12.5},
                {"date": "2024-01-14", "stock_code": "000002", "action": "sell", "quantity": 50, "price": 18.6}
            ]
        else:
            return {
                "holdings": self.generate_mock_data("holdings"),
                "transactions": self.generate_mock_data("transactions"),
                "balance": 50000.0,
                "total_value": 56160.0,
                "profit_loss": 1200.0
            }
    
    async def process_agent_decision_internal(self, decision: AgentDecision) -> Dict[str, Any]:
        """处理Agent决策"""
        logger.info(f"🤖 处理Agent决策: {decision.action} {decision.stock_code} (置信度: {decision.confidence})")
        
        try:
            # 记录决策
            decision_record = decision.dict()
            decision_record["processed_at"] = datetime.now().isoformat()
            self.decision_history.append(decision_record)
            self.system_stats["decisions_made"] += 1
            
            # 限制决策历史长度
            if len(self.decision_history) > 500:
                self.decision_history = self.decision_history[-500:]
            
            # 如果置信度足够高，自动执行交易
            if decision.confidence >= 0.7:
                trade_result = await self.execute_trade_internal(
                    action=decision.action,
                    stock_code=decision.stock_code,
                    quantity=decision.quantity,
                    price=decision.price,
                    agent_id="auto_decision"
                )
                
                decision_record["auto_executed"] = True
                decision_record["trade_result"] = trade_result
                
                return {
                    "success": True,
                    "message": f"决策已记录并自动执行 (置信度: {decision.confidence})",
                    "decision_id": len(self.decision_history),
                    "trade_result": trade_result
                }
            else:
                decision_record["auto_executed"] = False
                decision_record["reason"] = f"置信度不足 ({decision.confidence} < 0.7)"
                
                return {
                    "success": True,
                    "message": f"决策已记录，置信度不足未自动执行 (置信度: {decision.confidence})",
                    "decision_id": len(self.decision_history),
                    "requires_manual_approval": True
                }
                
        except Exception as e:
            error_msg = f"处理Agent决策异常: {e}"
            logger.error(f"❌ {error_msg}")
            self.system_stats["errors_count"] += 1
            return {"success": False, "message": error_msg}
    
    async def check_cloud_connection(self) -> bool:
        """检查云端连接"""
        try:
            response = requests.get(f"{self.cloud_api_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    async def notify_cloud_trade_result(self, trade_record: Dict[str, Any]):
        """通知云端交易结果"""
        try:
            requests.post(
                f"{self.cloud_api_url}/local-trade-result",
                json=trade_record,
                timeout=10
            )
        except Exception as e:
            logger.warning(f"⚠️ 通知云端失败: {e}")
    
    async def handle_websocket_connection(self, websocket: WebSocket):
        """处理WebSocket连接"""
        await websocket.accept()
        self.websocket_connection = websocket
        logger.info("✅ WebSocket连接建立")
        
        try:
            while True:
                # 发送心跳和状态更新
                status_update = {
                    "type": "status_update",
                    "timestamp": datetime.now().isoformat(),
                    "stats": self.system_stats,
                    "recent_trades": self.trade_history[-5:],
                    "recent_decisions": self.decision_history[-5:]
                }
                
                await websocket.send_text(json.dumps(status_update))
                await asyncio.sleep(30)  # 每30秒发送一次状态更新
                
        except WebSocketDisconnect:
            logger.info("🔌 WebSocket连接断开")
            self.websocket_connection = None
        except Exception as e:
            logger.error(f"❌ WebSocket错误: {e}")
            self.websocket_connection = None
    
    async def start_system(self):
        """启动系统"""
        logger.info("🚀 启动完整本地交易系统")
        self.running = True
        
        # 启动HTTP服务器
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=8888,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        logger.info("📍 服务地址:")
        logger.info("  - HTTP API: http://localhost:8888")
        logger.info("  - WebSocket: ws://localhost:8888/ws")
        logger.info("  - API文档: http://localhost:8888/docs")
        
        await server.serve()

# 全局系统实例
trading_system = CompleteLocalTradingSystem()

def main():
    """主函数"""
    try:
        asyncio.run(trading_system.start_system())
    except KeyboardInterrupt:
        logger.info("👋 系统已停止")
    except Exception as e:
        logger.error(f"❌ 系统启动失败: {e}")

class CloudAgentSystem:
    """云端Agent系统"""

    def __init__(self, local_api_url: str = "http://localhost:8888"):
        self.local_api_url = local_api_url
        self.agent_id = f"cloud_agent_{int(time.time())}"
        self.running = False
        self.market_data = []
        self.decisions = []

    async def start_agent(self):
        """启动Agent"""
        logger.info(f"🤖 启动云端Agent: {self.agent_id}")
        self.running = True

        # 检查本地连接
        if not await self.check_local_connection():
            logger.error("❌ 无法连接到本地交易系统")
            return

        # 启动市场监控
        await self.start_market_monitoring()

    async def check_local_connection(self) -> bool:
        """检查本地连接"""
        try:
            response = requests.get(f"{self.local_api_url}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ 本地连接正常 - 模式: {data.get('mode')}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 本地连接失败: {e}")
            return False

    async def start_market_monitoring(self):
        """启动市场监控"""
        logger.info("📊 开始市场监控和决策...")

        # 模拟市场数据
        market_data = [
            {"code": "000001", "name": "平安银行", "price": 12.85, "change": 4.2, "volume": 2500000},
            {"code": "000002", "name": "万科A", "price": 18.76, "change": -2.8, "volume": 1800000},
            {"code": "BJ430001", "name": "北交所测试", "price": 15.20, "change": 5.8, "volume": 1200000}
        ]

        for stock in market_data:
            decision = await self.analyze_and_decide(stock)
            if decision:
                await self.execute_decision(decision)
            await asyncio.sleep(2)  # 模拟分析间隔

    async def analyze_and_decide(self, stock_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """分析并决策"""
        code = stock_data["code"]
        price = stock_data["price"]
        change = stock_data["change"]
        volume = stock_data["volume"]

        logger.info(f"📈 分析 {code}: 价格¥{price}, 涨跌{change:+.2f}%, 成交量{volume:,}")

        # 简单策略
        if change > 3.0 and volume > 1000000:
            return {
                "action": "buy",
                "stock_code": code,
                "stock_name": stock_data["name"],
                "quantity": 100,
                "price": price,
                "confidence": 0.8,
                "reason": f"涨幅{change:.2f}%，成交量{volume:,}，买入信号",
                "timestamp": datetime.now().isoformat()
            }
        elif change < -2.0:
            return {
                "action": "sell",
                "stock_code": code,
                "stock_name": stock_data["name"],
                "quantity": 100,
                "price": price,
                "confidence": 0.7,
                "reason": f"跌幅{change:.2f}%，止损信号",
                "timestamp": datetime.now().isoformat()
            }

        logger.info("💤 策略判断: 持有观望")
        return None

    async def execute_decision(self, decision: Dict[str, Any]):
        """执行决策"""
        try:
            logger.info(f"🎯 执行决策: {decision['action']} {decision['stock_code']} (置信度: {decision['confidence']})")

            # 发送决策到本地系统
            response = requests.post(
                f"{self.local_api_url}/agent-decision",
                json=decision,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ 决策执行成功: {result['message']}")
                self.decisions.append({**decision, "result": result})
            else:
                logger.error(f"❌ 决策执行失败: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ 执行决策异常: {e}")

async def run_cloud_agent():
    """运行云端Agent"""
    agent = CloudAgentSystem()
    await agent.start_agent()

def start_cloud_agent():
    """启动云端Agent"""
    asyncio.run(run_cloud_agent())

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "agent":
        # 启动云端Agent
        start_cloud_agent()
    else:
        # 启动本地交易系统
        main()
