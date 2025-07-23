"""
WebSocket功能修复补丁

问题分析:
在测试过程中发现,尽管simple_test_server.py中包含了"/api/test/ws"的WebSocket端点,
但客户端无法成功连接,总是返回404错误。这可能有以下几个原因:

1. FastAPI的路由注册问题:FastAPI可能没有正确注册WebSocket路由
2. Uvicorn版本兼容性问题:不同版本的Uvicorn处理WebSocket的方式可能不同
3. 服务器重载导致的问题:使用reload=True可能导致某些连接问题

修复方案:
1. 添加一个根路径的WebSocket端点,确保基础WebSocket功能正常工作
2. 确保WebSocket中间件正确配置
3. 进一步简化WebSocket处理逻辑

使用说明:
1. 停止当前运行的simple_test_server.py
2. 将以下代码添加到simple_test_server.py文件中,或创建一个新文件
3. 启动新的服务器并测试WebSocket功能
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
import logging
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="WebSocket修复示例")

# 配置CORS - 确保WebSocket请求不会被CORS拦截
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储连接的WebSocket客户端
websocket_connections = {}

# 简单的WebSocket端点 - 使用根路径确保无路由问题
@app.websocket("/ws")
async def websocket_root(websocket: WebSocket):
    """根路径WebSocket端点"""
    await websocket.accept()
    logger.info("WebSocket客户端连接到根路径")
    
    client_id = str(id(websocket))
    websocket_connections[client_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"收到WebSocket消息: {data}")
            
            try:
                message = json.loads(data)
                # 简单回显所有消息
                await websocket.send_text(json.dumps({
                    "type": "echo",
                    "data": message,
                    "timestamp": time.time()
                }))
            except Exception as e:
                logger.error(f"处理消息时出错: {str(e)}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": str(e)
                }))
    
    except WebSocketDisconnect:
        if client_id in websocket_connections:
            del websocket_connections[client_id]
        logger.info(f"客户端断开连接")

# API测试端点 - 确保基本HTTP功能正常
@app.get("/api/ping")
async def ping():
    """简单的ping测试"""
    return {"message": "pong", "timestamp": time.time()}

# 主程序入口 - 注意关闭了reload功能
if __name__ == "__main__":
    logger.info("启动WebSocket修复示例服务器")
    # 关闭reload选项,避免可能的WebSocket连接问题
    uvicorn.run("websocket_fix_patch:app", host="0.0.0.0", port=8003, reload=False)

"""
修复后的服务器测试方法:

1. 启动修复后的服务器:
   python websocket_fix_patch.py

2. 使用以下Python代码测试WebSocket连接:

import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8003/ws"
    async with websockets.connect(uri) as websocket:
        message = {"type": "test", "data": "Hello WebSocket"}
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
        print(f"收到响应: {response}")

asyncio.run(test_websocket())

3. 或使用网页端WebSocket测试工具测试连接
""" 
 
