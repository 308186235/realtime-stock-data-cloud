"""
茶股帮连接调试脚本
用于详细分析服务器响应和数据格式
"""

import socket
import struct
import time
import threading
from datetime import datetime

class ChaguBangDebugger:
    """茶股帮调试器"""
    
    def __init__(self, host='l1.chagubang.com', port=6380, token=''):
        self.host = host
        self.port = port
        self.token = token
        self.socket = None
        self.running = False
        
    def connect_and_debug(self):
        """连接并调试"""
        try:
            print(f"🔍 开始调试茶股帮连接")
            print(f"服务器: {self.host}:{self.port}")
            print(f"Token: {self.token if self.token else '空token'}")
            print("-" * 50)
            
            # 创建socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 10秒超时
            
            # 连接
            print("📡 正在连接服务器...")
            self.socket.connect((self.host, self.port))
            print("✅ 连接成功!")
            
            # 发送token
            print("🔐 发送认证信息...")
            if self.token:
                self.socket.sendall(self.token.encode('utf-8'))
                print(f"   发送token: {self.token}")
            else:
                self.socket.sendall(b'')
                print("   发送空token")
            
            # 等待响应
            print("⏱️ 等待服务器响应...")
            time.sleep(2)
            
            # 尝试接收数据
            print("📥 开始接收数据...")
            self.running = True
            message_count = 0
            
            while self.running and message_count < 10:  # 最多接收10条消息
                try:
                    # 设置较短的超时
                    self.socket.settimeout(5)
                    
                    # 尝试读取消息长度
                    raw_msglen = self._recvall(4)
                    if not raw_msglen:
                        print("❌ 无法读取消息长度")
                        break
                    
                    msglen = struct.unpack('<I', raw_msglen)[0]
                    print(f"📏 消息长度: {msglen} bytes")
                    
                    if msglen > 1024 * 1024:  # 1MB限制
                        print(f"⚠️ 消息长度异常: {msglen}")
                        break
                    
                    if msglen == 0:
                        print("📭 收到空消息")
                        continue
                    
                    # 读取消息内容
                    message = self._recvall(msglen)
                    if not message:
                        print("❌ 无法读取消息内容")
                        break
                    
                    message_count += 1
                    print(f"\n📨 消息 #{message_count}:")
                    print(f"   长度: {len(message)} bytes")
                    
                    # 尝试解码
                    try:
                        decoded = message.decode('utf-8')
                        print(f"   内容: {decoded[:200]}{'...' if len(decoded) > 200 else ''}")
                        
                        # 分析数据格式
                        if decoded.startswith('{'):
                            print("   格式: JSON (北交所)")
                            self._analyze_json_data(decoded)
                        elif '$' in decoded:
                            print("   格式: 分隔符 (沪深)")
                            self._analyze_delimited_data(decoded)
                        else:
                            print("   格式: 未知")
                            
                    except UnicodeDecodeError:
                        print(f"   内容: 二进制数据 (前50字节): {message[:50].hex()}")
                    
                except socket.timeout:
                    print("⏰ 接收超时,可能没有更多数据")
                    break
                except Exception as e:
                    print(f"❌ 接收数据异常: {e}")
                    break
            
            if message_count == 0:
                print("\n🤔 分析: 连接成功但未收到数据")
                print("可能原因:")
                print("1. 需要有效的token")
                print("2. 需要发送特定的订阅消息")
                print("3. 服务器在特定时间才推送数据")
                print("4. 需要特定的协议握手")
                
                # 尝试发送一些常见的订阅消息
                print("\n🔄 尝试发送订阅消息...")
                self._try_subscription_messages()
            else:
                print(f"\n✅ 成功接收到 {message_count} 条消息")
                
        except socket.timeout:
            print("❌ 连接超时")
        except socket.error as e:
            print(f"❌ Socket错误: {e}")
        except Exception as e:
            print(f"❌ 调试异常: {e}")
        finally:
            self._cleanup()
    
    def _recvall(self, n):
        """接收指定长度的数据"""
        data = bytearray()
        while len(data) < n:
            packet = self.socket.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)
    
    def _analyze_json_data(self, json_str):
        """分析JSON数据"""
        try:
            import json
            data = json.loads(json_str)
            print(f"   JSON字段数: {len(data)}")
            print(f"   主要字段: {list(data.keys())[:10]}")
        except:
            print("   JSON解析失败")
    
    def _analyze_delimited_data(self, data_str):
        """分析分隔符数据"""
        fields = data_str.split('$')
        print(f"   字段数: {len(fields)}")
        print(f"   前5个字段: {fields[:5]}")
        if len(fields) >= 33:
            print("   符合33字段格式")
        else:
            print("   不符合33字段格式")
    
    def _try_subscription_messages(self):
        """尝试发送订阅消息"""
        subscription_attempts = [
            b'SUBSCRIBE',
            b'SUBSCRIBE_ALL',
            b'START',
            b'BEGIN',
            b'{"action":"subscribe"}',
            b'{"type":"subscribe","symbols":["000001"]}',
        ]
        
        for i, msg in enumerate(subscription_attempts):
            try:
                print(f"   尝试 #{i+1}: {msg.decode('utf-8', errors='ignore')}")
                self.socket.sendall(msg)
                time.sleep(1)
                
                # 尝试接收响应
                self.socket.settimeout(2)
                try:
                    response = self.socket.recv(1024)
                    if response:
                        try:
                            # 尝试解析响应
                            decoded_response = response.decode('utf-8', errors='ignore')
                            print(f"   响应: {decoded_response}")

                            # 检查是否是错误消息
                            if 'Token' in decoded_response and '失败' in decoded_response:
                                print("   ⚠️ Token鉴权失败!需要有效token")
                            elif 'success' in decoded_response.lower():
                                print("   ✅ 可能认证成功")
                                return True
                        except:
                            print(f"   响应 (hex): {response[:50].hex()}")

                        # 如果有响应,可能触发了数据流
                        return True
                except socket.timeout:
                    print("   无响应")
                    
            except Exception as e:
                print(f"   失败: {e}")
        
        return False
    
    def _cleanup(self):
        """清理资源"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("\n🔧 调试完成")


def main():
    """主调试函数"""
    print("🔍 茶股帮连接调试器")
    print("=" * 50)
    
    # 可以从命令行传入token
    import sys
    token = sys.argv[1] if len(sys.argv) > 1 else ''
    
    debugger = ChaguBangDebugger(token=token)
    
    try:
        debugger.connect_and_debug()
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断调试")
        debugger._cleanup()
    
    print("\n💡 调试建议:")
    print("1. 如果连接成功但无数据,可能需要有效token")
    print("2. 检查是否在交易时间内")
    print("3. 联系数据提供商确认协议细节")
    print("4. 尝试使用不同的订阅消息格式")


if __name__ == "__main__":
    main()
