import asyncio
import websockets
import json
import time
import sys
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def test_websocket():
    print("测试WebSocket连接...")
    
    uri = "ws://localhost:8000/api/test/ws"
    print(f"正在连接到: {uri}")
    
    try:
        # 设置更多的选项用于调试
        async with websockets.connect(
            uri, 
            ping_interval=None, # 禁用自动ping
            max_size=10 * 1024 * 1024, # 增大最大消息大小
            close_timeout=10,
            max_queue=1
        ) as websocket:
            print("WebSocket连接已建立")
            
            # 发送ping消息
            ping_message = {"type": "ping"}
            await websocket.send(json.dumps(ping_message))
            print(f"已发送: {ping_message}")
            
            # 接收pong响应
            print("等待响应...")
            response = await websocket.recv()
            print(f"已接收: {json.loads(response)}")
            
            # 订阅股票行情
            subscribe_message = {
                "type": "subscribe",
                "channel": "quote",
                "params": {"code": "sh600000"}
            }
            await websocket.send(json.dumps(subscribe_message))
            print(f"已发送: {subscribe_message}")
            
            # 接收订阅确认
            print("等待订阅确认...")
            response = await websocket.recv()
            print(f"已接收: {json.loads(response)}")
            
            # 等待并接收一条实时数据
            print("等待实时数据...")
            response = await websocket.recv()
            print(f"已接收实时数据: {json.loads(response)}")
                
            # 取消订阅
            unsubscribe_message = {
                "type": "unsubscribe",
                "channel": "quote"
            }
            await websocket.send(json.dumps(unsubscribe_message))
            print(f"已发送: {unsubscribe_message}")
            
            # 接收取消订阅确认
            print("等待取消订阅确认...")
            response = await websocket.recv()
            print(f"已接收: {json.loads(response)}")
            
            print("WebSocket测试完成")
    
    except Exception as e:
        print(f"WebSocket测试出错: {str(e)}")
        logger.exception("WebSocket测试详细错误信息")

if __name__ == "__main__":
    print(f"Python版本: {sys.version}")
    print(f"WebSockets库版本: {websockets.__version__}")
    try:
        asyncio.run(test_websocket())
    except KeyboardInterrupt:
        print("测试被用户中断")
    except Exception as e:
        print(f"运行测试时出错: {str(e)}")
        logger.exception("运行测试时出错") 
 