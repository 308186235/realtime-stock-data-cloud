"""
茶股帮完整集成设置脚本
包含token管理,连接测试,数据接收和系统集成
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Optional

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chagubang_token_manager import TokenManager
from chagubang_receiver import ChaguBangReceiver, start_chagubang_service

class ChaguBangSetup:
    """茶股帮完整设置"""
    
    def __init__(self):
        self.token_manager = TokenManager()
        self.receiver: Optional[ChaguBangReceiver] = None
        self.setup_complete = False
        
    def welcome(self):
        """欢迎界面"""
        print("🚀 茶股帮股票数据源完整集成")
        print("=" * 50)
        print("📊 实时股票数据 | 🔐 Token管理 | 🎯 系统集成")
        print("=" * 50)
        print()
        print("📋 功能说明:")
        print("• 连接茶股帮实时数据服务器 (l1.chagubang.com:6380)")
        print("• 接收沪深A股 + 北交所实时行情")
        print("• 支持多Token管理和自动切换")
        print("• 集成到您的AI股票交易系统")
        print()
    
    def check_token_status(self) -> bool:
        """检查token状态"""
        print("🔍 检查Token状态...")
        
        tokens = self.token_manager.config.get('tokens', [])
        if not tokens:
            print("❌ 没有配置Token")
            return False
        
        # 检查是否有有效token
        valid_tokens = [t for t in tokens if t.get('test_status') == 'valid']
        if valid_tokens:
            print(f"✅ 找到 {len(valid_tokens)} 个有效Token")
            return True
        
        # 检查是否有未测试的token
        untested_tokens = [t for t in tokens if t.get('test_status') == 'untested']
        if untested_tokens:
            print(f"⚠️ 有 {len(untested_tokens)} 个未测试Token")
            return False
        
        print("❌ 没有有效Token")
        return False
    
    def setup_tokens(self):
        """设置Token"""
        print("\n🔐 Token设置")
        print("-" * 30)
        
        if not self.check_token_status():
            print("\n需要添加Token才能继续")
            print("Token获取方式:")
            print("1. 从茶股帮官网申请")
            print("2. 联系数据提供商")
            print("3. 使用已有的API密钥")
            print()
            
            while True:
                choice = input("是否现在添加Token? (y/n): ").strip().lower()
                if choice == 'y':
                    self._add_token_interactive()
                    break
                elif choice == 'n':
                    print("⚠️ 没有Token无法继续,请稍后配置")
                    return False
                else:
                    print("请输入 y 或 n")
        
        # 测试所有未测试的token
        self._test_all_tokens()
        
        return self.check_token_status()
    
    def _add_token_interactive(self):
        """交互式添加Token"""
        while True:
            token = input("\n请输入Token: ").strip()
            if not token:
                print("Token不能为空")
                continue
            
            desc = input("请输入描述 (可选): ").strip()
            
            if self.token_manager.add_token(token, desc):
                # 立即测试新添加的token
                print("🔍 测试新添加的Token...")
                result = self.token_manager.test_token(token)
                
                if result['status'] == 'valid':
                    print("🎉 Token有效!")
                    break
                else:
                    print(f"❌ Token测试失败: {result['message']}")
            
            choice = input("是否继续添加Token? (y/n): ").strip().lower()
            if choice != 'y':
                break
    
    def _test_all_tokens(self):
        """测试所有Token"""
        tokens = self.token_manager.config.get('tokens', [])
        untested = [t for t in tokens if t.get('test_status') == 'untested']
        
        if untested:
            print(f"\n🔍 测试 {len(untested)} 个未测试Token...")
            for token_info in untested:
                self.token_manager.test_token(token_info['token'])
                time.sleep(1)  # 避免频繁请求
    
    def setup_data_receiver(self) -> bool:
        """设置数据接收器"""
        print("\n📡 设置数据接收器")
        print("-" * 30)
        
        # 获取最佳token
        best_token = self.token_manager.get_best_token()
        if not best_token:
            print("❌ 没有可用的Token")
            return False
        
        print(f"🔑 使用Token: {best_token[:15]}...")
        
        # 创建接收器
        try:
            self.receiver = ChaguBangReceiver(token=best_token)
            
            # 添加数据回调
            self.receiver.add_data_callback(self._on_stock_data)
            
            print("✅ 数据接收器创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 创建数据接收器失败: {e}")
            return False
    
    def _on_stock_data(self, stock_data):
        """股票数据回调"""
        # 这里可以添加数据处理逻辑
        code = stock_data['stock_code']
        price = stock_data['last_price']
        change_pct = stock_data['change_pct']
        
        # 简单的异动检测
        if abs(change_pct) > 3.0:  # 涨跌幅超过3%
            print(f"🚨 {code} 异动: {change_pct:+.2f}% 价格: {price:.2f}")
    
    def test_data_reception(self) -> bool:
        """测试数据接收"""
        print("\n📊 测试数据接收")
        print("-" * 30)
        
        if not self.receiver:
            print("❌ 数据接收器未初始化")
            return False
        
        print("🚀 启动数据接收测试 (30秒)...")
        
        # 启动接收线程
        import threading
        thread = threading.Thread(target=self.receiver.start_receiving, daemon=True)
        thread.start()
        
        # 等待30秒
        start_time = time.time()
        last_count = 0
        
        while time.time() - start_time < 30:
            time.sleep(5)
            stats = self.receiver.get_stats()
            current_count = stats['received_count']
            
            if current_count > last_count:
                print(f"📈 已接收 {current_count} 条数据")
                last_count = current_count
            elif stats['connection_status'] == 'connected':
                print("🔗 连接正常,等待数据...")
            else:
                print("❌ 连接异常")
                break
        
        # 获取最终统计
        final_stats = self.receiver.get_stats()
        total_received = final_stats['received_count']
        
        print(f"\n📊 测试结果:")
        print(f"   接收数据: {total_received} 条")
        print(f"   连接状态: {final_stats['connection_status']}")
        print(f"   错误次数: {final_stats['error_count']}")
        
        if total_received > 0:
            print("✅ 数据接收测试成功!")
            return True
        else:
            print("❌ 未接收到数据")
            return False
    
    def generate_integration_code(self):
        """生成集成代码"""
        print("\n💻 生成集成代码")
        print("-" * 30)
        
        best_token = self.token_manager.get_best_token()
        if not best_token:
            print("❌ 没有可用Token")
            return
        
        integration_code = f'''"""
