"""
Simple FastAPI application for testing Cloudflare tunnel connection
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import asyncio
from typing import List
from datetime import datetime

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Create FastAPI application
app = FastAPI(
    title="Stock Trading System API",
    description="API for automatic stock trading system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Stock Trading System API is running", "status": "ok"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2025-06-28T12:00:00Z"}

@app.get("/api/health")
async def api_health_check():
    """API Health check endpoint for mobile app"""
    return {
        "status": "healthy",
        "message": "APP API服务正常",
        "timestamp": datetime.now().isoformat(),
        "api_version": "1.0",
        "app_support": True,
        "service": "stock-trading-backend"
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "1.0.0",
        "status": "running",
        "services": {
            "trading": "available",
            "market_data": "available",
            "ai_analysis": "available"
        }
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint for connectivity"""
    return {
        "message": "Test endpoint working",
        "cloudflare_tunnel": "connected",
        "backend": "operational"
    }

# 交易API端点
@app.get("/api/trading/brokers")
async def get_brokers():
    """获取支持的券商列表"""
    return {
        "success": True,
        "data": [
            {"id": "dongwu", "name": "东吴证券", "status": "available"},
            {"id": "ths", "name": "同花顺", "status": "available"}
        ]
    }

@app.post("/api/trading/connect")
async def connect_broker():
    """连接券商"""
    return {
        "success": True,
        "message": "连接成功",
        "session_id": "mock_session_123"
    }

@app.post("/api/trading/disconnect")
async def disconnect_broker():
    """断开券商连接"""
    return {
        "success": True,
        "message": "断开连接成功"
    }

@app.get("/api/trading/account")
async def get_account():
    """获取账户信息"""
    return {
        "success": True,
        "data": {
            "account_id": "mock_account",
            "balance": 100000.00,
            "available": 95000.00,
            "market_value": 50000.00
        }
    }

@app.get("/api/trading/positions")
async def get_positions():
    """获取持仓信息"""
    return {
        "success": True,
        "data": [
            {
                "symbol": "000001",
                "name": "平安银行",
                "quantity": 1000,
                "price": 15.50,
                "market_value": 15500.00
            }
        ]
    }

@app.post("/api/trading/orders")
async def place_order():
    """下单"""
    return {
        "success": True,
        "data": {
            "order_id": "mock_order_123",
            "status": "submitted"
        }
    }

@app.get("/api/trading/orders")
async def get_orders():
    """获取委托列表"""
    return {
        "success": True,
        "data": []
    }

# Agent交易系统API端点
@app.get("/api/v1/agent-trading/status")
async def get_agent_status():
    """获取Agent交易系统状态"""
    return {
        "success": True,
        "data": {
            "status": "running",
            "running_time": "02:34:15",
            "trade_count": 8,
            "active_strategies": ["趋势跟踪", "量价分析"]
        }
    }

# 真实Agent交易API端点
@app.get("/api/agent-trading/fund")
async def get_agent_fund_info():
    """获取真实的资金信息"""
    try:
        # 直接调用余额读取模块
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))

        from fixed_balance_reader import get_balance_fixed

        # 获取真实的账户余额
        balance_result = get_balance_fixed()

        if balance_result and isinstance(balance_result, dict):
            # 处理真实的余额数据
            return {
                "status": "success",
                "message": "资金信息获取成功",
                "data": {
                    "total_assets": balance_result.get("total_assets", 0.0),
                    "available_cash": balance_result.get("available_cash", 0.0),
                    "market_value": balance_result.get("market_value", 0.0),
                    "frozen_amount": balance_result.get("frozen_amount", 0.0)
                }
            }
        else:
            return {
                "status": "error",
                "message": "获取真实余额失败或返回数据格式错误"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"获取资金信息失败: {str(e)}"
        }

