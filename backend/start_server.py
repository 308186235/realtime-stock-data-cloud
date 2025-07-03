#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的后端启动脚本
用于快速启动股票交易系统后端服务
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import json
import time
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="股票交易系统API",
    description="AI股票交易系统后端服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins = [
    "https://aigupiao.me",
    "https://api.aigupiao.me",
    "https://app.aigupiao.me",
    "https://mobile.aigupiao.me",
    "https://admin.aigupiao.me",
    "http://localhost:8080",
    "http://localhost:3000",
    "capacitor://localhost",
    "ionic://localhost"
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket连接管理
websocket_connections = {}

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "股票交易系统后端服务",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "stock-trading-backend"
    }

@app.get("/api/v1/agent-trading/system-status")
async def get_system_status():
    """获取系统状态"""
    return {
        "success": True,
        "data": {
            "status": "running",
            "ai_service": "active",
            "trading_service": "active",
            "data_service": "active",
            "websocket_connections": len(websocket_connections),
            "timestamp": datetime.now().isoformat()
        }
    }

@app.get("/api/v1/agent-trading/settings")
async def get_settings():
    """获取Agent设置"""
    return {
        "success": True,
        "data": {
            "auto_trading": False,
            "risk_level": "medium",
            "max_position": 100000,
            "stop_loss": 5.0,
            "take_profit": 10.0
        }
    }

@app.post("/api/v1/agent-trading/settings")
async def update_settings(settings: dict):
    """更新Agent设置"""
    return {
        "success": True,
        "message": "设置已更新",
        "data": settings
    }

@app.get("/api/v1/agent-trading/t0-stocks")
async def get_t0_stocks():
    """获取T+0股票池"""
    # 模拟数据
    mock_stocks = [
        {
            "symbol": "600519",
            "name": "贵州茅台",
            "price": 1680.50,
            "change": 2.3,
            "change_percent": 0.14,
            "volume": 1234567,
            "score": 85.6
        },
        {
            "symbol": "000858", 
            "name": "五粮液",
            "price": 158.20,
            "change": -1.8,
            "change_percent": -1.12,
            "volume": 2345678,
            "score": 78.9
        }
    ]
    
    return {
        "success": True,
        "data": {
            "stocks": mock_stocks,
            "total": len(mock_stocks),
            "update_time": datetime.now().isoformat()
        }
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点"""
    await websocket.accept()
    client_id = str(id(websocket))
    websocket_connections[client_id] = websocket
    
    logger.info(f"WebSocket客户端连接: {client_id}")
    
    try:
        # 发送连接确认
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "client_id": client_id,
            "message": "已连接到股票交易系统"
        })
        
        # 发送初始数据
        await websocket.send_json({
            "type": "system_status",
            "data": {
                "status": "running",
                "timestamp": datetime.now().isoformat()
            }
        })
        
        # 保持连接并处理消息
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                logger.info(f"收到WebSocket消息: {message}")
                
                # 回显消息
                await websocket.send_json({
                    "type": "echo",
                    "data": message,
                    "timestamp": datetime.now().isoformat()
                })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "无效的JSON格式"
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket客户端断开连接: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
    finally:
        if client_id in websocket_connections:
            del websocket_connections[client_id]

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"全局异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "服务器内部错误",
            "message": str(exc)
        }
    )

def main():
    """启动服务器"""
    print("=" * 60)
    print("🚀 启动股票交易系统后端服务")
    print("=" * 60)
    print(f"📡 API地址: http://localhost:8000")
    print(f"📡 WebSocket: ws://localhost:8000/ws")
    print(f"📖 API文档: http://localhost:8000/docs")
    print(f"🌐 健康检查: http://localhost:8000/api/health")
    print("=" * 60)
    
    # 启动服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
