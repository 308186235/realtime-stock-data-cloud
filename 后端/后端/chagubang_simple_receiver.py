"""
茶股帮简化数据接收器
基于MCP分析和现有代码优化的简化版本
协议:直接发送token字符串 + 长度前缀数据接收
"""

import socket
import struct
import json
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChaguBangSimpleReceiver:
    """茶股帮简化接收器 - 基于MCP分析优化"""
    
    def __init__(self, host: str = 'l1.chagubang.com', port: int = 6380, token: str = ''):
        self.host = host
        self.port = port
        self.token = token
        
        # 连接状态
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.connected = False
        
        # 数据存储
        self.latest_data: Dict[str, Dict] = {}
        self.data_callbacks: List[Callable] = []
        
        # 统计信息
        self.stats = {
            'received_count': 0,
            'parsed_count': 0,
            'error_count': 0,
            'connection_time': None,
            'last_receive_time': None,
            'connection_status': 'disconnected'
        }
    
    def add_data_callback(self, callback: Callable[[Dict], None]):
        """添加数据回调函数"""
        self.data_callbacks.append(callback)
    
    def receive_message(self, sock: socket.socket) -> Optional[bytes]:
        """
        接收完整消息 - 茶股帮协议
        协议:[4字节长度][消息内容]
        """
        try:
            # 读取消息长度(前4个字节,小端字节序)
            raw_msglen = self._recvall(sock, 4)
            if not raw_msglen:
                return None
            
            msglen = struct.unpack('<I', raw_msglen)[0]
            
            # 防止异常大的消息长度
            if msglen > 10 * 1024 * 1024:  # 10MB限制
                logger.error(f"消息长度异常: {msglen} bytes")
                return None
            
            if msglen == 0:
                logger.debug("收到空消息")
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
                    return None
                data.extend(packet)
            except socket.timeout:
                logger.warning("接收数据超时")
                return None
            except socket.error as e:
                logger.error(f"Socket错误: {e}")
                return None
        return bytes(data)
    
    def parse_stock_data(self, raw_data: bytes) -> Optional[Dict[str, Any]]:
        """解析股票数据 - 基于现有解析逻辑"""
        try:
            if not raw_data:
                return None
            
            # 解码为UTF-8
            try:
                decoded_message = raw_data.decode('utf-8')
            except UnicodeDecodeError:
                logger.debug("数据不是UTF-8格式,跳过解析")
                return None
            
            # 判断数据格式
            if decoded_message.strip().startswith('{'):
                # JSON格式 - 北交所
                return self._parse_bj_data(decoded_message)
            elif '$' in decoded_message:
                # $分隔格式 - 沪深A股
                return self._parse_sh_sz_data(decoded_message)
            else:
                logger.debug(f"未知数据格式: {decoded_message[:100]}")
                return None
                
        except Exception as e:
            logger.error(f"解析股票数据失败: {e}")
            return None
    
    def _parse_sh_sz_data(self, data_str: str) -> Optional[Dict[str, Any]]:
        """解析沪深A股数据 - 33字段格式"""
        try:
            fields = data_str.strip().split('$')
            if len(fields) < 6:  # 至少需要基本字段
                logger.warning(f"沪深数据字段不足: {len(fields)}")
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
                'stock_name': fields[1] if len(fields) > 1 else '',
                'last_price': safe_float(fields[6]) if len(fields) > 6 else 0.0,
                'open': safe_float(fields[3]) if len(fields) > 3 else 0.0,
                'high': safe_float(fields[4]) if len(fields) > 4 else 0.0,
                'low': safe_float(fields[5]) if len(fields) > 5 else 0.0,
                'volume': safe_int(fields[7]) if len(fields) > 7 else 0,
                'amount': safe_float(fields[8]) if len(fields) > 8 else 0.0,
                'last_close': safe_float(fields[30]) if len(fields) > 30 else 0.0,
                'change_pct': 0.0,
                'market': 'SH/SZ',
                'data_source': 'chagubang',
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'raw_fields': fields
            }
            
            # 计算涨跌幅
            if stock_data['last_close'] > 0:
                stock_data['change_pct'] = (
                    (stock_data['last_price'] - stock_data['last_close']) / 
                    stock_data['last_close'] * 100
                )
            
            return stock_data
            
        except Exception as e:
            logger.error(f"解析沪深数据失败: {e}")
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
                'raw_data': data
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
        except Exception as e:
            logger.error(f"解析北交所数据异常: {e}")
            return None
    
    def _connect_to_server(self) -> bool:
        """连接到茶股帮服务器 - 简化版本"""
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
            logger.info(f"成功连接到茶股帮服务器")
            
            # 直接发送token字符串(关键!)
            token_bytes = self.token.encode('utf-8')
            self.socket.sendall(token_bytes)
            logger.info(f"发送token: {self.token if self.token else '空token'}")
            
            # 等待服务器响应
            time.sleep(1)
            
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
    
    def _on_data_received(self, stock_data: Dict[str, Any]):
        """数据接收处理"""
        if not stock_data:
            return
        
        code = stock_data['stock_code']
        
        # 更新最新数据
        self.latest_data[code] = stock_data
        
        # 更新统计
        self.stats['parsed_count'] += 1
        self.stats['last_receive_time'] = time.time()
        
        # 调用回调函数
        for callback in self.data_callbacks:
            try:
                callback(stock_data)
            except Exception as e:
                logger.error(f"回调函数执行失败: {e}")
    
    def start_receiving(self):
        """开始接收数据 - 简化版本"""
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
                        logger.error("达到最大重试次数,停止接收")
                        break
                    
                    wait_time = min(2 ** retry_count, 60)
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                
                retry_count = 0
                
                # 接收数据循环
                while self.running and self.connected:
                    message = self.receive_message(self.socket)
                    if message is None:
                        logger.warning("连接断开,准备重连...")
                        break
                    
                    # 更新接收统计
                    self.stats['received_count'] += 1
                    
                    # 解析数据
                    stock_data = self.parse_stock_data(message)
                    if stock_data:
                        self._on_data_received(stock_data)
                    else:
                        self.stats['error_count'] += 1
                
            except KeyboardInterrupt:
                logger.info("收到中断信号,停止接收")
                break
            except Exception as e:
                logger.error(f"接收数据异常: {e}")
                self.stats['error_count'] += 1
                time.sleep(5)
            finally:
                self._disconnect()
        
        self.running = False
        logger.info("茶股帮数据接收已停止")
    
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
    
    def stop_receiving(self):
        """停止接收数据"""
        logger.info("正在停止茶股帮数据接收...")
        self.running = False
        self._disconnect()
    
    def get_latest_data(self, stock_code: str = None) -> Dict:
        """获取最新数据"""
        if stock_code:
            return self.latest_data.get(stock_code, {})
        return self.latest_data.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.connected and self.stats['connection_status'] == 'connected'


