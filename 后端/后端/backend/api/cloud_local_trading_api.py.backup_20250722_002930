#!/usr/bin/env python3
"""
云端本地交易API
云端Agent通过此API向本地电脑发送交易指令
"""

import os
import sys
import json
import time
import logging
import asyncio
import websockets
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
import requests
import uuid

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

# 数据模型
class LocalTradeCommand(BaseModel):
    """本地交易命令"""
    action: str = Field(..., description="交易动作: buy/sell")
    stock_code: str = Field(..., description="股票代码")
    quantity: int = Field(..., gt=0, description="交易数量")
    price: Optional[float] = Field(None, description="交易价格，None表示市价")
    agent_id: Optional[str] = Field(None, description="Agent ID")

class LocalExportCommand(BaseModel):
    """本地导出命令"""
    data_type: str = Field(default="all", description="导出数据类型")
    agent_id: Optional[str] = Field(None, description="Agent ID")

class CloudLocalTradingManager:
    """云端本地交易管理器"""
    
    def __init__(self):
        self.local_connections: Dict[str, WebSocket] = {}  # 本地连接
        self.pending_commands: Dict[str, Dict] = {}  # 待处理命令
        self.command_timeout = 30  # 命令超时时间(秒)
        
    def register_local_connection(self, connection_id: str, websocket: WebSocket):
        """注册本地连接"""
        self.local_connections[connection_id] = websocket
        logger.info(f"✅ 本地连接已注册: {connection_id}")
    
    def unregister_local_connection(self, connection_id: str):
        """注销本地连接"""
        if connection_id in self.local_connections:
            del self.local_connections[connection_id]
            logger.info(f"❌ 本地连接已注销: {connection_id}")
    
    async def send_command_to_local(self, command_type: str, data: Dict) -> Dict:
        """发送命令到本地"""
        if not self.local_connections:
            raise HTTPException(status_code=503, detail="没有可用的本地连接")
        
        # 生成命令ID
        command_id = str(uuid.uuid4())
        
        # 构造命令
        command = {
            "type": command_type,
            "id": command_id,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # 发送到第一个可用的本地连接
        connection_id = list(self.local_connections.keys())[0]
        websocket = self.local_connections[connection_id]
        
        try:
            # 记录待处理命令
            self.pending_commands[command_id] = {
                "command": command,
                "start_time": time.time(),
                "connection_id": connection_id
            }
            
            # 发送命令
            await websocket.send_text(json.dumps(command))
            logger.info(f"📤 命令已发送到本地: {command_type} ({command_id})")
            
            # 等待响应
            return await self._wait_for_response(command_id)
            
        except Exception as e:
            # 清理待处理命令
            if command_id in self.pending_commands:
                del self.pending_commands[command_id]
            
            logger.error(f"❌ 发送命令失败: {e}")
            raise HTTPException(status_code=500, detail=f"发送命令失败: {e}")
    
    async def _wait_for_response(self, command_id: str) -> Dict:
        """等待命令响应"""
        start_time = time.time()
        
        while time.time() - start_time < self.command_timeout:
            # 检查是否有响应
            if command_id not in self.pending_commands:
                # 命令已完成，查找结果
                # 这里应该从某个地方获取结果，简化处理
                return {"success": True, "message": "命令已发送"}
            
            await asyncio.sleep(0.1)  # 100ms检查一次
        
        # 超时处理
        if command_id in self.pending_commands:
            del self.pending_commands[command_id]
        
        raise HTTPException(status_code=408, detail="命令执行超时")
    
    def handle_local_response(self, response: Dict):
        """处理本地响应"""
        command_id = response.get("command_id")
        
        if command_id and command_id in self.pending_commands:
            # 记录响应并清理待处理命令
            pending_command = self.pending_commands[command_id]
            pending_command["response"] = response
            pending_command["completed"] = True
            
            logger.info(f"✅ 收到本地响应: {command_id}")
            
            # 可以在这里触发回调或通知等待的协程
            del self.pending_commands[command_id]

# 创建全局管理器
cloud_local_manager = CloudLocalTradingManager()

# WebSocket端点
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """本地连接WebSocket端点"""
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    
    try:
        # 注册连接
        cloud_local_manager.register_local_connection(connection_id, websocket)
        
        # 监听消息
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
                
                # 处理不同类型的消息
                message_type = data.get("type")
                
                if message_type == "register":
                    logger.info(f"📝 本地服务注册: {data}")
                    await websocket.send_text(json.dumps({
                        "type": "register_ack",
                        "status": "success",
                        "connection_id": connection_id
                    }))
                
                elif message_type == "response":
                    cloud_local_manager.handle_local_response(data)
                
                elif message_type == "heartbeat":
                    await websocket.send_text(json.dumps({
                        "type": "heartbeat_ack",
                        "timestamp": datetime.now().isoformat()
                    }))
                
                else:
                    logger.warning(f"⚠️ 未知消息类型: {message_type}")
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"❌ WebSocket消息处理失败: {e}")
                break
    
    finally:
        # 注销连接
        cloud_local_manager.unregister_local_connection(connection_id)

