import asyncio
import websockets
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def test_fixed_websocket():
    """测试修复版服务器的WebSocket功能"""
    uri = "ws://localhost:8002/ws"
    logger.info(f"连接到: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("WebSocket连接已建立")
            
            # 发送ping消息
            ping_message = {"type": "ping"}
            await websocket.send(json.dumps(ping_message))
            logger.info(f"已发送: {ping_message}")
            
            # 接收pong响应
            response = await websocket.recv()
            logger.info(f"已接收: {json.loads(response)}")
            
            # 发送自定义消息
            custom_message = {
                "type": "custom",
                "data": "测试数据",
                "timestamp": asyncio.get_event_loop().time()
            }
            await websocket.send(json.dumps(custom_message))
            logger.info(f"已发送: {custom_message}")
            
            # 接收回显响应
            response = await websocket.recv()
            logger.info(f"已接收: {json.loads(response)}")
            
            logger.info("WebSocket测试成功!")
    
    except Exception as e:
        logger.error(f"WebSocket测试失败: {str(e)}")
        return False
        
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_fixed_websocket())
        if result:
            logger.info("✅ 测试通过：WebSocket通信正常工作")
        else:
            logger.error("❌ 测试失败：WebSocket通信存在问题")
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
    except Exception as e:
        logger.error(f"运行测试出错: {str(e)}") 
 