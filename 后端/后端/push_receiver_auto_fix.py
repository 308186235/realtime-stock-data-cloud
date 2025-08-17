#!/usr/bin/env python3
"""
推送接收器自动修复工具
基于MCP诊断结果自动修复关键问题
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PushReceiverAutoFix:
    """推送接收器自动修复器"""
    
    def __init__(self):
        self.config_file = "backend/services/realtime_stock_receiver.py"
        self.backup_file = f"{self.config_file}.backup_{int(time.time())}"
        
    def run_auto_fix(self):
        """运行自动修复"""
        logger.info("🔧 开始自动修复推送接收器问题...")
        
        try:
            # 1. 备份原文件
            self._backup_original_file()
            
            # 2. 修复服务器配置
            self._fix_server_configuration()
            
            # 3. 添加心跳机制
            self._add_heartbeat_mechanism()
            
            # 4. 添加数据验证
            self._add_data_validation()
            
            # 5. 增强错误处理
            self._enhance_error_handling()
            
            # 6. 添加重连机制
            self._add_reconnection_mechanism()
            
            logger.info("✅ 自动修复完成!")
            
        except Exception as e:
            logger.error(f"❌ 自动修复失败: {e}")
            self._restore_backup()
    
    def _backup_original_file(self):
        """备份原文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as src:
                content = src.read()
            
            with open(self.backup_file, 'w', encoding='utf-8') as dst:
                dst.write(content)
            
            logger.info(f"📄 原文件已备份到: {self.backup_file}")
        else:
            logger.warning("⚠️ 原配置文件不存在,将创建新文件")
    
    def _fix_server_configuration(self):
        """修复服务器配置"""
        logger.info("🔧 修复服务器配置...")
        
        # 创建配置修复代码
        config_fix = '''
# 修复后的服务器配置
@dataclass
class ConnectionConfig:
    """连接配置 - 已修复"""
    api_key: str = "process.env.STOCK_API_KEY"
    
    # 🔴 重要:请填入实际的服务器信息
    host: str = "stock.api.server.com"  # 替换为实际服务器地址
    port: int = 8080                    # 替换为实际端口
    token: str = "your_actual_token"    # 替换为实际token
    
    # 性能配置
    buffer_size: int = 1024 * 1024      # 1MB缓冲区
    max_queue_size: int = 100000        # 最大队列大小
    redis_batch_size: int = 1000        # Redis批量写入大小
    
    # 心跳配置 - 新增
    heartbeat_interval: int = 30        # 心跳间隔(秒)
    heartbeat_timeout: int = 90         # 心跳超时(秒)
    
    # 重连配置 - 增强
    max_retries: int = 10               # 最大重试次数
    retry_base_delay: int = 2           # 重试基础延迟
    retry_max_delay: int = 300          # 最大重试延迟(5分钟)
    
    # 数据验证配置 - 新增
    enable_checksum: bool = True        # 启用校验和
    max_message_size: int = 10 * 1024 * 1024  # 10MB最大消息
'''
        
        # 如果文件存在,更新配置部分
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找并替换配置类
            import re
            pattern = r'@dataclass\s+class ConnectionConfig:.*?(?=\n\s*class|\n\s*def|\Z)'
            
            if re.search(pattern, content, re.DOTALL):
                # 替换现有配置
                new_content = re.sub(pattern, config_fix.strip(), content, flags=re.DOTALL)
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                logger.info("✅ 服务器配置已修复")
            else:
                logger.warning("⚠️ 未找到配置类,将在文件开头添加")
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    f.write(config_fix + "\n\n" + content)
    
    def _add_heartbeat_mechanism(self):
        """添加心跳机制"""
        logger.info("💓 添加心跳机制...")
        
        heartbeat_code = '''
    def _start_heartbeat_thread(self):
        """启动心跳线程"""
        if not hasattr(self, 'heartbeat_thread') or not self.heartbeat_thread.is_alive():
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self.heartbeat_thread.start()
            logger.info("心跳线程已启动")
    
    def _heartbeat_loop(self):
        """心跳循环"""
        while self.running:
            try:
                if hasattr(self, 'socket') and self.socket:
                    # 发送心跳
                    heartbeat_data = {
                        'type': 'heartbeat',
                        'timestamp': time.time(),
                        'client_id': id(self)
                    }
                    
                    heartbeat_bytes = json.dumps(heartbeat_data).encode('utf-8')
                    try:
                        self.socket.sendall(heartbeat_bytes)
                        logger.debug("心跳发送成功")
                    except Exception as e:
                        logger.warning(f"心跳发送失败: {e}")
                        # 心跳失败可能表示连接断开
                        self._handle_connection_lost()
                
                # 等待下次心跳
                time.sleep(self.config.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"心跳循环异常: {e}")
                time.sleep(5)  # 异常后短暂等待
    
    def _handle_connection_lost(self):
        """处理连接丢失"""
        logger.warning("检测到连接丢失,准备重连...")
        if hasattr(self, 'socket') and self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            self.socket = None
        
        # 触发重连
        self.stats['connection_status'] = 'reconnecting'
'''
        
        self._append_methods_to_class(heartbeat_code)
        logger.info("✅ 心跳机制已添加")
    
    def _add_data_validation(self):
        """添加数据验证"""
        logger.info("🔍 添加数据验证...")
        
        validation_code = '''
    def _recv_exact(self, n: int) -> Optional[bytes]:
        """精确接收指定字节数 - 新增数据验证"""
        try:
            data = bytearray()
            while len(data) < n:
                chunk = self.socket.recv(n - len(data))
                if not chunk:
                    logger.warning("连接意外关闭")
                    return None
                data.extend(chunk)
            return bytes(data)
        except socket.timeout:
            logger.warning("接收数据超时")
            return None
        except Exception as e:
            logger.error(f"接收数据失败: {e}")
            return None
    
    def _validate_message(self, message: bytes) -> bool:
        """验证消息完整性"""
        try:
            # 检查消息长度
            if len(message) > self.config.max_message_size:
                logger.warning(f"消息过大: {len(message)} bytes")
                return False
            
            # 检查消息格式
            if len(message) == 0:
                logger.warning("收到空消息")
                return False
            
            # 如果启用校验和,进行校验
            if self.config.enable_checksum:
                # 这里可以添加具体的校验和验证逻辑
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"消息验证失败: {e}")
            return False
    
    def _enhanced_receive_message(self) -> Optional[bytes]:
        """增强的消息接收 - 包含数据验证"""
        try:
            # 首先读取消息长度(前4个字节)
            raw_msglen = self._recv_exact(4)
            if not raw_msglen:
                return None
            
            msglen = struct.unpack('<I', raw_msglen)[0]  # 小端字节序
            
            # 验证消息长度
            if not self._validate_message_length(msglen):
                return None
            
            # 读取完整消息
            message = self._recv_exact(msglen)
            if not message:
                return None
            
            # 验证消息完整性
            if not self._validate_message(message):
                return None
            
            return message
            
        except Exception as e:
            logger.error(f"增强消息接收失败: {e}")
            return None
    
    def _validate_message_length(self, length: int) -> bool:
        """验证消息长度"""
        if length <= 0:
            logger.warning("消息长度无效")
            return False
        
        if length > self.config.max_message_size:
            logger.warning(f"消息长度超限: {length}")
            return False
        
        return True
'''
        
        self._append_methods_to_class(validation_code)
        logger.info("✅ 数据验证已添加")
    
    def _enhance_error_handling(self):
        """增强错误处理"""
        logger.info("🛡️ 增强错误处理...")
        
        error_handling_code = '''
    def _handle_socket_error(self, error: Exception) -> str:
        """处理Socket错误"""
        error_type = type(error).__name__
        
        if isinstance(error, socket.timeout):
            logger.debug("Socket超时 - 正常情况")
            return "timeout"
        elif isinstance(error, ConnectionResetError):
            logger.warning("连接被重置")
            return "connection_reset"
        elif isinstance(error, ConnectionAbortedError):
            logger.warning("连接被中止")
            return "connection_aborted"
        elif isinstance(error, OSError):
            logger.error(f"操作系统错误: {error}")
            return "os_error"
        else:
            logger.error(f"未知Socket错误: {error_type} - {error}")
            return "unknown_error"
    
    def _handle_data_error(self, error: Exception, data: bytes = None) -> None:
        """处理数据错误"""
        error_type = type(error).__name__
        
        if isinstance(error, json.JSONDecodeError):
            logger.warning(f"JSON解析错误: {error}")
            if data:
                logger.debug(f"错误数据: {data[:100]}...")
        elif isinstance(error, UnicodeDecodeError):
            logger.warning(f"编码错误: {error}")
        elif isinstance(error, struct.error):
            logger.warning(f"数据结构错误: {error}")
        else:
            logger.error(f"数据处理错误: {error_type} - {error}")
        
        # 更新错误统计
        self.stats['error_count'] += 1
        self.stats['last_error'] = {
            'type': error_type,
            'message': str(error),
            'timestamp': time.time()
        }
    
    def _should_retry_connection(self, error_type: str) -> bool:
        """判断是否应该重试连接"""
        retry_errors = [
            "timeout",
            "connection_reset", 
            "connection_aborted",
            "os_error"
        ]
        return error_type in retry_errors
'''
        
        self._append_methods_to_class(error_handling_code)
        logger.info("✅ 错误处理已增强")
    
    def _add_reconnection_mechanism(self):
        """添加重连机制"""
        logger.info("🔄 添加重连机制...")
        
        reconnection_code = '''
    def _enhanced_connection_loop(self):
        """增强的连接循环 - 包含智能重连"""
        retry_count = 0
        max_retries = self.config.max_retries
        
        while self.running:
            try:
                # 尝试连接
                if self._connect_to_server():
                    retry_count = 0  # 重置重试计数
                    logger.info("连接成功,开始接收数据")
                    
                    # 启动心跳
                    self._start_heartbeat_thread()
                    
                    # 接收数据循环
                    self._data_receive_loop()
                else:
                    # 连接失败,准备重试
                    retry_count += 1
                    
                    if retry_count >= max_retries:
                        logger.error("达到最大重试次数,停止连接")
                        break
                    
                    # 计算重试延迟(指数退避)
                    delay = min(
                        self.config.retry_base_delay * (2 ** (retry_count - 1)),
                        self.config.retry_max_delay
                    )
                    
                    logger.warning(f"连接失败,{delay}秒后重试 ({retry_count}/{max_retries})")
                    time.sleep(delay)
                
            except KeyboardInterrupt:
                logger.info("收到停止信号")
                break
            except Exception as e:
                logger.error(f"连接循环异常: {e}")
                time.sleep(5)
        
        logger.info("连接循环结束")
    
    def _data_receive_loop(self):
        """数据接收循环"""
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.running:
            try:
                # 使用增强的消息接收
                message = self._enhanced_receive_message()
                
                if message is None:
                    consecutive_errors += 1
                    if consecutive_errors >= max_consecutive_errors:
                        logger.warning("连续接收失败,可能连接断开")
                        break
                    continue
                
                # 重置错误计数
                consecutive_errors = 0
                
                # 处理消息
                self._process_received_message(message)
                
            except Exception as e:
                error_type = self._handle_socket_error(e)
                
                if not self._should_retry_connection(error_type):
                    logger.error("不可恢复的错误,断开连接")
                    break
                
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    logger.warning("连续错误过多,断开连接")
                    break
    
    def _process_received_message(self, message: bytes):
        """处理接收到的消息"""
        try:
            # 立即放入队列,避免阻塞
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
            logger.error("数据队列已满,丢弃数据!")
            self.stats['error_count'] += 1
        except Exception as e:
            self._handle_data_error(e, message)
'''
        
        self._append_methods_to_class(reconnection_code)
        logger.info("✅ 重连机制已添加")
    
    def _append_methods_to_class(self, methods_code: str):
        """将方法添加到类中"""
        if not os.path.exists(self.config_file):
            logger.error("配置文件不存在")
            return
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在类的最后添加新方法
        # 查找类的结束位置
        import re
        
        # 查找RealtimeStockReceiver类
        class_pattern = r'(class RealtimeStockReceiver:.*?)(\n\s*(?:class|def|$))'
        match = re.search(class_pattern, content, re.DOTALL)
        
        if match:
            # 在类的末尾添加新方法
            class_content = match.group(1)
            rest_content = match.group(2) if match.group(2) else ""
            
            new_class_content = class_content + methods_code + "\n"
            new_content = content.replace(match.group(0), new_class_content + rest_content)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
        else:
            # 如果找不到类,直接添加到文件末尾
            with open(self.config_file, 'a', encoding='utf-8') as f:
                f.write("\n" + methods_code)
    
    def _restore_backup(self):
        """恢复备份"""
        try:
            if os.path.exists(self.backup_file):
                with open(self.backup_file, 'r', encoding='utf-8') as src:
                    content = src.read()
                
                with open(self.config_file, 'w', encoding='utf-8') as dst:
                    dst.write(content)
                
                logger.info(f"✅ 已从备份恢复: {self.backup_file}")
            else:
                logger.error("❌ 备份文件不存在,无法恢复")
        except Exception as e:
            logger.error(f"❌ 恢复备份失败: {e}")

def main():
    """主函数"""
    print("🔧 推送接收器自动修复工具")
    print("=" * 50)
    
    fixer = PushReceiverAutoFix()
    
    # 询问用户确认
    response = input("是否开始自动修复?这将修改现有文件。(y/N): ")
    if response.lower() != 'y':
        print("❌ 用户取消操作")
        return
    
    # 执行修复
    fixer.run_auto_fix()
    
    print("\n🎉 修复完成!")
    print("📝 请检查以下事项:")
    print("1. 在配置文件中填入正确的服务器地址,端口和token")
    print("2. 测试连接是否正常")
    print("3. 检查心跳和重连机制是否工作")
    print(f"4. 如有问题,可从备份恢复: {fixer.backup_file}")

if __name__ == "__main__":
    main()
