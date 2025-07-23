#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent交易API - 提供Agent与快捷键交易的集成接口
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import asyncio
from datetime import datetime

from backend.ai.agent_hotkey_trader import AgentHotkeyTrader
from backend.ai.agent_system import TradingAgent

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/agent-trading", tags=["agent-trading"])

# 全局实例
agent_hotkey_trader: Optional[AgentHotkeyTrader] = None
trading_agent: Optional[TradingAgent] = None

# Pydantic模型
class TradingDecision(BaseModel):
    action: str  # buy, sell, hold
    symbol: str
    price: float
    quantity: int
    confidence: float
    reason: str = ""
    position_size: float = 0.1

class TradingConfig(BaseModel):
    auto_trading_enabled: bool = False
    auto_confirm: bool = False
    max_daily_trades: int = 50
    max_position_size: float = 0.2
    min_confidence_threshold: float = 0.7
    min_trade_interval: int = 60

class AgentConfig(BaseModel):
    enable_learning: bool = True
    decision_interval: int = 60
    market_analysis_enabled: bool = True
    risk_management_enabled: bool = True

@router.on_event("startup")
async def startup_event():
    """启动时初始化"""
    global agent_hotkey_trader, trading_agent
    
    try:
        # 初始化Agent快捷键交易器
        config = {
            "max_daily_trades": 50,
            "max_position_size": 0.2,
            "min_confidence_threshold": 0.7,
            "auto_confirm": False
        }
        agent_hotkey_trader = AgentHotkeyTrader(config)
        
        # 初始化Trading Agent
        agent_config = {
            "name": "HotkeyTradingAgent",
            "loop_interval": 60,
            "monitor_interval": 30
        }
        trading_agent = TradingAgent(agent_config)
        
        logger.info("Agent交易API初始化完成")
        
    except Exception as e:
        logger.error(f"Agent交易API初始化失败: {str(e)}")

