"""
实时股票数据接收器 - 高性能Socket接收，直接存入Redis
API Key: QT_wat5QfcJ6N9pDZM5
重要：数据堆积超过100M会被强制断开，必须快速处理！
"""
import socket
import struct
import threading
import time
import json
import logging
import hashlib
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import queue
from enum import Enum

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    """连接状态"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    FAILED = "failed"

@dataclass
class ConnectionConfig:
    """连接配置"""
    api_key: str = "QT_wat5QfcJ6N9pDZM5"
    host: str = ""  # 需要填入实际服务器地址
    port: int = 0   # 需要填入实际端口
    token: str = ""  # 需要填入实际token

    # 性能配置
    buffer_size: int = 65536  # 64KB缓冲区
    max_queue_size: int = 100000  # 最大队列大小
    redis_batch_size: int = 1000  # Redis批量写入大小

    # 心跳配置
    heartbeat_interval: int = 30  # 心跳间隔(秒)
    heartbeat_timeout: int = 90   # 心跳超时(秒)

    # 重连配置
    max_retries: int = 10         # 最大重试次数
    retry_base_delay: int = 2     # 重试基础延迟
    retry_max_delay: int = 300    # 最大重试延迟(5分钟)

    # 数据验证配置
    enable_checksum: bool = True  # 启用校验和
    max_message_size: int = 10 * 1024 * 1024  # 10MB最大消息
    
class RealtimeStockReceiver:
    """实时股票数据接收器"""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.running = False
        self.socket: Optional[socket.socket] = None
        
        # Redis连接
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=2,  # 专用数据库
            decode_responses=False,  # 二进制模式提高性能
            max_connections=20,
            socket_keepalive=True,
            socket_keepalive_options={},
            health_check_interval=30
        )
        
        # 高性能队列
        self.data_queue = queue.Queue(maxsize=self.config.max_queue_size)
        
        # 性能统计
        self.stats = {
            'received_count': 0,
            'processed_count': 0,
            'redis_stored_count': 0,
            'error_count': 0,
            'last_receive_time': 0,
            'data_rate_per_second': 0,
            'queue_size': 0,
            'connection_status': 'disconnected'
        }
        
        # 线程
        self.receive_thread: Optional[threading.Thread] = None
        self.process_thread: Optional[threading.Thread] = None
        
        # 回调函数
        self.data_callbacks = []
        
    def add_data_callback(self, callback: Callable):
        """添加数据处理回调"""
        self.data_callbacks.append(callback)
    
    def start(self):
        """启动接收器"""
        try:
            logger.info("启动实时股票数据接收器...")
            
            # 测试Redis连接
            self.redis_client.ping()
            logger.info("Redis连接成功")
            
            self.running = True
            
            # 启动接收线程
            self.receive_thread = threading.Thread(
                target=self._receive_loop,
                daemon=True,
                name="StockReceiver"
            )
            self.receive_thread.start()
            
            # 启动处理线程
            self.process_thread = threading.Thread(
                target=self._process_loop,
                daemon=True,
                name="StockProcessor"
            )
            self.process_thread.start()
            
            logger.info("实时股票数据接收器启动成功")
            
        except Exception as e:
            logger.error(f"启动接收器失败: {str(e)}")
            raise
    
    def stop(self):
        """停止接收器"""
        logger.info("停止实时股票数据接收器...")
        
        self.running = False
        
        # 关闭socket连接
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
        
        # 等待线程结束
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=5)
        
        if self.process_thread and self.process_thread.is_alive():
            self.process_thread.join(timeout=5)
        
        # 关闭Redis连接
        try:
            self.redis_client.close()
        except Exception:
            pass
        
        logger.info("实时股票数据接收器已停止")
    
    def _connect_to_server(self) -> bool:
        """连接到股票数据服务器"""
        try:
            # 创建socket连接
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)  # 30秒超时
            
            # 设置socket选项优化性能
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.config.buffer_size)
            
            # 连接服务器
            self.socket.connect((self.config.host, self.config.port))
            logger.info(f"连接到股票数据服务器: {self.config.host}:{self.config.port}")
            
            # 发送token认证
            token_bytes = self.config.token.encode('utf-8')
            self.socket.sendall(token_bytes)
            logger.info("发送认证token成功")
            
            self.stats['connection_status'] = 'connected'
            return True
            
        except Exception as e:
            logger.error(f"连接服务器失败: {str(e)}")
            self.stats['connection_status'] = 'failed'
            return False
    
    def _receive_message(self) -> Optional[bytes]:
        """接收消息 - 优化版本"""
        try:
            # 读取消息长度（前4个字节）
            raw_msglen = self._recvall(4)
            if not raw_msglen:
                return None
            
            msglen = struct.unpack('<I', raw_msglen)[0]  # 小端字节序
            
            # 检查消息长度合理性
            if msglen > 10 * 1024 * 1024:  # 10MB限制
                logger.warning(f"消息长度异常: {msglen}")
                return None
            
            # 根据消息长度读取完整消息
            return self._recvall(msglen)
            
        except Exception as e:
            logger.error(f"接收消息失败: {str(e)}")
            return None
    
    def _recvall(self, n: int) -> Optional[bytes]:
        """接收指定长度的数据"""
        try:
            data = bytearray()
            while len(data) < n:
                packet = self.socket.recv(n - len(data))
                if not packet:
                    return None
                data.extend(packet)
            return bytes(data)
        except Exception:
            return None
    
    def _receive_loop(self):
        """接收循环 - 在独立线程中运行"""
        retry_count = 0
        max_retries = 5
        
        while self.running:
            try:
                # 连接服务器
                if not self._connect_to_server():
                    retry_count += 1
                    if retry_count >= max_retries:
                        logger.error("达到最大重试次数，停止接收")
                        break
                    
                    wait_time = min(2 ** retry_count, 60)  # 指数退避，最大60秒
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                
                retry_count = 0  # 重置重试计数
                
                # 接收数据循环
                while self.running:
                    message = self._receive_message()
                    if message is None:
                        logger.warning("连接断开，准备重连...")
                        break
                    
                    # 立即放入队列，不做任何处理！
                    try:
                        self.data_queue.put_nowait({
                            'data': message,
                            'timestamp': time.time(),
                            'size': len(message)
                        })
                        
                        # 更新统计
                        self.stats['received_count'] += 1
                        self.stats['last_receive_time'] = time.time()
                        self.stats['queue_size'] = self.data_queue.qsize()
                        
                    except queue.Full:
                        logger.error("数据队列已满，丢弃数据！")
                        self.stats['error_count'] += 1
                
            except Exception as e:
                logger.error(f"接收循环错误: {str(e)}")
                self.stats['error_count'] += 1
                time.sleep(1)
            
            finally:
                # 关闭当前连接
                if self.socket:
                    try:
                        self.socket.close()
                    except Exception:
                        pass
                    self.socket = None
                
                self.stats['connection_status'] = 'disconnected'
    
    def _process_loop(self):
        """数据处理循环 - 批量处理提高性能"""
        batch_data = []
        last_process_time = time.time()
        
        while self.running:
            try:
                # 收集批量数据
                try:
                    # 等待数据，但不要阻塞太久
                    data_item = self.data_queue.get(timeout=0.1)
                    batch_data.append(data_item)
                    
                    # 继续收集更多数据（非阻塞）
                    while len(batch_data) < self.config.redis_batch_size:
                        try:
                            data_item = self.data_queue.get_nowait()
                            batch_data.append(data_item)
                        except queue.Empty:
                            break
                            
                except queue.Empty:
                    # 如果没有数据，检查是否需要处理已有批次
                    current_time = time.time()
                    if batch_data and (current_time - last_process_time) > 1.0:
                        # 超过1秒，处理现有批次
                        pass
                    else:
                        continue
                
                if batch_data:
                    # 批量处理数据
                    self._process_batch(batch_data)
                    
                    # 更新统计
                    self.stats['processed_count'] += len(batch_data)
                    self.stats['queue_size'] = self.data_queue.qsize()
                    
                    # 重置批次
                    batch_data = []
                    last_process_time = time.time()
                
            except Exception as e:
                logger.error(f"处理循环错误: {str(e)}")
                self.stats['error_count'] += 1
                time.sleep(0.1)
    
    def _process_batch(self, batch_data: list):
        """批量处理数据"""
        try:
            start_time = time.time()
            
            # 1. 批量存储到Redis（最高优先级）
            self._store_to_redis_batch(batch_data)
            
            # 2. 调用回调函数（如果有）
            if self.data_callbacks:
                for callback in self.data_callbacks:
                    try:
                        callback(batch_data)
                    except Exception as e:
                        logger.error(f"回调函数执行失败: {str(e)}")
            
            # 3. 更新性能统计
            elapsed = time.time() - start_time
            if elapsed > 0:
                self.stats['data_rate_per_second'] = len(batch_data) / elapsed
            
        except Exception as e:
            logger.error(f"批量处理失败: {str(e)}")
            self.stats['error_count'] += 1
    
    def _store_to_redis_batch(self, batch_data: list):
        """批量存储到Redis"""
        try:
            pipe = self.redis_client.pipeline()
            
            for i, data_item in enumerate(batch_data):
                timestamp = data_item['timestamp']
                raw_data = data_item['data']
                
                # 存储原始数据到Redis Stream
                stream_key = f"stock:realtime:raw"
                pipe.xadd(stream_key, {
                    'data': raw_data,
                    'timestamp': timestamp,
                    'size': len(raw_data)
                }, maxlen=100000)  # 保留最近10万条
                
                # 每1000条执行一次，避免pipeline过大
                if (i + 1) % 1000 == 0:
                    pipe.execute()
                    pipe = self.redis_client.pipeline()
            
            # 执行剩余的命令
            if len(batch_data) % 1000 != 0:
                pipe.execute()
            
            self.stats['redis_stored_count'] += len(batch_data)
            
        except Exception as e:
            logger.error(f"Redis批量存储失败: {str(e)}")
            self.stats['error_count'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        stats = self.stats.copy()
        stats['queue_size'] = self.data_queue.qsize()
        return stats
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.stats['connection_status'] == 'connected'

# 全局实例
realtime_stock_receiver = None

def create_receiver(host: str, port: int, token: str) -> RealtimeStockReceiver:
    """创建接收器实例"""
    global realtime_stock_receiver
    
    config = ConnectionConfig(
        host=host,
        port=port,
        token=token
    )
    
    realtime_stock_receiver = RealtimeStockReceiver(config)
    return realtime_stock_receiver

def get_receiver() -> Optional[RealtimeStockReceiver]:
    """获取全局接收器实例"""
    return realtime_stock_receiver