@app.get("/api/agent-trading/position")
async def get_agent_position_info():
    """获取真实的持仓信息"""
    try:
        # 直接调用持仓导出模块
        import sys
        import os
        import glob
        import pandas as pd
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))

        from trader_export_real import export_holdings

        # 获取真实的持仓数据
        export_success = export_holdings()

        if export_success:
            # 导出成功，现在读取导出的文件
            try:
                # 查找最新的持仓文件
                holdings_files = glob.glob("持仓数据_*.csv")
                if not holdings_files:
                    return {"status": "error", "message": "未找到持仓数据文件"}

                latest_file = max(holdings_files, key=lambda f: os.path.getctime(f))

                # 读取并解析CSV文件
                df = pd.read_csv(latest_file, encoding='gbk')

                # 转换数据格式
                formatted_positions = []
                for index, row in df.iterrows():
                    try:
                        position = {
                            "symbol": str(row.get('证券代码', '')).strip(),
                            "name": str(row.get('证券名称', '')).strip(),
                            "volume": int(float(row.get('股票余额', 0))),
                            "available_volume": int(float(row.get('可用余额', 0))),
                            "cost_price": float(row.get('成本价', 0)),
                            "current_price": float(row.get('最新价', 0)),
                            "market_value": float(row.get('最新市值', 0)),
                            "profit_loss": float(row.get('浮动盈亏', 0)),
                            "profit_loss_ratio": float(row.get('盈亏比例(%)', 0)) / 100 if row.get('盈亏比例(%)', 0) else 0,
                            "position_date": str(row.get('买入日期', '')).strip()
                        }

                        # 只添加有效的持仓
                        if position["symbol"] and position["volume"] > 0:
                            formatted_positions.append(position)

                    except Exception as e:
                        continue

                return {
                    "status": "success",
                    "message": "持仓信息获取成功",
                    "data": {
                        "total_value": sum(pos["market_value"] for pos in formatted_positions),
                        "positions": formatted_positions
                    }
                }

            except Exception as e:
                return {"status": "error", "message": f"解析持仓文件失败: {str(e)}"}
        else:
            return {"status": "error", "message": "持仓数据导出失败"}

    except Exception as e:
        return {
            "status": "error",
            "message": f"获取持仓信息失败: {str(e)}"
        }

@app.get("/api/v1/agent-trading/system/status")
async def get_agent_system_status():
    """获取Agent系统详细状态"""
    return {
        "success": True,
        "data": {
            "isRunning": True,
            "availableCash": 10183.94,
            "holdingsCount": 0,
            "status": "running",
            "learning_progress": 85,
            "performance": {
                "win_rate": 0.72,
                "total_trades": 156,
                "profit_rate": 0.089
            }
        }
    }

@app.post("/api/v1/agent-trading/start")
async def start_agent():
    """启动Agent交易系统"""
    return {
        "success": True,
        "message": "Agent交易系统已启动",
        "data": {
            "status": "running",
            "session_id": "mock-session-123"
        }
    }

@app.post("/api/v1/agent-trading/stop")
async def stop_agent():
    """停止Agent交易系统"""
    return {
        "success": True,
        "message": "Agent交易系统已停止",
        "data": {
            "status": "stopped"
        }
    }

# 市场数据API端点
@app.get("/api/market/stocks")
async def get_stock_list():
    """获取股票列表"""
    return {
        "success": True,
        "data": [
            {"code": "000001", "name": "平安银行", "market": "SZ", "industry": "银行"},
            {"code": "600000", "name": "浦发银行", "market": "SH", "industry": "银行"},
            {"code": "000002", "name": "万科A", "market": "SZ", "industry": "房地产"},
            {"code": "600036", "name": "招商银行", "market": "SH", "industry": "银行"}
        ],
        "count": 4
    }

@app.get("/api/market/kdata/{code}")
async def get_kdata(code: str):
    """获取K线数据"""
    return {
        "success": True,
        "data": {
            "code": code,
            "name": "平安银行" if code == "000001" else "股票",
            "kdata": [
                {
                    "date": "2025-06-28",
                    "open": 15.20,
                    "high": 15.80,
                    "low": 15.10,
                    "close": 15.50,
                    "volume": 1000000
                }
            ]
        }
    }

# T+0交易API端点
@app.post("/api/t-trading/ai-trade-decision")
async def get_ai_trade_decision():
    """获取AI交易决策"""
    return {
        "success": True,
        "data": {
            "decision": "BUY",
            "confidence": 0.85,
            "reasoning": "基于技术分析和市场情绪的综合判断",
            "target_price": 15.80,
            "stop_loss": 15.20
        }
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        # 发送连接成功消息
        await manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "status": "connected",
                "message": "WebSocket连接成功"
            }),
            websocket
        )

        # 定期发送心跳
        async def send_heartbeat():
            while True:
                try:
                    await asyncio.sleep(30)
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "heartbeat",
                            "timestamp": "2025-06-28T12:00:00Z"
                        }),
                        websocket
                    )
                except:
                    break

        # 启动心跳任务
        heartbeat_task = asyncio.create_task(send_heartbeat())

        # 监听客户端消息
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # 回显消息
            await manager.send_personal_message(
                json.dumps({
                    "type": "echo",
                    "original_message": message,
                    "timestamp": "2025-06-28T12:00:00Z"
                }),
                websocket
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        heartbeat_task.cancel()
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("simple_app:app", host="0.0.0.0", port=8000, reload=True)