# HTTP API端点
@router.get("/status")
async def get_local_status():
    """获取本地连接状态"""
    return {
        "local_connections": len(cloud_local_manager.local_connections),
        "pending_commands": len(cloud_local_manager.pending_commands),
        "connection_ids": list(cloud_local_manager.local_connections.keys()),
        "timestamp": datetime.now().isoformat()
    }

@router.post("/execute-trade")
async def execute_local_trade(command: LocalTradeCommand):
    """执行本地交易"""
    try:
        result = await cloud_local_manager.send_command_to_local("trade", {
            "action": command.action,
            "stock_code": command.stock_code,
            "quantity": command.quantity,
            "price": command.price,
            "agent_id": command.agent_id
        })
        
        return {
            "success": True,
            "message": "交易命令已发送到本地",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 执行本地交易失败: {e}")
        raise HTTPException(status_code=500, detail=f"执行失败: {e}")

@router.post("/export-data")
async def export_local_data(command: LocalExportCommand):
    """导出本地数据"""
    try:
        result = await cloud_local_manager.send_command_to_local("export", {
            "data_type": command.data_type,
            "agent_id": command.agent_id
        })
        
        return {
            "success": True,
            "message": "导出命令已发送到本地",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 导出本地数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出失败: {e}")

@router.get("/local-status")
async def get_local_trading_status():
    """获取本地交易状态"""
    try:
        result = await cloud_local_manager.send_command_to_local("status", {})
        
        return {
            "success": True,
            "local_status": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取本地状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {e}")

# Agent便捷接口
@router.post("/agent/buy")
async def agent_buy_local(
    stock_code: str,
    quantity: int,
    price: Optional[float] = None,
    agent_id: Optional[str] = None
):
    """Agent本地买入"""
    command = LocalTradeCommand(
        action="buy",
        stock_code=stock_code,
        quantity=quantity,
        price=price,
        agent_id=agent_id
    )
    return await execute_local_trade(command)

@router.post("/agent/sell")
async def agent_sell_local(
    stock_code: str,
    quantity: int,
    price: Optional[float] = None,
    agent_id: Optional[str] = None
):
    """Agent本地卖出"""
    command = LocalTradeCommand(
        action="sell",
        stock_code=stock_code,
        quantity=quantity,
        price=price,
        agent_id=agent_id
    )
    return await execute_local_trade(command)

@router.post("/agent/export/{data_type}")
async def agent_export_local(
    data_type: str,
    agent_id: Optional[str] = None
):
    """Agent本地导出"""
    command = LocalExportCommand(
        data_type=data_type,
        agent_id=agent_id
    )
    return await export_local_data(command)

# 通知接口（供本地服务器调用）
@router.post("/notify")
async def receive_local_notification(data: dict):
    """接收本地通知"""
    try:
        logger.info(f"📨 收到本地通知: {data}")
        
        # 这里可以处理本地发送的通知
        # 比如交易完成通知、数据导出完成通知等
        
        # 可以将通知存储到数据库或发送给相关的Agent
        
        return {
            "success": True,
            "message": "通知已接收",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 处理本地通知失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理通知失败: {e}")

# 测试接口
@router.post("/test-connection")
async def test_local_connection():
    """测试本地连接"""
    try:
        result = await cloud_local_manager.send_command_to_local("heartbeat", {})
        
        return {
            "success": True,
            "message": "本地连接测试成功",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 测试本地连接失败: {e}")
        raise HTTPException(status_code=500, detail=f"连接测试失败: {e}")

# 获取API文档
@router.get("/docs")
async def get_api_docs():
    """获取API文档"""
    return {
        "title": "云端本地交易API",
        "description": "云端Agent通过此API向本地电脑发送交易指令",
        "version": "1.0.0",
        "architecture": {
            "cloud": "Cloudflare + Supabase + GitHub",
            "local": "本地电脑 + 交易软件",
            "communication": "WebSocket + HTTP API"
        },
        "endpoints": {
            "WebSocket": "/ws - 本地连接端点",
            "POST /execute-trade": "执行本地交易",
            "POST /export-data": "导出本地数据", 
            "GET /local-status": "获取本地状态",
            "POST /agent/buy": "Agent本地买入",
            "POST /agent/sell": "Agent本地卖出",
            "POST /agent/export/{data_type}": "Agent本地导出",
            "POST /test-connection": "测试本地连接"
        },
        "data_flow": [
            "1. 云端Agent分析股票数据",
            "2. Agent生成交易决策",
            "3. 通过API发送指令到本地",
            "4. 本地执行交易/导出操作",
            "5. 结果反馈到云端"
        ]
    }
