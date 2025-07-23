"""
AI自动交易控制器
负责连接AI决策系统和交易执行系统
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import logging
import asyncio
import json
import time
from datetime import datetime

from services.brokers.ths_dongwu_broker import THSDongwuBroker
from ai.strategy_optimizer import StrategyOptimizer
from utils.websocket_manager import WebSocketManager

router = APIRouter(prefix="/ai-trading", tags=["ai-trading"])

# 管理所有WebSocket连接
ws_manager = WebSocketManager()

# 模型定义
class TradeDecision(BaseModel):
    """交易决策模型"""
    symbol: str = Field(..., description="证券代码")
    name: Optional[str] = Field(None, description="证券名称")
    action: str = Field(..., description="交易动作:BUY,SELL")
    price: float = Field(..., description="价格")
    volume: int = Field(..., description="数量")
    reason: str = Field(..., description="交易理由")
    confidence: float = Field(..., description="置信度 0-1")
    strategy_id: str = Field(..., description="策略ID")
    timestamp: Optional[str] = Field(None, description="决策时间")

class AITradingSettings(BaseModel):
    """AI交易设置"""
    auto_trading: bool = Field(False, description="是否启用自动交易")
    min_confidence: float = Field(0.7, description="最低置信度阈值,低于此值的不会执行")
    max_order_value: float = Field(10000.0, description="单笔订单最大金额限制")
    session_id: Optional[str] = Field(None, description="交易会话ID")
    broker_type: str = Field("THS_DONGWU", description="券商类型")
    verification_required: bool = Field(True, description="是否需要人工确认交易")

# 全局设置
ai_trading_settings = AITradingSettings()

# 活跃的AI交易状态
active_ai_trading = {
    "status": "stopped",  # "running", "stopped", "paused"
    "broker": None,
    "active_strategies": [],
    "start_time": None,
    "trade_history": [],
    "last_decision": None,
    "error": None
}

# AI策略优化器
strategy_optimizer = StrategyOptimizer()

@router.post("/settings", response_model=Dict)
async def update_settings(settings: AITradingSettings):
    """更新AI交易设置"""
    global ai_trading_settings
    ai_trading_settings = settings
    
    # 广播设置变更
    await ws_manager.broadcast_json({
        "type": "settings_updated",
        "data": settings.dict()
    })
    
    return {
        "success": True,
        "message": "设置已更新",
        "data": settings.dict()
    }

@router.get("/settings", response_model=Dict)
async def get_settings():
    """获取AI交易设置"""
    return {
        "success": True,
        "data": ai_trading_settings.dict()
    }

@router.post("/start", response_model=Dict)
async def start_ai_trading(background_tasks: BackgroundTasks, session_id: str = None):
    """启动AI自动交易"""
    global active_ai_trading
    
    if active_ai_trading["status"] == "running":
        return {
            "success": False,
            "message": "AI交易系统已在运行中"
        }
    
    # 检查会话ID
    if not session_id and not ai_trading_settings.session_id:
        return {
            "success": False,
            "message": "未提供交易会话ID,请先连接到交易账户"
        }
    
    # 使用提供的会话ID或默认设置中的会话ID
    use_session_id = session_id or ai_trading_settings.session_id
    
    try:
        # 初始化AI交易系统
        active_ai_trading = {
            "status": "running",
            "broker": "THS_DONGWU",
            "active_strategies": ["momentum", "mean_reversion", "trend_following"],
            "start_time": datetime.now().isoformat(),
            "trade_history": [],
            "last_decision": None,
            "error": None
        }
        
        # 在后台启动交易循环
        background_tasks.add_task(ai_trading_loop, use_session_id)
        
        # 广播状态变更
        await ws_manager.broadcast_json({
            "type": "ai_trading_started",
            "data": {
                "status": active_ai_trading["status"],
                "start_time": active_ai_trading["start_time"]
            }
        })
        
        return {
            "success": True,
            "message": "AI交易系统已启动",
            "data": {
                "status": active_ai_trading["status"],
                "start_time": active_ai_trading["start_time"]
            }
        }
    except Exception as e:
        logging.error(f"启动AI交易系统失败: {str(e)}")
        active_ai_trading["status"] = "stopped"
        active_ai_trading["error"] = str(e)
        
        return {
            "success": False,
            "message": f"启动AI交易系统失败: {str(e)}"
        }

@router.post("/stop", response_model=Dict)
async def stop_ai_trading():
    """停止AI自动交易"""
    global active_ai_trading
    
    if active_ai_trading["status"] != "running":
        return {
            "success": False,
            "message": "AI交易系统未在运行"
        }
    
    active_ai_trading["status"] = "stopped"
    
    # 广播状态变更
    await ws_manager.broadcast_json({
        "type": "ai_trading_stopped",
        "data": {
            "status": "stopped",
            "end_time": datetime.now().isoformat()
        }
    })
    
    return {
        "success": True,
        "message": "AI交易系统已停止",
        "data": {
            "status": "stopped",
            "trade_count": len(active_ai_trading["trade_history"])
        }
    }

@router.post("/execute-decision", response_model=Dict)
async def execute_trade_decision(decision: TradeDecision, verify: bool = True):
    """手动执行交易决策"""
    if not ai_trading_settings.session_id:
        return {
            "success": False,
            "message": "未连接到交易账户,请先连接"
        }
    
    # 如果需要人工确认且verify=False,返回待确认状态
    if ai_trading_settings.verification_required and not verify:
        return {
            "success": True,
            "message": "交易决策已生成,等待确认",
            "data": {
                "decision": decision.dict(),
                "requires_verification": True
            }
        }
    
    # 执行交易
    result = await execute_trade(ai_trading_settings.session_id, decision)
    
    # 记录交易历史
    if result["success"]:
        active_ai_trading["trade_history"].append({
            **decision.dict(),
            "execution_time": datetime.now().isoformat(),
            "execution_result": result
        })
    
    return result

@router.get("/status", response_model=Dict)
async def get_ai_trading_status():
    """获取AI交易系统状态"""
    return {
        "success": True,
        "data": {
            "status": active_ai_trading["status"],
            "broker": active_ai_trading["broker"],
            "active_strategies": active_ai_trading["active_strategies"],
            "start_time": active_ai_trading["start_time"],
            "trade_count": len(active_ai_trading["trade_history"]),
            "last_decision": active_ai_trading["last_decision"],
            "error": active_ai_trading["error"]
        }
    }

@router.get("/history", response_model=Dict)
async def get_trade_history(limit: int = 20, offset: int = 0):
    """获取交易历史"""
    history = active_ai_trading["trade_history"]
    total = len(history)
    
    # 分页获取
    paginated = history[offset:offset+limit]
    
    return {
        "success": True,
        "data": {
            "trades": paginated,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    }

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接以获取实时AI交易更新"""
    await ws_manager.connect(websocket)
    
    try:
        # 发送初始状态
        await websocket.send_json({
            "type": "init",
            "data": {
                "status": active_ai_trading["status"],
                "settings": ai_trading_settings.dict(),
                "trade_count": len(active_ai_trading["trade_history"]),
                "last_decision": active_ai_trading["last_decision"]
            }
        })
        
        # 等待客户端消息
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理客户端请求
            if message.get("action") == "get_status":
                await websocket.send_json({
                    "type": "status_update",
                    "data": {
                        "status": active_ai_trading["status"],
                        "trade_count": len(active_ai_trading["trade_history"]),
                        "last_decision": active_ai_trading["last_decision"],
                        "timestamp": datetime.now().isoformat()
                    }
                })
    
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

