#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易软件连接监控和自动重连系统
检测掉线状态,自动F5刷新重连
"""

import win32gui
import win32con
import win32api
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import re

class TradingConnectionMonitor:
    def __init__(self):
        self.window_title_patterns = [
            "网上股票交易系统",
            "东吴证券",
            "交易系统"
        ]
        self.offline_indicators = [
            "连接失败",
            "网络断开", 
            "连接超时",
            "服务器连接失败",
            "网络异常",
            "连接中断",
            "重新连接",
            "登录失败",
            "连接错误",
            "网络错误"
        ]
        self.online_indicators = [
            "资金余额",
            "可用资金", 
            "总资产",
            "持仓",
            "委托",
            "成交",
            "买入",
            "卖出"
        ]
        
        self.last_check_time = datetime.now()
        self.connection_status = "unknown"
        self.reconnect_count = 0
        self.max_reconnect_attempts = 5
        self.check_interval = 30  # 30秒检查一次
        self.monitoring = False
        self.monitor_thread = None
        
    def find_trading_window(self) -> Optional[int]:
        """查找交易软件窗口"""
        def enum_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                for pattern in self.window_title_patterns:
                    if pattern in title:
                        windows.append((hwnd, title))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_callback, windows)
        
        if windows:
            # 返回第一个匹配的窗口
            return windows[0][0]
        return None
    
    def get_window_text_content(self, hwnd: int) -> str:
        """获取窗口文本内容"""
        try:
            # 获取窗口类名
            class_name = win32gui.GetClassName(hwnd)
            
            # 尝试多种方法获取窗口文本
            text_content = ""
            
            # 方法1: 获取窗口标题
            title = win32gui.GetWindowText(hwnd)
            text_content += title + " "
            
            # 方法2: 遍历子窗口获取文本
            def enum_child_callback(child_hwnd, texts):
                try:
                    child_text = win32gui.GetWindowText(child_hwnd)
                    if child_text.strip():
                        texts.append(child_text)
                except:
                    pass
                return True
            
            child_texts = []
            win32gui.EnumChildWindows(hwnd, enum_child_callback, child_texts)
            text_content += " ".join(child_texts)
            
            return text_content
            
        except Exception as e:
            print(f"⚠️ 获取窗口文本失败: {e}")
            return ""
    
    def check_connection_status(self) -> Dict[str, any]:
        """检查连接状态"""
        print(f"🔍 检查交易软件连接状态...")
        
        # 查找交易窗口
        hwnd = self.find_trading_window()
        if not hwnd:
            return {
                "status": "no_window",
                "message": "未找到交易软件窗口",
                "timestamp": datetime.now().isoformat()
            }
        
        # 获取窗口内容
        window_content = self.get_window_text_content(hwnd)
        print(f"📄 窗口内容片段: {window_content[:200]}...")
        
        # 检查掉线指示器
        offline_found = []
        for indicator in self.offline_indicators:
            if indicator in window_content:
                offline_found.append(indicator)
        
        # 检查在线指示器
        online_found = []
        for indicator in self.online_indicators:
            if indicator in window_content:
                online_found.append(indicator)
        
        # 判断连接状态
        if offline_found:
            status = "offline"
            message = f"检测到掉线指示器: {', '.join(offline_found)}"
        elif online_found:
            status = "online"
            message = f"检测到在线指示器: {', '.join(online_found)}"
        else:
            # 尝试更深入的检测
            status = self._deep_connection_check(hwnd)
            message = f"深度检测结果: {status}"
        
        result = {
            "status": status,
            "message": message,
            "window_handle": hwnd,
            "offline_indicators": offline_found,
            "online_indicators": online_found,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📊 连接状态: {status} - {message}")
        return result
    
    def _deep_connection_check(self, hwnd: int) -> str:
        """深度连接检查"""
        try:
            # 检查窗口是否响应
            if not win32gui.IsWindow(hwnd):
                return "window_lost"
            
            # 检查窗口是否可见
            if not win32gui.IsWindowVisible(hwnd):
                return "window_hidden"
            
            # 尝试激活窗口看是否响应
            try:
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)
                current_fg = win32gui.GetForegroundWindow()
                if current_fg == hwnd:
                    return "responsive"
                else:
                    return "unresponsive"
            except:
                return "activation_failed"
                
        except Exception as e:
            print(f"⚠️ 深度检测异常: {e}")
            return "check_failed"
    
    def perform_reconnect(self, hwnd: int) -> bool:
        """执行重连操作(F5刷新)"""
        try:
            print(f"🔄 执行重连操作...")
            
            # 1. 激活交易软件窗口
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(1)
            
            # 2. 发送F5按键
            print("⌨️ 发送F5刷新...")
            win32api.keybd_event(win32con.VK_F5, 0, 0, 0)  # 按下F5
            time.sleep(0.1)
            win32api.keybd_event(win32con.VK_F5, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放F5
            
            print("✅ F5刷新命令已发送")
            
            # 3. 等待重连
            print("⏳ 等待重连...")
            time.sleep(5)  # 等待5秒让系统重连
            
            # 4. 检查重连结果
            reconnect_result = self.check_connection_status()
            
            if reconnect_result["status"] == "online":
                print("✅ 重连成功!")
                self.reconnect_count = 0  # 重置重连计数
                return True
            else:
                print(f"❌ 重连失败: {reconnect_result['message']}")
                return False
                
        except Exception as e:
            print(f"❌ 重连操作异常: {e}")
            return False
    
    def handle_connection_issue(self) -> bool:
        """处理连接问题"""
        print(f"🚨 检测到连接问题,开始处理...")
        
        # 查找交易窗口
        hwnd = self.find_trading_window()
        if not hwnd:
            print("❌ 无法找到交易软件窗口")
            return False
        
        # 检查重连次数
        if self.reconnect_count >= self.max_reconnect_attempts:
            print(f"❌ 已达到最大重连次数 ({self.max_reconnect_attempts}),停止重连")
            return False
        
        # 执行重连
        self.reconnect_count += 1
        print(f"🔄 第 {self.reconnect_count} 次重连尝试...")
        
        success = self.perform_reconnect(hwnd)
        
        if success:
            print(f"🎉 重连成功!")
            return True
        else:
            print(f"❌ 第 {self.reconnect_count} 次重连失败")
            
            # 如果还有重连机会,等待一段时间后再试
            if self.reconnect_count < self.max_reconnect_attempts:
                wait_time = min(30 * self.reconnect_count, 300)  # 最多等待5分钟
                print(f"⏳ 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            
            return False
    
    def start_monitoring(self):
        """开始监控"""
        if self.monitoring:
            print("⚠️ 监控已在运行中")
            return
        
        print("🚀 开始交易软件连接监控...")
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print(f"✅ 监控已启动,检查间隔: {self.check_interval} 秒")
    
    def stop_monitoring(self):
        """停止监控"""
        print("🛑 停止交易软件连接监控...")
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("✅ 监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                # 检查连接状态
                status_result = self.check_connection_status()
                current_status = status_result["status"]
                
                # 更新状态
                if current_status != self.connection_status:
                    print(f"📊 连接状态变化: {self.connection_status} → {current_status}")
                    self.connection_status = current_status
                
                # 处理掉线情况
                if current_status == "offline":
                    print("🚨 检测到掉线,开始自动重连...")
                    self.handle_connection_issue()
                elif current_status == "online":
                    # 连接正常,重置重连计数
                    if self.reconnect_count > 0:
                        print("✅ 连接已恢复正常")
                        self.reconnect_count = 0
                
                # 更新检查时间
                self.last_check_time = datetime.now()
                
                # 等待下次检查
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"❌ 监控循环异常: {e}")
                time.sleep(10)  # 异常时等待10秒
    
    def get_monitor_status(self) -> Dict[str, any]:
        """获取监控状态"""
        return {
            "monitoring": self.monitoring,
            "connection_status": self.connection_status,
            "last_check_time": self.last_check_time.isoformat(),
            "reconnect_count": self.reconnect_count,
            "max_reconnect_attempts": self.max_reconnect_attempts,
            "check_interval": self.check_interval
        }

def test_connection_monitor():
    """测试连接监控"""
    print("🧪 测试交易软件连接监控")
    print("=" * 50)
    
    monitor = TradingConnectionMonitor()
    
    # 1. 测试连接状态检查
    print("1️⃣ 测试连接状态检查...")
    status = monitor.check_connection_status()
    print(f"结果: {status}")
    
    # 2. 测试手动重连
    if status["status"] != "no_window":
        print("\n2️⃣ 测试手动重连...")
        hwnd = status.get("window_handle")
        if hwnd:
            reconnect_result = monitor.perform_reconnect(hwnd)
            print(f"重连结果: {reconnect_result}")
    
    # 3. 测试监控状态
    print("\n3️⃣ 获取监控状态...")
    monitor_status = monitor.get_monitor_status()
    print(f"监控状态: {monitor_status}")

def demo_auto_monitoring():
    """演示自动监控"""
    print("🚀 演示自动连接监控")
    print("=" * 50)
    
    monitor = TradingConnectionMonitor()
    
    try:
        # 启动监控
        monitor.start_monitoring()
        
        print("📊 监控运行中,按 Ctrl+C 停止...")
        print("💡 您可以手动断开网络测试自动重连功能")
        
        # 运行监控
        while True:
            time.sleep(10)
            status = monitor.get_monitor_status()
            print(f"📈 状态更新: {status['connection_status']} | 重连次数: {status['reconnect_count']}")
            
    except KeyboardInterrupt:
        print("\n👋 用户中断监控")
    finally:
        monitor.stop_monitoring()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'auto':
        demo_auto_monitoring()
    else:
        test_connection_monitor()
