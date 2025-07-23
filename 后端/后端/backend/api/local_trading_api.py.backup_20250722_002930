#!/usr/bin/env python3
"""
本地交易API服务
为Agent提供HTTP API接口调用本地交易软件
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 导入本地交易集成模块
try:
    from agent_local_trading_integration import (
        AgentTradingController, 
        TradeRequest, 
        TradeResult,
        agent_trading_controller
    )
    LOCAL_TRADING_AVAILABLE = True
except ImportError as e:
    logging.warning(f"本地交易模块不可用: {e}")
    LOCAL_TRADING_AVAILABLE = False

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/local-trading", tags=["本地交易"])

# Pydantic模型
class TradeRequestModel(BaseModel):
    """交易请求模型"""
    action: str = Field(..., description="交易动作: buy/sell")
    stock_code: str = Field(..., description="股票代码")
    quantity: int = Field(..., gt=0, description="交易数量")
    price: Optional[float] = Field(None, description="交易价格，None表示市价")

class TradeResponseModel(BaseModel):
    """交易响应模型"""
    success: bool
    message: str
    trade_id: Optional[str] = None
    timestamp: str

class ExportRequestModel(BaseModel):
    """导出请求模型"""
    data_type: str = Field(default="all", description="导出数据类型: all/holdings/transactions/orders")

class StatusResponseModel(BaseModel):
    """状态响应模型"""
    controller_running: bool
    local_interface_initialized: bool
    trading_software_active: bool
    trade_history_count: int
    last_export_time: Optional[str] = None

@router.get("/status", response_model=StatusResponseModel)
async def get_trading_status():
    """获取本地交易状态"""
    if not LOCAL_TRADING_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="本地交易模块不可用"
        )
    
    try:
        status = agent_trading_controller.get_status()
        
        return StatusResponseModel(
            controller_running=status["controller_running"],
            local_interface_initialized=status["local_interface_initialized"],
            trading_software_active=status["trading_software_status"].get("trading_software_active", False),
            trade_history_count=status["trade_history_count"],
            last_export_time=status["last_export_time"]
        )
    except Exception as e:
        logger.error(f"获取交易状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {e}")

@router.post("/start")
async def start_trading_controller():
    """启动交易控制器"""
    if not LOCAL_TRADING_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="本地交易模块不可用"
        )
    
    try:
        success = agent_trading_controller.start()
        
        if success:
            return {"success": True, "message": "交易控制器启动成功"}
        else:
            raise HTTPException(status_code=500, detail="交易控制器启动失败")
            
    except Exception as e:
        logger.error(f"启动交易控制器失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动失败: {e}")

@router.post("/stop")
async def stop_trading_controller():
    """停止交易控制器"""
    if not LOCAL_TRADING_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="本地交易模块不可用"
        )
    
    try:
        agent_trading_controller.stop()
        return {"success": True, "message": "交易控制器已停止"}
        
    except Exception as e:
        logger.error(f"停止交易控制器失败: {e}")
        raise HTTPException(status_code=500, detail=f"停止失败: {e}")

@router.post("/execute", response_model=TradeResponseModel)
async def execute_trade(trade_request: TradeRequestModel):
    """执行交易"""
    if not LOCAL_TRADING_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="本地交易模块不可用"
        )
    
    try:
        # 转换为内部格式
        decision = {
            "action": trade_request.action,
            "stock_code": trade_request.stock_code,
            "quantity": trade_request.quantity,
            "price": trade_request.price
        }
        
        # 执行交易
        result = agent_trading_controller.execute_agent_decision(decision)
        
        return TradeResponseModel(
            success=result["success"],
            message=result["message"],
            trade_id=result.get("trade_id"),
            timestamp=result.get("timestamp", datetime.now().isoformat())
        )
        
    except Exception as e:
        logger.error(f"执行交易失败: {e}")
        raise HTTPException(status_code=500, detail=f"交易执行失败: {e}")

@router.post("/export")
async def export_data(export_request: ExportRequestModel):
    """导出交易数据"""
    if not LOCAL_TRADING_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="本地交易模块不可用"
        )
    
    try:
        result = agent_trading_controller.local_interface.export_data(
            export_request.data_type
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "export_time": result.get("export_time"),
                "results": result.get("results", {})
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        logger.error(f"导出数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出失败: {e}")

@router.get("/portfolio")
async def get_portfolio():
    """获取投资组合数据"""
    if not LOCAL_TRADING_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="本地交易模块不可用"
        )
    
    try:
        result = agent_trading_controller.get_portfolio_data()
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "data_files": result.get("data_files", []),
                "export_result": result.get("export_result", {})
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        logger.error(f"获取投资组合失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取投资组合失败: {e}")

@router.get("/history")
async def get_trade_history():
    """获取交易历史"""
    if not LOCAL_TRADING_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="本地交易模块不可用"
        )
    
    try:
        # 获取交易历史
        history = agent_trading_controller.trade_history
        
        # 转换为可序列化格式
        serializable_history = []
        for item in history:
            serializable_history.append({
                "request": {
                    "action": item["request"].action,
                    "stock_code": item["request"].stock_code,
                    "quantity": item["request"].quantity,
                    "price": item["request"].price,
                    "timestamp": item["request"].timestamp.isoformat()
                },
                "result": {
                    "success": item["result"].success,
                    "message": item["result"].message,
                    "trade_id": item["result"].trade_id,
                    "timestamp": item["result"].timestamp.isoformat()
                },
                "timestamp": item["timestamp"].isoformat()
            })
        
        return {
            "success": True,
            "history": serializable_history,
            "total_count": len(serializable_history)
        }
        
    except Exception as e:
        logger.error(f"获取交易历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取历史失败: {e}")

@router.post("/test")
async def test_local_trading():
    """测试本地交易功能"""
    if not LOCAL_TRADING_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="本地交易模块不可用"
        )
    
    try:
        # 检查状态
        status = agent_trading_controller.get_status()
        
        # 测试导出功能
        export_result = agent_trading_controller.local_interface.export_data("holdings")
        
        return {
            "success": True,
            "message": "本地交易功能测试完成",
            "status": status,
            "export_test": export_result
        }
        
    except Exception as e:
        logger.error(f"测试本地交易功能失败: {e}")
        raise HTTPException(status_code=500, detail=f"测试失败: {e}")

# Agent决策执行的便捷接口
@router.post("/agent/buy")
async def agent_buy(
    stock_code: str,
    quantity: int,
    price: Optional[float] = None
):
    """Agent买入接口"""
    trade_request = TradeRequestModel(
        action="buy",
        stock_code=stock_code,
        quantity=quantity,
        price=price
    )
    return await execute_trade(trade_request)

@router.post("/agent/sell")
async def agent_sell(
    stock_code: str,
    quantity: int,
    price: Optional[float] = None
):
    """Agent卖出接口"""
    trade_request = TradeRequestModel(
        action="sell",
        stock_code=stock_code,
        quantity=quantity,
        price=price
    )
    return await execute_trade(trade_request)

@router.get("/agent/portfolio")
async def agent_get_portfolio():
    """Agent获取投资组合接口"""
    return await get_portfolio()

@router.post("/agent/export/{data_type}")
async def agent_export_data(data_type: str):
    """Agent导出数据接口"""
    export_request = ExportRequestModel(data_type=data_type)
    return await export_data(export_request)

# 健康检查
@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "local_trading_available": LOCAL_TRADING_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

# 获取API文档
@router.get("/docs")
async def get_api_docs():
    """获取API文档"""
    return {
        "title": "本地交易API",
        "description": "为Agent提供本地交易软件接口",
        "version": "1.0.0",
        "endpoints": {
            "GET /status": "获取交易状态",
            "POST /start": "启动交易控制器",
            "POST /stop": "停止交易控制器",
            "POST /execute": "执行交易",
            "POST /export": "导出数据",
            "GET /portfolio": "获取投资组合",
            "GET /history": "获取交易历史",
            "POST /test": "测试功能",
            "POST /agent/buy": "Agent买入",
            "POST /agent/sell": "Agent卖出",
            "GET /agent/portfolio": "Agent获取投资组合",
            "POST /agent/export/{data_type}": "Agent导出数据"
        },
        "requirements": [
            "working-trader-FIXED模块化代码",
            "本地交易软件运行",
            "Windows环境"
        ]
    }
