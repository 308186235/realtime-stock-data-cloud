"""
茶股帮Token管理器
用于管理和测试茶股帮API token
"""

import os
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any
from debug_chagubang import ChaguBangDebugger

class TokenManager:
    """Token管理器"""
    
    def __init__(self, config_file: str = 'chagubang_config.json'):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        
        # 默认配置
        return {
            'tokens': [],
            'current_token': '',
            'last_test_time': None,
            'test_results': {}
        }
    
    def _save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def add_token(self, token: str, description: str = '') -> bool:
        """添加token"""
        if not token:
            print("❌ Token不能为空")
            return False
        
        # 检查是否已存在
        for existing in self.config['tokens']:
            if existing['token'] == token:
                print("⚠️ Token已存在")
                return False
        
        # 添加新token
        token_info = {
            'token': token,
            'description': description,
            'added_time': datetime.now().isoformat(),
            'last_test_time': None,
            'test_status': 'untested'
        }
        
        self.config['tokens'].append(token_info)
        self._save_config()
        
        print(f"✅ Token已添加: {token[:10]}...")
        return True
    
    def list_tokens(self):
        """列出所有token"""
        if not self.config['tokens']:
            print("📭 没有保存的token")
            return
        
        print("📋 已保存的Token:")
        print("-" * 60)
        for i, token_info in enumerate(self.config['tokens']):
            token = token_info['token']
            desc = token_info.get('description', '')
            status = token_info.get('test_status', 'untested')
            last_test = token_info.get('last_test_time', '从未测试')
            
            status_emoji = {
                'untested': '❓',
                'valid': '✅',
                'invalid': '❌',
                'error': '⚠️'
            }.get(status, '❓')
            
            print(f"{i+1}. {status_emoji} {token[:15]}...")
            if desc:
                print(f"   描述: {desc}")
            print(f"   状态: {status}")
            print(f"   最后测试: {last_test}")
            print()
    
    def test_token(self, token: str) -> Dict[str, Any]:
        """测试token有效性"""
        print(f"🔍 测试Token: {token[:15]}...")
        
        debugger = ChaguBangDebugger(token=token)
        
        result = {
            'token': token,
            'test_time': datetime.now().isoformat(),
            'status': 'error',
            'message': '',
            'can_connect': False,
            'can_authenticate': False,
            'receives_data': False
        }
        
        try:
            # 创建socket连接
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            # 连接测试
            sock.connect(('l1.chagubang.com', 6380))
            result['can_connect'] = True
            print("✅ 连接成功")
            
            # 发送token
            sock.sendall(token.encode('utf-8'))
            time.sleep(1)
            
            # 尝试接收响应
            try:
                sock.settimeout(5)
                response = sock.recv(1024)
                
                if response:
                    try:
                        decoded = response.decode('utf-8', errors='ignore')
                        print(f"📨 服务器响应: {decoded}")
                        
                        if 'Token' in decoded and '失败' in decoded:
                            result['status'] = 'invalid'
                            result['message'] = 'Token鉴权失败'
                            print("❌ Token无效")
                        elif '成功' in decoded or 'success' in decoded.lower():
                            result['can_authenticate'] = True
                            result['status'] = 'valid'
                            result['message'] = 'Token有效'
                            print("✅ Token有效")
                            
                            # 尝试接收数据
                            print("📥 尝试接收数据...")
                            sock.settimeout(10)
                            
                            try:
                                # 尝试接收数据消息
                                raw_msglen = sock.recv(4)
                                if raw_msglen:
                                    import struct
                                    msglen = struct.unpack('<I', raw_msglen)[0]
                                    if 0 < msglen < 1024 * 1024:
                                        message = sock.recv(msglen)
                                        if message:
                                            result['receives_data'] = True
                                            print("✅ 可以接收数据")
                                        else:
                                            print("⚠️ 无法接收数据内容")
                                    else:
                                        print(f"⚠️ 异常消息长度: {msglen}")
                                else:
                                    print("⚠️ 认证成功但无数据推送")
                            except socket.timeout:
                                print("⏰ 接收数据超时")
                        else:
                            result['status'] = 'unknown'
                            result['message'] = f'未知响应: {decoded}'
                            print(f"❓ 未知响应: {decoded}")
                    except UnicodeDecodeError:
                        result['message'] = f'二进制响应: {response.hex()}'
                        print(f"📨 二进制响应: {response.hex()}")
                else:
                    result['message'] = '无服务器响应'
                    print("❌ 无服务器响应")
                    
            except socket.timeout:
                result['message'] = '服务器响应超时'
                print("⏰ 服务器响应超时")
            
            sock.close()
            
        except socket.error as e:
            result['message'] = f'连接错误: {e}'
            print(f"❌ 连接错误: {e}")
        except Exception as e:
            result['message'] = f'测试异常: {e}'
            print(f"❌ 测试异常: {e}")
        
        # 更新配置中的测试结果
        self._update_token_test_result(token, result)
        
        return result
    
    def _update_token_test_result(self, token: str, result: Dict[str, Any]):
        """更新token测试结果"""
        for token_info in self.config['tokens']:
            if token_info['token'] == token:
                token_info['last_test_time'] = result['test_time']
                token_info['test_status'] = result['status']
                break
        
        self.config['test_results'][token] = result
        self._save_config()
    
    def get_best_token(self) -> Optional[str]:
        """获取最佳可用token"""
        valid_tokens = []
        
        for token_info in self.config['tokens']:
            if token_info.get('test_status') == 'valid':
                valid_tokens.append(token_info)
        
        if valid_tokens:
            # 返回最近测试成功的token
            best_token = max(valid_tokens, key=lambda x: x.get('last_test_time', ''))
            return best_token['token']
        
        return None
    
    def interactive_setup(self):
        """交互式设置"""
        print("🔧 茶股帮Token管理器")
        print("=" * 40)
        
        while True:
            print("\n选择操作:")
            print("1. 添加Token")
            print("2. 列出Token")
            print("3. 测试Token")
            print("4. 测试所有Token")
            print("5. 获取最佳Token")
            print("0. 退出")
            
            choice = input("\n请选择 (0-5): ").strip()
            
            if choice == '1':
                token = input("请输入Token: ").strip()
                desc = input("请输入描述 (可选): ").strip()
                self.add_token(token, desc)
                
            elif choice == '2':
                self.list_tokens()
                
            elif choice == '3':
                self.list_tokens()
                try:
                    index = int(input("请选择要测试的Token编号: ")) - 1
                    if 0 <= index < len(self.config['tokens']):
                        token = self.config['tokens'][index]['token']
                        self.test_token(token)
                    else:
                        print("❌ 无效的编号")
                except ValueError:
                    print("❌ 请输入有效数字")
                    
            elif choice == '4':
                print("🔍 测试所有Token...")
                for token_info in self.config['tokens']:
                    self.test_token(token_info['token'])
                    print("-" * 40)
                    
            elif choice == '5':
                best_token = self.get_best_token()
                if best_token:
                    print(f"🏆 最佳Token: {best_token[:15]}...")
                else:
                    print("❌ 没有可用的Token")
                    
            elif choice == '0':
                print("👋 再见!")
                break
                
            else:
                print("❌ 无效选择")


def main():
    """主函数"""
    import sys
    
    manager = TokenManager()
    
    if len(sys.argv) > 1:
        # 命令行模式
        command = sys.argv[1]
        
        if command == 'add' and len(sys.argv) > 2:
            token = sys.argv[2]
            desc = sys.argv[3] if len(sys.argv) > 3 else ''
            manager.add_token(token, desc)
            
        elif command == 'test' and len(sys.argv) > 2:
            token = sys.argv[2]
            manager.test_token(token)
            
        elif command == 'list':
            manager.list_tokens()
            
        elif command == 'best':
            best_token = manager.get_best_token()
            if best_token:
                print(best_token)
            else:
                print("NO_VALID_TOKEN")
                
        else:
            print("用法:")
            print("  python chagubang_token_manager.py add <token> [description]")
            print("  python chagubang_token_manager.py test <token>")
            print("  python chagubang_token_manager.py list")
            print("  python chagubang_token_manager.py best")
    else:
        # 交互模式
        manager.interactive_setup()


if __name__ == "__main__":
    main()
