#!/usr/bin/env python3
"""
健壮的股票推送接收器 - 解决所有潜在问题
专门处理5000+股票推送的网络连接问题
"""

import socket
import struct
import time
import threading
import queue
import hashlib
import json
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# 最小化日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"

@dataclass
class RobustConnectionConfig:
    """健壮的连接配置"""
    # 服务器配置 - 需要填入实际值
    api_key: str = "process.env.STOCK_API_KEY"
    host: str = "your.server.host"  # 替换为实际服务器地址
    port: int = 8888  # 替换为实际端口
    token: str = "your_auth_token"  # 替换为实际token
    
    # 网络优化配置
    buffer_size: int = 1024 * 1024  # 1MB缓冲区
    socket_timeout: int = 10  # Socket超时
    connect_timeout: int = 30  # 连接超时
    
    # 心跳配置
    heartbeat_interval: int = 30  # 心跳间隔(秒)
    heartbeat_timeout: int = 60  # 心跳超时(秒)
    
    # 重连配置
    max_retries: int = 10  # 最大重试次数
    retry_base_delay: int = 2  # 重试基础延迟
    retry_max_delay: int = 300  # 最大重试延迟(5分钟)
    
    # 数据验证配置
    enable_checksum: bool = True  # 启用校验和
    max_message_size: int = 50 * 1024 * 1024  # 50MB最大消息
    
    # 性能配置
    queue_size: int = 100000  # 队列大小
    batch_size: int = 2000  # 批量大小

