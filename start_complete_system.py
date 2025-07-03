"""
完整股票交易系统启动脚本
集成茶股帮实时数据源，启动完整的AI股票交易系统
"""

import os
import sys
import time
import asyncio
import subprocess
import threading
from datetime import datetime
import json

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chagubang_token_manager import TokenManager
from chagubang_receiver import ChaguBangReceiver

class CompleteSystemStarter:
    """完整系统启动器"""
    
    def __init__(self):
        self.token_manager = TokenManager()
        self.processes = {}
        self.services_status = {}
        
    def welcome(self):
        """欢迎界面"""
        print("🚀 AI股票交易系统 - 完整启动")
        print("=" * 60)
        print("📊 茶股帮实时数据 | 🤖 AI Agent | 💼 自动交易")
        print("=" * 60)
        print()
        
    def check_prerequisites(self) -> bool:
        """检查前置条件"""
        print("🔍 检查系统前置条件...")
        
        checks = {
            "Python环境": self._check_python(),
            "依赖包": self._check_dependencies(),
            "茶股帮Token": self._check_chagubang_token(),
            "后端配置": self._check_backend_config(),
            "前端文件": self._check_frontend_files()
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            if not passed:
                all_passed = False
        
        return all_passed
    
    def _check_python(self) -> bool:
        """检查Python环境"""
        try:
            version = sys.version_info
            return version.major >= 3 and version.minor >= 8
        except:
            return False
    
    def _check_dependencies(self) -> bool:
        """检查依赖包"""
        required_packages = [
            'fastapi', 'uvicorn', 'websockets', 'requests'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                return False
        return True
    
    def _check_chagubang_token(self) -> bool:
        """检查茶股帮Token"""
        best_token = self.token_manager.get_best_token()
        return best_token is not None
    
    def _check_backend_config(self) -> bool:
        """检查后端配置"""
        return os.path.exists('backend/app.py')
    
    def _check_frontend_files(self) -> bool:
        """检查前端文件"""
        return os.path.exists('frontend/stock5/services/config.js')
    
    def setup_missing_requirements(self):
        """设置缺失的要求"""
        print("\n🔧 设置缺失的要求...")
        
        # 检查并设置Token
        if not self._check_chagubang_token():
            print("\n❌ 没有可用的茶股帮Token")
            print("请按以下步骤配置Token:")
            print("1. 获取茶股帮API Token")
            print("2. 运行: python chagubang_token_manager.py add <token>")
            print("3. 重新运行此脚本")
            return False
        
        # 检查依赖包
        if not self._check_dependencies():
            print("\n📦 安装缺失的依赖包...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 
                              'fastapi', 'uvicorn', 'websockets', 'requests'], 
                              check=True)
                print("✅ 依赖包安装完成")
            except subprocess.CalledProcessError:
                print("❌ 依赖包安装失败")
                return False
        
        return True
    
    def start_chagubang_service(self) -> bool:
        """启动茶股帮数据服务"""
        print("\n📡 启动茶股帮数据服务...")
        
        try:
            best_token = self.token_manager.get_best_token()
            if not best_token:
                print("❌ 没有可用Token")
                return False
            
            # 创建接收器
            receiver = ChaguBangReceiver(token=best_token)
            
            # 测试连接
            print("🔍 测试茶股帮连接...")
            thread = threading.Thread(target=receiver.start_receiving, daemon=True)
            thread.start()
            
            # 等待连接建立
            time.sleep(5)
            stats = receiver.get_stats()
            
            if stats['connection_status'] == 'connected':
                print("✅ 茶股帮数据服务启动成功")
                self.services_status['chagubang'] = 'running'
                return True
            else:
                print("❌ 茶股帮连接失败")
                return False
                
        except Exception as e:
            print(f"❌ 启动茶股帮服务失败: {e}")
            return False
    
    def start_backend_service(self) -> bool:
        """启动后端服务"""
        print("\n🔧 启动后端API服务...")
        
        try:
            # 启动FastAPI后端
            backend_cmd = [sys.executable, 'backend/app.py']
            
            self.processes['backend'] = subprocess.Popen(
                backend_cmd,
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待服务启动
            time.sleep(10)
            
            # 检查服务状态
            if self.processes['backend'].poll() is None:
                print("✅ 后端API服务启动成功 (http://localhost:8000)")
                self.services_status['backend'] = 'running'
                return True
            else:
                print("❌ 后端API服务启动失败")
                return False
                
        except Exception as e:
            print(f"❌ 启动后端服务失败: {e}")
            return False
    
    def start_frontend_service(self) -> bool:
        """启动前端服务"""
        print("\n🌐 启动前端服务...")
        
        try:
            # 检查是否有前端构建工具
            if os.path.exists('frontend/stock5/package.json'):
                # 使用npm/yarn启动
                frontend_cmd = ['npm', 'run', 'dev']
                cwd = 'frontend/stock5'
            else:
                # 使用Python简单HTTP服务器
                frontend_cmd = [sys.executable, '-m', 'http.server', '3000']
                cwd = 'frontend/stock5'
            
            self.processes['frontend'] = subprocess.Popen(
                frontend_cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(5)
            
            if self.processes['frontend'].poll() is None:
                print("✅ 前端服务启动成功 (http://localhost:3000)")
                self.services_status['frontend'] = 'running'
                return True
            else:
                print("❌ 前端服务启动失败")
                return False
                
        except Exception as e:
            print(f"❌ 启动前端服务失败: {e}")
            return False
    
    def monitor_services(self):
        """监控服务状态"""
        print("\n📊 服务监控中...")
        print("按 Ctrl+C 停止所有服务")
        print("-" * 50)
        
        try:
            while True:
                # 检查服务状态
                for service_name, process in self.processes.items():
                    if process.poll() is not None:
                        print(f"⚠️ {service_name} 服务已停止")
                        self.services_status[service_name] = 'stopped'
                
                # 显示状态
                status_line = " | ".join([
                    f"{name}: {'🟢' if status == 'running' else '🔴'}"
                    for name, status in self.services_status.items()
                ])
                print(f"\r{datetime.now().strftime('%H:%M:%S')} - {status_line}", end="")
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n\n⏹️ 收到停止信号...")
            self.stop_all_services()
    
    def stop_all_services(self):
        """停止所有服务"""
        print("🛑 停止所有服务...")
        
        for service_name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=10)
                print(f"✅ {service_name} 服务已停止")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔪 强制停止 {service_name} 服务")
            except Exception as e:
                print(f"❌ 停止 {service_name} 服务失败: {e}")
        
        print("✅ 所有服务已停止")
    
    def generate_system_info(self):
        """生成系统信息"""
        info = {
            "system_name": "AI股票交易系统",
            "version": "1.0.0",
            "start_time": datetime.now().isoformat(),
            "services": {
                "chagubang": {
                    "name": "茶股帮数据服务",
                    "url": "l1.chagubang.com:6380",
                    "status": self.services_status.get('chagubang', 'stopped')
                },
                "backend": {
                    "name": "后端API服务",
                    "url": "http://localhost:8000",
                    "status": self.services_status.get('backend', 'stopped')
                },
                "frontend": {
                    "name": "前端界面服务",
                    "url": "http://localhost:3000",
                    "status": self.services_status.get('frontend', 'stopped')
                }
            },
            "features": [
                "茶股帮实时股票数据",
                "AI智能分析",
                "自动交易执行",
                "风险管理",
                "实时监控"
            ]
        }
        
        # 保存系统信息
        with open('system_info.json', 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        return info
    
    def run_complete_startup(self):
        """运行完整启动流程"""
        self.welcome()
        
        try:
            # 检查前置条件
            if not self.check_prerequisites():
                print("\n❌ 前置条件检查失败")
                if not self.setup_missing_requirements():
                    print("❌ 无法满足前置条件，启动失败")
                    return False
            
            print("\n✅ 前置条件检查通过")
            
            # 启动服务
            services_to_start = [
                ("茶股帮数据服务", self.start_chagubang_service),
                ("后端API服务", self.start_backend_service),
                ("前端界面服务", self.start_frontend_service)
            ]
            
            for service_name, start_func in services_to_start:
                if not start_func():
                    print(f"❌ {service_name}启动失败")
                    return False
            
            # 生成系统信息
            system_info = self.generate_system_info()
            
            print(f"\n🎉 系统启动完成！")
            print(f"📊 后端API: http://localhost:8000")
            print(f"🌐 前端界面: http://localhost:3000")
            print(f"📈 API文档: http://localhost:8000/docs")
            print(f"📋 系统信息已保存到: system_info.json")
            
            # 开始监控
            self.monitor_services()
            
            return True
            
        except Exception as e:
            print(f"\n❌ 系统启动失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    starter = CompleteSystemStarter()
    success = starter.run_complete_startup()
    
    if not success:
        print("\n💡 启动失败解决方案:")
        print("1. 检查Python环境 (需要Python 3.8+)")
        print("2. 安装依赖: pip install fastapi uvicorn websockets requests")
        print("3. 配置茶股帮Token: python chagubang_token_manager.py add <token>")
        print("4. 检查端口占用 (8000, 3000)")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
