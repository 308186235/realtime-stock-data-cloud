from fastapi import FastAPI, WebSocket
import uvicorn
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="WebSocket测试")

@app.get("/")
async def root():
    return {"message": "WebSocket测试服务器正在运行"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """简单的WebSocket测试端点"""
    await websocket.accept()
    logger.info("WebSocket客户端连接")
    
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"收到消息: {data}")
            await websocket.send_text(f"你发送了: {data}")
    except Exception as e:
        logger.error(f"WebSocket错误: {str(e)}")

if __name__ == "__main__":
    logger.info("启动WebSocket测试服务器")
    uvicorn.run("ws_test_server:app", host="0.0.0.0", port=8001, reload=True) 
 