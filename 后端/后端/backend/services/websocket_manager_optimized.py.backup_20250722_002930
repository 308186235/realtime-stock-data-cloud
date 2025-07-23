"""
优化的WebSocket连接管理器 - 支持大规模股票数据推送
"""
import asyncio
import json
import time
import logging
from typing import Dict, Set, List, Optional
from collections import defaultdict
import weakref
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class ConnectionInfo:
    """连接信息"""
    websocket: WebSocket
    user_id: str
    subscribed_stocks: Set[str]
    last_ping: float
    created_at: float
    
class OptimizedWebSocketManager:
    """优化的WebSocket连接管理器"""
    
    def __init__(self):
        # 连接管理
        self.connections: Dict[str, ConnectionInfo] = {}  # connection_id -> ConnectionInfo
        self.stock_subscribers: Dict[str, Set[str]] = defaultdict(set)  # stock_code -> connection_ids
        self.user_connections: Dict[str, Set[str]] = defaultdict(set)  # user_id -> connection_ids
        
        # 性能配置
        self.max_connections = 10000
        self.ping_interval = 30  # 心跳间隔
        self.connection_timeout = 60  # 连接超时
        self.batch_size = 1000  # 批量推送大小
        
        # 推送队列
        self.push_queue = asyncio.Queue(maxsize=100000)
        self.broadcast_queue = asyncio.Queue(maxsize=50000)
        
        # 统计信息
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'total_messages_sent': 0,
            'total_messages_failed': 0,
            'push_rate': 0,
            'last_cleanup': 0
        }
        
        # 异步任务
        self.running = False
        self.push_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        
        # 线程池用于CPU密集型操作
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # 锁
        self.connection_lock = asyncio.Lock()
    
    async def start(self):
        """启动WebSocket管理器"""
        self.running = True
        
        # 启动后台任务
        self.push_task = asyncio.create_task(self._push_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        logger.info("优化WebSocket管理器已启动")
    
    async def stop(self):
        """停止WebSocket管理器"""
        self.running = False
        
        # 取消后台任务
        for task in [self.push_task, self.cleanup_task, self.heartbeat_task]:
            if task:
                task.cancel()
        
        # 关闭所有连接
        await self._close_all_connections()
        
        self.executor.shutdown(wait=True)
        logger.info("优化WebSocket管理器已停止")
    
    async def connect(self, websocket: WebSocket, user_id: str) -> str:
        """建立WebSocket连接"""
        try:
            # 检查连接数限制
            if len(self.connections) >= self.max_connections:
                await websocket.close(code=1008, reason="连接数已达上限")
                return None
            
            await websocket.accept()
            
            # 生成连接ID
            connection_id = f"{user_id}_{int(time.time() * 1000)}_{id(websocket)}"
            
            # 创建连接信息
            connection_info = ConnectionInfo(
                websocket=websocket,
                user_id=user_id,
                subscribed_stocks=set(),
                last_ping=time.time(),
                created_at=time.time()
            )
            
            async with self.connection_lock:
                # 存储连接
                self.connections[connection_id] = connection_info
                self.user_connections[user_id].add(connection_id)
                
                # 更新统计
                self.stats['total_connections'] += 1
                self.stats['active_connections'] = len(self.connections)
            
            logger.info(f"新连接建立: {connection_id}, 用户: {user_id}, 总连接数: {len(self.connections)}")
            
            # 发送欢迎消息
            await self._send_to_connection(connection_id, {
                'type': 'welcome',
                'connection_id': connection_id,
                'server_time': time.time()
            })
            
            return connection_id
            
        except Exception as e:
            logger.error(f"建立连接失败: {str(e)}")
            return None
    
    async def disconnect(self, connection_id: str):
        """断开WebSocket连接"""
        try:
            async with self.connection_lock:
                if connection_id in self.connections:
                    connection_info = self.connections[connection_id]
                    
                    # 取消所有股票订阅
                    for stock_code in connection_info.subscribed_stocks.copy():
                        await self._unsubscribe_stock_internal(connection_id, stock_code)
                    
                    # 从用户连接中移除
                    self.user_connections[connection_info.user_id].discard(connection_id)
                    if not self.user_connections[connection_info.user_id]:
                        del self.user_connections[connection_info.user_id]
                    
                    # 删除连接
                    del self.connections[connection_id]
                    
                    # 更新统计
                    self.stats['active_connections'] = len(self.connections)
            
            logger.info(f"连接断开: {connection_id}, 剩余连接数: {len(self.connections)}")
            
        except Exception as e:
            logger.error(f"断开连接失败: {str(e)}")
    
    async def subscribe_stock(self, connection_id: str, stock_code: str):
        """订阅股票数据"""
        try:
            async with self.connection_lock:
                if connection_id in self.connections:
                    connection_info = self.connections[connection_id]
                    
                    # 添加订阅
                    connection_info.subscribed_stocks.add(stock_code)
                    self.stock_subscribers[stock_code].add(connection_id)
                    
                    logger.debug(f"订阅股票: {connection_id} -> {stock_code}")
                    
                    # 发送确认消息
                    await self._send_to_connection(connection_id, {
                        'type': 'subscription_confirmed',
                        'stock_code': stock_code,
                        'subscriber_count': len(self.stock_subscribers[stock_code])
                    })
                    
        except Exception as e:
            logger.error(f"订阅股票失败: {str(e)}")
    
    async def unsubscribe_stock(self, connection_id: str, stock_code: str):
        """取消订阅股票数据"""
        await self._unsubscribe_stock_internal(connection_id, stock_code)
    
    async def _unsubscribe_stock_internal(self, connection_id: str, stock_code: str):
        """内部取消订阅方法"""
        try:
            if connection_id in self.connections:
                connection_info = self.connections[connection_id]
                
                # 移除订阅
                connection_info.subscribed_stocks.discard(stock_code)
                self.stock_subscribers[stock_code].discard(connection_id)
                
                # 如果没有订阅者，删除股票记录
                if not self.stock_subscribers[stock_code]:
                    del self.stock_subscribers[stock_code]
                
                logger.debug(f"取消订阅: {connection_id} -> {stock_code}")
                
        except Exception as e:
            logger.error(f"取消订阅失败: {str(e)}")
    
    async def push_stock_data(self, stock_code: str, data: Dict):
        """推送股票数据"""
        try:
            # 添加到推送队列
            message = {
                'type': 'stock_data',
                'stock_code': stock_code,
                'data': data,
                'timestamp': time.time()
            }
            
            await self.push_queue.put((stock_code, message))
            
        except Exception as e:
            logger.error(f"推送股票数据失败: {str(e)}")
    
    async def broadcast_message(self, message: Dict, user_ids: List[str] = None):
        """广播消息"""
        try:
            broadcast_data = {
                'message': message,
                'user_ids': user_ids,
                'timestamp': time.time()
            }
            
            await self.broadcast_queue.put(broadcast_data)
            
        except Exception as e:
            logger.error(f"广播消息失败: {str(e)}")
    
    async def _push_loop(self):
        """推送循环"""
        while self.running:
            try:
                # 批量处理推送队列
                batch_messages = []
                
                # 收集批量消息
                try:
                    # 等待第一个消息
                    stock_code, message = await asyncio.wait_for(
                        self.push_queue.get(), timeout=1.0
                    )
                    batch_messages.append((stock_code, message))
                    
                    # 收集更多消息（非阻塞）
                    for _ in range(self.batch_size - 1):
                        try:
                            stock_code, message = self.push_queue.get_nowait()
                            batch_messages.append((stock_code, message))
                        except asyncio.QueueEmpty:
                            break
                            
                except asyncio.TimeoutError:
                    continue
                
                if batch_messages:
                    await self._process_push_batch(batch_messages)
                
            except Exception as e:
                logger.error(f"推送循环错误: {str(e)}")
                await asyncio.sleep(0.1)
    
    async def _process_push_batch(self, batch_messages: List[tuple]):
        """处理推送批次"""
        try:
            start_time = time.time()
            
            # 按股票代码分组
            stock_groups = defaultdict(list)
            for stock_code, message in batch_messages:
                stock_groups[stock_code].append(message)
            
            # 并行推送
            tasks = []
            for stock_code, messages in stock_groups.items():
                if stock_code in self.stock_subscribers:
                    task = self._push_to_subscribers(stock_code, messages)
                    tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # 更新统计
            elapsed = time.time() - start_time
            self.stats['push_rate'] = len(batch_messages) / elapsed if elapsed > 0 else 0
            
        except Exception as e:
            logger.error(f"处理推送批次失败: {str(e)}")
    
    async def _push_to_subscribers(self, stock_code: str, messages: List[Dict]):
        """推送给订阅者"""
        try:
            subscriber_ids = self.stock_subscribers.get(stock_code, set()).copy()
            
            if not subscriber_ids:
                return
            
            # 合并消息
            combined_message = {
                'type': 'stock_data_batch',
                'stock_code': stock_code,
                'data_list': [msg['data'] for msg in messages],
                'count': len(messages),
                'timestamp': time.time()
            }
            
            # 并行发送给所有订阅者
            tasks = []
            for connection_id in subscriber_ids:
                task = self._send_to_connection(connection_id, combined_message)
                tasks.append(task)
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 统计发送结果
                success_count = sum(1 for r in results if not isinstance(r, Exception))
                self.stats['total_messages_sent'] += success_count
                self.stats['total_messages_failed'] += len(results) - success_count
            
        except Exception as e:
            logger.error(f"推送给订阅者失败: {str(e)}")
    
    async def _send_to_connection(self, connection_id: str, message: Dict):
        """发送消息给指定连接"""
        try:
            if connection_id in self.connections:
                connection_info = self.connections[connection_id]
                await connection_info.websocket.send_json(message)
                return True
            return False
            
        except WebSocketDisconnect:
            # 连接已断开，清理连接
            await self.disconnect(connection_id)
            return False
        except Exception as e:
            logger.debug(f"发送消息失败: {connection_id}, 错误: {str(e)}")
            return False
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self.running:
            try:
                await asyncio.sleep(60)  # 每分钟清理一次
                await self._cleanup_dead_connections()
                self.stats['last_cleanup'] = time.time()
                
            except Exception as e:
                logger.error(f"清理循环错误: {str(e)}")
    
    async def _cleanup_dead_connections(self):
        """清理死连接"""
        try:
            current_time = time.time()
            dead_connections = []
            
            async with self.connection_lock:
                for connection_id, connection_info in self.connections.items():
                    # 检查连接超时
                    if current_time - connection_info.last_ping > self.connection_timeout:
                        dead_connections.append(connection_id)
            
            # 清理死连接
            for connection_id in dead_connections:
                await self.disconnect(connection_id)
            
            if dead_connections:
                logger.info(f"清理了 {len(dead_connections)} 个死连接")
                
        except Exception as e:
            logger.error(f"清理死连接失败: {str(e)}")
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while self.running:
            try:
                await asyncio.sleep(self.ping_interval)
                
                # 发送心跳给所有连接
                ping_message = {
                    'type': 'ping',
                    'timestamp': time.time()
                }
                
                connection_ids = list(self.connections.keys())
                tasks = []
                
                for connection_id in connection_ids:
                    task = self._send_to_connection(connection_id, ping_message)
                    tasks.append(task)
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                
            except Exception as e:
                logger.error(f"心跳循环错误: {str(e)}")
    
    async def _close_all_connections(self):
        """关闭所有连接"""
        try:
            connection_ids = list(self.connections.keys())
            
            for connection_id in connection_ids:
                try:
                    connection_info = self.connections[connection_id]
                    await connection_info.websocket.close()
                except Exception:
                    pass
            
            self.connections.clear()
            self.stock_subscribers.clear()
            self.user_connections.clear()
            
        except Exception as e:
            logger.error(f"关闭所有连接失败: {str(e)}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = self.stats.copy()
        stats['stock_subscriptions'] = len(self.stock_subscribers)
        stats['total_subscriptions'] = sum(len(subs) for subs in self.stock_subscribers.values())
        return stats

# 全局WebSocket管理器实例
optimized_websocket_manager = OptimizedWebSocketManager()
