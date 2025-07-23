#!/usr/bin/env python3
"""
连接阿里云服务器的本地脚本
"""

import socket
import json
import sys

class AliyunConnector:
    def __init__(self, host='47.236.101.147', port=9999):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self):
        """连接到阿里云服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"✅ 已连接到阿里云服务器 {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def send_command(self, command, args=None):
        """发送命令到服务器"""
        if not self.socket:
            print("❌ 未连接到服务器")
            return None
        
        try:
            command_data = {
                'command': command,
                'args': args or []
            }
            
            message = json.dumps(command_data)
            self.socket.send(message.encode('utf-8'))
            
            # 接收响应
            response = self.socket.recv(8192).decode('utf-8')
            return json.loads(response)
            
        except Exception as e:
            print(f"❌ 发送命令失败: {e}")
            return None
    
    def shell(self, command):
        """执行shell命令"""
        return self.send_command('shell', [command])
    
    def system_info(self):
        """获取系统信息"""
        return self.send_command('system_info')
    
    def list_dir(self, path='.'):
        """列出目录"""
        return self.send_command('list_dir', [path])
    
    def read_file(self, filepath):
        """读取文件"""
        return self.send_command('read_file', [filepath])
    
    def write_file(self, filepath, content):
        """写入文件"""
        return self.send_command('write_file', [filepath, content])
    
    def close(self):
        """关闭连接"""
        if self.socket:
            self.socket.close()
            print("🔌 连接已关闭")

def main():
    connector = AliyunConnector()
    
    if not connector.connect():
        return
    
    try:
        # 获取系统信息
        print("\n📊 系统信息:")
        result = connector.system_info()
        if result and result.get('success'):
            print(result['result'])
        
        # 交互式命令行
        print("\n💻 交互式命令行 (输入 'exit' 退出):")
        while True:
            try:
                cmd = input("aliyun> ").strip()
                if cmd.lower() in ['exit', 'quit']:
                    break
                
                if cmd:
                    result = connector.shell(cmd)
                    if result and result.get('success'):
                        print(result['result'])
                    else:
                        print(f"❌ 命令执行失败: {result.get('error', '未知错误')}")
                        
            except KeyboardInterrupt:
                break
                
    finally:
        connector.close()

if __name__ == '__main__':
    main()
