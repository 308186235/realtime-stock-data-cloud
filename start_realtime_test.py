"""
实时股票数据测试启动器
一键启动后端服务和测试工具
"""
import os
import sys
import time
import subprocess
import threading
import webbrowser
from datetime import datetime
import requests

class RealtimeTestLauncher:
    """实时测试启动器"""
    
    def __init__(self):
        self.backend_process = None
        self.test_processes = []
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 配置
        self.config = {
            'backend_port': 8001,
            'backend_url': 'http://localhost:8001',
            'test_files': {
                'connection_tester': 'realtime_data_connection_tester.py',
                'monitor': 'realtime_monitor.py',
                'web_monitor': 'frontend/realtime_data_monitor.html'
            }
        }
    
    def print_banner(self):
        """打印启动横幅"""
        print("=" * 80)
        print("🚀 实时股票数据测试启动器")
        print("API Key: QT_wat5QfcJ6N9pDZM5")
        print("=" * 80)
        print(f"📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📂 工作目录: {self.base_dir}")
        print(f"🌐 后端地址: {self.config['backend_url']}")
        print("=" * 80)
    
    def check_market_time(self):
        """检查市场时间"""
        now = datetime.now()
        hour = now.hour
        day = now.weekday()  # 0=周一, 6=周日
        
        is_market_time = day < 5 and 9 <= hour < 15
        
        if is_market_time:
            print("✅ 当前在交易时间 (9:00-15:00)，可以测试真实数据推送")
        else:
            print("⏰ 当前非交易时间")
            if day >= 5:
                print("📅 今天是周末，股市休市")
            else:
                print("🕐 交易时间: 9:00-15:00")
            print("💡 在非交易时间可能只能接收到模拟数据")
        
        return is_market_time
    
    def check_backend_running(self):
        """检查后端是否已运行"""
        try:
            response = requests.get(f"{self.config['backend_url']}/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ 后端服务已在运行")
                return True
        except:
            pass
        
        print("❌ 后端服务未运行")
        return False
    
    def start_backend(self):
        """启动后端服务"""
        if self.check_backend_running():
            return True
        
        print("🔄 启动后端服务...")
        
        try:
            # 设置环境变量
            env = os.environ.copy()
            env['PORT'] = str(self.config['backend_port'])
            
            # 启动后端
            backend_cmd = [sys.executable, 'backend/app.py']
            self.backend_process = subprocess.Popen(
                backend_cmd,
                cwd=self.base_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待后端启动
            print("⏳ 等待后端服务启动...")
            for i in range(30):  # 最多等待30秒
                time.sleep(1)
                if self.check_backend_running():
                    print("✅ 后端服务启动成功")
                    return True
                print(f"   等待中... ({i+1}/30)")
            
            print("❌ 后端服务启动超时")
            return False
            
        except Exception as e:
            print(f"❌ 启动后端服务失败: {str(e)}")
            return False
    
    def open_web_monitor(self):
        """打开Web监控页面"""
        web_monitor_path = os.path.join(self.base_dir, self.config['test_files']['web_monitor'])
        
        if os.path.exists(web_monitor_path):
            file_url = f"file:///{web_monitor_path.replace(os.sep, '/')}"
            print(f"🌐 打开Web监控页面: {file_url}")
            webbrowser.open(file_url)
            return True
        else:
            print(f"❌ Web监控页面不存在: {web_monitor_path}")
            return False
    
    def run_connection_test(self):
        """运行连接测试"""
        test_file = os.path.join(self.base_dir, self.config['test_files']['connection_tester'])
        
        if not os.path.exists(test_file):
            print(f"❌ 测试文件不存在: {test_file}")
            return False
        
        print("🔍 运行连接测试...")
        try:
            result = subprocess.run([sys.executable, test_file], 
                                  cwd=self.base_dir, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=60)
            
            print("📋 连接测试结果:")
            print(result.stdout)
            if result.stderr:
                print("错误信息:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("⏰ 连接测试超时")
            return False
        except Exception as e:
            print(f"❌ 运行连接测试失败: {str(e)}")
            return False
    
    def start_monitor(self):
        """启动监控器"""
        monitor_file = os.path.join(self.base_dir, self.config['test_files']['monitor'])
        
        if not os.path.exists(monitor_file):
            print(f"❌ 监控文件不存在: {monitor_file}")
            return False
        
        print("📊 启动实时监控器...")
        try:
            monitor_process = subprocess.Popen(
                [sys.executable, monitor_file],
                cwd=self.base_dir
            )
            self.test_processes.append(monitor_process)
            print("✅ 监控器已启动")
            return True
            
        except Exception as e:
            print(f"❌ 启动监控器失败: {str(e)}")
            return False
    
    def show_menu(self):
        """显示菜单"""
        print("\n📋 测试选项:")
        print("1. 🔍 运行连接测试 (快速测试)")
        print("2. 📊 启动实时监控器 (持续监控)")
        print("3. 🌐 打开Web监控页面 (浏览器监控)")
        print("4. 🚀 全部启动 (推荐)")
        print("5. ❌ 退出")
        print("-" * 40)
    
    def cleanup(self):
        """清理进程"""
        print("\n🧹 清理进程...")
        
        # 停止测试进程
        for process in self.test_processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        
        # 停止后端进程
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except:
                try:
                    self.backend_process.kill()
                except:
                    pass
        
        print("✅ 清理完成")
    
    def run(self):
        """运行启动器"""
        try:
            self.print_banner()
            self.check_market_time()
            
            # 启动后端服务
            if not self.start_backend():
                print("❌ 无法启动后端服务，退出")
                return
            
            while True:
                self.show_menu()
                choice = input("请选择操作 (1-5): ").strip()
                
                if choice == '1':
                    self.run_connection_test()
                    
                elif choice == '2':
                    self.start_monitor()
                    print("💡 监控器已在后台运行，按Ctrl+C可停止")
                    
                elif choice == '3':
                    self.open_web_monitor()
                    
                elif choice == '4':
                    print("🚀 启动所有测试工具...")
                    self.run_connection_test()
                    time.sleep(2)
                    self.start_monitor()
                    time.sleep(1)
                    self.open_web_monitor()
                    print("✅ 所有工具已启动")
                    print("💡 Web监控页面已打开，监控器在后台运行")
                    
                elif choice == '5':
                    break
                    
                else:
                    print("❌ 无效选择，请重新输入")
                
                input("\n按回车键继续...")
        
        except KeyboardInterrupt:
            print("\n⏹️ 用户中断")
        except Exception as e:
            print(f"\n❌ 运行错误: {str(e)}")
        finally:
            self.cleanup()

def main():
    """主函数"""
    launcher = RealtimeTestLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