茶股帮数据源集成代码
自动生成于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

from chagubang_receiver import start_chagubang_service, get_stock_data, get_service_stats

# 启动茶股帮数据服务
def start_stock_data_service():
    """启动股票数据服务"""
    token = "{best_token}"
    thread = start_chagubang_service(token=token)
    print("🚀 茶股帮数据服务已启动")
    return thread

# 获取股票数据
def get_realtime_stock_data(stock_code=None):
    """获取实时股票数据"""
    return get_stock_data(stock_code)

# 获取服务状态
def get_data_service_status():
    """获取数据服务状态"""
    return get_service_stats()

# 使用示例
if __name__ == "__main__":
    # 启动服务
    service_thread = start_stock_data_service()
    
    # 等待数据
    import time
    time.sleep(10)
    
    # 获取数据
    all_data = get_realtime_stock_data()
    print(f"接收到 {{len(all_data)}} 只股票数据")
    
    # 获取特定股票
    stock_000001 = get_realtime_stock_data("000001")
    if stock_000001:
        print(f"000001 价格: {{stock_000001['last_price']:.2f}}")
'''
        
        # 保存到文件
        filename = f"chagubang_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(integration_code)
            print(f"✅ 集成代码已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            print("\n集成代码:")
            print(integration_code)
    
    def run_complete_setup(self):
        """运行完整设置"""
        self.welcome()
        
        try:
            # 步骤1: Token设置
            if not self.setup_tokens():
                print("❌ Token设置失败,无法继续")
                return False
            
            # 步骤2: 数据接收器设置
            if not self.setup_data_receiver():
                print("❌ 数据接收器设置失败")
                return False
            
            # 步骤3: 数据接收测试
            if not self.test_data_reception():
                print("⚠️ 数据接收测试失败,但可以继续")
            
            # 步骤4: 生成集成代码
            self.generate_integration_code()
            
            print("\n🎉 茶股帮集成设置完成!")
            print("\n📋 后续步骤:")
            print("1. 使用生成的集成代码")
            print("2. 集成到您的交易系统")
            print("3. 配置Agent使用实时数据")
            print("4. 测试交易策略")
            
            self.setup_complete = True
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️ 用户中断设置")
            return False
        except Exception as e:
            print(f"\n❌ 设置过程中发生异常: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if self.receiver:
                self.receiver.stop_receiving()


def main():
    """主函数"""
    setup = ChaguBangSetup()
    success = setup.run_complete_setup()
    
    if success:
        print("\n✅ 设置成功完成!")
        return 0
    else:
        print("\n❌ 设置未完成")
        return 1


if __name__ == "__main__":
    exit(main())
