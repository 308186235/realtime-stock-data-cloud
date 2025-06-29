import asyncio
import websockets
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def simple_test():
    """简单的WebSocket测试客户端"""
    uri = "ws://localhost:8001/ws"
    
    async with websockets.connect(uri) as websocket:
        logger.info("已连接到WebSocket服务器")
        
        # 发送测试消息
        message = "你好，WebSocket!"
        await websocket.send(message)
        logger.info(f"已发送: {message}")
        
        # 接收响应
        response = await websocket.recv()
        logger.info(f"已接收: {response}")

async def main():
    try:
        await simple_test()
        logger.info("测试完成")
    except Exception as e:
        logger.error(f"测试出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 
 