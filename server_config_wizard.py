#!/usr/bin/env python3
"""
服务器配置向导
帮助用户正确配置股票推送服务器信息
"""

import os
import json
import socket
import time
import logging
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServerConfigWizard:
    """服务器配置向导"""
    
    def __init__(self):
        self.config_file = "backend/services/realtime_stock_receiver.py"
        self.config_data = {}
        
    def run_wizard(self):
        """运行配置向导"""
        print("🧙‍♂️ 股票推送服务器配置向导")
        print("=" * 50)
        print("此向导将帮助您配置股票数据推送服务器连接信息")
        print()
        
        try:
            # 1. 收集配置信息
            self._collect_server_info()
            
            # 2. 测试连接
            if self._test_connection():
                print("✅ 连接测试成功！")
            else:
                print("⚠️ 连接测试失败，但配置仍会保存")
            
            # 3. 保存配置
            self._save_configuration()
            
            # 4. 生成配置报告
            self._generate_config_report()
            
            print("\n🎉 配置完成！")
            
        except KeyboardInterrupt:
            print("\n❌ 用户取消配置")
        except Exception as e:
            print(f"\n❌ 配置过程出错: {e}")
    
    def _collect_server_info(self):
        """收集服务器信息"""
        print("📝 请输入服务器连接信息：")
        print()
        
        # API密钥
        api_key = input("API密钥 [QT_wat5QfcJ6N9pDZM5]: ").strip()
        if not api_key:
            api_key = "QT_wat5QfcJ6N9pDZM5"
        self.config_data['api_key'] = api_key
        
        # 服务器地址
        while True:
            host = input("服务器地址 (如: stock.api.com): ").strip()
            if host:
                self.config_data['host'] = host
                break
            print("❌ 服务器地址不能为空")
        
        # 服务器端口
        while True:
            try:
                port_str = input("服务器端口 [8080]: ").strip()
                if not port_str:
                    port = 8080
                else:
                    port = int(port_str)
                
                if 1 <= port <= 65535:
                    self.config_data['port'] = port
                    break
                else:
                    print("❌ 端口号必须在1-65535之间")
            except ValueError:
                print("❌ 请输入有效的端口号")
        
        # 认证Token
        while True:
            token = input("认证Token: ").strip()
            if token:
                self.config_data['token'] = token
                break
            print("❌ 认证Token不能为空")
        
        # 高级配置
        print("\n⚙️ 高级配置 (可选，直接回车使用默认值):")
        
        # 缓冲区大小
        buffer_size_str = input("缓冲区大小 (KB) [1024]: ").strip()
        try:
            buffer_size = int(buffer_size_str) * 1024 if buffer_size_str else 1024 * 1024
            self.config_data['buffer_size'] = buffer_size
        except ValueError:
            self.config_data['buffer_size'] = 1024 * 1024
        
        # 心跳间隔
        heartbeat_str = input("心跳间隔 (秒) [30]: ").strip()
        try:
            heartbeat = int(heartbeat_str) if heartbeat_str else 30
            self.config_data['heartbeat_interval'] = heartbeat
        except ValueError:
            self.config_data['heartbeat_interval'] = 30
        
        # 最大重试次数
        retry_str = input("最大重试次数 [10]: ").strip()
        try:
            retries = int(retry_str) if retry_str else 10
            self.config_data['max_retries'] = retries
        except ValueError:
            self.config_data['max_retries'] = 10
        
        print("\n✅ 配置信息收集完成")
    
    def _test_connection(self) -> bool:
        """测试连接"""
        print(f"\n🔍 测试连接到 {self.config_data['host']}:{self.config_data['port']}...")
        
        try:
            # 创建socket连接测试
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # 10秒超时
            
            result = sock.connect_ex((self.config_data['host'], self.config_data['port']))
            sock.close()
            
            if result == 0:
                print("✅ 基础网络连接成功")
                return True
            else:
                print(f"❌ 连接失败，错误代码: {result}")
                return False
                
        except socket.gaierror as e:
            print(f"❌ DNS解析失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 连接测试失败: {e}")
            return False
    
    def _save_configuration(self):
        """保存配置"""
        print("\n💾 保存配置...")
        
        try:
            # 生成配置代码
            config_code = self._generate_config_code()
            
            # 读取现有文件
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 备份原文件
                backup_file = f"{self.config_file}.backup_{int(time.time())}"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"📄 原文件已备份到: {backup_file}")
                
                # 替换配置部分
                import re
                pattern = r'@dataclass\s+class ConnectionConfig:.*?(?=\n\s*class|\n\s*def|\Z)'
                
                if re.search(pattern, content, re.DOTALL):
                    new_content = re.sub(pattern, config_code.strip(), content, flags=re.DOTALL)
                else:
                    # 如果找不到配置类，在文件开头添加
                    new_content = config_code + "\n\n" + content
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            else:
                # 创建新文件
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    f.write(config_code)
            
            print("✅ 配置已保存")
            
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
    
    def _generate_config_code(self) -> str:
        """生成配置代码"""
        return f'''@dataclass
class ConnectionConfig:
    """连接配置 - 由配置向导生成"""
    # 基础配置
    api_key: str = "{self.config_data['api_key']}"
    host: str = "{self.config_data['host']}"
    port: int = {self.config_data['port']}
    token: str = "{self.config_data['token']}"
    
    # 性能配置
    buffer_size: int = {self.config_data['buffer_size']}  # {self.config_data['buffer_size']//1024}KB缓冲区
    max_queue_size: int = 100000        # 最大队列大小
    redis_batch_size: int = 1000        # Redis批量写入大小
    
    # 心跳配置
    heartbeat_interval: int = {self.config_data['heartbeat_interval']}  # 心跳间隔(秒)
    heartbeat_timeout: int = {self.config_data['heartbeat_interval'] * 3}   # 心跳超时(秒)
    
    # 重连配置
    max_retries: int = {self.config_data['max_retries']}         # 最大重试次数
    retry_base_delay: int = 2           # 重试基础延迟
    retry_max_delay: int = 300          # 最大重试延迟(5分钟)
    
    # 数据验证配置
    enable_checksum: bool = True        # 启用校验和
    max_message_size: int = 10 * 1024 * 1024  # 10MB最大消息
    
    # 配置生成信息
    generated_at: str = "{time.strftime('%Y-%m-%d %H:%M:%S')}"
    wizard_version: str = "1.0"'''
    
    def _generate_config_report(self):
        """生成配置报告"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "configuration": self.config_data.copy(),
            "status": "configured",
            "next_steps": [
                "启动股票数据接收器",
                "监控连接状态",
                "检查数据接收情况",
                "根据需要调整配置参数"
            ]
        }
        
        report_file = f"server_config_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 配置报告已保存到: {report_file}")
        
        # 显示配置摘要
        print("\n📋 配置摘要:")
        print("-" * 30)
        print(f"服务器地址: {self.config_data['host']}")
        print(f"端口: {self.config_data['port']}")
        print(f"API密钥: {self.config_data['api_key'][:10]}...")
        print(f"Token: {self.config_data['token'][:10]}...")
        print(f"缓冲区: {self.config_data['buffer_size']//1024}KB")
        print(f"心跳间隔: {self.config_data['heartbeat_interval']}秒")
        print(f"最大重试: {self.config_data['max_retries']}次")

class QuickConfigPresets:
    """快速配置预设"""
    
    @staticmethod
    def get_presets() -> Dict[str, Dict[str, Any]]:
        """获取预设配置"""
        return {
            "development": {
                "name": "开发环境",
                "host": "localhost",
                "port": 8080,
                "heartbeat_interval": 10,
                "max_retries": 3,
                "buffer_size": 64 * 1024
            },
            "production": {
                "name": "生产环境",
                "host": "stock.api.server.com",
                "port": 443,
                "heartbeat_interval": 30,
                "max_retries": 10,
                "buffer_size": 1024 * 1024
            },
            "testing": {
                "name": "测试环境",
                "host": "test.stock.api.com",
                "port": 8080,
                "heartbeat_interval": 15,
                "max_retries": 5,
                "buffer_size": 256 * 1024
            }
        }
    
    @staticmethod
    def apply_preset(wizard: ServerConfigWizard, preset_name: str):
        """应用预设配置"""
        presets = QuickConfigPresets.get_presets()
        if preset_name in presets:
            preset = presets[preset_name]
            wizard.config_data.update(preset)
            print(f"✅ 已应用 {preset['name']} 预设配置")
        else:
            print(f"❌ 未找到预设: {preset_name}")

def main():
    """主函数"""
    wizard = ServerConfigWizard()
    
    # 检查是否使用预设配置
    print("🚀 配置选项:")
    print("1. 使用配置向导 (推荐)")
    print("2. 使用预设配置")
    print("3. 退出")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        wizard.run_wizard()
    elif choice == "2":
        presets = QuickConfigPresets.get_presets()
        print("\n📋 可用预设:")
        for key, preset in presets.items():
            print(f"  {key}: {preset['name']}")
        
        preset_choice = input("\n选择预设: ").strip()
        if preset_choice in presets:
            QuickConfigPresets.apply_preset(wizard, preset_choice)
            
            # 仍需要输入敏感信息
            print("\n🔐 请输入敏感信息:")
            wizard.config_data['api_key'] = input("API密钥 [QT_wat5QfcJ6N9pDZM5]: ").strip() or "QT_wat5QfcJ6N9pDZM5"
            wizard.config_data['token'] = input("认证Token: ").strip()
            
            if wizard.config_data['token']:
                wizard._save_configuration()
                wizard._generate_config_report()
                print("✅ 预设配置已应用")
            else:
                print("❌ Token不能为空")
        else:
            print("❌ 无效的预设选择")
    elif choice == "3":
        print("👋 再见！")
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