@router.post("/start")
async def start_trading_system():
    """启动Agent交易系统"""
    try:
        if not agent_hotkey_trader:
            raise HTTPException(status_code=500, detail="Agent快捷键交易器未初始化")
        
        # 启动快捷键交易器
        hotkey_result = await agent_hotkey_trader.start()
        if not hotkey_result:
            raise HTTPException(status_code=500, detail="快捷键交易器启动失败")
        
        # 启动Trading Agent
        if trading_agent:
            agent_result = await trading_agent.start()
            if not agent_result:
                logger.warning("Trading Agent启动失败,但快捷键交易器已启动")
        
        return {
            "status": "success",
            "message": "Agent交易系统启动成功",
            "hotkey_trader_active": agent_hotkey_trader.active,
            "trading_agent_active": trading_agent.active if trading_agent else False
        }
        
    except Exception as e:
        logger.error(f"启动Agent交易系统失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_trading_system():
    """停止Agent交易系统"""
    try:
        results = {}
        
        # 停止快捷键交易器
        if agent_hotkey_trader:
            await agent_hotkey_trader.stop()
            results["hotkey_trader"] = "stopped"
        
        # 停止Trading Agent
        if trading_agent:
            await trading_agent.stop()
            results["trading_agent"] = "stopped"
        
        return {
            "status": "success",
            "message": "Agent交易系统已停止",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"停止Agent交易系统失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-decision")
async def execute_trading_decision(decision: TradingDecision):
    """执行交易决策"""
    try:
        if not agent_hotkey_trader:
            raise HTTPException(status_code=500, detail="Agent快捷键交易器未初始化")
        
        if not agent_hotkey_trader.active:
            raise HTTPException(status_code=400, detail="Agent交易系统未启动")
        
        # 转换为字典格式
        decision_dict = decision.dict()
        
        # 执行决策
        result = await agent_hotkey_trader.execute_agent_decision(decision_dict)
        
        return {
            "status": "success",
            "message": "决策执行完成",
            "decision": decision_dict,
            "execution_result": result
        }
        
    except Exception as e:
        logger.error(f"执行交易决策失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent-decision")
async def get_agent_decision(symbol: str, context: Dict[str, Any] = None):
    """获取Agent决策"""
    try:
        if not trading_agent:
            raise HTTPException(status_code=500, detail="Trading Agent未初始化")
        
        if not trading_agent.active:
            raise HTTPException(status_code=400, detail="Trading Agent未启动")
        
        # 构建决策上下文
        decision_context = context or {}
        decision_context["symbol"] = symbol
        decision_context["timestamp"] = datetime.now().isoformat()
        
        # 获取Agent决策
        decision = await trading_agent.make_decision(decision_context)
        
        return {
            "status": "success",
            "message": "Agent决策获取成功",
            "decision": decision,
            "context": decision_context
        }
        
    except Exception as e:
        logger.error(f"获取Agent决策失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto-trade")
async def execute_auto_trade(symbol: str, background_tasks: BackgroundTasks):
    """执行自动交易(获取Agent决策并自动执行)"""
    try:
        if not agent_hotkey_trader or not trading_agent:
            raise HTTPException(status_code=500, detail="系统组件未初始化")
        
        if not agent_hotkey_trader.active or not trading_agent.active:
            raise HTTPException(status_code=400, detail="系统未完全启动")
        
        # 获取Agent决策
        decision_context = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "auto_execution": True
        }
        
        decision = await trading_agent.make_decision(decision_context)
        
        if "error" in decision:
            raise HTTPException(status_code=500, detail=f"Agent决策失败: {decision['error']}")
        
        # 执行决策
        execution_result = await agent_hotkey_trader.execute_agent_decision(decision)
        
        return {
            "status": "success",
            "message": "自动交易执行完成",
            "decision": decision,
            "execution_result": execution_result
        }
        
    except Exception as e:
        logger.error(f"自动交易执行失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_system_status():
    """获取系统状态"""
    try:
        status = {
            "timestamp": datetime.now().isoformat(),
            "hotkey_trader": None,
            "trading_agent": None
        }
        
        # 获取快捷键交易器状态
        if agent_hotkey_trader:
            status["hotkey_trader"] = agent_hotkey_trader.get_status()
        
        # 获取Trading Agent状态
        if trading_agent:
            status["trading_agent"] = await trading_agent.get_status()
        
        return {
            "status": "success",
            "data": status
        }
        
    except Exception as e:
        logger.error(f"获取系统状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/position")
async def get_position_info():
    """获取持仓信息"""
    try:
        if not agent_hotkey_trader:
            raise HTTPException(status_code=500, detail="Agent快捷键交易器未初始化")
        
        result = await agent_hotkey_trader.get_position_info()
        
        return {
            "status": "success",
            "message": "持仓信息获取成功",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"获取持仓信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fund")
async def get_fund_info():
    """获取资金信息"""
    try:
        if not agent_hotkey_trader:
            raise HTTPException(status_code=500, detail="Agent快捷键交易器未初始化")
        
        result = await agent_hotkey_trader.get_fund_info()
        
        return {
            "status": "success",
            "message": "资金信息获取成功",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"获取资金信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config/trading")
async def update_trading_config(config: TradingConfig):
    """更新交易配置"""
    try:
        if not agent_hotkey_trader:
            raise HTTPException(status_code=500, detail="Agent快捷键交易器未初始化")
        
        # 更新配置
        config_dict = config.dict()
        agent_hotkey_trader.update_config(config_dict)
        
        # 启用/禁用自动交易
        agent_hotkey_trader.enable_auto_trading(config.auto_trading_enabled)
        
        return {
            "status": "success",
            "message": "交易配置更新成功",
            "config": config_dict
        }
        
    except Exception as e:
        logger.error(f"更新交易配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_execution_history(limit: int = 50):
    """获取执行历史"""
    try:
        if not agent_hotkey_trader:
            raise HTTPException(status_code=500, detail="Agent快捷键交易器未初始化")
        
        history = agent_hotkey_trader.get_execution_history(limit)
        
        return {
            "status": "success",
            "message": "执行历史获取成功",
            "data": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error(f"获取执行历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history")
async def clear_execution_history():
    """清空执行历史"""
    try:
        if not agent_hotkey_trader:
            raise HTTPException(status_code=500, detail="Agent快捷键交易器未初始化")
        
        agent_hotkey_trader.clear_execution_history()
        
        return {
            "status": "success",
            "message": "执行历史已清空"
        }
        
    except Exception as e:
        logger.error(f"清空执行历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
