"""
完整集成测试脚本
测试茶股帮数据源与AI股票交易系统的完整集成
"""

import os
import sys
import time
import asyncio
import requests
import threading
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chagubang_receiver import ChaguBangReceiver
from chagubang_token_manager import TokenManager

class IntegrationTester:
    """集成测试器"""
    
    def __init__(self):
        self.token_manager = TokenManager()
        self.test_results = {}
        
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 AI股票交易系统 - 完整集成测试")
        print("=" * 50)
        
        tests = [
            ("茶股帮连接测试", self.test_chagubang_connection),
            ("数据接收测试", self.test_data_reception),
            ("API集成测试", self.test_api_integration),
            ("前端配置测试", self.test_frontend_config),
            ("系统集成测试", self.test_system_integration)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 {test_name}")
            print("-" * 30)
            
            try:
                result = test_func()
                self.test_results[test_name] = result
                status = "✅ 通过" if result else "❌ 失败"
                print(f"结果: {status}")
            except Exception as e:
                print(f"❌ 测试异常: {e}")
                self.test_results[test_name] = False
        
        self.print_summary()
    
    def test_chagubang_connection(self) -> bool:
        """测试茶股帮连接"""
        try:
            # 获取Token
            best_token = self.token_manager.get_best_token()
            if not best_token:
                print("⚠️ 没有可用Token，使用空Token测试连接")
                best_token = ''
            
            # 创建接收器
            receiver = ChaguBangReceiver(token=best_token)
            
            # 启动连接测试
            thread = threading.Thread(target=receiver.start_receiving, daemon=True)
            thread.start()
            
            # 等待连接
            time.sleep(5)
            
            # 检查连接状态
            stats = receiver.get_stats()
            connected = stats['connection_status'] == 'connected'
            
            print(f"连接状态: {stats['connection_status']}")
            print(f"服务器: l1.chagubang.com:6380")
            print(f"Token: {best_token[:15] + '...' if best_token else '空Token'}")
            
            receiver.stop_receiving()
            return connected
            
        except Exception as e:
            print(f"连接测试失败: {e}")
            return False
    
    def test_data_reception(self) -> bool:
        """测试数据接收"""
        try:
            best_token = self.token_manager.get_best_token()
            if not best_token:
                print("⚠️ 没有有效Token，跳过数据接收测试")
                return False
            
            receiver = ChaguBangReceiver(token=best_token)
            received_data = []
            
            def on_data(stock_data):
                received_data.append(stock_data)
                print(f"📊 接收数据: {stock_data['stock_code']} {stock_data['last_price']:.2f}")
            
            receiver.add_data_callback(on_data)
            
            # 启动接收
            thread = threading.Thread(target=receiver.start_receiving, daemon=True)
            thread.start()
            
            # 等待数据
            print("⏱️ 等待15秒接收数据...")
            time.sleep(15)
            
            receiver.stop_receiving()
            
            success = len(received_data) > 0
            print(f"接收数据量: {len(received_data)} 条")
            
            return success
            
        except Exception as e:
            print(f"数据接收测试失败: {e}")
            return False
    
    def test_api_integration(self) -> bool:
        """测试API集成"""
        try:
            # 检查API文件是否存在
            api_files = [
                'backend/api/routers/chagubang_api.py',
                'backend/services/chagubang_integration.py'
            ]
            
            for file_path in api_files:
                if not os.path.exists(file_path):
                    print(f"❌ API文件不存在: {file_path}")
                    return False
                else:
                    print(f"✅ API文件存在: {file_path}")
            
            # 检查API路由配置
            app_file = 'backend/app.py'
            if os.path.exists(app_file):
                with open(app_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'chagubang_router' in content:
                        print("✅ API路由已配置")
                        return True
                    else:
                        print("❌ API路由未配置")
                        return False
            else:
                print("❌ 后端应用文件不存在")
                return False
                
        except Exception as e:
            print(f"API集成测试失败: {e}")
            return False
    
    def test_frontend_config(self) -> bool:
        """测试前端配置"""
        try:
            config_files = [
                'frontend/stock5/services/config.js',
                'frontend/stock5/services/chaguBangService.js'
            ]
            
            for file_path in config_files:
                if not os.path.exists(file_path):
                    print(f"❌ 前端文件不存在: {file_path}")
                    return False
                else:
                    print(f"✅ 前端文件存在: {file_path}")
            
            # 检查配置内容
            config_file = 'frontend/stock5/services/config.js'
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'chagubang' in content:
                    print("✅ 前端配置已更新")
                    return True
                else:
                    print("❌ 前端配置未更新")
                    return False
                    
        except Exception as e:
            print(f"前端配置测试失败: {e}")
            return False
    
    def test_system_integration(self) -> bool:
        """测试系统集成"""
        try:
            # 检查启动脚本
            startup_files = [
                'start_complete_system.py',
                'chagubang_token_manager.py',
                'chagubang_receiver.py'
            ]
            
            for file_path in startup_files:
                if not os.path.exists(file_path):
                    print(f"❌ 系统文件不存在: {file_path}")
                    return False
                else:
                    print(f"✅ 系统文件存在: {file_path}")
            
            # 检查Token管理
            tokens = self.token_manager.config.get('tokens', [])
            if tokens:
                print(f"✅ 已配置 {len(tokens)} 个Token")
            else:
                print("⚠️ 未配置Token")
            
            return True
            
        except Exception as e:
            print(f"系统集成测试失败: {e}")
            return False
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 50)
        print("🎯 测试总结")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{status} {test_name}")
        
        print(f"\n📊 总体结果: {passed}/{total} 测试通过")
        
        if passed == total:
            print("\n🎉 所有测试通过！系统集成完成")
            print("\n📋 下一步操作:")
            print("1. 配置有效的茶股帮Token")
            print("2. 运行: python start_complete_system.py")
            print("3. 访问: http://localhost:8000 (后端API)")
            print("4. 访问: http://localhost:3000 (前端界面)")
        else:
            print(f"\n⚠️ {total - passed} 个测试失败")
            print("\n🔧 解决方案:")
            
            if not self.test_results.get("茶股帮连接测试", False):
                print("• 检查网络连接和茶股帮服务器状态")
                print("• 配置有效Token: python chagubang_token_manager.py add <token>")
            
            if not self.test_results.get("API集成测试", False):
                print("• 检查后端API文件是否正确创建")
                print("• 确认路由配置是否正确")
            
            if not self.test_results.get("前端配置测试", False):
                print("• 检查前端配置文件是否正确创建")
                print("• 确认服务文件是否存在")


def main():
    """主函数"""
    tester = IntegrationTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
