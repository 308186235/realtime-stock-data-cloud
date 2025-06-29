import asyncio
import websockets
import json
import logging
import sys

# 配置日志
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def test_websocket_path(path):
    """测试不同的WebSocket路径"""
    uri = f"ws://localhost:8000{path}"
    logger.info(f"尝试连接到: {uri}")
    
    try:
        async with websockets.connect(uri, ping_interval=None, max_size=10 * 1024 * 1024) as websocket:
            logger.info(f"成功连接到: {uri}")
            
            # 发送ping消息
            ping_message = {"type": "ping"}
            await websocket.send(json.dumps(ping_message))
            logger.info(f"已发送: {ping_message}")
            
            # 等待响应
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            logger.info(f"已接收: {response}")
            
            return True
    except Exception as e:
        logger.error(f"连接 {uri} 失败: {str(e)}")
        return False

async def main():
    """测试多个可能的WebSocket路径"""
    # 可能的WebSocket路径列表
    paths = [
        "/ws",
        "/api/ws",
        "/api/test/ws",
        "/websocket",
        "/socket",
        "/api/websocket",
        "/api/socket"
    ]
    
    logger.info("开始测试多个WebSocket路径...")
    
    success = False
    for path in paths:
        if await test_websocket_path(path):
            logger.info(f"找到有效的WebSocket路径: {path}")
            success = True
            break
    
    if not success:
        logger.error("所有WebSocket路径测试均失败")

if __name__ == "__main__":
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"WebSockets库版本: {websockets.__version__}")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
    except Exception as e:
        logger.error(f"测试出错: {str(e)}") 
 