#!/usr/bin/env python
"""
增强版WebSocket测试脚本
用于测试WebSocket服务器的连接,认证和消息收发
"""

import asyncio
import json
import time
import websockets
import argparse
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ws_test')

# 连接设置
DEFAULT_URL = "ws://localhost:8000/ws"
DEFAULT_TOKEN = None

async def test_websocket(url, token=None, test_duration=30):
    """测试WebSocket连接并进行消息交互"""
    # 构建URL
    if token:
        url = f"{url}?token={token}"
    
    logger.info(f"连接到: {url}")
    
    try:
        async with websockets.connect(url) as websocket:
            logger.info("连接成功!")
            
            # 等待欢迎消息
            response = await websocket.recv()
            welcome = json.loads(response)
            logger.info(f"收到欢迎消息: {welcome}")
            
            # 发送ping消息
            ping_message = {
                "type": "ping",
                "timestamp": time.time()
            }
            logger.info(f"发送ping: {ping_message}")
            await websocket.send(json.dumps(ping_message))
            
            # 接收pong响应
            response = await websocket.recv()
            pong = json.loads(response)
            latency = time.time() - ping_message["timestamp"]
            logger.info(f"收到pong响应: {pong} (延迟: {latency*1000:.2f}ms)")
            
            # 订阅股票行情
            subscribe_message = {
                "type": "subscribe",
                "channel": "quote",
                "params": {
                    "symbols": ["AAPL", "MSFT", "GOOGL"]
                }
            }
            logger.info(f"发送订阅请求: {subscribe_message}")
            await websocket.send(json.dumps(subscribe_message))
            
            # 接收订阅确认
            response = await websocket.recv()
            subscription = json.loads(response)
            logger.info(f"收到订阅确认: {subscription}")
            
            # 指定测试时长,接收消息
            start_time = time.time()
            message_count = 0
            
            logger.info(f"开始接收消息,持续 {test_duration} 秒...")
            
            while time.time() - start_time < test_duration:
                try:
                    # 设置超时,避免永久阻塞
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    message = json.loads(response)
                    message_count += 1
                    
                    # 只打印部分消息,避免日志过多
                    if message_count % 5 == 0 or message.get("type") != "quote":
                        logger.info(f"收到消息 #{message_count}: {message}")
                except asyncio.TimeoutError:
                    # 超时但继续循环
                    continue
                except Exception as e:
                    logger.error(f"接收消息错误: {str(e)}")
                    break
            
            # 发送取消订阅消息
            unsubscribe_message = {
                "type": "unsubscribe",
                "channel": "quote"
            }
            logger.info(f"发送取消订阅: {unsubscribe_message}")
            await websocket.send(json.dumps(unsubscribe_message))
            
            # 接收取消订阅确认
            response = await websocket.recv()
            unsubscription = json.loads(response)
            logger.info(f"收到取消订阅确认: {unsubscription}")
            
            # 测试结果
            elapsed = time.time() - start_time
            logger.info(f"测试完成! 共收到 {message_count} 条消息,耗时 {elapsed:.2f} 秒")
            logger.info(f"消息率: {message_count/elapsed:.2f} 条/秒")
    
    except websockets.exceptions.ConnectionClosed as e:
        logger.error(f"连接关闭: {e.code} {e.reason}")
    except Exception as e:
        logger.error(f"测试错误: {str(e)}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="WebSocket客户端测试工具")
    parser.add_argument("--url", default=DEFAULT_URL, help="WebSocket服务器URL")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="认证令牌")
    parser.add_argument("--duration", type=int, default=30, help="测试持续时间(秒)")
    
    args = parser.parse_args()
    
    # 启动测试
    try:
        asyncio.run(test_websocket(args.url, args.token, args.duration))
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
    except Exception as e:
        logger.error(f"未处理的错误: {str(e)}")

if __name__ == "__main__":
    main() 