async def ai_trading_loop(session_id: str):
    """AI交易主循环"""
    logging.info(f"AI交易循环已启动,会话ID: {session_id}")
    
    while active_ai_trading["status"] == "running":
        try:
            # 1. 获取市场数据
            market_data = await get_market_data()
            
            # 2. 运行AI策略生成决策
            decisions = await generate_trade_decisions(market_data)
            
            if decisions:
                # 记录最后决策
                active_ai_trading["last_decision"] = decisions[0].dict()
                
                # 广播决策信息
                await ws_manager.broadcast_json({
                    "type": "new_decision",
                    "data": {
                        "decisions": [d.dict() for d in decisions],
                        "timestamp": datetime.now().isoformat()
                    }
                })
                
                # 如果启用了自动交易且不需要人工确认,则自动执行
                if ai_trading_settings.auto_trading and not ai_trading_settings.verification_required:
                    for decision in decisions:
                        # 检查置信度阈值
                        if decision.confidence >= ai_trading_settings.min_confidence:
                            # 执行交易
                            result = await execute_trade(session_id, decision)
                            
                            # 记录交易历史
                            if result["success"]:
                                trade_record = {
                                    **decision.dict(),
                                    "execution_time": datetime.now().isoformat(),
                                    "execution_result": result
                                }
                                active_ai_trading["trade_history"].append(trade_record)
                                
                                # 广播交易结果
                                await ws_manager.broadcast_json({
                                    "type": "trade_executed",
                                    "data": trade_record
                                })
            
            # 等待一段时间再进行下一轮决策
            await asyncio.sleep(10)  # 可以根据需要调整间隔
            
        except Exception as e:
            logging.error(f"AI交易循环异常: {str(e)}")
            active_ai_trading["error"] = str(e)
            
            # 广播错误信息
            await ws_manager.broadcast_json({
                "type": "error",
                "data": {
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            })
            
            # 等待一段时间后重试
            await asyncio.sleep(30)
    
    logging.info("AI交易循环已停止")

async def get_market_data():
    """获取市场数据"""
    # 在实际应用中,这里应该从行情API获取真实数据
    # 这里使用模拟数据作为示例
    return {
        "time": datetime.now().isoformat(),
        "symbols": {
            "600519": {  # 贵州茅台
                "price": 1826.50,
                "change_pct": 0.0234,
                "volume": 1520000,
                "turnover": 2774280000.0,
                "high": 1840.0,
                "low": 1790.0,
                "open": 1800.0,
                "prev_close": 1785.0
            },
            "000858": {  # 五粮液
                "price": 185.20,
                "change_pct": 0.0158,
                "volume": 4562000,
                "turnover": 844914400.0,
                "high": 187.5,
                "low": 182.3,
                "open": 183.1,
                "prev_close": 182.32
            }
            # 可以添加更多股票
        },
        "indices": {
            "000001": {  # 上证指数
                "price": 3458.23,
                "change_pct": 0.0135
            },
            "399001": {  # 深证成指
                "price": 14256.89,
                "change_pct": 0.0162
            }
        }
    }

async def generate_trade_decisions(market_data):
    """生成交易决策"""
    # 在实际应用中,这里应该调用AI模型生成真实的交易决策
    # 这里使用模拟决策作为示例
    
    # 从市场数据中选择符合条件的股票
    decisions = []
    
    # 简单示例:价格上涨超过2%的股票考虑买入
    for symbol, data in market_data["symbols"].items():
        if data["change_pct"] > 0.02:
            # 生成买入决策
            decision = TradeDecision(
                symbol=symbol,
                name=get_stock_name(symbol),
                action="BUY",
                price=data["price"],
                volume=calculate_volume(data["price"], 5000),  # 假设5000元资金
                reason=f"价格上涨{data['change_pct']*100:.2f}%,动量信号强烈",
                confidence=min(data["change_pct"] * 10, 0.95),  # 根据涨幅计算置信度
                strategy_id="momentum",
                timestamp=datetime.now().isoformat()
            )
            decisions.append(decision)
        
        # 股票跌超2%考虑买入(反转策略)
        elif data["change_pct"] < -0.02:
            # 生成买入决策(反转)
            decision = TradeDecision(
                symbol=symbol,
                name=get_stock_name(symbol),
                action="BUY",
                price=data["price"],
                volume=calculate_volume(data["price"], 5000),
                reason=f"价格下跌{abs(data['change_pct'])*100:.2f}%,可能超卖,反转信号",
                confidence=min(abs(data["change_pct"]) * 8, 0.85),
                strategy_id="mean_reversion",
                timestamp=datetime.now().isoformat()
            )
            decisions.append(decision)
    
    # 使用策略优化器优化决策(示例)
    # 实际系统中,这里应该使用真正的AI模型分析
    if hasattr(strategy_optimizer, 'evaluate_decisions'):
        for decision in decisions:
            # 根据策略优化器调整置信度
            decision.confidence = min(decision.confidence * 1.1, 0.95)
    
    return decisions

async def execute_trade(session_id: str, decision: TradeDecision):
    """执行交易决策"""
    try:
        # 连接到交易服务API
        response = await call_ths_service_api(
            session_id=session_id,
            symbol=decision.symbol,
            price=decision.price,
            volume=decision.volume,
            direction=decision.action
        )
        
        if response.get("success"):
            return {
                "success": True,
                "message": f"交易执行成功: {decision.action} {decision.symbol}",
                "data": response.get("data", {})
            }
        else:
            return {
                "success": False,
                "message": f"交易执行失败: {response.get('message', '未知错误')}"
            }
    except Exception as e:
        logging.error(f"执行交易决策异常: {str(e)}")
        return {
            "success": False,
            "message": f"执行交易异常: {str(e)}"
        }

async def call_ths_service_api(session_id: str, symbol: str, price: float, volume: int, direction: str):
    """调用同花顺交易服务API"""
    # 在实际应用中,这里应该调用真实的API接口
    # 这里使用模拟响应作为示例
    
    # 模拟调用API
    time.sleep(0.5)  # 模拟延迟
    
    # 模拟成功响应
    return {
        "success": True,
        "message": "委托已提交",
        "data": {
            "order_id": f"AI_{int(time.time())}",
            "symbol": symbol,
            "price": price,
            "volume": volume,
            "direction": direction,
            "status": "SUBMITTED",
            "message": "委托已提交"
        }
    }

def get_stock_name(symbol: str) -> str:
    """根据证券代码获取证券名称"""
    # 示例股票名称映射
    stock_names = {
        "600519": "贵州茅台",
        "000858": "五粮液",
        "601318": "中国平安",
        "600036": "招商银行"
    }
    return stock_names.get(symbol, "未知股票")

def calculate_volume(price: float, amount: float) -> int:
    """根据价格和金额计算数量"""
    # 计算能买多少股
    volume = int(amount / price / 100) * 100  # 按手(100股)取整
    return max(volume, 100)  # 至少买1手 
