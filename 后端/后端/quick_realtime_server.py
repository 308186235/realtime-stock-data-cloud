#!/usr/bin/env python3
"""
快速实时数据服务器
连接茶股帮并推送数据给云端agent
"""

import asyncio
import websockets
import socket
import json
import time
import threading
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 茶股帮配置
CHAGUBANG_CONFIG = {
    'host': 'l1.chagubang.com',
    'port': 6380,
    'token': 'process.env.STOCK_API_KEY'
}

class QuickRealtimeServer:
    def __init__(self):
        self.running = False
        self.socket = None
        self.websocket_clients = set()
        self.stock_data = {}
        self.stats = {
            'received': 0,
            'processed': 0,
            'clients': 0,
            'start_time': time.time()
        }

    def connect_to_chagubang(self):
        """连接到茶股帮"""
        try:
            logger.info(f"🔗 连接茶股帮: {CHAGUBANG_CONFIG['host']}:{CHAGUBANG_CONFIG['port']}")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((CHAGUBANG_CONFIG['host'], CHAGUBANG_CONFIG['port']))
            
            # 发送token
            self.socket.send(CHAGUBANG_CONFIG['token'].encode('utf-8'))
            
            logger.info("✅ 茶股帮连接成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 茶股帮连接失败: {e}")
            return False

    def receive_data_loop(self):
        """数据接收循环"""
        buffer = ""
        
        while self.running:
            try:
                data = self.socket.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    logger.warning("连接断开")
                    break
                
                buffer += data
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    
                    if line:
                        self.stats['received'] += 1
                        
                        # 解析股票数据
                        stock_data = self.parse_stock_data(line)
                        if stock_data:
                            self.stock_data[stock_data['symbol']] = stock_data
                            self.stats['processed'] += 1
                            
                            # 推送给WebSocket客户端
                            asyncio.run_coroutine_threadsafe(
                                self.broadcast_to_clients(stock_data),
                                self.loop
                            )
                        
                        # 每1000条数据打印统计
                        if self.stats['received'] % 1000 == 0:
                            self.print_stats()
                            
            except Exception as e:
                logger.error(f"接收数据错误: {e}")
                break

    def parse_stock_data(self, line):
        """解析股票数据"""
        try:
            # 简单的数据解析
            parts = line.split('|')
            if len(parts) >= 10:
                return {
                    'symbol': parts[0],
                    'name': parts[1] if len(parts) > 1 else '',
                    'price': float(parts[2]) if len(parts) > 2 and parts[2] else 0,
                    'change_percent': float(parts[3]) if len(parts) > 3 and parts[3] else 0,
                    'volume': int(parts[4]) if len(parts) > 4 and parts[4] else 0,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            logger.debug(f"解析数据失败: {e}")
        
        return None

    async def broadcast_to_clients(self, stock_data):
        """广播数据给WebSocket客户端"""
        if self.websocket_clients:
            message = json.dumps({
                'type': 'stock_data',
                'data': stock_data,
                'timestamp': time.time()
            })
            
            # 发送给所有连接的客户端
            disconnected = set()
            for client in self.websocket_clients:
                try:
                    await client.send(message)
                except:
                    disconnected.add(client)
            
            # 移除断开的客户端
            self.websocket_clients -= disconnected
            self.stats['clients'] = len(self.websocket_clients)

    async def websocket_handler(self, websocket):
        """WebSocket处理器"""
        logger.info(f"🔗 新的WebSocket客户端连接: {websocket.remote_address}")
        self.websocket_clients.add(websocket)
        self.stats['clients'] = len(self.websocket_clients)
        
        try:
            # 发送欢迎消息
            await websocket.send(json.dumps({
                'type': 'welcome',
                'message': '已连接到实时股票数据服务',
                'stats': self.stats
            }))
            
            # 保持连接
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data.get('type') == 'ping':
                        await websocket.send(json.dumps({'type': 'pong'}))
                except:
                    pass
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.websocket_clients.discard(websocket)
            self.stats['clients'] = len(self.websocket_clients)
            logger.info(f"🔌 WebSocket客户端断开: {websocket.remote_address}")

    def print_stats(self):
        """打印统计信息"""
        uptime = time.time() - self.stats['start_time']
        logger.info(f"📊 统计: 接收{self.stats['received']} 处理{self.stats['processed']} "
                   f"客户端{self.stats['clients']} 运行{uptime:.0f}秒")

    async def start_websocket_server(self):
        """启动WebSocket服务器"""
        logger.info("🚀 启动WebSocket服务器 (端口8765)")
        
        server = await websockets.serve(
            self.websocket_handler,
            "localhost",
            8765
        )
        
        logger.info("✅ WebSocket服务器已启动")
        return server

    async def start(self):
        """启动服务"""
        logger.info("🚀 启动快速实时数据服务器...")
        
        # 连接茶股帮
        if not self.connect_to_chagubang():
            return False
        
        self.running = True
        self.loop = asyncio.get_event_loop()
        
        # 启动WebSocket服务器
        server = await self.start_websocket_server()
        
        # 启动数据接收线程
        data_thread = threading.Thread(target=self.receive_data_loop)
        data_thread.start()
        
        logger.info("✅ 服务启动完成")
        logger.info("📡 WebSocket端点: ws://localhost:8765")
        logger.info("🔗 茶股帮数据正在接收...")
        
        try:
            # 保持服务运行
            await server.wait_closed()
        except KeyboardInterrupt:
            logger.info("⏹️ 收到停止信号")
        finally:
            self.running = False
            if self.socket:
                self.socket.close()
            data_thread.join(timeout=5)

async def main():
    """主函数"""
    server = QuickRealtimeServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
