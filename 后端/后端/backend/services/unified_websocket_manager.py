#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一WebSocket管理器
管理云端与本地Agent,前端客户端的WebSocket连接
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect

# 配置日志
logger = logging.getLogger(__name__)

class ConnectionInfo:
    """连接信息"""
    def __init__(self, websocket: WebSocket, connection_type: str, client_id: str = None):
        self.websocket = websocket
        self.connection_type = connection_type  # local_agent, frontend_client, admin_client
        self.client_id = client_id or str(uuid.uuid4())
        self.connected_at = datetime.now()
        self.last_heartbeat = datetime.now()
        self.metadata = {}

class UnifiedWebSocketManager:
    """统一WebSocket管理器"""
    
    def __init__(self):
        # 连接管理
        self.connections: Dict[str, ConnectionInfo] = {}
        self.local_agents: Dict[str, ConnectionInfo] = {}
        self.frontend_clients: Dict[str, ConnectionInfo] = {}
        self.admin_clients: Dict[str, ConnectionInfo] = {}
        
        # 命令管理
        self.pending_commands: Dict[str, Dict] = {}
        self.command_timeout = 30  # 30秒超时
        
        # 统计信息
        self.stats = {
            "total_connections": 0,
            "active_local_agents": 0,
            "active_frontend_clients": 0,
            "active_admin_clients": 0,
            "commands_sent": 0,
            "commands_completed": 0,
            "start_time": datetime.now().isoformat()
        }
        
        # 启动清理任务
        asyncio.create_task(self._cleanup_task())
    
    async def connect(self, websocket: WebSocket, connection_type: str, client_id: str = None) -> str:
        """建立WebSocket连接"""
        await websocket.accept()
        
        connection_id = client_id or str(uuid.uuid4())
        connection_info = ConnectionInfo(websocket, connection_type, connection_id)
        
        # 存储连接
        self.connections[connection_id] = connection_info
        
        # 按类型分类存储
        if connection_type == "local_agent":
            self.local_agents[connection_id] = connection_info
            self.stats["active_local_agents"] += 1
        elif connection_type == "frontend_client":
            self.frontend_clients[connection_id] = connection_info
            self.stats["active_frontend_clients"] += 1
        elif connection_type == "admin_client":
            self.admin_clients[connection_id] = connection_info
            self.stats["active_admin_clients"] += 1
        
        self.stats["total_connections"] += 1
        
        logger.info(f"✅ WebSocket连接建立: {connection_type} ({connection_id})")
        
        # 发送连接确认
        await self._send_to_connection(connection_id, {
            "type": "connection_established",
            "connection_id": connection_id,
            "connection_type": connection_type,
            "timestamp": datetime.now().isoformat()
        })
        
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """断开WebSocket连接"""
        if connection_id in self.connections:
            connection_info = self.connections[connection_id]
            connection_type = connection_info.connection_type
            
            # 从分类存储中移除
            if connection_type == "local_agent" and connection_id in self.local_agents:
                del self.local_agents[connection_id]
                self.stats["active_local_agents"] -= 1
            elif connection_type == "frontend_client" and connection_id in self.frontend_clients:
                del self.frontend_clients[connection_id]
                self.stats["active_frontend_clients"] -= 1
            elif connection_type == "admin_client" and connection_id in self.admin_clients:
                del self.admin_clients[connection_id]
                self.stats["active_admin_clients"] -= 1
            
            # 从总连接中移除
            del self.connections[connection_id]
            
            logger.info(f"🔌 WebSocket连接断开: {connection_type} ({connection_id})")
    
    async def handle_message(self, connection_id: str, message: Dict[str, Any]):
        """处理WebSocket消息"""
        try:
            message_type = message.get("type")
            
            if message_type == "heartbeat":
                await self._handle_heartbeat(connection_id, message)
            elif message_type == "register":
                await self._handle_register(connection_id, message)
            elif message_type == "response":
                await self._handle_command_response(connection_id, message)
            elif message_type == "broadcast":
                await self._handle_broadcast(connection_id, message)
            else:
                logger.warning(f"⚠️ 未知消息类型: {message_type} from {connection_id}")
                
        except Exception as e:
            logger.error(f"❌ 处理消息失败: {e}")
    
    async def send_to_local_agent(self, command: Dict[str, Any], agent_id: str = None) -> Dict[str, Any]:
        """发送命令到本地Agent"""
        if not self.local_agents:
            raise Exception("没有可用的本地Agent连接")
        
        # 选择目标Agent
        target_agent_id = agent_id or list(self.local_agents.keys())[0]
        
        if target_agent_id not in self.local_agents:
            raise Exception(f"本地Agent不存在: {target_agent_id}")
        
        # 生成命令ID
        command_id = str(uuid.uuid4())
        command["id"] = command_id
        command["timestamp"] = datetime.now().isoformat()
        
        # 记录待处理命令
        self.pending_commands[command_id] = {
            "command": command,
            "target_agent": target_agent_id,
            "start_time": time.time(),
            "status": "pending"
        }
        
        # 发送命令
        await self._send_to_connection(target_agent_id, command)
        
        self.stats["commands_sent"] += 1
        logger.info(f"📤 命令已发送到本地Agent: {command.get('type')} ({command_id})")
        
        # 等待响应
        return await self._wait_for_response(command_id)
    
    async def broadcast_to_clients(self, message: Dict[str, Any], client_type: str = None):
        """广播消息到客户端"""
        target_clients = self.frontend_clients
        
        if client_type == "admin":
            target_clients = self.admin_clients
        elif client_type == "all":
            target_clients = {**self.frontend_clients, **self.admin_clients}
        
        if not target_clients:
            logger.warning("⚠️ 没有可用的客户端连接")
            return
        
        # 添加广播标识
        message["broadcast"] = True
        message["timestamp"] = datetime.now().isoformat()
        
        # 发送到所有目标客户端
        for client_id in list(target_clients.keys()):
            try:
                await self._send_to_connection(client_id, message)
            except Exception as e:
                logger.error(f"❌ 广播到客户端失败 ({client_id}): {e}")
        
        logger.debug(f"📡 消息已广播到 {len(target_clients)} 个客户端")
    
    async def _send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """发送消息到指定连接"""
        if connection_id not in self.connections:
            raise Exception(f"连接不存在: {connection_id}")
        
        connection_info = self.connections[connection_id]
        
        try:
            await connection_info.websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"❌ 发送消息失败 ({connection_id}): {e}")
            # 连接可能已断开,移除连接
            await self.disconnect(connection_id)
            raise
    
    async def _wait_for_response(self, command_id: str) -> Dict[str, Any]:
        """等待命令响应"""
        start_time = time.time()
        
        while time.time() - start_time < self.command_timeout:
            if command_id in self.pending_commands:
                command_info = self.pending_commands[command_id]
                
                if command_info["status"] == "completed":
                    result = command_info["response"]
                    del self.pending_commands[command_id]
                    self.stats["commands_completed"] += 1
                    return result
                elif command_info["status"] == "error":
                    error = command_info["error"]
                    del self.pending_commands[command_id]
                    raise Exception(f"命令执行失败: {error}")
            
            await asyncio.sleep(0.1)
        
        # 超时处理
        if command_id in self.pending_commands:
            del self.pending_commands[command_id]
        
        raise Exception(f"命令执行超时: {command_id}")
    
    async def _handle_heartbeat(self, connection_id: str, message: Dict[str, Any]):
        """处理心跳消息"""
        if connection_id in self.connections:
            self.connections[connection_id].last_heartbeat = datetime.now()
            
            # 发送心跳响应
            await self._send_to_connection(connection_id, {
                "type": "heartbeat_ack",
                "timestamp": datetime.now().isoformat()
            })
    
    async def _handle_register(self, connection_id: str, message: Dict[str, Any]):
        """处理注册消息"""
        if connection_id in self.connections:
            connection_info = self.connections[connection_id]
            connection_info.metadata.update(message.get("metadata", {}))
            
            logger.info(f"📝 客户端注册: {connection_info.connection_type} ({connection_id})")
            
            # 发送注册确认
            await self._send_to_connection(connection_id, {
                "type": "register_ack",
                "status": "success",
                "connection_id": connection_id,
                "timestamp": datetime.now().isoformat()
            })
    
    async def _handle_command_response(self, connection_id: str, message: Dict[str, Any]):
        """处理命令响应"""
        command_id = message.get("command_id")
        
        if command_id and command_id in self.pending_commands:
            command_info = self.pending_commands[command_id]
            
            if message.get("type") == "error":
                command_info["status"] = "error"
                command_info["error"] = message.get("error", "未知错误")
            else:
                command_info["status"] = "completed"
                command_info["response"] = message.get("data", message)
            
            logger.info(f"📨 收到命令响应: {command_id}")
    
    async def _handle_broadcast(self, connection_id: str, message: Dict[str, Any]):
        """处理广播消息"""
        # 转发广播消息到其他客户端
        broadcast_data = message.get("data", {})
        target_type = message.get("target_type", "frontend")
        
        await self.broadcast_to_clients(broadcast_data, target_type)
    
    async def _cleanup_task(self):
        """清理任务"""
        while True:
            try:
                current_time = time.time()
                
                # 清理超时的命令
                expired_commands = []
                for command_id, command_info in self.pending_commands.items():
                    if current_time - command_info["start_time"] > self.command_timeout:
                        expired_commands.append(command_id)
                
                for command_id in expired_commands:
                    del self.pending_commands[command_id]
                    logger.warning(f"⏰ 清理超时命令: {command_id}")
                
                # 检查连接健康状态
                disconnected_connections = []
                for connection_id, connection_info in self.connections.items():
                    # 检查心跳超时(5分钟)
                    if (datetime.now() - connection_info.last_heartbeat).total_seconds() > 300:
                        disconnected_connections.append(connection_id)
                
                for connection_id in disconnected_connections:
                    logger.warning(f"💔 连接心跳超时,移除连接: {connection_id}")
                    await self.disconnect(connection_id)
                
                await asyncio.sleep(60)  # 每分钟清理一次
                
            except Exception as e:
                logger.error(f"❌ 清理任务失败: {e}")
                await asyncio.sleep(60)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "current_connections": len(self.connections),
            "pending_commands": len(self.pending_commands),
            "uptime_seconds": (datetime.now() - datetime.fromisoformat(self.stats["start_time"])).total_seconds()
        }
    
    def get_connections_info(self) -> Dict[str, Any]:
        """获取连接信息"""
        return {
            "local_agents": [
                {
                    "connection_id": conn.client_id,
                    "connected_at": conn.connected_at.isoformat(),
                    "last_heartbeat": conn.last_heartbeat.isoformat(),
                    "metadata": conn.metadata
                }
                for conn in self.local_agents.values()
            ],
            "frontend_clients": [
                {
                    "connection_id": conn.client_id,
                    "connected_at": conn.connected_at.isoformat(),
                    "last_heartbeat": conn.last_heartbeat.isoformat(),
                    "metadata": conn.metadata
                }
                for conn in self.frontend_clients.values()
            ],
            "admin_clients": [
                {
                    "connection_id": conn.client_id,
                    "connected_at": conn.connected_at.isoformat(),
                    "last_heartbeat": conn.last_heartbeat.isoformat(),
                    "metadata": conn.metadata
                }
                for conn in self.admin_clients.values()
            ]
        }
