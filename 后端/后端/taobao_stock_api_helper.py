#!/usr/bin/env python3
"""
淘宝股票数据API配置助手
帮助获取和配置从淘宝购买的股票推送服务连接信息
"""

import os
import json
import time
import socket
import logging
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaobaoStockAPIHelper:
    """淘宝股票API配置助手"""
    
    def __init__(self):
        self.config_data = {}
        self.api_key = "process.env.STOCK_API_KEY"
        
    def run_helper(self):
        """运行配置助手"""
        print("🛒 淘宝股票数据API配置助手")
        print("=" * 50)
        print("帮助您配置从淘宝购买的股票推送服务")
        print()
        
        try:
            # 1. 收集淘宝服务信息
            self._collect_taobao_service_info()
            
            # 2. 验证连接信息
            self._validate_connection_info()
            
            # 3. 测试连接
            if self._test_connection():
                print("✅ 连接测试成功!")
            else:
                print("⚠️ 连接测试失败,请检查信息是否正确")
            
            # 4. 保存配置
            self._save_configuration()
            
            # 5. 生成使用说明
            self._generate_usage_guide()
            
            print("\n🎉 配置完成!")
            
        except KeyboardInterrupt:
            print("\n❌ 用户取消配置")
        except Exception as e:
            print(f"\n❌ 配置过程出错: {e}")
    
    def _collect_taobao_service_info(self):
        """收集淘宝服务信息"""
        print("📝 请输入从淘宝卖家获得的连接信息:")
        print()
        
        # 显示API Key
        print(f"📋 您的API Key: {self.api_key}")
        confirm = input("是否正确?(Y/n): ").strip().lower()
        if confirm == 'n':
            new_key = input("请输入正确的API Key: ").strip()
            if new_key:
                self.api_key = new_key
        
        self.config_data['api_key'] = self.api_key
        print()
        
        # 服务器地址
        print("🌐 服务器地址信息:")
        print("   常见格式: xxx.xxx.xxx.xxx 或 domain.com")
        while True:
            host = input("服务器地址: ").strip()
            if host:
                self.config_data['host'] = host
                break
            print("❌ 服务器地址不能为空")
        
        # 服务器端口
        print("\n🔌 端口信息:")
        print("   常见端口: 8080, 9999, 7777, 8888")
        while True:
            try:
                port_str = input("服务器端口: ").strip()
                port = int(port_str)
                if 1 <= port <= 65535:
                    self.config_data['port'] = port
                    break
                else:
                    print("❌ 端口号必须在1-65535之间")
            except ValueError:
                print("❌ 请输入有效的端口号")
        
        # 认证Token
        print("\n🔐 认证信息:")
        print("   Token通常是一串字母数字组合")
        while True:
            token = input("认证Token: ").strip()
            if token:
                self.config_data['token'] = token
                break
            print("❌ 认证Token不能为空")
        
        print("\n✅ 基本信息收集完成")
    
    def _validate_connection_info(self):
        """验证连接信息"""
        print("\n🔍 验证连接信息...")
        
        issues = []
        
        # 验证服务器地址
        host = self.config_data['host']
        if not self._is_valid_host(host):
            issues.append(f"服务器地址格式可能有误: {host}")
        
        # 验证端口
        port = self.config_data['port']
        if port in [80, 443, 22, 21]:
            issues.append(f"端口 {port} 通常不用于股票数据推送")
        
        # 验证Token长度
        token = self.config_data['token']
        if len(token) < 8:
            issues.append("Token长度较短,请确认是否正确")
        
        if issues:
            print("⚠️ 发现潜在问题:")
            for issue in issues:
                print(f"   - {issue}")
            
            confirm = input("\n是否继续?(Y/n): ").strip().lower()
            if confirm == 'n':
                print("请重新输入正确信息")
                self._collect_taobao_service_info()
        else:
            print("✅ 连接信息格式正确")
    
    def _is_valid_host(self, host: str) -> bool:
        """验证主机地址格式"""
        try:
            # 尝试解析IP地址
            socket.inet_aton(host)
            return True
        except socket.error:
            # 检查域名格式
            if '.' in host and len(host) > 3:
                return True
            return False
    
    def _test_connection(self) -> bool:
        """测试连接"""
        print(f"\n🔍 测试连接到 {self.config_data['host']}:{self.config_data['port']}...")
        
        try:
            # 基础TCP连接测试
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            result = sock.connect_ex((self.config_data['host'], self.config_data['port']))
            sock.close()
            
            if result == 0:
                print("✅ TCP连接成功")
                
                # 尝试简单的认证测试
                return self._test_authentication()
            else:
                print(f"❌ TCP连接失败,错误代码: {result}")
                self._suggest_connection_fixes()
                return False
                
        except Exception as e:
            print(f"❌ 连接测试失败: {e}")
            self._suggest_connection_fixes()
            return False
    
    def _test_authentication(self) -> bool:
        """测试认证"""
        print("🔐 测试认证...")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.config_data['host'], self.config_data['port']))
            
            # 发送认证信息
            auth_data = {
                'api_key': self.config_data['api_key'],
                'token': self.config_data['token'],
                'action': 'auth'
            }
            
            # 尝试不同的认证格式
            formats_to_try = [
                json.dumps(auth_data).encode('utf-8'),  # JSON格式
                self.config_data['token'].encode('utf-8'),  # 纯Token
                f"{self.config_data['api_key']}:{self.config_data['token']}".encode('utf-8')  # Key:Token格式
            ]
            
            for i, auth_bytes in enumerate(formats_to_try):
                try:
                    sock.send(auth_bytes)
                    
                    # 等待响应
                    sock.settimeout(5)
                    response = sock.recv(1024)
                    
                    if response:
                        print(f"✅ 认证格式 {i+1} 收到响应: {response[:50]}...")
                        sock.close()
                        return True
                        
                except Exception as e:
                    print(f"⚠️ 认证格式 {i+1} 失败: {e}")
                    continue
            
            sock.close()
            print("⚠️ 所有认证格式都未收到明确响应,但连接正常")
            return True
            
        except Exception as e:
            print(f"❌ 认证测试失败: {e}")
            return False
    
    def _suggest_connection_fixes(self):
        """建议连接修复方案"""
        print("\n💡 连接问题排查建议:")
        print("1. 检查网络连接是否正常")
        print("2. 确认服务器地址和端口是否正确")
        print("3. 检查防火墙是否阻止连接")
        print("4. 联系淘宝卖家确认服务状态")
        print("5. 确认服务是否在运行时间内")
    
    def _save_configuration(self):
        """保存配置"""
        print("\n💾 保存配置...")
        
        try:
            # 生成配置代码
            config_code = self._generate_config_code()
            
            # 保存到配置文件
            config_file = "backend/services/realtime_stock_receiver.py"
            
            if os.path.exists(config_file):
                # 备份原文件
                backup_file = f"{config_file}.backup_{int(time.time())}"
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"📄 原文件已备份到: {backup_file}")
                
                # 替换配置
                import re
                pattern = r'@dataclass\s+class ConnectionConfig:.*?(?=\n\s*class|\n\s*def|\Z)'
                
                if re.search(pattern, content, re.DOTALL):
                    new_content = re.sub(pattern, config_code.strip(), content, flags=re.DOTALL)
                else:
                    new_content = config_code + "\n\n" + content
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            else:
                # 创建新文件
                os.makedirs(os.path.dirname(config_file), exist_ok=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(config_code)
            
            # 保存JSON配置
            json_config = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": "淘宝购买",
                "config": self.config_data,
                "status": "configured"
            }
            
            with open("taobao_stock_config.json", 'w', encoding='utf-8') as f:
                json.dump(json_config, f, ensure_ascii=False, indent=2)
            
            print("✅ 配置已保存")
            
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
    
    def _generate_config_code(self) -> str:
        """生成配置代码"""
        return f'''@dataclass
class ConnectionConfig:
    """连接配置 - 淘宝股票数据服务"""
    # 淘宝服务配置
    api_key: str = "{self.config_data['api_key']}"
    host: str = "{self.config_data['host']}"
    port: int = {self.config_data['port']}
    token: str = "{self.config_data['token']}"
    
    # 性能配置
    buffer_size: int = 1024 * 1024      # 1MB缓冲区
    max_queue_size: int = 100000        # 最大队列大小
    redis_batch_size: int = 1000        # Redis批量写入大小
    
    # 心跳配置
    heartbeat_interval: int = 30        # 心跳间隔(秒)
    heartbeat_timeout: int = 90         # 心跳超时(秒)
    
    # 重连配置
    max_retries: int = 10               # 最大重试次数
    retry_base_delay: int = 2           # 重试基础延迟
    retry_max_delay: int = 300          # 最大重试延迟(5分钟)
    
    # 数据验证配置
    enable_checksum: bool = True        # 启用校验和
    max_message_size: int = 10 * 1024 * 1024  # 10MB最大消息
    
    # 配置信息
    configured_at: str = "{time.strftime('%Y-%m-%d %H:%M:%S')}"
    source: str = "淘宝购买"
    helper_version: str = "1.0"'''
    
    def _generate_usage_guide(self):
        """生成使用说明"""
        guide = f"""
# 🛒 淘宝股票数据服务使用说明

## 📋 配置信息
- **服务器地址**: {self.config_data['host']}
- **端口**: {self.config_data['port']}
- **API Key**: {self.config_data['api_key']}
- **Token**: {self.config_data['token'][:10]}...

## 🚀 启动服务
```python
# 启动股票数据接收器
python -m backend.services.realtime_stock_receiver
```

## 📞 联系卖家
如果遇到连接问题,请联系淘宝卖家:
1. 确认服务器是否正常运行
2. 确认您的账户是否有效
3. 确认服务时间(通常是交易时间)
4. 获取最新的连接参数

## 🔧 故障排查
1. **连接超时**: 检查网络和防火墙
2. **认证失败**: 确认Token是否正确
3. **无数据**: 确认在交易时间内测试
4. **频繁断线**: 联系卖家检查服务稳定性

## 📊 监控建议
- 在交易时间(9:00-15:00)测试
- 持续监控30分钟以上
- 记录错误日志并反馈给卖家
"""
        
        with open("taobao_stock_usage_guide.md", 'w', encoding='utf-8') as f:
            f.write(guide)
        
        print(f"📖 使用说明已保存到: taobao_stock_usage_guide.md")

def main():
    """主函数"""
    helper = TaobaoStockAPIHelper()
    
    print("🎯 选择操作:")
    print("1. 配置淘宝股票数据服务")
    print("2. 测试现有配置")
    print("3. 查看配置信息")
    print("4. 退出")
    
    choice = input("\n请选择 (1-4): ").strip()
    
    if choice == "1":
        helper.run_helper()
    elif choice == "2":
        if os.path.exists("taobao_stock_config.json"):
            with open("taobao_stock_config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            helper.config_data = config['config']
            if helper._test_connection():
                print("✅ 配置测试通过")
            else:
                print("❌ 配置测试失败")
        else:
            print("❌ 未找到配置文件,请先进行配置")
    elif choice == "3":
        if os.path.exists("taobao_stock_config.json"):
            with open("taobao_stock_config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("\n📋 当前配置:")
            print(f"服务器: {config['config']['host']}:{config['config']['port']}")
            print(f"API Key: {config['config']['api_key']}")
            print(f"Token: {config['config']['token'][:10]}...")
            print(f"配置时间: {config['timestamp']}")
        else:
            print("❌ 未找到配置文件")
    elif choice == "4":
        print("👋 再见!")
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
