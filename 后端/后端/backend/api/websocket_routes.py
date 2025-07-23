#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket路由
处理WebSocket连接和消息传递
"""

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter()

# 全局WebSocket管理器实例(将在app.py中注入)
websocket_manager = None

def set_websocket_manager(manager):
    """设置WebSocket管理器"""
    global websocket_manager
    websocket_manager = manager

@router.websocket("/local-agent")
async def local_agent_websocket(websocket: WebSocket):
    """本地Agent WebSocket连接"""
    if not websocket_manager:
        await websocket.close(code=1011, reason="WebSocket管理器未初始化")
        return
    
    connection_id = None
    
    try:
        # 建立连接
        connection_id = await websocket_manager.connect(websocket, "local_agent")
        logger.info(f"✅ 本地Agent连接建立: {connection_id}")
        
        # 监听消息
        while True:
            try:
                # 接收消息
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # 处理消息
                await websocket_manager.handle_message(connection_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"🔌 本地Agent连接断开: {connection_id}")
                break
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON解析失败: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "JSON格式错误"
                }))
            except Exception as e:
                logger.error(f"❌ 处理消息失败: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"处理失败: {str(e)}"
                }))
                
    except Exception as e:
        logger.error(f"❌ 本地Agent WebSocket连接失败: {e}")
    finally:
        if connection_id:
            await websocket_manager.disconnect(connection_id)

@router.websocket("/agent-client")
async def agent_client_websocket(websocket: WebSocket):
    """前端Agent客户端WebSocket连接"""
    if not websocket_manager:
        await websocket.close(code=1011, reason="WebSocket管理器未初始化")
        return
    
    connection_id = None
    
    try:
        # 建立连接
        connection_id = await websocket_manager.connect(websocket, "frontend_client")
        logger.info(f"✅ 前端客户端连接建立: {connection_id}")
        
        # 监听消息
        while True:
            try:
                # 接收消息
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # 处理消息
                await websocket_manager.handle_message(connection_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"🔌 前端客户端连接断开: {connection_id}")
                break
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON解析失败: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "JSON格式错误"
                }))
            except Exception as e:
                logger.error(f"❌ 处理消息失败: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"处理失败: {str(e)}"
                }))
                
    except Exception as e:
        logger.error(f"❌ 前端客户端WebSocket连接失败: {e}")
    finally:
        if connection_id:
            await websocket_manager.disconnect(connection_id)

@router.websocket("/admin-client")
async def admin_client_websocket(websocket: WebSocket):
    """管理员客户端WebSocket连接"""
    if not websocket_manager:
        await websocket.close(code=1011, reason="WebSocket管理器未初始化")
        return
    
    connection_id = None
    
    try:
        # 建立连接
        connection_id = await websocket_manager.connect(websocket, "admin_client")
        logger.info(f"✅ 管理员客户端连接建立: {connection_id}")
        
        # 监听消息
        while True:
            try:
                # 接收消息
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # 处理消息
                await websocket_manager.handle_message(connection_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"🔌 管理员客户端连接断开: {connection_id}")
                break
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON解析失败: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "JSON格式错误"
                }))
            except Exception as e:
                logger.error(f"❌ 处理消息失败: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"处理失败: {str(e)}"
                }))
                
    except Exception as e:
        logger.error(f"❌ 管理员客户端WebSocket连接失败: {e}")
    finally:
        if connection_id:
            await websocket_manager.disconnect(connection_id)
