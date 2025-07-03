"""
茶股帮股票数据接收器 - 专门用于接收茶股帮推送的实时股票数据
服务器: l1.chagubang.com:6380
协议: TCP Socket + 长度前缀协议
"""

import socket
import struct
import json
import time
import threading
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Callable
import queue

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChaguBangReceiver:
    """茶股帮数据接收器"""
    
    def __init__(self, host: str = 'l1.chagubang.com', port: int = 6380, token: str = ''):
        """
        初始化茶股帮数据接收器
        
        Args:
            host: 服务器地址 (默认: l1.chagubang.com)
            port: 服务器端口 (默认: 6380)
            token: 认证token
        """
        self.host = host
        self.port = port
        self.token = token
        
        # 连接状态
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.connected = False
        
        # 数据存储
        self.latest_data: Dict[str, Dict] = {}
        self.data_queue = queue.Queue(maxsize=10000)  # 数据队列
        
        # 回调函数
        self.data_callbacks: list[Callable] = []
        
        # 统计信息
        self.stats = {
            'received_count': 0,
            'error_count': 0,
            'last_receive_time': None,
            'connection_time': None,
            'connection_status': 'disconnected'
        }
        
        # 线程锁
        self.lock = threading.Lock()
    
    def add_data_callback(self, callback: Callable[[Dict], None]):
        """添加数据回调函数"""
        with self.lock:
            self.data_callbacks.append(callback)
    
    def remove_data_callback(self, callback: Callable[[Dict], None]):
        """移除数据回调函数"""
        with self.lock:
            if callback in self.data_callbacks:
                self.data_callbacks.remove(callback)
    
    def receive_message(self, sock: socket.socket) -> Optional[bytes]:
        """
        接收完整消息 - 茶股帮协议
        协议格式: [4字节长度][消息内容]
        """
        try:
            # 读取消息长度（前4个字节，小端字节序）
            raw_msglen = self._recvall(sock, 4)
            if not raw_msglen:
                return None
            
            msglen = struct.unpack('<I', raw_msglen)[0]
            
            # 防止异常大的消息长度
            if msglen > 1024 * 1024:  # 1MB限制
                logger.error(f"消息长度异常: {msglen} bytes")
                return None
            
            if msglen == 0:
                logger.warning("收到空消息")
                return b''
            
            # 根据消息长度读取完整消息
            message = self._recvall(sock, msglen)
            return message
            
        except struct.error as e:
            logger.error(f"解析消息长度失败: {e}")
            return None
        except Exception as e:
            logger.error(f"接收消息失败: {e}")
            return None
    
    def _recvall(self, sock: socket.socket, n: int) -> Optional[bytes]:
        """接收指定长度的数据"""
        data = bytearray()
        while len(data) < n:
            try:
                packet = sock.recv(n - len(data))
                if not packet:
                    logger.warning("连接被远程关闭")
                    return None
                data.extend(packet)
            except socket.timeout:
                logger.warning("接收数据超时")
                return None
            except socket.error as e:
                logger.error(f"Socket错误: {e}")
                return None
            except Exception as e:
                logger.error(f"接收数据异常: {e}")
                return None
        return bytes(data)
    
    def parse_stock_data(self, raw_data: bytes) -> Optional[Dict[str, Any]]:
        """解析股票数据"""
        try:
            if not raw_data:
                return None
                
            decoded_message = raw_data.decode('utf-8')
            
            # 根据数据格式判断是沪深还是北交所
            if decoded_message.startswith('{'):
                return self._parse_bj_data(decoded_message)
            else:
                return self._parse_sh_sz_data(decoded_message)
                
        except UnicodeDecodeError as e:
            logger.error(f"数据解码失败: {e}")
            return None
        except Exception as e:
            logger.error(f"解析股票数据失败: {e}")
            return None
    
    def _parse_sh_sz_data(self, data_str: str) -> Optional[Dict[str, Any]]:
        """解析沪深A股数据 - 33字段格式"""
        try:
            fields = data_str.strip().split('$')
            if len(fields) < 33:
                logger.warning(f"沪深数据字段不足: {len(fields)}/33")
                return None
            
            # 安全转换函数
            def safe_float(value, default=0.0):
                try:
                    return float(value) if value else default
                except (ValueError, TypeError):
                    return default

            def safe_int(value, default=0):
                try:
                    return int(float(value)) if value else default
                except (ValueError, TypeError):
                    return default

            stock_data = {
                'stock_code': fields[0],
                'stock_name': fields[1],
                'last_price': safe_float(fields[6]),
                'open': safe_float(fields[3]),
                'high': safe_float(fields[4]),
                'low': safe_float(fields[5]),
                'volume': safe_int(fields[7]),
                'amount': safe_float(fields[8]),
                'last_close': safe_float(fields[30]),
                'change_pct': 0.0,
                'market': 'SH/SZ',
                'data_source': 'chagubang',
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'raw_fields': fields  # 保留原始字段用于调试
            }
            
            # 计算涨跌幅
            if stock_data['last_close'] > 0:
                stock_data['change_pct'] = (
                    (stock_data['last_price'] - stock_data['last_close']) / 
                    stock_data['last_close'] * 100
                )
            
            return stock_data
            
        except (ValueError, IndexError) as e:
            logger.error(f"解析沪深数据失败: {e}")
            return None
        except Exception as e:
            logger.error(f"解析沪深数据异常: {e}")
            return None
    
    def _parse_bj_data(self, json_str: str) -> Optional[Dict[str, Any]]:
        """解析北交所数据 - JSON格式"""
        try:
            data = json.loads(json_str)
            
            stock_data = {
                'stock_code': data.get('stock_code', ''),
                'stock_name': data.get('stock_name', ''),
                'last_price': float(data.get('lastPrice', 0)),
                'open': float(data.get('open', 0)),
                'high': float(data.get('high', 0)),
                'low': float(data.get('low', 0)),
                'volume': int(data.get('volume', 0)),
                'amount': float(data.get('amount', 0)),
                'last_close': float(data.get('lastClose', 0)),
                'change_pct': 0.0,
                'market': 'BJ',
                'data_source': 'chagubang',
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'raw_data': data  # 保留原始数据用于调试
            }
            
            # 计算涨跌幅
            if stock_data['last_close'] > 0:
                stock_data['change_pct'] = (
                    (stock_data['last_price'] - stock_data['last_close']) / 
                    stock_data['last_close'] * 100
                )
            
            return stock_data
            
        except json.JSONDecodeError as e:
            logger.error(f"解析北交所JSON数据失败: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"解析北交所数据失败: {e}")
            return None
        except Exception as e:
            logger.error(f"解析北交所数据异常: {e}")
            return None
    
    def _connect_to_server(self) -> bool:
        """连接到茶股帮服务器"""
        try:
            # 创建socket连接
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)  # 30秒超时
            
            # 设置socket选项
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            
            # 连接服务器
            logger.info(f"正在连接茶股帮服务器: {self.host}:{self.port}")
            self.socket.connect((self.host, self.port))
            logger.info(f"成功连接到茶股帮服务器: {self.host}:{self.port}")
            
            # 发送token认证
            if self.token:
                token_bytes = self.token.encode('utf-8')
                self.socket.sendall(token_bytes)
                logger.info(f"发送认证token: {self.token}")
            else:
                # 发送空token
                self.socket.sendall(b'')
                logger.info("发送空token")

            # 等待服务器响应
            time.sleep(1)

            # 尝试发送订阅消息（如果需要）
            try:
                # 发送一个简单的订阅请求
                subscribe_msg = b'SUBSCRIBE_ALL'
                self.socket.sendall(subscribe_msg)
                logger.info("发送订阅消息")
            except Exception as e:
                logger.warning(f"发送订阅消息失败: {e}")
                # 不影响连接，继续执行
            
            self.connected = True
            self.stats['connection_status'] = 'connected'
            self.stats['connection_time'] = time.time()
            
            return True
            
        except socket.timeout:
            logger.error("连接茶股帮服务器超时")
            return False
        except socket.error as e:
            logger.error(f"连接茶股帮服务器失败: {e}")
            return False
        except Exception as e:
            logger.error(f"连接茶股帮服务器异常: {e}")
            return False
    
    def _disconnect(self):
        """断开连接"""
        self.connected = False
        self.stats['connection_status'] = 'disconnected'
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        logger.info("已断开茶股帮服务器连接")

    def _on_data_received(self, stock_data: Dict[str, Any]):
        """数据接收处理"""
        if not stock_data:
            return

        code = stock_data['stock_code']

        # 更新最新数据
        with self.lock:
            self.latest_data[code] = stock_data

        # 更新统计
        self.stats['received_count'] += 1
        self.stats['last_receive_time'] = time.time()

        # 调用回调函数
        with self.lock:
            for callback in self.data_callbacks:
                try:
                    callback(stock_data)
                except Exception as e:
                    logger.error(f"回调函数执行失败: {e}")

        # 简化的日志输出
        if self.stats['received_count'] % 100 == 0:  # 每100条数据输出一次
            logger.info(f"已接收 {self.stats['received_count']} 条数据，最新: {code} {stock_data['last_price']:.2f}")

    def start_receiving(self):
        """开始接收数据"""
        self.running = True
        retry_count = 0
        max_retries = 5

        logger.info("开始接收茶股帮股票数据...")

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
                while self.running and self.connected:
                    message = self.receive_message(self.socket)
                    if message is None:
                        logger.warning("连接断开，准备重连...")
                        break

                    # 解析数据
                    stock_data = self.parse_stock_data(message)
                    if stock_data:
                        self._on_data_received(stock_data)

                        # 放入队列供其他模块使用
                        try:
                            self.data_queue.put_nowait({
                                'data': stock_data,
                                'timestamp': time.time()
                            })
                        except queue.Full:
                            logger.warning("数据队列已满，丢弃数据")
                            self.stats['error_count'] += 1
                    else:
                        self.stats['error_count'] += 1

            except KeyboardInterrupt:
                logger.info("收到中断信号，停止接收")
                break
            except Exception as e:
                logger.error(f"接收数据异常: {e}")
                self.stats['error_count'] += 1
                time.sleep(5)  # 异常后等待5秒
            finally:
                self._disconnect()

        self.running = False
        logger.info("茶股帮数据接收已停止")

    def stop_receiving(self):
        """停止接收数据"""
        logger.info("正在停止茶股帮数据接收...")
        self.running = False
        self._disconnect()

    def get_latest_data(self, stock_code: str = None) -> Dict:
        """获取最新数据"""
        with self.lock:
            if stock_code:
                return self.latest_data.get(stock_code, {})
            return self.latest_data.copy()

    def get_data_from_queue(self, timeout: float = 1.0) -> Optional[Dict]:
        """从队列获取数据"""
        try:
            return self.data_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()
        stats['queue_size'] = self.data_queue.qsize()
        stats['latest_data_count'] = len(self.latest_data)
        return stats

    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.connected and self.stats['connection_status'] == 'connected'