class RobustPushReceiver:
    """健壮的推送接收器"""
    
    def __init__(self, config: RobustConnectionConfig = None):
        self.config = config or RobustConnectionConfig()
        
        # 连接状态
        self.state = ConnectionState.DISCONNECTED
        self.socket = None
        self.running = False
        
        # 线程管理
        self.threads = []
        self.thread_lock = threading.Lock()
        
        # 数据队列
        self.data_queue = queue.Queue(maxsize=self.config.queue_size)
        
        # 心跳管理
        self.last_heartbeat_sent = 0
        self.last_heartbeat_received = 0
        self.heartbeat_sequence = 0
        
        # 连接质量监控
        self.connection_metrics = {
            'total_received': 0,
            'total_errors': 0,
            'reconnect_count': 0,
            'last_connect_time': 0,
            'avg_latency': 0,
            'packet_loss_rate': 0,
            'connection_uptime': 0
        }
        
        # Redis连接
        self.redis_client = None
        self._init_redis()
        
        # 回调函数
        self.on_data_callback: Optional[Callable] = None
        self.on_state_change_callback: Optional[Callable] = None
    
    def _init_redis(self):
        """初始化Redis连接"""
        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=4,  # 专用数据库
                decode_responses=False,
                max_connections=20,
                socket_keepalive=True,
                retry_on_timeout=True
            )
            self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}")
            self.redis_client = None
    
    def start(self):
        """启动接收器"""
        if self.running:
            return
        
        logger.warning("🚀 启动健壮推送接收器...")
        self.running = True
        
        # 启动线程
        self.threads = [
            threading.Thread(target=self._connection_loop, daemon=True),
            threading.Thread(target=self._heartbeat_loop, daemon=True),
            threading.Thread(target=self._data_process_loop, daemon=True),
            threading.Thread(target=self._monitor_loop, daemon=True)
        ]
        
        for thread in self.threads:
            thread.start()
        
        logger.warning("✅ 健壮推送接收器启动完成")
    
    def stop(self):
        """停止接收器"""
        self.running = False
        self._disconnect()
        
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
    
    def _connection_loop(self):
        """连接循环"""
        retry_count = 0
        
        while self.running:
            try:
                if self.state == ConnectionState.DISCONNECTED:
                    self._set_state(ConnectionState.CONNECTING)
                    
                    if self._connect_to_server():
                        retry_count = 0
                        self._set_state(ConnectionState.CONNECTED)
                        self.connection_metrics['last_connect_time'] = time.time()
                        
                        # 开始接收数据
                        self._receive_data_loop()
                    else:
                        self._set_state(ConnectionState.FAILED)
                        retry_count += 1
                        
                        if retry_count >= self.config.max_retries:
                            logger.error("达到最大重试次数,停止连接")
                            break
                        
                        # 计算重试延迟
                        delay = min(
                            self.config.retry_base_delay ** retry_count,
                            self.config.retry_max_delay
                        )
                        
                        logger.warning(f"连接失败,{delay}秒后重试 ({retry_count}/{self.config.max_retries})")
                        time.sleep(delay)
                
            except Exception as e:
                logger.error(f"连接循环异常: {e}")
                time.sleep(5)
    
    def _connect_to_server(self) -> bool:
        """连接到服务器"""
        try:
            # 检查配置
            if not self.config.host or not self.config.port or not self.config.token:
                logger.error("服务器配置不完整")
                return False
            
            # 创建socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # 优化socket设置
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.config.buffer_size)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.config.buffer_size)
            
            # 设置超时
            self.socket.settimeout(self.config.connect_timeout)
            
            # 连接服务器
            self.socket.connect((self.config.host, self.config.port))
            
            # 发送认证
            auth_data = {
                'api_key': self.config.api_key,
                'token': self.config.token,
                'client_type': 'robust_receiver',
                'version': '1.0'
            }
            
            auth_bytes = json.dumps(auth_data).encode('utf-8')
            self._send_message(auth_bytes)
            
            # 等待认证响应
            response = self._receive_message()
            if response and b'auth_success' in response:
                logger.warning(f"连接成功: {self.config.host}:{self.config.port}")
                return True
            else:
                logger.error("认证失败")
                return False
                
        except Exception as e:
            logger.error(f"连接失败: {e}")
            self._disconnect()
            return False
    
    def _send_message(self, data: bytes):
        """发送消息"""
        if not self.socket:
            return False
        
        try:
            # 计算校验和
            checksum = hashlib.md5(data).digest() if self.config.enable_checksum else b''
            
            # 构造消息头
            header = struct.pack('<II', len(data), len(checksum))
            
            # 发送消息
            self.socket.sendall(header + checksum + data)
            return True
            
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False
    
    def _receive_message(self) -> Optional[bytes]:
        """接收消息"""
        try:
            # 接收消息头
            header = self._recv_exact(8)  # 4字节长度 + 4字节校验和长度
            if not header:
                return None
            
            data_len, checksum_len = struct.unpack('<II', header)
            
            # 验证消息长度
            if data_len > self.config.max_message_size:
                logger.warning(f"消息过大: {data_len}")
                return None
            
            # 接收校验和
            checksum = self._recv_exact(checksum_len) if checksum_len > 0 else b''
            
            # 接收数据
            data = self._recv_exact(data_len)
            if not data:
                return None
            
            # 验证校验和
            if checksum and self.config.enable_checksum:
                expected_checksum = hashlib.md5(data).digest()
                if checksum != expected_checksum:
                    logger.warning("校验和验证失败")
                    return None
            
            return data
            
        except Exception as e:
            logger.error(f"接收消息失败: {e}")
            return None
    
    def _recv_exact(self, n: int) -> Optional[bytes]:
        """精确接收指定字节数"""
        try:
            data = bytearray()
            while len(data) < n:
                chunk = self.socket.recv(n - len(data))
                if not chunk:
                    return None
                data.extend(chunk)
            return bytes(data)
        except Exception:
            return None

    def _receive_data_loop(self):
        """数据接收循环"""
        self.socket.settimeout(self.config.socket_timeout)

        while self.running and self.state == ConnectionState.CONNECTED:
            try:
                message = self._receive_message()
                if message is None:
                    logger.warning("连接断开")
                    break

                # 检查是否是心跳响应
                if self._is_heartbeat_response(message):
                    self.last_heartbeat_received = time.time()
                    continue

                # 立即放入队列
                try:
                    self.data_queue.put_nowait({
                        'data': message,
                        'timestamp': time.time(),
                        'size': len(message)
                    })

                    self.connection_metrics['total_received'] += 1

                except queue.Full:
                    logger.warning("数据队列已满")
                    self.connection_metrics['total_errors'] += 1

            except socket.timeout:
                # 超时是正常的,继续循环
                continue
            except Exception as e:
                logger.error(f"数据接收异常: {e}")
                break

        self._set_state(ConnectionState.DISCONNECTED)

    def _heartbeat_loop(self):
        """心跳循环"""
        while self.running:
            try:
                if self.state == ConnectionState.CONNECTED:
                    current_time = time.time()

                    # 发送心跳
                    if current_time - self.last_heartbeat_sent >= self.config.heartbeat_interval:
                        self._send_heartbeat()

                    # 检查心跳超时
                    if (current_time - self.last_heartbeat_received >= self.config.heartbeat_timeout and
                        self.last_heartbeat_received > 0):
                        logger.warning("心跳超时,断开连接")
                        self._disconnect()

                time.sleep(5)  # 5秒检查一次

            except Exception as e:
                logger.error(f"心跳循环异常: {e}")

    def _send_heartbeat(self):
        """发送心跳"""
        try:
            heartbeat_data = {
                'type': 'heartbeat',
                'timestamp': time.time(),
                'client_id': id(self)
            }

            heartbeat_bytes = json.dumps(heartbeat_data).encode('utf-8')
            if self._send_message(heartbeat_bytes):
                self.last_heartbeat_sent = time.time()
                logger.debug("心跳发送成功")
            else:
                logger.warning("心跳发送失败")

        except Exception as e:
            logger.error(f"发送心跳异常: {e}")

    def _is_heartbeat_response(self, message: bytes) -> bool:
        """检查是否是心跳响应"""
        try:
            if message.startswith(b'{'):
                data = json.loads(message.decode('utf-8'))
                return data.get('type') == 'heartbeat_response'
        except Exception:
            pass
        return False

    def _disconnect(self):
        """断开连接"""
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            finally:
                self.socket = None

        self._set_state(ConnectionState.DISCONNECTED)

    def _data_processor_loop(self):
        """数据处理循环"""
        batch = []
        last_process_time = time.time()

        while self.running:
            try:
                # 从队列获取数据
                try:
                    item = self.data_queue.get(timeout=1)
                    batch.append(item)
                except queue.Empty:
                    # 超时是正常的,检查是否需要处理批次
                    pass

                # 检查是否需要处理批次
                current_time = time.time()
                should_process = (
                    len(batch) >= self.config.batch_size or
                    (batch and current_time - last_process_time >= 1.0)  # 1秒超时
                )

                if should_process and batch:
                    self._process_batch(batch)
                    batch.clear()
                    last_process_time = current_time

            except Exception as e:
                logger.error(f"数据处理循环异常: {e}")
                if self.on_error_callback:
                    try:
                        self.on_error_callback(e)
                    except Exception:
                        pass

    def _process_batch(self, batch: list):
        """处理数据批次"""
        try:
            if self.on_data_callback:
                # 解析数据
                parsed_data = []
                for item in batch:
                    parsed = self._parse_data(item['data'])
                    if parsed:
                        parsed['receive_timestamp'] = item['timestamp']
                        parsed['data_size'] = item['size']
                        parsed_data.append(parsed)

                if parsed_data:
                    self.on_data_callback(parsed_data)

        except Exception as e:
            logger.error(f"批次处理失败: {e}")
            self.connection_metrics['total_errors'] += 1

    def _parse_data(self, data: bytes) -> Optional[dict]:
        """解析推送数据"""
        try:
            # JSON格式解析
            if data.startswith(b'{'):
                parsed = json.loads(data.decode('utf-8'))

                # 验证必要字段
                if 'code' in parsed and 'price' in parsed:
                    return {
                        'stock_code': parsed.get('code'),
                        'price': float(parsed.get('price', 0)),
                        'volume': int(parsed.get('volume', 0)),
                        'timestamp': parsed.get('timestamp', time.time()),
                        'raw_data': parsed
                    }

            # 其他数据格式解析可以在这里添加
            logger.warning(f"未知数据格式: {data[:50]}")
            return None

        except Exception as e:
            logger.error(f"数据解析失败: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """获取接收器状态"""
        return {
            'state': self.state.value,
            'running': self.running,
            'queue_size': self.data_queue.qsize(),
            'metrics': self.connection_metrics.copy(),
            'config': {
                'host': self.config.host,
                'port': self.config.port,
                'api_key': self.config.api_key[:10] + "..." if self.config.api_key else "未设置"
            }
        }

# 配置验证工具
class ConfigValidator:
    """配置验证器"""

    @staticmethod
    def validate_config(config: RobustConnectionConfig) -> Dict[str, Any]:
        """验证配置"""
        issues = []
        warnings = []

        # 检查服务器配置
        if not config.host or config.host == "your.server.host":
            issues.append("❌ 服务器地址未配置")

        if config.port <= 0 or config.port == 8888:
            issues.append("❌ 服务器端口未配置")

        if not config.token or config.token == "your_auth_token":
            issues.append("❌ 认证token未配置")

        if not config.api_key:
            issues.append("❌ API密钥未配置")

        # 检查性能配置
        if config.buffer_size < 64 * 1024:
            warnings.append("⚠️ 缓冲区大小可能过小")

        if config.heartbeat_interval > 60:
            warnings.append("⚠️ 心跳间隔可能过长")

        if config.max_retries < 3:
            warnings.append("⚠️ 重试次数可能过少")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'total_problems': len(issues) + len(warnings)
        }

# 使用示例
def create_robust_receiver() -> RobustPushReceiver:
    """创建健壮的接收器"""
    config = RobustConnectionConfig(
        api_key="process.env.STOCK_API_KEY",
        host="your.actual.server.host",  # 需要替换
        port=8888,  # 需要替换
        token="your_actual_token"  # 需要替换
    )

    # 验证配置
    validation = ConfigValidator.validate_config(config)
    if not validation['valid']:
        logger.error("配置验证失败:")
        for issue in validation['issues']:
            logger.error(f"  {issue}")
        for warning in validation['warnings']:
            logger.warning(f"  {warning}")

    receiver = RobustPushReceiver(config)

    # 设置回调
    def on_data(data_batch):
        logger.info(f"接收到 {len(data_batch)} 条数据")
        for item in data_batch:
            logger.debug(f"股票: {item['stock_code']}, 价格: {item['price']}")

    def on_error(error):
        logger.error(f"接收器错误: {error}")

    def on_state_change(old_state, new_state):
        logger.info(f"状态变更: {old_state.value} -> {new_state.value}")

    receiver.set_callbacks(on_data, on_error, on_state_change)

    return receiver

if __name__ == "__main__":
    # 测试代码
    receiver = create_robust_receiver()

    try:
        receiver.start()
        logger.info("接收器已启动,按Ctrl+C停止")

        while True:
            status = receiver.get_status()
            logger.info(f"状态: {status['state']}, 队列: {status['queue_size']}")
            time.sleep(10)

    except KeyboardInterrupt:
        logger.info("收到停止信号")
    finally:
        receiver.stop()
        logger.info("程序结束")
    
    def _receive_data_loop(self):
        """数据接收循环"""
        self.socket.settimeout(self.config.socket_timeout)
        
        while self.running and self.state == ConnectionState.CONNECTED:
            try:
                message = self._receive_message()
                if message is None:
                    logger.warning("连接断开")
                    break
                
                # 检查是否是心跳响应
                if self._is_heartbeat_response(message):
                    self.last_heartbeat_received = time.time()
                    continue
                
                # 立即放入队列
                try:
                    self.data_queue.put_nowait({
                        'data': message,
                        'timestamp': time.time(),
                        'size': len(message)
                    })
                    
                    self.connection_metrics['total_received'] += 1
                    
                except queue.Full:
                    logger.warning("数据队列已满")
                    self.connection_metrics['total_errors'] += 1
                
            except socket.timeout:
                # 超时是正常的,继续循环
                continue
            except Exception as e:
                logger.error(f"数据接收异常: {e}")
                break
        
        self._set_state(ConnectionState.DISCONNECTED)
    
    def _heartbeat_loop(self):
        """心跳循环"""
        while self.running:
            try:
                if self.state == ConnectionState.CONNECTED:
                    current_time = time.time()
                    
                    # 发送心跳
                    if current_time - self.last_heartbeat_sent >= self.config.heartbeat_interval:
                        self._send_heartbeat()
                    
                    # 检查心跳超时
                    if (current_time - self.last_heartbeat_received >= self.config.heartbeat_timeout and
                        self.last_heartbeat_received > 0):
                        logger.warning("心跳超时,断开连接")
                        self._disconnect()
                
                time.sleep(5)  # 5秒检查一次
                
            except Exception as e:
                logger.error(f"心跳循环异常: {e}")
    
    def _send_heartbeat(self):
        """发送心跳"""
        try:
            self.heartbeat_sequence += 1
            heartbeat = {
                'type': 'heartbeat',
                'sequence': self.heartbeat_sequence,
                'timestamp': time.time()
            }
            
            heartbeat_bytes = json.dumps(heartbeat).encode('utf-8')
            if self._send_message(heartbeat_bytes):
                self.last_heartbeat_sent = time.time()
            
        except Exception as e:
            logger.error(f"发送心跳失败: {e}")
    
    def _is_heartbeat_response(self, message: bytes) -> bool:
        """检查是否是心跳响应"""
        try:
            data = json.loads(message.decode('utf-8'))
            return data.get('type') == 'heartbeat_response'
        except:
            return False
    
    def _data_process_loop(self):
        """数据处理循环"""
        batch_data = []
        last_process_time = time.time()

        while self.running:
            try:
                # 收集批量数据
                try:
                    item = self.data_queue.get(timeout=1)

                    # 数据包完整性验证
                    if not self._validate_packet(item['data']):
                        logger.warning("数据包完整性验证失败")
                        continue

                    # 解析数据
                    parsed_data = self._parse_data(item['data'])
                    if parsed_data:
                        batch_data.append({
                            'parsed_data': parsed_data,
                            'timestamp': item['timestamp'],
                            'size': item['size']
                        })

                        self.connection_metrics['packets_received'] += 1
                        self.connection_metrics['last_packet_time'] = time.time()

                        # 更新连接质量统计
                        self._update_connection_quality()

                except queue.Empty:
                    # 队列为空,继续循环
                    pass

                # 批量处理数据
                current_time = time.time()
                if (len(batch_data) >= self.config.batch_size or
                    current_time - last_process_time >= self.config.batch_timeout):

                    if batch_data and self.data_callback:
                        try:
                            self.data_callback(batch_data)
                            self.connection_metrics['batches_processed'] += 1
                        except Exception as e:
                            logger.error(f"数据回调处理失败: {e}")

                    batch_data.clear()
                    last_process_time = current_time

            except Exception as e:
                logger.error(f"数据处理循环异常: {e}")
                time.sleep(1)

    def _validate_packet(self, data: bytes) -> bool:
        """验证数据包完整性"""
        try:
            # 基本长度检查
            if len(data) < 10:  # 最小数据包长度
                return False

            # 尝试解析JSON格式
            if data.startswith(b'{'):
                json.loads(data.decode('utf-8'))
                return True

            # 其他格式验证可以在这里添加
            return True

        except Exception:
            return False

    def _parse_data(self, data: bytes) -> Optional[dict]:
        """解析推送数据"""
        try:
            # JSON格式解析
            if data.startswith(b'{'):
                parsed = json.loads(data.decode('utf-8'))

                # 验证必要字段
                if 'code' in parsed and 'price' in parsed:
                    return {
                        'stock_code': parsed.get('code'),
                        'price': float(parsed.get('price', 0)),
                        'volume': int(parsed.get('volume', 0)),
                        'timestamp': parsed.get('timestamp', time.time()),
                        'raw_data': parsed
                    }

            # 其他数据格式解析可以在这里添加
            logger.warning(f"未知数据格式: {data[:50]}")
            return None

        except Exception as e:
            logger.error(f"数据解析失败: {e}")
            return None

    def _update_connection_quality(self):
        """更新连接质量统计"""
        try:
            current_time = time.time()

            # 计算延迟
            if hasattr(self, 'last_ping_time') and hasattr(self, 'last_pong_time'):
                if self.last_pong_time > self.last_ping_time:
                    latency = (self.last_pong_time - self.last_ping_time) * 1000
                    self.connection_metrics['latency_ms'] = latency

            # 计算数据接收速率
            time_window = 60  # 1分钟窗口
            if current_time - self.connection_metrics.get('rate_calc_time', 0) >= time_window:
                packets_in_window = self.connection_metrics['packets_received'] - self.connection_metrics.get('last_packet_count', 0)
                self.connection_metrics['packets_per_minute'] = packets_in_window
                self.connection_metrics['last_packet_count'] = self.connection_metrics['packets_received']
                self.connection_metrics['rate_calc_time'] = current_time

        except Exception as e:
            logger.error(f"连接质量更新失败: {e}")

    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                current_time = time.time()

                # 检查连接超时
                if (self.state == ConnectionState.CONNECTED and
                    current_time - self.connection_metrics.get('last_packet_time', current_time) > self.config.data_timeout):
                    logger.warning("数据接收超时")
                    self._disconnect()

                # 检查队列积压
                queue_size = self.data_queue.qsize()
                if queue_size > self.config.max_queue_size * 0.8:
                    logger.warning(f"数据队列积压严重: {queue_size}")

                # 记录监控指标
                self.connection_metrics['queue_size'] = queue_size
                self.connection_metrics['monitor_time'] = current_time

                time.sleep(30)  # 30秒检查一次

            except Exception as e:
                logger.error(f"监控循环异常: {e}")
                time.sleep(30)
    
    def _process_batch(self, batch_data: list):
        """处理批量数据"""
        try:
            if self.redis_client:
                # 存储到Redis
                pipe = self.redis_client.pipeline()
                
                for item in batch_data:
                    pipe.lpush('stock:robust:queue', item['data'])
                
                pipe.ltrim('stock:robust:queue', 0, 200000)  # 保留20万条
                pipe.execute()
            
            # 调用回调函数
            if self.on_data_callback:
                self.on_data_callback(batch_data)
                
        except Exception as e:
            logger.error(f"批量处理失败: {e}")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 更新连接时长
                if self.state == ConnectionState.CONNECTED:
                    self.connection_metrics['connection_uptime'] = (
                        time.time() - self.connection_metrics['last_connect_time']
                    )
                
                # 计算丢包率
                total_packets = self.connection_metrics['total_received'] + self.connection_metrics['total_errors']
                if total_packets > 0:
                    self.connection_metrics['packet_loss_rate'] = (
                        self.connection_metrics['total_errors'] / total_packets * 100
                    )
                
                time.sleep(30)  # 30秒更新一次
                
            except Exception:
                pass
    
    def _set_state(self, new_state: ConnectionState):
        """设置连接状态"""
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            
            if self.on_state_change_callback:
                self.on_state_change_callback(old_state, new_state)
    
    def _disconnect(self):
        """断开连接"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        self._set_state(ConnectionState.DISCONNECTED)
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取连接指标"""
        return {
            'state': self.state.value,
            'queue_size': self.data_queue.qsize(),
            'metrics': self.connection_metrics.copy()
        }
    
    def set_callbacks(self, on_data: Callable = None, on_state_change: Callable = None):
        """设置回调函数"""
        self.on_data_callback = on_data
        self.on_state_change_callback = on_state_change

class PushReceiverDiagnostics:
    """推送接收器诊断工具"""

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.recommendations = []

    def check_configuration(self, config: RobustConnectionConfig) -> Dict[str, Any]:
        """检查配置问题"""
        self.issues = []
        self.warnings = []
        self.recommendations = []

        # 检查服务器配置
        if not config.host or config.host == "your.server.host":
            self.issues.append("❌ 服务器地址未配置")
            self.recommendations.append("请设置正确的服务器地址")

        if not config.port or config.port == 0:
            self.issues.append("❌ 服务器端口未配置")
            self.recommendations.append("请设置正确的服务器端口")

        if not config.token or config.token == "your_auth_token":
            self.issues.append("❌ 认证token未配置")
            self.recommendations.append("请设置正确的认证token")

        # 检查网络配置
        if config.buffer_size < 64 * 1024:
            self.warnings.append("⚠️ 缓冲区大小可能过小")
            self.recommendations.append("建议缓冲区大小至少64KB")

        if config.heartbeat_interval > 60:
            self.warnings.append("⚠️ 心跳间隔可能过长")
            self.recommendations.append("建议心跳间隔不超过60秒")

        # 检查性能配置
        if config.queue_size < 50000:
            self.warnings.append("⚠️ 队列大小可能不足")
            self.recommendations.append("建议队列大小至少50000")

        return {
            'issues': self.issues,
            'warnings': self.warnings,
            'recommendations': self.recommendations,
            'is_ready': len(self.issues) == 0
        }

    def check_network_connectivity(self, host: str, port: int) -> Dict[str, Any]:
        """检查网络连通性"""
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(10)

            start_time = time.time()
            result = test_socket.connect_ex((host, port))
            latency = (time.time() - start_time) * 1000

            test_socket.close()

            if result == 0:
                return {
                    'connected': True,
                    'latency_ms': latency,
                    'status': f"✅ 连接成功,延迟: {latency:.2f}ms"
                }
            else:
                return {
                    'connected': False,
                    'error_code': result,
                    'status': f"❌ 连接失败,错误码: {result}"
                }

        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'status': f"❌ 连接异常: {e}"
            }

    def check_system_resources(self) -> Dict[str, Any]:
        """检查系统资源"""
        try:
            # 内存检查
            memory = psutil.virtual_memory()
            memory_available_gb = memory.available / (1024**3)

            # CPU检查
            cpu_percent = psutil.cpu_percent(interval=1)

            # 网络检查
            network_stats = psutil.net_io_counters()

            issues = []
            if memory_available_gb < 1.0:
                issues.append("❌ 可用内存不足1GB")

            if cpu_percent > 80:
                issues.append("❌ CPU使用率过高")

            return {
                'memory_available_gb': memory_available_gb,
                'cpu_percent': cpu_percent,
                'network_bytes_sent': network_stats.bytes_sent,
                'network_bytes_recv': network_stats.bytes_recv,
                'issues': issues,
                'status': '✅ 系统资源充足' if not issues else '⚠️ 系统资源不足'
            }

        except Exception as e:
            return {
                'error': str(e),
                'status': f"❌ 系统检查失败: {e}"
            }

    def generate_report(self, config: RobustConnectionConfig) -> str:
        """生成诊断报告"""
        report = "🔍 推送接收器诊断报告\n"
        report += "=" * 50 + "\n\n"

        # 配置检查
        config_result = self.check_configuration(config)
        report += "📋 配置检查:\n"

        if config_result['is_ready']:
            report += "✅ 配置完整\n"
        else:
            for issue in config_result['issues']:
                report += f"  {issue}\n"

        for warning in config_result['warnings']:
            report += f"  {warning}\n"

        # 网络连通性检查
        if config.host and config.host != "your.server.host" and config.port:
            network_result = self.check_network_connectivity(config.host, config.port)
            report += f"\n🌐 网络连通性:\n  {network_result['status']}\n"

        # 系统资源检查
        system_result = self.check_system_resources()
        report += f"\n💻 系统资源:\n  {system_result['status']}\n"
        report += f"  内存可用: {system_result.get('memory_available_gb', 0):.2f}GB\n"
        report += f"  CPU使用率: {system_result.get('cpu_percent', 0):.1f}%\n"

        # 建议
        if config_result['recommendations']:
            report += "\n💡 建议:\n"
            for rec in config_result['recommendations']:
                report += f"  • {rec}\n"

        return report

# 使用示例和测试
if __name__ == '__main__':
    print("🚀 推送接收器诊断工具")

    # 创建诊断工具
    diagnostics = PushReceiverDiagnostics()

    # 测试配置
    test_config = RobustConnectionConfig(
        host="your.server.host",  # 需要替换
        port=8888,  # 需要替换
        token="your_auth_token"  # 需要替换
    )

    # 生成诊断报告
    report = diagnostics.generate_report(test_config)
    print(report)

    # 如果配置完整,启动接收器
    config_check = diagnostics.check_configuration(test_config)

    if config_check['is_ready']:
        print("\n🚀 配置完整,启动接收器...")

        receiver = RobustPushReceiver(test_config)

        def on_data_received(batch_data):
            print(f"📊 接收到 {len(batch_data)} 条数据")

        def on_state_changed(old_state, new_state):
            print(f"🔄 连接状态: {old_state.value} -> {new_state.value}")

        receiver.set_callbacks(on_data_received, on_state_changed)

        try:
            receiver.start()

            while True:
                metrics = receiver.get_metrics()
                print(f"📈 状态: {metrics['state']}, 队列: {metrics['queue_size']}")
                time.sleep(10)

        except KeyboardInterrupt:
            print("⏹️ 停止接收器")
        finally:
            receiver.stop()
    else:
        print("\n❌ 配置不完整,请先解决配置问题")
