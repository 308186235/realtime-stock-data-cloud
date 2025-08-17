#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版云端调用系统
集成连接监控和自动重连功能
"""

from simple_cloud_caller import SimpleCloudCaller
from trading_connection_monitor import TradingConnectionMonitor
from datetime import datetime
import time

class EnhancedCloudCaller(SimpleCloudCaller):
    def __init__(self):
        super().__init__()
        self.connection_monitor = TradingConnectionMonitor()
        self.auto_reconnect_enabled = True
        self.max_connection_retries = 3
    
    def ensure_connection(self) -> bool:
        """确保交易软件连接正常"""
        print("🔍 检查交易软件连接状态...")
        
        # 检查连接状态
        status_result = self.connection_monitor.check_connection_status()
        current_status = status_result["status"]
        
        if current_status == "no_window":
            print("❌ 未找到交易软件窗口,请先启动交易软件")
            return False
        
        if current_status == "online":
            print("✅ 交易软件连接正常")
            return True
        
        if current_status == "offline":
            print("⚠️ 检测到交易软件掉线")
            
            if self.auto_reconnect_enabled:
                print("🔄 开始自动重连...")
                return self._attempt_reconnection()
            else:
                print("❌ 自动重连已禁用")
                return False
        
        # 其他状态(unresponsive等)也尝试重连
        print(f"⚠️ 交易软件状态异常: {current_status}")
        if self.auto_reconnect_enabled:
            return self._attempt_reconnection()
        
        return False
    
    def _attempt_reconnection(self) -> bool:
        """尝试重连"""
        for attempt in range(1, self.max_connection_retries + 1):
            print(f"🔄 第 {attempt} 次重连尝试...")
            
            # 执行重连
            success = self.connection_monitor.handle_connection_issue()
            
            if success:
                print("✅ 重连成功!")
                return True
            
            if attempt < self.max_connection_retries:
                wait_time = 10 * attempt  # 递增等待时间
                print(f"⏳ 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        
        print("❌ 所有重连尝试都失败")
        return False
    
    def call_with_connection_check(self, operation_type):
        """
        带连接检查的调用
        在执行操作前确保连接正常
        """
        print(f"🚀 开始带连接检查的调用: {operation_type}")
        print("=" * 50)
        
        # 1. 检查并确保连接
        if not self.ensure_connection():
            return {
                "success": False,
                "message": "交易软件连接失败,无法执行操作",
                "error_type": "connection_failed"
            }
        
        # 2. 执行原有的调用逻辑
        try:
            result = self.call_with_time_tracking(operation_type)
            
            # 3. 如果调用失败,检查是否是连接问题
            if not result.get("success", False):
                print("⚠️ 操作失败,检查是否为连接问题...")
                
                # 再次检查连接
                status_result = self.connection_monitor.check_connection_status()
                if status_result["status"] == "offline":
                    print("🔍 确认为连接问题,尝试重连后重试...")
                    
                    # 重连
                    if self.ensure_connection():
                        print("🔄 重连成功,重新执行操作...")
                        result = self.call_with_time_tracking(operation_type)
                        result["reconnected"] = True
                    else:
                        result["error_type"] = "connection_failed_retry"
            
            return result
            
        except Exception as e:
            print(f"❌ 调用过程中出现异常: {e}")
            return {
                "success": False,
                "message": f"调用异常: {e}",
                "error_type": "execution_error"
            }
    
    def start_background_monitoring(self):
        """启动后台连接监控"""
        print("🚀 启动后台连接监控...")
        self.connection_monitor.start_monitoring()
        print("✅ 后台监控已启动")
    
    def stop_background_monitoring(self):
        """停止后台连接监控"""
        print("🛑 停止后台连接监控...")
        self.connection_monitor.stop_monitoring()
        print("✅ 后台监控已停止")
    
    def get_connection_status(self):
        """获取连接状态"""
        status_result = self.connection_monitor.check_connection_status()
        monitor_status = self.connection_monitor.get_monitor_status()
        
        return {
            "connection": status_result,
            "monitor": monitor_status,
            "auto_reconnect_enabled": self.auto_reconnect_enabled,
            "timestamp": datetime.now().isoformat()
        }

class SmartTradingAgent:
    """智能交易Agent - 最终版本"""
    
    def __init__(self):
        self.caller = EnhancedCloudCaller()
        self.version = "2.0.0"
        
    def get_balance_with_connection_check(self):
        """获取余额(带连接检查)"""
        print("💰 智能获取账户余额...")
        result = self.caller.call_with_connection_check('balance')
        
        if result['success']:
            # 获取详细余额数据
            try:
                from fixed_balance_reader import FixedBalanceReader
                balance_reader = FixedBalanceReader()
                balance_data = balance_reader.get_account_balance()
                
                return {
                    "success": True,
                    "data": balance_data,
                    "connection_info": {
                        "reconnected": result.get("reconnected", False)
                    },
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"余额数据获取失败: {e}",
                    "timestamp": datetime.now().isoformat()
                }
        else:
            return {
                "success": False,
                "message": result.get("message"),
                "error_type": result.get("error_type"),
                "timestamp": datetime.now().isoformat()
            }
    
    def export_data_with_connection_check(self, data_type):
        """导出数据(带连接检查)"""
        print(f"📊 智能导出{data_type}数据...")
        result = self.caller.call_with_connection_check(data_type)
        
        return {
            "success": result['success'],
            "filename": result.get('filename'),
            "local_path": result.get('local_path'),
            "message": result.get('message'),
            "connection_info": {
                "reconnected": result.get("reconnected", False)
            },
            "error_type": result.get("error_type"),
            "timestamp": datetime.now().isoformat()
        }
    
    def start_smart_monitoring(self):
        """启动智能监控"""
        print("🧠 启动智能交易监控系统...")
        self.caller.start_background_monitoring()
        print("✅ 智能监控系统已启动")
        print("💡 系统将自动监控连接状态并在掉线时自动重连")
    
    def stop_smart_monitoring(self):
        """停止智能监控"""
        print("🛑 停止智能交易监控系统...")
        self.caller.stop_background_monitoring()
        print("✅ 智能监控系统已停止")
    
    def get_system_status(self):
        """获取系统状态"""
        connection_status = self.caller.get_connection_status()
        
        return {
            "version": self.version,
            "system_status": "active",
            "connection_status": connection_status,
            "features": [
                "智能连接检查",
                "自动重连功能", 
                "后台连接监控",
                "时间跟踪调用",
                "智能文件查找",
                "OneDrive同步"
            ],
            "timestamp": datetime.now().isoformat()
        }

def test_enhanced_caller():
    """测试增强版调用器"""
    print("🧪 测试增强版云端调用器")
    print("=" * 60)
    
    agent = SmartTradingAgent()
    
    # 1. 获取系统状态
    print("1️⃣ 获取系统状态...")
    status = agent.get_system_status()
    print(f"系统版本: {status['version']}")
    print(f"连接状态: {status['connection_status']['connection']['status']}")
    
    # 2. 测试智能余额获取
    print("\n2️⃣ 测试智能余额获取...")
    balance = agent.get_balance_with_connection_check()
    if balance['success']:
        cash = balance['data']['available_cash']
        reconnected = balance['connection_info']['reconnected']
        print(f"✅ 余额获取成功: {cash:,.2f}元")
        if reconnected:
            print("🔄 过程中执行了自动重连")
    else:
        print(f"❌ 余额获取失败: {balance['message']}")
    
    # 3. 测试智能数据导出
    print("\n3️⃣ 测试智能持仓导出...")
    holdings = agent.export_data_with_connection_check('holdings')
    if holdings['success']:
        filename = holdings['filename']
        reconnected = holdings['connection_info']['reconnected']
        print(f"✅ 持仓导出成功: {filename}")
        if reconnected:
            print("🔄 过程中执行了自动重连")
    else:
        print(f"❌ 持仓导出失败: {holdings['message']}")
    
    print("\n🎉 测试完成!")

def demo_smart_monitoring():
    """演示智能监控"""
    print("🧠 演示智能交易监控系统")
    print("=" * 60)
    
    agent = SmartTradingAgent()
    
    try:
        # 启动智能监控
        agent.start_smart_monitoring()
        
        print("📊 智能监控运行中...")
        print("💡 系统会自动检测掉线并重连")
        print("💡 您可以断网测试自动重连功能")
        print("💡 按 Ctrl+C 停止监控")
        
        # 定期显示状态
        while True:
            time.sleep(30)
            status = agent.get_system_status()
            conn_status = status['connection_status']['connection']['status']
            monitor_status = status['connection_status']['monitor']
            
            print(f"📈 系统状态: 连接={conn_status} | 监控={monitor_status['monitoring']} | 重连次数={monitor_status['reconnect_count']}")
            
    except KeyboardInterrupt:
        print("\n👋 用户停止监控")
    finally:
        agent.stop_smart_monitoring()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'monitor':
        demo_smart_monitoring()
    else:
        test_enhanced_caller()