# 全局实例
_chagubang_receiver: Optional[ChaguBangReceiver] = None

def create_chagubang_receiver(host: str = 'l1.chagubang.com',
                             port: int = 6380,
                             token: str = '') -> ChaguBangReceiver:
    """创建茶股帮接收器实例"""
    global _chagubang_receiver

    _chagubang_receiver = ChaguBangReceiver(host=host, port=port, token=token)
    return _chagubang_receiver

def get_chagubang_receiver() -> Optional[ChaguBangReceiver]:
    """获取全局茶股帮接收器实例"""
    return _chagubang_receiver

def start_chagubang_service(host: str = 'l1.chagubang.com',
                           port: int = 6380,
                           token: str = '') -> threading.Thread:
    """启动茶股帮数据服务"""
    receiver = create_chagubang_receiver(host, port, token)

    thread = threading.Thread(target=receiver.start_receiving, daemon=True)
    thread.start()

    logger.info(f"茶股帮数据服务已启动: {host}:{port}")
    return thread

def get_stock_data(stock_code: str = None) -> Dict:
    """获取股票数据"""
    if _chagubang_receiver:
        return _chagubang_receiver.get_latest_data(stock_code)
    return {}

def get_service_stats() -> Dict[str, Any]:
    """获取服务统计"""
    if _chagubang_receiver:
        return _chagubang_receiver.get_stats()
    return {'status': 'not_initialized'}


if __name__ == "__main__":
    """测试茶股帮数据接收器"""
    import sys

    # 从命令行参数获取token
    token = sys.argv[1] if len(sys.argv) > 1 else ''

    print("🚀 茶股帮股票数据接收器测试")
    print(f"服务器: l1.chagubang.com:6380")
    print(f"Token: {token if token else '空token'}")
    print("-" * 50)

    # 创建接收器
    receiver = ChaguBangReceiver(token=token)

    # 添加数据回调
    def on_stock_data(data):
        print(f"📊 {data['stock_code']} {data.get('stock_name', '')} "
              f"价格: {data['last_price']:.2f} "
              f"涨跌: {data['change_pct']:+.2f}% "
              f"市场: {data['market']}")

    receiver.add_data_callback(on_stock_data)

    try:
        # 开始接收数据
        receiver.start_receiving()
    except KeyboardInterrupt:
        print("\n⏹️ 停止接收数据")
        receiver.stop_receiving()

    print("✅ 测试完成")
