from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
import logging
import time
import random
from datetime import datetime
from typing import Dict, Any, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="通信测试服务器（修复版）",
    description="修复后的测试服务器，确保WebSocket正常工作",
    version="1.0.1"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储连接的WebSocket客户端
websocket_connections = {}

# 简单的测试数据
test_data = {
    "message": "Hello from WebSocket server!"
}

# 简单的HTTP端点
@app.get("/api/ping")
async def ping():
    """简单的ping测试"""
    return {"message": "pong", "timestamp": time.time()}

# WebSocket端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket测试端点"""
    await websocket.accept()
    logger.info("WebSocket客户端连接")
    
    # 生成客户端ID
    client_id = str(id(websocket))
    websocket_connections[client_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"收到WebSocket消息: {data}")
            
            try:
                message = json.loads(data)
                message_type = message.get("type", "")
                
                # 处理不同类型的消息
                if message_type == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": time.time()
                    }))
                    logger.info("响应ping消息")
                else:
                    # 回显消息
                    await websocket.send_text(json.dumps({
                        "type": "echo",
                        "data": message,
                        "timestamp": time.time()
                    }))
                    logger.info(f"回显消息: {message}")
            
            except json.JSONDecodeError:
                # 无效的JSON
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": "无效的JSON数据"
                }))
                logger.error("无效的JSON数据")
            
            except Exception as e:
                # 其他错误
                logger.error(f"处理WebSocket消息时出错: {str(e)}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": f"处理消息时出错: {str(e)}"
                }))
    
    except WebSocketDisconnect:
        # 客户端断开连接
        if client_id in websocket_connections:
            del websocket_connections[client_id]
        logger.info(f"客户端 {client_id} 断开连接")
    
    except Exception as e:
        # 其他错误
        logger.error(f"WebSocket连接错误: {str(e)}")
        if client_id in websocket_connections:
            del websocket_connections[client_id]

if __name__ == "__main__":
    logger.info("启动修复版测试服务器")
    uvicorn.run("fixed_test_server:app", host="0.0.0.0", port=8002, reload=True) 
 