# 简化的使用接口
def create_simple_receiver(token: str = '') -> ChaguBangSimpleReceiver:
    """创建简化接收器"""
    return ChaguBangSimpleReceiver(token=token)

def test_simple_connection(token: str = ''):
    """测试简化连接"""
    print("🔍 茶股帮简化连接测试")
    print("-" * 40)
    
    receiver = create_simple_receiver(token)
    
    # 数据计数器
    data_count = 0
    
    def on_data(stock_data):
        nonlocal data_count
        data_count += 1
        print(f"📊 接收数据 #{data_count}: {stock_data['stock_code']} "
              f"{stock_data.get('stock_name', '')} "
              f"价格: {stock_data['last_price']:.2f} "
              f"涨跌: {stock_data['change_pct']:+.2f}%")
    
    receiver.add_data_callback(on_data)
    
    # 启动接收线程
    thread = threading.Thread(target=receiver.start_receiving, daemon=True)
    thread.start()
    
    try:
        # 运行30秒
        print("⏱️ 运行30秒测试...")
        time.sleep(30)
        
        # 获取统计
        stats = receiver.get_stats()
        print(f"\n📈 测试结果:")
        print(f"   连接状态: {stats['connection_status']}")
        print(f"   接收消息: {stats['received_count']} 条")
        print(f"   解析成功: {stats['parsed_count']} 条")
        print(f"   错误次数: {stats['error_count']} 次")
        print(f"   股票数量: {len(receiver.latest_data)} 只")
        
        if stats['parsed_count'] > 0:
            print("✅ 简化连接测试成功!")
            return True
        else:
            print("❌ 未接收到有效数据")
            return False
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断测试")
        return False
    finally:
        receiver.stop_receiving()


if __name__ == "__main__":
    """测试简化接收器"""
    import sys
    
    # 从命令行参数获取token
    token = sys.argv[1] if len(sys.argv) > 1 else ''
    
    print("🚀 茶股帮简化数据接收器")
    print("基于MCP分析优化的版本")
    print(f"Token: {token if token else '空token'}")
    print("=" * 50)
    
    success = test_simple_connection(token)
    
    if success:
        print("\n🎉 测试成功!可以开始使用")
    else:
        print("\n💡 使用建议:")
        print("1. 获取有效的茶股帮Token")
        print("2. 运行: python chagubang_simple_receiver.py <token>")
        print("3. 确保在交易时间内测试")
